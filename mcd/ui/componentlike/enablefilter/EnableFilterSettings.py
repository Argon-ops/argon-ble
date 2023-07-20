import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)
from mcd.ui.componentlike import AbstractDefaultSetter

from mcd.ui.componentlike.util import ComponentLikeUtils as CLU

_suffixes = {
    "_clamp01" : True,
    "_invert" : False,
    "_threshold" : .5
}

# a default setter equivalent for EFSs
class EnableFilterDefaultSetter(object):
    @staticmethod 
    def OnAddKey(enableClass, key, targets):
        for suffix, val in _suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(enableClass.Append(suffix), val, targets)

    @staticmethod
    def OnRemoveKey(enableClass, targets):
        print(F"on rm keys EFDS")
        for suffix in _suffixes.keys():
            print(F" will rm key: {enableClass.Append(suffix)}")
            AbstractDefaultSetter._RemoveKey(enableClass.Append(suffix), targets)


class EnableFilterSettings(PropertyGroup): # or is it an operator

    IS_ENABLEABLE_CLASS = True
    
    # filterType : EnumProperty(
    #     items=(
    #         ('No filter', 'No filter', 'Do not mess with'), # DECIDE: or should we filter the signal (float 01) value at this point?? and then scalars could use the same filters??? no destroying info?
    #     )
    # )

    clamp01 : BoolProperty(
        description="If true, clamp the signal between 0 and 1. Don't clamp otherwise",
        # NOTE: using self.Append. We require (fervently hope) that the sub-class mix-in inherits from AbstractComponentLike
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

    # TODO: initial state strat??

    @classmethod
    def displayEnableSettings(cls, box):
        # with GetSceneInstance. this can be a static 
        #   then the classes don't even need to call it from their Display methods
        #   can be called by Inspector.py

        # Possibly evil: this relies on the child class being an instance of AbstractComponentLike 
        #    (i.e. AbstractComponentLike is it's other parent)
        #  why are we dabbling in evil: so that child classes can be spared calling this method from their Display methods manually
        self = cls.GetSceneInstance() 

        box = box.box()
        row = box.row()
        row.prop(bpy.context.scene, "showEnableSettings", 
            icon="TRIA_DOWN" if bpy.context.scene.showEnableSettings else "TRIA_UP",
            icon_only=True, emboss=False )
        row.label(text="Enable Filter")
        if not bpy.context.scene.showEnableSettings:
            return
        box.row().prop(self, "clamp01", text="Clamp01")
        box.row().prop(self, "invert", text="Invert")
        box.row().prop(self, "threshold", text="Threshold")
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

