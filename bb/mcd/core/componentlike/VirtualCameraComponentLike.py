import bpy
from bpy.props import (BoolProperty,)
from bpy.types import (PropertyGroup,)

from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU

suffixes = {
    "_destroy_camera" : True,
}

class VirtualCameraDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return VirtualCameraComponentLike.AcceptsKey(key)

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
            if VirtualCameraComponentLike.GetTargetKey() in target:
                del target[VirtualCameraComponentLike.GetTargetKey()]
        for suffix in suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets=targets)

def _Append(suffix : str = "") -> str:
    return F"{VirtualCameraComponentLike.GetTargetKey()}{suffix}"


class VirtualCameraComponentLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_virtual_camera"

    @staticmethod
    def AcceptsKey(key : str):
        return key == VirtualCameraComponentLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        mcl = context.scene.virtualCameraComponentLike
        box.row().prop(mcl, "destroyCamera", text="Destroy Camera")

    destroyCamera : BoolProperty(
        description="If true, the (original Unity) Camera will be destroyed. If false, it will be left in place in which case you'll have a cinemachine camera and a regular camera on the same object. You usually don't want that.",
        get=lambda self : CLU.getBoolFromKey(self.Append("_destroy_camera")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_destroy_camera"), value)
    )


classes = (
    VirtualCameraComponentLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Scene.virtualCameraComponentLike = bpy.props.PointerProperty(type=VirtualCameraComponentLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.virtualCameraComponentLike
