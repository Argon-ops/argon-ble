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
from mcd.ui.componentlike.util import ObjectPointerMsgbusUtils as MsgbusUtils
from mcd.ui.componentlike.AbstractPerObjectData import AbstractPerObjectData



# When the prop is assigned an object
#  add a callback to the msgbus. with the target obj as owner


# class OT_PointerTests(bpy.types.Operator):
#     """Tests on obj pointers"""
#     bl_idname = "test.obj_pointers_etc"
#     bl_label = ""
#     bl_description = "a description would go here if there were one"
#     bl_options = {'REGISTER', 'UNDO'}

#     action : StringProperty(
#         name="",
#         default=""
#         )

#     def invoke(self, context, event):
#         return self.execute(context)

#     @classmethod
#     def poll(cls, context):
#         return len(context.selected_objects) > 0

#     def execute(self, context):
#         if self.action == "DELETE":
#             DDeleteFakeProp(context.selected_objects)
#             return {'FINISHED'}
#         if self.action == 'clear_load_post_del_me':
#             from mcd.util import AppHandlerHelper
#             AppHandlerHelper.ClearAllLoadPostHandlers()
#             return {'FINISHED'}
#         DtestCheckFakeProp(context.selected_objects)
#         return {'FINISHED'}

suffixes = {
    "_release_cursor" : True,
    "_hide_root_object" : "",
    "_show_root_object" : "",
}

class CamLockSessionEnableDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return CamLockSessionEnableLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        for key in suffixes.keys():
            if not AbstractDefaultSetter._IsEqual(_Append(key), a, b):
                return False
        return True

    @staticmethod
    def OnAddKey(key : str, val, targets):
        # DtestUseFakePtr(targets)
        pass

    @staticmethod
    def OnRemoveKey(key : str, targets):
        for suffix in suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)
            
        # delete (unset) camLockPerObjectData
        for target in targets:
            target.property_unset("camLockPerObjectData")
            # clp = target.camLockPerObjectData
            # DhideRootWas = clp.hideRootObject
            # clp.property_unset("hideRootObject")
            # # clp.showObjectRoot.property_unset()
            

    @staticmethod
    def IsMultiSelectAllowed() -> bool:
        return False

def _Append(suffix : str) -> str:
    return F"{CamLockSessionEnableLike.GetTargetKey()}{suffix}"

# REGION: msgbus for object pointer properties

from bpy.app.handlers import persistent

@persistent
def resubscribeAllLoadPostCamLock(dummy):
    print(F"cam lock resub load post ^")
    perObjectFieldName = "camLockPerObjectData"

    fieldsAndPropNames = (
        ("hideRootObject", "_hide_root_object"), # for each object PointerProperty that needs updates, add a line here
        ("showRootObject", "_show_root_object"),
    )
    for fieldAndPropName in fieldsAndPropNames:
        MsgbusUtils.resubscribeAll_LP(
            perObjectFieldName, 
            fieldAndPropName[0], 
            _Append(fieldAndPropName[1])) #, 
            # CamLockPerObjectData.OwnerKey(fieldAndPropName[1])) # fieldAndPropName[1])


# add a load post handler so that we resubscribeAll upon loading a new file         
def setupLoadPost():
    from mcd.util import AppHandlerHelper
    AppHandlerHelper.RefreshLoadPostHandler(resubscribeAllLoadPostCamLock) # [resubscribeAllLoadPostCamLock, "resubscribeAllLoadPostCamLock"])

# Since Cam Lock data wants to have object pointer properties
#  it makes sense to store a property group per object...
#  Extended reminder notes below
class CamLockPerObjectData(PropertyGroup, AbstractPerObjectData):
    """Per object cam lock data."""

    hideRootObject : PointerProperty(
        type=bpy.types.Object,
        description="Optional: disable this object and its children at the start of the session. Enable at the end.",
        update=lambda self, context: MsgbusUtils.onObjectUpdate(
            context.active_object,  
            self, 
            "hideRootObject",
            _Append("_hide_root_object"))
            # MsgbusUtils.GetOwnerToken(context.active_object, CamLockPerObjectData.OwnerKey("_hide_root_object"))) 
    )

    showRootObject : PointerProperty(
        type=bpy.types.Object,
        description="Optional: enable this object and its children at the start of the session. Disable at the end.",
        update=lambda self, context: MsgbusUtils.onObjectUpdate(
            context.active_object,
            self,
            "showRootObject",
            _Append("_show_root_object"))
            # MsgbusUtils.GetOwnerToken(context.active_object, CamLockPerObjectData.OwnerKey("_show_root_object")))
    )

#END REGION

from mcd.ui.componentlike.enablefilter.EnableFilterSettings import EnableFilterSettings

class CamLockSessionEnableLike(EnableFilterSettings, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_cam_lock_session_enable"

    @staticmethod
    def AcceptsKey(key : str):
        return key == CamLockSessionEnableLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        mcl = context.scene.camLockSessionEnableLike
        row = box.row()
        row.prop(mcl, "releaseCursor", text="Release Cursor")

        # per object
        target = context.active_object # for now disallow multi select.
        pod = target.camLockPerObjectData
        box.row().prop(pod, "hideRootObject", text="Hide Root")
        box.row().prop(pod, "showRootObject", text="Show Root")

    releaseCursor : BoolProperty(
        description="If true, unlock the cursor during camera lock session",
        get=lambda self: CLU.getBoolFromKey(_Append("_release_cursor"), False),
        set=lambda self, value: CLU.setValueAtKey(_Append("_release_cursor"), value)
    )

 
classes = (
    CamLockSessionEnableLike,
    CamLockPerObjectData,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Object.camLockPerObjectData = bpy.props.PointerProperty(type=CamLockPerObjectData)
    bpy.types.Scene.camLockSessionEnableLike = bpy.props.PointerProperty(type=CamLockSessionEnableLike)

    resubscribeAllLoadPostCamLock(dummy=None)
    setupLoadPost()

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.camLockSessionEnableLike
    del bpy.types.Object.camLockPerObjectData



# REMINDER/GUIDE: how to do PointerProperties to blender Objects (when you need to use their update callbacks):
#  Define a PropertyGroup class that mixin-inherits AbstractPerObjectData (e.g. CamLockPerObjectData)
#   In the class, define some fields that are pointer-properties to objects. 
#    Use the MsgbusUtils.onObjectUpdate as shown in CamLockPerObjectData
#  The goal is to have an object reference that also writes its name to the 
#    owner object's (i.e. selected object's) custom props when the user chooses an object in the picker UI
#    If users never renamed objects this would be simple. But, since they do rename objects,
#       we also need to respond when they rename the pointed-to object. Otherwise the custom props key could
#         become out of sync when/if they rename.
#   So...
#  the onObjectUpdate function does two things: 
#    1. writes the new object's name to a custom props key
#    2. refreshes a msgbus callback to target the newly picked reference object (and remove any no-longer-relevant callbacks.)
#
#  Then...there's a next problem
#    next problem is that these msgbus callbacks don't persist when a new file loads.
#    So define a function (e.g. 'resubscribeAllLoadPost') that iterates over all objects in the scene and checks
#      whether they own a non-None reference to the per object data object. 
#       If they do, refresh the msgbus callback for each field of the object that refers to another object
#            (and that requires custom prop updating).
#     You want this function to get called on file load, so use the AppHandlerHelper.RefreshLoadPostHandlers function
#       providing the function and its name as a string (TODO: just use .__name__ and spare the extra parameter)



# GRAVEYARD DEL ME            
# def resubscribeAll():
#     print(F"resubscribe all")
#     for obj in bpy.context.scene.objects:
#         camlockData = obj.camLockPerObjectData
#         if camlockData.hideRootObject is not None:
#             updateMsgbus(
#                 [obj], 
#                 camlockData.hideRootObject, 
#                 _Append("_hide_root_object"), 
#                 OwnerTokens.GetOrAddToken(camlockData.ownerTokens, "_hide_root_object"))

#NOTES
   
    # Need an object per target-hideRoot pair. i.e. an owner object per target-per variable.
    #   can we use a static dictionary. together with object scoped variables...

    # Alternative, use an object scoped property group? With this scheme...do we need to add a msg_bus? Yes, for re-name.
    #  So in this case...we use the Object pointer 
    #    Basically the same idea, but it might
    #   look more comprehensible? 

    # TODO: hide root object / show root objects
    #  How to msgBus again?? Want to know when object's name changes right?
    #   Keep track of any CamLockSessionLike owners
    #    Subscribe to name changes for::
    #     all objects? Then, just iterate over the owners and re-write their names to the props?
    #  



# def DtestUseFakePtr(targets):
#     assignTest = bpy.context.scene.objects['AssignTest']
#     for target in targets:
#         target.fakePtr = assignTest
#         print(F"assigned {assignTest.name} to {target.name}")
#         target.fakeProp.bar = target.fakeProp.bar + 1

# def msgBusTestCB(*args):
#     target=args[0]
#     assignTest=args[1]
#     print(F"msg bus callback with target: {target.name}. assigned: {assignTest.name}")

# def DtestCheckFakeProp(targets):
#     assignTest = bpy.context.scene.objects['AssignTest']
#     for target in targets:
#         fp = target.fakeProp
#         print(F"bar is: {fp.bar}")
#         fp.bar = fp.bar + 1
#         fp.someObj = assignTest
#         print(F"some obj pos: {fp.someObj.location.x}")
        
#         #msgbus
#         bpy.msgbus.clear_by_owner(target) #clear first

#         bpy.msgbus.subscribe_rna(
#             key=fp.someObj.location,
#             owner=target,
#             args=(target, fp.someObj),
#             notify=msgBusTestCB,
#         )

# def DDeleteFakeProp(targets):
#     for target in targets:
#         target.fakeProp = None # ok. not really deleting


# class Test_PT_AltPattern(PropertyGroup):
#     foo : StringProperty()
#     bar : IntProperty()
#     someObj : PointerProperty(type=bpy.types.Object)

