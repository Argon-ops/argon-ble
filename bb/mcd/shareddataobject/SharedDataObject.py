
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
#     from bb.mcd.util import AppHandlerHelper
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

def DTestUVIter():
    _zeroOutUVs(bpy.context.active_object, 0.0)

def _zeroOutUVs(ob, scalar = 0.0):
    for loop in ob.data.loops:
        try:
            ob.data.uv_layers.active.data[loop.index].uv *= scalar
            uv_coords = ob.data.uv_layers.active.data[loop.index].uv
            print(uv_coords)
        except IndexError:
            print(F"Got IndexError when zeroing out uvs of {ob.data.name}")
            break

def DTestPropOnMaterial():
    mat = bpy.context.active_object.active_material
    if mat is None:
        print(F"mat is None")
        return
    p = "some_prop"
    mat[p] = 2.5
    print(F"{mat[p]}")


def getSharedRoot():
    rootObj = bpy.context.scene.objects.get(__SHARED_DATA_ROOT__)
    # do we need to make a new one?    
    if rootObj is None:
        # FBX exporter might ignore an empty; so add a hard-to-see cube
        bpy.ops.mesh.primitive_cube_add(location=(0,0,0), size=0.0001) 
        # actually use an armature
        # bpy.ops.object.armature_add(enter_editmode=False, align='WORLD')

        rootObj = bpy.context.view_layer.objects.active
        # rootObj = bpy.data.armatures[-1] # bpy.context.view_layer.objects.active
        rootObj.name = __SHARED_DATA_ROOT__
        # add a destroy tag
        rootObj['mel_destroy']=0

        # _zeroOutUVs(rootObj) # FIX ME: this kills blender!!
        #  TODO: test all kinds of strange-ness with these lazy get obj functions
        #    for example, seems like (emphasis) we tried to get the root obj while in edit mode.
        #      what actually happened was: we stayed in edit mode and added a cube to the obj we were editing (!)
        #      Then we renamed that object to __SHARED_DATA_ROOT__
        #    Then, (somehow) this process happened over and over again in an infinite loop?
        #     And not coincidentally, the obj being edited ended up with 100K vertices (all tiny cubes we are thinking)
        #   So TODO make sure we're in object mode before object creating... 
        #    (and it'd be amazing if we could just add an empty but Q: will the Fbx exporter export our empty?)

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



def addNewArmatureAndGet():
    # contortions to retrieve the armature that we are about to add
    prev_names = bpy.data.armatures.keys().copy()
    bpy.ops.object.armature_add(enter_editmode=False, align='WORLD')
    for key in bpy.data.armatures.keys():
        if key not in prev_names:
            return bpy.data.armatures[key]
    raise "won't happen"


def getSharedDataObjectWithName(name : str):
    
    # is the object in the scene already?
    __dataObject = bpy.context.scene.objects.get(name)
    # updateMsgbusShared(__dataObject, name) # RETREAT: do nothing to fend off renaming. Trust users to not rename

    # do we need to make a new one?    
    if __dataObject is None:

        print(F"CREATE shared data obj: {name}")
        # FBX exporter might ignore an empty; so add a hard-to-see cube
        bpy.ops.mesh.primitive_cube_add(location=(0,0,0), size=0.0001) 
        # actually use an armature
        __dataObject = bpy.context.view_layer.objects.active
        # __dataObject = addNewArmatureAndGet() # bpy.context.view_layer.objects.active

        __dataObject.name = name

        # __dataObject.parent = getSharedRoot()

        # add a destroy tag
        __dataObject['mel_destroy']=0
        _zeroOutUVs(__dataObject)

    return __dataObject

def GetFirstSelectedObjectOrAny():
    if len(bpy.context.selected_objects) > 0:
        return bpy.context.selected_objects[0]
    return bpy.context.scene.objects[0]
    



def objectExists(name : str):
    return bpy.context.scene.objects.get(name) is not None

def emptySharedDataObjectExists():
    return bpy.context.scene.objects.get(__DATA_OBJECT_NAME__) is not None

def getEmptySharedDataOject():
    return getSharedDataObjectWithName(__DATA_OBJECT_NAME__)

def selectSharedDataObjects(select : bool):
    return # ## armature TODO: get the associated object
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