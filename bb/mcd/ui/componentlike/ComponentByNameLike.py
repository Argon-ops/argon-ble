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

suffixes = (
    "_type_name",
    "_namespace"
)

class ComponentByNameDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return ComponentByNameLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append(), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        pass

    @staticmethod
    def OnRemoveKey(key : str, targets):
        for suffix in suffixes:
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets=targets)

def _Append(suffix : str = "") -> str:
    return F"{ComponentByNameLike.GetTargetKey()}{suffix}"

class ComponentByNameLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_component_by_name"

    @staticmethod
    def AcceptsKey(key : str):
        return key == ComponentByNameLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        mcl = context.scene.componentByNameLike
        box.row().prop(mcl, "typeName", text="Type Name")
        box.row().prop(mcl, "namespace", text="Namespace")

    typeName : StringProperty(
        description="The type name of the component. (For example 'AudioListener')",
        get=lambda self : CLU.getStringFromKey(_Append("_type_name")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_type_name"), value)
    )

    namespace : StringProperty(
        description="Optional namespace specification. Use if you have types with the same name in separate namespaces. (This text should match the name space in your C#. code: 'Some.Example.Namespace' )",
        get=lambda self : CLU.getStringFromKey(_Append("_namespace")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_namespace"), value)
    )

classes = (
    ComponentByNameLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.componentByNameLike = bpy.props.PointerProperty(type=ComponentByNameLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.componentByNameLike

