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

from bb.mcd.util import ObjectLookupHelper
from bb.mcd.ui.command.CUSTOM_PG_AS_Collection import (
    CUSTOM_PG_AS_Collection,
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
                scn.as_custom.move(idx, idx+1)
                scn.as_custom_index += 1
                info = 'Item "%s" moved to position %d' % (
                    item.name, scn.as_custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                scn.as_custom.move(idx, idx-1)
                scn.as_custom_index -= 1
                info = 'Item "%s" moved to position %d' % (
                    item.name, scn.as_custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                scn.as_custom.remove(idx)
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


# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

class CUSTOM_UL_AS_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        item.draw(row)

    def invoke(self, context, event):
        pass


# -------------------------------------------------------------------
#   Collection
# -------------------------------------------------------------------

def enforceUnique(currentName, context):
    increment = 0

    def constructName(baseName, idx):
        return baseName if increment == 0 else F"{baseName}{idx}"

    for item in context.scene.as_custom:
        compare = constructName(currentName, increment)
        if compare == item.name:
            increment += 1
    return constructName(currentName, increment)


classes = (
    CUSTOM_OT_AS_actions,
    CUSTOM_UL_AS_items,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.as_custom = CollectionProperty(
        type=CUSTOM_PG_AS_Collection)
    bpy.types.Scene.as_custom_index = IntProperty()
    bpy.types.Scene.as_show_starter_list = BoolProperty()


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.as_custom
    del bpy.types.Scene.as_custom_index
    del bpy.types.Scene.as_show_starter_list
