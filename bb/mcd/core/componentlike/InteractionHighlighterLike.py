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
from bb.mcd.core.componentlike.AbstractPerObjectData import AbstractPerObjectData
from bb.mcd.core.componentlike.enablefilter.SleepStateSettings import SleepStateSettings
from bb.mcd.util import ObjectLookupHelper

from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.core.componentlike.util import ObjectPointerMsgbusUtils as MsgbusUtils

from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU
from bb.mcd.core.sharedtypes import TurnOnOffAction


from bpy.app.handlers import persistent

# region LoadPost boilerplate


@persistent
def resubAllLoadPostInterHighlighter(dummy):
    perObjectFieldName = "highlighterPerObjectData"

    fieldsAndPropNames = (
        # for each object PointerProperty that needs updates, add a line here
        ("rendererTarget", "_renderer_target"),
        ("forwardFaceReference", "_forward_face_reference"),
        ("beaconPositionReference", "_beacon_position_reference"),
    )

    for fieldAndPropName in fieldsAndPropNames:
        MsgbusUtils.resubscribeAll_LP(
            perObjectFieldName,
            fieldAndPropName[0],
            _Append(fieldAndPropName[1]))
        

def setupLoadPost():
    """add a load post handler so that we resubscribeAll upon loading a new file"""
    from bb.mcd.util import AppHandlerHelper
    AppHandlerHelper.RefreshLoadPostHandler(resubAllLoadPostInterHighlighter)

# endregion LoadPost boilerplate


class InteractionHighlighterDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):

    @staticmethod
    def IsMultiSelectAllowed() -> bool:
        return False

    @staticmethod
    def AcceptsKey(key: str):
        return InteractionHighlighterLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a: object, b: object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append("_highlight_mat"), a, b)

    @staticmethod
    def OnAddKey(key: str, val, targets):
        default = AbstractDefaultSetter._GetDefaultFromPrefs(key)
        try:
            AbstractDefaultSetter._SetKeyValOnTargets(
                _Append("_highlight_mat"), "Highlighter", targets)

        except BaseException as e:
            print(F" failed to set default {str(e)}")
            print(F"default keys: {default.keys()}")

    @staticmethod
    def OnRemoveKey(key: str, targets):
        suffixes = ("_highlight_mat", "_renderer_target")
        for suffix in suffixes:
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)

        for target in targets:
            target.property_unset("highlighterPerObjectData")

    @staticmethod
    def Validate(target):
        if not InteractionHighlighterLike.GetTargetKey() in target:
            print(
                F" i don't know why you wanted me to validate a target with no highlighter like: {target.name} no key: {InteractionHighlighterLike.GetTargetKey()}")
            return

        from bb.mcd.core.componentlike.util.ColliderLikeShared import ColliderLikeShared

        rt = target.highlighterPerObjectData.rendererTarget
        rt = target if rt is None else rt

        if not ColliderLikeShared.IsCollider(rt):
            from bb.mcd.lookup import KeyValDefault
            from bb.mcd.core.componentlike import StorageRouter
            from bb.mcd.core.componentlike import BoxColliderLike as bcl

            default = KeyValDefault.getDefaultValue(
                bcl.BoxColliderLike.GetTargetKey())
            StorageRouter.setDefaultValueOnTarget(
                bcl.BoxColliderLike.GetTargetKey(), default, target)


def _Append(suffix: str) -> str:
    return F"{InteractionHighlighterLike.GetTargetKey()}{suffix}"


class HighlighterPerObjectData(PropertyGroup, AbstractPerObjectData):
    """Defines fields for InteractionHighlighters that we need to define 'per object' (See the register function where this type is defined on Object not Scene).
    
        Per object data because highlighters might need to reference a renderer target and a few other scene objects"""

    rendererTarget: PointerProperty(
        type=bpy.types.Object,
        description="Optional: specify a highlight target other than this object. Useful, for example, if this object won't have a renderer. Defaults to this object.",
        update=lambda self, context: MsgbusUtils.onObjectUpdate(
            context.active_object, # COMPLAINT: context.active object happens to be the object we want (in all cases since active object is the one being edited by the user) but can we rely on it? suppose a case where rendererTarget is updated when we're not expecting it to be updated.
            self,
            "rendererTarget",
            _Append("_renderer_target")
        )
    )

    forwardFaceReference: PointerProperty(
        type=bpy.types.Object,
        description="Optional: specify an object that defines the forward normal for the highlighter. \
The forward face reference object's position relative to the highlighter will define a forward facing normal vector. If \
a forward normal is defined, the highlighter will only activate when the player is positioned in front of the highlighter.",
        update=lambda self, context: MsgbusUtils.onObjectUpdate(
            context.active_object,
            self,
            "forwardFaceReference",
            _Append("_forward_face_reference")
        )
    )

    beaconPositionReference: PointerProperty(
        type=bpy.types.Object,
        description="Optional: if using a beacon highlighter, defines an object whose position will be used to set the position of the beacon",
        update=lambda self, context: MsgbusUtils.onObjectUpdate(
            context.active_object,
            self,
            "beaconPositionReference",
            _Append("_beacon_position_reference")
        )
    )


class InteractionHighlighterLike(SleepStateSettings, AbstractComponentLike):

    @staticmethod
    def GetTargetKey() -> str:
        return "mel_interaction_highlighter"

    @staticmethod
    def AcceptsKey(key: str):
        return key == InteractionHighlighterLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        mcl = context.scene.interactionHighlighterLike

        boxb = box.box()
        boxb.row().prop(mcl, "mode", text="Mode")
        if mcl.mode == "HighlightMaterial":
            boxb.row().prop(mcl, "highlightMat", text="Highlight Material")

            # validate active_object to fend off an error. although not sure how we get here when active_object is None (guess: copy pasting an object that has this?)
            if context.active_object is not None:
                # per obje
                hlpo = context.active_object.highlighterPerObjectData
                box.row().prop(hlpo, "rendererTarget", text="Renderer Target (Optional)")

        elif mcl.mode == "ClickBeacon":
            boxb.row().prop(mcl, "clickBeaconPrefab", text="Click Beacon Prefab")
            boxb.row().prop(mcl, "beaconPlacementOption", text="Beacon Placement Option")
            boxb.row().prop(mcl, "beaconNudgeVector", text="Beacon Nudge")
            boxb.row().prop(mcl, "beaconShouldRotateNinety", text="Rotate Ninety")
            if context.active_object is not None:
                boxb.row().prop(context.active_object.highlighterPerObjectData,
                                "beaconPositionReference", text="Beacon Position Object")

        if context.active_object is not None:
            # per object: forward facing ref
            hlpo = context.active_object.highlighterPerObjectData
            box.row().prop(hlpo, "forwardFaceReference", text="Forward Face Object (Optional)")

        box.row().prop(mcl, "downtimeSeconds", text="Downtime Seconds")
        box.row().prop(mcl, "onSleepAction", text="On Sleep Action")
        box.row().prop(mcl, "isInvisibleToProximity", text="Is Invisible to Proximity")

    mode: EnumProperty(
        items=(
            ('HighlightMaterial', 'HighlightMaterial', 'HL desc'),
            ('ClickBeacon', 'ClickBeacon', 'CB desc'),
            ('Invisible', 'Invisible',
             'A highlighter does nothing. Dummy highlighters are needed in some situations')
        ),
        get=lambda self: CLU.getIntFromKey(_Append("_mode")),
        set=lambda self, value: CLU.setValueAtKey(_Append("_mode"), value),
    )

    highlightMat: StringProperty(
        name="Highlight Material",
        get=lambda self: CLU.getStringFromKey(_Append("_highlight_mat")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_highlight_mat"), value),
    )

    clickBeaconPrefab: StringProperty(
        description="Defines the name of the prefab that should be used as a click beacon. For example 'my-sprite'. Path not needed. '.prefab' not needed ",
        get=lambda self: CLU.getStringFromKey(_Append("_click_beacon_prefab")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_click_beacon_prefab"), value),
    )

    beaconPlacementOption: EnumProperty(
        items=(
            ('ObjectPosition', 'Object Position',
             'Position the beacon right on top of this object'),
            ('ColliderBoundsCenter', 'Collider Bounds Center',
             'Position the beacon at the center of the collider attached to this object. (Assumes that there is one.)')
        ),
        get=lambda self: CLU.getIntFromKey(
            _Append("_beacon_placement_option")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_beacon_placement_option"), value),
    )

    beaconNudgeVector: FloatVectorProperty(
        description="Defines how far to move the beacon away from its anchor position. Scales with renderer or collider bounds where possible",
        get=lambda self: CLU.getFloatArrayFromKey(
            _Append("_beacon_nudge_vector")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_beacon_nudge_vector"), value),
        soft_min=-3.0,
        soft_max=3.0,
    )

    beaconShouldRotateNinety: BoolProperty(
        description="Rotate the beacon by 90 degrees in the colliders local space if true. Do nothing otherwise",
        get=lambda self: CLU.getBoolFromKey(
            _Append("_beacon_should_rotate_ninety")),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_beacon_should_rotate_ninety"), value),
    )

    onSleepAction: EnumProperty(
        items=TurnOnOffAction.TurnOnOffAction,
        description="Defines what this highlighter should do when it gets put to 'sleep': Nothing, Turn On, Turn Off. Turn Off is the default",
        get=lambda self: CLU.getIntFromKey(_Append("_on_sleep_action"), 2),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_on_sleep_action"), value)
    )

    downtimeSeconds: FloatProperty(
        description="",
        get=lambda self: CLU.getFloatFromKey(_Append("_downtime_seconds"), 0),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_downtime_seconds"), value)
    )

    visibleRadius: FloatProperty(
        description="When the camera is further than this radius from the beacon, the beacon will be hidden. \
                        If zero or less, the beacon will never be hidden",
        get=lambda self: CLU.getFloatFromKey(_Append("_visible_radius"), -1.0),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_visible_radius"), value)
    )

    isInvisibleToProximity: BoolProperty(
        description="Highlighters are automatically found and toggled visible/active/off by Argon's proximity detection \
system--but not if this is set to true. If true, the detection system will ignore this highlighter. \
Use when you want to interact with the highlighters in some other way. \
For example, use this on highlighters that should only activate during a cam lock session.",
        get=lambda self: CLU.getBoolFromKey(
            _Append("_is_invisible_to_proximity"), False),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_is_invisible_to_proximity"), value)
    )


classes = (
    InteractionHighlighterLike,
    HighlighterPerObjectData,
)


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Object.highlighterPerObjectData = bpy.props.PointerProperty(
        type=HighlighterPerObjectData)
    bpy.types.Scene.interactionHighlighterLike = bpy.props.PointerProperty(
        type=InteractionHighlighterLike)


def defer():
    resubAllLoadPostInterHighlighter(dummy=None)
    setupLoadPost()


def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Object.highlighterPerObjectData
    del bpy.types.Scene.interactionHighlighterLike
