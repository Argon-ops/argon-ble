import bpy
from bpy.props import (StringProperty,)
from bpy.types import (Operator,)


class TestOverrideToStr(bpy.types.PropertyGroup):
    something : int
    def __str__(self):
        print(F" HAYYYYYY we're overriding __str__")
        return "this is all fake. something is: {something}"


class CDU_OT_DWhat(Operator):
    """ Select all items in the scene that contain the key defined in target_key. """
    bl_idname = "custom.dwhat"
    bl_label = "Test something for debugging"
    bl_description = "a description would go here"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        print(F"d waht")
        self.report({'INFO'}, F"d what")
        return {'FINISHED'}
    






class CDU_OT_SelectByKey(Operator):
    """ Select all items in the scene that contain the key defined in target_key. """
    bl_idname = "custom.select_by_key"
    bl_label = "Select by key"
    bl_description = "a description would go here"
    bl_options = {'REGISTER', 'UNDO'}

    target_key : StringProperty(
        name="target key",
        default=""
        )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if len(self.target_key) == 0:
            return {'FINISHED'}

        obs = [ob for ob in context.scene.objects if ob.visible_get() == True]
        for ob in obs:
            if self.target_key in ob:
                ob.select_set(True)

        return {'FINISHED'}


def register():
    from bpy.utils import register_class
    register_class(CDU_OT_SelectByKey)
    register_class(CDU_OT_DWhat)
    register_class(TestOverrideToStr)

    bpy.types.Object.testOb = bpy.props.PointerProperty(type=TestOverrideToStr)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(CDU_OT_SelectByKey)
    unregister_class(CDU_OT_DWhat)
    unregister_class(TestOverrideToStr)

    del bpy.types.Object.testOb

