
import bpy

from bpy.props import (IntProperty,
                       BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty,
                       PointerProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)
import json

from mcd.util import ObjectLookupHelper
from mcd.shareddataobject import SharedDataObject
from mcd.ui.actionstarterlist import OT_TarAnimsList

from mcd.ui.componentlike.enablereceiverbutton import EnableReceiverButton
from mcd.util import DisplayHelper


class AS_OT_AddToTargets(Operator):
    """Edit targets per playable """
    bl_idname = "custom.per_playable_targets_actions"
    bl_label = "Targets"
    bl_description = "Add remove playable targets"
    bl_options = {'REGISTER'}

    # action: bpy.props.EnumProperty(
    #     items=(
    #         ('UP', "Up", ""),
    #         ('DOWN', "Down", ""),
    #         ('REMOVE', "Remove", ""),
    #         ('ADD', "Add", "")))
    
    playableName: StringProperty(
        name="playable_name"
    )

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.as_custom_index

        try:
            playable = scn.as_custom[self.playableName] # scn.as_custom[idx]
            print(F"found playable {playable.name} {playable.playableType} want pl name: {self.playableName}")
        except IndexError:
            pass
        else:
            next = playable.targets.add() 
            next.name = F"{len(playable.targets)}-targ"
            _ASJson.updateExtraTargets(playable)
            print(F" we did it")
              
        return {"FINISHED"}
    

class AS_OT_RemoveFromTargets(Operator):
    """Edit targets per playable """
    bl_idname = "custom.per_playable_targets_remove_action"
    bl_label = "Targets"
    bl_description = "Add remove playable targets"
    bl_options = {'REGISTER'}

    playableNameConcatTargetName: StringProperty(
        name="playable_name"
    )

    def invoke(self, context, event):
        scn = context.scene
        names = self.playableNameConcatTargetName.split(',,,')
        playableName = names[0]
        targetName = names[1]

        try:
            playable = scn.as_custom[playableName] # scn.as_custom[idx]
            target = playable.targets[targetName]
            print(F"found target {target.name} with obj : {target.object.name if target.object != None else '<no object>'} \
                   from playable {playable.name} want pl name: {self.playableNameConcatTargetName}")
        except IndexError:
            pass
        else:
            idx = ObjectLookupHelper._indexOf(playable.targets, target)
            playable.targets.remove(idx)
            _ASJson.updateExtraTargets(playable)
              
        return {"FINISHED"}

def getPlayableTypes():
    return (
        ('0', 'Event Only', 'Nothing to play. Just generate an event'),
        ('1', 'Animation', 'Animation and/or audio'),
        ('2', 'Looping Animation', 'Looping animation and/or audio'),
        ('3', 'Message', 'Send a signal to a target object'),
        ('4', 'Camera Shake', 'Trigger a camera shake'),
        ('5', 'Screen Overlay', 'Screen overlay'),
    )

class _ASJson:
    __DATA_KEY_SUFFIX__="_data"

    def GetActionStarterSharedObject():
        ob = SharedDataObject.getSharedDataObjectWithName("zDuksGames_AS_SharedObject")
        ob["mel_action_starter"] = 1 # tag object so that the importer will see it
        return ob

    def SharedASObjectExists():
        return SharedDataObject.objectExists("zDuksGames_AS_SharedObject")

    @staticmethod
    def _getASBaseKey(actionName : str) ->str:
        # prefix must match the import script in unity addon
        return F"mel_AS_{actionName}"

    @staticmethod
    def _getDataKey(actionName : str):
        return F"{_ASJson._getASBaseKey(actionName)}{_ASJson.__DATA_KEY_SUFFIX__}"

    @staticmethod
    def _getJSONString(actionName : str, sharedDataObj):
        dataKey = _ASJson._getDataKey(actionName)
        if dataKey in sharedDataObj:
            return sharedDataObj[dataKey]
        return ""

    @staticmethod
    def _getData(actionName : str, ob):
        jsonStr = _ASJson._getJSONString(actionName, ob)
        if not jsonStr:
            return None
        return json.loads(jsonStr)

    @staticmethod
    def _getValueAt(actionName : str, key, ob):
        data = _ASJson._getData(actionName, ob)
        if not data:
            return None
        if key not in data.keys():
            return None
        return data[key]
    
    @staticmethod
    def _copyFromTo(fromActionName : str, toActionName : str, ob):
        jsonStr = _ASJson._getJSONString(fromActionName, ob)
        ob[_ASJson._getDataKey(toActionName)] = jsonStr

    @staticmethod
    def getValueAt(collectionSelf, jsonkey):
        ob = _ASJson.GetActionStarterSharedObject()
        return _ASJson._getValueAt(collectionSelf.name, jsonkey, ob)

    @staticmethod
    def getStringAt(collectionSelf, jsonkey):
        result = _ASJson.getValueAt(collectionSelf, jsonkey)
        return result if result else ""
    
    @staticmethod
    def getFloatAt(collectionSelf, jsonkey, default=0.0):
        result = _ASJson.getValueAt(collectionSelf, jsonkey)
        return result if isinstance(result, float) else default
    
    @staticmethod
    def getIntAt(collectionSelf, jsonkey, default=-1):
        result = _ASJson.getValueAt(collectionSelf, jsonkey)
        return result if isinstance(result, int) else default
    
    @staticmethod 
    def getBoolAt(collectionSelf, jsonKey, default=False):
        result = _ASJson.getValueAt(collectionSelf, jsonKey)
        return result if isinstance(result, bool) else default

    @staticmethod
    def _setValueAt(playableName : str, key, value, sharedDataObj):
        data = _ASJson._getData(playableName, sharedDataObj)
        if data is None:
            data = {}
        data[key] = value
        dataKey = _ASJson._getDataKey(playableName)
        sharedDataObj[dataKey] = json.dumps(data)

    @staticmethod
    def setValueAt(collectionSelf, key, value):
        _ASJson.setValueWithPlayableName(collectionSelf.name, key, value)

    @staticmethod
    def setValueWithPlayableName(playableName, key, value):
        ob = _ASJson.GetActionStarterSharedObject() 
        _ASJson._setValueAt(playableName, key, value, ob)

    @staticmethod
    def updateFromPointer(collectionSelf, key, pointerObject):
        if pointerObject is None:
            _ASJson.setValueAt(collectionSelf, key, "")
            return
        _ASJson.setValueAt(collectionSelf, key, pointerObject.name)
  
    @staticmethod
    def updatePathFromPointer(collectionSelf, pathKey, pointerObject):
        if pointerObject is None:
            _ASJson.setValueAt(collectionSelf, pathKey, "")
            return
        parents = ObjectLookupHelper._hierarchyToString(pointerObject)
        _ASJson.setValueAt(collectionSelf, pathKey, parents)

    @staticmethod
    def updateObjectAndPath(collectionSelf, objkey, pathKey, pointerObject):
        _ASJson.updateFromPointer(collectionSelf, objkey, pointerObject)
        _ASJson.updatePathFromPointer(collectionSelf, pathKey, pointerObject)

    @staticmethod
    def updateExtraTargets(collectionSelf):
        extraPaths = [(ObjectLookupHelper._hierarchyToStringStrange(target.object) if target.object is not None else "") for target in collectionSelf.targets]
        _ASJson.setValueAt(collectionSelf, "target_paths", extraPaths)
    
    @staticmethod
    def updateAllPlayableExtraTargets(context):
        print(F"update all ex targs")
        for playable in context.scene.as_custom:
            _ASJson.updateExtraTargets(playable)

    @staticmethod 
    def setNextName(collectionSelf, value):
        if not value:
            print(F"not value")
            return
        shared = _ASJson.GetActionStarterSharedObject()
        _ASJson._copyFromTo(collectionSelf.name, value, shared)
        dataKey = _ASJson._getDataKey(collectionSelf.name)
        if dataKey in shared:
            del shared[_ASJson._getDataKey(collectionSelf.name)]
        collectionSelf.name = value
        _ASJson.setValueAt(collectionSelf, "playableId", value)


class PG_AS_TargetsPropGroup(PropertyGroup):
    """ Ble needs the targets to be wrapped in a property group"""
    name : StringProperty(
        name="Name",
    )
    object : PointerProperty(
        name="object",
        type = bpy.types.Object,
        update = lambda self, context : _ASJson.updateAllPlayableExtraTargets(context)
    )


class CUSTOM_PG_AS_Collection(PropertyGroup):

    @staticmethod
    def InitPlayable(playable):
        """Make sure a few defaults are written to the storage object"""
        _ASJson.setValueAt(playable, "playableId", playable.name)
        _ASJson.setValueAt(playable, "playableType", int(playable.playableType))
        playable.internalId = F"ID_{playable.name}"

    name : StringProperty(
        name="name",
        description = "the name of the action starter ",
        update=lambda self, context : _ASJson.setValueAt(self, "playableId", self.name))
    
    nextName : StringProperty(
        name="next_name",
        description="the name of the playable",
        get=lambda self :  _ASJson.getStringAt(self, "playableId"),
        set=lambda self, value : _ASJson.setNextName(self, value),
    )

    internalId : StringProperty(
        name="internal id"
    )
    
    # TODO: fields for an object to own the animator (or bool option please generate for me)
    # TODO: fields for an object to own the audioSource (or bool option please use some audio mixer attached to camera)

    # TODO: for animation playables, list of animations / object targets
    #  WANT
    # tarAnims : CollectionProperty(type=OT_TarAnimsList.PG_AS_ObjectAnimPair)
    # tarAnimIndex : IntProperty() 

    playableType : EnumProperty( # Should be an enum: AnimationAndAudio, EventOnly=0
        items=getPlayableTypes(),
        description="",
        default=1, #TODO use this
        get=lambda self : _ASJson.getIntAt(self, "playableType", 1),
        set=lambda self, value : _ASJson.setValueAt(self, "playableType", value)                                           
    )
    commandBehaviourType : EnumProperty(
        name="Behaviour",
        description="What does the playable do each time interaction is initiated",
        items=(
            ('RestartForwards', 'RestartForwards', 'Just restart play from the beginning.'),
            ('ToggleAndRestart', 'ToggleAndRestart', 'If the playback cursor is closer to the end, play backwards starting from the end. Else play forwards from the beginning.'),
            ('FlipDirections', 'FlipDirections', 'Switch between forward and reverse with each invocation. Don\'t do anything to the playback position.'),
        ),
        get=lambda self : _ASJson.getIntAt(self, "command_behaviour_type", 0), # CLU.getIntFromKey(_Append("_command_behaviour_type")),
        set=lambda self, value : _ASJson.setValueAt(self, "command_behaviour_type", value) # CLU.setValueAtKey(_Append("_command_behaviour_type"), value)
    )

    customInfo : StringProperty(
        name="Custom Info",
        description="Optional. Use any way you want in a CommandEvent handler. The contents of this field will be copied to the 'CustomInfo' field in each CommandEvent sent from this playable",
        get=lambda self : _ASJson.getStringAt(self, "custom_info"),
        set=lambda self, value : _ASJson.setValueAt(self, "custom_info", value)
    )

    allowsInterrupts : BoolProperty(
        name="Allows Interrupts",
        description="Should subsequent interactions interrupt a command that is already running. Looping animations that don't allow interrupts will never stop playing.",
        get=lambda self : _ASJson.getBoolAt(self, "allowsInterrupts", False),
        set=lambda self, value : _ASJson.setValueAt(self, "allowsInterrupts", value)
    )
    
    # BUGGG: its possible to choose a playableType like animation, assign a target then switch to (e.g.) Screen Overlay for the playable type
    #   The targets will never get deleted but they won't be visible, editable either.
    #  Best if: we force the user to specify they pType on creation and they can't change it after. (Could show the type in the row view to reinforce 
    #    how much it is stuck to being that type.)
    targets : CollectionProperty(
        name="Targets",
        type=PG_AS_TargetsPropGroup,
    )

    animAction : PointerProperty(
        name="action name",
        type=bpy.types.Action,
        poll = lambda self, action : True, # _isActionInList(self, action), 
        update=lambda self, context : _ASJson.updateFromPointer(self, "anim_name", self.animAction)
    )
    # TODO: consider adding an audio only type playable
    audioClipName : StringProperty(
        name="audio clip name",
        description="the name of a clip in your Unity project.",
        get=lambda self : _ASJson.getStringAt(self, "audio_name"),
        set=lambda self, value : _ASJson.setValueAt(self, "audio_name", value)
    )
    loopAudio : BoolProperty(
        name="Loop Audio",
        description="If true, audio will loop while animating. If false, audio will play once. (Once per loop, if this is a looping animation.) If there is only audio, this option does nothing.  ",
        get=lambda self : _ASJson.getBoolAt(self, "loop_audio"),
        set=lambda self, value : _ASJson.setValueAt(self, "loop_audio", value)
    )

    audioAlwaysForwards : BoolProperty(
        name="Audio Always Forwards",
        description="Should audio play forwards even when the animation is playing backwards",
        get=lambda self : _ASJson.getBoolAt(self, "audio_always_forwards"),
        set=lambda self, value : _ASJson.setValueAt(self, "audio_always_forwards", value)
    )
    autoAddEnableReceiver : BoolProperty(
        name="Add Enable Receiver",
        description="Add an Enable Receiver component on the target objects. Enable Receivers enable/disable their IEnablable targets based on their interpretation of the signal",
        get=lambda self : _ASJson.getBoolAt(self, "auto_add_enable_receiver"),
        set=lambda self, value : _ASJson.setValueAt(self, "auto_add_enable_receiver", value)
    )

    # These two props (applyToChildren and setInitialState) are duplicated in EnableReceiverLike.
    #  Setting these will result in an EnableMessageReceiver being applied to the target object in Unity
    #   Adding an EnableReceiverLike in blender will have the same effect.
    #    The point is we want to give the user a convenient shortcut for adding this component that they probably want
    applyToChildren : BoolProperty(
        name="Apply to Children",
        description="Should search children for IEnableables",
        get=lambda self : _ASJson.getBoolAt(self, "apply_to_children"),
        set=lambda self, value : _ASJson.setValueAt(self, "apply_to_children", value)
    )
    setInitialState : EnumProperty(
        items=(
            ('DONT', 'Don\'t set initial state', 'Do nothing at start up'),
            ('TRUE', 'Enabled', 'Set enabled at start up'),
            ('FALSE', 'Disabled', 'Set disabled at start up')
        ),
        get=lambda self : _ASJson.getIntAt(self, "set_initial_state" ),
        set=lambda self, value : _ASJson.setValueAt(self, "set_initial_state", value)
    )

    autoAddScalarReceiver : BoolProperty(
        name="Add Scalar Receiver",
        description="Add a Scalar Receiver component to the target objects",
        get=lambda self : _ASJson.getBoolAt(self, "auto_add_scalar_receiver"),
        set=lambda self, value : _ASJson.setValueAt(self, "auto_add_scalar_receiver", value)
    )
    applyToChildrenScalar : BoolProperty(
        name="Apply to Children Scalar",
        description="Should scalar receiver search children for scalar targets",
        get=lambda self : _ASJson.getBoolAt(self, "apply_to_children_scalar"),
        set=lambda self, value : _ASJson.setValueAt(self, "apply_to_children_scalar", value)
    )
    setInitialStateScalar : BoolProperty(
        description="Should the scalar receiver initialize its targets with a value at Start",
        get=lambda self : _ASJson.getBoolAt(self, "set_inital_state_scalar"),
        set=lambda self, value : _ASJson.setValueAt(self, "set_initial_state_scalar", value)
    )
    scalarInitialState : FloatProperty(
        description="Defines the value to set the scalar targets to at Start",
        get=lambda self : _ASJson.getFloatAt(self, "scalar_initial_state"),
        set=lambda self, value : _ASJson.setValueAt(self, "scalar_initial_state", value)
    )

    #screen overlay
    overlayName : StringProperty(
        description="The name of the UIDocument element to overlay. (Classic GUI not supported at the moment sorry)",
        get=lambda self : _ASJson.getStringAt(self, "overlay_name"),
        set=lambda self, value : _ASJson.setValueAt(self, "overlay_name", value)
    )

    # camera shake
    shakeDuration : FloatProperty(
        description="Camera shake duration in seconds",
        get=lambda self : _ASJson.getFloatAt(self, "shake_duration", 0.8),
        set=lambda self, value : _ASJson.setValueAt(self, "shake_duration", value)
    )

    def draw(self, layout):
        # Row view
        split = layout.row().split(factor=.65)
        split.label(text=self.name)
        split.operator(CU_OT_PlayablePickPopup.bl_idname, text="", icon="GREASEPENCIL").playableId = self.internalId


class CU_OT_PlayablePickPopup(bpy.types.Operator):
    """Edit a Playable. At the moment this just duplicates the in-row edit options. Use if we need more complex options"""
    bl_idname = "view3d.viewport_edit_playable"
    bl_label = "Edit Playable"
    bl_options = {'REGISTER', 'UNDO'}
    
    playableId : bpy.props.StringProperty(name="internalId") # bpy.props.IntProperty(name="playabeIdx")

    @classmethod
    def poll(cls, context):
        return True 
        
    def execute(self, context):
        info = '%s bye' % ("BYE")
        self.report({'INFO'}, info)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        dpi = context.preferences.system.pixel_size
        ui_size = context.preferences.system.ui_scale
        dialog_size = int(450 * dpi * ui_size)
        return wm.invoke_props_dialog(self, width=dialog_size)
    
    def _findPlayable(self, as_custom):
        for pl in as_custom:
            if pl.internalId == self.playableId:
                return pl
        return None

    def drawTargetsList(self, playable, box):
        # box = self.layout.box()  
        rowb = box.row()
        rowb.label(text="Targets") 
        
        for targ in playable.targets:
            rowb = box.row()
            rowb.prop(targ, "object", text='target')
            rowb.operator(AS_OT_RemoveFromTargets.bl_idname, icon='X', text="").playableNameConcatTargetName = F"{playable.name},,,{targ.name}"
        rowb=box.row()
        rowb.operator(AS_OT_AddToTargets.bl_idname, icon='ADD', text="ADD" ).playableName = playable.name # self.playableName
        # TODO WARNING IF extra targets len is zero or no non None targets


    def draw(self, context):
        scn = context.scene
        # TODO: internalId / playableId is more flexible i guess, but we're not using. only added it to facilitate
        #   changing playableNames. it worked but there were other problems and in the end we decided to ban renaming playables
        #  so, we could go back to just owning a 'playableName' and looking up with this: "scn.as_custom[self.playableName]"
        playable = self._findPlayable(scn.as_custom) # scn.as_custom[self.playableIdx] # scn.as_custom[self.playableName]

        row = self.layout.row()
        row.label(text=F"{getPlayableTypes()[int(playable.playableType)][1]} > {playable.name} ")

        playableType = int(playable.playableType)
        if playableType == 0: # event only
            self.drawTargetsList(playable, self.layout.box())

        elif playableType == 1 or playableType == 2: # anim or looping anim
            row = self.layout.row()
            #targets box
            self.drawTargetsList(playable, self.layout.box())

            row = self.layout.row()
            row.prop(playable, "animAction", text="Action Name")
            row = self.layout.row()
            row.prop(playable, "audioClipName", text="Audio Clip Name", icon="SOUND")
            if len(playable.audioClipName) > 0:
                self.layout.row().prop(playable, "loopAudio", text="Loop Audio")

            if int(playable.playableType) == 1: # anim
                self.layout.row().prop(playable, "commandBehaviourType", text="Behaviour")
                if not playable.commandBehaviourType in ('RestartForwards',):
                    self.layout.row().prop(playable, "audioAlwaysForwards", text="Audio Always Forwards")

            self.layout.row().prop(playable, "allowsInterrupts", text="Allows Interrupts")
        
        elif playableType == 3:
            row = self.layout.row()
            #targets box
            self.drawTargetsList(playable, self.layout.box())
            row = self.layout.row()
            row.prop(playable, "autoAddEnableReceiver", text="Add Enable Receiver")
            if playable.autoAddEnableReceiver:
                row = self.layout.row()
                row.prop(playable, "applyToChildren", text="Apply to Children")
                row.prop(playable, "setInitialState", text="Set Initial State")

            row = self.layout.row()
            row.prop(playable, "autoAddScalarReceiver", text="Add Scalar Receiver")
            if playable.autoAddScalarReceiver:
                row = self.layout.row()
                row.prop(playable, "applyToChildrenScalar", text="Appy to Children Scalar")
                row.prop(playable, "setInitialStateScalar", text="Set Initial State Scalar")
                row.prop(playable, "scalarInitialState", text="Scalar Initial State")
            
        elif playableType == 4: # camera shake
            self.layout.row().prop(playable, "shakeDuration", text="Duration")

        elif playableType == 5: # camera overlay
            self.layout.row().prop(playable, "overlayName", text="Overlay Name")

        
        self.layout.row().prop(playable, "customInfo", text="Custom Info")
        

        # if int(playable.playableType) == 1 or int(playable.playableType) == 2: # anim type
            
        # BEGIN OLD STRUCTURE
        #########
        #########

        # if int(playable.playableType) > 0: # not event-only 
        #     row = self.layout.row()

        #     #targets box
        #     box = self.layout.box()  
        #     rowb = box.row()
        #     rowb.label(text="Targets") 
            
        #     for targ in playable.targets:
        #         rowb = box.row()
        #         rowb.prop(targ, "object", text='target')
        #         rowb.operator(AS_OT_RemoveFromTargets.bl_idname, icon='X', text="").playableNameConcatTargetName = F"{playable.name},,,{targ.name}"
        #     rowb=box.row()
        #     rowb.operator(AS_OT_AddToTargets.bl_idname, icon='ADD', text="ADD" ).playableName = playable.name # self.playableName

        #     # TODO WARNING IF extra targets len is zero or no non None targets

        #     if int(playable.playableType) != 3: # not enable message
        #         row = self.layout.row()
        #         row.prop(playable, "animAction", text="Action Name")
        #         row = self.layout.row()
        #         row.prop(playable, "audioClipName", text="Audio Clip Name", icon="SOUND")
        #         if len(playable.audioClipName) > 0:
        #             self.layout.row().prop(playable, "loopAudio", text="Loop Audio")

        #     if int(playable.playableType) == 3: # enable message
        #         row = self.layout.row()
        #         row.prop(playable, "autoAddEnableReceiver", text="Add Enable Receiver")
        #         if playable.autoAddEnableReceiver:
        #             row = self.layout.row()
        #             row.prop(playable, "applyToChildren", text="Apply to Children")
        #             row.prop(playable, "setInitialState", text="Set Initial State")

        #         row = self.layout.row()
        #         row.prop(playable, "autoAddScalarReceiver", text="Add Scalar Receiver")
        #         if playable.autoAddScalarReceiver:
        #             row = self.layout.row()
        #             row.prop(playable, "applyToChildrenScalar", text="Appy to Children Scalar")
        #             row.prop(playable, "setInitialStateScalar", text="Set Initial State Scalar")
        #             row.prop(playable, "scalarInitialState", text="Scalar Initial State")
            
        # if int(playable.playableType) == 1: # anim
        #     row = self.layout.row()
        #     row.prop(playable, "commandBehaviourType", text="Behaviour")
        #     if not playable.commandBehaviourType in ('RestartForwards',):
        #         self.layout.row().prop(playable, "audioAlwaysForwards", text="Audio Always Forwards")

        # if int(playable.playableType) == 1 or int(playable.playableType) == 2: # anim type
        #     row = self.layout.row()
        #     row.prop(playable, "allowsInterrupts", text="Allows Interrupts")


def syncPlayables():
    # lament: if we could capture the action whose name was edited, we could update only 
    #   playables that use that action. Instead, we're updating all of them.
    playables = bpy.context.scene.as_custom
    for playable in playables:
        _ASJson.updateFromPointer(playable, "anim_name", playable.animAction)
        # _ASJson.updateObjectAndPath(playable, "target", "target_path", playable.target)
        # _ASJson.updateFromPointer(playable, "target", playable.target)
    
    # extra targets
    # for playable in playables:
    #     _ASJson.updateExtraTargets(playable)

from bpy.app.handlers import persistent

@persistent
def syncPlayablesOnLoadPost():
    syncPlayables()

@persistent
def onActionNameMsgbus(*arsg):
    """callback on the user changing the name of an action.
        ensure that the json data is in sync with the new name"""
    syncPlayablesOnLoadPost()

@persistent
def onObjectNameMsgbus(*args):
    """callback on an object rename.
        ensure the json data is in sync with any name change"""
    # Complaint: this will get called in many cases where it's not needed.
    # Also interesting: gets called about 20 times per rename
    print(F"**onObjectNameMSGBUS")
    syncPlayablesOnLoadPost()
    _ASJson.updateAllPlayableExtraTargets(bpy.context)

def setupActionMsgBusSubscription():
    owner = object()
    # https://docs.blender.org/api/current/bpy.msgbus.html
    subscribe_to = (bpy.types.Action, "name") 
  
    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=owner,
        args=(),
        notify=onActionNameMsgbus,)
    
    subscribe_to_ob = (bpy.types.Object, "name")
    bpy.msgbus.subscribe_rna(
        key=subscribe_to_ob,
        owner=owner,
        args=(),
        notify=onObjectNameMsgbus,)

def setupSyncPostLoad():
    from mcd.util import AppHandlerHelper
    AppHandlerHelper.RefreshLoadPostHandlers([syncPlayablesOnLoadPost, "syncPlayablesOnLoadPost"])

classes = (
    PG_AS_TargetsPropGroup,
    CUSTOM_PG_AS_Collection,
    CU_OT_PlayablePickPopup,
    AS_OT_AddToTargets,
    AS_OT_RemoveFromTargets,
    )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    setupActionMsgBusSubscription()
    setupSyncPostLoad()

    # bpy.types.Scene.ShowExtraTargets = BoolProperty(name="Extra Targets")

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    # del bpy.types.Scene.ShowExtraTargets
