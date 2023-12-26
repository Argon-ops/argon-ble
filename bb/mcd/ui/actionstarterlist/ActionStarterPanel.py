import bpy
# from bb.mcd.ui.materiallist.MaterialList import (
#     CUSTOM_OT_actions,
#     CUSTOM_OT_addBlendMaterials,
#     )

# from bb.mcd.ui.materiallist import MaterialListExporter

from bb.mcd.ui.actionstarterlist.ActionStarterList import(
    CUSTOM_OT_AS_actions,
    # CUSTOM_OT_addBlendAnimations,
    manualDrawASItems
    # CUSTOM_PG_AS_Collection
)

from bb.mcd.util import DisplayHelper
from bb.mcd.ui.actionstarterlist import PlusActionStarterPopup

# At the moment this is just a function; not an actual bpy.Panel 
def Draw(layout, context):
    scn = bpy.context.scene

    rows = 2
    row = layout.row()
    DisplayHelper._drawShowHideTriangle(row, context.scene, "as_show_starter_list", context.scene.as_show_starter_list )
    row.label(text="Commands")
    if not context.scene.as_show_starter_list:
        return

    row = layout.row()
    row.template_list(
        "CUSTOM_UL_AS_items", "as_custom_def_list", scn, 
        "as_custom", scn, "as_custom_index", rows=5)

    col = row.column(align=True)
    # col.operator(CUSTOM_OT_AS_actions.bl_idname, icon='ADD', text="").action = 'ADD'
    col.operator(PlusActionStarterPopup.CU_OT_PlayableCreate.bl_idname, icon='ADD', text="").should_append = False
    col.operator(CUSTOM_OT_AS_actions.bl_idname, icon='REMOVE', text="").action = 'REMOVE'
    col.separator()
    col.operator(CUSTOM_OT_AS_actions.bl_idname, icon='TRIA_UP', text="").action = 'UP'
    col.operator(CUSTOM_OT_AS_actions.bl_idname, icon='TRIA_DOWN', text="").action = 'DOWN'

    # row = layout.row()
    # row.operator(CUSTOM_OT_addBlendAnimations.bl_idname, icon="NODE_MATERIAL")

    box = layout.box()
    # manualDrawASItems(box, context) # would work except no scrollbar which blender doesn't seem to provide
