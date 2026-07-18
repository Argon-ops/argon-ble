import bpy
from bpy.props import (FloatProperty,)
from bpy.types import (PropertyGroup,)

from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU


_suffixes = {
    "_thickness": 1.0,
}


def _Append(suffix: str) -> str:
    return F"{FacesToWallsLike.GetTargetKey()}{suffix}"


class FacesToWallsDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key: str):
        return FacesToWallsLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a: object, b: object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append("_thickness"), a, b)

    @staticmethod
    def OnAddKey(key: str, val, targets):
        for suffix, defaultVal in _suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(
                _Append(suffix), defaultVal, targets)

    @staticmethod
    def OnRemoveKey(key: str, targets):
        for suffix in _suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)


class FacesToWallsLike(PropertyGroup, AbstractComponentLike):
    """Turn each flat face of this object's mesh into a wall collider. On import, the C#
        side groups the mesh's coplanar, adjacent triangles into faces and adds one rotated
        child BoxCollider per face. 'thickness' sets the collider depth along the face normal."""

    @staticmethod
    def AcceptsKey(key: str):
        return key == FacesToWallsLike.GetTargetKey()

    @staticmethod
    def GetTargetKey() -> str:
        return "mel_faces_to_walls"

    @staticmethod
    def Display(box, context) -> None:
        mcl = context.scene.facesToWallsLike
        box.row().prop(mcl, "thickness", text="Thickness")

    thickness: FloatProperty(
        description="Depth of each generated wall collider along its face's normal "
                    "(the dimension the flat face itself has no extent in).",
        get=lambda self: CLU.getFloatFromKey(_Append("_thickness"), 1.0),
        set=lambda self, value: CLU.setValueAtKey(_Append("_thickness"), value),
        soft_min=0.001,
        soft_max=10.0,
    )


classes = (
    FacesToWallsLike,
)


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Scene.facesToWallsLike = bpy.props.PointerProperty(
        type=FacesToWallsLike)


def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.facesToWallsLike
