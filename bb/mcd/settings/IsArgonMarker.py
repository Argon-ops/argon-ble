import bpy
from bb.mcd.util import ObjectLookupHelper

class IsArgonMarker:

    __IS_ARGON_MARKER_KEY__="mel_is_argon_marker_key"

    @staticmethod
    def PreExport(targetDataHolder):
        IsArgonMarker._PurgePreviousTargetObjects()
        IsArgonMarker._WriteToTargetObject(targetDataHolder)
        IsArgonMarker._SanitizeExport(targetDataHolder)

    @staticmethod
    def _PurgePreviousTargetObjects():
        for previous in ObjectLookupHelper._findAllObjectsWithKey(IsArgonMarker.__IS_ARGON_MARKER_KEY__):
            del previous[IsArgonMarker.__IS_ARGON_MARKER_KEY__]

    @staticmethod
    def _WriteToTargetObject(target):
        target[IsArgonMarker.__IS_ARGON_MARKER_KEY__] = 1

    @staticmethod
    def _SanitizeExport(target):
        configs = ObjectLookupHelper._findAllObjectsWithKey(IsArgonMarker.__IS_ARGON_MARKER_KEY__)
        for config in configs:
            if config != target:
                print(F"IMPOSTER config {config.name} __ real one is {target.name}")
                raise "This will never happen"



