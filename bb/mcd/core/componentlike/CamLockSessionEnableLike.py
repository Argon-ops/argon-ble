from bb.mcd.core.componentlike.enablefilter.EnableFilterSettings import EnableFilterSettings
from bpy.app.handlers import persistent
import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)

from bb.mcd.util import ObjectLookupHelper
from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU
from bb.mcd.core.componentlike.util import ObjectPointerMsgbusUtils as MsgbusUtils
from bb.mcd.core.componentlike.AbstractPerObjectData import AbstractPerObjectData


# When the prop is assigned an object
#  add a callback to the msgbus. with the target obj as owner


suffixes = {
    "_release_cursor": True,
    "_hide_root_object": "",
    "_show_root_object": "",
    "_disable_camera": True,
}


class CamLockSessionEnableDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key: str):
        return CamLockSessionEnableLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a: object, b: object) -> bool:
        for key in suffixes.keys():
            if not AbstractDefaultSetter._IsEqual(_Append(key), a, b):
                return False
        return True

    @staticmethod
    def OnAddKey(key: str, val, targets):
        pass

    @staticmethod
    def OnRemoveKey(key: str, targets):
        for suffix in suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets)

        # delete (unset) camLockPerObjectData
        for target in targets:
            target.property_unset("camLockPerObjectData")

    @staticmethod
    def IsMultiSelectAllowed() -> bool:
        return False


def _Append(suffix: str) -> str:
    return F"{CamLockSessionEnableLike.GetTargetKey()}{suffix}"

# region: msgbus for object pointer properties


@persistent
def resubscribeAllLoadPostCamLock(dummy):
    # print(F"== cam lock resub load post ==")
    perObjectFieldName = "camLockPerObjectData"

    fieldsAndPropNames = (
        # for each object PointerProperty that needs updates, add a line here
        ("hideRootObject", "_hide_root_object"),
        ("showRootObject", "_show_root_object"),
    )
    for fieldAndPropName in fieldsAndPropNames:
        MsgbusUtils.resubscribeAll_LP(
            perObjectFieldName,
            fieldAndPropName[0],
            _Append(fieldAndPropName[1]))  # ,
        # CamLockPerObjectData.OwnerKey(fieldAndPropName[1])) # fieldAndPropName[1])


# add a load post handler so that we resubscribeAll upon loading a new file
def setupLoadPost():
    from bb.mcd.util import AppHandlerHelper
    # [resubscribeAllLoadPostCamLock, "resubscribeAllLoadPostCamLock"])
    AppHandlerHelper.RefreshLoadPostHandler(resubscribeAllLoadPostCamLock)


class CamLockPerObjectData(PropertyGroup, AbstractPerObjectData):
    """Per object cam lock data."""

    hideRootObject: PointerProperty(
        type=bpy.types.Object,
        description="Optional: disable this object and its children at the start of the session. Enable at the end.",
        update=lambda self, context: MsgbusUtils.onObjectUpdate(
            context.active_object,
            self,
            "hideRootObject",
            _Append("_hide_root_object"))
        # MsgbusUtils.GetOwnerToken(context.active_object, CamLockPerObjectData.OwnerKey("_hide_root_object")))
    )

    showRootObject: PointerProperty(
        type=bpy.types.Object,
        description="Optional: enable this object and its children at the start of the session. Disable at the end.",
        update=lambda self, context: MsgbusUtils.onObjectUpdate(
            context.active_object,
            self,
            "showRootObject",
            _Append("_show_root_object"))
        # MsgbusUtils.GetOwnerToken(context.active_object, CamLockPerObjectData.OwnerKey("_show_root_object")))
    )

# END REGION


class CamLockSessionEnableLike(EnableFilterSettings, AbstractComponentLike):
    @staticmethod
    def GetTargetKey() -> str:
        return "mel_cam_lock_session_enable"

    @staticmethod
    def AcceptsKey(key: str):
        return key == CamLockSessionEnableLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        row = box.row()
        mcl = context.scene.camLockSessionEnableLike
        row = box.row()
        row.prop(mcl, "releaseCursor", text="Release Cursor")
        box.row().prop(mcl, "disableCamera", text="Disable Camera During Import")

        # per object
        target = context.active_object  # for now disallow multi select.
        pod = target.camLockPerObjectData
        box.row().prop(pod, "hideRootObject", text="Hide Root")
        box.row().prop(pod, "showRootObject", text="Show Root")
        

    releaseCursor: BoolProperty(
        description="If true, unlock the cursor during camera lock session",
        get=lambda self: CLU.getBoolFromKey(_Append("_release_cursor"), False),
        set=lambda self, value: CLU.setValueAtKey(
            _Append("_release_cursor"), value)
    )

    disableCamera: BoolProperty(
        description="If true, the Camera component will be disabled during import",
        get=lambda self: CLU.getBoolFromKey(_Append("_disable_camera"), False),
        set=lambda self, value: CLU.setValueAtKey(_Append("_disable_camera"), value)
    )


classes = (
    CamLockSessionEnableLike,
    CamLockPerObjectData,
)


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Object.camLockPerObjectData = bpy.props.PointerProperty(
        type=CamLockPerObjectData)
    bpy.types.Scene.camLockSessionEnableLike = bpy.props.PointerProperty(
        type=CamLockSessionEnableLike)


def defer():
    resubscribeAllLoadPostCamLock(dummy=None)
    setupLoadPost()


def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.camLockSessionEnableLike
    del bpy.types.Object.camLockPerObjectData
