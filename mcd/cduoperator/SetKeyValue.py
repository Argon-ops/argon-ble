import bpy
from bpy.props import (StringProperty,)
from bpy.types import (Operator,)
from mcd.util import ObjectLookupHelper

class CUSTOM_OT_SetDefaultValue(Operator):
    """Sets key and default value as custom properties on selected objects"""
    bl_idname = "custom.set_selected"
    bl_label = "set key value for selected objects"
    bl_description = "would be nice"
    bl_options={'REGISTER'}

    target_key : StringProperty(
        name="target key")
    
    def invoke(self, context, event):
        default = ObjectLookupHelper._guessReasonableValue(self.target_key, context) 
        from mcd.ui.componentlike import StorageRouter
        StorageRouter.handleSetDefaultValue(self.target_key, default, context.selected_objects)

        # ObjectLookupHelper._setValForKeyOnSelected(self.target_key, context, default)
        # no need to update the state of our display list. it reads from the objects themselves
        
        return {'FINISHED'}

def register():
    from bpy.utils import register_class
    register_class(CUSTOM_OT_SetDefaultValue)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(CUSTOM_OT_SetDefaultValue)