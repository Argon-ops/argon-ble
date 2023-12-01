import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)

from mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
from mcd.ui.componentlike import AbstractDefaultSetter
from mcd.ui.componentlike.util import ComponentLikeUtils as CLU
from mcd.ui.componentlike.enablefilter.EnableFilterSettings import EnableFilterSettings


class SwapMaterialEnableDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return SwapMaterialEnableLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append("_clip_name"), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        default = AbstractDefaultSetter._GetDefaultFromPrefs(key)
        try:
            AbstractDefaultSetter._SetKeyValOnTargets(_Append("_clip_name"), "", targets)
            AbstractDefaultSetter._SetKeyValOnTargets(_Append("_loop"), False, targets)
            
        except BaseException as e:
            print(F" failed to set default {str(e)}")
            print(F"default keys: {default.keys()}")

    @staticmethod
    def OnRemoveKey(key : str, targets):
        suffixes = ("_clip_name", "_loop")
        for suffix in suffixes:
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)

def _Append(suffix : str) -> str:
    return F"{SwapMaterialEnableLike.GetTargetKey()}{suffix}"


class SwapMaterialEnableLike(EnableFilterSettings, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_swap_material_enable"

    @staticmethod
    def AcceptsKey(key : str):
        return key == SwapMaterialEnableLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        mcl = context.scene.swapMaterialEnableLike
        row = box.row()
        row.prop(mcl, "material", text="Material Name")

    material : StringProperty(
        get=lambda self : CLU.getStringFromKey(_Append("_material")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_material"), value),
    )
    

classes = (
    SwapMaterialEnableLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.swapMaterialEnableLike = bpy.props.PointerProperty(type=SwapMaterialEnableLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.swapMaterialEnableLike

