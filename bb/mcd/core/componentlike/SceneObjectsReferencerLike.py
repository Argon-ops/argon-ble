from bb.mcd.core.componentlike.util.ColliderLikeShared import ColliderLikeShared
import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)
from bb.mcd.util import ObjectLookupHelper

from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU

class SceneObjectsReferencerDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return SceneObjectsReferencerLike.AcceptsKey(key)

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

        ColliderLikeShared.OnAddKey(targets)

    @staticmethod
    def OnRemoveKey(key : str, targets):
        AbstractDefaultSetter._RemoveKey("mel_box_collider_is_trigger", targets=targets)
        
        ColliderLikeShared.OnRemoveKey(targets)


def _Append(suffix : str) -> str:
    return F"{SceneObjectsReferencerLike.GetTargetKey()}{suffix}"

class SceneObjectsReferencerLike(PropertyGroup, AbstractComponentLike):

    @staticmethod
    def AcceptsKey(key : str):
        return key == SceneObjectsReferencerLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        mcl = context.scene.sceneObjectsReferencerLike
        row = box.row()
        row.prop(mcl, "objectName1", text = "Object Name")

    @staticmethod
    def GetTargetKey() -> str:
        return "mel_scene_objects_referencer"

    
    objectName1 : StringProperty( # TODO : actually do a list instead of just offering one object
        default="",
        get=lambda self : CLU.getStringFromKey(_Append("_object_name_1")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_object_name_1"), value)
    )

classes = (
    SceneObjectsReferencerLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.sceneObjectsReferencerLike = bpy.props.PointerProperty(type=SceneObjectsReferencerLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.sceneObjectsReferencerLike

