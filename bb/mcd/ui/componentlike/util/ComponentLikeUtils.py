import bpy
# from bpy.mathutils import Vector

from bb.mcd.util import ObjectLookupHelper
from bb.mcd.ui.componentlike import AbstractDefaultSetter
from bb.mcd.ui.actionstarterlist.CUSTOM_PG_AS_Collection import CUSTOM_PG_AS_Collection

def getValueFromKey(key_name):
    return ObjectLookupHelper._getValueFromActive(key_name, bpy.context)

def getStringFromKey(key_name, default=""):
    str = getValueFromKey(key_name)
    return str if str is not None else default

def getBoolFromKey(key_name, default=False):
    isTrigger = getValueFromKey(key_name) 
    return isTrigger if isTrigger is not None else default

def getFloatFromKey(key, default=0.0):
    f = getValueFromKey(key)
    return f if f is not None else default

def getIntFromKey(key, default=0):
    i = getValueFromKey(key)
    return i if i is not None else default

def getBoolArrayFromKey(key):
    bray = getValueFromKey(key)
    return bray if bray is not None else (False, False, False)

def getFloatArrayFromKey(key):
    fray = getValueFromKey(key)
    return fray if fray is not None else (0.0, 0.0, 0.0)

def getColorArrayFromKey(key):
    fray = getValueFromKey(key)
    return fray if fray is not None else (0.0, 0.0, 0.0)

def getFloat4ArrayFromKey(key):
    fray = getValueFromKey(key)
    return fray if fray is not None else (0.0, 0.0, 0.0, 0.0)

def getFloatBackedBooleanVector(key):
    fff = getValueFromKey(key)
    if len(fff) < 3:
        return (False, False, False)
    def truth(f : float):
        return True if f > 0.00001 else False
    return (truth(fff[0]), truth(fff[1]), truth(fff[2]))

def setFloatBackedBooleanVector(key, boolVector):
    def zeroOne(b : bool):
        return 1.0 if b else 0.0
    setValueAtKey(key, [zeroOne(boolVector[0]), zeroOne(boolVector[1]), zeroOne(boolVector[2])])

def setValueAtKey(key_name, value):
    AbstractDefaultSetter._SetKeyValOnTargets(key_name, value, bpy.context.selected_objects)


def setObjectPathStrangeAtKey(key_name, pointerObject):
    if pointerObject is None:
        setValueAtKey(key_name, "")
        return
    strangePath = ObjectLookupHelper._hierarchyToStringStrange(pointerObject)
    setValueAtKey(key_name, strangePath)

# playables as enum callback
def playablesItemCallback(context):
    playables = context.scene.as_custom
    return [(p.name, p.name, p.name) for p in playables]

def playableEnumIndexFromName(playableName : str):
    playables = bpy.context.scene.as_custom
    # iterate with an index instead of using enumerate. Enumerate leads to glitchy behavior. 
    for i in range(len(playables)):
        if playables[i].name == playableName:
            return i
    return 0 # returning -1 spams warnings -1

def playableEnumIndex(playableKey):
    return  playableEnumIndexFromName(getStringFromKey(playableKey))

def playableFromIndex(idx : int) -> CUSTOM_PG_AS_Collection:
    playables = bpy.context.scene.as_custom
    if len(playables) <= idx:
        return None # type: ignore
    return playables[idx]


def storePlayableName(targetObject, idx : int, storeStrAttr : str = "playAfterStor"):
    playable = playableFromIndex(idx)
    if playable is None:
        setattr(targetObject, storeStrAttr, "")
        # self.playAfterStor = ""
        return
    
    print(F"CLU playAfterStor was: {getattr(targetObject, storeStrAttr)} WILL SET TO : {playable.name} TYPE: {type(playable.name)}")
    # self.playAfterStor = playable.name
    setattr(targetObject, storeStrAttr, playable.name)
    print(F"playAfterStor is now: {getattr(targetObject, storeStrAttr)}")



class GenericDefaultSetter(object):
    @staticmethod 
    def OnAddKey(settingsClass, targets):
        # assume a class property Suffixes. which should be a dictionary of key values
        for suffix, val in settingsClass.Suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(settingsClass.Append(suffix), val, targets)

    @staticmethod
    def OnRemoveKey(settingsClass, targets):
        for suffix in settingsClass.Suffixes.keys():
            print(F"Generc. will rm key: {settingsClass.Append(suffix)}")
            AbstractDefaultSetter._RemoveKey(settingsClass.Append(suffix), targets)

