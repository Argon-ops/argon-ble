# The actual KeyValDefault is a dictionary
# this class codefies our expectations for which keys we'll find

import json
from mcd.melstor import MCDKeyValConfig ## WANT 
import typing

class EHandlingHint():
    PRIMITIVE = "PRIMITIVE"
    TAG = "TAG"
    CUSTOM_INSPECTOR = "CUSTOM_INSPECTOR"

class DefaultValueInfo(object):
    default : any
    # serializableDefault : any # TODO this shouldn't exist?
    handlingHint : str
    help : str

_storage : typing.Dict[str, DefaultValueInfo] = {}

def _isPrimitive(val):
    return isinstance(val, str) or isinstance(val, int) or isinstance(val, float)

def _parse(val : any) -> DefaultValueInfo:
    def createDefaultValueInfo(default, hint : str, help : str) -> DefaultValueInfo:
        dvi = DefaultValueInfo()
        dvi.default = default
        # dvi.serializableDefault = serializableDefault
        dvi.handlingHint = hint
        dvi.help = help
        return dvi

    if _isPrimitive(val):
        return createDefaultValueInfo(val, EHandlingHint.PRIMITIVE, "")
 
    # if val has no keys its just a tag
    if val is None or not val or len(val.keys()) == 0:
        return createDefaultValueInfo(0, EHandlingHint.TAG, "")

    # must be an object with config directives
    # TODO: serializbleDefault is pointless and even default is a little awkward.
    #    figure out what settings are easiest for the clients of this script
    default = 0
    if 'default' in val:
        default = val['default']
    hint = val['hint']
    hint = hint if hint else EHandlingHint.PRIMITIVE
    help = val['help']
    return createDefaultValueInfo(default, hint, help)

def _addEntry(key : str, val):
    global _storage

    if key in _storage.keys():
        print(F"storage has this key already? do we care?")
    
    _storage[key] = _parse(val)


def _loadFrom(json_str : str):
    try:
        data = json.loads(json_str)
        for key, val in data.items():
            _addEntry(key, val)

    except BaseException as e:
        print(F"trouble loading {str(e)}")

def getDefaultValue(key : str):
    global _storage
    item = _storage[key]
    if item.handlingHint == EHandlingHint.TAG:
        return -7 # value doesn't matter well never see this. nonetheless just give them any old value
    return item.default

def getHandlingHint(key: str) -> EHandlingHint:
    global _storage
    try:
        item = _storage[key]
        return item.handlingHint
    except BaseException as e:
        return EHandlingHint.PRIMITIVE

def getHelp(key : str) -> str:
    global _storage
    try:
        item = _storage[key]
        return item.help
    except BaseException as e:
        return ""

# def getSerializableDefaultValue(key : str):
#     # return getDefaultValue(key)
#     # # BUT WE ACTUALLY WANT THE BELOW
#     global _storage
#     item = _storage[key]
#     return item.serializableDefault

def getMCDConfig() -> typing.Dict[str, DefaultValueInfo]:
    global _storage
    # already loaded?
    if "mel_no_renderer" not in _storage.keys():
        _loadFrom(MCDKeyValConfig.config)
    return _storage



# TODO: load Mel's defaults from an adjacent str that's json formatted in file
#  MelDefaults.py