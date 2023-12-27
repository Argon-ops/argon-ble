
from bb.mcd.ui.componentlike import (LightEnableLike, MeshColliderLike, 
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
                                    ComponentByNameLike,
                                    SpawnerLike,
                                    CamLockSessionEnableLike,
                                    DisableComponentLike,
                                    TextMeshLike,
                                    VisualEffectLike,
                                    RE2PickSessionLike,
                                    LayerCamLockPickableLike,
                                    DestroyLike,
                                    ForcePCWLike,
                                    PlayableScalarAdapterLike,
                                    SwapMaterialEnableLike,
                                    )

_components = {
    MeshColliderLike.MeshColliderLike : MeshColliderLike.MeshColliderDefaultSetter,
    StaticFlags.StaticFlagsLike : StaticFlags.StaticFlagsDefaultSetter,
    RigidbodyLike.RigidbodyLike : RigidbodyLike.RigidbodyDefaultSetter,
    OffMeshLinkLike.OffMeshLinkLike : OffMeshLinkLike.OffMeshLinkDefaultSetter,
    BoxColliderLike.BoxColliderLike : BoxColliderLike.BoxColliderDefaultSetter,
    InteractionHandlerLike.InteractionHandlerLike : InteractionHandlerLike.InteractionHandlerDefaultSetter,
    InteractionHighlighterLike.InteractionHighlighterLike : InteractionHighlighterLike.InteractionHighlighterDefaultSetter,
    ParticleSystemLike.ParticleSystemLike : ParticleSystemLike.ParticleSystemDefaultSetter,
    EnableReceiverLike.EnableReceiverLike : EnableReceiverLike.EnableReceiverDefaultSetter,
    ObjectEnableLike.ObjectEnableLike : ObjectEnableLike.ObjectEnableDefaultSetter,
    ScreenOverlayEnableLike.ScreenOverlayEnableLike : ScreenOverlayEnableLike.ScreenOverlayEnableDefaultSetter,
    AudioEnableLike.AudioEnableLike : AudioEnableLike.AudioEnableDefaultSetter,
    SliderColliderLike.SliderColliderLike : SliderColliderLike.SliderColliderDefaultSetter,
    ComponentByNameLike.ComponentByNameLike : ComponentByNameLike.ComponentByNameDefaultSetter,
    SpawnerLike.SpawnerLike : SpawnerLike.SpawnerDefaultSetter,
    CamLockSessionEnableLike.CamLockSessionEnableLike : CamLockSessionEnableLike.CamLockSessionEnableDefaultSetter,
    DisableComponentLike.DisableComponentLike : DisableComponentLike.DisableComponentDefaultSetter,
    TextMeshLike.TextMeshLike : TextMeshLike.TextMeshDefaultSetter,
    LightEnableLike.LightEnableLike : LightEnableLike.LightEnableDefaultSetter,
    VisualEffectLike.VisualEffectLike : VisualEffectLike.VisualEffectDefaultSetter,
    RE2PickSessionLike.RE2PickSessionLike : RE2PickSessionLike.RE2PickSessionDefaultSetter,
    LayerCamLockPickableLike.LayerCamLockPickableLike : LayerCamLockPickableLike.LayerCamLockPickableDefaultSetter,
    DestroyLike.DestroyLike : DestroyLike.DestroyDefaultSetter,
    ForcePCWLike.ForcePCWLike : ForcePCWLike.ForcePCWDefaultSetter,
    PlayableScalarAdapterLike.PlayableScalarAdapterLike : PlayableScalarAdapterLike.PlayableScalarAdapterDefaultSetter,
    SwapMaterialEnableLike.SwapMaterialEnableLike : SwapMaterialEnableLike.SwapMaterialEnableDefaultSetter,
}

from bb.mcd.ui.componentlike.enablefilter.EnableFilterSettings import (EnableFilterSettings, EnableFilterDefaultSetter) 
from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU

def _defaultEquality(key : str, a : object, b : object) -> bool:
    if key in a and key in b:
        return a[key] == b[key]
    return False

def evaluateEqual(key : str, a : object, b : object) -> bool:
    for cl in _components.values(): # default_setters:
        if cl.AcceptsKey(key):
            return cl.EqualValues(a, b)
    return _defaultEquality(key, a, b)

def displayItem(key, box, context):
    for component_like in _components.keys(): #  component_likes:
        if component_like.AcceptsKey(key):
            component_like.Display(box, context)

            if hasattr(component_like, "IS_ENABLEABLE_CLASS"):
                component_like.displayEnableSettings(box)
            if hasattr(component_like, "IS_SLEEPSTATE_CLASS"):
                component_like.displaySleepSettings(box)
                
            return True
    return False

# REMINDER: multi select is complicated if we need object references. (Example: CamLockPerObjectData) #unfortunately just disallow it in these cases
def _isMultiSelectAllowed(key):
    for ds in _components.values(): 
        if ds.AcceptsKey(key):
            return ds.IsMultiSelectAllowed()
    return True

def _getTargetList(key, context):
    return context.selected_objects if _isMultiSelectAllowed(key) else [context.active_object]

def handleRemoveKey(key, context): # target_list):
    targets = _getTargetList(key, context)

    # remove the key
    for target in targets:
        if key in target:
            del target[key]

    # let the default setters clean up
    for clc, default_setter in _components.items(): 
        if default_setter.AcceptsKey(key):
            default_setter.OnRemoveKey(key, targets)
            # if issubclass(clc, EnableFilterSettings):
            if hasattr(clc, "IS_ENABLEABLE_CLASS"): 
                EnableFilterDefaultSetter.OnRemoveKey(clc, targets)
            if hasattr(clc, "IS_SLEEPSTATE_CLASS"):
                CLU.GenericDefaultSetter.OnRemoveKey(clc, targets)
            break

def handleSetDefaultValue(key, val, context): # targets):
    targets = _getTargetList(key, context)

    for component_like_class, default_setter in _components.items(): 

        if component_like_class.AcceptsKey(key):

            # make sure the base key is set to something. the default setter can overwrite if it wants
            _setPrimitiveValue(key, val, targets) # target_list) 
            default_setter.OnAddKey(key, val, targets) #=target_list)
            if hasattr(component_like_class, "IS_ENABLEABLE_CLASS"): # issubclass(component_like_class, EnableFilterSettings):
                EnableFilterDefaultSetter.OnAddKey(component_like_class, key, targets)
            if hasattr(component_like_class, "IS_SLEEPSTATE_CLASS"):
                CLU.GenericDefaultSetter.OnAddKey(component_like_class, targets)
            return
    _setPrimitiveValue(key, val, targets) 

def _setPrimitiveValue(key, val, targets):
    for target in targets:
        target[key] = val


