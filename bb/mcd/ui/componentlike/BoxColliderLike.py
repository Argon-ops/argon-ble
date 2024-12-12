from bb.mcd.ui.componentlike.util.ColliderLikeShared import ColliderLikeShared
import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,
                       FloatVectorProperty)
from bpy.types import (PropertyGroup,)
from bb.mcd.util import ObjectLookupHelper

from bb.mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.ui.componentlike import AbstractDefaultSetter
from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU

_suffixes={
    "_is_trigger" : False,
    "_material" : "",
    "_scale_dimensions" : (1.0, 1.0, 1.0)
}

def _Append(suffix : str) -> str:
    return F"{BoxColliderLike.GetTargetKey()}{suffix}"


class BoxColliderDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return BoxColliderLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual("mel_box_collider_is_trigger", a, b) 

    @staticmethod
    def OnAddKey(key : str, val, targets):
        for suffix, defaultVal in _suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(_Append(suffix), defaultVal, targets)
        ColliderLikeShared.OnAddKey(targets)

    @staticmethod
    def OnRemoveKey(key : str, targets):
        for suffix in _suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)
        ColliderLikeShared.OnRemoveKey(targets)



class BoxColliderLike(PropertyGroup, AbstractComponentLike):

    @staticmethod
    def AcceptsKey(key : str):
        return key == BoxColliderLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        mcl = context.scene.boxColliderLike
        row = box.row()
        row.prop(mcl, "isTrigger", text = "isTrigger")
        row = box.row()
        row.prop(mcl, "material", text="material")
        box.row().prop(mcl, "scaleDimensions", text="Scale Dimensions")

    @staticmethod
    def GetTargetKey() -> str:
        return "mel_box_collider"

    isTrigger : BoolProperty(
        name="isTrigger",
        default = False,
        get=lambda self : CLU.getBoolFromKey("mel_box_collider_is_trigger"),
        set=lambda self, value : CLU.setValueAtKey("mel_box_collider_is_trigger", value)
    )
    
    material : StringProperty(
        default="",
        get=lambda self : CLU.getStringFromKey("mel_box_collider_material"),
        set=lambda self, value : CLU.setValueAtKey("mel_box_collider_material", value)
    )

    scaleDimensions : FloatVectorProperty(
        description="Defines a vector that will scale the box collider. The collider's size will = mesh-bounds-size * scaleDimensions",
        get=lambda self : CLU.getFloatArrayFromKey(_Append("_scale_dimensions")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_scale_dimensions"), value),
        soft_min=0.001,
        soft_max=4.0,
    )

classes = (
    BoxColliderLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.boxColliderLike = bpy.props.PointerProperty(type=BoxColliderLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.boxColliderLike

