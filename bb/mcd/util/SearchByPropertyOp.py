import bpy
import json
from bpy.props import StringProperty
from bpy.types import Operator

_last_query = ""

_MT_KEY        = 'key'         # query found in property key name
_MT_FULL_VALUE = 'full_value'  # query exactly equals the whole value
_MT_JSON_KEY   = 'json_key'    # query exactly equals a key inside a JSON value
_MT_PARTIAL    = 'partial'     # query is a substring of value only — no clean delete


class _Match:
    __slots__ = ('obj_name', 'prop_key', 'match_type', 'json_key')

    def __init__(self, obj_name, prop_key, match_type, json_key=''):
        self.obj_name = obj_name
        self.prop_key = prop_key
        self.match_type = match_type
        self.json_key = json_key


def _try_parse_json_dict(val_str):
    s = val_str.strip()
    if not s.startswith('{'):
        return None
    try:
        result = json.loads(s)
        return result if isinstance(result, dict) else None
    except (json.JSONDecodeError, ValueError):
        return None


def _search(query, context):
    q = query.lower()
    matches = []
    for obj in context.scene.objects:
        for key, val in obj.items():
            if key.startswith('_'):
                continue
            val_str = str(val)

            if q in key.lower():
                matches.append(_Match(obj.name, key, _MT_KEY))
                continue

            if q == val_str.lower():
                matches.append(_Match(obj.name, key, _MT_FULL_VALUE))
                continue

            if q in val_str.lower():
                parsed = _try_parse_json_dict(val_str)
                if parsed is not None:
                    json_hits = [k for k in parsed if q == k.lower()]
                    for jk in json_hits:
                        matches.append(_Match(obj.name, key, _MT_JSON_KEY, jk))
                    if json_hits:
                        continue
                matches.append(_Match(obj.name, key, _MT_PARTIAL))

    return matches


class CDU_OT_AddObjectToSelection(Operator):
    """Select this object, clearing any existing selection"""
    bl_idname = "util.add_object_to_selection"
    bl_label = "Select Object"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    object_name: StringProperty()

    def execute(self, context):
        obj = context.scene.objects.get(self.object_name)
        if obj is None:
            self.report({'WARNING'}, f"Object '{self.object_name}' not found")
            return {'CANCELLED'}
        try:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
        except RuntimeError:
            self.report({'WARNING'}, f"Cannot select '{self.object_name}': object may be hidden")
            return {'CANCELLED'}
        return {'FINISHED'}


class CDU_OT_DeleteMatchedProperty(Operator):
    """Delete the matched property or JSON key"""
    bl_idname = "util.delete_matched_property"
    bl_label = "Delete Matched Property"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    object_name: StringProperty()
    prop_key: StringProperty()
    match_type: StringProperty()
    json_key: StringProperty()

    def execute(self, context):
        obj = context.scene.objects.get(self.object_name)
        if obj is None:
            self.report({'WARNING'}, f"Object '{self.object_name}' not found")
            return {'CANCELLED'}
        if self.prop_key not in obj:
            self.report({'WARNING'}, f"Property '{self.prop_key}' not found on '{self.object_name}'")
            return {'CANCELLED'}

        if self.match_type in (_MT_KEY, _MT_FULL_VALUE):
            del obj[self.prop_key]
            return {'FINISHED'}

        if self.match_type == _MT_JSON_KEY:
            val_str = str(obj[self.prop_key])
            parsed = _try_parse_json_dict(val_str)
            if parsed is None:
                self.report({'WARNING'}, f"'{self.prop_key}' is no longer valid JSON")
                return {'CANCELLED'}
            if self.json_key not in parsed:
                self.report({'WARNING'}, f"JSON key '{self.json_key}' not found in '{self.prop_key}'")
                return {'CANCELLED'}
            del parsed[self.json_key]
            obj[self.prop_key] = json.dumps(parsed)
            return {'FINISHED'}

        return {'CANCELLED'}


class CDU_OT_SearchByProperty(Operator):
    """Search scene objects by custom property name or value"""
    bl_idname = "util.search_by_property"
    bl_label = "Search By Custom Property"
    bl_options = {'REGISTER'}
    bl_property = "search_query"

    search_query: StringProperty(name="Query", default="")

    def execute(self, context):
        global _last_query
        _last_query = self.search_query
        return {'FINISHED'}

    def invoke(self, context, event):
        self.search_query = _last_query
        dpi = context.preferences.system.pixel_size
        ui_scale = context.preferences.system.ui_scale
        width = int(450 * dpi * ui_scale)
        return context.window_manager.invoke_props_dialog(self, width=width)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "search_query", text="Query")
        layout.separator()

        query = self.search_query.strip()
        box = layout.box()

        if not query:
            box.label(text="Type to search...", icon='INFO')
            return

        matches = _search(query, context)

        if not matches:
            box.label(text="No matches found", icon='INFO')
            return

        box.label(text=f"{len(matches)} match(es):")
        for m in matches:
            row = box.row(align=True)

            label = f"{m.obj_name}  ·  {m.prop_key}"
            if m.match_type == _MT_JSON_KEY:
                label += f"  ·  {m.json_key}"
            row.label(text=label, icon='OBJECT_DATA')

            sel_op = row.operator("util.add_object_to_selection", text="", icon='RESTRICT_SELECT_OFF')
            sel_op.object_name = m.obj_name

            if m.match_type != _MT_PARTIAL:
                del_op = row.operator("util.delete_matched_property", text="", icon='TRASH')
                del_op.object_name = m.obj_name
                del_op.prop_key = m.prop_key
                del_op.match_type = m.match_type
                del_op.json_key = m.json_key


classes = (
    CDU_OT_AddObjectToSelection,
    CDU_OT_DeleteMatchedProperty,
    CDU_OT_SearchByProperty,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
