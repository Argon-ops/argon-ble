import bpy
from mcd.ui.materiallist.MaterialList import (
    CUSTOM_OT_actions,
    CUSTOM_OT_addBlendMaterials,
    CUSTOM_OT_addSpecificMaterial,
    )
from mcd.ui.materiallist import MaterialListExporter

from mcd.util import DisplayHelper

def Draw(layout, context):
    scn = bpy.context.scene

    rows = 2
    row = layout.row()

    DisplayHelper._drawShowHideTriangle(row, context.scene, "ml_show_material_map", context.scene.ml_show_material_map )
    row.label(text="Material Map")
    if not context.scene.ml_show_material_map:
        return

    row = layout.row()
    row.template_list(
        "CUSTOM_UL_items", "ml_custom_def_list", scn, 
        "ml_custom", scn, "ml_custom_index", rows=rows)

    col = row.column(align=True)
    col.operator(CUSTOM_OT_addSpecificMaterial.bl_idname, icon='ADD', text="")#.action = 'ADD'
    col.operator(CUSTOM_OT_actions.bl_idname, icon='REMOVE', text="").action = 'REMOVE'
    col.separator()
    col.operator(CUSTOM_OT_actions.bl_idname, icon='TRIA_UP', text="").action = 'UP'
    col.operator(CUSTOM_OT_actions.bl_idname, icon='TRIA_DOWN', text="").action = 'DOWN'

    layout.row().operator(CUSTOM_OT_addSpecificMaterial.bl_idname, icon="NODE_MATERIAL")
    layout.row().operator(CUSTOM_OT_addBlendMaterials.bl_idname, icon="NODE_MATERIAL")

    # Actually lets just bundle the materials with the fbx export
    # row = layout.row()
    # row.operator(MaterialListExporter.CDU_OT_MaterialListExporter.bl_idname, text="Export material map", icon="EXPORT")
