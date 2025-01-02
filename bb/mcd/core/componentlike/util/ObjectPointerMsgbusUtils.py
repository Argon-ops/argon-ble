from bpy.app.handlers import persistent
import bpy
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU

# FIXME: this static dictionary
#   gets wiped out each time we reload the script. (Possibly we can live with this
#     since it will only affect us during development.  But it will affect a user
#       who reloads the plugin multiple times)
_lookuplookup = {}


def _getTokenLookup(target):
    """
    Get the dictionary associated with target.

        Create if it didn't exist yet.
    """
    global _lookuplookup

    if target not in _lookuplookup.keys():  # FIXME: needs to be a string ... could we use name
        print(
            F" ``` NOT IN. adding new owner-token dictionary for {target.name}")
        _lookuplookup[target] = {}
    return _lookuplookup[target]



def GetOwnerToken(target, token_key: str):
    """
    Gets a unique owner object (for msg bus). per blender object, per token key

        token_key is a key that's (hopefully) unique for the given class, prop field (e.g. "CamLockDataPerObjectHideObject")
    """
    lookup = _getTokenLookup(target)
    if token_key not in lookup:
        lookup[token_key] = object()
    return lookup[token_key]


@persistent
def msgBusObjectPointerCallback(*args):
    target = args[0]
    ptrObj = args[1]
    key = args[2]
    # if len(args) < 3:
    #     return # delete this check
    # # DebugInfo = args[3] if len(args) > 3 else "<Not supplied>"
    # # print(F" %%% MSG BUS len args({len(args)}) CB key:  {key} :: \n\t targets: {target} \n\t ptrObj: {getattr(ptrObj, 'name')} \n\t Debug Info: {DebugInfo} ")
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
            # NOTE: this 4th arg is for debugging
            args=(target, ptrPropObject, propertyKey,
                  F"orig ptr ob name [{ptrPropObject.name}], targ name: {target.name}"),
            notify=msgBusObjectPointerCallback
        )


def onObjectUpdate(target, perObjectSelf, ptrPropName, propertyKey):
    """ 
    Args:

        target:  object that owns a PerObject PropertyGroup instance.
                   typically this is the current active-selected object.
        perObjectSelf: the per-object-data object,
        ptrPropName: the name of the PointerProperty (e.g. 'showObjectRoot')
        propertyKey: the key under which to store the object
    """
    ptrPropObject = getattr(perObjectSelf, ptrPropName)

    token = perObjectSelf.__annotations__[ptrPropName]

    updateMsgbus(target, ptrPropObject, propertyKey,
                 token)

    #  write to this object's properties
    AbstractDefaultSetter.SetVal(
        propertyKey,
        ptrPropObject.name if ptrPropObject is not None else "",
        target)


def resubscribeAll_LP(perObField: str, refObField: str, fullKey: str):
    """
    Restore msg bus callbacks where appropriate for the given per-object data

        params
        1: perObField: the string name of the per object field attribute. e.g. 'camLockPerObjectData' 
        2: refObField: the string name of the object ref attribute. e.g. 'hideRootObject' 
        3: fullKey: the custom prop field. e.g.  'mel_cam_lock_session_enable_hide_root_object'
    """
    for obj in bpy.context.scene.objects:
        # get the per-object data: e.g. CamLockPerObjectData
        perObjectData = getattr(obj, perObField)
        # get the field in question: e.g. showRootObject
        refObj = getattr(perObjectData, refObField)
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
