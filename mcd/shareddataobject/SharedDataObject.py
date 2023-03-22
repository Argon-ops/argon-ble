
import bpy

__SHARED_DATA_ROOT__="z_Duks_SharedDataRoot"

# must match unity importer script
__DATA_OBJECT_NAME__="z_DuksGames_SharedData_"

# # must match unity importer script
# __DATA_OBJECT_MAIN_KEY__="mel_shared_data_object"

def getSharedRoot():
    # is the object in the scene already?
    # if __dataObject is None: ## just search every time
    rootObj = bpy.context.scene.objects.get(__SHARED_DATA_ROOT__)

    # do we need to make a new one?    
    if rootObj is None:
        # FBX exporter might ignore an empty; so add a hard-to-see cube
        bpy.ops.mesh.primitive_cube_add(location=(0,0,0), size=0.0001) 
        rootObj = bpy.context.view_layer.objects.active
        rootObj.name = __SHARED_DATA_ROOT__

    return rootObj


def getSharedDataObjectWithName(name : str):
    # is the object in the scene already?
    # if __dataObject is None: ## just search every time
    __dataObject = bpy.context.scene.objects.get(name)

    # do we need to make a new one?    
    if __dataObject is None:
        # FBX exporter might ignore an empty; so add a hard-to-see cube
        bpy.ops.mesh.primitive_cube_add(location=(0,0,0), size=0.0001) 
        __dataObject = bpy.context.view_layer.objects.active
        __dataObject.name = name
        root = getSharedRoot()
        __dataObject.parent = root

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
    # ob = getEmptySharedDataOject()
    # ob.select_set(select)