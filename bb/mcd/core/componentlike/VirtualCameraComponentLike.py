import bpy
from bpy.types import (PropertyGroup,)

from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.core.componentlike import AbstractDefaultSetter


class VirtualCameraDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return VirtualCameraComponentLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return True

    @staticmethod
    def OnAddKey(key : str, val, targets):
        pass

    @staticmethod
    def OnRemoveKey(key : str, targets):
        for target in targets:
            if VirtualCameraComponentLike.GetTargetKey() in target:
                del target[VirtualCameraComponentLike.GetTargetKey()]


class VirtualCameraComponentLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_virtual_camera"

    @staticmethod
    def AcceptsKey(key : str):
        return key == VirtualCameraComponentLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        pass


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
