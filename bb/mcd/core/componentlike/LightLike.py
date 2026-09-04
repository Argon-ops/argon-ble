import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       BoolProperty,
                       EnumProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)

from bb.mcd.core.componentlike.AbstractComponentLike import AbstractComponentLike
from bb.mcd.core.componentlike import AbstractDefaultSetter
from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU

# Authoring for Unity's Light component, aimed at baked lighting.
#   Unity's FBX import creates the Light itself (which is what gets the Blender -> Unity
#   rotation right for spots and suns); these keys tell the Argon importer what to overwrite
#   afterwards. Range is authored because it does not survive the FBX trip at all (every light
#   arrives at Unity's default 10).
#
#   Intensity is deliberately NOT authored here: Unity's import passes Blender's wattage
#   straight through to Light.intensity, so the light already arrives at the brightness it was
#   given in Blender. Set the energy on the lamp and it survives. An authored intensity key only
#   ever managed to fight that -- see the removed _intensity below.
_baseKey = "mel_light"

_suffixes = {
    "_mode": 1,          # 0 realtime, 1 baked, 2 mixed
    "_range": 10.0,
    "_shadows": 2,       # 0 none, 1 hard, 2 soft
    "_bounce": 1.0,
}

# Suffixes this component-like used to write and no longer does. Removing the component-like
#   still purges them, so objects authored before the change do not keep a dead key that the
#   importer ignores but the .blend carries forever.
_retiredSuffixes = (
    "_intensity",
)

# Area-light shape and size. Derived rather than authored: these are read straight off the lamp
#   at export time (see Validate), because nothing about an area light's shape or dimensions
#   survives the FBX -- every one of them lands in Unity as a 1x1 Rectangle regardless of what it
#   was in Blender. They are deliberately absent from the panel: a field that silently reverted on
#   every export would be worse than no field. Resize the lamp itself and the export follows.
#
#   Values are written in *Unity's* terms, so the importer stays a dumb apply:
#     _shape   0 = Rectangle, 1 = Disc
#     _size_x  rectangle width, or disc RADIUS  (Blender's disk "size" is a diameter)
#     _size_y  rectangle height; equal to _size_x for a disc, which Unity ignores
_derivedSuffixes = (
    "_shape",
    "_size_x",
    "_size_y",
)

_SHAPE_RECTANGLE = 0
_SHAPE_DISC = 1


def _getSuffixKey(suffix: str) -> str:
    return F"{_baseKey}{suffix}"


def _unityShapeAndSize(lightData):
    """Map a Blender area lamp onto Unity's (shape, sizeX, sizeY), or None if not an area lamp.

    Blender offers four shapes to Unity's two. Square is a rectangle whose sides match, and
    ellipse has no Unity equivalent at all, so it degrades to the disc that best approximates it.
    """
    shape = lightData.shape

    if shape == 'SQUARE':
        return (_SHAPE_RECTANGLE, lightData.size, lightData.size)

    if shape == 'RECTANGLE':
        return (_SHAPE_RECTANGLE, lightData.size, lightData.size_y)

    if shape == 'DISK':
        radius = lightData.size * 0.5
        return (_SHAPE_DISC, radius, radius)

    if shape == 'ELLIPSE':
        # Unity has no elliptical area light. Average the two axes into one disc and say so,
        #   rather than silently picking one of them.
        radius = (lightData.size + lightData.size_y) * 0.25
        print(F"[Argon] mel_light: '{lightData.name}' is an ELLIPSE area light, which Unity cannot "
              F"represent. Exporting it as a Disc of radius {radius:.4f}.")
        return (_SHAPE_DISC, radius, radius)

    print(F"[Argon] mel_light: unrecognised area shape '{shape}' on '{lightData.name}'; "
          "leaving shape and size to Unity's import.")
    return None


class LightDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key: str):
        return LightLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a: object, b: object) -> bool:
        for suffix in _suffixes.keys():
            if not AbstractDefaultSetter._IsEqual(_getSuffixKey(suffix), a, b):
                return False
        return True

    @staticmethod
    def OnAddKey(key: str, val, targets):
        for suffix, defaultVal in _suffixes.items():
            AbstractDefaultSetter._SetKeyValOnTargets(
                _getSuffixKey(suffix), defaultVal, targets)

    @staticmethod
    def OnRemoveKey(key: str, targets):
        for suffix in tuple(_suffixes.keys()) + _retiredSuffixes + _derivedSuffixes:
            AbstractDefaultSetter._RemoveKey(_getSuffixKey(suffix), targets)

    @staticmethod
    def Validate(target):
        """Refresh the derived shape/size keys from the lamp. Called per mel_light object at export.

        Doing this at export rather than on add is what keeps the keys honest: the artist can
        resize or reshape the lamp any number of times and the exported values still match what
        they see in the viewport.
        """
        lightData = getattr(target, "data", None)
        isAreaLamp = getattr(lightData, "type", None) == 'AREA'

        shapeAndSize = _unityShapeAndSize(lightData) if isAreaLamp else None

        if shapeAndSize is None:
            # Point/spot/sun, or a shape we do not understand: carry no shape keys at all, and
            #   clear any left over from when this lamp was an area light.
            AbstractDefaultSetter._RemoveKey(_getSuffixKey("_shape"), [target])
            AbstractDefaultSetter._RemoveKey(_getSuffixKey("_size_x"), [target])
            AbstractDefaultSetter._RemoveKey(_getSuffixKey("_size_y"), [target])
            return

        shape, sizeX, sizeY = shapeAndSize
        AbstractDefaultSetter.SetVal(_getSuffixKey("_shape"), shape, target)
        AbstractDefaultSetter.SetVal(_getSuffixKey("_size_x"), float(sizeX), target)
        AbstractDefaultSetter.SetVal(_getSuffixKey("_size_y"), float(sizeY), target)


class LightLike(PropertyGroup, AbstractComponentLike):

    @staticmethod
    def GetTargetKey() -> str:
        return _baseKey

    @staticmethod
    def AcceptsKey(key: str):
        return key == LightLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        lil = context.scene.lightLike
        box.row().prop(lil, "mode", text="Mode")
        box.row().prop(lil, "range", text="Range")
        box.row().prop(lil, "shadows", text="Shadows")
        box.row().prop(lil, "bounce", text="Bounce Intensity")
        box.row().label(text="Bake needs ContributeGI (mel_static_flags) on the geometry")
        box.row().label(text="Brightness, shape and size come from the lamp itself, at export")

    mode: EnumProperty(
        items=(
            ('0', 'Realtime', 'realtime'),
            ('1', 'Baked', 'baked'),
            ('2', 'Mixed', 'mixed')),
        default='1',
        description="Unity light mode. Nothing in the FBX carries this, so it is always authored here",
        get=lambda self: CLU.getIntFromKey(_getSuffixKey("_mode"), 1),
        set=lambda self, value: CLU.setValueAtKey(_getSuffixKey("_mode"), value)
    )

    range: FloatProperty(
        default=10.0,
        min=0.0,
        description="Unity light range in meters. Authored because range does not survive the FBX trip intact",
        get=lambda self: CLU.getFloatFromKey(_getSuffixKey("_range"), 10.0),
        set=lambda self, value: CLU.setValueAtKey(_getSuffixKey("_range"), value)
    )

    shadows: EnumProperty(
        items=(
            ('0', 'None', 'no shadows'),
            ('1', 'Hard', 'hard shadows'),
            ('2', 'Soft', 'soft shadows')),
        default='2',
        get=lambda self: CLU.getIntFromKey(_getSuffixKey("_shadows"), 2),
        set=lambda self, value: CLU.setValueAtKey(_getSuffixKey("_shadows"), value)
    )

    bounce: FloatProperty(
        default=1.0,
        min=0.0,
        description="Indirect (bounce) multiplier used by the bake",
        get=lambda self: CLU.getFloatFromKey(_getSuffixKey("_bounce"), 1.0),
        set=lambda self, value: CLU.setValueAtKey(_getSuffixKey("_bounce"), value)
    )


classes = (
    LightLike,
)


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Scene.lightLike = bpy.props.PointerProperty(type=LightLike)


def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.lightLike
