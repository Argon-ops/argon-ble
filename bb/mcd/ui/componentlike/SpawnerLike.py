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

suffixes = {
    "_prefab_name" : "",
    "_spawn_mode" : 0,
    "_spawn_interval" : 5.0,
}

class SpawnerDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return SpawnerLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append(), a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        for suffix, defaultVal in suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(_Append(suffix), defaultVal, targets)

    @staticmethod
    def OnRemoveKey(key : str, targets):
        for suffix in suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets=targets)

def _Append(suffix : str = "") -> str:
    return F"{SpawnerLike.GetTargetKey()}{suffix}"

from bb.mcd.ui.componentlike.enablefilter.EnableFilterSettings import EnableFilterSettings

class SpawnerLike(EnableFilterSettings, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_spawner"

    @staticmethod
    def AcceptsKey(key : str):
        return key == SpawnerLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        mcl = context.scene.spawnerLike
        box.row().prop(mcl, "prefabName", text="Prefab Name")
        box.row().prop(mcl, "spawnMode", text="Spawn Mode")
        if mcl.spawnMode == 'Periodic':
            box.row().prop(mcl, "spawnInterval", text="Spawn Interval (Seconds)")

    prefabName : StringProperty(
        description="The name of the prefab to spawn",
        get=lambda self : CLU.getStringFromKey(self.Append("_prefab_name")),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_prefab_name"), value)
    )

    spawnMode : EnumProperty(
        items=(
            ('Once', 'Once', 'Once'),
            ('Periodic', 'Periodic', 'Periodic')
        ),
        get=lambda self : CLU.getIntFromKey(self.Append("_spawn_mode"), 0),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_spawn_mode"), value)
    )

    spawnInterval : FloatProperty(
        description="The spawn interval for continuous mode in seconds",
        get=lambda self : CLU.getFloatFromKey(self.Append("_spawn_interval"), 5.0),
        set=lambda self, value : CLU.setValueAtKey(self.Append("_spawn_interval"), value)
    )


classes = (
    SpawnerLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.spawnerLike = bpy.props.PointerProperty(type=SpawnerLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.spawnerLike

