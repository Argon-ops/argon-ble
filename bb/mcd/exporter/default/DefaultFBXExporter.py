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
import os
import re

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

        print("hi debug")
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

            # (for Blender >= 4.3) if we don't del the property 
            #  before assigning enumstr to it, we get an error:
            #  TypeError: cannot assign a 'str' value to the existing 'apply_scale_options' Int IDProperty
            del last_props['apply_scale_options'] 
            last_props['apply_scale_options'] = enumstr
            
        bpy.ops.export_scene.fbx(
            'INVOKE_DEFAULT',
            **last_props)

        SharedDataObject.selectSharedDataObjects(False) #TODO: ideally we'd restore the prev selection state
        
        return {'FINISHED'}


class CDU_OT_ExportTopLevelObjectsSeparately(Operator):
    """Export each top-level (parentless) scene object as its own FBX file"""
    bl_idname = "mel_export_scene.top_level_objects_separately"
    bl_label = "Export Top Level Objects Separately"
    bl_options = {'REGISTER'}

    directory: StringProperty(subtype='DIR_PATH')

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        top_level = [obj for obj in context.scene.objects if obj.parent is None]

        if not top_level:
            self.report({'WARNING'}, "No top-level objects found in scene")
            return {'CANCELLED'}

        prev_selected = list(context.selected_objects)
        prev_active = context.view_layer.objects.active
        exported = 0

        for obj in top_level:
            for o in context.scene.objects:
                o.select_set(False)
            obj.select_set(True)
            context.view_layer.objects.active = obj
            for child in self._all_children(obj):
                try:
                    child.select_set(True)
                except RuntimeError:
                    pass

            safe_name = re.sub(r'[<>:"/\\|?*]', '_', obj.name)
            filepath = os.path.join(self.directory, safe_name + ".fbx")

            bpy.ops.export_scene.fbx(
                filepath=filepath,
                use_selection=True,
                apply_scale_options='FBX_SCALE_ALL',
                use_custom_props=True,
            )
            exported += 1

        for o in context.scene.objects:
            o.select_set(False)
        for obj in prev_selected:
            try:
                obj.select_set(True)
            except RuntimeError:
                pass
        context.view_layer.objects.active = prev_active

        self.report({'INFO'}, f"Exported {exported} FBX file(s) to: {self.directory}")
        return {'FINISHED'}

    def _all_children(self, obj):
        result = []
        for child in obj.children:
            result.append(child)
            result.extend(self._all_children(child))
        return result


def register():
    bpy.utils.register_class(CDU_OT_DefaultExportUnityFBX)
    bpy.utils.register_class(CDU_OT_ExportTopLevelObjectsSeparately)


def unregister():
    bpy.utils.unregister_class(CDU_OT_DefaultExportUnityFBX)
    bpy.utils.unregister_class(CDU_OT_ExportTopLevelObjectsSeparately)

