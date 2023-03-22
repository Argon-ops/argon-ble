from mcd.lookup import KeyValDefault

def _RemoveKey(key : str, targets):
    for target in targets:
        if key in target:
            del target[key]
            print(F"rm {key} from {target.name}")
            continue
        print(F"key {key} NOT in {target.name}")

def _GetDefaultFromPrefs(key : str):
    return KeyValDefault.getDefaultValue(key)

def _SetKeyValOnTargets(key : str, val, targets):
    for target in targets:
        target[key] = val

def _IsEqual(key : str, a : object, b : object) -> bool:
    if key in a and key in b:
        return a[key] == b[key]
    return False

class AbstractDefaultSetter():
    @staticmethod
    def AcceptsKey(key : str) -> bool:
        raise "override me pls"

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        raise "pls override this method"

    @staticmethod
    def OnAddKey(key : str, val, targets) -> None:
        """Handle any and all set up when the base key is added to object(s)"""
        raise "override me"

    @staticmethod
    def OnRemoveKey(key : str, targets) -> None:
        raise "override me"