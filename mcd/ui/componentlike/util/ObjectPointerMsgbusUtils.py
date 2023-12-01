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
from mcd.shareddataobject import SharedDataObject

# FIXME: this static _lookuplookup 
#   gets wiped out each time we reload the script. (Possibly we can live with this
#     since it will only affect us during development.  But it will affect a user
#       who reloads the plugin multiple times)
_lookuplookup = {}

# def _getLLSharedObjTry():
#     return SharedDataObject.getSharedDataObjectWithName("z_MsgBusTokenLLObj")

# def _getLLTry():
#     llob = _getLLSharedObjTry()
#     if 'lookup' not in llob:
#         llob['lookup'] = {}
#     return llob['lookup']

# Get the dictionary associated with target
#  create if it didn't exist yet.
def _getTokenLookup(target):
    global _lookuplookup
    # _lookuplookup = _getLLTry()
    if target not in _lookuplookup.keys(): # FIXME: needs to be a string ... could we use name
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


from bpy.app.handlers import persistent

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

    AbstractDefaultSetter.SetVal(key, ptrObj.name, target)



def updateMsgbus(target, ptrPropObject, propertyKey, callbackOwner):
    bpy.msgbus.clear_by_owner(callbackOwner)

    if ptrPropObject is not None:

        bpy.msgbus.subscribe_rna(
            # path_resolve is required here. not just 'ptrPropObject.name'
            # reference: https://blender.stackexchange.com/a/224186/100992
            key=ptrPropObject.path_resolve("name", False), 
            owner=callbackOwner,
            args=(target, ptrPropObject, propertyKey, F"orig ptr ob name [{ptrPropObject.name}], targ name: {target.name}"), # NOTE: this 4th arg is for debugging
            notify=msgBusObjectPointerCallback
        )


# params:
# target:  object that owns a PerObject PropertyGroup instance.
#            typically this is the current active-selected object.
# ptrObjectSelf : the per-object-data object, 
# ptrPropName : the name of the PointerProperty (e.g. 'showObjectRoot')
# propertyKey:   the key under which the referred to object's name should be stored
# callbackOwner:   can be any object. this is used as the msgbus callback owner. You want to 
#       supply the same object for the same target-pointerProp pair. This way any 
#       previous callback will be removed/unsubscribed upon subsequent calls.
def onObjectUpdate(target, perObjectSelf, ptrPropName, propertyKey):
    
    ptrPropObject = getattr(perObjectSelf, ptrPropName) 

    token = perObjectSelf.__annotations__[ptrPropName] 

    updateMsgbus(target, ptrPropObject, propertyKey, 
                 token)

    #  write to this object's properties 
    AbstractDefaultSetter.SetVal(
        propertyKey, 
        ptrPropObject.name if ptrPropObject is not None else "", 
        target)



# restore msg bus callbacks where appropriate 
## params
#    1: perObField: the per object field attribute e.g. .camLockPerObjectData (but use getattr)
#    2: refObField: the object ref attribute on the previous obj e.g. .hideRootObject (but use getattr)
#    3: fullKey: the custom prop field. e.g.  "_hide_root_object"
def resubscribeAll_LP(perObField : str, refObField : str, fullKey : str):
    for obj in bpy.context.scene.objects:
        perObjectData = getattr(obj, perObField) # get the per-object data: e.g. CamLockPerObjectData
        refObj = getattr(perObjectData, refObField) # get the field in question: e.g. showRootObject
        if refObj is None:
            continue

        # any python object can serve as the owner token.
        #  So use the pointer property itself (not the pointed-to object) as the token
        #   since this is (by definition) unique per object per data_object per pointer_prop field
        token = perObjectData.__annotations__[refObField] 

        # restore the msgbus subscription for this ob            
        updateMsgbus(
            obj, 
            refObj, 
            fullKey, 
            token)



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

# TODO: array-ize everything. meaning, for each target. clear by THAT target's owner (need a list of owners)
# also, array-ize the callback: each target gets its own personal callback with its personal owner object
#  WHY: this way, we'll avoid scenarios where a callback attached to an objects owner doesn't decide to meddle with
#   the data on another object--especially after that object has (potentially) reassigned its object pointer; so the
#   first object has no business.