import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,
                       PointerProperty,
                       FloatVectorProperty,
                       IntVectorProperty,
                       BoolVectorProperty,
                       EnumProperty)
from bpy.types import (PropertyGroup,)
from mcd.util import ObjectLookupHelper

# TODO: red button: export with no dialogue

from mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
from mcd.ui.componentlike import AbstractDefaultSetter
from mcd.ui.componentlike.util import ComponentLikeUtils as CLU
from mcd.ui.componentlike.util import UnderscoreUtils   

_baseKey="mel_off_mesh_link"

_suffixes = {
    "_setup_type" : 0,
    "_cost_override" : -1,
    "_bidirectional" : True,
    "_activated" : True,
    "_auto_update_positions" : False,
    "_navigation_area" : "Walkable",
    }

def _getSuffixKey(suffix : str) -> str:
    result = F"{_baseKey}{suffix}"
    return result

_camelKeys = []
_exclude = ("_setup_type")

def _getCamelKeys():
    global _camelKeys
    if not _camelKeys or len(_camelKeys) == 0:
        _camelKeys = [UnderscoreUtils.underscoreToCamel(k) for k in _suffixes.keys() if k not in _exclude]
    return _camelKeys

class OffMeshLinkDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return OffMeshLinkLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        for suffix in _suffixes.keys():
            if not AbstractDefaultSetter._IsEqual(_getSuffixKey(suffix), a, b):
                return False
        return True

    @staticmethod
    def OnAddKey(key : str, val, targets):
        for suffix, defaultVal in _suffixes.items():
            print(F"{suffix} set {defaultVal} ")
            AbstractDefaultSetter._SetKeyValOnTargets(_getSuffixKey(suffix), defaultVal, targets)

    @staticmethod
    def OnRemoveKey(key : str, targets):
        for suffix in _suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_getSuffixKey(suffix), targets=targets)


class OffMeshLinkLike(PropertyGroup, AbstractComponentLike):

    @staticmethod
    def AcceptsKey(key : str):
        return key == OffMeshLinkLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        oml = context.scene.offMeshLinkLike
        row = box.row()
        row.prop(oml, "setupType", text="setup type")
        if oml.setupType != '0':
            row = box.row()
            row.prop(oml, "start", text="start")
            row.prop(oml, "end", text="end")

        for camelKey in _getCamelKeys():
            row = box.row()
            row.prop(oml, camelKey, text = camelKey)

    @staticmethod
    def GetTargetKey() -> str:
        return _baseKey 

    setupType : EnumProperty(
        items=(
            ('0', 'LongAxis', 'Create start and end transforms at each end of this mesh\'s longest extents (measured in local space)'),
            ('1', 'Manual', 'Manually specify the names of the start and end transforms')),
        default='0',
        get=lambda self : CLU.getIntFromKey(_getSuffixKey("_setup_type")),
        set=lambda self, value : CLU.setValueAtKey(_getSuffixKey("_setup_type"), value)
    )
    start : StringProperty(
        description="the name of the start transform",
        get=lambda self : CLU.getStringFromKey(_getSuffixKey("_start")),
        set=lambda  self, value : CLU.setValueAtKey(_getSuffixKey("_start"), value)
    )
    end : StringProperty(
        description="the name of the end transform",
        get=lambda self : CLU.getStringFromKey(_getSuffixKey("_end")),
        set=lambda  self, value : CLU.setValueAtKey(_getSuffixKey("_end"), value)
    )
    costOverride : IntProperty(
        default=-1,
        get=lambda self : CLU.getIntFromKey(_getSuffixKey("_cost_override"), -1),
        set=lambda self, value : CLU.setValueAtKey(_getSuffixKey("_cost_override"), value)
    )
    bidirectional : BoolProperty(
        default=True,
        get=lambda self : CLU.getBoolFromKey(_getSuffixKey("_bidirectional")),
        set=lambda self, value : CLU.setValueAtKey(_getSuffixKey("_bidirectional"), value)
    )
    activated : BoolProperty(
        default=True,
        get=lambda self : CLU.getBoolFromKey(_getSuffixKey("_activated")),
        set=lambda self, value : CLU.setValueAtKey(_getSuffixKey("_activated"), value)
    )
    autoUpdatePositions : BoolProperty(
        default=True,
        get=lambda self : CLU.getBoolFromKey(_getSuffixKey("_auto_update_positions"), True),
        set=lambda self, value : CLU.setValueAtKey(_getSuffixKey("_auto_update_positions"), value)
    )
    navigationArea : StringProperty(
        get=lambda self : CLU.getStringFromKey(_getSuffixKey("_navigation_area"), "Walkable"),
        set=lambda self, value : CLU.setValueAtKey(_getSuffixKey("_navigation_area"), value)
    )


classes = (
    OffMeshLinkLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.offMeshLinkLike = bpy.props.PointerProperty(type=OffMeshLinkLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.offMeshLinkLike