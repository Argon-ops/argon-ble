import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)
from mcd.util import ObjectLookupHelper

from mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
from mcd.ui.componentlike import AbstractDefaultSetter

class DemoException(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class StaticFlagsDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return StaticFlagsLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual(StaticFlagsLike.GetTargetKey(), a, b) 

    @staticmethod
    def OnAddKey(key : str, val, targets):
        AbstractDefaultSetter._SetKeyValOnTargets(StaticFlagsLike.GetTargetKey(), ~0, targets)

    @staticmethod
    def OnRemoveKey(key : str, targets):
        # no additional clean up since we use only the target key
        pass

def _getInt() -> int:
    result = ObjectLookupHelper._getFirstVal(StaticFlagsLike.GetTargetKey(), bpy.context)
    return result if result is not None else 0

def _setFlag(index, isOn) -> None:
    mask = 1 << index
    stor = _getInt()
    if isOn:
        ObjectLookupHelper._setValForKeyOnSelected(StaticFlagsLike.GetTargetKey(), bpy.context, stor | mask)
        return

    mask = ~mask
    ObjectLookupHelper._setValForKeyOnSelected(StaticFlagsLike.GetTargetKey(), bpy.context, stor & mask)

def _getFlag(index : int) -> bool:
    mask = 1 << index
    stor = _getInt()
    return bool(stor & mask)

def getEverything() -> bool:
    return _getInt() == 0b1111111

def setEverything(everything : bool) -> None:
    ObjectLookupHelper._setValForKeyOnSelected(StaticFlagsLike.GetTargetKey(), bpy.context, 0b1111111 if everything else 0)

def getNothing() -> bool:
    return _getInt() == 0


class StaticFlagsLike(PropertyGroup, AbstractComponentLike):

    @staticmethod
    def AcceptsKey(key : str):
        return key == StaticFlagsLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        mcl = context.scene.staticFlagsLike
        for name in StaticFlagsLike._FlagNames():
            row.prop(mcl, name, text=name)
            row = box.row()

    @staticmethod
    def GetTargetKey() -> str:
        return "mel_static_flags"
    
    @staticmethod
    def _FlagNames():
        return [
            "nothing",
            "everything",
            "contributeGI",
            "occluderStatic",
            "batchingStatic",
            "navigationStatic",
            "occludeeStatic",
            "offMeshLinkGeneration",
            "reflectionProbeStatic"]

    nothing : BoolProperty(
        get=lambda self : getNothing(),
        set=lambda self, value : setEverything(value == False)
    )
    everything : BoolProperty(
        get=lambda self : getEverything(),
        set=lambda self, value : setEverything(value)
    )
    contributeGI : BoolProperty(
        get=lambda self : _getFlag(0),
        set=lambda self, value : _setFlag(0, value)
    )
    occluderStatic : BoolProperty(
        get=lambda self : _getFlag(1),
        set=lambda self, value : _setFlag(1, value)
    )
    batchingStatic : BoolProperty(
        get=lambda self : _getFlag(2),
        set=lambda self, value : _setFlag(2, value)
    )
    navigationStatic : BoolProperty(
        get=lambda self : _getFlag(3),
        set=lambda self, value : _setFlag(3, value)
    )
    occludeeStatic : BoolProperty(
        get=lambda self : _getFlag(4),
        set=lambda self, value : _setFlag(4, value)
    )
    offMeshLinkGeneration : BoolProperty(
        get=lambda self : _getFlag(5),
        set=lambda self, value : _setFlag(5, value)
    )
    reflectionProbeStatic : BoolProperty(
        get=lambda self : _getFlag(6),
        set=lambda self, value : _setFlag(6, value)
    )
    

classes = (
    StaticFlagsLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    # bpy.types.Object.staticFlagsLike = bpy.props.PointerProperty(type=StaticFlagsLike)
    bpy.types.Scene.staticFlagsLike = bpy.props.PointerProperty(type=StaticFlagsLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.staticFlagsLike