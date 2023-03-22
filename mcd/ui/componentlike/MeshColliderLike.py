import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)
from mcd.util import ObjectLookupHelper

from mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
from mcd.ui.componentlike import AbstractDefaultSetter
from mcd.ui.componentlike.util import ComponentLikeUtils as CLU

import json


def getConvex(self):
    return CLU.getBoolFromKey("mel_mesh_collider_convex")

def setConvex(self, value):
    CLU.setValueAtKey("mel_mesh_collider_convex", value)

def getIsTrigger(self):
    return CLU.getBoolFromKey("mel_mesh_collider_is_trigger")

def setIsTrigger(self, value):
    CLU.setValueAtKey("mel_mesh_collider_is_trigger", value)

class MeshColliderDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return MeshColliderLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        return AbstractDefaultSetter._IsEqual("mel_mesh_collider_is_trigger", a, b) \
            and AbstractDefaultSetter._IsEqual("mel_mesh_collider_convex", a, b)

    @staticmethod
    def OnAddKey(key : str, val, targets):
        # AbstractDefaultSetter._SetKeyValOnTargets("mel_mesh_collider", -7, targets) # no need
        default = AbstractDefaultSetter._GetDefaultFromPrefs(key)
        try:
            AbstractDefaultSetter._SetKeyValOnTargets("mel_mesh_collider_is_trigger", default['isTrigger'], targets)
            AbstractDefaultSetter._SetKeyValOnTargets("mel_mesh_collider_convex", default['convex'], targets)
        except BaseException as e:
            print(F" failed to set default {str(e)}")
            print(F"default keys: {default.keys()}")

    @staticmethod
    def OnRemoveKey(key : str, targets):
        AbstractDefaultSetter._RemoveKey("mel_mesh_collider_is_trigger", targets=targets)
        AbstractDefaultSetter._RemoveKey("mel_mesh_collider_convex", targets=targets)


class MeshColliderLike(PropertyGroup, AbstractComponentLike):

    @staticmethod
    def AcceptsKey(key : str):
        return key == MeshColliderLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        mcl = context.scene.meshColliderLike
        row.prop(mcl, "convex", text = "convex")
        row = box.row()
        row.prop(mcl, "isTrigger", text = "isTrigger")

        def getOptionsString(cookingOptions : int) -> str:
            options = { 2 : "Faster Sim" , 4 : "Mesh Cleaning", 8 : "Weld Colocated", 16 : "Fast Midphase"}
            if cookingOptions < 2: 
                return "None"
            if cookingOptions >= 30:
                return "Everything"
            result = ""
            for mask, description in options.items():
                if (mask & (cookingOptions & 31)) > 0:
                    result += F"|{description}"
            return result

        row = box.row()
        row.label(text="cooking options:")

        row = box.row()
        row.prop(mcl, "cookingOptions", text=getOptionsString(mcl.cookingOptions))

        row = box.row()
        row.prop(mcl, "material", text="material")

    @staticmethod
    def GetTargetKey() -> str:
        return "mel_mesh_collider"

    convex : BoolProperty(
        name = "convex",
        default = True,
        get=getConvex,
        set=setConvex)

    isTrigger : BoolProperty(
        name="isTrigger",
        default = False,
        get=getIsTrigger,
        set=setIsTrigger)

    cookingOptions : IntProperty(
        name="cooking_options",
        default=1,
        description="Set cooking options flags. You have to convert binary to decimal yourself, at the moment: add some combination of 2, 4, 8, 16 to set the desired flags. 30 = everything",
        get=lambda self : CLU.getIntFromKey("mel_mesh_collider_cooking_options", default=30),
        set=lambda self, value : CLU.setValueAtKey("mel_mesh_collider_cooking_options", value),
        min=0,
        max=31)
    
    material : StringProperty(
        default="",
        get=lambda self : CLU.getStringFromKey("mel_mesh_collider_material"),
        set=lambda self, value : CLU.setValueAtKey("mel_mesh_collider_material", value)
    )

classes = (
    MeshColliderLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.meshColliderLike = bpy.props.PointerProperty(type=MeshColliderLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.meshColliderLike


#BEAUTIFUL NOTES: please ignore

# TODO: require this to exist for clarity

# This feels much more straight forward -- more like the blender way 
#   the only thing is, its making us rethink the scheme embodied by the ItemKV prop group
#   Seems more wholesome to merely maintain a list of keys that are present on sel ob[s]
#  Knowing how to handle them, could be left to the sub classes...
#  But then again the ItemKV sceme makes it easy to adopt new custom Keys / Value types from a json file
#  Perhaps there's a big divide between keys that MelCustoData knows how to handle and keys it can only 
#    handle in default ways...

# JSON based method
# def getBoolFromSerKey(val_key, component_key):
#     serval = ObjectLookupHelper._getSharedVal(val_key, bpy.context)
#     if serval is None or serval == ObjectLookupHelper._MIXED_():
#         return False
#     try:
#         val = json.loads(serval)
#         result = val[component_key]
#         if isinstance(result, bool) == False:
#             raise "won't ever happen"
#         return result
#     except BaseException as e:
#         print(F"something failed: {str(e)}")
#         return False

# def setBoolWithSerKey(val_key, component_key, value):
#     serval = ObjectLookupHelper._getSharedVal(val_key, bpy.context)
#     if serval is None or serval == ObjectLookupHelper._MIXED_():
#         return
#     obj = json.loads(serval)
#     obj[component_key] = value
#     serialized = json.dumps(obj)
#     ObjectLookupHelper._setValForKeyOnSelected(val_key, bpy.context, serialized)

# kind of hate the json check in out way
#   let's go back to the special keys way. it was wonky and beautiful
#    just need to do a littl special handling when we first add the keys right?
#   or if its multi-selected, not much of a problem...
# plus all that json deserialization on the Unity side could be slow
#  but just make sure you have the means / mechanisms for keeping 
#   the extra custo prop keys in synch with the main key

# def getBoolFromKey(key_name):
#     # CONSIDER: possibly we should show a consensus value of all selected objects?
#     isTrigger = ObjectLookupHelper._getValueFromActive(key_name, bpy.context)
#     if isTrigger is None:
#         return False
#     return isTrigger

# def setBoolAtKey(key_name, value):
#     AbstractDefaultSetter._SetKeyValOnTargets(key_name, value, bpy.context.selected_objects)
#     # ObjectLookupHelper._setValForKeyOnSelected(key_name, bpy.context, value)    
