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
from mcd.ui.componentlike import AbstractDefaultSetter
from mcd.ui.componentlike.util import ComponentLikeUtils as CLU

_lookuplookup = {}

def _getTokenLookup(target):
    global _lookuplookup
    if target not in _lookuplookup.keys():
        print(F" ``` NOT IN. adding new owner-token dictionary for {target.name}")
        _lookuplookup[target] = {}
    return _lookuplookup[target]

#  Gets a unique owner object (for msg bus). per blender object, per token key
# token_key is a key that's (hopefully) unique for the given class, prop field (e.g. "CamLockDataPerObjectHideObject")
def GetOwnerToken(target, token_key : str): 
    lookup = _getTokenLookup(target)
    if token_key not in lookup:
        lookup[token_key] = object()
    return lookup[token_key]
    

# whole idea is kaput because prop groups are bad at being msgbus tokens. 
# class OwnerTokens(PropertyGroup):
#     @staticmethod
#     def GetOrAddToken(tokens, key : str):
#         print(F" token keys: {','.join([t.key for t in tokens])}")
#         for token in tokens:
#             if key == token.key:
#                 print(F"already had a token for key {key}. Len tokens {len(tokens)}")
#                 return token
#         token = tokens.add()
#         token.key = key
#         print(F" Add a token for key: {key}. Len tokens now: {len(tokens)}")
#         return token
    
#     key : StringProperty()

from bpy.app.handlers import persistent

# TODO: it actually doesn't seem too crazy to just change the msgBus callback so that
#  it assumes an array of written to objs...
#  No wait... that already happens... but isn't what we need. simply need a method
#   that propagates the changed of object to the other fields of the other targets...
#  do-able, granted we'll need to tolerate some parameter count bloat.
#   And just document the living hell out of this plz. <-- this doesn't fly because we can't assign to POinterProps

## static
@persistent
def msgBusObjectPointerCallback(*args):
    target = args[0]
    ptrObj = args[1]
    key = args[2]
    DebugInfo = args[3] if len(args) > 3 else "<Not supplied>"
    if len(args) < 3:
        return # delete this check
    print(F" %%% MSG BUS len args({len(args)}) CB key:  {key} :: \n\t targets: {target} \n\t ptrObj: {getattr(ptrObj, 'name')} \n\t Debug Info: {DebugInfo} ")
    # TODO: there's an error if the target was deleted. try including the owner of the msgb cb as an arg. if the target nE anymore. remove the callback

    # AbstractDefaultSetter._SetKeyValOnTargets(key, ptrObj.name, targets)
    AbstractDefaultSetter.SetVal(key, ptrObj.name, target)

# TODO: restrict the callback owner and the callback so that its all one-to-one-to-one
#   for one ptrobj-pointingProp combo (per prop owning object), let there be exactly one callback-owner

# TODO: array-ize everything. meaning, for each target. clear by THAT target's owner (need a list of owners)
# also, array-ize the callback: each target gets its own personal callback with its personal owner object
#  WHY: this way, we'll avoid scenarios where a callback attached to an objects owner doesn't decide to meddle with
#   the data on another object--especially after that object has (potentially) reassigned its object pointer; so the
#   first object has no business.

## static
def updateMsgbus(target, ptrPropObject, propertyKey, callbackOwner):
    bpy.msgbus.clear_by_owner(callbackOwner)

    if ptrPropObject is not None:

        bpy.msgbus.subscribe_rna(
            # path_resolve is required here. not just ptrPropObject.name. 
            # reference: https://blender.stackexchange.com/a/224186/100992
            key=ptrPropObject.path_resolve("name", False), 
            owner=callbackOwner,
            args=(target, ptrPropObject, propertyKey, F"orig ptr ob name [{ptrPropObject.name}], targ name: {target.name}"), # NOTE: this 4th arg is for debugging
            notify=msgBusObjectPointerCallback
        )

## static / helper for PerObject (or part of base class idk)
# params:
# targets:   a list (or similar) of the objects that own PerObject PropertyGroup instance(s) 
#    e.g. the current selected objects
# ptrObjectSelf : the per-object-data object, 
# ptrPropName : the name of the PointerProperty (e.g. 'showObjectRoot')
# propertyKey:   the key under which the refered to object's name should be stored
# callbackOwner:   can be any object. this is used as the msgbus callback owner. You want to 
#   supply the same object for the same target-pointerProp pair. This way any 
#     previous callback will be removed/unsubscribed upon subsequent calls.

# def onObjectUpdate(targets, ptrPropObject, propertyKey, callbackOwner):    
def onObjectUpdate(target, perObjectSelf, ptrPropName, propertyKey, callbackOwner):
    # TODO: just one target please! may as well have param target. targets.Length == 1
    # if len(target) != 1:
    #     print(F"Only one target please")
    #     raise "Only one target plz."
    
    ptrPropObject = getattr(perObjectSelf, ptrPropName) # Pointlessly using getattr instead of just requiring ptrPropOjbect as a param 

    updateMsgbus(target, ptrPropObject, propertyKey, callbackOwner)

    #  write to this object's properties 
    AbstractDefaultSetter.SetVal(
        propertyKey, 
        ptrPropObject.name if ptrPropObject is not None else "", 
        target)

## params
#    1: the per object field attribute e.g. .camLockPerObjectData (but use getattr)
#    2: the object ref attribute on the previous obj e.g. .hideRootObject (but use getattr)
#    3: the custom prop field  "_hide_root_object"
##   Test the newly genericized func here to ensure that it works
# restore msg bus callbacks where appropriate
def resubscribeAll_LP(perObField : str, refObField : str, fullKey : str, ownerTokenKey : str):
    print(F"resubscribe all in OPMUtils")
    for obj in bpy.context.scene.objects:
        camlockData = getattr(obj, perObField) # get the per-object data: e.g. CamLockPerObjectData
        refObj = getattr(camlockData, refObField) # get the field in question: e.g. showRootObject
        if refObj is None:
            continue

        # print(F"()()() Will resub {obj.name} with ref {refObField} ==> {refObj.name} ()()()")
        updateMsgbus(
            obj, #[obj], 
            refObj, 
            fullKey, 
            GetOwnerToken(obj, ownerTokenKey))



## RETREAT: multi-select version of onObjectUpdate that might work but then we remembered 
##  we can't directly assign to PointerProperties.
##   So, just revert to only dealing with the active_object. no multi selection
# def onObjectUpdate(referenceTarget, targets, perObjectFieldName, ptrPropName, propertyKey, ownerTokenKey : str) : # callbackOwner):
#     for target in targets:
#         perObjectSelf = getattr(target, perObjectFieldName)
#         ptrPropObject = getattr(perObjectSelf, ptrPropName)
#         callbackOwner = OwnerTokens.GetOrAddToken(perObjectSelf.ownerTokens, ownerTokenKey)
#         updateMsgbus([target], ptrPropObject, propertyKey, callbackOwner) # TODO: target doesn't need to be in a list. 
    
#     # also update the values that the ptrPropObjects point to
#     #  so that they match that the value set on the active object (referenceTarget)
#     #  separate for loop for clarity? (wait... are we allowed to do that??)

#     #  write to this object's properties 
#     AbstractDefaultSetter._SetKeyValOnTargets(
#         propertyKey, 
#         ptrPropObject.name if ptrPropObject is not None else "", 
#         targets)
    