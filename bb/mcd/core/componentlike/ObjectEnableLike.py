import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)

from bb.mcd.util import ObjectLookupHelper
from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU

class ObjectEnableDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return ObjectEnableLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return True 

    @staticmethod
    def OnAddKey(key : str, val, targets):
        pass

    @staticmethod
    def OnRemoveKey(key : str, targets):
        pass


def _Append(suffix : str) -> str:
    return F"{ObjectEnableLike.GetTargetKey()}{suffix}"

from bb.mcd.core.componentlike.enablefilter.EnableFilterSettings import EnableFilterSettings

class ObjectEnableLike(EnableFilterSettings, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_object_enable"

    @staticmethod
    def AcceptsKey(key : str):
        return key == ObjectEnableLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        pass
       

classes = (
    ObjectEnableLike,
    )


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Object.fakeInt = bpy.props.IntProperty()
    bpy.types.Scene.objectEnableLike = bpy.props.PointerProperty(type=ObjectEnableLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.objectEnableLike
    del bpy.types.Object.fakeInt

