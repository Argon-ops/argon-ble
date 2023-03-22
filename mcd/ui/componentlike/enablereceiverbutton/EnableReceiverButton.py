import bpy
from bpy.props import (StringProperty,PointerProperty)
from bpy.types import (Operator,)

from mcd.ui.componentlike import EnableReceiverLike
from mcd.util import ObjectLookupHelper

class OT_EnableReceiverButton(Operator):
    """Add an enable receiver"""
    bl_idname = "custom.enable_receiver_button"
    bl_label = "Add an enable receiver"
    bl_description = "add an enable receiver to the indicated object"
    bl_options = {'REGISTER', 'UNDO'}

    
    target : StringProperty(
        name = "Target",
        default="",
    )

    def invoke(self, context, event):
        return self.execute(context)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # if self.target is None:
        #     return {'FINISHED'}

        # targetObject = bpy.data.objects[self.target]
        # print(F"the target ob is: {targetObject.name}")
        print(F"fake exec ")
        # targetObject['mel_enable_receiver'] = {}
        # targetObject['mel_enable_receiver_apply_to_children'] = True
        # EnableReceiverLike.EnableReceiverDefaultSetter.OnAddKey("", "", [targetObject])

        return {'FINISHED'}
    
classes=(
    OT_EnableReceiverButton,
)

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

