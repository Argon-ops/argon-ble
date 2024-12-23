import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,
                       PointerProperty,
                       FloatVectorProperty,
                       IntVectorProperty,
                       BoolVectorProperty,
                       EnumProperty)
from bpy.types import (PropertyGroup,)
from bb.mcd.util import ObjectLookupHelper

from bb.mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.ui.componentlike import AbstractDefaultSetter
from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU
from bb.mcd.ui.componentlike.enablefilter.EnableFilterSettings import (
    EnableFilterSettings, EnableFilterDefaultSetter)

_baseKey = "mel_rigidbody"

_suffixes = {
    "_mass": 1.0,
    "_drag": 0.0,
    "_angular_drag": 0.05,
    "_use_gravity": True,
    "_is_kinematic": False,
    "_interpolate": 0,
    "_collision_detection": 0,
    "_freeze_position": (0.0, 0.0, 0.0),
    "_freeze_rotation": (0.0, 0.0, 0.0),
}


def _getSuffixKey(suffix: str) -> str:
    return F"{_baseKey}{suffix}"


class RigidbodyDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key: str):
        return RigidbodyLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a: object, b: object) -> bool:
        for suffix in _suffixes.keys():
            if not AbstractDefaultSetter._IsEqual(_getSuffixKey(suffix), a, b):
                return False
        return True

    @staticmethod
    def OnAddKey(key: str, val, targets):
        EnableFilterDefaultSetter.OnAddKey(RigidbodyLike, key, targets)
        for suffix, defaultVal in _suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(
                _getSuffixKey(suffix), defaultVal, targets)

    @staticmethod
    def OnRemoveKey(key: str, targets):
        EnableFilterDefaultSetter.OnRemoveKey(RigidbodyLike, targets)
        for suffix in _suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_getSuffixKey(suffix), targets)


class RigidbodyLike(EnableFilterSettings, AbstractComponentLike):

    @staticmethod
    def GetTargetKey() -> str:
        return _baseKey

    @staticmethod
    def AcceptsKey(key: str):
        return key == RigidbodyLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        rbl = context.scene.rigidbodyLike
        row.prop(rbl, "mass", text="mass")
        row = box.row()
        row.prop(rbl, "drag", text="drag")
        row = box.row()
        row.prop(rbl, "angularDrag", text="angular drag")
        row = box.row()
        row.prop(rbl, "useGravity", text="use gravity")
        row = box.row()
        row.prop(rbl, "isKinematic", text="is kinematic")
        row = box.row()
        row.prop(rbl, "interpolate", text="interpolate")
        row = box.row()
        row.prop(rbl, "collisionDetection", text="collision detection")
        row = box.row()
        row.prop(rbl, "freezePosition", text="freeze position")
        row = box.row()
        row.prop(rbl, "freezeRotation", text="freeze rotation")

    mass: FloatProperty(
        default=2.7,
        get=lambda self: CLU.getFloatFromKey(_getSuffixKey("_mass")),
        set=lambda self, value: CLU.setValueAtKey(
            _getSuffixKey("_mass"), value)
    )
    drag: FloatProperty(
        default=0.0,
        get=lambda self: CLU.getFloatFromKey(_getSuffixKey("_drag")),
        set=lambda self, value: CLU.setValueAtKey(
            _getSuffixKey("_drag"), value)
    )
    angularDrag: FloatProperty(
        default=0.05,
        get=lambda self: CLU.getFloatFromKey(_getSuffixKey("_angular_drag")),
        set=lambda self, value: CLU.setValueAtKey(
            _getSuffixKey("_angular_drag"), value)
    )
    useGravity: BoolProperty(
        default=True,
        get=lambda self: CLU.getBoolFromKey(_getSuffixKey("_use_gravity")),
        set=lambda self, value: CLU.setValueAtKey(
            _getSuffixKey("_use_gravity"), value)
    )
    isKinematic: BoolProperty(
        default=False,
        get=lambda self: CLU.getBoolFromKey(_getSuffixKey("_is_kinematic")),
        set=lambda self, value: CLU.setValueAtKey(
            _getSuffixKey("_is_kinematic"), value)
    )
    interpolate: EnumProperty(
        items=(
            ('0', 'None', 'none'),
            ('1', 'Interpolate', 'interpolate'),
            ('2', 'Extrapolate', 'extrapolate')),
        default='0',
        get=lambda self: CLU.getIntFromKey(_getSuffixKey("_interpolate")),
        set=lambda self, value: CLU.setValueAtKey(
            _getSuffixKey("_interpolate"), value)
    )
    collisionDetection: EnumProperty(
        items=(
            ('0', 'Discrete', 'discrete'),
            ('1', 'Continuous', 'continuous'),
            ('2', 'Continuous Dynamic', 'continuous dynamic'),
            ('3', 'Continuous Speculative', 'continuous speculative')),
        default='0',
        get=lambda self: CLU.getIntFromKey(
            _getSuffixKey("_collision_detection")),
        set=lambda self, value: CLU.setValueAtKey(
            _getSuffixKey("_collision_detection"), value)
    )
    freezePosition: BoolVectorProperty(
        size=3,
        get=lambda self: CLU.getFloatBackedBooleanVector(
            _getSuffixKey("_freeze_position")),
        set=lambda self, value: CLU.setFloatBackedBooleanVector(
            _getSuffixKey("_freeze_position"), value),
        subtype="XYZ",
    )
    freezeRotation: BoolVectorProperty(
        size=3,
        get=lambda self: CLU.getFloatBackedBooleanVector(_getSuffixKey(
            "_freeze_rotation")),  # exception when there's no key present?
        set=lambda self, value: CLU.setFloatBackedBooleanVector(
            _getSuffixKey("_freeze_rotation"), value),
        subtype="XYZ",
    )


classes = (
    RigidbodyLike,
)


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Scene.rigidbodyLike = bpy.props.PointerProperty(
        type=RigidbodyLike)


def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.rigidbodyLike
