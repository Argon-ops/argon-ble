import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)
from bb.mcd.ui.componentlike import AbstractDefaultSetter

from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU

_suffixes = {
    "_clamp01" : True,
    "_invert" : False,
    "_threshold" : .5
}

class EnableFilterDefaultSetter(object):
    @staticmethod 
    def OnAddKey(enableClass, key, targets):
        for suffix, val in _suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(enableClass.Append(suffix), val, targets)

    @staticmethod
    def OnRemoveKey(enableClass, targets):
        for suffix in _suffixes.keys():
            AbstractDefaultSetter._RemoveKey(enableClass.Append(suffix), targets)


class EnableFilterSettings(PropertyGroup):

    IS_ENABLEABLE_CLASS = True
   
    clamp01 : BoolProperty(
        description="If true, clamp the signal between 0 and 1. Don't clamp otherwise",
        # NOTE: using self.Append. We require (hope) that the sub-class mix-in inherits from AbstractComponentLike
        get=lambda self : CLU.getBoolFromKey(self.Append("_clamp01"), True), 
        set=lambda self, value : CLU.setValueAtKey(self.Append("_clamp01"), value)
    )

    invert : BoolProperty(
        description="If true, set the signal to 1 minus signal before comparing with the threshold value. Otherwise, don't change the signal's value",
        get=lambda self : CLU.getBoolFromKey(self.Append("_invert"), False),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_invert"), value)
    )

    threshold : FloatProperty(
        description="Defines the value to compare against when evaluating the signal: enable if threshold < signal",
        get=lambda self : CLU.getFloatFromKey(self.Append("_threshold"), .5),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_threshold"), value),
        soft_min=0.0,
        soft_max=1.0,
    )

    isSelfToggling : BoolProperty(
        description="If true, toggle on/off each time this component receives a signal; the value of the signal itself will be ignored",
        get=lambda self : CLU.getBoolFromKey(self.Append("_is_self_toggling"), False),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_is_self_toggling"), value)
    )

    setInitialState : EnumProperty(
        items=(
            ('DONT', 'Don\'t set initial state', 'Do nothing at start up'),
            ('ONE', 'On', 'Send a one signal at start up'),
            ('ZERO', 'Off', 'Send a zero signal at start up')
        ),
        description="Defines what state this component should set itself to at start up",
        get=lambda self : CLU.getIntFromKey(self.Append("_set_initial_state"), 0),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_set_initial_state"), value)
    )

    @classmethod
    def displayEnableSettings(cls, box):
        # with GetSceneInstance. this can be a static 
        #   then the classes don't even need to call it from their Display methods
        #    can be called by Inspector.py

        # Mild evil: GetSceneInstance() is an AbstractComponentLike classmethod
        #  We are assuming that this class also descends from AbstactComponentLike
        #  why do we need this: so that child classes can be spared calling this method from their Display methods manually
        self = cls.GetSceneInstance() 

        box = box.box()
        row = box.row()
        row.prop(bpy.context.scene, "showEnableSettings", 
            icon="TRIA_DOWN" if bpy.context.scene.showEnableSettings else "TRIA_UP",
            icon_only=True, emboss=False)
        row.label(text="Enable Filter")
        if not bpy.context.scene.showEnableSettings:
            return
        box.row().prop(self, "isSelfToggling", text="Self Toggle")
        if not self.isSelfToggling:
            boxb = box.box()
            boxb.row().prop(self, "clamp01", text="Clamp01")
            boxb.row().prop(self, "invert", text="Invert")
            boxb.row().prop(self, "threshold", text="Threshold")

        box.row().prop(self, "setInitialState", text="Set Initial State")


classes = (
    EnableFilterSettings,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Scene.showEnableSettings = BoolProperty()

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)
    
    del bpy.types.Scene.showEnableSettings

