# # TO start with: just gets the name of an animation action
# #   around which we can build an ActionStarterBehaviour
# #  Later, we'll add associating a sound with the behviour
# #  Later still, design a user-friendly way to
# #    chain ActionStarters (or chain the abstract command things that they work with)

# import bpy
# from bpy.props import (IntProperty,
#                        FloatProperty,
#                        StringProperty,
#                        BoolProperty,
#                        CollectionProperty,)
# from bpy.types import (PropertyGroup,)
# from mcd.util import ObjectLookupHelper

# from mcd.ui.componentlike.AbstractComponentLike import AbstractComponentLike
# from mcd.ui.componentlike import AbstractDefaultSetter
# from mcd.ui.componentlike.util import ComponentLikeUtils as CLU

# def _append(suffix : str) -> str:
#     return F"{ActionStarterLike.GetTargetKey()}{suffix}"

# class ActionStarterDefaultSetter(AbstractDefaultSetter.AbstractDefaultSetter):

#     @staticmethod
#     def AcceptsKey(key : str):
#         return ActionStarterLike.AcceptsKey(key)

#     @staticmethod
#     def EqualValues(a : object, b : object) -> bool:
#         return AbstractDefaultSetter._IsEqual(_append("_anim_name"), a, b) 

#     @staticmethod
#     def OnAddKey(key : str, val, targets):
#         default = AbstractDefaultSetter._GetDefaultFromPrefs(key)
#         try:
#             AbstractDefaultSetter._SetKeyValOnTargets(_append("_anim_name"), default['animName'], targets)
#         except BaseException as e:
#             print(F" failed to set default {str(e)}")
#             print(F"default keys: {default.keys()}")

#     @staticmethod
#     def OnRemoveKey(key : str, targets):
#         AbstractDefaultSetter._RemoveKey(_append("_anim_name"), targets=targets)

# # TODO: this needs to be its own section alla MaterialList
# #   a list of action-starter-configs
# #   The ui provides an option to add all animations
# #   or (+) to add a specific animation
# #  anytime there's a change to the config list: write it to JSON to the sharedDataObject
# #   then on the csharp side we can unpack it and make it available however necessary.

# class ActionStarterLike(PropertyGroup, AbstractComponentLike):
#     @staticmethod
#     def AcceptsKey(key : str):
#         return key == ActionStarterLike.GetTargetKey()

#     @staticmethod
#     def Display(box, context) -> None:
#         mcl = context.scene.actionStarterLike
#         row = box.row()
#         row.prop(mcl, "animName", text = "animation name")

#     @staticmethod
#     def GetTargetKey() -> str:
#         return "mel_action_starter"

#     animName : StringProperty(
#         name="animName",
#         get=lambda self : CLU.getStringFromKey(_append("_anim_name")),
#         set=lambda self, value : CLU.setValueAtKey(_append("_anim_name"), value)
#     )
#     audioName : StringProperty(
#         name="audioName",
#         description="optional: specify the name of an audio clip in your project if audio is required",
#         get=lambda self : CLU.getStringFromKey(_append("_audio_name")),
#         set=lambda self, value : CLU.setValueAtKey(_append("_audio_name"), value)
#     )


# classes = (
#     ActionStarterLike,
#     )

# def register():
#     from bpy.utils import register_class
#     for c in classes:
#         register_class(c)
    
#     bpy.types.Scene.actionStarterLike = bpy.props.PointerProperty(type=ActionStarterLike)

# def unregister():
#     from bpy.utils import unregister_class
#     for c in classes:
#         unregister_class(c)

#     del bpy.types.Scene.actionStarterLike

