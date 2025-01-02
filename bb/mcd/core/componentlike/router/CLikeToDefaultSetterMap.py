from bb.mcd.core.componentlike.AbstractDefaultSetter import AbstractDefaultSetter
from bb.mcd.core.componentlike.StorageRouter import _components # rude

# region _components-access
        
def getDefaultSetter(componentLikeCls) -> AbstractDefaultSetter:
    if componentLikeCls not in _components:
        raise Exception(F"I need a 'component like' class. The thing you passed: {componentLikeCls} wasn't found")
    return _components[componentLikeCls]

def getComponentLikes():
    return _components.keys()

# endregion
