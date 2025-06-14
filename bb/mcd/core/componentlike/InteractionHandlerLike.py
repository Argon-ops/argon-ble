import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)
from bb.mcd.core.command.CUSTOM_PG_AS_Collection import CUSTOM_PG_AS_Collection
from bb.mcd.core.componentlike.enablefilter.EnableFilterSettings import EnableFilterSettings
from bb.mcd.core.componentlike.enablefilter.SleepStateSettings import SleepStateSettings
from bb.mcd.util import ObjectLookupHelper

from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike

from bb.mcd.core.command import CommandsList
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU
from bb.mcd.core.command import AddCommandPopup
from bb.mcd.core.command import CUSTOM_PG_AS_Collection
from bb.mcd.core.componentlike.adjunct import AddSubtractExtraPlayables
from bb.mcd.core.componentlike.constants.ConfigSymbols import ApplyObjectSymbols

#region ADD REMOVE EXTRA PLAYABLES


def RemoveUnusedPlayableData(context):
    hl = context.scene.interactionHandlerLike
    if hl.numExtraPlayables >= AddSubtractExtraPlayables.MaxExtraPlayables:
        return
    for i in range(hl.numExtraPlayables + 1, AddSubtractExtraPlayables.MaxExtraPlayables):
        key = _Append(F"_playable{i}")
        ObjectLookupHelper._removeKeyFromSelected(key, context)


class CU_OT_NumExtraPlayables(bpy.types.Operator):
    """Num Extra Playables"""
    bl_idname = "view3d.num_extra_playables"
    bl_label = "Add or delete command slots"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "num_extra_playables"

    should_add: BoolProperty()

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        AddSubtractExtraPlayables.AddSubtractNumExtraPlayables(
            self.should_add, context)
        RemoveUnusedPlayableData(context)
        return {'FINISHED'}

# endregion


_suffixes = {

    #  TODO: it would be nice to eliminate the warning we get when no commands (i.e. playables) exists. 
    #    For now: just let this be an empty string. This forces the user to pick a command or make one.
    "_playable": "", # The default playable name is an empty string. not the first playable that exists's name. (see commented out line below)
                         # lambda:  bpy.context.scene.as_custom[0].name if len(bpy.context.scene.as_custom) > 0 else "",
    "_allows_interrupt": False,
    "_interaction_type": 0,
    "_is_trigger_enter_exit": False,
    "_enter_signal": 1.0,
    "_exit_signal": 0.0,
    "_is_click_hold": False,
    "_num_extra_playables": 0,
    "_playable1": "",
    "_playable2": "",
    "_playable3": "",
    "_playable4": "",
    "_playable5": "",
    "_click_feedback": False,
    "_scene_object_forward_target": ApplyObjectSymbols.ArgonThisObject(),
}


class InteractionHandlerDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key: str):
        return InteractionHandlerLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a: object, b: object) -> bool:
        return AbstractDefaultSetter._IsEqual("mel_interaction_handler_playable", a, b)

    @staticmethod
    def OnAddKey(key: str, val, targets):
        for suffix, defaultVal in _suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(
                _Append(suffix), defaultVal() if callable(defaultVal) else defaultVal, targets)

    @staticmethod
    def OnRemoveKey(key: str, targets):
        for suffix in _suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets=targets)

    @staticmethod
    def _EnforceHighlighterForClickHandlers(target):
        ''' Add a highlighter if this is a click handle and if there is none currently
        '''
        if not InteractionHandlerLike.GetTargetKey() in target:
            return
        try:
            # If this is a trigger type. Don't force this object to add a highlighter
            if target[_Append("_interaction_type")] == 1:
                return
        except:
            pass

        from bb.mcd.core.componentlike import InteractionHighlighterLike as ihl
        from bb.mcd.core.componentlike import BoxColliderLike as bcl
        from bb.mcd.lookup import KeyValDefault
        from bb.mcd.core.componentlike import StorageRouter

        # Add a highlighter if there was none
        if not ihl.InteractionHighlighterLike.HasBaseKey(target):
            default = KeyValDefault.getDefaultValue(
                ihl.InteractionHighlighterLike.GetTargetKey())
            StorageRouter.setDefaultValueOnTarget(
                ihl.InteractionHighlighterLike.GetTargetKey(), default, target)
            # Allow this highlighter to validate. May mean that it validates twice
            ihl.InteractionHighlighterDefaultSetter.Validate(target)

    @staticmethod
    def Validate(target):
        InteractionHandlerDefaultSetter._EnforceHighlighterForClickHandlers(
            target)

        # TODO: NOT HERE: the Commands list in the UI may show a command that is never actually written to the object.
        #   This happens when a command exists and they have just added an interaction handler like.
        #   Unfortunately, we'll need to reorganize how commands work. Because it's not ok to make people think that
        #    a command has been set (maybe the one that popped up was what they wanted and they didn't touch it)
        #    but never have that command actually be written to the object. Best to not give this impression


def _Append(suffix: str) -> str:
    return F"{InteractionHandlerLike.GetTargetKey()}{suffix}"


def _playablesItemCallback(self, context):
    playables = context.scene.as_custom
    return [(p.name, p.name, p.name) for p in playables]


def _playableEnumGetter(self, suffix="_playable"):
    playableName = CLU.getStringFromKey(_Append(suffix))
    playables = bpy.context.scene.as_custom
    # iterate with an index instead of using enumerate. Enumerate leads to glitchy behavior. (see below if curious)
    for i in range(len(playables)):
        if playables[i].name == playableName:
            return i
    return -1


# Must match TriggerInteractionHandler.cs EnterExitHandler
enterExitEnum = (
    ("ENTER", "Enter Only", "Only trigger enter starts this interaction"),
    ("EXIT", "Exit Only", "Only trigger exit starts this interaction"),
    ("ENTER_AND_EXIT", "Enter and Exit", "Enter and exit both start interactions. Enter sends the enter signal value, exit sends the exit signal value."))

interactionType = (
    ("CLICK", "Click", "Mouse clicks start this interaction"),
    ("TRIGGER", "Trigger", "Trigger collider events start this interaction"),
)

signalInputTypes = (
    ("Value", "Value Type", "A static value"),
    ("Playable", "Playable Type", "A playable"),
    ("Object", "Object Type", "an object")
)


class InteractionHandlerLike(SleepStateSettings, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_interaction_handler"

    @staticmethod
    def AcceptsKey(key: str):
        return key == InteractionHandlerLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        boxa = box.box()
        row = boxa.row()
        ihl = context.scene.interactionHandlerLike

        row = boxa.row()
        row.label(text="Commands")

        def drawPlayableRow(attrName, idx):
            # TODO: handle the case where no playables exist in the blend file's as_custom (not even 1)
            #  We are getting this warning:
            # WARN (bpy.rna): C:\Users\blender\git\blender-v320\blender.git\source\blender\python\intern\bpy_rna.c:1339 pyrna_enum_to_py: current value '0' matches no enum in 'InteractionHandlerLike', '', 'playable'
            attrib = getattr(ihl, attrName)
            spl = row.split(factor=.6)
            spl.label(text=F"{idx + 1} : {attrib}")
            spl.prop(ihl, attrName, text="")
            if attrib:
                row.operator(CUSTOM_PG_AS_Collection.CU_OT_PlayablePickPopup.bl_idname,
                             text="", icon="GREASEPENCIL").playableName = attrib

            plusOp = row.operator(
                AddCommandPopup.CU_OT_PlayableCreate.bl_idname, icon='ADD', text="New Command")
            plusOp.should_insert = True
            plusOp.insert_at_idx = idx

        row = boxa.row()
        drawPlayableRow("playable", 0)

        # Extra playables
        for i in range(ihl.numExtraPlayables):
            row = boxa.row()
            drawPlayableRow(F"playable{i+1}", i + 1)

        row = boxa.row()
        row.operator(CU_OT_NumExtraPlayables.bl_idname,
                     icon="ADD", text="").should_add = True
        row.operator(CU_OT_NumExtraPlayables.bl_idname,
                     icon="REMOVE", text="").should_add = False

        row = box.row()
        row.prop(ihl, "interactionType", text="Type")
        boxb = box.box()

        if ihl.interactionType == 'TRIGGER':
            row = boxb.row()
            row.prop(ihl, "isTriggerEnterExit")
            if not ihl.isTriggerEnterExit == 'EXIT':
                row = boxb.row()
                row.prop(ihl, "enterSignalInputType", text="Enter Signal")
                if ihl.enterSignalInputType == 'Value':
                    row.prop(ihl, "enterSignal", text="")
                elif ihl.enterSignalInputType == 'Object':
                    row.prop(ihl, "enterSignalProvider", text="")
                elif ihl.enterSignalInputType == 'Playable':
                    row.prop(ihl, "enterSignalPlayable", text="")

            if not ihl.isTriggerEnterExit == 'ENTER':
                row = boxb.row()
                row.prop(ihl, "exitSignalInputType", text="Exit Signal")
                if ihl.exitSignalInputType == 'Value':
                    row.prop(ihl, "exitSignal", text="")
                elif ihl.exitSignalInputType == 'Object':
                    row.prop(ihl, "exitSignalProvider")
                elif ihl.exitSignalInputType == 'Playable':
                    row.prop(ihl, "exitSignalPlayable", text="")

        elif ihl.interactionType == 'CLICK':
            row = boxb.row()
            row.prop(ihl, "isClickHold")
            if ihl.isClickHold:
                row = boxb.row()
                row.prop(ihl, "handleDiscreteClicksAlso",
                         text="Discrete Clicks Also")
                if ihl.handleDiscreteClicksAlso:
                    row.prop(ihl, "discreteClickFakeHoldTime",
                             text="Discrete Click Hold Time")

            boxbb = boxb.box()
            boxbb.row().prop(ihl, "shouldForwardInteractions",
                             text="Should Forward Interactions")
            if ihl.shouldForwardInteractions:
                boxbb.row().prop(ihl, "sceneObjectForwardTarget", text="Scene Objects Forward Taget")

            # TODO: "useRadius"
            row = boxb.row()
            row.prop(ihl, "enterSignal", text="Mouse Down Signal")
            if ihl.isClickHold:
                row = boxb.row()
                row.prop(ihl, "exitSignal", text="Mouse Up Signal")

            boxc = boxb.box()
            # TODO: add an option (not default) never destroy not even on receiving destroy messages
            boxc.row().prop(ihl, "selfDestructBehaviour", text="Self Destruct Behaviour")
            boxd = boxc.box()
            # if mcl.selfDestructBehaviour != "NeverSelfDestruct":
            # CONSIDER: there could be a self destruct directive neverSelfDestructAndEvenIgnoreDestroyMessages
            #   or a directive destroyMessagesOnly
            boxd.row().label(text="On Destroy Settings")
            boxd.row().prop(ihl, "destroyHighlighterAlso", text="Destroy Highlighter Also")
            boxd.row().prop(ihl, "destroyColliderAlso", text="Destroy Collider Also")
            boxd.row().prop(ihl, "destroyGameObjectAlso", text="Destroy Game Object Also")

            boxc.row().prop(ihl, "sleepBehaviour", text="Sleep Behaviour")

        # sleep also settings

        def dislaySleepAlsoSettings(box_ss):
            row = box_ss.row()
            row.prop(bpy.context.scene, "showSleepSpreader",
                     icon="TRIA_DOWN" if bpy.context.scene.showSleepSpreader else "TRIA_UP",
                     icon_only=True, emboss=False)
            row.label(text="Sleep Also")
            if not bpy.context.scene.showSleepSpreader:
                return

            if ihl.interactionType == 'CLICK':
                box_ss.row().prop(ihl, "sleepHighlighterAlso", text="Sleep Highlighter Also")
            box_ss.row().prop(ihl, "sleepColliderAlso", text="Sleep Collider Also")

        dislaySleepAlsoSettings(box.box())

    # TODO: when commands get deleted. they are not purged out of the properties that reference them
    #   don't think it's impractical or too expensive to iter over objects
    #   and purge any references to a deleted command...in most cases (what if someone has lots of objects...)

    playable: EnumProperty(
        items=lambda self, context: CLU.playablesItemCallback(context),
        get=lambda self: CLU.playableEnumIndex(_Append("_playable")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_playable"), bpy.context.scene.as_custom[value].name),
    )
    numExtraPlayables: IntProperty(
        get=lambda self: CLU.getIntFromKey(_Append("_num_extra_playables")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_num_extra_playables"), value)
    )
    playable1: EnumProperty(
        items=lambda self, context: CLU.playablesItemCallback(context),
        get=lambda self: CLU.playableEnumIndex(_Append("_playable1")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_playable1"), bpy.context.scene.as_custom[value].name),
    )
    playable2: EnumProperty(
        items=lambda self, context: CLU.playablesItemCallback(context),
        get=lambda self: CLU.playableEnumIndex(_Append("_playable2")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_playable2"), bpy.context.scene.as_custom[value].name),
    )
    playable3: EnumProperty(
        items=lambda self, context: CLU.playablesItemCallback(context),
        get=lambda self: CLU.playableEnumIndex(_Append("_playable3")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_playable3"), bpy.context.scene.as_custom[value].name),
    )
    playable4: EnumProperty(
        items=lambda self, context: CLU.playablesItemCallback(context),
        get=lambda self: CLU.playableEnumIndex(_Append("_playable4")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_playable4"), bpy.context.scene.as_custom[value].name),
    )
    playable5: EnumProperty(
        items=lambda self, context: CLU.playablesItemCallback(context),
        get=lambda self: CLU.playableEnumIndex(_Append("_playable5")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_playable5"), bpy.context.scene.as_custom[value].name),
    )

    interactionType: EnumProperty(
        items=interactionType,
        get=lambda self: CLU.getIntFromKey(_Append("_interaction_type")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_interaction_type"), value)
    )
    isTriggerEnterExit: EnumProperty(
        name="Trigger Enter Exit",
        items=enterExitEnum,
        get=lambda self: CLU.getIntFromKey(_Append("_is_trigger_enter_exit")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_is_trigger_enter_exit"), value)
    )

    enterSignalInputType: EnumProperty(
        items=signalInputTypes,
        description="TODO",
        get=lambda self: CLU.getIntFromKey(
            _Append("_enter_signal_input_type")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_enter_signal_input_type"), value)
    )
    enterSignalPlayable: EnumProperty(
        items=_playablesItemCallback,
        get=lambda self: _playableEnumGetter(self, "_enter_signal_playable"),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_enter_signal_playable"), bpy.context.scene.as_custom[value].name),
    )
    enterSignalProvider: PointerProperty(  
        name="Enter Signal Provider",
        description="TODO",
        type=bpy.types.Object,
        update=lambda self, context: CLU.setObjectPathStrangeAtKey(
            _Append("_enter_signal_provider"), self.enterSignalProvider)
        # TODO: need the dosey-doh to track when an object is renamed so that we can update the entry here
    )
    enterSignal: FloatProperty(
        name="Enter Signal",
        description="The value to send to the command with a click or on trigger enter.",
        get=lambda self: CLU.getFloatFromKey(_Append("_enter_signal")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_enter_signal"), value)
    )

    exitSignalInputType: EnumProperty(
        items=signalInputTypes,
        description="TODO",
        get=lambda self: CLU.getIntFromKey(_Append("_exit_signal_input_type")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_exit_signal_input_type"), value)
    )
    exitSignalPlayable: EnumProperty(
        items=_playablesItemCallback,
        get=lambda self: _playableEnumGetter(self, "_exit_signal_playable"),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_exit_signal_playable"), bpy.context.scene.as_custom[value].name),
    )
    exitSignalProvider: PointerProperty(  # TODO: change name and suffix to 'enterSignalObject' / '_enter_signal_object'
        name="Exit Signal Provider",
        description="TODO",
        type=bpy.types.Object,
        update=lambda self, context: CLU.setObjectPathStrangeAtKey(
            _Append("_exit_signal_provider"), self.enterSignalProvider)
        # TODO: need the dosey-doh to track when an object is renamed so that we can update the entry here
    )
    exitSignal: FloatProperty(
        name="Exit Signal",
        description="The value to send to the command on trigger exit.",
        get=lambda self: CLU.getFloatFromKey(_Append("_exit_signal")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_exit_signal"), value)
    )
    # radius : FloatProperty(
    #     description="defines the distance within which interaction is permitted. Negative values are interpretted as infinite",
    #     default=-1.0
    # )
    isClickHold: BoolProperty(
        name="Is Click and Hold",
        description="If true, track mouse down and up events (signal 1 for down, 0 for up). If false, only track down",
        get=lambda self: CLU.getBoolFromKey(_Append("_is_click_hold")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_is_click_hold"), value)
    )
    handleDiscreteClicksAlso: BoolProperty(
        description="If true, treat discrete clicks as though they were click-holds by adding an artificial hold time. If false, ignore discrete clicks (i.e. quick clicks with no hold time)",
        get=lambda self: CLU.getBoolFromKey(
            _Append("_handle_discrete_clicks_also")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_handle_discrete_clicks_also"), value)
    )
    discreteClickFakeHoldTime: FloatProperty(
        description="How long to wait before sending an up signal after getting a discrete click. In seconds",
        get=lambda self: CLU.getFloatFromKey(
            _Append("_discrete_click_fake_hold_time"), 0.2),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_discrete_click_fake_hold_time"), value)
    )

    # forward interactions
    shouldForwardInteractions: BoolProperty(
        description="If true, forward interactions to each object in an adjacent SceneObjectsReferencer",
        get=lambda self: CLU.getBoolFromKey(
            _Append("_should_forward_interactions")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_should_forward_interactions"), value)
    )

    sceneObjectForwardTarget: StringProperty(
        description="",
        get=lambda self: CLU.getStringFromKey(
            _Append("_scene_object_forward_target")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_scene_object_forward_target"), value)
    )

    # destroy behaviour
    selfDestructBehaviour: EnumProperty(
        description="When (if ever) should this handler self destruct",
        items=(
            ('On Receive Destroy Message', 'On Receive Destroy Message',
             'On Receive Destroy Message'),
            ('AfterFirstInteraction', 'After First Interaction',
             'After First Interaction'),
            ('NeverSelfDestruct', 'Never Self Destruct', 'Never Self Destruct'),
        ),
        get=lambda self: CLU.getIntFromKey(
            _Append("_self_destruct_behaviour")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_self_destruct_behaviour"), value)
    )
    destroyHighlighterAlso: BoolProperty(
        description="",
        get=lambda self: CLU.getBoolFromKey(
            _Append("_destroy_highlighter_also")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_destroy_highlighter_also"), value)
    )
    destroyColliderAlso: BoolProperty(
        description="",
        get=lambda self: CLU.getBoolFromKey(_Append("_destroy_collider_also")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_destroy_collider_also"), value)
    )
    destroyGameObjectAlso: BoolProperty(
        description="",
        get=lambda self: CLU.getBoolFromKey(
            _Append("_destroy_game_object_also")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_destroy_game_object_also"), value)
    )

    # sleep behaviour
    sleepBehaviour: EnumProperty(
        description="When (if ever) should this handler sleep",
        items=(
            ('NeverSleep', 'NeverSleep', 'NeverSleep'),
            ('AfterAnyInteraction', 'AfterAnyInteraction', 'AfterAnyInteraction')
        ),
        get=lambda self: CLU.getIntFromKey(_Append("_sleep_behaviour")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_sleep_behaviour"), value)
    )

    sleepHighlighterAlso: BoolProperty(
        description="When this handler receives a sleep signal, send the same signal (sleep or wake up) to the attached highlighter ",
        get=lambda self: CLU.getBoolFromKey(
            _Append("_sleep_highlighter_also")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_sleep_highlighter_also"), value)
    )
    sleepColliderAlso: BoolProperty(
        description="When this handler receives a sleep signal, enable or disable the attached collider (enable on awake, disable on sleep)",
        get=lambda self: CLU.getBoolFromKey(_Append("_sleep_collider_also")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_sleep_collider_also"), value)
    )


classes = (
    CU_OT_NumExtraPlayables,
    InteractionHandlerLike,
)


def register():
    from bpy.utils import register_class
    for c in classes:
        print(F"IntHandlerLike will register: {c}")
        register_class(c)

    bpy.types.Scene.interactionHandlerLike = bpy.props.PointerProperty(
        type=InteractionHandlerLike)
    bpy.types.Scene.showSleepSpreader = bpy.props.BoolProperty()


def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.interactionHandlerLike
    del bpy.types.Scene.showSleepSpreader
