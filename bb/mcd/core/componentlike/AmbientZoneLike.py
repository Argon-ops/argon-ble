import bpy
from bpy.props import (StringProperty,
                       FloatProperty,
                       FloatVectorProperty,)
from bpy.types import (PropertyGroup,)

from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU
from bb.mcd.core.componentlike.util.ColliderLikeShared import ColliderLikeShared


_suffixes = {
    "_clip_name": "",
    "_volume": 1.0,
    "_fade": 1.5,
    "_scale_dimensions": (1.0, 1.0, 1.0),
}


def _Append(suffix: str) -> str:
    return F"{AmbientZoneLike.GetTargetKey()}{suffix}"


class AmbientZoneDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key: str):
        return AmbientZoneLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a: object, b: object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append("_clip_name"), a, b)

    @staticmethod
    def OnAddKey(key: str, val, targets):
        for suffix, defaultVal in _suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(
                _Append(suffix), defaultVal, targets)
        # This component-like adds a (trigger) collider on import; honor the collider marker.
        ColliderLikeShared.OnAddKey(targets)

    @staticmethod
    def OnRemoveKey(key: str, targets):
        for suffix in _suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)
        ColliderLikeShared.OnRemoveKey(targets)


class AmbientZoneLike(PropertyGroup, AbstractComponentLike):
    """Audio zone: a trigger volume that loops a sound on the Ambient bus while the
        player is inside. The object's mesh defines the shape; it is hidden on import."""

    @staticmethod
    def AcceptsKey(key: str):
        return key == AmbientZoneLike.GetTargetKey()

    @staticmethod
    def GetTargetKey() -> str:
        return "mel_ambient_zone"

    @staticmethod
    def Display(box, context) -> None:
        mcl = context.scene.ambientZoneLike
        box.row().prop(mcl, "clipName", text="Clip Name")
        row = box.row()
        row.prop(mcl, "volume", text="Volume")
        row.prop(mcl, "fade", text="Fade (s)")
        box.row().prop(mcl, "scaleDimensions", text="Scale Dimensions")

    clipName: StringProperty(
        description="Name of the audio clip (or SoundBank key) to loop. Registered on the "
                    "Ambient bus during import.",
        get=lambda self: CLU.getStringFromKey(_Append("_clip_name")),
        set=lambda self, value: CLU.setValueAtKey(_Append("_clip_name"), value),
    )

    volume: FloatProperty(
        description="Loudness of the loop while the player is inside (0..1). The Ambient "
                    "volume slider still applies on top of this.",
        get=lambda self: CLU.getFloatFromKey(_Append("_volume")),
        set=lambda self, value: CLU.setValueAtKey(_Append("_volume"), value),
        soft_min=0.0,
        soft_max=1.0,
    )

    fade: FloatProperty(
        description="Seconds to fade the loop in/out as the player enters/leaves. 0 = snap.",
        get=lambda self: CLU.getFloatFromKey(_Append("_fade")),
        set=lambda self, value: CLU.setValueAtKey(_Append("_fade"), value),
        soft_min=0.0,
        soft_max=10.0,
    )

    scaleDimensions: FloatVectorProperty(
        description="Scales the trigger box. Collider size = mesh-bounds-size * scaleDimensions",
        get=lambda self: CLU.getFloatArrayFromKey(_Append("_scale_dimensions")),
        set=lambda self, value: CLU.setValueAtKey(_Append("_scale_dimensions"), value),
        soft_min=0.001,
        soft_max=4.0,
    )


classes = (
    AmbientZoneLike,
)


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Scene.ambientZoneLike = bpy.props.PointerProperty(
        type=AmbientZoneLike)


def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.ambientZoneLike
