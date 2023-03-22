import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)

from mcd.util import ObjectLookupHelper
from mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
from mcd.ui.componentlike import AbstractDefaultSetter
from mcd.ui.componentlike.util import ComponentLikeUtils as CLU

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
        return AbstractDefaultSetter._IsEqual(_Append("_on_object"), a, b) and \
                AbstractDefaultSetter._IsEqual(_Append("_off_object"), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        # _addSwapOwners(targets)
        pass

    @staticmethod
    def OnRemoveKey(key : str, targets):
        suffixes = ("_on_object", "_off_object")
        for suffix in suffixes:
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)
        # _removeSwapOwners(targets)

def _Append(suffix : str) -> str:
    return F"{ObjectEnableLike.GetTargetKey()}{suffix}"

#     # TRICKY because we can set up an object rename msg bus. But even if we manage to do this per target object
#     #   we still then need to iterate over all of the objects in the scene to find the one(s) that is(are) holding 
#     #    references to this object...This is just due to the way we store these component-likes.
#     #  This is making us think that we just need to insist on the user publishing their fbx from this add on. 
#     #    I believe this issue is done and dusted and we already rely on that?? Or did msg bus bail us out last time...

# can this ObjectEnableLike object be kept in some separate collection. collection of things that
#  need to update when an object name changes...


# def _UpdateFromPointer(swapSelf):
#      CLU.setValueAtKey(_Append("_on_object"), swapSelf.onObject.name)

# def _SyncWithObject(obj):
#     onObjectName = CLU.getStringFromKey()

class ObjectEnableLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_object_enable"

    @staticmethod
    def AcceptsKey(key : str):
        return key == ObjectEnableLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        mcl = context.scene.objectEnableLike
        row = box.row()
        row.prop(mcl, "invert", text="Invert")

    invert : BoolProperty(
        description="If true, set disabled with a positive signal and enabled with a negative signal. Otherwise, enable positive, disable negative.",
        get=lambda self: CLU.getBoolFromKey(_Append("_invert"), False),
        set=lambda self, value: CLU.setValueAtKey(_Append("_invert"), value)
    )

classes = (
    ObjectEnableLike,
    )

# from bpy.app.handlers import persistent
# @persistent
# def messWithObRename(*args):
#     print (F"#### on ob rename")
#     # for owner in _owners.values():


# def setupActionMsgBusSubscription():
#     owner = object()
#     # https://docs.blender.org/api/current/bpy.msgbus.html
    
#     subscribe_to_ob = (bpy.types.Object, "name")
#     bpy.msgbus.subscribe_rna(
#         key=subscribe_to_ob,
#         owner=owner,
#         args=(),
#         notify=messWithObRename,)

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Object.fakeInt = bpy.props.IntProperty()
    bpy.types.Scene.objectEnableLike = bpy.props.PointerProperty(type=ObjectEnableLike)

    # setupActionMsgBusSubscription()

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.objectEnableLike
    del bpy.types.Object.fakeInt

