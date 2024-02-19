import bpy

# from bb.mcd.ui.actionstarterlist.CUSTOM_PG_AS_Collection import (
#         PlayablesExporter as PE
#     )
# from bb.mcd.shareddataobject.SharedDataObject import GetFirstSelectedObjectOrAny

def ObjDictTest():
    import json
    ob = bpy.context.scene.as_custom[0]
    # print(vars(ob))
    # print(F"found {ob.name}")
    # print(json.dumps(ob.__dict__))
    # print(ob.__annotations__)

    from bb.mcd.ui.actionstarterlist.CUSTOM_PG_AS_Collection import CUSTOM_PG_AS_Collection as AS
    for fn in ob.__annotations__.keys():
        serVal = AS.GetSerialiazableValue(ob, fn)
        print(F"field: {fn} val: {getattr(ob, fn)} serval: {serVal}")


def _D_anyActionNames():
    for obj in bpy.context.scene.objects:
        ad = obj.animation_data
        if ad:
            if ad.action:
                print(obj.name,'uses',ad.action.name)
            for t in ad.nla_tracks:
                for s in t.strips:
                    print(obj.name,'uses',s.action.name)


# def TestWriteCommands():
#     target = GetFirstSelectedObjectOrAny()
#     PE.WriteCommandsToTargetObject(target)

def ShowCommands():
    from bb.mcd.ui.actionstarterlist.CUSTOM_PG_AS_Collection import CUSTOM_PG_AS_Collection as AS
    for cmd in bpy.context.scene.as_custom:
        print(F"CMD: {cmd.name} ")
        for fn in cmd.__annotations__.keys():
            print(F"{fn} : {AS.GetSerialiazableValue(cmd, fn)}")

def TestGetFirst():
    from bb.mcd.shareddataobject import SharedDataObject as SDO
    f = SDO.GetFirstSelectedObjectOrAny()
    print(F"first {f.name}")

def GetAnArma(name : str):
    safe = 0
    for arma in bpy.data.armatures:
        print(F" arma name: {arma.name}")
        if safe > 40:
            break
        safe += 1
    found = bpy.data.armatures[name]
    print(F"found arma: {arma.name if arma is not None else '<did not find anything>'}")

def ListArmas():
    for i in range(len(bpy.data.armatures)):
        arma = bpy.data.armatures[i]
        print(F"[{i}]: {arma.name}")
    # print("By keys")
    # for akey in bpy.data.armatures.keys():
    #     print(F"arma key {akey} val: {bpy.data.armatures[akey].name}")

def ListObjs():
    for ob in bpy.context.scene.objects:
        print(F"OB_: {ob.name}")
        print(F"IS armature: {ob.type == 'ARMATURE'}")
        # print(F"DIR : {dir(ob)} ")
        for arma in ob.modifiers:
            print(F"    ob's arma: {arma.name}")

def AddAndGetNew():
    prev_names = bpy.data.armatures.keys().copy()
    bpy.ops.object.armature_add(enter_editmode=False, align='WORLD')
    for key in bpy.data.armatures.keys():
        if key not in prev_names:
            return bpy.data.armatures[key]
    print(F"this won't happen")
    raise "won't happen"


def NameAnArma(name : str, idx = 0):
    arma = bpy.data.armatures[idx]
    print(F"prev name {arma.name}")
    arma.name = name
    print(F"now : {arma.name}")

def TestAddArma(name : str):
    # is the object in the scene already?
    __dataObject = bpy.data.armatures.get(name) # [name] # bpy.context.scene.objects.get(name)
    # updateMsgbusShared(__dataObject, name) # RETREAT: do nothing to fend off renaming. Trust users to not rename

    # do we need to make a new one?    
    if __dataObject is None:
        print(F"NEED to ADD {name}")
        # FBX exporter might ignore an empty; so add a hard-to-see cube
        # bpy.ops.mesh.primitive_cube_add(location=(0,0,0), size=0.0001) 
        # actually use an armature
        # bpy.ops.object.armature_add(enter_editmode=False, align='WORLD')

        __dataObject = AddAndGetNew() #  bpy.data.armatures[-1] # bpy.context.view_layer.objects.active

        print(F"JUST AFTER ADD")
        ListArmas()

        __dataObject.name = name
        # __dataObject.parent = getSharedRoot()

        # add a destroy tag
        __dataObject['mel_destroy']=0
        # _zeroOutUVs(__dataObject)

    return __dataObject

def GetOrAdd(name :str):
    got = TestAddArma(name)
    print(F"GOT: {got.name}")
    ListArmas()
    print(F"DONE")

def CommandNames():
    import bb.mcd.ui.actionstarterlist.CUSTOM_PG_AS_Collection as AS
    cmds = [s[1] for s in AS.getPlayableTypes()]
    for c in sorted(cmds):
        print(F"## {c}")


def TestR():
    print("scratch")
    mat_door = bpy.data.materials["Door"]
    for prop in mat_door.keys():
        print(F"{prop}")
    print("done")


def ListPropKeys():
    c = bpy.context.scene.custom
    print("hello")
    for k in sorted([k.key for k in c]):
        k = k[4:].replace("_", " ")
        k = k.title()
        print(F"## {k}")
    print("hi")
