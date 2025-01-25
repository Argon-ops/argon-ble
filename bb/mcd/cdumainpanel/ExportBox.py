import bpy
from bb.mcd.exporter.default import DefaultFBXExporter
from bb.mcd.exporter.edyj import BlenderToUnityFbxExporter
from bpy.props import BoolProperty
from bb.mcd.util import DisplayHelper

def Draw(box, context):
    row = box.row()
    DisplayHelper._drawShowHideTriangle(row, context.scene, "show_export_box", context.scene.show_export_box)
    row.label(text="Export")
    if not context.scene.show_export_box:
        return

    box.prop(context.scene, "export_correct_rotation", text="Correct rotation")
    if context.scene.export_correct_rotation:
        box.operator(BlenderToUnityFbxExporter.ExportUnityFbx.bl_idname, text="Export Unity FBX (.fbx)", icon="EXPORT")
    else:
        box.operator(DefaultFBXExporter.CDU_OT_DefaultExportUnityFBX.bl_idname, text="Export Default Unity FBX", icon="EXPORT")


def register():
    bpy.types.Scene.export_correct_rotation = BoolProperty(
        name="Export Correct Rotation",
        description="Toggle on to compensate for the 90 degree rotation that the FBX exporter applies. Recommended unless it breaks your project; for example, animations that don't use armatures will often cause trouble.",
        default=True)
    bpy.types.Scene.show_export_box = BoolProperty(
        default=True)

def unregister():
    del bpy.types.Scene.export_correct_rotation
    del bpy.types.Scene.show_export_box