import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)


from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU

suffixes = {
    "_should_call_click_handlers" : False,
    "_cancel_button_0" : "Cancel",
    "_cancel_button_1" : "AltCancel",
}

class RE2PickSessionDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return RE2PickSessionLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append(), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        for suff, default_val in suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(_Append(suff), default_val, targets)

    @staticmethod
    def OnRemoveKey(key : str, targets):
        for suff in suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suff), targets)

def _Append(suffix : str = "") -> str:
    return F"{RE2PickSessionLike.GetTargetKey()}{suffix}"


class RE2PickSessionLike(PropertyGroup, AbstractComponentLike): 
    
    @classmethod
    def _append(cls, suffix: str = "") -> str:
        return F"{RE2PickSessionLike.GetTargetKey()}{suffix}"

    @staticmethod
    def GetTargetKey() -> str:
        return "mel_re2_pick_session"
    
    @staticmethod
    def AcceptsKey(key : str):
        return key == RE2PickSessionLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        mcl : RE2PickSessionLike = context.scene.rE2PickSessionLike
        boxb=box.box()
        # boxb.row().prop(mcl, "mode", text="Mode")
        # if mcl.mode == 'MouseInput' or mcl.mode=='MouseAndKeyboardInput':
        boxb.row().prop(mcl, "shouldCallClickHandlers")
        boxb.row().prop(mcl, "tryInventory")

        box.row().prop(mcl, "cancelButton0")
        box.row().prop(mcl, "cancelButton1")
        pass

    # mode : EnumProperty(
    #     items=(
    #         ('MouseInput', 'Mouse Input', 'MouseInput'),
    #         ('KeyboardInput', 'Keyboard Input', 'KeyboardInput'),
    #         ('MouseAndKeyboardInput', 'Mouse and Keyboard Input', 'MouseAndKeyboardInput')
    #     ),
    #     description="Defines whether the session should track mouse clicks, key presses or both",
    #     get=lambda self : CLU.getIntFromKey(_Append("_mode")),
    #     set=lambda self , value : CLU.setValueAtKey(_Append("_mode"), value)
    # )

    shouldCallClickHandlers : BoolProperty(
        description="If true, invoke the interaction handler on any collider that gets clicked during the session, \
if a click type interaction handler is found. If false, don't do this. Note: even when this option is false,\
the pick session will still emit an event, 'OnItemPick', when the user clicks a collider during the session. Use that event to handle \
the picking behaviour yourself, as needed.",
        get=lambda self : CLU.getBoolFromKey(_Append("_should_call_click_handlers"), False),
        set=lambda self, value : CLU.setValueAtKey(_Append("_should_call_click_handlers"), value)
    )

    tryInventory : BoolProperty(
        description="If true, any hit colliders will be passed to the inventory. If not, this won't happen",
        get=lambda self : CLU.getBoolFromKey(_Append("_try_inventory"), False),
        set=lambda self, value : CLU.setValueAtKey(_Append("_try_inventory"), value)
    )

    cancelButton0 : StringProperty(
        description="The name of a button that should exit the session. Must be defined in Unity Project Settings > Input Manager",
        get=lambda self : CLU.getStringFromKey(_Append("_cancel_button_0"), "Cancel"),
        set=lambda self, value : CLU.setValueAtKey(_Append("_cancel_button_0"), value)
    )
    cancelButton1 : StringProperty(
        description="The name of a button that should exit the session. Must be defined in Unity Project Settings > Input Manager",
        get=lambda self : CLU.getStringFromKey(_Append("_cancel_button_1"), "AltCancel"),
        set=lambda self, value : CLU.setValueAtKey(_Append("_cancel_button_1"), value)
    )
  

classes = (
    RE2PickSessionLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.rE2PickSessionLike = bpy.props.PointerProperty(type=RE2PickSessionLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.rE2PickSessionLike

