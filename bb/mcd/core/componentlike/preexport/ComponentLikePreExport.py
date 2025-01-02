
class ComponentLikePreExport:

    @staticmethod
    def PreExport(targetDataHolder):
        from bb.mcd.core.componentlike.router import CLikeToDefaultSetterMap
        from bb.mcd.util import ObjectLookupHelper

        for clike in CLikeToDefaultSetterMap.getComponentLikes():
            dfsetter = CLikeToDefaultSetterMap.getDefaultSetter(clike)
            if hasattr(dfsetter, "Validate"):
                validate = getattr(dfsetter, "Validate")
                obs = ObjectLookupHelper._findAllObjectsWithKey(
                    clike.GetTargetKey())
                for clikeObj in obs:
                    validate(clikeObj)
