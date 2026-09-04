import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       BoolProperty,
                       FloatVectorProperty,)
from bpy.types import (PropertyGroup,)

from bb.mcd.util import ObjectLookupHelper

from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU
from bb.mcd.core.command import AddCommandPopup
from bb.mcd.core.command import CUSTOM_PG_AS_Collection

_baseKey = "mel_keycode_map"

# Must match KeycodeMapKeySet.MaxCodes on the Unity side. The code list is flattened into this many
#   indexed key groups because the custom property exporter only carries primitives -- there is no
#   nested/dictionary type to lean on. '_code_count' says how many of the slots are actually in use.
MaxCodes = 8

# Fields that make up one KeycodeResult. The 'incorrect' result reuses all of these except "_key",
#   since there is no code that matches "the code was wrong".
_resultFields = {
    "_flash_color": [1.0, 0.0, 0.0, 1.0],
    "_flash_seconds": 3.0,
    "_gestalt": "",
    "_command": "",
}


def _Append(suffix: str) -> str:
    return F"{_baseKey}{suffix}"


def _CodeSuffix(index: int, field: str) -> str:
    return F"_code_{index}{field}"


def _BuildSuffixDefaults():
    """Every key this component-like owns, mapped to the value it gets when the key is first added."""
    suffixes = {
        "_code_length": 4,
        "_code_count": 1,
    }
    for i in range(MaxCodes):
        suffixes[_CodeSuffix(i, "_key")] = ""
        for field, default in _resultFields.items():
            suffixes[_CodeSuffix(i, field)] = default
    for field, default in _resultFields.items():
        suffixes[F"_incorrect{field}"] = default
    return suffixes


_suffixes = _BuildSuffixDefaults()


class KeycodeMapDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key: str):
        return KeycodeMapLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a: object, b: object) -> bool:
        for suffix in _suffixes.keys():
            if not AbstractDefaultSetter._IsEqual(_Append(suffix), a, b):
                return False
        return True

    @staticmethod
    def OnAddKey(key: str, val, targets):
        for suffix, defaultVal in _suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(_Append(suffix), defaultVal, targets)

    @staticmethod
    def OnRemoveKey(key: str, targets):
        for suffix in _suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets=targets)

    @staticmethod
    def IsMultiSelectAllowed() -> bool:
        # Two objects sharing one set of codes is almost never what anyone means, and the per-code
        #   command pickers make a multi-select edit very hard to reason about.
        return False


# region add / remove code slots

def _RemoveUnusedCodeData(context):
    """Delete the keys for slots past the current count so stale codes don't get imported."""
    kml = context.scene.keycodeMapLike
    for i in range(kml.codeCount, MaxCodes):
        ObjectLookupHelper._removeKeyFromSelected(_Append(_CodeSuffix(i, "_key")), context)
        for field in _resultFields.keys():
            ObjectLookupHelper._removeKeyFromSelected(_Append(_CodeSuffix(i, field)), context)


def _RestoreCodeData(context, index: int):
    """Put the default keys back for a slot that was just (re)added."""
    targets = [context.active_object]
    AbstractDefaultSetter._SetKeyValOnTargets(_Append(_CodeSuffix(index, "_key")), "", targets)
    for field, default in _resultFields.items():
        AbstractDefaultSetter._SetKeyValOnTargets(_Append(_CodeSuffix(index, field)), default, targets)


class CU_OT_NumKeycodes(bpy.types.Operator):
    """Add or remove a code slot"""
    bl_idname = "view3d.num_keycodes"
    bl_label = "Add or delete code slots"
    bl_options = {'REGISTER', 'UNDO'}

    should_add: BoolProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        kml = context.scene.keycodeMapLike
        if self.should_add:
            if kml.codeCount >= MaxCodes:
                self.report({'WARNING'}, F"A keycode map holds at most {MaxCodes} codes")
                return {'CANCELLED'}
            newIndex = kml.codeCount
            kml.codeCount = newIndex + 1
            _RestoreCodeData(context, newIndex)
            return {'FINISHED'}

        if kml.codeCount <= 0:
            return {'CANCELLED'}
        kml.codeCount = kml.codeCount - 1
        _RemoveUnusedCodeData(context)
        return {'FINISHED'}

# endregion


class KeycodeMapLike(PropertyGroup, AbstractComponentLike):
    """The set of codes a keypad accepts, and what should happen for each one.

        Applied on the Unity side by KeycodeMapProcessor, which builds a KeycodeMap component.
        Note that the keypad controller itself is NOT created here -- this component-like only
        describes the codes. Wire the controller to its map in the Unity editor.
    """

    @staticmethod
    def GetTargetKey() -> str:
        return _baseKey

    @staticmethod
    def AcceptsKey(key: str):
        return key == _baseKey

    @staticmethod
    def _DrawCommandRow(row, kml, attrName):
        commandName = getattr(kml, attrName)
        row.prop(kml, attrName, text="Command")
        if commandName:
            row.operator(CUSTOM_PG_AS_Collection.CU_OT_PlayablePickPopup.bl_idname,
                         text="", icon="GREASEPENCIL").playableName = commandName
        plusOp = row.operator(AddCommandPopup.CU_OT_PlayableCreate.bl_idname, icon='ADD', text="New Command")
        plusOp.should_insert = True
        plusOp.insert_at_idx = len(bpy.context.scene.as_custom)

    @staticmethod
    def _DrawResult(box, kml, prefix, label):
        box.row().label(text=label)
        box.row().prop(kml, F"{prefix}FlashColor", text="Flash Color")
        box.row().prop(kml, F"{prefix}FlashSeconds", text="Flash Seconds")
        box.row().prop(kml, F"{prefix}Gestalt", text="Gestalt (Optional)")
        KeycodeMapLike._DrawCommandRow(box.row(), kml, F"{prefix}Command")

    @staticmethod
    def Display(box, context) -> None:
        kml = context.scene.keycodeMapLike

        box.row().prop(kml, "codeLength", text="Code Length")

        codesBox = box.box()
        codesBox.row().label(text="Codes")
        for i in range(kml.codeCount):
            slot = codesBox.box()
            slot.row().prop(kml, F"code{i}Key", text=F"Code {i + 1}")
            KeycodeMapLike._DrawResult(slot, kml, F"code{i}", "On Match")

        row = codesBox.row()
        row.operator(CU_OT_NumKeycodes.bl_idname, icon="ADD", text="").should_add = True
        row.operator(CU_OT_NumKeycodes.bl_idname, icon="REMOVE", text="").should_add = False

        KeycodeMapLike._DrawResult(box.box(), kml, "incorrect", "On Incorrect Code")

    codeLength: IntProperty(
        description="How many characters make up a complete code. Input shorter than this is never checked",
        get=lambda self: CLU.getIntFromKey(_Append("_code_length"), 4),
        set=lambda self, value: CLU.setValueAtKey(_Append("_code_length"), value),
        min=1,
        soft_max=12,
    )

    codeCount: IntProperty(
        description="How many code slots are in use",
        get=lambda self: CLU.getIntFromKey(_Append("_code_count"), 0),
        set=lambda self, value: CLU.setValueAtKey(_Append("_code_count"), value),
        min=0,
        max=MaxCodes,
    )


# region generated per-slot properties
#
#   Blender resolves a PropertyGroup's properties from __annotations__ at register_class time, so we can
#     fill them in programmatically here rather than hand-writing MaxCodes * len(_resultFields) near-identical
#     declarations.
#
#   The key each accessor reads has to be bound per-slot, but it CANNOT be bound with a default argument
#     (`lambda self, k=key: ...`): Blender checks the arity of get/set callbacks when it registers the
#     property and rejects anything that isn't exactly (self) / (self, value). So each accessor is built by
#     a factory function instead, which closes over the key while keeping the signature Blender expects.


def _GetString(key):
    return lambda self: CLU.getStringFromKey(key)


def _SetValue(key):
    return lambda self, value: CLU.setValueAtKey(key, value)


def _GetFloat4(key):
    return lambda self: CLU.getFloat4ArrayFromKey(key)


def _GetFloat(key, default):
    return lambda self: CLU.getFloatFromKey(key, default)


def _GetPlayableIndex(key):
    return lambda self: CLU.playableEnumIndex(key)


def _SetPlayableName(key):
    return lambda self, value: CLU.setValueAtKey(key, bpy.context.scene.as_custom[value].name)


def _AddResultProperties(cls, propPrefix: str, keyPrefix: str):
    colorKey = _Append(F"{keyPrefix}_flash_color")
    cls.__annotations__[F"{propPrefix}FlashColor"] = FloatVectorProperty(
        description="Colour the input screen flashes when this result fires",
        subtype='COLOR_GAMMA',
        get=_GetFloat4(colorKey),
        set=_SetValue(colorKey),
        size=4,
        min=0.0,
        max=1.0,
    )

    secondsKey = _Append(F"{keyPrefix}_flash_seconds")
    cls.__annotations__[F"{propPrefix}FlashSeconds"] = FloatProperty(
        description="How long the screen flash lasts, in seconds",
        get=_GetFloat(secondsKey, 3.0),
        set=_SetValue(secondsKey),
        min=0.0,
        soft_max=10.0,
    )

    gestaltKey = _Append(F"{keyPrefix}_gestalt")
    cls.__annotations__[F"{propPrefix}Gestalt"] = StringProperty(
        description="Optional name of a gestalt to play alongside the flash. Leave empty for no gestalt",
        get=_GetString(gestaltKey),
        set=_SetValue(gestaltKey),
    )

    commandKey = _Append(F"{keyPrefix}_command")
    cls.__annotations__[F"{propPrefix}Command"] = EnumProperty(
        description="Command invoked after the flash (and gestalt) finish. Optional",
        items=lambda self, context: CLU.playablesItemCallback(context),
        get=_GetPlayableIndex(commandKey),
        set=_SetPlayableName(commandKey),
    )


def _BuildGeneratedProperties(cls):
    for i in range(MaxCodes):
        codeKey = _Append(_CodeSuffix(i, "_key"))
        cls.__annotations__[F"code{i}Key"] = StringProperty(
            description="The code the player has to enter to trigger this result, e.g. \"1234\"",
            get=_GetString(codeKey),
            set=_SetValue(codeKey),
        )
        _AddResultProperties(cls, F"code{i}", _CodeSuffix(i, ""))

    _AddResultProperties(cls, "incorrect", "_incorrect")


_BuildGeneratedProperties(KeycodeMapLike)

# endregion


classes = (
    CU_OT_NumKeycodes,
    KeycodeMapLike,
)


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Scene.keycodeMapLike = bpy.props.PointerProperty(type=KeycodeMapLike)


def unregister():
    from bpy.utils import unregister_class
    for c in reversed(classes):
        unregister_class(c)

    del bpy.types.Scene.keycodeMapLike
