import bpy
from bpy.props import (CollectionProperty,)

class AbstractPerObjectData(object):

    @classmethod
    def OwnerKey(cls, suffix):
        return F"{cls.__name__}{suffix}"
