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

from bb.mcd.core.command import CommandsList
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU

suffixes = {
    "_preserve_children" : False,
}

class DestroyDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return DestroyLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append(), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        for suffix, defaultVal in suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(_Append(suffix), defaultVal, targets)

    @staticmethod
    def OnRemoveKey(key : str, targets):
        for suffix in suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets=targets)

def _Append(suffix : str = "") -> str:
    return F"{DestroyLike.GetTargetKey()}{suffix}"


class DestroyLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_destroy"

    @staticmethod
    def AcceptsKey(key : str):
        return key == DestroyLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        mcl = context.scene.destroyLike
        box.row().prop(mcl, "preserveChildren", text="Preserve Children")

    preserveChildren : BoolProperty(
        description="",
        get=lambda self : CLU.getBoolFromKey(self.Append("_preserve_children")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_preserve_children"), value)
    )


classes = (
    DestroyLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.destroyLike = bpy.props.PointerProperty(type=DestroyLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.destroyLike