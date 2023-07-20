import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)

from mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
from mcd.ui.componentlike import AbstractDefaultSetter
from mcd.ui.componentlike.AbstractPerObjectData import AbstractPerObjectData
from mcd.ui.componentlike.util import ComponentLikeUtils as CLU

from mcd.ui.componentlike.util import ObjectPointerMsgbusUtils as MsgbusUtils

from bpy.app.handlers import persistent

# REGION LoadPost boilerplate

@persistent
def resubAllLoadPostSliderCollider(dummy):
    perObjectFieldName = "sliderColliderPerObjectData"

    fieldsAndPropNames = (
        ("target", "_target"), # for each object PointerProperty that needs updates, add a line here
        ("action", "_action"),
    )
    print(F"=== resub all for slider collider ===")
    for fieldAndPropName in fieldsAndPropNames:
        MsgbusUtils.resubscribeAll_LP(
            perObjectFieldName, 
            fieldAndPropName[0], 
            _Append(fieldAndPropName[1])) #,  
            # SliderColliderPerObjectData.OwnerKey(fieldAndPropName[1])) # fieldAndPropName[1])

# add a load post handler so that we resubscribeAll upon loading a new file         
def setupLoadPost():
    from mcd.util import AppHandlerHelper
    AppHandlerHelper.RefreshLoadPostHandler(resubAllLoadPostSliderCollider) 

# END REGION LoadPost boilerplate


class SliderColliderDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return SliderColliderLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append("_playable"), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        default = AbstractDefaultSetter._GetDefaultFromPrefs(key)
        try:
            AbstractDefaultSetter._SetKeyValOnTargets(_Append("_playable"), True, targets)
            
        except BaseException as e:
            print(F" failed to set default {str(e)}")
            print(F"default keys: {default.keys()}")

    @staticmethod
    def OnRemoveKey(key : str, targets):
        suffixes = ("_playable", "_axis", "_invert")
        for suffix in suffixes:
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)

def _Append(suffix : str) -> str:
    return F"{SliderColliderLike.GetTargetKey()}{suffix}"

class SliderColliderPerObjectData(PropertyGroup, AbstractPerObjectData):
    #  per new thinking regarding ColliderSliders and (tb created) ANimSliders
    #    the Slider just targets an object, not a Playable. (which never made sense)
    #  Infact: COllider and ANim sliders could be the same 'Like' class. Just with an option
    #    is it Collider type or ANim type
    target : PointerProperty(
        type=bpy.types.Object,
        description="TODO:MORE ACCURATE: Defines the object whose components should receive slider updates",
        update=lambda self, context : MsgbusUtils.onObjectUpdate(
            context.active_object,
            self,
            "target",
            _Append("_target")
            # MsgbusUtils.GetOwnerToken(context.active_object, SliderColliderPerObjectData.OwnerKey("_target"))
        )
    )

    action : PointerProperty(
        type=bpy.types.Action,
        description="The action that defines the animation that should get slid",
        update=lambda self, context : MsgbusUtils.onObjectUpdate(
            context.active_object,
            self,
            "action",
            _Append("_action")
            # MsgbusUtils.GetOwnerToken(context.active_object, SliderColliderPerObjectData.OwnerKey("_action"))
        )
    )


class SliderColliderLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_slider_collider"

    @staticmethod
    def AcceptsKey(key : str):
        return key == SliderColliderLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        
        scpo = context.active_object.sliderColliderPerObjectData
        mcl = context.scene.sliderColliderLike

        # TODO: bool: either target or playable
        # target is presumably something with IScalarHandlers (at least one)
        boxb = box.box()
        boxb.row().prop(mcl, "targetType", text="Target Type")
        if mcl.targetType != "None":
            boxb.row().prop(scpo, "target", text="Target")
            if mcl.targetType == "Animation":
                # boxb.row().prop(mcl, "actionName")
                boxb.row().prop(scpo, "action")

        # box.row().prop(mcl, "playable", text="Playable")
        row = box.row()
        row.prop(mcl, "axis", text="Unity Axis")
        row = box.row()
        row.prop(mcl, "invert", text="Invert")

    targetType : EnumProperty(
        items=(
            ("None", "None", "None"),
            ("Animation", "Animation", "Animation"),
            ("Object", "Object", "Object"),
        ),
        get=lambda self : CLU.getIntFromKey(_Append("_target_type"), 0),
        set=lambda self, value : CLU.setValueAtKey(_Append("_target_type"), value)
    )

    # actionName : StringProperty( # TODO: convert to enum
    #     get=lambda self : CLU.getStringFromKey(_Append("_action_name")),
    #     set=lambda self, value : CLU.setValueAtKey(_Append("_action_name"), value)
    # )

    # playable : EnumProperty(
    #     description="The playable whose position should be set according to the slide distance",
    #     items=lambda self, context : CLU.playablesItemCallback(context),
    #     get=lambda self: CLU.playableEnumIndex(_Append("_playable")),
    #     set=lambda self, value: CLU.setValueAtKey(_Append("_playable"), bpy.context.scene.as_custom[value].name)
    # )

    axis : EnumProperty(
        items=(
            ('x', 'x', 'x'),
            ('y', 'y', 'y'),
            ('z', 'z', 'z'),
        ),
        description="The axis to use when measuring the linear slide distance. Unity space; so Y is up and Blender +Y is Unity -Z",
        get=lambda self: CLU.getIntFromKey(_Append("_axis")),
        set=lambda self, value: CLU.setValueAtKey(_Append("_axis"), value)
    )

    invert : BoolProperty(
        description="If true, send signal 1.0 - n. If false, send n.",
        get=lambda self : CLU.getBoolFromKey(_Append("_invert")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_invert"), value)
    )


classes = (
    SliderColliderPerObjectData,
    SliderColliderLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Object.sliderColliderPerObjectData = bpy.props.PointerProperty(type=SliderColliderPerObjectData)
    bpy.types.Scene.sliderColliderLike = bpy.props.PointerProperty(type=SliderColliderLike)

    resubAllLoadPostSliderCollider(dummy=None)
    setupLoadPost()

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Object.sliderColliderPerObjectData
    del bpy.types.Scene.sliderColliderLike

