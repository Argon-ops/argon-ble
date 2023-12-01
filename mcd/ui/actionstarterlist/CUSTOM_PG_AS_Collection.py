
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

from mcd.ui.componentlike.util import ComponentLikeUtils as CLU
from mcd.ui.actionstarterlist import CommandNameItems


# TODO: we need a version of this for COmmandGroup type
#  But with real options to ADD / REMOVE
#    Is a generic possible?
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
            # _ASJson.updateExtraTargets(playable)
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
            # _ASJson.updateExtraTargets(playable)
              
        return {"FINISHED"}

def getPlayableTypes():
    return (
        ('0', 'Event Only', 'Nothing to play. Just generate an event'),
        ('1', 'Animation', 'Animation and/or audio'),
        ('2', 'Looping Animation', 'Looping animation and/or audio'),
        ('3', 'Send Signal', 'Send a signal to target objects'),
        ('4', 'Camera Shake', 'Trigger a camera shake'),
        ('5', 'Screen Overlay', 'Screen overlay'),
        ('6', 'Send Sleep/Wake-up Signal', 'Send a sleep or wake-up signal to targets'),
        ('7', 'Display Headline', 'Display text in the center of the screen'),
        ('8', 'Message Bus', 'Send a message on the MessageBus'),
        ('9', 'Send Destroy Signal', 'Send a destroy signal to the targets'),
        ('10', 'Command Group', 'A command that invokes a set of commands'),
        ('11', 'Wait Seconds', 'Waits for the given number of seconds')
    )

class PlayablesExporter:

    __COMMAND_MARKER_KEY__ = "mel_action_starter"

    @staticmethod
    def PreExport(targetDataHolder):
        PlayablesExporter.PurgePreviousTargetObjects()
        PlayablesExporter.WriteCommandsToTargetObject(targetDataHolder)
        PlayablesExporter.SanitizeExport(targetDataHolder)

    def DshowTargetKeys(target):
        print(F"showing target keys: for {target.name}")
        for k in target.keys():
            if ASSharedDataUtil.__DATA_KEY_PREFIX__ in k:
                print(F"{target.name} has key: {k}")

    def PurgePreviousTargetObjects():
        for previous in ObjectLookupHelper._findAllObjectsWithKey(PlayablesExporter.__COMMAND_MARKER_KEY__):
            del previous[PlayablesExporter.__COMMAND_MARKER_KEY__]
            keys = [key for key in previous.keys()]
            for key in keys:
                print(F"found key: {key}")
                if key.startswith(ASSharedDataUtil.__DATA_KEY_PREFIX__):
                    print(F"will del key {key}")
                    del previous[key]

    def WriteCommandsToTargetObject(target):
        # target = bpy.context.scene.objects[0]
        target[PlayablesExporter.__COMMAND_MARKER_KEY__] = 1
        PlayablesExporter._ExportCommands(target)
                    # ASSharedDataUtil.GetCommandDataSharedObject())
        return target

    def _ExportCommands(writeToOb):
        import json
        cmds = bpy.context.scene.as_custom
        print(F"num cmds: {len(cmds)}")
        for command in bpy.context.scene.as_custom:
            d = CUSTOM_PG_AS_Collection.ToDict(command)
            key = ASSharedDataUtil.GetPlayableBaseKey(command.name)
            print(F"base key: {key}")
            writeToOb[key] = json.dumps(d)

    def SanitizeExport(target):
        configs = ObjectLookupHelper._findAllObjectsWithKey(PlayablesExporter.__COMMAND_MARKER_KEY__)
        for config in configs:
            if config != target:
                print(F"IMPOSTER config {config.name} __ real one is {target.name}")
        print(F"END OF SANITIZE")

    def CleanUpTargetObject(target):
        # return # !! Test so we can see
        for command in bpy.context.scene.as_custom:
            del target[ASSharedDataUtil.GetPlayableBaseKey(command.name)]
        del target[PlayablesExporter.__COMMAND_MARKER_KEY__]

    


class ASSharedDataUtil:
    __DATA_KEY_SUFFIX__="_data"

    __DATA_KEY_PREFIX__="mel_AS_"

    def GetCommandDataSharedObject():
        ob = SharedDataObject.getSharedDataObjectWithName("z_DuksGames_AS_SharedObject")
        ob["mel_action_starter"] = 1 # tag object so that the importer will see it
        return ob

    # def SharedASObjectExists():
    #     return SharedDataObject.objectExists("zDuksGames_AS_SharedObject")

    @staticmethod
    def GetPlayableBaseKey(playableName : str) ->str:
        # prefix must match the import script in unity addon
        return F"{ASSharedDataUtil.__DATA_KEY_PREFIX__}{playableName}"

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
        collectionSelf[key] = value
        # _ASJson.setValueWithPlayableName(collectionSelf.name, key, value)

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
        # print(F"update all ex targs")
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

# TODO: revisit trying to protect the shared data objects from being deleted
#   can you add properties to the scene itself??

   


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

# FIXME: new playables get an 'anim_name' key by default somehow. find out why...
#    Since it isn't happening in InitPlayable

class CUSTOM_PG_AS_Collection(PropertyGroup):

    @staticmethod
    def InitPlayable(playable):
        return 
        ### ALL GOOD...
        """Make sure a few defaults are written to the storage object"""
        _ASJson.setValueAt(playable, "playableId", playable.name)
        _ASJson.setValueAt(playable, "playableType", int(playable.playableType))

        if playable.playableType == 4: #camera shake
            _ASJson.setValueAt(playable, "shake_duration", 1.0)
            _ASJson.setValueAt(playable, "shake_displacement_distance", 0.1)

        elif playable.playableType == 7: # headline
            _ASJson.setValueAt(playable, "headline_display_seconds", 1.5)

        playable.internalId = F"ID_{playable.name}"


    def DPrintInfo(self):
        print(self.DGetInfo())

    def DGetInfo(self):
        return F"NAME: {self.name} | PLAYABLE_TYPE: {self.playableType}"
    
    @staticmethod
    def ToDict(pgSelf):
        d = {}
        for fieldName in pgSelf.__annotations__.keys():
            serVal = CUSTOM_PG_AS_Collection.GetSerialiazableValue(pgSelf, fieldName)
            d[fieldName] = serVal
        return d
    
    @staticmethod 
    def GetSerialiazableValue(pgSelf, fieldName : str):
        val = getattr(pgSelf, fieldName)
        if fieldName == "targets":
            return [(ObjectLookupHelper._hierarchyToStringStrange(target.object) if target.object is not None else "") for target in val]
        elif fieldName == "animAction":
            return val.name if val is not None else ""
        elif fieldName == "commandNames":
            return [wrapper.commandName for wrapper in val]
        return val


    name : StringProperty(
        name="name",
        description = "the name of the command ",
    )
    
    nextName : StringProperty(
        name="next_name",
        description="the name of the command to invoke after this one",
    )

    # TODO: fields for an object to own the audioSource (or bool option please use some audio mixer attached to camera)
    # TODO: for animation playables, list of animations / object targets
    #  WANT
    # tarAnims : CollectionProperty(type=OT_TarAnimsList.PG_AS_ObjectAnimPair)
    # tarAnimIndex : IntProperty() 

    playableType : EnumProperty( # Should be an enum: AnimationAndAudio, EventOnly=0
        items=getPlayableTypes(),
        description="",
        default=1, 
    )
    commandBehaviourType : EnumProperty(
        name="Behaviour",
        description="What does the playable do each time interaction is initiated",
        items=(
            ('RestartForwards', 'RestartForwards', 'Just restart play from the beginning.'),
            ('ToggleAndRestart', 'ToggleAndRestart', 'If the playback cursor is closer to the end, play backwards starting from the end. Else play forwards from the beginning.'),
            ('FlipDirections', 'FlipDirections', 'Switch between forward and reverse with each invocation. Just change directions and don\'t set the playback position (to either start or end) before hand.'),
        ),
    )

    customInfo : StringProperty(
        name="Custom Info2",
        description="Optional. Use any way you want in a CommandEvent handler. The contents of this field will be copied to the 'CustomInfo' field in each CommandEvent sent from this playable",
    )

    allowsInterrupts : BoolProperty(
        name="Allows Interrupts",
        description="Should subsequent interactions interrupt a command that is already running. Looping animations that don't allow interrupts will never stop playing.",
    )
    
    targets : CollectionProperty(
        name="Targets",
        type=PG_AS_TargetsPropGroup,
    )

    animAction : PointerProperty(
        name="action name",
        type=bpy.types.Action,
        poll = lambda self, action : True, # _isActionInList(self, action), 
    )
    # TODO: consider adding an audio only type playable
    audioClipName : StringProperty(
        name="audio clip name",
        description="the name of a clip in your Unity project.",
    )
    loopAudio : BoolProperty(
        name="Loop Audio",
        description="If true, audio will loop while animating. If false, audio will play once. (Once per loop, if this is a looping animation.) If there is only audio, this option does nothing.  ",
    )

    audioAlwaysForwards : BoolProperty(
        name="Audio Always Forwards",
        description="Should audio play forwards even when the animation is playing backwards",
    )


    # These two props (applyToChildren and setInitialState) are duplicated in EnableReceiverLike.
    #  Setting these will result in an EnableMessageReceiver being applied to the target object in Unity
    #   Adding an EnableReceiverLike in blender will have the same effect.
    #    The point is we want to give the user a convenient shortcut for adding this component that they probably want
    applyToChildren : BoolProperty(
        name="Apply to Children",
        description="If true, the importer will search the target and the target's children for message receivers. If false, only search the target",
    )

    # overtime
    overTime : BoolProperty(
        description="If true, the command sends multiple signals over a time interval. If false, sends only one signal immediately"
    )
    overTimeFunction : EnumProperty(
        items=(
            ('StartValueEndValue', 'StartValueEndValue', 'Send the low value immediately. Send the high value after the Duration has elapsed'),
            ('SawTooth', 'SawTooth', 'Function f(t) = (t % period) / period * (high - low) + high'),
            ('Linear', 'Linear', 'Function f(t) = t * (high - low) / period + low'),
        ),
        description="Defines the type of the function that supplies the output signal"
    )
    lowValue : FloatProperty(
        description="",
        default=0.0,
    )
    highValue : FloatProperty(
        description="",
        default=1.0,
    )
    runIndefinitely : BoolProperty(
        description="If true, the signal will broadcast for an indefinite length of time. If false, the signal will stop after the specified interval"
    )
    pickUpFromLastState : BoolProperty(
        description="If true, commands will pick up where they left off during the last command. In other words, the first signal sent will equal the last signal sent during the previous invocation of the command"
    )

    shouldClampFunction : BoolProperty(
        description="If true, clamp the function between lowValue and highValue",
        default=True,
    )
    totalRangeSeconds : FloatProperty(
        description="Defines the length of time in seconds during which signals should be broadcast",
        default=1.0,
    )
    periodSeconds : FloatProperty(
        description="Defines the period in seconds when the function is periodic; e.g. SawTooth. ",
        default=0.5,
    )
    broadcastIntervalSeconds : FloatProperty(
        description="Defines the tick resolution; the amount of time to wait between broadcasts. In seconds",
        default=0.033,
    )

    #region signal overtime outro
    shouldOutro : BoolProperty(
        description="",
    )
    outroBehaviour : EnumProperty(
        items=(
            ('None', 'None', 'None'),
            ('Constant', 'Constant', 'Outro always plays to the destination specified by Destination Value (e.g. animation snaps back to the beginning if Destination Value is 0.)'),
            ('ThresholdCondition', 'ThresholdCondition', 'Outro plays to destination A if the signal meets the threshold (e.g. animation reaches beyond halfway point). Plays to B otherwise')
        )
    )
    outroSpeedMultiplier : FloatProperty(
        description="Higher values correspond to quicker outros.",
        default=1.0
    )
    outroThreshold : FloatProperty(
        description="",
        default=0.5,
    )
    outroDestinationValue : FloatProperty(
        description="",
        default=1.0,
    )
    outroDestinationValueB : FloatProperty(
        description="",
        default=0.0,
    )
    #endregion




    # TODO: not really here: could make a button. it's text is the playable name.
    #    its operator is just a popup that let's you choose which playable you want.
    #      more clicks. but visually clearer. This instead of the current label : enum-drop-down

    # setInitialState : EnumProperty(
    #     items=(
    #         ('DONT', 'Don\'t set initial state', 'Do nothing at start up'),
    #         ('TRUE', 'Enabled', 'Set enabled at start up'),
    #         ('FALSE', 'Disabled', 'Set disabled at start up')
    #     ),
    #     #get=lambda self : _ASJson.getIntAt(self, "set_initial_state" ),
    #     #set=lambda self, value : _ASJson.setValueAt(self, "set_initial_state", value)
    # )
    # enableSignalFilter : EnumProperty(
    #     items=(
    #         ('Greater than half', 'Greater than half', 'Signal values greater than .5 will be considered true/enable. Otherwise false/disable'),
    #         ('Less than half')
    #     )
    # )

    # TODO: not really here: need some clarity around the language of 'Enable Filters'
    #   Maybe just an explanation label 


    #screen overlay
    overlayName : StringProperty(
        description="The name of the UIDocument element to overlay. (Classic GUI not supported at the moment sorry)",
    )

    # camera shake
    shakeDuration : FloatProperty(
        description="Camera shake duration in seconds",
    )
    shakeDisplacementDistance : FloatProperty(
        description="Defines how violently the camera will shake",
    )

    signalFilters : EnumProperty(
        items=(
            ('DontFilter', 'Don\'t Filter', 'DF'),
            ('ConstantValue', 'Constant Value', 'CV'),
            ('OneMinusSignal', 'One Minus Signal', 'OMS'),
        ),
    )

    signalConstantValue : FloatProperty(
    )

    #  WAIT Commands already have modifiers! but how do we add them from the ble side?
    #  You don't , yet.  They get auto added for a certain animation play behavior type. 
    #   So, this could be one way to add them.

    shouldPlayAfter : BoolProperty(
        description="Should this command invoke another command after it finishes",
    )

    playAfterAdditionalDelay : FloatProperty(
        description="Defines the number of seconds to wait after the end of this command before starting the next command",
    )

    playAfter : EnumProperty(
        items=lambda self, context : CLU.playablesItemCallback(context),
    )

    playAfterDeferToLatest : BoolProperty(
        description="If true, the second command will only be invoked at the end of the last delay, in the case where multiple invocations of the first command create overlapping delay intervals. If false, the second command will always fire after delay, ignoring subsequent invocations of the first command",
    )

    # headline
    headlineText : StringProperty(
    )

    headlineDisplaySeconds : FloatProperty(
    )

    # message bus
    messageBusType : StringProperty(
    )

    #composite command
    commandNames : CollectionProperty(
        type=CommandNameItems.PG_AS_CommandName
    )

    isSequential : BoolProperty(
        description="If true, play commands sequentially; if not, play all simultaneously"
    )

    # wait seconds command
    waitSeconds : FloatProperty(
        description="The length of time in seconds to wait"
    )

    # commandNamesIndex : IntProperty() # For use with display list

    def draw(self, layout):
        # Row view
        split = layout.row().split(factor=.65)
        split.label(text=self.name)
        split.operator(CU_OT_PlayablePickPopup.bl_idname, text="", icon="GREASEPENCIL").playableName = self.name # internalId
        # split.operator(CU_OT_PlayablePickPopup.bl_idname, text="", icon="GREASEPENCIL").playableId = self.internalId

class CU_OT_Select(bpy.types.Operator):
    """Select"""
    bl_idname = "view3d.select_target"
    bl_label = "Select"
    bl_options = {'REGISTER', 'UNDO'}
    
    target : bpy.props.StringProperty() 

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        if len(self.target) == 0:
            return {'FINISHED'}
        ObjectLookupHelper._selectInScene(self.target)
        # bpy.ops.object.select_all(action='DESELECT')
        # bpy.data.objects[self.target].select_set(True)
        # bpy.context.view_layer.objects.active = bpy.data.objects[self.target] # also make it the active object 
        return {'FINISHED'}


class CU_OT_PlayablePickPopup(bpy.types.Operator):
    """Edit a Playable. At the moment this just duplicates the in-row edit options. Use if we need more complex options"""
    bl_idname = "view3d.playable_pick_popup" #"view3d.viewport_edit_playable"
    bl_label = "Edit Playable"
    bl_options = {'REGISTER', 'UNDO'}
    
    playableName : bpy.props.StringProperty(name="playabeName")
    # playableId : bpy.props.StringProperty(name="internalId") # bpy.props.IntProperty(name="playabeIdx")

    @classmethod
    def poll(cls, context):
        return True 
        
    def execute(self, context):
        info = '%s PlayablePickPop bye' % ("BYE")
        self.report({'INFO'}, info)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        dpi = context.preferences.system.pixel_size
        ui_size = context.preferences.system.ui_scale
        dialog_size = int(450 * dpi * ui_size)
        return wm.invoke_props_dialog(self, width=dialog_size)
    
    # def _findPlayable(self, as_custom):
    #     for pl in as_custom:
    #         if pl.internalId == self.playableId:
    #             return pl
    #     return None

    def drawTargetsList(self, playable, box):
        from mcd.ui.InspectorPopup import CU_OT_InspectorPopup
        rowb = box.row()
        rowb.label(text="Targets") 
        
        for targ in playable.targets:
            rowb = box.row()
            rowb.prop(targ, "object", text='target')
            # TODO: operator to select the target
            rowb.operator(CU_OT_Select.bl_idname, icon='RESTRICT_SELECT_OFF', text="").target=targ.object.name if targ.object else ""
            rowb.operator(AS_OT_RemoveFromTargets.bl_idname, icon='X', text="").playableNameConcatTargetName=F"{playable.name},,,{targ.name}"
            if targ.object:
                rowb.operator(CU_OT_InspectorPopup.bl_idname, text="Edit", icon="KEYTYPE_JITTER_VEC").objectName=targ.object.name if targ.object else ""

        rowb=box.row()
        rowb.operator(AS_OT_AddToTargets.bl_idname, icon='ADD', text="ADD" ).playableName = playable.name # self.playableName
        # TODO WARNING IF extra targets len is zero or no none None-targets

# TODO: just package the Command (AS custom) data as JSON in a file that you write next to the output fbx. 

# WARNING WIDE RANGING THOUGHTS: Command Namespaces
# TODO: CONSIDER: institute a sort of namespace for Commands > they are always under a scene. 
#     Of course, the scene's name may not be known at export time
#   Basically we're imagining a list of as_custom lists??
#    With the goal of enabling importing one blend file into another and preserving the actions??
#     RELATED: what does happen to the as_custom list when user imports or appends:
#             -IMPORT FBX: depends...we could add an option to *embed* the Command list in a zDuks
#             -APPEND FBX: not sure: well, if you append a collection, not likely that scene data would append also?
#   Seems to entail a pretty big re-think of how actions are referenced (by clickables, other actions, etc.)

    def draw(self, context):
        ObjectLookupHelper.DLog("Command Draw A")
        scn = context.scene

        # TODO: internalId / playableId is more flexible, but we're not using. only added it to facilitate
        #   changing playableNames. it worked but there were other problems and in the end we decided to ban renaming playables
        #  so, we could go back to just owning a 'playableName' and looking up with this: "scn.as_custom[self.playableName]"
        playable = scn.as_custom[self.playableName] 
        # playable = self._findPlayable(scn.as_custom) # scn.as_custom[self.playableIdx] # scn.as_custom[self.playableName]

        if playable is None:
            print(F"Something went wrong in Playable popup draw function. with playableId: [{self.playableId}]")
            return
        
        row = self.layout.row()
        row.label(text=F"{getPlayableTypes()[int(playable.playableType)][1]} > {playable.name} ")
        self.layout.row().prop(playable, "playableType")

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
        
        elif playableType == 3: # send signal
            row = self.layout.row()
            #targets box
            boxt = self.layout.box()
            self.drawTargetsList(playable, boxt)
            boxt.row().prop(playable, "applyToChildren", text="Apply to Children")
            boxt.row().prop(playable, "overTime", text="Over Time")
            if playable.overTime:
                boxt.row().prop(playable, "overTimeFunction")
                boxt.row().prop(playable, "runIndefinitely", text="Run Indefinetly")
                boxt.row().prop(playable, "pickUpFromLastState", text="Pick-up from Last State")
                if not playable.runIndefinitely:
                    boxt.row().prop(playable, "totalRangeSeconds", text="Duration Seconds")
                boxt.row().prop(playable, "lowValue")
                boxt.row().prop(playable, "highValue")
                if playable.overTimeFunction != "StartValueEndValue":
                    boxt.row().prop(playable, "periodSeconds", text="Period Seconds")
                    boxt.row().prop(playable, "broadcastIntervalSeconds", text="Broadcast Tick Seconds")
                    boxt.row().prop(playable, "shouldClampFunction", text="Clamp Function Output")
                # boxt.row().prop(playable, "shouldOutro", text="Outro")
                boxt.row().prop(playable, "outroBehaviour", text="Outro")
                if playable.outroBehaviour != "None":
                    # boxt.row().prop(playable, "outroBehaviour", text="Outro Behaviour")
                    if playable.outroBehaviour == "Constant":
                        boxt.row().prop(playable, "outroDestinationValue", text="Outro Destination Value")
                    if playable.outroBehaviour == "ThresholdCondition":
                        boxt.row().prop(playable, "outroThreshold", text="Outro Threshold")
                        boxt.row().prop(playable, "outroDestinationValue", text="Over Threshold Destination")
                        boxt.row().prop(playable, "outroDestinationValueB", text="Under Threshold Destination")
                    boxt.row().prop(playable, "outroSpeedMultiplier", text="Outro Speed Multiplier")
                    
                self.layout.row().prop(playable, "allowsInterrupts", text="Allows Interrupts")
                
           
        elif playableType == 4: # camera shake
            self.layout.row().prop(playable, "shakeDuration", text="Duration")
            self.layout.row().prop(playable, "shakeDisplacementDistance", text="Displacement Distance")

        elif playableType == 5: # camera overlay
            self.layout.row().prop(playable, "overlayName", text="Overlay Name")

        elif playableType == 6: # sleep signal
            self.drawTargetsList(playable, self.layout.box())

        elif playableType == 7: # headline
            self.layout.row().prop(playable, "headlineText", text="Text")
            self.layout.row().prop(playable, "headlineDisplaySeconds", text="Display Time Seconds")

        elif playableType == 8: # message bus
            self.layout.row().prop(playable, "messageBusType", text="Type")
            self.drawTargetsList(playable, self.layout.box())

        elif playableType == 9: # destroy symbol
            self.drawTargetsList(playable, self.layout.box())

        elif playableType == 10: # composite command
            CommandNameItems.DrawList(self.layout, playable)
            self.layout.row().prop(playable, "isSequential", text="Sequential")
        
        elif playableType == 11: # wait seconds
            self.layout.row().prop(playable, "waitSeconds", text="Wait Seconds")


        self.layout.row().prop(playable, "signalFilters", text="Signal Filter ")
        if playable.signalFilters == "ConstantValue":
            self.layout.row().prop(playable, "signalConstantValue", text="Signal Constant Value")

        self.layout.row().prop(playable, "shouldPlayAfter", text="Play A Command After")
        if playable.shouldPlayAfter:
            row = self.layout.row()
            row.prop(playable, "playAfter", text="Play After")
            row.operator(CU_OT_PlayablePickPopup.bl_idname, text="", icon="GREASEPENCIL").playableName = playable.playAfter 
            # row.operator(CU_OT_PlayablePickPopup.bl_idname, text="", icon="GREASEPENCIL").playableId = context.scene.as_custom[CLU.playableEnumIndexFromName(playable.playAfter)].internalId
            self.layout.row().prop(playable, "playAfterAdditionalDelay", text="Delay Seconds")
            self.layout.row().prop(playable, "playAfterDeferToLatest", text="Play After Defer to Latest")

        self.layout.row().prop(playable, "customInfo", text="Custom Info")

        ObjectLookupHelper.DLog("Command Draw FINISHED")

        

def cleanUpPostExport(dataMuleObject ):
    print("clean up post export")
    # TODO: remove playable data from object[0]

def syncPlayables():
    # lament: if we could capture the action whose name was edited, we could update only 
    #   playables that use that action. Instead, we're updating all of them.
    playables = bpy.context.scene.as_custom
    for playable in playables:
        break # TODO del me
        # _ASJson.updateFromPointer(playable, "anim_name", playable.animAction)
        # _ASJson.updateObjectAndPath(playable, "target", "target_path", playable.target)
        # _ASJson.updateFromPointer(playable, "target", playable.target)
    
    # extra targets
    # for playable in playables:
    #     _ASJson.updateExtraTargets(playable)

from bpy.app.handlers import persistent

@persistent
def syncPlayablesOnLoadPost(dummy):
    print(F"LOAD POST for CUSTOM PG_AS")
    syncPlayables()

@persistent
def onActionNameMsgbus(*arsg):
    """callback on the user changing the name of an action.
        ensure that the json data is in sync with the new name"""
    syncPlayables()

@persistent
def onObjectNameMsgbus(*args):
    """callback on an object rename.
        ensure the json data is in sync with any name change"""
    # Complaint: this will get called in many cases where it's not needed.
    # Also interesting: gets called about 20 times per rename
    print(F"**onObjectNameMSGBUS")
    syncPlayables()
    # _ASJson.updateAllPlayableExtraTargets(bpy.context)

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

# def setupSyncPostLoad():
#     from mcd.util import AppHandlerHelper
#     AppHandlerHelper.RefreshLoadPostHandler(syncPlayablesOnLoadPost) 

classes = (
    PG_AS_TargetsPropGroup,
    CUSTOM_PG_AS_Collection,
    CU_OT_Select,
    CU_OT_PlayablePickPopup,
    AS_OT_AddToTargets,
    AS_OT_RemoveFromTargets,
    )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # setupActionMsgBusSubscription()
    # setupSyncPostLoad()

    # bpy.types.Scene.ShowExtraTargets = BoolProperty(name="Extra Targets")

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    # del bpy.types.Scene.ShowExtraTargets
