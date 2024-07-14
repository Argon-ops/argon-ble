
class ComponentLikePreExport:

    @staticmethod
    def PreExport(targetDataHolder):
        from bb.mcd.ui.componentlike.router import CLikeToDefaultSetterMap
        from bb.mcd.util import ObjectLookupHelper

        for clike in CLikeToDefaultSetterMap.getComponentLikes(): # StorageRouter.getComponentLikes():
            dfsetter = CLikeToDefaultSetterMap.getDefaultSetter(clike) # StorageRouter.getDefaultSetter(clike)
            if hasattr(dfsetter, "Validate"):
                print(F"will validate {dfsetter}")
                validate = getattr(dfsetter, "Validate")
                obs = ObjectLookupHelper._findAllObjectsWithKey(clike.GetTargetKey())
                for clikeObj in obs: 
                    validate(clikeObj)


