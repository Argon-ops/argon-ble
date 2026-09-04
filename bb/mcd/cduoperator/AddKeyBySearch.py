import bpy
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator

from bb.mcd.util import ObjectLookupHelper, DisplayHelper
from bb.mcd.core.componentlike import StorageRouter


def _addableKeys(context):
    """ Keys the 'Add key to selected' menu would actually offer as an operator
        (i.e. not already present on every selected object). """
    return [key for key in ObjectLookupHelper._getAllPrefsKeys(context)
            if not ObjectLookupHelper._allSelectedHaveKey(key, context)]


def _findBestMatchingKey(query : str, context):
    """ Find the addable key (component-like or custom property) whose
        display name most closely matches query. """
    q = query.strip().lower()
    if len(q) == 0:
        return None

    best_key = None
    best_rank = None
    for key in _addableKeys(context):
        display = DisplayHelper._trimMelPrefix(key).lower()
        if display == q:
            rank = 0
        elif display.startswith(q):
            rank = 1
        elif q in display:
            rank = 2
        else:
            continue

        if best_rank is None or rank < best_rank:
            best_key, best_rank = key, rank
            if rank == 0:
                break

    return best_key


def _onAddKeySearchEditTextChanged(scene, context, edit_text):
    """ Called live as the user types in the search box (Blender's StringProperty
        'search' callback). We piggyback on it to keep the 'closest match' preview
        label up to date, and return the list of candidate display names so
        Blender can show them in the box just below the search field. """
    best = _findBestMatchingKey(edit_text, context)
    scene.add_key_search_match_display = DisplayHelper._trimMelPrefix(best) if best else ""
    return [DisplayHelper._trimMelPrefix(key) for key in _addableKeys(context)]


def _onAddKeySearchCommitted(scene, context):
    """ Called when the search field's value is confirmed (an entry is picked
        from the filtered list, or the typed text is confirmed with Return).
        Applies the matching key to selected objects exactly as the
        'Add key to selected' menu's operator would. """
    text = scene.add_key_search
    scene.add_key_search_match_display = ""
    if len(text) == 0:
        return

    target_key = None
    for key in _addableKeys(context):
        if DisplayHelper._trimMelPrefix(key) == text:
            target_key = key
            break
    if target_key is None:
        target_key = _findBestMatchingKey(text, context)

    scene.add_key_search = ""

    if target_key is None:
        return

    StorageRouter.handleSetDefaultsWithKey(target_key, context)
    ObjectLookupHelper._setSelectedIndex(context, target_key)


#region keyboard shortcut

# Blender does not keep its own reference to the strings an EnumProperty items-callback
#   hands back; built on the fly they can be collected while the search popup is still
#   showing them (garbled entries / crashes). So keep a reference here.
_enum_items_ref = []


def _addKeyEnumItems(self, context):
    """ Items for the search popup. The identifier is the real key; the visible name is
        the same display name the inspector's search field offers. """
    global _enum_items_ref
    _enum_items_ref = [(key, DisplayHelper._trimMelPrefix(key), "")
                       for key in _addableKeys(context)]
    return _enum_items_ref


class CU_OT_AddKeySearchPopup(Operator):
    """Search component-like / custom property keys and add the picked one to the selected objects"""
    bl_idname = "view3d.argon_add_key_search"
    bl_label = "Argon: Add Component-Like (Search)"
    bl_options = {'REGISTER', 'UNDO'}

    # tells invoke_search_popup which property the search field edits
    bl_property = "target_key"

    target_key: EnumProperty(
        name="Key",
        description="Component-like / custom property key to add",
        items=_addKeyEnumItems,
    )

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def invoke(self, context, event):
        if len(_addableKeys(context)) == 0:
            self.report({'INFO'}, "Nothing to add: the selected objects already have every key")
            return {'CANCELLED'}

        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        key = self.target_key
        if len(key) == 0:
            return {'CANCELLED'}

        StorageRouter.handleSetDefaultsWithKey(key, context)
        ObjectLookupHelper._setSelectedIndex(context, key)
        return {'FINISHED'}


# Ctrl+Shift+F: left hand only, and unbound in Blender's default 3D View keymap
#   (plain Ctrl+F is the Edit Mode face menu; the Ctrl+Shift variant is free).
#
# Two keymaps, because "3D View" is only handled by the viewport's WINDOW region:
#   "3D View Generic" is the area wide one (it is where N / T live, which is why those
#   work while hovering the sidebar), so it covers the Argon panel too.
_KEYMAP_NAMES = ("3D View", "3D View Generic")

_addon_keymaps = []


def _registerKeymap():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc is None:  # e.g. blender running in background mode
        return

    for km_name in _KEYMAP_NAMES:
        km = kc.keymaps.new(name=km_name, space_type='VIEW_3D')

        # hot-reloading (boot2.py) re-runs register() without unregister(), and the module
        #   level list above is reset by the reload, so drop any leftovers from last time.
        for old in [k for k in km.keymap_items if k.idname == CU_OT_AddKeySearchPopup.bl_idname]:
            km.keymap_items.remove(old)

        kmi = km.keymap_items.new(CU_OT_AddKeySearchPopup.bl_idname,
                                  'F', 'PRESS', ctrl=True, shift=True)
        _addon_keymaps.append((km, kmi))


def _unregisterKeymap():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _addon_keymaps.clear()

#endregion


def register():
    bpy.utils.register_class(CU_OT_AddKeySearchPopup)
    _registerKeymap()

    bpy.types.Scene.add_key_search = StringProperty(
        name="Search",
        description="Search component-like / custom property keys to add to selected objects",
        default="",
        search=_onAddKeySearchEditTextChanged,
        update=_onAddKeySearchCommitted,
    )
    bpy.types.Scene.add_key_search_match_display = StringProperty(default="", options={'SKIP_SAVE'})


def unregister():
    _unregisterKeymap()
    bpy.utils.unregister_class(CU_OT_AddKeySearchPopup)

    del bpy.types.Scene.add_key_search
    del bpy.types.Scene.add_key_search_match_display
