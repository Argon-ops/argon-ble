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
from bb.mcd.ui.componentlike import AbstractDefaultSetter
from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU

suffixes = {
    "_component_names" : "",
}


class DisableComponentDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return DisableComponentLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        for key in suffixes.keys():
            if not AbstractDefaultSetter._IsEqual(_Append(key), a, b):
                return False
        return True

    @staticmethod
    def OnAddKey(key : str, val, targets):
        pass

    @staticmethod
    def OnRemoveKey(key : str, targets):
        for suffix in suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)

def _Append(suffix : str) -> str:
    return F"{DisableComponentLike.GetTargetKey()}{suffix}"

class DisableComponentLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_disable_component"

    @staticmethod
    def AcceptsKey(key : str):
        return key == DisableComponentLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        mcl = context.scene.disableComponentLike
        row = box.row()
        row.prop(mcl, "componentNames", text="Component Name")

    # TODO: actually want a collection of strings.
    componentNames : StringProperty(
        description="Comma-separated names of the component(s) to disable",
        get=lambda self: CLU.getStringFromKey(_Append("_component_names")),
        set=lambda self, value: CLU.setValueAtKey(_Append("_component_names"), value)
    )

classes = (
    DisableComponentLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Scene.disableComponentLike = bpy.props.PointerProperty(type=DisableComponentLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.disableComponentLike

