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
from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU

class EnableReceiverDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return EnableReceiverLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append("_apply_to_children"), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        default = AbstractDefaultSetter._GetDefaultFromPrefs(key)
        try:
            AbstractDefaultSetter._SetKeyValOnTargets(_Append("_apply_to_children"), True, targets)
            
        except BaseException as e:
            print(F" failed to set default {str(e)}")
            print(F"default keys: {default.keys()}")

    @staticmethod
    def OnRemoveKey(key : str, targets):
        suffixes = ("_apply_to_children", "_set_initial_state")
        for suffix in suffixes:
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)

def _Append(suffix : str) -> str:
    return F"{EnableReceiverLike.GetTargetKey()}{suffix}"


class EnableReceiverLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_enable_receiver"

    @staticmethod
    def AcceptsKey(key : str):
        return key == EnableReceiverLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        mcl = context.scene.enableReceiverLike
        row = box.row()
        row.prop(mcl, "applyToChildren", text="Apply to children")
        row = box.row()
        row.prop(mcl, "setInitialState", text="Set Initial State")

    applyToChildren : BoolProperty(
        get=lambda self : CLU.getBoolFromKey(_Append("_apply_to_children")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_apply_to_children"), value),
    )

    setInitialState : EnumProperty(
        items=(
            ('DONT', 'Don\'t set initial state', 'Do nothing at start up'),
            ('TRUE', 'Enabled', 'Set enabled at start up'),
            ('FALSE', 'Disabled', 'Set disabled at start up')
        ),
        get=lambda self : CLU.getIntFromKey(_Append("_set_initial_state")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_set_initial_state"), value)
    )

classes = (
    EnableReceiverLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.enableReceiverLike = bpy.props.PointerProperty(type=EnableReceiverLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.enableReceiverLike

