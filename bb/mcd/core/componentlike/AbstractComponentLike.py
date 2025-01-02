import bpy


class AbstractComponentLike(object):
    """Handle display of component like key values"""
    @staticmethod
    def AcceptsKey(key: str) -> bool:
        raise "override this func pls"

    @staticmethod
    def Display(box, context) -> None:
        raise "override this func pls"

    @staticmethod
    def GetTargetKey() -> str:
        raise "pls override"

    @classmethod
    def Append(cls, suffix: str) -> str:
        return F"{cls.GetTargetKey()}{suffix}"

    @classmethod
    def HasBaseKey(cls, obj) -> bool:
        return cls.GetTargetKey() in obj

    # COMPLAINT: just calling displayEnableSettings from
    #   each EnableableLike's Display() method is more straight forward. (if you don't
    #     understand this comment, be glad.)
    @classmethod
    def __ProbableSceneInstanceName(cls) -> str:
        """Scene instance name is always class name with lower case first char"""
        return F"{cls.__name__[0].lower()}{cls.__name__[1:]}"

    @classmethod
    def _GetSceneInstanceNonStandardName(cls) -> str:
        return ""

    @classmethod
    def GetSceneInstance(cls):
        """this ugly method relies on our naming convention for component-like instance vars (bpy.types.Scene.particleSystemLike for example)"""
        scn = bpy.context.scene
        if len(cls._GetSceneInstanceNonStandardName()) > 0:
            return getattr(scn, cls._GetSceneInstanceNonStandardName())
        if hasattr(scn, cls.__ProbableSceneInstanceName()):
            return getattr(scn, cls.__ProbableSceneInstanceName())
        raise F"no scene instance found for [{cls.__name__}]"
