import bpy
from bpy.props import (CollectionProperty,)

# from bb.mcd.ui.componentlike.util.ObjectPointerMsgbusUtils import OwnerTokens

class AbstractPerObjectData(object):

    @classmethod
    def OwnerKey(cls, suffix):
        return F"{cls.__name__}{suffix}"

    # ownerTokens : CollectionProperty(
    #     type=OwnerTokens
    # )