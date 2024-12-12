
from bb.mcd.ui.componentlike.enablefilter.EnableFilterSettings import (
    EnableFilterSettings, EnableFilterDefaultSetter)
from bb.mcd.ui.CustomComponentInspector import CustomComponentUtil
from bb.mcd.lookup import KeyValDefault
from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU
from bb.mcd.ui.componentlike import (LightEnableLike, MeshColliderLike, ReplaceWithPrefabLike,
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
                                     SceneObjectsReferencerLike,
                                     )
from bb.mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.ui.componentlike.AbstractDefaultSetter import AbstractDefaultSetter

_components = {
    MeshColliderLike.MeshColliderLike: MeshColliderLike.MeshColliderDefaultSetter,
    StaticFlags.StaticFlagsLike: StaticFlags.StaticFlagsDefaultSetter,
    RigidbodyLike.RigidbodyLike: RigidbodyLike.RigidbodyDefaultSetter,
    OffMeshLinkLike.OffMeshLinkLike: OffMeshLinkLike.OffMeshLinkDefaultSetter,
    BoxColliderLike.BoxColliderLike: BoxColliderLike.BoxColliderDefaultSetter,
    InteractionHandlerLike.InteractionHandlerLike: InteractionHandlerLike.InteractionHandlerDefaultSetter,
    InteractionHighlighterLike.InteractionHighlighterLike: InteractionHighlighterLike.InteractionHighlighterDefaultSetter,
    ParticleSystemLike.ParticleSystemLike: ParticleSystemLike.ParticleSystemDefaultSetter,
    EnableReceiverLike.EnableReceiverLike: EnableReceiverLike.EnableReceiverDefaultSetter,
    ObjectEnableLike.ObjectEnableLike: ObjectEnableLike.ObjectEnableDefaultSetter,
    ScreenOverlayEnableLike.ScreenOverlayEnableLike: ScreenOverlayEnableLike.ScreenOverlayEnableDefaultSetter,
    AudioEnableLike.AudioEnableLike: AudioEnableLike.AudioEnableDefaultSetter,
    SliderColliderLike.SliderColliderLike: SliderColliderLike.SliderColliderDefaultSetter,
    ComponentByNameLike.ComponentByNameLike: ComponentByNameLike.ComponentByNameDefaultSetter,
    SpawnerLike.SpawnerLike: SpawnerLike.SpawnerDefaultSetter,
    CamLockSessionEnableLike.CamLockSessionEnableLike: CamLockSessionEnableLike.CamLockSessionEnableDefaultSetter,
    DisableComponentLike.DisableComponentLike: DisableComponentLike.DisableComponentDefaultSetter,
    TextMeshLike.TextMeshLike: TextMeshLike.TextMeshDefaultSetter,
    LightEnableLike.LightEnableLike: LightEnableLike.LightEnableDefaultSetter,
    VisualEffectLike.VisualEffectLike: VisualEffectLike.VisualEffectDefaultSetter,
    RE2PickSessionLike.RE2PickSessionLike: RE2PickSessionLike.RE2PickSessionDefaultSetter,
    LayerCamLockPickableLike.LayerCamLockPickableLike: LayerCamLockPickableLike.LayerCamLockPickableDefaultSetter,
    DestroyLike.DestroyLike: DestroyLike.DestroyDefaultSetter,
    ForcePCWLike.ForcePCWLike: ForcePCWLike.ForcePCWDefaultSetter,
    PlayableScalarAdapterLike.PlayableScalarAdapterLike: PlayableScalarAdapterLike.PlayableScalarAdapterDefaultSetter,
    SwapMaterialEnableLike.SwapMaterialEnableLike: SwapMaterialEnableLike.SwapMaterialEnableDefaultSetter,
    ReplaceWithPrefabLike.ReplaceWithPrefabLike: ReplaceWithPrefabLike.ReplaceWithPrefabDefaultSetter,
    SceneObjectsReferencerLike.SceneObjectsReferencerLike: SceneObjectsReferencerLike.SceneObjectsReferencerDefaultSetter,
}


def _defaultEquality(key: str, a: object, b: object) -> bool:
    if key in a and key in b:
        return a[key] == b[key]
    return False


def evaluateEqual(key: str, a: object, b: object) -> bool:
    for defaultSetter in _components.values():  # default_setters
        if defaultSetter.AcceptsKey(key):
            return defaultSetter.EqualValues(a, b)
    return _defaultEquality(key, a, b)


def displayItem(key, box, context):
    for componentLike in _components.keys():  # component_likes
        if componentLike.AcceptsKey(key):
            componentLike.Display(box, context)

            if hasattr(componentLike, "IS_ENABLEABLE_CLASS"):
                componentLike.displayEnableSettings(box)
            if hasattr(componentLike, "IS_SLEEPSTATE_CLASS"):
                componentLike.displaySleepSettings(box)

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


def handleRemoveKey(key, context):
    """Delete the key on each appropriate target.

            Call OnRemoveKey callbacks where applicable"""
    targets = _getTargetList(key, context)

    handleRemoveCustom(key, targets)

    # remove the key
    for target in targets:
        if key in target:
            del target[key]

    # let the default setters clean up
    for clc, defaultSetter in _components.items():
        if defaultSetter.AcceptsKey(key):
            defaultSetter.OnRemoveKey(key, targets)

            if hasattr(clc, "IS_ENABLEABLE_CLASS"):
                EnableFilterDefaultSetter.OnRemoveKey(clc, targets)
            if hasattr(clc, "IS_SLEEPSTATE_CLASS"):
                CLU.GenericDefaultSetter.OnRemoveKey(clc, targets)
            break


def handleRemoveCustom(key, targets):
    defaultInfo = KeyValDefault.getDefaultValueInfo(key)
    if defaultInfo.hint != KeyValDefault.EHandlingHint.CUSTOM_COMPONENT:
        return

    data_key = CustomComponentUtil.GetPayloadKey(key)
    apply_key = CustomComponentUtil.GetApplyClassKey(key)
    for target in targets:
        if data_key in target:
            del target[data_key]
        if apply_key in target:
            del target[apply_key]


def handleSetDefaultValue(key, val, context):
    targets = _getTargetList(key, context)
    _setDefaultValueOnTargets(key, val, targets)


def handleSetDefaultsWithKey(key, context):
    targets = _getTargetList(key, context)
    _setDefaultValueOnTargetsWithKey(key, targets)


def _setDefaultValueOnTargetsWithKey(key, targets):
    defaultInfo = KeyValDefault.getDefaultValueInfo(key)

    if defaultInfo.hint == KeyValDefault.EHandlingHint.CUSTOM_COMPONENT:
        _setDefaultValueForCustomComponentType(key, defaultInfo, targets)
        return

    _setDefaultValueOnTargets(key, defaultInfo.default, targets)


def setDefaultValueOnTarget(key, val, target):
    _setDefaultValueOnTargets(key, val, [target])


def _setDefaultValueForCustomComponentType(key, defaultInfo, targets):
    import json
    _setPrimitiveValue(key, 1, targets)
    _setPrimitiveValue(CustomComponentUtil.GetPayloadKey(
        key), json.dumps(defaultInfo.default), targets)
    if defaultInfo.applyClass:
        _setPrimitiveValue(CustomComponentUtil.GetApplyClassKey(
            key), defaultInfo.applyClass, targets)


def _setDefaultValueOnTargets(key, val, targets):
    ''' if a component like handles this key, let the component like module initialize.

            Also check if the component like class needs additional setup: 
                is it an Enableable or a Sleepstate aware class, for example.
        if no component like handles this key, set a primitive value for it
    '''
    for component_like_class, default_setter in _components.items():
        if component_like_class.AcceptsKey(key):
            # make sure the base key is set to something. the default setter can overwrite if it wants
            _setPrimitiveValue(key, val, targets)
            default_setter.OnAddKey(key, val, targets)

            # shared configs for certain classes
            if hasattr(component_like_class, "IS_ENABLEABLE_CLASS"):
                EnableFilterDefaultSetter.OnAddKey(
                    component_like_class, key, targets)
            if hasattr(component_like_class, "IS_SLEEPSTATE_CLASS"):
                CLU.GenericDefaultSetter.OnAddKey(
                    component_like_class, targets)
            return

    # no component-like handles this key. it must be a primitive
    _setPrimitiveValue(key, val, targets)


def _setPrimitiveValue(key, val, targets):
    for target in targets:
        target[key] = val


# # region _components-access

# def getDefaultSetter(componentLikeCls) -> AbstractDefaultSetter:
#     if componentLikeCls not in _components:
#         raise Exception(F"I need a 'component like' class. The thing you passed: {componentLikeCls} wasn't found")
#     return _components[componentLikeCls]

# def getComponentLikes():
#     return _components.keys()

# # endregion
