from bb.mcd.core.componentlike.util.ColliderLikeShared import ColliderLikeShared
import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)

from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU


def getConvex(self):
    return CLU.getBoolFromKey("mel_mesh_collider_convex")


def setConvex(self, value):
    CLU.setValueAtKey("mel_mesh_collider_convex", value)


def getIsTrigger(self):
    return CLU.getBoolFromKey("mel_mesh_collider_is_trigger")


def setIsTrigger(self, value):
    CLU.setValueAtKey("mel_mesh_collider_is_trigger", value)


class MeshColliderDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key: str):
        return MeshColliderLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a: object, b: object) -> bool:
        return AbstractDefaultSetter._IsEqual("mel_mesh_collider_is_trigger", a, b) \
            and AbstractDefaultSetter._IsEqual("mel_mesh_collider_convex", a, b)

    @staticmethod
    def OnAddKey(key: str, val, targets):
        default = AbstractDefaultSetter._GetDefaultFromPrefs(key)
        try:
            AbstractDefaultSetter._SetKeyValOnTargets(
                "mel_mesh_collider_is_trigger", default['isTrigger'], targets)
            AbstractDefaultSetter._SetKeyValOnTargets(
                "mel_mesh_collider_convex", default['convex'], targets)
        except BaseException as e:
            print(F" failed to set default {str(e)}")
            print(F"default keys: {default.keys()}")

        ColliderLikeShared.OnAddKey(targets)

    @staticmethod
    def OnRemoveKey(key: str, targets):
        AbstractDefaultSetter._RemoveKey(
            "mel_mesh_collider_is_trigger", targets=targets)
        AbstractDefaultSetter._RemoveKey(
            "mel_mesh_collider_convex", targets=targets)

        ColliderLikeShared.OnRemoveKey(targets)


class MeshColliderLike(PropertyGroup, AbstractComponentLike):

    @staticmethod
    def AcceptsKey(key: str):
        return key == MeshColliderLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        mcl = context.scene.meshColliderLike
        row.prop(mcl, "convex", text="convex")
        row = box.row()
        row.prop(mcl, "isTrigger", text="isTrigger")

        def getOptionsString(cookingOptions: int) -> str:
            options = {2: "Faster Sim", 4: "Mesh Cleaning",
                       8: "Weld Colocated", 16: "Fast Midphase"}
            if cookingOptions < 2:
                return "None"
            if cookingOptions >= 30:
                return "Everything"
            result = ""
            for mask, description in options.items():
                if (mask & (cookingOptions & 31)) > 0:
                    result += F"|{description}"
            return result

        row = box.row()
        row.label(text="cooking options:")

        row = box.row()
        row.prop(mcl, "cookingOptions",
                 text=getOptionsString(mcl.cookingOptions))

        row = box.row()
        row.prop(mcl, "material", text="material")

    @staticmethod
    def GetTargetKey() -> str:
        return "mel_mesh_collider"

    convex: BoolProperty(
        name="convex",
        default=True,
        get=getConvex,
        set=setConvex)

    isTrigger: BoolProperty(
        name="isTrigger",
        default=False,
        get=getIsTrigger,
        set=setIsTrigger)

    cookingOptions: IntProperty(
        name="cooking_options",
        default=1,
        description="Set cooking options flags. You have to convert binary to decimal yourself, at the moment: add some combination of 2, 4, 8, 16 to set the desired flags. 30 = everything",
        get=lambda self: CLU.getIntFromKey(
            "mel_mesh_collider_cooking_options", default=30),
        set=lambda self, value: CLU.setValueAtKey(
            "mel_mesh_collider_cooking_options", value),
        min=0,
        max=31)

    material: StringProperty(
        default="",
        get=lambda self: CLU.getStringFromKey("mel_mesh_collider_material"),
        set=lambda self, value: CLU.setValueAtKey(
            "mel_mesh_collider_material", value)
    )


classes = (
    MeshColliderLike,
)


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Scene.meshColliderLike = bpy.props.PointerProperty(
        type=MeshColliderLike)


def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.meshColliderLike
