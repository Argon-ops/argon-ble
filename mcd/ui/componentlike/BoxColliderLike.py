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
from mcd.ui.componentlike.util import ComponentLikeUtils as CLU

class BoxColliderDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return BoxColliderLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual("mel_box_collider_is_trigger", a, b) 

    @staticmethod
    def OnAddKey(key : str, val, targets):
        default = AbstractDefaultSetter._GetDefaultFromPrefs(key)
        try:
            AbstractDefaultSetter._SetKeyValOnTargets("mel_box_collider_is_trigger", default['isTrigger'], targets)
        except BaseException as e:
            print(F" failed to set default {str(e)}")
            print(F"default keys: {default.keys()}")

    @staticmethod
    def OnRemoveKey(key : str, targets):
        AbstractDefaultSetter._RemoveKey("mel_box_collider_is_trigger", targets=targets)


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

