import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)
from mcd.ui.actionstarterlist.CUSTOM_PG_AS_Collection import CUSTOM_PG_AS_Collection
from mcd.ui.componentlike.enablefilter.EnableFilterSettings import EnableFilterSettings
from mcd.ui.componentlike.enablefilter.SleepStateSettings import SleepStateSettings
from mcd.util import ObjectLookupHelper

from mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike

from mcd.ui.actionstarterlist import ActionStarterList
from mcd.ui.componentlike import AbstractDefaultSetter
from mcd.ui.componentlike.util import ComponentLikeUtils as CLU
from mcd.ui.actionstarterlist import PlusActionStarterPopup
from mcd.ui.actionstarterlist import CUSTOM_PG_AS_Collection

import json

# TODO: option to add a new Playable from an interation handler
# TODO: option to edit the chosen playable from interaction handler

class InteractionHandlerDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return InteractionHandlerLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual("mel_interaction_handler_playable", a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        default = AbstractDefaultSetter._GetDefaultFromPrefs(key)
        try:
            AbstractDefaultSetter._SetKeyValOnTargets("mel_interaction_handler_playable", default['playable'], targets)
            AbstractDefaultSetter._SetKeyValOnTargets(_Append("_allows_interrupt"), default['allows_interrupt'], targets)
            AbstractDefaultSetter._SetKeyValOnTargets(_Append("_enter_signal"), default['enter_signal'], targets)
            AbstractDefaultSetter._SetKeyValOnTargets(_Append("_interaction_type"), default['interaction_type'], targets)
            AbstractDefaultSetter._SetKeyValOnTargets(_Append("_command_behaviour_type"), 0, targets) # TODO : add formal defaults for these too
            AbstractDefaultSetter._SetKeyValOnTargets(_Append("_enter_signal"), 1, targets)
            AbstractDefaultSetter._SetKeyValOnTargets(_Append("_exit_signal"), 0, targets)
            AbstractDefaultSetter._SetKeyValOnTargets(_Append("_is_click_hold"), 0, targets)
            
        except BaseException as e:
            print(F" failed to set default {str(e)}")
            print(F"default keys: {default.keys()}")

    @staticmethod
    def OnRemoveKey(key : str, targets):
        suffixes = ("_playable", "_allows_interrupt", "_interaction_type", "_is_trigger_enter_exit", "_command_behaviour_type", \
                    "_enter_signal", "_exit_signal", "_is_click_hold", "_num_extra_playables", "_playable1", "_playable2", "_playable3", "_playable4", "_playable5")

        for suffix in suffixes:
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)

def _Append(suffix : str) -> str:
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
enterExitEnum=(
            ("ENTER", "Enter Only", "Only trigger enter starts this interaction"),
            ("EXIT", "Exit Only", "Only trigger exit starts this interaction"),
            ("ENTER_AND_EXIT", "Enter and Exit", "Enter and exit both start interactions. Enter sends the enter signal value, exit sends the exit signal value."))

interactionType=(
    ("CLICK", "Click", "Mouse clicks start this interaction"),
    ("TRIGGER", "Trigger", "Trigger collider events start this interaction"),
    )

signalInputTypes=(
    ("Value", "Value Type", "A static value"),
    ("Playable", "Playable Type", "A playable"),
    ("Object", "Object Type", "an object")
    )

class CU_OT_NumExtraPlayables(bpy.types.Operator):
    """Num Extra Playables"""
    bl_idname = "view3d.num_extra_playables"
    bl_label = "Change the number of playables"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "num_extra_playables"

    should_add : BoolProperty()

    @classmethod
    def poll(cls, context):
        return True 
    
    def invoke(self, context, event):
        hl = context.scene.interactionHandlerLike
        if self.should_add and hl.numExtraPlayables < 5:
            hl.numExtraPlayables = hl.numExtraPlayables + 1
            print(F"will add now num is: {hl.numExtraPlayables}")
        if not self.should_add and hl.numExtraPlayables > 0:
            hl.numExtraPlayables = hl.numExtraPlayables - 1

        print(F"num is: {hl.numExtraPlayables}")
        
        return {'FINISHED'}


# class InteractionHandlerLike(EnableFilterSettings, AbstractComponentLike):
class InteractionHandlerLike(SleepStateSettings, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_interaction_handler"

    @staticmethod
    def AcceptsKey(key : str):
        return key == InteractionHandlerLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        mcl = context.scene.interactionHandlerLike
        row = box.row()
        row.prop(mcl, "playable", text="Playable")

        # TODO: add rows
        if mcl.playable: # is not None: # 'not None' won't catch empty strings
            row.operator(CUSTOM_PG_AS_Collection.CU_OT_PlayablePickPopup.bl_idname, text="", icon="GREASEPENCIL").playableId = context.scene.as_custom[mcl.playable].internalId
        # Extra playables
        for i in range(mcl.numExtraPlayables):
            row = box.row()
            attrName = F"playable{i+1}"
            row.prop(mcl, F"playable{i+1}", text=F"Playable {i+1}")
            attrib = getattr(mcl, attrName)
            if attrib: # mcl.playable:
                row.operator(CUSTOM_PG_AS_Collection.CU_OT_PlayablePickPopup.bl_idname, text="", icon="GREASEPENCIL").playableId = context.scene.as_custom[attrib].internalId
        row = box.row()
        row.operator(CU_OT_NumExtraPlayables.bl_idname, icon="ADD", text="").should_add = True
        row.operator(CU_OT_NumExtraPlayables.bl_idname, icon="REMOVE", text="").should_add = False

        row = box.row()
        row.operator(PlusActionStarterPopup.CU_OT_PlayableCreate.bl_idname, icon='ADD', text="New Playable")

        row = box.row()
        row.prop(mcl, "interactionType", text="Type")
        boxb = box.box()
        row = boxb.row()


        if mcl.interactionType == 'TRIGGER':
            row.prop(mcl, "isTriggerEnterExit")
            if not mcl.isTriggerEnterExit == 'EXIT':
                row = boxb.row()
                row.prop(mcl, "enterSignalInputType", text="Enter Signal")
                if mcl.enterSignalInputType == 'Value':
                    row.prop(mcl, "enterSignal", text="")
                elif mcl.enterSignalInputType == 'Object':
                    row.prop(mcl, "enterSignalProvider", text="")
                elif mcl.enterSignalInputType == 'Playable':
                    row.prop(mcl, "enterSignalPlayable", text="")

            if not mcl.isTriggerEnterExit == 'ENTER':
                row = boxb.row()
                row.prop(mcl, "exitSignalInputType", text="Exit Signal")
                if mcl.exitSignalInputType == 'Value':
                    row.prop(mcl, "exitSignal", text="")
                elif mcl.exitSignalInputType == 'Object':
                    row.prop(mcl, "exitSignalProvider")
                elif mcl.exitSignalInputType == 'Playable':
                    row.prop(mcl, "exitSignalPlayable", text="")


        elif mcl.interactionType == 'CLICK':
            row.prop(mcl, "isClickHold")
            if mcl.isClickHold:
                row = boxb.row()
                row.prop(mcl, "handleDiscreteClicksAlso", text="Discrete Clicks Also")
                if mcl.handleDiscreteClicksAlso:
                    row.prop(mcl, "discreteClickFakeHoldTime", text="Discrete Click Hold Time")
            # row = boxb.row()
            # row.prop(mcl, "radius")
            row = boxb.row()
            row.prop(mcl, "enterSignal")
            if mcl.isClickHold:
                row = boxb.row()
                row.prop(mcl, "exitSignal")

            boxc = boxb.box()
            boxc.row().prop(mcl, "selfDestructBehaviour", text="Self Destruct Behaviour")
            if mcl.selfDestructBehaviour != "NeverSelfDestruct":
                boxc.row().prop(mcl, "destroyHighlighterAlso", text="Destroy Highlighter Also")
                boxc.row().prop(mcl, "destroyColliderAlso", text="Destroy Collider Also")

        # sleep also settings
        def dislaySleepAlsoSettings(box_ss):
            if mcl.interactionType == 'CLICK':
                box_ss.row().prop(mcl, "sleepHighlighterAlso", text="Sleep Highlighter Also")
            box_ss.row().prop(mcl, "sleepColliderAlso", text="Sleep Collider Also")
        
        dislaySleepAlsoSettings(box.box())
        # mcl.displayEnableSettings(box)
        
        # TRIGGER ENTER EXIT
        # CONSIDER : It starts to make more sense to 
        #   have click handlers and trigger handlers be separate classes...
        #    We are getting two layers of conditions with this current scheme...


    playable : EnumProperty(
        # _playablesItemCallback, # TODO: use the CLU version of this. TIDY! # also to. finish designing SliderColliderLike
        items=lambda self, context : CLU.playablesItemCallback(context),
        get=lambda self : CLU.playableEnumIndex(_Append("_playable")),  # _playableEnumGetter(self, "_playable"),
        # post mortem: there's probably a way, but trying to store the playable's internalId, while displaying its name is 
        #   not working. 
        # set=lambda self, value : CLU.setValueAtKey(_Append("_playable"), bpy.context.scene.as_custom[value].internalId),
        set=lambda self, value : CLU.setValueAtKey(_Append("_playable"), bpy.context.scene.as_custom[value].name),
    )
    numExtraPlayables : IntProperty(
        get=lambda self : CLU.getIntFromKey(_Append("_num_extra_playables")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_num_extra_playables"), value)
    )
    playable1 : EnumProperty(
        items=lambda self, context : CLU.playablesItemCallback(context),
        get=lambda self : CLU.playableEnumIndex(_Append("_playable1")),  # _playableEnumGetter(self, "_playable"),
        set=lambda self, value : CLU.setValueAtKey(_Append("_playable1"), bpy.context.scene.as_custom[value].name),
    )
    playable2 : EnumProperty(
        items=lambda self, context : CLU.playablesItemCallback(context),
        get=lambda self : CLU.playableEnumIndex(_Append("_playable2")),  # _playableEnumGetter(self, "_playable"),
        set=lambda self, value : CLU.setValueAtKey(_Append("_playable2"), bpy.context.scene.as_custom[value].name),
    )
    playable3 : EnumProperty(
        items=lambda self, context : CLU.playablesItemCallback(context),
        get=lambda self : CLU.playableEnumIndex(_Append("_playable3")),  # _playableEnumGetter(self, "_playable"),
        set=lambda self, value : CLU.setValueAtKey(_Append("_playable3"), bpy.context.scene.as_custom[value].name),
    )
    playable4 : EnumProperty(
        items=lambda self, context : CLU.playablesItemCallback(context),
        get=lambda self : CLU.playableEnumIndex(_Append("_playable4")),  # _playableEnumGetter(self, "_playable"),
        set=lambda self, value : CLU.setValueAtKey(_Append("_playable4"), bpy.context.scene.as_custom[value].name),
    )
    playable5 : EnumProperty(
        items=lambda self, context : CLU.playablesItemCallback(context),
        get=lambda self : CLU.playableEnumIndex(_Append("_playable5")),  # _playableEnumGetter(self, "_playable"),
        set=lambda self, value : CLU.setValueAtKey(_Append("_playable5"), bpy.context.scene.as_custom[value].name),
    )
    
    interactionType : EnumProperty(
        items=interactionType,
        get=lambda self : CLU.getIntFromKey(_Append("_interaction_type")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_interaction_type"), value)
    )
    isTriggerEnterExit : EnumProperty(
        name="Trigger Enter Exit",
        items=enterExitEnum,
        get=lambda self : CLU.getIntFromKey(_Append("_is_trigger_enter_exit")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_is_trigger_enter_exit"), value)
    )

    enterSignalInputType : EnumProperty(
        items=signalInputTypes,
        description="TODO",
        get=lambda self : CLU.getIntFromKey(_Append("_enter_signal_input_type")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_enter_signal_input_type"), value)
    )
    enterSignalPlayable : EnumProperty(
        items=_playablesItemCallback,
        get=lambda self : _playableEnumGetter(self, "_enter_signal_playable"),
        set=lambda self, value : CLU.setValueAtKey(_Append("_enter_signal_playable"), bpy.context.scene.as_custom[value].name),
    )
    enterSignalProvider : PointerProperty( #TODO: change name and suffix to 'enterSignalObject' / '_enter_signal_object'
        name="Enter Signal Provider",
        description="TODO",
        type=bpy.types.Object,
        update=lambda self, context : CLU.setObjectPathStrangeAtKey(_Append("_enter_signal_provider"), self.enterSignalProvider)
        # TODO: need the dosey-doh to track when an object is renamed so that we can update the entry here
    )
    enterSignal : FloatProperty(
        name="Enter Signal",
        description="The value to send to the command with a click or on trigger enter.",
        get=lambda self : CLU.getFloatFromKey(_Append("_enter_signal")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_enter_signal"), value)
    )

    exitSignalInputType : EnumProperty(
        items=signalInputTypes,
        description="TODO",
        get=lambda self : CLU.getIntFromKey(_Append("_exit_signal_input_type")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_exit_signal_input_type"), value)
    )
    exitSignalPlayable : EnumProperty(
        items=_playablesItemCallback,
        get=lambda self : _playableEnumGetter(self, "_exit_signal_playable"),
        set=lambda self, value : CLU.setValueAtKey(_Append("_exit_signal_playable"), bpy.context.scene.as_custom[value].name),
    )
    exitSignalProvider : PointerProperty( #TODO: change name and suffix to 'enterSignalObject' / '_enter_signal_object'
        name="Exit Signal Provider",
        description="TODO",
        type=bpy.types.Object,
        update=lambda self, context : CLU.setObjectPathStrangeAtKey(_Append("_exit_signal_provider"), self.enterSignalProvider)
        # TODO: need the dosey-doh to track when an object is renamed so that we can update the entry here
    )
    exitSignal : FloatProperty(
        name="Exit Signal",
        description="The value to send to the command on trigger exit.",
        get=lambda self : CLU.getFloatFromKey(_Append("_exit_signal")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_exit_signal"), value)
    )
    # radius : FloatProperty(
    #     description="defines the distance within which interaction is permitted. Negative values are interpretted as infinite",
    #     default=-1.0
    # )
    isClickHold : BoolProperty(
        name="Is Click and Hold",
        description="If true, track mouse down and up events (signal 1 for down, 0 for up). If false, only track down",
        get=lambda self : CLU.getBoolFromKey(_Append("_is_click_hold")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_is_click_hold"), value)
    )
    handleDiscreteClicksAlso : BoolProperty(
        description="If true, treat discrete clicks as though they were click-holds by adding an artificial hold time. If false, ignore discrete clicks (i.e. quick clicks with no hold time)",
        get=lambda self : CLU.getBoolFromKey(_Append("_handle_discrete_clicks_also")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_handle_discrete_clicks_also"), value)
    )
    discreteClickFakeHoldTime : FloatProperty(
        description="How long to wait before sending an up signal after getting a discrete click. In seconds",
        get=lambda self : CLU.getFloatFromKey(_Append("_discrete_click_fake_hold_time"), 0.2),
        set=lambda self, value : CLU.setValueAtKey(_Append("_discrete_click_fake_hold_time"))
    )

    # destroy behaviour
    selfDestructBehaviour : EnumProperty (
        items=(
            ('NeverSelfDestruct', 'Never Self Destruct', 'Never Self Destruct'),
            ('AfterFirstInteraction', 'After First Interaction', 'After First Interaction'),
        ),
        get=lambda self : CLU.getIntFromKey(_Append("_self_destruct_behaviour")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_self_destruct_behaviour"), value)
    )
    destroyHighlighterAlso : BoolProperty (
        description="",
        get=lambda self : CLU.getBoolFromKey(_Append("_destroy_highlighter_also")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_destroy_highlighter_also"), value)
    )
    destroyColliderAlso : BoolProperty (
        description="",
        get=lambda self : CLU.getBoolFromKey(_Append("_destroy_collider_also")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_destroy_collider_also"), value)
    )

    sleepHighlighterAlso : BoolProperty(
        description="When this handler receives a sleep signal, send the same signal (sleep or wake up) to the attached highlighter ",
        get=lambda self : CLU.getBoolFromKey(_Append("_sleep_highlighter_also")),
        set=lambda   self, value : CLU.setValueAtKey(_Append("_sleep_highlighter_also"), value)
    )
    sleepColliderAlso : BoolProperty(
        description="When this handler receives a sleep signal, send the same signal (sleep or wake up) to the attached collider",
        get=lambda self : CLU.getBoolFromKey(_Append("_sleep_collider_also")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_sleep_collider_also"), value)
    )
  
    
    

classes = (
    InteractionHandlerLike,
    CU_OT_NumExtraPlayables,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.interactionHandlerLike = bpy.props.PointerProperty(type=InteractionHandlerLike)


def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.interactionHandlerLike

