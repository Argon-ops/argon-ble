bl_info = {
	"name": "Default Unity FBX format",
	"author": "MelSov",
	"version": (1, 3, 1),
	"blender": (2, 80, 0),
	"location": "File > Export > Default Unity FBX",
	"description": "FBX exporter compatible with Unity's coordinate and scaling system.",
	"warning": "",
	"wiki_url": "",
	"category": "Import-Export",
}

import bpy
import mathutils
import math

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

from mcd.shareddataobject import SharedDataObject

class CDU_OT_DefaultExportUnityFBX(Operator):
    """Add key to all selected objects"""
    bl_idname = "mel_export_scene.unity_fbx"
    bl_label = "Launch default fbx exporter"
    bl_description = "Use this exporter if something goes wrong with the preferred exporter"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        print(F"invoke for def fbx ex")
        return self.execute(context)

    @classmethod
    def poll(cls, context):
        return True

    # TEST: Call the export func without 'INVOKE DEFAULT' (i.e. we're using some other execution context)--and using last used filepath
    #   Does this just export and does it suppress the file picker dialog <--yes.
    #  WORKS but the EdyJ export needs to do the same thing. So don't add this until we've resolved these two export classes.
    def _exportNoDialog(self, context):
        last_props = context.window_manager.operator_properties_last('export_scene.fbx')
        last_props['use_custom_props'] = True # never a bad idea since the package does nothing without this

        # print(F"last file path: {last_props['filepath']}")
        bpy.ops.export_scene.fbx(
            **last_props)
        # bpy.ops.export_scene.fbx(
        #     'INVOKE_DEFAULT',
        #     **last_props)
        return {'FINISHED'}

    # TODO: shouldn't we select the data objects?? 
    #  pretty sure we had this set up before. not sure what happened
    def execute(self, context):
        from mcd.exporter import ExportOp
        ExportOp.PreExport(context) 
        
        # return self._exportNoDialog(context) # test
        SharedDataObject.selectSharedDataObjects(True)

        last_props = context.window_manager.operator_properties_last('export_scene.fbx')
        last_props['use_custom_props'] = True # never a bad idea since the package does nothing without this
        bpy.ops.export_scene.fbx(
            'INVOKE_DEFAULT',
            **last_props)

        SharedDataObject.selectSharedDataObjects(False) #TODO: ideally we'd restore the prev selection state
        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
# def menu_func_export(self, context):
# 	self.layout.operator(CDU_OT_DefaultExportUnityFBX.bl_idname, text="Default Unity FBX (.fbx)")


def register():
	bpy.utils.register_class(CDU_OT_DefaultExportUnityFBX)
	# bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
	bpy.utils.unregister_class(CDU_OT_DefaultExportUnityFBX)
	# bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

