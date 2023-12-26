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

# _owners = dict() # track objects that own SwapObjectLikes 
# def _addSwapOwners(targets):
#     for target in targets:
#         _owners[target.name] = target

# def _removeSwapOwners(targets):
#     for target in targets:
#         del _owners[target.name]

# TODO: add remove on addkey removekey
class ObjectEnableDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return ObjectEnableLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return True # um....
        # return AbstractDefaultSetter._IsEqual(_Append("_invert"), a, b) and \
        #         AbstractDefaultSetter._IsEqual(_Append("_recursive"), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        # _addSwapOwners(targets)
        pass

    @staticmethod
    def OnRemoveKey(key : str, targets):
        pass
        # suffixes = ("_invert", "_recursive") # "_on_object", "_off_object")
        # for suffix in suffixes:
        #     AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)
        # # _removeSwapOwners(targets)

def _Append(suffix : str) -> str:
    return F"{ObjectEnableLike.GetTargetKey()}{suffix}"

from bb.mcd.ui.componentlike.enablefilter.EnableFilterSettings import EnableFilterSettings

class ObjectEnableLike(EnableFilterSettings, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_object_enable"

    @staticmethod
    def AcceptsKey(key : str):
        return key == ObjectEnableLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        pass
        # mcl = context.scene.objectEnableLike
        # box.row().prop(mcl, "invert", text="Invert")
        # box.row().prop(mcl, "recursive", text="Recursive")

    # invert : BoolProperty(
    #     description="If true, set disabled with a positive signal and enabled with a negative signal. Otherwise, enable positive, disable negative.",
    #     get=lambda self: CLU.getBoolFromKey(_Append("_invert"), False),
    #     set=lambda self, value: CLU.setValueAtKey(_Append("_invert"), value)
    # )
    # recursive : BoolProperty(
    #     description="If true, recursively apply to children.",
    #     get=lambda self: CLU.getBoolFromKey(_Append("_recursive"), False),
    #     set=lambda self, value: CLU.setValueAtKey(_Append("_recursive"), value)
    # )

classes = (
    ObjectEnableLike,
    )


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Object.fakeInt = bpy.props.IntProperty()
    bpy.types.Scene.objectEnableLike = bpy.props.PointerProperty(type=ObjectEnableLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.objectEnableLike
    del bpy.types.Object.fakeInt

