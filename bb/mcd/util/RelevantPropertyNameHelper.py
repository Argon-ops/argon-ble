

def _getPropNameForType(value):
    if isinstance(value, float):
        return "vfloat"
    elif isinstance(value, str):
        return "val"
    return "vint"