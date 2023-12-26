import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,
                       FloatVectorProperty)
from bpy.types import (PropertyGroup,)
from bb.mcd.ui.componentlike.AbstractPerObjectData import AbstractPerObjectData
from bb.mcd.ui.componentlike.enablefilter.SleepStateSettings import SleepStateSettings
from bb.mcd.util import ObjectLookupHelper

from bb.mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.ui.componentlike.util import ObjectPointerMsgbusUtils as MsgbusUtils

from bb.mcd.ui.actionstarterlist import ActionStarterList
from bb.mcd.ui.componentlike import AbstractDefaultSetter
from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU
from bb.mcd.ui.sharedtypes import TurnOnOffAction

import json

from bpy.app.handlers import persistent

# REGION LoadPost boilerplate

@persistent
def resubAllLoadPostInterHighlighter(dummy):
    perObjectFieldName = "highlighterPerObjectData"

    fieldsAndPropNames = (
        ("rendererTarget", "_renderer_target"), # for each object PointerProperty that needs updates, add a line here
    )
    print(F"=== resub all for highlighter ===")
    for fieldAndPropName in fieldsAndPropNames:
        MsgbusUtils.resubscribeAll_LP(
            perObjectFieldName, 
            fieldAndPropName[0], 
            _Append(fieldAndPropName[1])) #,  
            #HighlighterPerObjectData.OwnerKey(fieldAndPropName[1])) # fieldAndPropName[1])

# add a load post handler so that we resubscribeAll upon loading a new file         
def setupLoadPost():
    from bb.mcd.util import AppHandlerHelper
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
            _Append("_renderer_target")
        )
    )

# TODO: not here: bug where the program renames one of your objects to z_Duks_sharedDataRoot ???

class InteractionHighlighterLike(SleepStateSettings, AbstractComponentLike):

    @staticmethod
    def GetTargetKey() -> str:
        return "mel_interaction_highlighter"

    @staticmethod
    def AcceptsKey(key : str):
        return key == InteractionHighlighterLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        mcl = context.scene.interactionHighlighterLike

        boxb=box.box()
        boxb.row().prop(mcl, "mode", text="Mode")
        if mcl.mode == "HighlightMaterial":
            boxb.row().prop(mcl, "highlightMat", text="Highlight Material")

            # fend off a None error. although not sure how we get here when active_object is None (guess: copy pasting an object that has this?)
            if context.active_object is not None:
                # per obje
                hlpo = context.active_object.highlighterPerObjectData
                box.row().prop(hlpo, "rendererTarget", text="Renderer Target (Optional)")
        elif mcl.mode == "ClickBeacon":
            boxb.row().prop(mcl, "clickBeaconPrefab", text="Click Beacon Prefab")
            boxb.row().prop(mcl, "beaconPlacementOption", text="Beacon Placement Option")
            boxb.row().prop(mcl, "beaconNudgeVector", text="Beacon Nudge")
            boxb.row().prop(mcl, "beaconShouldRotateNinety", text="Rotate Ninety")
            boxb.row().prop(mcl, "visibleRadius", text="Visible Radius")

        box.row().prop(mcl, "downtimeSeconds", text="Downtime Seconds")
        box.row().prop(mcl, "onSleepAction", text="On Sleep Action")
        box.row().prop(mcl, "isInvisibleToProximity", text="Is Invisible to Proximity")

    mode : EnumProperty(
        items=(
            ('HighlightMaterial', 'HighlightMaterial', 'HL desc'),
            ('ClickBeacon', 'ClickBeacon', 'CB desc'),
            # ('ClickAndNearbyBeacon', 'ClickAndNearbyBeacon', 'CANB desc'),
            ('Invisible', 'Invisible', 'A highlighter does nothing. Dummy highlighters are needed in some situations')
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
        description="Defines the name of the prefab that should be used as a click beacon. For example 'my-sprite'. Path not needed. '.prefab' not needed ",
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

    beaconNudgeVector : FloatVectorProperty(
        description="Defines how far to move the beacon away from its anchor position. Scales with renderer or collider bounds where possible",
        get=lambda self : CLU.getFloatArrayFromKey(_Append("_beacon_nudge_vector")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_beacon_nudge_vector"), value),
        soft_min=-3.0,
        soft_max=3.0,
    )

    beaconShouldRotateNinety : BoolProperty(
        description="Rotate the beacon by 90 degrees in the colliders local space if true. Do nothing otherwise",
        get=lambda self : CLU.getBoolFromKey(_Append("_beacon_should_rotate_ninety")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_beacon_should_rotate_ninety"), value),
    )

    onSleepAction : EnumProperty(
        items=TurnOnOffAction.TurnOnOffAction,
        description="Defines what this highlighter should do when it gets put to 'sleep': Nothing, Turn On, Turn Off. Turn Off is the default",
        get=lambda self : CLU.getIntFromKey(_Append("_on_sleep_action"), 2),
        set=lambda self, value : CLU.setValueAtKey(_Append("_on_sleep_action"), value)
    )

    downtimeSeconds : FloatProperty(
        description="",
        get=lambda self : CLU.getFloatFromKey(_Append("_downtime_seconds"), 0),
        set=lambda self, value : CLU.setValueAtKey(_Append("_downtime_seconds"), value)
    )

    # TODO: decide if this is the same thing as enableRadius
    visibleRadius : FloatProperty(
        description="When the camera is further than this radius from the beacon, the beacon will be hidden. \
                        If zero or less, the beacon will never be hidden",
        get=lambda self : CLU.getFloatFromKey(_Append("_visible_radius"), -1.0),
        set=lambda self, value : CLU.setValueAtKey(_Append("_visible_radius"), value)
    )

    isInvisibleToProximity : BoolProperty (
        description="Highlighters are automatically found and toggled visible/active/off by the proximity detection \
                        system--but not if this is set to true. If true, the detection system will ignore this highlighter. \
                            Use when you want to interact with the highlighters in some other way. \
                                For example, use this on highlighters that should only activate during a cam lock session.",
        get=lambda self : CLU.getBoolFromKey(_Append("_is_invisible_to_proximity"), False),
        set=lambda self, value : CLU.setValueAtKey(_Append("_is_invisible_to_proximity"), value)
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

def defer():
    resubAllLoadPostInterHighlighter(dummy=None)
    setupLoadPost()

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Object.highlighterPerObjectData
    del bpy.types.Scene.interactionHighlighterLike

