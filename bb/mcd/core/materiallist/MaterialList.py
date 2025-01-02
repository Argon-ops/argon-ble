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

from bb.mcd.shareddataobject import SharedDataObject
from bb.mcd.util import ObjectLookupHelper
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
                scn.ml_custom.move(idx, idx+1)
                scn.ml_custom_index += 1

            elif self.action == 'UP' and idx >= 1:
                scn.ml_custom.move(idx, idx-1)
                scn.ml_custom_index -= 1

            elif self.action == 'REMOVE':
                scn.ml_custom.remove(idx)
                if scn.ml_custom_index == 0:
                    scn.ml_custom_index = 0
                else:
                    scn.ml_custom_index -= 1

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


def _GetMaterialIndexInList(scene, mat: bpy.types.Material) -> int:
    for i in range(len(scene.ml_custom)):
        item = scene.ml_custom[i]
        if item.material.name == mat.name:
            return i
    return -1


def AddMaterial(scene, mat: bpy.types.Material) -> None:
    mat_list = scene.ml_custom

    if _GetMaterialIndexInList(scene, mat) == -1:
        item = mat_list.add()
        item.id = len(mat_list)
        item.material = mat
        item.name = item.material.name
        scene.ml_custom_index = (len(mat_list)-1)


def SelectMaterial(scene, mat: bpy.types.Material) -> int:
    if mat is None:
        return -1
    idx = _GetMaterialIndexInList(scene, mat)

    if idx >= 0 and idx < len(scene.ml_custom.keys()):
        scene.ml_custom_index = idx
        return idx
    return -1


def SetUnityName(scene, idx, unityMaterialName) -> None:
    if idx < 0:
        return
    item = scene.ml_custom[idx]
    item.unityMaterial = unityMaterialName


class CUSTOM_OT_addSpecificMaterial(Operator):
    """Add a material to the material map"""
    bl_idname = "ml_custom.add_specific_material"
    bl_label = "Add material"
    bl_description = "Add a material to the material map"
    bl_options = {'REGISTER'}

    @staticmethod
    def _getUnityMaterialName(asmSelf) -> str:
        choice = bpy.context.scene.ml_specific_material_choice
        if choice is None:
            return asmSelf.unityMaterialStoreName

        map_item = bpy.context.scene.ml_custom.get(choice.name)
        if map_item:
            if asmSelf.unityMaterialStoreName:
                return asmSelf.unityMaterialStoreName
            return map_item.unityMaterial
        return asmSelf.unityMaterialStoreName

    @staticmethod
    def _storeUnityMaterialName(asmSelf, value):
        asmSelf.unityMaterialStoreName = value

    unityMaterialStoreName: StringProperty()

    unityMaterialName: StringProperty(
        description="The name of the unity material that this material should map to. No need to include '.mat'",
        get=lambda self: CUSTOM_OT_addSpecificMaterial._getUnityMaterialName(
            self),
        set=lambda self, value: CUSTOM_OT_addSpecificMaterial._storeUnityMaterialName(
            self, value)
    )

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        dpi = context.preferences.system.pixel_size
        ui_size = context.preferences.system.ui_scale
        dialog_size = int(450 * dpi * ui_size)

        # prepare pre-launch
        context.scene.ml_specific_material_choice = None
        self.unityMaterialStoreName = ""

        return wm.invoke_props_dialog(self, width=dialog_size)

    def execute(self, context):
        AddMaterial(context.scene, context.scene.ml_specific_material_choice)
        idx = SelectMaterial(
            context.scene, context.scene.ml_specific_material_choice)
        SetUnityName(context.scene, idx, self.unityMaterialStoreName)
        return {'FINISHED'}

    def draw(self, context):
        row = self.layout.row()
        row.row()
        row.prop(context.scene, "ml_specific_material_choice", text="Material")
        row.prop(self, "unityMaterialName", text="Unity Material")
        row.row()


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
        for mat in bpy.data.materials:
            if not context.scene.ml_custom.get(mat.name):
                AddMaterial(context.scene, mat)

        return {'FINISHED'}


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
                print("Material:", mat, "-", mat.name, mat.diffuse_color)
        else:
            for item in scn.ml_custom:
                mat = item.material
                print("Material:", mat, "-", mat.name, mat.diffuse_color)
        return {'FINISHED'}


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
                        bpy.data.materials.remove(mat_obj, do_unlink=True)

            # Clear the list
            context.scene.ml_custom.clear()
            self.report({'INFO'}, "All materials removed from scene")
        else:
            self.report({'INFO'}, "Nothing to remove")
        return {'FINISHED'}


# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

class CUSTOM_UL_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        mat = item.material
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.3)

            if mat is not None:
                split.prop(mat, "name", text="", emboss=False,
                           icon_value=layout.icon(mat))

            split.prop(item, "unityMaterial", text="Unity Material")

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=layout.icon(mat))

    def invoke(self, context, event):
        pass

# -------------------------------------------------------------------
#   Collection
# -------------------------------------------------------------------


def _getMaterialKey(blenderMaterialName: str) -> str:
    # prefix must match the import script in unity addon
    return F"{MaterialListExporter.Prefix}{blenderMaterialName}"


def _lookupUnityMaterialName(blenderMaterialName: str):
    data = SharedDataObject.getEmptySharedDataOject()
    key = _getMaterialKey(blenderMaterialName)
    if key in data:
        return data[key]
    return ""


def _getUnityMaterial(self):
    return _lookupUnityMaterialName(self.material.name) if self.material is not None else ""


def _setUM(self, value):
    data = SharedDataObject.getEmptySharedDataOject()
    key = _getMaterialKey(self.material.name)
    data[key] = value


class MaterialListExporter:
    ''' Pack the material list into a target object pre-export'''

    Prefix = "_mel_UM_"

    __TARGET_KEY_MARKER__ = "mel_material_list_marker"

    @staticmethod
    def PreExport(target):
        MaterialListExporter.PurgePreviousTargetObjects()
        MaterialListExporter.WriteCommandsToTargetObject(target)

    def PurgePreviousTargetObjects():
        for previous in ObjectLookupHelper._findAllObjectsWithKey(MaterialListExporter.__TARGET_KEY_MARKER__):
            del previous[MaterialListExporter.__TARGET_KEY_MARKER__]

    def WriteCommandsToTargetObject(target):
        MaterialListExporter._WriteList(target)

    def _WriteList(target):
        import json
        mlist = bpy.context.scene.ml_custom
        data = []
        for mpair in mlist:
            #  allow empty unityMaterial
            materialMap = {
                "material": mpair.material.name,
                "unityMaterial": mpair.unityMaterial
            }
            data.append(materialMap)

        payload = {
            "map": data
        }
        target[MaterialListExporter.__TARGET_KEY_MARKER__] = json.dumps(
            payload)


class CUSTOM_PG_materialCollection(PropertyGroup):
    material: PointerProperty(
        name="Material",
        type=bpy.types.Material)

    unityMaterial: StringProperty(
        name="UnityMaterial",
        description="the name of the material. no need to include '.mat' ",
    )


# -------------------------------------------------------------------
#   Msgbus for deleted materials
# -------------------------------------------------------------------

def materials_callback(*args):
    print(F"^^^materials callback got args {args}")
    # TODO: update list reflecting deleted materials


_subscribe_owner = object()


def _subscribe():
    subscribe_to = bpy.data.materials
    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=_subscribe_owner,
        args=(1, 2, 3),
        notify=materials_callback
    )

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
    CUSTOM_OT_actions,
    CUSTOM_OT_addSpecificMaterial,
    CUSTOM_OT_addBlendMaterials,
    CUSTOM_OT_printItems,
    CUSTOM_OT_clearList,
    CUSTOM_UL_items,
    CUSTOM_PG_materialCollection
)


def register():
    print(F" &&&& REGISTER MATERIAL LIST &&&&")
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # Custom scene properties
    bpy.types.Scene.ml_custom = CollectionProperty(
        type=CUSTOM_PG_materialCollection)
    bpy.types.Scene.ml_custom_index = IntProperty()
    bpy.types.Scene.ml_show_material_map = BoolProperty()
    bpy.types.Scene.ml_specific_material_choice = PointerProperty(
        type=bpy.types.Material)


# this will be called slightly later than register
# because we don't have access to some types during register
def defer():
    _subscribe()


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.ml_custom
    del bpy.types.Scene.ml_custom_index
    del bpy.types.Scene.ml_show_material_map
    del bpy.types.Scene.ml_specific_material_choice
