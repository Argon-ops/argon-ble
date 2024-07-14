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

def DrawInPanel(box):
    box.row().operator(CU_OT_CustomCompontentFilePickPopup.bl_idname, icon='ADD', text="Configure Custom Definition Files")

class CU_OT_CustomCompontentFilePickPopup(bpy.types.Operator):
    """Pop up to choose custom component definition files"""
    bl_idname = "view3d.custom_compo_file_pick"
    bl_label = "Inspector Popup"
    bl_options = {'REGISTER', 'UNDO'}
    
    objectName : bpy.props.StringProperty(name="internalId") # bpy.props.IntProperty(name="playabeIdx")

    @classmethod
    def poll(cls, context):
        return True 
        
    def execute(self, context):
        print(F"done exec Pop up")
        from bb.mcd.lookup import KeyValDefault
        KeyValDefault.forceReload()
        return {'FINISHED'}


    def invoke(self, context, event):
        wm = context.window_manager
        dpi = context.preferences.system.pixel_size
        ui_size = context.preferences.system.ui_scale
        dialog_size = int(450 * dpi * ui_size)
        return wm.invoke_props_dialog(self, width=dialog_size)

    def draw(self, context):
        self.layout.row().prop(context.scene, "compo_definition_file")
        

classes = (
    CU_OT_CustomCompontentFilePickPopup,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.compo_definition_file = StringProperty(
        name="Component Definition File Path",
        description="Path to a file that describes user defined components for use as ComponentLikes in Argon",
        subtype="FILE_PATH"
    )
   

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
