import bpy
from bb.mcd.lookup import KeyValDefault
from bb.mcd.ui.componentlike import StorageRouter
import typing

def _anySelectedHaveKey(key, context):
    for ob in context.selected_objects:
        if key in ob:
            return True
    return False

def _allSelectedHaveKey(key, context):
    for ob in context.selected_objects:
        if key not in ob:
            return False
    return True



def _getDisplayKeys(context):
    return [key for key in _getPrefItems(context).keys()] # these are always the keys we want, right?
    # return [item.key for item in context.scene.custom] # del me

def _setSelectedIndex(context, key : str) -> None:
    filtered = _getDisplayKeys(context) # _currentFilteredKeys(context)
    try:
        idx = filtered.index(key)
        context.scene.custom_index = idx
    except ValueError as e:
        print(F"value error : {e}")
        raise e

def _nextRelevantIndex(context, originalIndex : int, moveUp = False) -> int:
    if _isNothingSelected(context):
        return -1
    startIndex = originalIndex + (1 if moveUp else -1)
    startIndex = startIndex if startIndex > 0 else 0
    displayKeys = _getDisplayKeys(context)
    if len(displayKeys) == 0:
        return -1
    iter = range(0, len(displayKeys)) if moveUp else range(startIndex, 0, -1)
    for i in iter:
        if _isKeyInActiveOject(displayKeys[i], context):
            return i
    if moveUp == False:
        return _nextRelevantIndex(context, originalIndex, True)
    return -1

def getPrefs(context): # WANT to type specify -->> # -> MelCustomDataUtilPreferences:
    return context.preferences.addons[__name__].preferences

def _getPrefItems(context):
    try:
        return KeyValDefault.getMCDConfig() # TODO: where how to accommodate user custom KVs and even suppressing MCD default KVs?
        prefs = getPrefs(context)
        return prefs.custom
    except BaseException as e:
        if True: # WANT --> # _IS_DEBUG_:
            # Enable load/run from blender's script window where preferences won't be defined.
            FakeKVItem = type("FakeKVItem", (object,), {
                "key" : "fake_kv_key",
                "val" : "a_fake_val",
                "vint" : 0,
                "vfloat" : 0.0,
                "relevant_prop_name" : "val"
                })
            def nextFakeKV(key : str, value) -> FakeKVItem:
                result = FakeKVItem()
                result.key = key
                if isinstance(value, str):
                    result.val = value
                    result.relevant_prop_name = "val"
                elif isinstance(value, int):
                    result.vint = value
                    result.relevant_prop_name = "vint"
                elif isinstance(value, float):
                    result.vfloat = value
                    result.relevant_prop_name = "vfloat"
                return result

            return {
                "foo" : nextFakeKV("fake_keyA", "fake val A"),
                "bar" : nextFakeKV("fake_keyB", 3), 
                "baz" : nextFakeKV("mel_mesh_collider", """ {
                    "convex" : true,
                    "isTrigger" : false
                    } """)
                } 
        # raise e


# hacky way of getting the current filtered keys (our UIList already does this)
def _currentFilteredKeys(context):
    prefsKeys = _getPrefItems(context)
    return [k for k in prefsKeys if _anySelectedHaveKey(k, context)]
    

def _getAllPrefsKeys(context):
    prefs = _getPrefItems(context=context)
    return prefs.keys()

def _getUnusedKeys(context):
    items = _getPrefItems(context)
    return [key for key in items.keys() if _anySelectedHaveKey(key, context) == False]

def _addKeyIfMissing(context, key : str, default="zero"):
    for ob in context.selected_objects:
        if key not in ob:
            ob[key] = default

def _setValForKeyOnSelected(key, context, val):
    for ob in context.selected_objects:
        ob[key] = val

def _guessReasonableValue(key, context):
    # first try to read the value from any selected object
    if len(context.selected_objects) > 0:
        if key in context.active_object:
            return context.active_object[key]
        for ob in context.selected_objects:
            if key in ob:
                return ob[key]
    # fall back to the default
    return KeyValDefault.getDefaultValue(key)
    # return KeyValDefault.getSerializableDefaultValue(key) # KeyValDefault.getDefaultValue(key)
    # return _getDefaultVal(context, key)

def _MIXED_():
    return "%%__MIXED__%%"

def _findAllObjectsWithKey(key):
    obs = bpy.context.scene.objects
    return [ob for ob in obs if key in ob]

def _getFirstVal(key, context):
    obs = context.selected_objects
    if len(obs) == 0:
        return None
    if key not in obs[0]:
        return None
    return obs[0][key]

def _getSharedVal(key, context):
    obs = context.selected_objects
    if len(obs) == 0:
        return None
    if key not in obs[0]:
        return _MIXED_()
    shared = obs[0][key]
    for i in range(1, len(obs)):
        if key not in obs[i] or StorageRouter.evaluateEqual(key, obs[0], obs[i]) == False: 
            # shared != obs[i][key]: # TODO: this inequality probably breaks when we're dealing with the special handling keys
            return _MIXED_()
    return shared

def DdumpAllKeyVals(context):
    obs = context.selected_objects
    for ob in obs:
        print(F"**KEYS in {ob.name}******************")
        for k,v in ob.items():
            print(F"   {k} : {v}")
        print(F"----------------------")
    print(F"")


def _isMixedValues(key, context):
    return len(context.selected_objects) > 1 and _getSharedVal(key, context) == _MIXED_()

def _isNothingSelected(context) -> bool:
    return len(context.selected_objects) == 0

def _isKeyInActiveOject(key, context) -> bool:
    if len(context.selected_objects) == 0:
        return False
    if context.active_object is None:
        return key in context.selected_objects[0]
    return key in context.active_object # NOT ALWAYS THE SAME! -> context.selected_objects[0]

def _getValueFromActive(key, context):
    obs = context.selected_objects
    if len(obs) == 0:
        return None
    if key in obs[0]:
        return obs[0][key]
    return None

def _getPropNameForType(value):
    if isinstance(value, float):
        return "vfloat"
    elif isinstance(value, str):
        return "val"
    return "vint"

def _removeKeyFromSelected(key, context):
    for ob in context.selected_objects:
        if key in ob:
            print(F"will del {key} from {ob.name}")
            del ob[key]

def _selectedObjectNames(context):
    obs = context.selected_objects
    count = len(obs)
    if count == 0:
        return ""
    if count == 1:
        return obs[0].name
    return '|'.join([obs[i].name for i in range(min(3, count))]) + ("" if count <= 3 else F"(+{count - 3})")

def _hierarchyToString(ob, glue='/') -> str:
    """Returns a slash separated string of the names of the object and its parents up to a root object"""
    tree = [ob]
    while ob.parent:
        ob = ob.parent
        tree.append(ob)
    
    return glue.join(map(lambda x: F"{x.name}", tree[::-1]))

def strangeSep():
    return "~~&&&~~"

def _hierarchyToStringStrange(ob) -> str:
    return _hierarchyToString(ob, strangeSep())


def _indexOf(collection, object) -> int:
    for i in range(len(collection)):
        if object == collection[i]:
            return i
    return -1

def _selectInScene(objectName):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[objectName].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[objectName] # also make it the active object

def selectObjectsInScene(objects, active = None):
    bpy.ops.object.select_all(action='DESELECT')
    [ob.select_set(True) for ob in objects]
    if len(objects) == 0:
        return
    bpy.context.view_layer.objects.active = objects[0] if active is None else active

def DLog(s : str) -> None:
    print(s)

