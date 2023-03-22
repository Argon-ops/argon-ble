import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)

class AbstractComponentLike(object):
    """Handle display of component like key values"""
    @staticmethod
    def AcceptsKey(key : str) -> bool:
        raise "override this func pls"

    @staticmethod
    def Display(box, context) -> None:
        raise "override this func pls"

    @staticmethod
    def GetTargetKey() -> str:
        raise "pls override"

    @classmethod
    def Append(cls, suffix : str) -> str:
        return F"{cls.GetTargetKey()}{suffix}"
