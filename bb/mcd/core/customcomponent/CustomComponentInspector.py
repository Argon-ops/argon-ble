import bpy
from bpy.props import (CollectionProperty, 
                        StringProperty, 
                        FloatProperty, 
                        IntProperty)
from bpy.types import (Panel, 
                       PropertyGroup,
                       UIList)
from bb.mcd.util import ObjectLookupHelper
import json

_currentDefaultJSONObject = {}
_payloadKey = ""

class DisplayListUtils():
    
    @staticmethod
    def FillDisplayListWithBlanks(context):
        dl = context.scene.component_display_list
        dl.clear()
        for i in range(40): # ASSUMPTION: no one will want a component like object with more than this many properties
            ditem = dl.add()
            ditem.index = i

""" ComponentDisplayList's job is to display a Collection of CustomComponentProperty objects.
    But--funny thing is--CustomComponentProperty objects don't have any specific state, save for knowing their own index in the list.
    Instead of owning state, they look up the nth property of a (JSON) dictionary object based on their index. And make that property on that 
    dictionary editable in the UI (via getter/setter methods, see val, vint and vfloat). 
    The dictionary is read off of a custom property of the current selected object(s) (encoded as a JSON string).
      And the setter methods make sure that any changes are written back to the dictionary.

    The point of all this is to support storing and editing user-defined key-value data, stored in custom properties of objects as JSON strings.
    The key of the custom property itself is also user defined.
"""
# -------------------------------------------------------------------
#   A UIList that filters items based on whether key
#    appears as a custom property key on the selected object{s}
# -------------------------------------------------------------------
class CU_UL_ComponentDisplayList(UIList):
    """TODO: ."""

    def filter_items(self, context, data, propname):

        kvs = getattr(data, propname)

        if len(context.selected_objects) == 0:
            return [~self.bitflag_filter_item] * len(kvs), []
        
        count = CustomComponentUtil.GetPropertyCount()
        return [self.bitflag_filter_item if i < count else ~self.bitflag_filter_item for i in range(len(kvs))], []        
      

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        global _currentDefaultJSONObject

        items = _currentDefaultJSONObject.items()
        keys = list(items)
        if index >= len(keys):
            layout.row().label(text=F"out of range")
            return
        
        key, val = keys[index]

        if CustomComponentUtil.SelectionHasMixed():
            layout.row().label(text="mixed values")
            return
        
        prop_name = CU_PG_CustomComponentProperty.GetPropName(val)
        layout.row().prop(item, prop_name, text=key)


def _drawCompoList(box):
     # draw the key select uilist
    scn = bpy.context.scene
    row = box.row()
    row.template_list("CU_UL_ComponentDisplayList", "co_custom_def_list", scn, "component_display_list", 
        scn, "compo_stor_index", rows=5)



# -------------------------------------------------------------------
# Getters / Setters for KeyValItem
# -------------------------------------------------------------------

def _getSerString() -> str:
    global _payloadKey
    context = bpy.context
    if len(context.selected_objects) == 0:
        return ""
    if _payloadKey not in context.selected_objects[0]:
        return ""
    result = context.selected_objects[0][_payloadKey]
    for i in range(1, len(context.selected_objects)):
        sel = context.selected_objects[i]
        if _payloadKey not in sel or sel[_payloadKey] != result:
            return ObjectLookupHelper._MIXED_()
    return result 


def _getUniformValue(self) -> str:
    global _payloadKey
    ser = _getSerString() # ObjectLookupHelper._getSharedVal(_payloadKey, bpy.context)
    if ser == ObjectLookupHelper._MIXED_(): 
        raise Exception("mixed values exception")
    data = json.loads(ser)
    propName = CustomComponentUtil.GetPropertyKeyAtIndex(self.index)
    if propName in data:
        return data[propName]
    return F"<{propName} not found>"

def getUniformValueStr(self) -> str:
    return str(_getUniformValue(self))

def getUniformValueInt(self) -> int:
    result = _getUniformValue(self)
    return result if isinstance(result, int) else 0

def getUniformValueFloat(self) -> float:
    result = _getUniformValue(self)
    return result if isinstance(result, float) else 0.0


def setUniformValue(self, value):
    global _payloadKey
    ser = _getSerString() 
    data = json.loads(ser)
    propName = CustomComponentUtil.GetPropertyKeyAtIndex(self.index)
    data[propName] = value
    reser = json.dumps(data)
    ObjectLookupHelper._setValForKeyOnSelected(_payloadKey, bpy.context, reser)


class CustomComponentUtil():
    CUSTOM_COMPONENT_KEY_PREFIX="m3ldata_" # must match c# code
    DATA_PAYLOAD_KEY_SUFFIX="_payload" # must match c# code 
    CONFIG_KEY_SUFFIX="_config" # must match c# code
    APPLY_CLASS_NAME_SUFFIX="_apply_class_name" # same

    @staticmethod
    def GetPayloadKey(componentLikeKey : str) -> str:
        return F"{CustomComponentUtil.CUSTOM_COMPONENT_KEY_PREFIX}{componentLikeKey}{CustomComponentUtil.DATA_PAYLOAD_KEY_SUFFIX}"
    
    @staticmethod
    def GetApplyClassKey(componentLikeKey : str) -> str:
        return F"{CustomComponentUtil.CUSTOM_COMPONENT_KEY_PREFIX}{componentLikeKey}{CustomComponentUtil.APPLY_CLASS_NAME_SUFFIX}"
    
    @staticmethod
    def GetConfigDataKey(componentLikeKey : str) -> str:
        return F"{CustomComponentUtil.CUSTOM_COMPONENT_KEY_PREFIX}{componentLikeKey}{CustomComponentUtil.CONFIG_KEY_SUFFIX}"
    
    @staticmethod
    def SetDefaultObject(nextObjext : object) -> None:
        global _currentDefaultJSONObject
        _currentDefaultJSONObject = nextObjext

    @staticmethod
    def SetGlobalPayloadKey(componentLikeKey : str) -> None:
        global _payloadKey
        _payloadKey = CustomComponentUtil.GetPayloadKey(componentLikeKey)

    @staticmethod
    def GetPropertyKeyAtIndex(index : int) -> str:
        global _currentDefaultJSONObject
        keys = list(_currentDefaultJSONObject)
        if index >= len(keys):
            raise Exception(F"index {index} out of range")
        return keys[index]
    
    @staticmethod
    def GetPropertyCount() -> int:
        global _currentDefaultJSONObject
        return len(list(_currentDefaultJSONObject))
    
    @staticmethod
    def SelectionHasMixed() -> bool:
        global _payloadKey
        return ObjectLookupHelper.hasMixedValues(_payloadKey, bpy.context)



class CU_PG_CustomComponentProperty(PropertyGroup):
    """ Define a key value pair
    
    and prop name that is used to switch between val, vint, and vfloat.
    The three value properties (val, vint, vfloat) read/write their values
    from the selected objects using getters and setters """

    @staticmethod
    def GetPropName(v):
        from bb.mcd.util import RelevantPropertyNameHelper
        return RelevantPropertyNameHelper._getPropNameForType(v)
        # if isinstance(v, int):
        #     return "vint"
        # elif isinstance(v, float):
        #     return "vfloat"
        # return "val"
    
    index : IntProperty()

    val: StringProperty(
        name="val",
        default="",
        get=getUniformValueStr,
        set=setUniformValue)
    vint : IntProperty(
        name="vint",
        default=0,
        get=getUniformValueInt,
        set=setUniformValue)
    vfloat : FloatProperty(
        name="vfloat",
        default=0.0,
        get=getUniformValueFloat,
        set=setUniformValue)
    relevant_prop_name : StringProperty(
        name="type-index",
        default="error_pls")


def displayCustomCompos(box, baseKey : str):
    """ Inspector Entry point. display the custom component at key: baseKey """

    nextDefaultObject = ObjectLookupHelper.lookupDefaultValue(bpy.context, baseKey)
    CustomComponentUtil.SetDefaultObject(nextDefaultObject)
    CustomComponentUtil.SetGlobalPayloadKey(baseKey)
    _drawCompoList(box)

classes = (
    CU_UL_ComponentDisplayList,
    CU_PG_CustomComponentProperty,
)

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Scene.component_display_list = CollectionProperty(type=CU_PG_CustomComponentProperty)
    bpy.types.Scene.compo_stor_index = IntProperty()

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.component_display_list
    del bpy.types.Scene.compo_store_index
