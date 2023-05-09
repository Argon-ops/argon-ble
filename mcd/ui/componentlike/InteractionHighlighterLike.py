import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)
from mcd.ui.componentlike.AbstractPerObjectData import AbstractPerObjectData
from mcd.ui.componentlike.enablefilter.SleepStateSettings import SleepStateSettings
from mcd.util import ObjectLookupHelper

from mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
from mcd.ui.componentlike.util import ObjectPointerMsgbusUtils as MsgbusUtils

from mcd.ui.actionstarterlist import ActionStarterList
from mcd.ui.componentlike import AbstractDefaultSetter
from mcd.ui.componentlike.util import ComponentLikeUtils as CLU
from mcd.ui.sharedtypes import TurnOnOffAction

import json

from bpy.app.handlers import persistent

# REGION LoadPost boilerplate

@persistent
def resubAllLoadPostInterHighlighter(dummy):
    perObjectFieldName = "highlighterPerObjectData"

    fieldsAndPropNames = (
        ("rendererTarget", 
         "_renderer_target"), # for each object PointerProperty that needs updates, add a line here
    )
    print(F"=== resub all for highlighter ===")
    for fieldAndPropName in fieldsAndPropNames:
        MsgbusUtils.resubscribeAll_LP(
            perObjectFieldName, 
            fieldAndPropName[0], 
            _Append(fieldAndPropName[1]),  
            HighlighterPerObjectData.OwnerKey(fieldAndPropName[1])) # fieldAndPropName[1])

# add a load post handler so that we resubscribeAll upon loading a new file         
def setupLoadPost():
    from mcd.util import AppHandlerHelper
    AppHandlerHelper.RefreshLoadPostHandler(resubAllLoadPostInterHighlighter) 

# END REGION LoadPost boilerplate


class InteractionHighlighterDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):

    @staticmethod
    def IsMultiSelectAllowed() -> bool:
        return False

    @staticmethod
    def AcceptsKey(key : str):
        return InteractionHighlighterLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append("_highlight_mat"), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        default = AbstractDefaultSetter._GetDefaultFromPrefs(key)
        try:
            AbstractDefaultSetter._SetKeyValOnTargets(_Append("_highlight_mat"), "Highlighter", targets)
            
        except BaseException as e:
            print(F" failed to set default {str(e)}")
            print(F"default keys: {default.keys()}")

    @staticmethod
    def OnRemoveKey(key : str, targets):
        suffixes = ("_highlight_mat", "_renderer_target")
        for suffix in suffixes:
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)
        
        for target in targets:
            target.property_unset("highlighterPerObjectData")

def _Append(suffix : str) -> str:
    return F"{InteractionHighlighterLike.GetTargetKey()}{suffix}"

class HighlighterPerObjectData(PropertyGroup, AbstractPerObjectData):
    """Per object data because highlighters might need to reference a renderer target"""

    rendererTarget : PointerProperty(
        type=bpy.types.Object,
        description="Optional: specify a highlight target other than this object. Useful, for example, if this object won't have a renderer. Defaults to this object.",
        update=lambda self, context : MsgbusUtils.onObjectUpdate(
            context.active_object, 
            self,
            "rendererTarget",
            _Append("_renderer_target"),
            MsgbusUtils.GetOwnerToken(context.active_object, HighlighterPerObjectData.OwnerKey("_renderer_target"))
        )
    )


class InteractionHighlighterLike(SleepStateSettings, AbstractComponentLike):

    @staticmethod
    def GetTargetKey() -> str:
        return "mel_interaction_highlighter"

    @staticmethod
    def AcceptsKey(key : str):
        return key == InteractionHighlighterLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        mcl = context.scene.interactionHighlighterLike

        boxb=box.box()
        boxb.row().prop(mcl, "mode", text="Mode")
        if mcl.mode == "HighlightMaterial":
            boxb.row().prop(mcl, "highlightMat", text="Highlight Material")
            # per obje
            hlpo = context.active_object.highlighterPerObjectData
            box.row().prop(hlpo, "rendererTarget", text="Renderer Target (Optional)")
        else:
            boxb.row().prop(mcl, "clickBeaconPrefab", text="Click Beacon Prefab")
            boxb.row().prop(mcl, "beaconPlacementOption", text="Beacon Placement Option")

        box.row().prop(mcl, "onSleepAction", text="On Sleep Action")

    mode : EnumProperty(
        items=(
            ('HighlightMaterial', 'HighlightMaterial', 'HL desc'),
            ('ClickBeacon', 'ClickBeacon', 'CB desc'),
            ('ClickAndNearbyBeacon', 'ClickAndNearbyBeacon', 'CANB desc'),
        ),
        get=lambda self : CLU.getIntFromKey(_Append("_mode")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_mode"), value),
    )

    highlightMat : StringProperty(
        name="Highlight Material",
        get=lambda self : CLU.getStringFromKey(_Append("_highlight_mat")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_highlight_mat"), value),
    )

    clickBeaconPrefab : StringProperty(
        get=lambda self : CLU.getStringFromKey(_Append("_click_beacon_prefab")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_click_beacon_prefab"), value),
    )

    beaconPlacementOption : EnumProperty(
        items=(
            ('ObjectPosition', 'Object Position', 'Position the beacon right on top of this object'),
            # ('TargetRendererBoundsCenter', 'Target Renderer Bounds Center', 'Position the beacon at the renderers center'),
            ('ColliderBoundsCenter', 'Collider Bounds Center', 'Position the beacon at the center of the collider attached to this object. (Assumes that there is one.)')
        ),
        get=lambda self : CLU.getIntFromKey(_Append("_beacon_placement_option")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_beacon_placement_option"), value),
    )

    onSleepAction : EnumProperty(
        items=TurnOnOffAction.TurnOnOffAction,
        description="Defines what this highlighter should do when it gets put to 'sleep': Nothing, Turn On, Turn Off. Turn Off is the default",
        get=lambda self : CLU.getIntFromKey(_Append("_on_sleep_action"), 2),
        set=lambda self, value : CLU.setValueAtKey(_Append("_on_sleep_action"), value)
    )
  

classes = (
    InteractionHighlighterLike,
    HighlighterPerObjectData,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Object.highlighterPerObjectData = bpy.props.PointerProperty(type=HighlighterPerObjectData)
    bpy.types.Scene.interactionHighlighterLike = bpy.props.PointerProperty(type=InteractionHighlighterLike)

    resubAllLoadPostInterHighlighter(dummy=None)
    setupLoadPost()

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Object.highlighterPerObjectData
    del bpy.types.Scene.interactionHighlighterLike

