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

from mcd.util import ObjectLookupHelper


class PG_GlobalImportSettings(PropertyGroup):
    '''Argon Global Settings Property Group

        Must match with the C# side for JSON serialization 
    '''
    pcwForAllClips : BoolProperty(
        description= "If true, generate a PlayableClipWrapper for each animation clip in the exported file. \
                This is useful if you want to use PlayableClipWrappers in your own Unity scripts. \
                    A PlayableClipWrapper is an argon class that wraps around a Unity PlayableGraph--the PCW builds\
                         the Unity PlayabeGraph during Start(). ",
    )

class GlobalSettingsExporter:

    __GLOBALS_MARKER_KEY__="mel_global_settings_marker"
    __GLOBALS_PAYLOAD_KEY__="mel_global_settings_payload"

    @staticmethod
    def PreExport(targetDataHolder):
        GlobalSettingsExporter._PurgePreviousTargetObjects()
        GlobalSettingsExporter._WriteCommandsToTargetObject(targetDataHolder)
        GlobalSettingsExporter._SanitizeExport(targetDataHolder)

    @staticmethod
    def _ToDict(globalsSelf : PG_GlobalImportSettings):
        d = {}
        for fieldName in globalsSelf.__annotations__.keys():
            d[fieldName] = GlobalSettingsExporter._GetSerialiazableValue(globalsSelf, fieldName)
        return d
    
    @staticmethod 
    def _GetSerialiazableValue(pgSelf, fieldName : str):
        return getattr(pgSelf, fieldName)
    
    def _PurgePreviousTargetObjects():
        for previous in ObjectLookupHelper._findAllObjectsWithKey(GlobalSettingsExporter.__GLOBALS_MARKER_KEY__):
            del previous[GlobalSettingsExporter.__GLOBALS_MARKER_KEY__]
            del previous[GlobalSettingsExporter.__GLOBALS_PAYLOAD_KEY__]

    def _WriteCommandsToTargetObject(target):
        target[GlobalSettingsExporter.__GLOBALS_MARKER_KEY__] = 1
        GlobalSettingsExporter._ExportCommands(target)
        return target

    def _ExportCommands(writeToOb):
        import json
        argon_globals = bpy.context.scene.argon_globals
        d = GlobalSettingsExporter._ToDict(argon_globals)
        writeToOb[GlobalSettingsExporter.__GLOBALS_PAYLOAD_KEY__] = json.dumps(d)

    def _SanitizeExport(target):
        configs = ObjectLookupHelper._findAllObjectsWithKey(GlobalSettingsExporter.__GLOBALS_MARKER_KEY__)
        for config in configs:
            if config != target:
                print(F"IMPOSTER config {config.name} __ real one is {target.name}")
                raise "This will never happen"



def DrawGlobalsButton(box):
    box.row().operator(CU_OT_ArgonGlobalsPopup.bl_idname, icon='ADD', text="Global Export Settings")


class CU_OT_ArgonGlobalsPopup(bpy.types.Operator):
    """Argon Global Settings Popup"""
    bl_idname = "view3d.argon_globals"
    bl_label = "Argon Global Settings"
    bl_options = {'REGISTER', 'UNDO'}
    # bl_property = "argon_global_settings"

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

    def draw(self, context):
        ag = bpy.context.scene.argon_globals
        self.layout.row().prop(ag, "pcwForAllClips", text="Playable Clip Wrapper for all clips")


# ------------------------------------------------------------------------
#    register, unregister
# ------------------------------------------------------------------------

classes = [
    PG_GlobalImportSettings,
    CU_OT_ArgonGlobalsPopup,
]

def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)

    bpy.types.Scene.argon_globals = PointerProperty(type=PG_GlobalImportSettings)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.argon_globals

