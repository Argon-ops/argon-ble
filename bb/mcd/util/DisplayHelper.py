
def _trimMelPrefix(key : str) -> str:
    return key.removeprefix('mel_')

def _drawShowHideTriangle(row, propertyOwner, boolPropertyName : str, boolValue : bool):
    row.prop(propertyOwner, boolPropertyName, 
        icon="TRIA_DOWN" if boolValue else "TRIA_UP",
        icon_only=True, emboss=False)
