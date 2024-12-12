import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)
from bb.mcd.util import ObjectLookupHelper

from bb.mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike

from bb.mcd.ui.command import CommandsList
from bb.mcd.ui.componentlike import AbstractDefaultSetter
from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU

suffixes = {
    "_prefab_name" : "<prefab_name>",
    "_parent_adopts_prefab" : False,
    "_prefab_adopts_children" : False,
    "_destroy_target" : True,
    # "_destroy_children_too" : False,
    "_match_position" : True,
    "_match_rotation" : True,
    "_compensate_import_rotation" : False,
    "_match_scale" : True,
}

class ReplaceWithPrefabDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return ReplaceWithPrefabLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append(), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        for suffix, defaultVal in suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(_Append(suffix), defaultVal, targets)

    @staticmethod
    def OnRemoveKey(key : str, targets):
        for suffix in suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets=targets)

def _Append(suffix : str = "") -> str:
    return F"{ReplaceWithPrefabLike.GetTargetKey()}{suffix}"


class ReplaceWithPrefabLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_replace_with_prefab"

    @staticmethod
    def AcceptsKey(key : str):
        return key == ReplaceWithPrefabLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        mcl = context.scene.replaceWithPrefabLike
        box.row().prop(mcl, "prefabName", text="Prefab name")
        box.row().prop(mcl, "prefabAdoptsChildren", text="Prefab adopts children")
        box.row().prop(mcl, "destroyTarget", text="Destroy Target")
        box = box.box()
        box.row().prop(mcl, "matchPosition", text="Match position")
        box.row().prop(mcl, "matchRotation", text="Match rotation")
        if mcl.matchRotation:
            box.row().prop(mcl, "compensateImportRotation", text="Compensate for import rotation")
        box.row().prop(mcl, "matchScale", text="Match scale")
        

    prefabName : StringProperty(
        description="The name of the prefab. No need to include the '.prefab' file extension.",
        get=lambda self : CLU.getStringFromKey(self.Append("_prefab_name")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_prefab_name"), value)
    )

    # required, non-optional
    # parentAdoptsPrefab : BoolProperty(
    #     description="If true, this object's parent will become the parent of the replacement prefab. If false, the prefab's parent will be null",
    #     get=lambda self : CLU.getBoolFromKey(self.Append("_parent_adopts_prefab")),
    #     set=lambda self, value : CLU.setValueAtKey(self.Append("_parent_adopts_prefab"), value)
    # )

    prefabAdoptsChildren : BoolProperty(
        description="If true, set this object's children as the prefab's children.",
        get=lambda self : CLU.getBoolFromKey(self.Append("_prefab_adopts_children")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_prefab_adopts_children"), value)
    )

    destroyTarget : BoolProperty(
        description="If true, destroy this object after swapping it for the prefab.",
        get=lambda self : CLU.getBoolFromKey(self.Append("_destroy_target")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_destroy_target"), value)
    )

    # destroyChildrenToo : BoolProperty(
    #     description="If true, this objects children will be destroyed. If false, they won't be.",
    #     get=lambda self : CLU.getBoolFromKey(self.Append("_destroy_children_too")),
    #     set=lambda self, value : CLU.setValueAtKey(self.Append("_destroy_children_too"), value)
    # )

    
    matchPosition : BoolProperty(
        description="",
        get=lambda self : CLU.getBoolFromKey(self.Append("_match_position")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_match_position"), value)
    )
    
    matchRotation : BoolProperty(
        description="",
        get=lambda self : CLU.getBoolFromKey(self.Append("_match_rotation")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_match_rotation"), value)
    )

    compensateImportRotation : BoolProperty(
        description="If you do not choose to correct rotation when exporting, you will likely want this option.",
        get=lambda self : CLU.getBoolFromKey(self.Append("_compensate_import_rotation")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_compensate_import_rotation"), value)
    )
    
    matchScale : BoolProperty(
        description="",
        get=lambda self : CLU.getBoolFromKey(self.Append("_match_scale")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_match_scale"), value)
    )

    


classes = (
    ReplaceWithPrefabLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.replaceWithPrefabLike = bpy.props.PointerProperty(type=ReplaceWithPrefabLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.replaceWithPrefabLike