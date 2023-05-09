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


class AudioEnableDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return AudioEnableLike.AcceptsKey(key)

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
    return F"{AudioEnableLike.GetTargetKey()}{suffix}"


class AudioEnableLike(EnableFilterSettings, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_audio_enable"

    @staticmethod
    def AcceptsKey(key : str):
        return key == AudioEnableLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        mcl = context.scene.audioEnableLike
        row = box.row()
        row.prop(mcl, "clipName", text="Clip Name")
        row = box.row()
        row.prop(mcl, "loop", text="Loop")

    clipName : StringProperty(
        get=lambda self : CLU.getStringFromKey(_Append("_clip_name")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_clip_name"), value),
    )
    loop : BoolProperty(
        get=lambda self : CLU.getBoolFromKey(_Append("_loop")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_loop"), value)
    )

classes = (
    AudioEnableLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.audioEnableLike = bpy.props.PointerProperty(type=AudioEnableLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.audioEnableLike

