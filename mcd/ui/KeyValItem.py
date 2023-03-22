import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       CollectionProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList,
                       AddonPreferences)

from mcd.util import ObjectLookupHelper # WANT but try
# import sys
# ObjectLookupHelper = sys.modules[modulesNames['mcd.util.ObjectLookupHelper']]

# -------------------------------------------------------------------
# Getters / Setters for KeyValItem
# -------------------------------------------------------------------

def _getUniformValue(self) -> str:
    context = bpy.context
    if len(context.selected_objects) == 0:
        return ""
    if self.key not in context.selected_objects[0]:
        return ""
    result = context.selected_objects[0][self.key]
    for i in range(1, len(context.selected_objects)):
        sel = context.selected_objects[i]
        if self.key not in sel or sel[self.key] != result:
            return "__MIXED_VALS__"
    return result 

def getUniformValueStr(self) -> str:
    return str(_getUniformValue(self))

def getUniformValueInt(self) -> int:
    result = _getUniformValue(self)
    return result if isinstance(result, int) else 0

def getUniformValueFloat(self) -> float:
    result = _getUniformValue(self)
    return result if isinstance(result, float) else 0.0

def setUniformValue(self, value):
    ObjectLookupHelper._setValForKeyOnSelected(self.key, bpy.context, value)

# -------------------------------------------------------------------
#   Collection
# -------------------------------------------------------------------

class CUSTOM_PG_KeyValItem(PropertyGroup):
    """ Define a key value pair
    
    and prop name that is used to switch between val, vint, and vfloat.
    The three value properties (val, vint, vfloat) read/write their values
    from the selected objects using getters and setters """

    key: StringProperty(
        name="key",
        default="")
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
    handlingHint : StringProperty(
        name="handlingHint",)


def register():
    from bpy.utils import register_class
    register_class(CUSTOM_PG_KeyValItem)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(CUSTOM_PG_KeyValItem)