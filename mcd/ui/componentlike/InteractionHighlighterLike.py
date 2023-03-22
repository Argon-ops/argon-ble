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

from mcd.ui.actionstarterlist import ActionStarterList
from mcd.ui.componentlike import AbstractDefaultSetter
from mcd.ui.componentlike.util import ComponentLikeUtils as CLU

import json


class InteractionHighlighterDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return InteractionHighlighterLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append("_highlight_mat"), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        default = AbstractDefaultSetter._GetDefaultFromPrefs(key)
        try:
            AbstractDefaultSetter._SetKeyValOnTargets(_Append("_highlight_mat"), "Highlighter", targets)
            
        except BaseException as e:
            print(F" failed to set default {str(e)}")
            print(F"default keys: {default.keys()}")

    @staticmethod
    def OnRemoveKey(key : str, targets):
        suffixes = ("_highlight_mat", )
        for suffix in suffixes:
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)

def _Append(suffix : str) -> str:
    return F"{InteractionHighlighterLike.GetTargetKey()}{suffix}"


class InteractionHighlighterLike(PropertyGroup, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_interaction_highlighter"

    @staticmethod
    def AcceptsKey(key : str):
        return key == InteractionHighlighterLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        mcl = context.scene.interactionHighlighterLike
        row = box.row()
        row.prop(mcl, "highlightMat", text="Highlight Material")

    highlightMat : StringProperty(
        name="Highlight Material",
        get=lambda self : CLU.getStringFromKey(_Append("_highlight_mat")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_highlight_mat"), value),
    )
  

classes = (
    InteractionHighlighterLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.interactionHighlighterLike = bpy.props.PointerProperty(type=InteractionHighlighterLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.interactionHighlighterLike

