
def getFocusedItemIndex(context) -> int:
    return context.scene.custom_index 

def getFocusedItem(context):
    try:
        items = context.scene.custom
        idx = getFocusedItemIndex(context)
        if idx < 0:
            return None
        if idx >= len(items):
            return None
        return items[idx]
    except TypeError as te:
        return None

def getFocusedKey(context) -> str:
    item = getFocusedItem(context)
    if item is None:
        return ""
    return item.key

def getFocusedValue(context):
    item = getFocusedItem(context)
    return getattr(item, item.relevant_prop_name)
