
from mcd.ui.componentlike import (MeshColliderLike, 
                                    StaticFlags, 
                                    RigidbodyLike, 
                                    OffMeshLinkLike,
                                    BoxColliderLike,
                                    InteractionHandlerLike,
                                    InteractionHighlighterLike,
                                    ParticleSystemLike,
                                    EnableReceiverLike,
                                    ObjectEnableLike,
                                    ScreenOverlayEnableLike,
                                    AudioEnableLike,
                                    SliderColliderLike,
                                    )


default_setters = [
    MeshColliderLike.MeshColliderDefaultSetter,
    StaticFlags.StaticFlagsDefaultSetter, 
    RigidbodyLike.RigidbodyDefaultSetter,  
    OffMeshLinkLike.OffMeshLinkDefaultSetter, 
    BoxColliderLike.BoxColliderDefaultSetter,
    InteractionHandlerLike.InteractionHandlerDefaultSetter,
    InteractionHighlighterLike.InteractionHighlighterDefaultSetter,
    ParticleSystemLike.ParticleSystemDefaultSetter,
    EnableReceiverLike.EnableReceiverDefaultSetter,
    ObjectEnableLike.ObjectEnableDefaultSetter,
    ScreenOverlayEnableLike.ScreenOverlayEnableDefaultSetter,
    AudioEnableLike.AudioEnableDefaultSetter,
    SliderColliderLike.SliderColliderDefaultSetter,
    ]

component_likes = [
    MeshColliderLike.MeshColliderLike,
    StaticFlags.StaticFlagsLike,
    RigidbodyLike.RigidbodyLike,
    OffMeshLinkLike.OffMeshLinkLike,
    BoxColliderLike.BoxColliderLike,
    InteractionHandlerLike.InteractionHandlerLike,
    InteractionHighlighterLike.InteractionHighlighterLike,
    ParticleSystemLike.ParticleSystemLike,
    EnableReceiverLike.EnableReceiverLike,
    ObjectEnableLike.ObjectEnableLike,
    ScreenOverlayEnableLike.ScreenOverlayEnableLike,
    AudioEnableLike.AudioEnableLike,
    SliderColliderLike.SliderColliderLike,
    ]

def _defaultEquality(key : str, a : object, b : object) -> bool:
    if key in a and key in b:
        return a[key] == b[key]
    return False

def evaluateEqual(key : str, a : object, b : object) -> bool:
    for cl in default_setters:
        if cl.AcceptsKey(key):
            return cl.EqualValues(a, b)
    return _defaultEquality(key, a, b)

def displayItem(key, box, context):
    for component_like in component_likes:
        if component_like.AcceptsKey(key):
            component_like.Display(box, context)
            return True
    return False

def handleRemoveKey(key, targets):
    # remove the key
    for target in targets:
        if key in target:
            del target[key]
    # let the default setters do their own clean up
    for ds in default_setters:
        if ds.AcceptsKey(key):
            ds.OnRemoveKey(key, targets)
            break

def handleSetDefaultValue(key, val, targets):
    for default_setter in default_setters:
        if default_setter.AcceptsKey(key):
            # make sure the base key is set to something. the default setter can overwrite if it wants
            _setPrimitiveValue(key, val, targets) 
            default_setter.OnAddKey(key, val, targets=targets)
            return
    _setPrimitiveValue(key, val, targets=targets)


def _setPrimitiveValue(key, val, targets):
    for target in targets:
        target[key] = val


