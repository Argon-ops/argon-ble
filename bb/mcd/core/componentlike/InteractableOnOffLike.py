import bpy
from bpy.props import (BoolProperty,)
from bpy.types import (PropertyGroup,)

from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU

suffixes = {
    "_click_handler" : False,
    "_trigger_handler" : False,
    "_highlighter" : False,
    "_collider" : False,
}

class InteractableOnOffDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return InteractableOnOffLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        for suffix in suffixes.keys():
            if not AbstractDefaultSetter._IsEqual(_Append(suffix), a, b):
                return False
        return True

    @staticmethod
    def OnAddKey(key : str, val, targets):
        for suffix, defaultVal in suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(_Append(suffix), defaultVal, targets)

    @staticmethod
    def OnRemoveKey(key : str, targets):
        for target in targets:
            if InteractableOnOffLike.GetTargetKey() in target:
                del target[InteractableOnOffLike.GetTargetKey()]
        for suffix in suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets=targets)

def _Append(suffix : str = "") -> str:
    return F"{InteractableOnOffLike.GetTargetKey()}{suffix}"


class InteractableOnOffLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_interactable_on_off"

    @staticmethod
    def AcceptsKey(key : str):
        return key == InteractableOnOffLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        mcl = context.scene.interactableOnOffLike
        box.row().prop(mcl, "clickHandler", text="Click Handler")
        box.row().prop(mcl, "triggerHandler", text="Trigger Handler")
        box.row().prop(mcl, "highlighter", text="Highlighter")
        box.row().prop(mcl, "collider", text="Collider")

    clickHandler : BoolProperty(
        description="if true, the click handler will also be toggled on/off",
        get=lambda self : CLU.getBoolFromKey(self.Append("_click_handler")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_click_handler"), value)
    )

    triggerHandler : BoolProperty(
        description="if true, the trigger handler will also be toggled on/off",
        get=lambda self : CLU.getBoolFromKey(self.Append("_trigger_handler")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_trigger_handler"), value)
    )

    highlighter : BoolProperty(
        description="if true, the highlighter will also be toggled on/off",
        get=lambda self : CLU.getBoolFromKey(self.Append("_highlighter")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_highlighter"), value)
    )

    collider : BoolProperty(
        description="if true, the collider will also be toggled on/off",
        get=lambda self : CLU.getBoolFromKey(self.Append("_collider")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_collider"), value)
    )


classes = (
    InteractableOnOffLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Scene.interactableOnOffLike = bpy.props.PointerProperty(type=InteractableOnOffLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.interactableOnOffLike
