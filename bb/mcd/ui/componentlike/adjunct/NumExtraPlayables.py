# import bpy
# from bpy.props import (BoolProperty,)

# __MaxExtraPlayables = 5

# def AddSubtractNumExtraPlayables(should_add, context):
#     hl = context.scene.interactionHandlerLike
#     if should_add and hl.numExtraPlayables < __MaxExtraPlayables:
#         hl.numExtraPlayables = hl.numExtraPlayables + 1
#     if not should_add and hl.numExtraPlayables > 0:
#         hl.numExtraPlayables = hl.numExtraPlayables - 1

#     return hl.numExtraPlayables

# def RemoveUnusedPlayableData(context):
#     hl = context.scene.interactionHandlerLike
#     if hl.numExtraPlayables >= __MaxExtraPlayables:
#         return
#     for i in range(hl.numExtraPlayables, __MaxExtraPlayables):
#         key = F"playable{i}"
#         print(F"try to del {key}")
#         if key in hl:
#             del hl[key]
        

# class CU_OT_NumExtraPlayables(bpy.types.Operator):
#     """Num Extra Playables"""
#     bl_idname = "view3d.num_extra_playables"
#     bl_label = "Change the number of playables"
#     bl_options = {'REGISTER', 'UNDO'}
#     bl_property = "num_extra_playables"

#     should_add : BoolProperty()

#     @classmethod
#     def poll(cls, context):
#         return True 
    
#     def invoke(self, context, event):
#         AddSubtractNumExtraPlayables(self.should_add, context)
#         RemoveUnusedPlayableData(context)
#         return {'FINISHED'}

# classes = (
#     CU_OT_NumExtraPlayables,
# )


# def register():
#     from bpy.utils import register_class
#     for c in classes:
#         register_class(c)

# def unregister():
#     from bpy.utils import unregister_class
#     for c in classes:
#         unregister_class(c)

