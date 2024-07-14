
from bb.mcd.ui.componentlike import AbstractDefaultSetter


class ColliderLikeShared:
    IsColliderMarker="mel_is_collider_marker"

    @staticmethod
    def OnAddKey(targets):
        """Based on the honor system, any ComponentLike DefaultSetter that adds a Collider
            should call this method from its own OnAddKey
        """
        AbstractDefaultSetter._SetKeyValOnTargets(ColliderLikeShared.IsColliderMarker, 1, targets)

    @staticmethod
    def OnRemoveKey(targets):
        """And ComponentLike DefaultSetter that adds a Colliders 
            should call this method from its own OnRemoveKey
        """
        AbstractDefaultSetter._RemoveKey(ColliderLikeShared.IsColliderMarker, targets)

    @staticmethod
    def IsCollider(target) -> bool:
        return ColliderLikeShared.IsColliderMarker in target
    