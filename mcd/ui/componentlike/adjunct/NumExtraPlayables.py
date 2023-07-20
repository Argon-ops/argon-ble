import bpy
from bpy.props import (BoolProperty,)


def AddSubtractNumExtraPlayables(should_add, context):
    hl = context.scene.interactionHandlerLike
    if should_add and hl.numExtraPlayables < 5:
        hl.numExtraPlayables = hl.numExtraPlayables + 1
        print(F"will add now num is: {hl.numExtraPlayables}")
    if not should_add and hl.numExtraPlayables > 0:
        hl.numExtraPlayables = hl.numExtraPlayables - 1

    print(F"num is: {hl.numExtraPlayables}")
    return hl.numExtraPlayables
        

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
        AddSubtractNumExtraPlayables(self.should_add, context)
        return {'FINISHED'}

classes = (
    CU_OT_NumExtraPlayables,
)


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    


def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

