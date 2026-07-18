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


# Custom property a collection carries when it has been flagged as an export
# group (see bb/mcd/cduoperator/ToggleExportGroup.py).
_EXPORT_GROUP_PROP = "mel_is_export_group"


class CDU_OT_ExportGroupsBatch(Operator):
    """Batch export each collection flagged as an export group to its own FBX file"""
    bl_idname = "mel_export_scene.export_groups_batch"
    bl_label = "Export Groups Batch"
    bl_options = {'REGISTER'}

    directory: StringProperty(subtype='DIR_PATH')

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        from bb.mcd.exporter import ExportOp

        # Prepare shared data for export, exactly like the other custom exporters.
        targetDataHolder = SharedDataObject.GetFirstSelectedObjectOrAny()
        ExportOp.PreExport(targetDataHolder)

        # Map every collection to its parent collection so we can resolve an
        # object's export group by walking one level up when needed.
        parent_map = self._buildParentMap()

        # Bucket objects: one bucket per export-group collection, plus a leftover
        # bucket for everything not in an export group.
        groups = {}          # collection name -> (collection, [objects])
        leftover = []
        for obj in context.scene.objects:
            export_groups = self._resolveExportGroups(obj, parent_map)
            if export_groups:
                for export_group in export_groups:
                    bucket = groups.setdefault(export_group.name, (export_group, []))
                    bucket[1].append(obj)
            else:
                leftover.append(obj)

        if not groups and not leftover:
            self.report({'WARNING'}, "No objects found in scene")
            return {'CANCELLED'}

        blend_name = self._blendFileBaseName()

        prev_selected = list(context.selected_objects)
        prev_active = context.view_layer.objects.active
        exported = 0

        # One FBX per export group, named "<blend>_<collection>.fbx".
        for collection, objs in groups.values():
            filename = self._safeName(f"{blend_name}_{collection.name}") + ".fbx"
            self._exportObjects(context, objs, os.path.join(self.directory, filename))
            exported += 1

        # Everything not in an export group goes to a single "<blend>.fbx".
        if leftover:
            filename = self._safeName(blend_name) + ".fbx"
            self._exportObjects(context, leftover, os.path.join(self.directory, filename))
            exported += 1

        # Restore the previous selection state.
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

    def _buildParentMap(self):
        """Return {child_collection_name: parent_collection} for all collections."""
        parent_map = {}
        for coll in bpy.data.collections:
            for child in coll.children:
                parent_map[child.name] = coll
        return parent_map

    def _resolveExportGroups(self, obj, parent_map):
        """Return every export-group collection an object belongs to.

        For each collection the object is in: that collection is an export
        group when it is flagged with mel_is_export_group != 0. Otherwise, if
        that collection's parent is flagged with mel_is_export_group == 1, the
        parent is the export group. An object can match several groups.
        """
        found = []
        seen = set()
        for coll in obj.users_collection:
            group = None
            if coll.get(_EXPORT_GROUP_PROP, 0):
                group = coll
            else:
                parent = parent_map.get(coll.name)
                if parent is not None and parent.get(_EXPORT_GROUP_PROP, 0) == 1:
                    group = parent
            if group is not None and group.name not in seen:
                seen.add(group.name)
                found.append(group)
        return found

    def _exportObjects(self, context, objs, filepath):
        for o in context.scene.objects:
            o.select_set(False)
        active = None
        for obj in objs:
            try:
                obj.select_set(True)
                active = obj
            except RuntimeError:
                pass
        context.view_layer.objects.active = active

        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=True,
            apply_scale_options='FBX_SCALE_ALL',
            use_custom_props=True,
        )

    def _blendFileBaseName(self):
        base = bpy.path.basename(bpy.data.filepath)
        if base.lower().endswith(".blend"):
            base = base[:-len(".blend")]
        return base if base else "untitled"

    def _safeName(self, name):
        return re.sub(r'[<>:"/\\|?*]', '_', name)


def register():
    bpy.utils.register_class(CDU_OT_DefaultExportUnityFBX)
    bpy.utils.register_class(CDU_OT_ExportTopLevelObjectsSeparately)
    bpy.utils.register_class(CDU_OT_ExportGroupsBatch)


def unregister():
    bpy.utils.unregister_class(CDU_OT_DefaultExportUnityFBX)
    bpy.utils.unregister_class(CDU_OT_ExportTopLevelObjectsSeparately)
    bpy.utils.unregister_class(CDU_OT_ExportGroupsBatch)

