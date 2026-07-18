import bpy
from bpy.props import StringProperty

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


def register():
    bpy.types.Scene.add_key_search = StringProperty(
        name="Search",
        description="Search component-like / custom property keys to add to selected objects",
        default="",
        search=_onAddKeySearchEditTextChanged,
        update=_onAddKeySearchCommitted,
    )
    bpy.types.Scene.add_key_search_match_display = StringProperty(default="", options={'SKIP_SAVE'})


def unregister():
    del bpy.types.Scene.add_key_search
    del bpy.types.Scene.add_key_search_match_display
