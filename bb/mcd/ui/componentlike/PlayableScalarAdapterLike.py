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

# REGION LoadPost boilerplate

@persistent
def resubAllLoadPostPlayableScalarAdapter(dummy):
    perObjectFieldName = "playableScalarAdapterPerObjectData"

    fieldsAndPropNames = (
        ("target", "_target"), # for each object PointerProperty that needs updates, add a line here
        ("action", "_action"),
    )
    print(F"=== resub all for PScalarAdapter ===")
    for fieldAndPropName in fieldsAndPropNames:
        MsgbusUtils.resubscribeAll_LP(
            perObjectFieldName, 
            fieldAndPropName[0], 
            _Append(fieldAndPropName[1])) #,  
            # PlayableScalarAdapterPerObjectData.OwnerKey(fieldAndPropName[1])) # fieldAndPropName[1])

# add a load post handler so that we resubscribeAll upon loading a new file         
def setupLoadPost():
    from bb.mcd.util import AppHandlerHelper
    AppHandlerHelper.RefreshLoadPostHandler(resubAllLoadPostPlayableScalarAdapter) 

# END REGION LoadPost boilerplate


class PlayableScalarAdapterDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return PlayableScalarAdapterLike.AcceptsKey(key)

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
    return F"{PlayableScalarAdapterLike.GetTargetKey()}{suffix}"

class PlayableScalarAdapterPerObjectData(PropertyGroup, AbstractPerObjectData):

    target : PointerProperty(
        type=bpy.types.Object,
        description="TODO:MORE ACCURATE: Defines the object whose components should receive slider updates",
        update=lambda self, context :  MsgbusUtils.onObjectUpdate(
            context.active_object,
            self,
            "target",
            _Append("_target")
        )
    )

    # this doesn't need to be a per object value but it belongs here 
    isClipNameSpecifiedManually : BoolProperty(
        description="If true, specify the animation clip manually. If false, specify by picking from the available actions in this scene.",
        update=lambda self, context : CLU.setValueAtKey(_Append("_is_clip_name_specified_manually"), self.isClipNameSpecifiedManually)
    )

    clipName : StringProperty(
        description="The exact name of the animation clip. Use this field if the clip's name will not export as '<ObjectName>|<ActionName>",
        update=lambda self, context : CLU.setValueAtKey(_Append("_clip_name"), self.clipName)
    )

    action : PointerProperty(
        type=bpy.types.Action,
        description="The action that defines the animation that should be played",
        update=lambda self, context : MsgbusUtils.onObjectUpdate(
            context.active_object,
            self,
            "action",
            _Append("_action")
        )
    )


class PlayableScalarAdapterLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_playable_scalar_adapter"

    @staticmethod
    def AcceptsKey(key : str):
        return key == PlayableScalarAdapterLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        
        scpo : PlayableScalarAdapterPerObjectData = context.active_object.playableScalarAdapterPerObjectData
        mcl = context.scene.playableScalarAdapterLike

        # TODO: bool: either target or playable
        # target is presumably something with IScalarHandlers (at least one)
        boxb = box.box()
        # boxb.row().prop(mcl, "targetType", text="Target Type")
        # if mcl.targetType != "None":
        boxb.row().prop(scpo, "target", text="Target")
        boxb.row().prop(scpo, "isClipNameSpecifiedManually")

        if scpo.isClipNameSpecifiedManually:
            boxb.row().prop(scpo, "clipName")
        else :
            boxb.row().prop(scpo, "action")

        # if mcl.targetType == "Animation":
            # boxb.row().prop(mcl, "actionName")

        #todo audio


classes = (
    PlayableScalarAdapterPerObjectData,
    PlayableScalarAdapterLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Object.playableScalarAdapterPerObjectData = bpy.props.PointerProperty(type=PlayableScalarAdapterPerObjectData)
    bpy.types.Scene.playableScalarAdapterLike = bpy.props.PointerProperty(type=PlayableScalarAdapterLike)

def defer():
    resubAllLoadPostPlayableScalarAdapter(dummy=None)
    setupLoadPost()

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Object.playableScalarAdapterPerObjectData
    del bpy.types.Scene.playableScalarAdapterLike

