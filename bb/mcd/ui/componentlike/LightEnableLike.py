import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,
                       PointerProperty,
                       FloatVectorProperty,
                       IntVectorProperty,
                       BoolVectorProperty,
                       EnumProperty)
from bpy.types import (PropertyGroup,)
from bb.mcd.util import ObjectLookupHelper

from bb.mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.ui.componentlike import AbstractDefaultSetter
from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU
from bb.mcd.ui.componentlike.enablefilter.EnableFilterSettings import (EnableFilterSettings, EnableFilterDefaultSetter)

_baseKey="mel_light_enable"

_suffixes = {
    }

def _getSuffixKey(suffix : str) -> str:
    return F"{_baseKey}{suffix}"

class LightEnableDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return LightEnableLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        for suffix in _suffixes.keys():
            if not AbstractDefaultSetter._IsEqual(_getSuffixKey(suffix), a, b):
                return False
        return True

    @staticmethod
    def OnAddKey(key : str, val, targets):
        EnableFilterDefaultSetter.OnAddKey(LightEnableLike, key, targets)
        for suffix, defaultVal in _suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(_getSuffixKey(suffix), defaultVal, targets)

    @staticmethod
    def OnRemoveKey(key : str, targets):
        EnableFilterDefaultSetter.OnRemoveKey(LightEnableLike, targets)
        for suffix in _suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_getSuffixKey(suffix), targets)



class LightEnableLike(EnableFilterSettings, AbstractComponentLike):

    @staticmethod
    def GetTargetKey() -> str:
        return _baseKey 

    @staticmethod
    def AcceptsKey(key : str):
        return key == LightEnableLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        raise "Don't add. there's not too much point. we don't think. just use object enable"

classes = (
    LightEnableLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.lightEnableLike = bpy.props.PointerProperty(type=LightEnableLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.lightEnableLike