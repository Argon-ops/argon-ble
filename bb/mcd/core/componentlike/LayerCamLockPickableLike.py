import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)

from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.core.componentlike import AbstractDefaultSetter

suffixes = {
    "mel_layer" : "CamLockPickable",
}

class LayerCamLockPickableDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return LayerCamLockPickableLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        for key in suffixes.keys():
            if not AbstractDefaultSetter._IsEqual(_Append(key), a, b):
                return False
        return True

    @staticmethod
    def OnAddKey(key : str, val, targets):
        for key, val in suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(key, val, targets)
            
    @staticmethod
    def OnRemoveKey(key : str, targets):
        for key in suffixes.keys():
            AbstractDefaultSetter._RemoveKey(key, targets)

def _Append(suffix : str) -> str:
    return F"{LayerCamLockPickableLike.GetTargetKey()}{suffix}"

# TODO: unfortunately this is flawed. because the inspector decides that there is both a layer and a layercamlockpickable
#    even if we only add a layercamlockpickable.
#     instead, add modes to the LayerLike: 
#       bool UseArgonSpecificLayer / UseCustomLayer
#        an enum of Argon specific layers to choose from
#        
class LayerCamLockPickableLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_layer_cam_lock_pickable"

    @staticmethod
    def AcceptsKey(key : str):
        return key == LayerCamLockPickableLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        pass

    

classes = (
    LayerCamLockPickableLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Scene.layerCamLockPickableLike = bpy.props.PointerProperty(type=LayerCamLockPickableLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.layerCamLockPickableLike

