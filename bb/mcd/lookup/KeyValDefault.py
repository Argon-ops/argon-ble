"""
This module provides functions for accessing the defaults dictionary.

The defaults dictionary stores a key for each component-like that's available to the user and a value 
representing default settings for that component-like. 
"""

import json
from bb.mcd.configs import MCDKeyValConfig
import typing


class EHandlingHint():
    PRIMITIVE = "PRIMITIVE"
    TAG = "TAG"
    CUSTOM_INSPECTOR = "CUSTOM_INSPECTOR"
    CUSTOM_COMPONENT = "CUSTOM_COMPONENT"


class DefaultValueInfo(object):
    """Formal declarations of the expected fields

        for config objects.
    """
    default: any
    hint: str
    help: str
    applyClass: str


_storage: typing.Dict[str, DefaultValueInfo] = {}


def _isPrimitive(val):
    return isinstance(val, str) or isinstance(val, int) or isinstance(val, float)


def _parse(val: any) -> DefaultValueInfo:
    """Convert from json config data to DefaultValueInfo objects"""

    def createDefaultValueInfo(default, hint: str, help: str, apply: str) -> DefaultValueInfo:
        dvi = DefaultValueInfo()
        dvi.default = default
        dvi.hint = hint
        dvi.help = help
        dvi.applyClass = apply
        return dvi

    default = 0
    if 'default' in val:
        default = val['default']
    hint = val['hint']
    help = val['help']
    apply = val['apply_class'] if 'apply_class' in val else ''

    if hint == "PRIMITIVE":
        return createDefaultValueInfo(default, EHandlingHint.PRIMITIVE, "", apply)

    if hint == "TAG":
        return createDefaultValueInfo(0, EHandlingHint.TAG, "", apply)

    if hint == "CUSTOM_COMPONENT":
        return createDefaultValueInfo(default, EHandlingHint.CUSTOM_COMPONENT, help, apply)

    else:  # CUSTOM_INSPECTOR
        hint = hint if hint else EHandlingHint.CUSTOM_INSPECTOR
        return createDefaultValueInfo(default, hint, help, apply)


def _addEntry(key: str, val):
    global _storage
    _storage[key] = _parse(val)


def _loadFrom(json_str: str) -> None:
    try:
        data = json.loads(json_str)
        for key, val in data.items():
            _addEntry(key, val)

    except BaseException as e:
        print(F"trouble loading {str(e)}")


def getDefaultValueInfo(key: str):
    global _storage
    return _storage[key]


def getDefaultValue(key: str):
    global _storage
    item = _storage[key]
    if item.hint == EHandlingHint.TAG:
        return -7  # value doesn't matter. nonetheless just return something
    if item.hint == EHandlingHint.CUSTOM_COMPONENT:
        # the default value is the json string
        # TODO: handle a case where we want to combine this with applying a custom component
        return json.dumps(item.default)
    return item.default


def getHandlingHint(key: str) -> EHandlingHint:
    global _storage
    try:
        item = _storage[key]
        return item.hint
    except BaseException as e:
        return EHandlingHint.PRIMITIVE


def getHelp(key: str) -> str:
    global _storage
    try:
        item = _storage[key]
        return item.help
    except BaseException as e:
        return ""


def getMCDConfig() -> typing.Dict[str, DefaultValueInfo]:
    global _storage
    # already loaded?
    if "mel_no_renderer" not in _storage.keys():
        forceReload()
    return _storage


def forceReload() -> None:
    """Reset the global variable that stores all Key-Value configs"""
    _storage.clear()
    _loadFrom(MCDKeyValConfig.config)
    _getCustomDefsConfig()


def _getCustomDefsConfig() -> None:
    import bpy
    from pathlib import Path
    path = bpy.context.scene.compo_definition_file
    f = Path(bpy.path.abspath(path))
    if not f.exists():
        return None

    try:
        _loadFrom(f.read_text())
    except:
        print(
            F"There was an error parsing the custom component definition file at {path} ")
