# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy

from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty,
                       PointerProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)
import json

from bb.mcd.util import ObjectLookupHelper
from bb.mcd.ui.actionstarterlist.CUSTOM_PG_AS_Collection import (
                                                        CUSTOM_PG_AS_Collection,
                                                        # _ASJson
                                                    )
# -------------------------------------------------------------------
#   Operators
# -------------------------------------------------------------------

class CUSTOM_OT_AS_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "as_custom.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def random_color(self):
        from mathutils import Color
        from random import random
        return Color((random(), random(), random()))

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.as_custom_index

        try:
            item = scn.as_custom[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(scn.as_custom) - 1:
                item_next = scn.as_custom[idx+1].name
                scn.as_custom.move(idx, idx+1)
                scn.as_custom_index += 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.as_custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.as_custom[idx-1].name
                scn.as_custom.move(idx, idx-1)
                scn.as_custom_index -= 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.as_custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                # remove the corresponding custom property on the shared data object
                # NOT NEEDED
                # if _ASJson.SharedASObjectExists():
                #     actionStarterKey = _ASJson._getDataKey(item.name) 
                #     try:
                #         del _ASJson.GetActionStarterSharedObject()[actionStarterKey]
                #     except KeyError as ke:
                #         print(F"KeyError for {actionStarterKey} is not a problem")

                # remove the list item
                scn.as_custom.remove(idx)
                # update index
                if scn.as_custom_index == 0:
                    scn.as_custom_index = 0
                else:
                    scn.as_custom_index -= 1

        if self.action == 'ADD':
            item = scn.as_custom.add()
            item.id = len(scn.as_custom)
            item.name = "fake_as_name"
            scn.as_custom_index = (len(scn.as_custom)-1)
            info = '%s added to list' % (item.name)
            self.report({'INFO'}, info)
        return {"FINISHED"}


# class CUSTOM_OT_addBlendAnimations(Operator):
#     """Add all materials of the current Blend-file to the UI list"""
#     bl_idname = "as_custom.add_bmaterials"
#     bl_label = "Add all available Materials"
#     bl_description = "Add all available materials to the UI list"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(cls, context):
#         return len(bpy.data.materials)
    
#     def execute(self, context):
#         raise Exception("not impld")
#         scn = context.scene
#         for mat in bpy.data.materials:
#             if not context.scene.as_custom.get(mat.name):
#                 item = scn.as_custom.add()
#                 item.id = len(scn.as_custom)
#                 item.material = mat
#                 item.name = item.material.name
#                 scn.as_custom_index = (len(scn.as_custom)-1)
#                 info = '%s added to list' % (item.name)
#                 self.report({'INFO'}, info)
#         return{'FINISHED'}


# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

class CUSTOM_UL_AS_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        item.draw(row) 
        
    def invoke(self, context, event):
        pass

def manualDrawASItems(layout, context):
    # works but no scroll bar.. 
    #  maybe if this were in a subpanel
    items = context.scene.as_custom
    for item in items:
        item.draw(layout.box())

# ----------------------
# Drop Down
# ---------------------

def anyActionNames():
    for obj in bpy.context.scene.objects:
        ad = obj.animation_data
        if ad:
            if ad.action:
                print(obj.name,'uses',ad.action.name)
            for t in ad.nla_tracks:
                for s in t.strips:
                    print(obj.name,'uses',s.action.name)

# -------------------------------------------------------------------
#   Collection
# -------------------------------------------------------------------


def _isActionInList(self, action):
    # not in use: keep as an API demo for a minute
    for item in bpy.context.scene.as_custom:
        #  if this is the current item, it should appear in the drop down list
        if self.animAction == item.animAction:
            return True 
        # if this is action is already reference by another list item
        if action == item.animAction:
            return False
    return True

def enforceUnique(currentName, context):
    increment = 0
    def constructName(baseName, idx):
        return baseName if increment == 0 else F"{baseName}{idx}"

    for item in context.scene.as_custom:
        compare = constructName(currentName, increment)
        if compare == item.name:
            increment += 1
    return constructName(currentName, increment)



# TODO: double click on an AS gets you a pop-up with more options
#   COUld this popup be the same one?? (but sans the ability to rename??)

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    CUSTOM_OT_AS_actions,
    # CUSTOM_OT_addBlendAnimations,
    CUSTOM_UL_AS_items,
    # CUSTOM_PG_AS_Collection
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # TODO CUSTOM_PG_AS_Collection has a nonsenscical name. But moreover
    #  we need to figure out how to subclass it. Is that OK? Collection prop
    #   but the members of the collection are actually sub classes?
    #  One snare is that Cprop's .add method doesn't take parameters?? or does it
    #  can we specify what it adds? Or could we work around by...
    #   having a wrapper object. that owns the actual CUSTOM_PG_AS_Collection sub-class object?
    #  (This would be as a pointer property...)
    #   Or some scheme using a hierarchy of objects, one for each playable.
    #  Each object is assigned a collection prop?
    #   It'd be great to learn the what and how of pointers to custom props in blender scripting
    #  Like what does it mean to assign an IntProperty or PointerProperty to the type Object
    #   Does each object get a ref to that type??
    #  Or are we allowed to assign a pointer property to an object using: ob['myPointerKey'] PointerProperty(etc..)?
    # Maybe make a button to test this stuff

    # Custom scene properties
    bpy.types.Scene.as_custom = CollectionProperty(type=CUSTOM_PG_AS_Collection)
    bpy.types.Scene.as_custom_index = IntProperty()
    bpy.types.Scene.as_show_starter_list = BoolProperty()
    bpy.types.Scene.as_actions = PointerProperty(
        name="Actions",
        type=bpy.types.Action,
        poll = lambda self, action : True) #     "a" in action.name)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.as_custom
    del bpy.types.Scene.as_custom_index
    del bpy.types.Scene.as_show_starter_list
    del bpy.types.Scene.as_actions
