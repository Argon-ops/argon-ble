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

from bb.mcd.util import ObjectLookupHelper
from bb.mcd.shareddataobject import SharedDataObject

from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU
from bb.mcd.ui.actionstarterlist import CommandNameItems
from bb.mcd.ui.actionstarterlist import CommandTypes as CT

#region command targets list add / remove

class AS_OT_AddToTargets(Operator):
    """Edit targets per playable """
    bl_idname = "custom.per_playable_targets_actions"
    bl_label = "Targets"
    bl_description = "Add remove playable targets"
    bl_options = {'REGISTER'}
    
    playableName: StringProperty(
        name="playable_name"
    )

    def invoke(self, context, event):
        try:
            playable = context.scene.as_custom[self.playableName] 
        except IndexError:
            pass
        else:
            next = playable.targets.add() 
            next.name = F"{len(playable.targets)}-targ"
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
        names = self.playableNameConcatTargetName.split(',,,')
        playableName = names[0]
        targetName = names[1]
        try:
            playable = context.scene.as_custom[playableName]
            target = playable.targets[targetName]
        except IndexError:
            pass
        else:
            idx = ObjectLookupHelper._indexOf(playable.targets, target)
            playable.targets.remove(idx)
        return {"FINISHED"}
    
#endregion


class PlayablesExporter:

    __COMMAND_MARKER_KEY__ = "mel_action_starter"

    @staticmethod
    def PreExport(targetDataHolder):
        PlayablesExporter.PurgePreviousTargetObjects()
        PlayablesExporter.WriteCommandsToTargetObject(targetDataHolder)

    def PurgePreviousTargetObjects():
        for previous in ObjectLookupHelper._findAllObjectsWithKey(PlayablesExporter.__COMMAND_MARKER_KEY__):
            del previous[PlayablesExporter.__COMMAND_MARKER_KEY__]
            keys = [key for key in previous.keys()]
            for key in keys:
                if key.startswith(ASSharedDataUtil.__DATA_KEY_PREFIX__):
                    del previous[key]

    def WriteCommandsToTargetObject(target):
        target[PlayablesExporter.__COMMAND_MARKER_KEY__] = 1
        PlayablesExporter._ExportCommands(target)
        return target

    def _ExportCommands(writeToOb):
        import json
        cmds = bpy.context.scene.as_custom
        for command in bpy.context.scene.as_custom:
            d = CUSTOM_PG_AS_Collection.ToDict(command)
            key = ASSharedDataUtil.GetPlayableBaseKey(command.name)
            writeToOb[key] = json.dumps(d)


class ASSharedDataUtil:
    __DATA_KEY_SUFFIX__="_data"

    __DATA_KEY_PREFIX__="mel_AS_"

    def GetCommandDataSharedObject():
        ob = SharedDataObject.getSharedDataObjectWithName("z_DuksGames_AS_SharedObject")
        ob["mel_action_starter"] = 1 # tag object so that the importer will see it
        return ob

    @staticmethod
    def GetPlayableBaseKey(playableName : str) ->str:
        # prefix must match the import script in unity addon
        return F"{ASSharedDataUtil.__DATA_KEY_PREFIX__}{playableName}"
    

class PG_AS_TargetsPropGroup(PropertyGroup):
    """ The type of the command target collection. Ble needs the targets to be wrapped in a property group"""
    name : StringProperty(
        name="Name",
    )
    object : PointerProperty(
        name="object",
        type = bpy.types.Object,
    )

class CUSTOM_PG_AS_Collection(PropertyGroup):

    # @staticmethod
    # def InitPlayable(playable):
    #     return 
    #     ### TODO: do we need to set these defaults elsewhere
    #     """Make sure a few defaults are written to the storage object"""
    #     _ASJson.setValueAt(playable, "playableId", playable.name)
    #     _ASJson.setValueAt(playable, "playableType", int(playable.playableType))

    #     if playable.playableType == 4: #camera shake
    #         _ASJson.setValueAt(playable, "shake_duration", 1.0)
    #         _ASJson.setValueAt(playable, "shake_displacement_distance", 0.1)

    #     elif playable.playableType == 7: # headline
    #         _ASJson.setValueAt(playable, "headline_display_seconds", 1.5)

    #     playable.internalId = F"ID_{playable.name}"

    
    @staticmethod
    def ToDict(pgSelf):
        d = {}
        for fieldName in pgSelf.__annotations__.keys():
            serVal = CUSTOM_PG_AS_Collection.GetSerialiazableValue(pgSelf, fieldName)
            d[fieldName] = serVal
        return d
    
    @staticmethod 
    def GetSerialiazableValue(pgSelf, fieldName : str):
        """ Convert any object values into something serializable. Just return any other values.  """
        val = getattr(pgSelf, fieldName)
        if fieldName == "targets":
            return [(ObjectLookupHelper._hierarchyToStringStrange(target.object) if target.object is not None else "") for target in val]
        elif fieldName == "animAction":
            return val.name if val is not None else ""
        elif fieldName == "commandNames":
            return [wrapper.commandNameStor for wrapper in val]
            # return [wrapper.commandName for wrapper in val]
        elif fieldName == "camera":
            return val.name if val is not None else ""
        return val

    name : StringProperty(
        name="name",
        description = "the name of the command ",
    )
    
    nextName : StringProperty(
        name="next_name",
        description="the name of the command to invoke after this one",
    )

    playableType : EnumProperty( 
        items=CT.getPlayableTypes(),
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
            ('RestartBackwards', 'RestartBackwards', 'Restart play from the end and play to the beginning'),
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
        # poll = lambda self, action : True, # _isActionInList(self, action), 
    )
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

    applyToChildren : BoolProperty(
        name="Apply to Children",
        description="If true, the importer will search the target and the target's children for message receivers. If false, only search the target",
    )

    #region signal overtime
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
    # loopTime : BoolProperty(
    #     description="If true, set time to zero once it reaches totalRangeSeconds"
    # )
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
        description="Defines the period in seconds when the function is periodic; e.g. SawTooth. For linear function: \
f(t) = t*(highValue-lowValue)/periodSeconds + lowValue. So f(periodSeconds) = highValue",
        default=0.5,
    )
    broadcastIntervalSeconds : FloatProperty(
        description="Defines the tick resolution; the amount of time to wait between broadcasts. In seconds",
        default=0.033,
    )
    #endregion

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

    #region screen overlay
    overlayName : StringProperty(
        description="The name of the UIDocument element to overlay. (Classic GUI not supported at the moment sorry)",
    )
    overlayHasDuration : BoolProperty(
        description="If true, display the overlay for a certain time interval and then hide it again. If false, turn the overlay on indefinitely (or off indefinitely if the signal is less than .5)"
    )
    #endregion

    #region camera shake
    shakeDuration : FloatProperty(
        description="Camera shake duration in seconds",
    )
    shakeDisplacementDistance : FloatProperty(
        description="Defines how violently the camera will shake",
    )
    #endregion

    signalFilters : EnumProperty(
        items=(
            ('DontFilter', 'Don\'t Filter', 'DF'),
            ('ConstantValue', 'Constant Value', 'CV'),
            ('OneMinusSignal', 'One Minus Signal', 'OMS'),
        ),
    )

    signalConstantValue : FloatProperty(
    )

    #region play after
    shouldPlayAfter : BoolProperty(
        description="Should this command invoke another command after it finishes",
    )

    playAfterAdditionalDelay : FloatProperty(
        description="Defines the number of seconds to wait after the end of this command before starting the next command",
    )

    # def setPlayAfter(self, val : int):
    #     playable = CLU.playableFromIndex(val)
    #     if playable is None:
    #         print(F"the playable was None playAfterStor will be empty")
    #         self.playAfterStor = ""
    #         return
        
    #     #TODO: we are seeing playAfter not working on the Unity side.
    #     #  are we declining to write to playAfterStor intentionally? The import script seems to 
    #     #   expect it to contain a value
    #     playableAfterName = playable.name
    #     print(F"playAfterStor was: {self.playAfterStor} WILL SET TO : {playableAfterName} TYPE: {type(playableAfterName)}")
    #     # self.playAfterStor = playable.name
    #     setattr(self, "playAfterStor", playable.name)
    #     print(F"playAfterStor is now: {self.playAfterStor}")

    playAfter : EnumProperty(
        items=lambda self, context : CLU.playablesItemCallback(context),
        get=lambda self : CLU.playableEnumIndexFromName(self.playAfterStor),
        set=lambda self, value: CLU.storePlayableName(self, value, "playAfterStor") # self.setPlayAfter(value) 
    )

    playAfterStor : StringProperty(
        description="'P_rivate' string used to store the name of the play after command"
    )

    playAfterDeferToLatest : BoolProperty(
        description="If true, the second command will only be invoked at the end of the last delay, in the case where multiple invocations of the first command create overlapping delay intervals. If false, the second command will always fire after delay, ignoring subsequent invocations of the first command",
    )
    #endregion

    #region headline
    headlineText : StringProperty(
    )

    headlineDisplaySeconds : FloatProperty(
        default=2.0
    )
    #endregion

    # message bus
    messageBusType : StringProperty(
    )

    #region composite command
    commandNames : CollectionProperty(
        type=CommandNameItems.PG_AS_CommandName
    )

    isSequential : BoolProperty(
        description="If true, play commands sequentially; if not, play all simultaneously"
    )
    #endregion

    #region wait seconds command
    waitSeconds : FloatProperty(
        description="The length of time to wait in seconds"
    )
    #endregion

    #region cutscene
    camera : PointerProperty(
        type=bpy.types.Object
    )

    isCancellable : BoolProperty(
        description="Should the scene stop playing when the user cancels"
    )
    #endregion

    def draw(self, layout):
        # Row view
        split = layout.row().split(factor=.65)
        split.label(text=self.name)
        split.operator(CU_OT_PlayablePickPopup.bl_idname, text="", icon="GREASEPENCIL").playableName = self.name 

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
        return {'FINISHED'}

class CU_OT_PlayablePickPopup(bpy.types.Operator):
    """Edit a Playable. At the moment this just duplicates the in-row edit options. Use if we need more complex options"""
    bl_idname = "view3d.playable_pick_popup" 
    bl_label = "Edit Command"
    bl_options = {'REGISTER', 'UNDO'}
    
    playableName : bpy.props.StringProperty(name="playabeName")

    @classmethod
    def poll(cls, context):
        return True 
        
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        dpi = context.preferences.system.pixel_size
        ui_size = context.preferences.system.ui_scale
        dialog_size = int(450 * dpi * ui_size)
        return wm.invoke_props_dialog(self, width=dialog_size)

    def drawTargetsList(self, playable, box):
        from bb.mcd.ui.InspectorPopup import CU_OT_InspectorPopup
        rowb = box.row()
        rowb.label(text="Targets") 
        
        for targ in playable.targets:
            rowb = box.row()
            rowb.prop(targ, "object", text='target')

            rowb.operator(CU_OT_Select.bl_idname, icon='RESTRICT_SELECT_OFF', text="").target=targ.object.name if targ.object else ""
            rowb.operator(AS_OT_RemoveFromTargets.bl_idname, icon='X', text="").playableNameConcatTargetName=F"{playable.name},,,{targ.name}"
            if targ.object:
                rowb.operator(CU_OT_InspectorPopup.bl_idname, text="Edit", icon="KEYTYPE_JITTER_VEC").objectName=targ.object.name if targ.object else ""

        rowb=box.row()
        rowb.operator(AS_OT_AddToTargets.bl_idname, icon='ADD', text="ADD" ).playableName = playable.name # self.playableName
        # TODO WARNING IF extra targets len is zero or no none None-targets

    def draw(self, context):
        scn = context.scene

        playable = scn.as_custom[self.playableName] 

        if playable is None:
            print(F"Something went wrong in Playable popup draw function. with playableId: [{self.playableId}]")
            return
        
        row = self.layout.row()
        row.label(text=F"{CT.getPlayableTypes()[int(playable.playableType)][1]} > {playable.name} ")
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
            boxt.row().prop(playable, "applyToChildren", text="Include Children")
            boxt.row().prop(playable, "overTime", text="Over Time")
            if playable.overTime:
                boxt.row().prop(playable, "overTimeFunction")
                boxt.row().prop(playable, "runIndefinitely", text="Run Indefinetly")
                if playable.overTimeFunction != "StartValueEndValue":
                    boxt.row().prop(playable, "pickUpFromLastState", text="Pick-up from Last State")
                
                # broadcast settings
                if not playable.runIndefinitely or playable.overTimeFunction != "StartValueEndValue":
                    boxg = boxt.box()
                    boxg.label(text="Broadcast Settings")
                    if not playable.runIndefinitely:
                        boxg.row().prop(playable, "totalRangeSeconds", text="Duration Seconds")
                    if playable.overTimeFunction != "StartValueEndValue":
                        boxg.row().prop(playable, "broadcastIntervalSeconds", text="Broadcast Tick Seconds")

                boxh = boxt.box()
                boxh.label(text="Function Settings")
                boxh.row().prop(playable, "lowValue")
                boxh.row().prop(playable, "highValue")
                if playable.overTimeFunction != "StartValueEndValue":
                    boxh.row().prop(playable, "periodSeconds", text="Period Seconds")
                    boxh.row().prop(playable, "shouldClampFunction", text="Clamp Function Output")

                boxx=boxt.box()
                boxx.row().prop(playable, "outroBehaviour", text="Outro")
                if playable.outroBehaviour != "None":
                    if playable.outroBehaviour == "Constant":
                        boxx.row().prop(playable, "outroDestinationValue", text="Outro Destination Value")
                    if playable.outroBehaviour == "ThresholdCondition":
                        boxx.row().prop(playable, "outroThreshold", text="Outro Threshold")
                        boxx.row().prop(playable, "outroDestinationValue", text="Over Threshold Destination")
                        boxx.row().prop(playable, "outroDestinationValueB", text="Under Threshold Destination")
                    boxx.row().prop(playable, "outroSpeedMultiplier", text="Outro Speed Multiplier")
                    
                self.layout.row().prop(playable, "allowsInterrupts", text="Allows Interrupts")
                
           
        elif playableType == 4: # camera shake
            self.layout.row().prop(playable, "shakeDuration", text="Duration")
            self.layout.row().prop(playable, "shakeDisplacementDistance", text="Displacement Distance")

        elif playableType == 5: # camera overlay
            self.layout.row().prop(playable, "overlayName", text="Overlay Name")
            self.layout.row().prop(playable, "overlayHasDuration", text="Has Duration")
            if playable.overTime:
                self.layout.row().prop(playable, "shakeDuration", text="Duration Seconds") 

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
            # FIXME: Scenario where the command name is not recorded (maybe when the user never actually selects a command from the list of commands) 
            CommandNameItems.DrawList(self.layout, playable)
            self.layout.row().prop(playable, "isSequential", text="Sequential")
        
        elif playableType == 11: # wait seconds
            self.layout.row().prop(playable, "waitSeconds", text="Wait Seconds")

        elif playableType == 12: # cutscene
            row = self.layout.row()

            self.layout.row().prop(playable, "camera", text="Camera")
            #targets box
            self.layout.row().label(text="Animation Targets")
            self.drawTargetsList(playable, self.layout.box())

            row = self.layout.row()
            row.prop(playable, "animAction", text="Action Name")
            row = self.layout.row()
            row.prop(playable, "audioClipName", text="Audio Clip Name", icon="SOUND")
            if len(playable.audioClipName) > 0:
                self.layout.row().prop(playable, "loopAudio", text="Loop Audio")
            self.layout.row().prop(playable, "isCancellable", text="Is Cancellable")     



        self.layout.row().prop(playable, "signalFilters", text="Signal Filter ")
        if playable.signalFilters == "ConstantValue":
            self.layout.row().prop(playable, "signalConstantValue", text="Signal Constant Value")

        self.layout.row().prop(playable, "shouldPlayAfter", text="Play A Command After")
        if playable.shouldPlayAfter:
            row = self.layout.row()
            row.prop(playable, "playAfter", text="Play After")
            print(F"Display play after now: {playable.playAfter} | stor: {playable.playAfterStor}")
            row.operator(CU_OT_PlayablePickPopup.bl_idname, text="", icon="GREASEPENCIL").playableName = playable.playAfter 
            self.layout.row().prop(playable, "playAfterAdditionalDelay", text="Delay Seconds")
            self.layout.row().prop(playable, "playAfterDeferToLatest", text="Play After Defer to Latest")
       


        self.layout.row().prop(playable, "customInfo", text="Custom Info")
        
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

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
