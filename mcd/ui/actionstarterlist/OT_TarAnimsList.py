#  WANT IF: We want to enable a list of Object/Acitons
#    that is owned by a Playable
#    At the moment, we're having trouble registering such a list

# import bpy
# from bpy.props import (IntProperty,
#                        BoolProperty,
#                        StringProperty,
#                        EnumProperty,
#                        CollectionProperty,
#                        PointerProperty)
# from bpy.types import (Operator,
#                        Panel,
#                        PropertyGroup,
#                        UIList)

# class OT_TarAnimsList(Operator):
#     """Move items up and down, add and remove"""
#     bl_idname = "ta_custom.list_action"
#     bl_label = "List Actions"
#     bl_description = "Move items up and down, add and remove"
#     bl_options = {'REGISTER'}

#     action: bpy.props.EnumProperty(
#         items=(
#             ('UP', "Up", ""),
#             ('DOWN', "Down", ""),
#             ('REMOVE', "Remove", ""),
#             ('ADD', "Add", "")))

#     def random_color(self):
#         from mathutils import Color
#         from random import random
#         return Color((random(), random(), random()))

#     def invoke(self, context, event):
#         scn = context.scene
#         idx = scn.ta_custom_index

#         try:
#             item = scn.ta_custom[idx]
#         except IndexError:
#             pass
#         else:
#             if self.action == 'DOWN' and idx < len(scn.ta_custom) - 1:
#                 item_next = scn.ta_custom[idx+1].name
#                 scn.ta_custom.move(idx, idx+1)
#                 scn.ta_custom_index += 1
#                 info = 'Item "%s" moved to position %d' % (item.name, scn.ta_custom_index + 1)
#                 self.report({'INFO'}, info)

#             elif self.action == 'UP' and idx >= 1:
#                 item_prev = scn.ta_custom[idx-1].name
#                 scn.ta_custom.move(idx, idx-1)
#                 scn.ta_custom_index -= 1
#                 info = 'Item "%s" moved to position %d' % (item.name, scn.ta_custom_index + 1)
#                 self.report({'INFO'}, info)

#             elif self.action == 'REMOVE':
#                 scn.ta_custom.remove(idx)
#                 if scn.ta_custom_index == 0:
#                     scn.ta_custom_index = 0
#                 else:
#                     scn.ta_custom_index -= 1
#                 # self.report({'INFO'}, info)

#         if self.action == 'ADD':
#             item = scn.ta_custom.add()
#             item.id = len(scn.ta_custom)
#             item.material = bpy.data.materials.new(name="Material")
#             item.name = item.material.name
#             col = self.random_color()
#             item.material.diffuse_color = (col.r, col.g, col.b, 1.0)
#             scn.ta_custom_index = (len(scn.ta_custom)-1)
#             info = '%s added to list' % (item.name)
#             self.report({'INFO'}, info)
#         return {"FINISHED"}


# # how to display this list of TarAnims
# #   TODO: we're writing a lot of lists. We can probably
# #    write a generic list display class no?
# class AS_UL_PerPlayableTarAnims(UIList):
#     """Draw each key-val row that's defined as a property of the selected objects."""

#     def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
#         from mcd.util import DisplayHelper
#         split = layout.split(factor=0.35)
#         split.lable(text="Hi this is an item")

#         #  maybe want
#         # split.label(text=F"{DisplayHelper._trimMelPrefix(item.key)}")
#         # shared = ObjectLookupHelper._getSharedVal(item.key, context=context)
#         # split = split.split(factor=.77)
        
#         # split.label(text="") # smooth out formatting if we have nothing else to put here

#         # if index == context.scene.custom_index:
#         #     split.operator(CDU_OT_actions.bl_idname, icon='X', text="").action = 'REMOVE'


# class PG_AS_ObjectAnimPair(PropertyGroup):
#     target : PointerProperty(
#         name="target object",
#         description="The object that should perform the action (e.g. be animated). The fbx exporter creates multiple animations per action in some cases; this field is required to identify which object is intended. An animation named \"<this-object>|<this-action>\" should exist. (Check the Animation tab in the Unity import inspector)",
#         type=bpy.types.Object,
#         # update=lambda self, context : _ASJson.updateFromPointer(self, "target", self.target)
#     )
#     animAction : PointerProperty(
#         name="action name",
#         type=bpy.types.Action,
#         poll = lambda self, action : True, # _isActionInList(self, action), 
#         # update=lambda self, context : _ASJson.updateFromPointer(self, "anim_name", self.animAction)
#     )   

# classes = (
#     PG_AS_ObjectAnimPair,
#     OT_TarAnimsList,
#     AS_UL_PerPlayableTarAnims,
# )

# def register():
    

#     from bpy.utils import register_class

#     for cls in classes:
#         register_class(cls)

#     bpy.types.Scene.ta_custom = CollectionProperty(type=PG_AS_ObjectAnimPair)
#     bpy.types.Scene.ta_custom_index = IntProperty()

# def unregister():
#     from bpy.utils import unregister_class

#     for cls in classes:
#         unregister_class(cls)

#     del bpy.types.Scene.ta_custom
#     del bpy.typtes.Scene.ta_custom_index

# # bpy.types.Scene.as_show_starter_list = BoolProperty()
# #     bpy.types.Scene.as_actions = PointerProperty(
# #         name="Actions",
# #         type=bpy.types.Action,
# #         poll = lambda self, action : True) #     "a" in action.name)


# # def unregister():
# #     from bpy.utils import unregister_class
# #     for cls in reversed(classes):
# #         unregister_class(cls)

# #     del bpy.types.Scene.as_custom
# #     del bpy.types.Scene.as_custom_index
# #     del bpy.types.Scene.as_show_starter_list
# #     del bpy.types.Scene.as_actions