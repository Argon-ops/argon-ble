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

from bb.mcd.shareddataobject import SharedDataObject

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

    def execute(self, context):
        from bb.mcd.exporter import ExportOp

        targetDataHolder = SharedDataObject.GetFirstSelectedObjectOrAny()
        print(F"DEFAULt COmmand data holder: {targetDataHolder.name}")

        ExportOp.PreExport(targetDataHolder) 
        
        # return self._exportNoDialog(context) # test
        SharedDataObject.selectSharedDataObjects(True)

        last_props = context.window_manager.operator_properties_last('export_scene.fbx')
        last_props['use_custom_props'] = True # never a bad idea since the package does nothing without this


        #  WORK AROUND: if, during last export, the user chose a scale option other than default (for example: FBX SCALE ALL) 
        #   this time around the script throws an error: 
        #      TypeError: Converting py args to operator properties:  expected a string enum, not int
        #       Therefore presumptuously update the last_props array
        if 'apply_scale_options' in last_props and isinstance(last_props['apply_scale_options'], int):
            aso = last_props['apply_scale_options']
            enumstr = 'FBX_SCALE_NONE'
            if aso == 1:
                enumstr = 'FBX_SCALE_UNITS'
            elif aso == 2:
                enumstr = 'FBX_SCALE_CUSTOM'
            elif aso == 3:
                enumstr = 'FBX_SCALE_ALL' 
            last_props['apply_scale_options'] = enumstr



        bpy.ops.export_scene.fbx(
            'INVOKE_DEFAULT',
            **last_props)

        SharedDataObject.selectSharedDataObjects(False) #TODO: ideally we'd restore the prev selection state
        
        return {'FINISHED'}


def register():
	bpy.utils.register_class(CDU_OT_DefaultExportUnityFBX)


def unregister():
	bpy.utils.unregister_class(CDU_OT_DefaultExportUnityFBX)

