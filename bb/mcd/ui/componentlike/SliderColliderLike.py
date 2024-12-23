import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)

from bb.mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.ui.componentlike import AbstractDefaultSetter
from bb.mcd.ui.componentlike.AbstractPerObjectData import AbstractPerObjectData
from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU
from bb.mcd.ui.componentlike.util import ObjectPointerMsgbusUtils as MsgbusUtils

from bpy.app.handlers import persistent

#region LoadPost boilerplate


@persistent
def resubAllLoadPostSliderCollider(dummy):
    perObjectFieldName = "sliderColliderPerObjectData"

    fieldsAndPropNames = (
        ("target", "_target"),
        ("action", "_action"),
    )

    for fieldAndPropName in fieldsAndPropNames:
        MsgbusUtils.resubscribeAll_LP(
            perObjectFieldName,
            fieldAndPropName[0],
            _Append(fieldAndPropName[1]))


def setupLoadPost():
    """add a load post handler so that we resubscribeAll upon loading a new file"""
    from bb.mcd.util import AppHandlerHelper
    AppHandlerHelper.RefreshLoadPostHandler(resubAllLoadPostSliderCollider)

#endregion LoadPost boilerplate


class SliderColliderDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key: str):
        return SliderColliderLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a: object, b: object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append("_playable"), a, b)

    @staticmethod
    def OnAddKey(key: str, val, targets):
        default = AbstractDefaultSetter._GetDefaultFromPrefs(key)
        try:
            AbstractDefaultSetter._SetKeyValOnTargets(
                _Append("_playable"), True, targets)

        except BaseException as e:
            print(F" failed to set default {str(e)}")
            print(F"default keys: {default.keys()}")

    @staticmethod
    def OnRemoveKey(key: str, targets):
        suffixes = ("_playable", "_axis", "_invert")
        for suffix in suffixes:
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)


def _Append(suffix: str) -> str:
    return F"{SliderColliderLike.GetTargetKey()}{suffix}"


class SliderColliderPerObjectData(PropertyGroup, AbstractPerObjectData):
    target: PointerProperty(
        type=bpy.types.Object,
        description="Defines the object whose components should receive slider updates ",
        update=lambda self, context: MsgbusUtils.onObjectUpdate(
            context.active_object,
            self,
            "target",
            _Append("_target")
        )
    )

    action: PointerProperty(
        type=bpy.types.Action,
        description="The action that defines the animation that should get slid",
        update=lambda self, context: MsgbusUtils.onObjectUpdate(
            context.active_object,
            self,
            "action",
            _Append("_action")
        )
    )


class SliderColliderLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_slider_collider"

    @staticmethod
    def AcceptsKey(key: str):
        return key == SliderColliderLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:

        scpo = context.active_object.sliderColliderPerObjectData
        mcl = context.scene.sliderColliderLike

        boxb = box.box()
        boxb.row().prop(mcl, "targetType", text="Target Type")
        if mcl.targetType != "None":
            boxb.row().prop(scpo, "target", text="Target")
            if mcl.targetType == "Animation":
                boxb.row().prop(scpo, "action")

        row = box.row()
        row.prop(mcl, "axis", text="Unity Axis")
        row = box.row()
        row.prop(mcl, "invert", text="Invert")

    targetType: EnumProperty(
        items=(
            ("None", "None", "None"),
            ("Animation", "Animation", "Animation"),
            ("Object", "Object", "Object"),
        ),
        get=lambda self: CLU.getIntFromKey(_Append("_target_type"), 0),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_target_type"), value)
    )

    axis: EnumProperty(
        items=(
            ('x', 'x', 'x'),
            ('y', 'y', 'y'),
            ('z', 'z', 'z'),
        ),
        description="The axis to use when measuring the linear slide distance. In Unity space: Y is up and Blender +Y is Unity -Z",
        get=lambda self: CLU.getIntFromKey(_Append("_axis")),
        set=lambda self, value: CLU.setValueAtKey(_Append("_axis"), value)
    )

    invert: BoolProperty(
        description="If true, send signal 1.0 - n. If false, send n.",
        get=lambda self: CLU.getBoolFromKey(_Append("_invert")),
        set=lambda self, value: CLU.setValueAtKey(_Append("_invert"), value)
    )


classes = (
    SliderColliderPerObjectData,
    SliderColliderLike,
)


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Object.sliderColliderPerObjectData = bpy.props.PointerProperty(
        type=SliderColliderPerObjectData)
    bpy.types.Scene.sliderColliderLike = bpy.props.PointerProperty(
        type=SliderColliderLike)


def testCallThisFunc():
    print(F"*** test call this func got called 888 ffaabb")


def defer():
    resubAllLoadPostSliderCollider(dummy=None)
    setupLoadPost()


def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Object.sliderColliderPerObjectData
    del bpy.types.Scene.sliderColliderLike
