from bb.mcd.core.componentlike.enablefilter.EnableFilterSettings import EnableFilterSettings
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

from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike

from bb.mcd.core.command import CommandsList
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU

suffixes = {
    "_type_name": "",
    "_namespace": "",
    "_apply_to_self": False,
    "_search_children": True,
}


class SpawnerDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key: str):
        return SpawnerLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a: object, b: object) -> bool:
        return AbstractDefaultSetter._IsEqual(_Append(), a, b)

    @staticmethod
    def OnAddKey(key: str, val, targets):
        for suffix, defaultVal in suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(
                _Append(suffix), defaultVal, targets)

    @staticmethod
    def OnRemoveKey(key: str, targets):
        for suffix in suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets=targets)


def _Append(suffix: str = "") -> str:
    return F"{SpawnerLike.GetTargetKey()}{suffix}"


class SpawnerLike(EnableFilterSettings, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_enable_component"

    @staticmethod
    def AcceptsKey(key: str):
        return key == SpawnerLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        mcl = context.scene.spawnerLike
        box.row().prop(mcl, "prefabName", text="Prefab Name")
        box.row().prop(mcl, "spawnMode", text="Spawn Mode")
        if mcl.spawnMode == 'Periodic':
            box.row().prop(mcl, "spawnInterval", text="Spawn Interval (Seconds)")

    typeName: StringProperty(
        description="Defines the name of the type. (Example: 'Collider')",
        get=lambda self: CLU.getStringFromKey(self.Append("_prefab_name")),
        set=lambda self, value: CLU.setValueAtKey(
            self.Append("_prefab_name"), value)
    )

    namespace: StringProperty(
        description="Optional: defines the namespace that contains the type. Will search all namespaces if this property is empty",
        get=lambda self: CLU.getStringFromKey(self.Append("_namespace")),
        set=lambda self, value: CLU.setValueAtKey(self.Append("_namespace"))
    )

    applyToSelf: BoolProperty(
        description=""
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
