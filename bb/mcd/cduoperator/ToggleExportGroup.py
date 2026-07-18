import bpy
from bpy.types import Operator

_PROP_NAME = "mel_is_export_group"

# Color tag applied to a collection while it is flagged as an export group.
# Blender shows this as a colored folder icon next to the name in the Outliner.
# (Blender's Python API has no per-row draw hook for the Outliner tree, so the
# color tag is the supported way to change a collection's appearance there.)
_MARK_COLOR_TAG = 'COLOR_04'  # green


def _applyExportGroupAppearance(collection):
    """Sync the collection's Outliner appearance to its export-group flag."""
    if collection.get(_PROP_NAME, 0):
        collection.color_tag = _MARK_COLOR_TAG
    elif collection.color_tag == _MARK_COLOR_TAG:
        collection.color_tag = 'NONE'


class CUSTOM_OT_ToggleExportGroup(Operator):
    """Toggle the export group flag on this collection"""
    bl_idname = "custom.toggle_export_group"
    bl_label = "Toggle Export Group"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.collection is not None

    def execute(self, context):
        collection = context.collection
        collection[_PROP_NAME] = 0 if collection.get(_PROP_NAME, 0) else 1
        _applyExportGroupAppearance(collection)
        return {'FINISHED'}


def _drawOutlinerCollectionMenu(self, context):
    collection = context.collection
    if collection is None:
        return
    text = "Unmark as Export Group" if collection.get(_PROP_NAME, 0) else "Mark as Export Group"
    self.layout.operator(CUSTOM_OT_ToggleExportGroup.bl_idname, text=text)


def register():
    from bpy.utils import register_class
    register_class(CUSTOM_OT_ToggleExportGroup)

    draw_funcs = bpy.types.OUTLINER_MT_collection._dyn_ui_initialize()
    for f in list(draw_funcs):
        if f.__name__ == "_drawOutlinerCollectionMenu":
            draw_funcs.remove(f)
    draw_funcs.append(_drawOutlinerCollectionMenu)

    # Backfill: apply the appearance to collections already flagged before this
    # change, so existing export groups show the color tag without re-toggling.
    for collection in bpy.data.collections:
        _applyExportGroupAppearance(collection)


def unregister():
    bpy.types.OUTLINER_MT_collection.remove(_drawOutlinerCollectionMenu)
    from bpy.utils import unregister_class
    unregister_class(CUSTOM_OT_ToggleExportGroup)
