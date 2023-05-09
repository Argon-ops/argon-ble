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

class SliderColliderDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return SliderColliderLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append("_playable"), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        default = AbstractDefaultSetter._GetDefaultFromPrefs(key)
        try:
            AbstractDefaultSetter._SetKeyValOnTargets(_Append("_playable"), True, targets)
            
        except BaseException as e:
            print(F" failed to set default {str(e)}")
            print(F"default keys: {default.keys()}")

    @staticmethod
    def OnRemoveKey(key : str, targets):
        suffixes = ("_playable", "_axis", "_invert")
        for suffix in suffixes:
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)

def _Append(suffix : str) -> str:
    return F"{SliderColliderLike.GetTargetKey()}{suffix}"

class SliderColliderLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_slider_collider"

    @staticmethod
    def AcceptsKey(key : str):
        return key == SliderColliderLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        mcl = context.scene.sliderColliderLike
        row = box.row()
        row.prop(mcl, "playable", text="Playable")
        row = box.row()
        row.prop(mcl, "axis", text="Unity Axis")
        row = box.row()
        row.prop(mcl, "invert", text="Invert")

    playable : EnumProperty(
        description="The playable whose position should be set according to the slide distance",
        items=lambda self, context : CLU.playablesItemCallback(context),
        get=lambda self: CLU.playableEnumIndex(_Append("_playable")),
        set=lambda self, value: CLU.setValueAtKey(_Append("_playable"), bpy.context.scene.as_custom[value].name)
    )

    axis : EnumProperty(
        items=(
            ('x', 'x', 'x'),
            ('y', 'y', 'y'),
            ('z', 'z', 'z'),
        ),
        description="The axis to use when measuring the linear slide distance. Unity space; so Y is up and Blender +Y is Unity -Z",
        get=lambda self: CLU.getIntFromKey(_Append("_axis")),
        set=lambda self, value: CLU.setValueAtKey(_Append("_axis"), value)
    )

    invert : BoolProperty(
        description="If true, send signal 1.0 - n. If false, send n.",
        get=lambda self : CLU.getBoolFromKey(_Append("_invert")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_invert"), value)
    )


classes = (
    SliderColliderLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.sliderColliderLike = bpy.props.PointerProperty(type=SliderColliderLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.sliderColliderLike

