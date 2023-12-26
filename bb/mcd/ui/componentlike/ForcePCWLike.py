import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)
from bb.mcd.util import ObjectLookupHelper

from bb.mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike

from bb.mcd.ui.actionstarterlist import ActionStarterList
from bb.mcd.ui.componentlike import AbstractDefaultSetter
from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU

suffixes = {
    "_any_matching_action" : True,
}

class ForcePCWDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return ForcePCWLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append(), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        for suffix, defaultVal in suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(_Append(suffix), defaultVal, targets)

    @staticmethod
    def OnRemoveKey(key : str, targets):
        for suffix in suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets=targets)

def _Append(suffix : str = "") -> str:
    return F"{ForcePCWLike.GetTargetKey()}{suffix}"


class ForcePCWLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_force_pcw"

    @staticmethod
    def AcceptsKey(key : str):
        return key == ForcePCWLike.GetTargetKey()

    @staticmethod #ccccccccccccccccccccccccccc
    def Display(box, context) -> None:
        mcl = context.scene.forcePCWLike
        box.row().prop(mcl, "anyMatchingAction", text="Any Matching Action")
        if not mcl.anyMatchingAction:
            box.row().prop(mcl, "actionName", text="Action Name")
        box.row().prop(mcl, "convenienceLink", text="Convenience Link")

    anyMatchingAction : BoolProperty(
        description="Add PlayableClipWrappers for any animation clip whose name includes this object",
        get=lambda self : CLU.getBoolFromKey(self.Append("_any_matching_action")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_any_matching_action"), value)
    )

    actionName : StringProperty(
        description="",
        get=lambda self : CLU.getStringFromKey(self.Append("_action_name")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_action_name"), value)
    )

    convenienceLink : BoolProperty(
        description="Add a component on this object that exposes links to the PCW so that they are easier to find in the hierarchy",
        get=lambda self : CLU.getBoolFromKey(self.Append("_convenience_link")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_convenience_link"), value)
    )


classes = (
    ForcePCWLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.forcePCWLike = bpy.props.PointerProperty(type=ForcePCWLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.forcePCWLike