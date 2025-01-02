import bpy
from bpy.props import (StringProperty,
                       )

from bpy.types import (Operator,
                       )

from bb.mcd.util import ObjectLookupHelper
from bb.mcd.lookup import KeyValDefault
from bb.mcd.core.componentlike import StorageRouter
from bb.mcd.core.customcomponent import CustomComponentInspector


class CUSTOM_OT_AddKeyToSelected(Operator):
    """Add key to all selected objects"""
    bl_idname = "custom.add_key_to_selected"
    bl_label = "Add key to selected objects"
    bl_description = "a description would go here if there were one"
    bl_options = {'REGISTER', 'UNDO'}

    target_key: StringProperty(
        name="target key",
        default=""
    )

    def invoke(self, context, event):
        return self.execute(context)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        if len(self.target_key) == 0:
            return {'FINISHED'}

        StorageRouter.handleSetDefaultsWithKey(self.target_key, context)
        ObjectLookupHelper._setSelectedIndex(context, self.target_key)
        self.target_key = ""
        return {'FINISHED'}


classes = (
    CUSTOM_OT_AddKeyToSelected,
)


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)
