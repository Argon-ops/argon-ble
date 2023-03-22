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

# bl_info = {
#     "name": "material-pointer-uilist-dev",
#     "description": "",
#     "author": "p2or",
#     "version": (0, 2),
#     "blender": (2, 80, 0),
#     "location": "Text Editor",
#     "warning": "", # used for warning icon and text in addons panel
#     "wiki_url": "",
#     "tracker_url": "",
#     "category": "Development"
# }

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

# -------------------------------------------------------------------
#   Operators
# -------------------------------------------------------------------

class CUSTOM_OT_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "ml_custom.list_action"
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
        idx = scn.ml_custom_index

        try:
            item = scn.ml_custom[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(scn.ml_custom) - 1:
                item_next = scn.ml_custom[idx+1].name
                scn.ml_custom.move(idx, idx+1)
                scn.ml_custom_index += 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.ml_custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.ml_custom[idx-1].name
                scn.ml_custom.move(idx, idx-1)
                scn.ml_custom_index -= 1
                info = 'Item "%s" moved to position %d' % (item.name, scn.ml_custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                # Don't delete the material from the project!
                # just rm from our list
                # item = scn.ml_custom[scn.ml_custom_index]
                # mat = item.material
                # if mat:         
                #     mat_obj = bpy.data.materials.get(mat.name, None)
                #     if mat_obj:
                #         bpy.data.materials.remove(mat_obj, do_unlink=True)
                # info = 'Item %s removed from scene' % (item)
                scn.ml_custom.remove(idx)
                if scn.ml_custom_index == 0:
                    scn.ml_custom_index = 0
                else:
                    scn.ml_custom_index -= 1
                # self.report({'INFO'}, info)

        if self.action == 'ADD':
            item = scn.ml_custom.add()
            item.id = len(scn.ml_custom)
            item.material = bpy.data.materials.new(name="Material")
            item.name = item.material.name
            col = self.random_color()
            item.material.diffuse_color = (col.r, col.g, col.b, 1.0)
            scn.ml_custom_index = (len(scn.ml_custom)-1)
            info = '%s added to list' % (item.name)
            self.report({'INFO'}, info)
        return {"FINISHED"}


class CUSTOM_OT_addBlendMaterials(Operator):
    """Add all materials of the current Blend-file to the UI list"""
    bl_idname = "ml_custom.add_bmaterials"
    bl_label = "Add all available Materials"
    bl_description = "Add all available materials to the UI list"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(bpy.data.materials)
    
    def execute(self, context):
        scn = context.scene
        for mat in bpy.data.materials:
            if not context.scene.ml_custom.get(mat.name):
                item = scn.ml_custom.add()
                item.id = len(scn.ml_custom)
                item.material = mat
                item.name = item.material.name
                scn.ml_custom_index = (len(scn.ml_custom)-1)
                info = '%s added to list' % (item.name)
                self.report({'INFO'}, info)
        return{'FINISHED'}


class CUSTOM_OT_printItems(Operator):
    """Print all items and their properties to the console"""
    bl_idname = "ml_custom.print_items"
    bl_label = "Print Items to Console"
    bl_description = "Print all items and their properties to the console"
    bl_options = {'REGISTER', 'UNDO'}

    reverse_order: BoolProperty(
        default=False,
        name="Reverse Order")

    @classmethod
    def poll(cls, context):
        return bool(context.scene.ml_custom)

    def execute(self, context):
        scn = context.scene
        if self.reverse_order:
            for i in range(scn.ml_custom_index, -1, -1):        
                mat = scn.ml_custom[i].material
                print ("Material:", mat,"-",mat.name, mat.diffuse_color)
        else:
            for item in scn.ml_custom:
                mat = item.material
                print ("Material:", mat,"-",mat.name, mat.diffuse_color)
        return{'FINISHED'}


class CUSTOM_OT_clearList(Operator):
    """Clear all items of the list and remove from scene"""
    bl_idname = "ml_custom.clear_list"
    bl_label = "Clear List and Remove Materials"
    bl_description = "Clear all items of the list and remove from scene"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.ml_custom)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):

        if bool(context.scene.ml_custom):
            # Remove materials from the scene
            for i in context.scene.ml_custom:
                if i.material:
                    mat_obj = bpy.data.materials.get(i.material.name, None)
                    if mat_obj:
                        info = 'Item %s removed from scene' % (i.material.name)
                        bpy.data.materials.remove(mat_obj, do_unlink=True)
                        
            # Clear the list
            context.scene.ml_custom.clear()
            self.report({'INFO'}, "All materials removed from scene")
        else:
            self.report({'INFO'}, "Nothing to remove")
        return{'FINISHED'}


# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

class CUSTOM_UL_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        mat = item.material
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.3)

            # TODO: not here. just need some kind of a title and maybe another box around the upper two sections? certainly the export section
            #   plus maybe bring the export sectino to the bottom

            # TODO: UnityPaths makes a unity root folder available
            #  some class uses this to maintain a list of unity materials in proj
            #    (via searching the project for '.mat')
            # Allow the user to input a string, and be super helpful by suggesting
            #   the names of materials in their unity project.
            #  Hopefully this helpfulness will be worth the effort
            #    since it may also enable us to be helpful when prompting the user to make other mappings
            # 
            #   Also, we could potentially warn the user, if the name in the field isn't in their project. b/c e.g. they renamed the material

            # split.label(text="Index: %d" % (index))
            # static method UILayout.icon returns the integer value of the icon ID
            # "computed" for the given RNA object.
            split.prop(mat, "name", text="", emboss=False, icon_value=layout.icon(mat))

            split.prop(item, "unityMaterial", text="Unity Material")
            # split.prop_search() # TODO <-- figure the data type item that should exist
            # TODO: not really here: storing the material map data in an empty gets
            #  awkward because what if the user wants to export with the option only_selected or active_collection?

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=layout.icon(mat))

    def invoke(self, context, event):
        pass

# -------------------------------------------------------------------
#   Collection
# -------------------------------------------------------------------

def _getMaterialKey(blenderMaterialName : str) ->str:
    # prefix must match the import script in unity addon
    return F"_mel_UM_{blenderMaterialName}"

from mcd.shareddataobject import SharedDataObject

def _lookupUnityMaterialName(blenderMaterialName : str):
    data = SharedDataObject.getEmptySharedDataOject() 
    key = _getMaterialKey(blenderMaterialName)
    if key in data:
        return data[key]
    return ""

def _getUnityMaterial(self):
    return _lookupUnityMaterialName(self.material.name)

def _setUM(self, value):
    data = SharedDataObject.getEmptySharedDataOject()
    key = _getMaterialKey(self.material.name)
    data[key] = value

class CUSTOM_PG_materialCollection(PropertyGroup):
    material: PointerProperty(
        name="Material",
        type=bpy.types.Material)

    unityMaterial : StringProperty(
        name="UnityMaterial",
        description="the name of the material. no need to include '.mat' ",
        get=_getUnityMaterial,
        set=_setUM)

def MaterialMapToDictionary(context):
    raise BaseException("no one is using this rn")
    d = dict()
    items = context.scene.ml_custom
    for item in items:
        d[item.material.name] = item.unityMaterial
    return d

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    CUSTOM_OT_actions,
    CUSTOM_OT_addBlendMaterials,
    CUSTOM_OT_printItems,
    CUSTOM_OT_clearList,
    CUSTOM_UL_items,
    # CUSTOM_PT_materialList,
    CUSTOM_PG_materialCollection
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # Custom scene properties
    bpy.types.Scene.ml_custom = CollectionProperty(type=CUSTOM_PG_materialCollection)
    bpy.types.Scene.ml_custom_index = IntProperty()
    bpy.types.Scene.ml_show_material_map = BoolProperty()


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.ml_custom
    del bpy.types.Scene.ml_custom_index
    del bpy.types.Scene.ml_show_material_map


# if __name__ == "__main__":
#     register()