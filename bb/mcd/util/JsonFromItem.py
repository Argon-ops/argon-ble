
def _parseJSONProperty(item):
    val = getattr(item, item.relevant_prop_name)
    if isinstance(val, str) == False:
        return None
    if len(val) == 0:
        return None
    import json
    try:
        return json.loads(val)
    except BaseException as e:
        print(F"parse json failed {e}")
        return None
