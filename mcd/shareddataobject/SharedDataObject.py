
import bpy

__SHARED_DATA_ROOT__="z_Duks_SharedDataRoot"

# must match unity importer script
__DATA_OBJECT_NAME__="z_DuksGames_SharedData_"

# # must match unity importer script
# __DATA_OBJECT_MAIN_KEY__="mel_shared_data_object"


# # REGION LoadPost boilerplate

# from bpy.app.handlers import persistent
# @persistent
# def resubAllLoadPostSliderCollider(dummy):
#     getSharedRoot()

# # add a load post handler so that we resubscribeAll upon loading a new file         
# def setupLoadPost():
#     from mcd.util import AppHandlerHelper
#     AppHandlerHelper.RefreshLoadPostHandler(resubAllLoadPostSliderCollider) 

# # END_REGION


# def _sharedObjectCallback( *args) -> None:
#     sharedObject=args[0]
#     properName=args[1]
#     if properName == sharedObject.name:
#         print(F"correct name no need to take action. bye")
#         return
    
#     print(F"_shared ob callback. name now: {sharedObject.name} | should be: {properName}")
#     # TODO: enforce old name (politely)
#     # bpy.context.report({'INFO'}, F"$$$$ polite msg")
#     bpy.ops.report.helper()
#     sharedObject.name=properName

# # do we need @persistent??
# def updateMsgbusShared(sharedObject, properName):
#     bpy.msgbus.clear_by_owner(sharedObject) # not a bad idea
#     bpy.msgbus.subscribe_rna(
#         key=sharedObject.path_resolve("name", False),
#         owner=sharedObject,
#         args=(sharedObject, properName),
#         notify=_sharedObjectCallback)

# def updateRootMsgbus():
#     rootObj = bpy.context.scene.objects.get(__SHARED_DATA_ROOT__)
#     if rootObj is not None:
#         updateMsgbusShared(rootObj, __SHARED_DATA_ROOT__) 

def getSharedRoot():
    rootObj = bpy.context.scene.objects.get(__SHARED_DATA_ROOT__)
    # do we need to make a new one?    
    if rootObj is None:
        # FBX exporter might ignore an empty; so add a hard-to-see cube
        bpy.ops.mesh.primitive_cube_add(location=(0,0,0), size=0.0001) 
        rootObj = bpy.context.view_layer.objects.active
        rootObj.name = __SHARED_DATA_ROOT__
        # add a destroy tag
        rootObj['mel_destroy']=0
        #add to collection
        # addToArgonSharedCollection(rootObj)

    # #msgbus
    # updateMsgbusShared(rootObj, __SHARED_DATA_ROOT__) # RETREAT: don't defend against renaming. just trust the users. And document

    return rootObj

# def _getOrCreateArgonDataCollection():
#     __ARGON_SHARED__="ArgonShared"
#     if __ARGON_SHARED__ not in bpy.data.collections: 
#         argonc = bpy.data.collections.new(__ARGON_SHARED__)
#         bpy.context.scene.collection.children.link(argonc)
#         return argonc
#     return bpy.data.collections[__ARGON_SHARED__]

# def addToArgonSharedCollection(ob : object):
#     argonc = _getOrCreateArgonDataCollection()
#     if ob.name in argonc.objects:
#         print(F"{ob.name} is already in the collection")
#         return
#     argonc.objects.link(ob)

# TODO: put any shared objects into the default scene collection
# TODO: on the c# side, delete the shared objects from the hierarchy: just add a Destroy tag on this side actually
#   Are we able to add tags from another module? Easy to do it manually in the case of Destroy but...

def getSharedDataObjectWithName(name : str):
    # is the object in the scene already?
    __dataObject = bpy.context.scene.objects.get(name)
    # updateMsgbusShared(__dataObject, name) # RETREAT: do nothing to fend off renaming. Trust user's to not rename

    # do we need to make a new one?    
    if __dataObject is None:
        # FBX exporter might ignore an empty; so add a hard-to-see cube
        bpy.ops.mesh.primitive_cube_add(location=(0,0,0), size=0.0001) 
        __dataObject = bpy.context.view_layer.objects.active
        __dataObject.name = name
        __dataObject.parent = getSharedRoot()

        # destroy tag
        __dataObject['mel_destroy']=0

    return __dataObject



def objectExists(name : str):
    return bpy.context.scene.objects.get(name) is not None

def emptySharedDataObjectExists():
    return bpy.context.scene.objects.get(__DATA_OBJECT_NAME__) is not None

def getEmptySharedDataOject():
    return getSharedDataObjectWithName(__DATA_OBJECT_NAME__)

def selectSharedDataObjects(select : bool):
    root = getSharedRoot()
    root.select_set(select)
    for child in root.children:
        child.select_set(select)


def register():
    pass
    # CONSIDER: can we just try to add in some protections on the C# side. instead of enforcing these names??
    #   Or is the name enforcement helpful?? What if the user tries to copy this shared_data to another file...oh boy...
    # updateRootMsgbus()

def unregister():   
    pass