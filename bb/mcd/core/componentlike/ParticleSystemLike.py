import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)

from bb.mcd.core.componentlike.enablefilter.EnableFilterSettings import EnableFilterSettings
from bb.mcd.util import ObjectLookupHelper

from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike

from bb.mcd.core.command import CommandsList
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU

class ParticleSystemDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return ParticleSystemLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append(), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        default = AbstractDefaultSetter._GetDefaultFromPrefs(key)
        try:
            AbstractDefaultSetter._SetKeyValOnTargets(_Append(), default['default_name'], targets)
        except BaseException as e:
            print(F" failed to set default {str(e)}")
            print(F"default keys: {default.keys()}")

    @staticmethod
    def OnRemoveKey(key : str, targets):
        AbstractDefaultSetter._RemoveKey(_Append(), targets)

def _Append(suffix : str = "") -> str:
    return F"{ParticleSystemLike.GetTargetKey()}{suffix}"


class ParticleSystemLike(EnableFilterSettings, AbstractComponentLike): 
    
    @classmethod
    def _append(cls, suffix: str = "") -> str:
        return F"{ParticleSystemLike.GetTargetKey()}{suffix}"

    @staticmethod
    def GetTargetKey() -> str:
        return "mel_particle_system"
    
    @staticmethod
    def AcceptsKey(key : str):
        return key == ParticleSystemLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        mcl : ParticleSystemLike = context.scene.particleSystemLike
        box.row().prop(mcl, "name", text="Prefab Name")
        box.row().prop(mcl, "toggleGameObject", text="Toggle Game Object")

    # command info modifier(s)
    name : StringProperty(
        description="the name of a particle system prefab in the target Unity project",
        get=lambda self : CLU.getStringFromKey(_Append("")),
        set=lambda self, value : CLU.setValueAtKey(_Append(""), value)
    )

    initialState : BoolProperty(
        description="should the particle system be active at the start of play",
        get=lambda self : CLU.getBoolFromKey(_Append("_initial_state")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_initial_state"), value)
    )

    toggleGameObject : BoolProperty(
        description="should the particle system's gameobject become active/inactive when the particle system starts and stops",
        get=lambda self : CLU.getBoolFromKey(_Append("_toggle_game_object")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_toggle_game_object"), value)
    )
    

classes = (
    ParticleSystemLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.particleSystemLike = bpy.props.PointerProperty(type=ParticleSystemLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.particleSystemLike

