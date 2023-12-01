import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,
                       PointerProperty,
                       FloatVectorProperty,
                       IntVectorProperty,
                       BoolVectorProperty,
                       EnumProperty)
from bpy.types import (PropertyGroup,)
from mcd.util import ObjectLookupHelper

# TODO: red button: export with no dialogue

from mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
from mcd.ui.componentlike import AbstractDefaultSetter
from mcd.ui.componentlike.util import ComponentLikeUtils as CLU
from mcd.ui.componentlike.util import UnderscoreUtils   

_baseKey="mel_text_mesh"

_suffixes = {
    "_content" : "",
    "_character_size" : .1,
    "_font_size" : 32,
    "_color" : [1.0, 1.0, 1.0, 1.0],
    "_enable_radius": 16,
    "_use_tmpro" : False,
    "_wrapping" : False,
    "_overflow" : 0,
    }

def _Append(suffix : str) -> str:
    return F"{_baseKey}{suffix}"


class TextMeshDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):
    @staticmethod
    def AcceptsKey(key : str):
        return TextMeshLike.AcceptsKey(key)

    @staticmethod
    def EqualValues(a : object, b : object) -> bool:
        for suffix in _suffixes.keys():
            if not AbstractDefaultSetter._IsEqual(_Append(suffix), a, b):
                return False
        return True

    @staticmethod
    def OnAddKey(key : str, val, targets):
        for suffix, defaultVal in _suffixes.items():
            print(F"{suffix} set {defaultVal} ")
            AbstractDefaultSetter._SetKeyValOnTargets(_Append(suffix), defaultVal, targets)

    @staticmethod
    def OnRemoveKey(key : str, targets):
        for suffix in _suffixes.keys():
            AbstractDefaultSetter._RemoveKey(_Append(suffix), targets=targets)


class TextMeshLike(PropertyGroup, AbstractComponentLike):

    @staticmethod
    def AcceptsKey(key : str):
        return key == TextMeshLike.GetTargetKey()

    @staticmethod
    def Display(box, context) -> None:
        oml = context.scene.textMeshLike
        box.row().prop(oml, "content", text="Text")
        # box.row().prop(oml, "fontName", text="Font (Optional)")
        box.row().prop(oml, "fontSize", text="Font Size")
        box.row().prop(oml, "useTMPro", text="Text Mesh Pro")
        if not oml.useTMPro:
            box.row().prop(oml, "characterSize", text="Character Size")
            box.row().prop(oml, "anchor", text="Anchor")
            box.row().prop(oml, "alignment", text="Alignment")
            box.row().prop(oml, "offsetZ", text="Offset Z")
        else:
            box.row().prop(oml, "wrapping")
            box.row().prop(oml, "overflow")
            box.row().prop(oml, "horizontalAlignment")
            box.row().prop(oml, "verticalAlignment")
            
        box.row().prop(oml, "useProximityEnable", text="Enable Only When Nearby")
        if oml.useProximityEnable:
            box.row().prop(oml, "enableRadius", text="Enable Radius")
        box.row().prop(oml, "alwaysFaceCamera", text="Always Face Camera")

        if not oml.alwaysFaceCamera:
            box.row().prop(oml, "rotateDegreesY", text="Rotate Degrees Y")
        box.row().prop(oml, "color", text="Color")

    @staticmethod
    def GetTargetKey() -> str:
        return _baseKey 
    
    content : StringProperty(
        description="defines the text to display",
        get=lambda self : CLU.getStringFromKey(_Append("_content")),
        set=lambda  self, value : CLU.setValueAtKey(_Append("_content"), value)
    )

    #
    #  Unfortunately switching fonts in editor in TMPro is non trivial
    #   Users can just set the TMProFont Asset manually in the editor. The import won't 
    #     overwrite overrides
    #
    # fontName : StringProperty(
    #     description="(Optional) Defines the font name.",
    #     get=lambda self : CLU.getStringFromKey(_Append("_font_name")),
    #     set = lambda self, value : CLU.setValueAtKey(_Append("_font_name"), value)
    # )

    alwaysFaceCamera : BoolProperty(
        get=lambda self : CLU.getBoolFromKey(_Append("_always_face_camera")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_always_face_camera"), value)
    )

    useProximityEnable : BoolProperty(
        description="Enable when the player gets close to this game object",
        get=lambda self : CLU.getBoolFromKey(_Append("_use_proximity_enable")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_use_proximity_enable"), value)
    )



    # offset : FloatVectorProperty(
    #     description="Defines how far to move the text away from its anchor position. Scales with renderer or collider bounds where possible",
    #     get=lambda self : CLU.getFloatArrayFromKey(_Append("_offset")),
    #     set=lambda self, value : CLU.setValueAtKey(_Append("_offset"), value),
    #     soft_min=-3.0,
    #     soft_max=3.0,
    # )

    enableRadius : FloatProperty(
        description="Become visible when the player is within this distance.",
        get=lambda self : CLU.getFloatFromKey(_Append("_enable_radius"), 16.0),
        set=lambda self, value : CLU.setValueAtKey(_Append("_enable_radius"), value),
        soft_min=0.0,
    )

    offsetZ : FloatProperty(
        get=lambda self : CLU.getFloatFromKey(_Append("_offset_z")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_offset_z"))
    )

    characterSize : FloatProperty(
        description="Smaller values correspond to sharper text meshes. 1 will look pixelated",
        get=lambda self : CLU.getFloatFromKey(_Append("_character_size"), .1),
        set=lambda self, value : CLU.setValueAtKey(_Append("_character_size"), value),
        soft_min=0.01,
        soft_max=3.0,
    )

    alignment : EnumProperty(
        items=(
            ('Left', 'Left', 'Left'),
            ('Center', 'Center', 'Center'),
            ('Right', 'Right', 'Right'),
        ),
        get=lambda self : CLU.getIntFromKey(_Append("_alignment")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_alignment"), value)
    )

    anchor : EnumProperty(
        items=(
            ('Upper left','Upper left','Upper left'),
            ('Upper center','Upper center','Upper center'),
            ('Upper right','Upper right','Upper right'),
            ('Middle left','Middle left','Middle left'),
            ('Middle center','Middle center','Middle center'),
            ('Middle right','Middle right','Middle right'),
            ('Lower left','Lower left','Lower left'),
            ('Lower center','Lower center','Lower center'),
            ('Lower right','Lower right','Lower right'),
        ),
        get=lambda self : CLU.getIntFromKey(_Append("_anchor")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_anchor"), value)
    )

    fontSize : FloatProperty(
        get=lambda self : CLU.getIntFromKey(_Append("_font_size"), 32),
        set=lambda self, value : CLU.setValueAtKey(_Append("_font_size"), value),
        soft_min=0,
    )

    # TODO: add the other suffixes

    color : FloatVectorProperty(
        subtype='COLOR_GAMMA',
        # default=[1.0,1.0,1.0,1.0], # blender doesn't seem to respect this default; maybe b/c of the getter.
        get=lambda self : CLU.getFloat4ArrayFromKey(_Append("_color")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_color"), value),
        size=4,
        min=0.0, 
        max=1.0,
    )

    useTMPro : BoolProperty(
        description="Use TextMeshPro to render text if true (Requires the UnityEngine.TextMeshPro package)",
        get=lambda self : CLU.getBoolFromKey(_Append("_use_tmpro")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_use_tmpro"), value)
    )

    wrapping : BoolProperty(
        get=lambda self : CLU.getBoolFromKey(_Append("_wrapping")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_wrapping"), value)
    )

    overflow : EnumProperty(
        items=(
            ("Overflow","Overflow","Overflow"),
            ("Ellipsis","Ellipsis","Ellipsis"),
            ("Masking","Masking","Masking"),
            ("Truncate","Truncate","Truncate"),
            ("Scroll Rect","Scroll Rect","Scroll Rect"),
            ("Page","Page","Page"),
            ("Linked","Linked","Linked")
        ),
        get=lambda self : CLU.getIntFromKey(_Append("_overflow")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_overflow"), value)
    )
    horizontalAlignment : EnumProperty(
        items=(
            ("Left", "Left", "Left" ),
            ("Center", "Center", "Center" ),
            ("Right", "Right", "Right"),
            ("Justified", "Justified", "Justified"),
            ("Flush", "Flush", "Flush"),
            ("Geometry", "Geometry", "Geometry"),
        ),
        get=lambda self : CLU.getIntFromKey(_Append("_horizontal_alignment")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_horizontal_alignment"), value)
    )
    verticalAlignment : EnumProperty(
        items=(
            ("Top", "Top", "Top" ),
            ("Middle", "Middle", "Middle" ),
            ("Bottom", "Bottom", "Bottom"),
            ("Baseline", "Baseline", "Baseline"),
            ("Geometry", "Geometry", "Geometry"),
            ("Capline", "Capline", "Capline"),
        ),
        get=lambda self : CLU.getIntFromKey(_Append("_vertical_alignment")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_vertical_alignment"), value)
    )
    rotateDegreesY : FloatProperty(
        description="Defines how far in degrees to rotate the text around the (Unity) Y axis",
        get=lambda self : CLU.getFloatFromKey(_Append("_rotate_degrees_y")),
        set=lambda self, value : CLU.setValueAtKey(_Append("_rotate_degrees_y"), value)
    )


classes = (
    TextMeshLike,
    )

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    
    bpy.types.Scene.textMeshLike = bpy.props.PointerProperty(type=TextMeshLike)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

    del bpy.types.Scene.textMeshLike