# import bpy
# from bpy.props import (IntProperty,
#                        FloatProperty,
#                        StringProperty,
#                        BoolProperty,
#                        CollectionProperty,
#                        PointerProperty)
# from bpy.types import (PropertyGroup,)
# from bb.mcd.util import ObjectLookupHelper
# import os


# def _unityProjectRootUpdated(self, context):
#     try:
#         with open(bpy.path.abspath(self.file_path)) as json_file:
#             data = json.load(json_file)
#             current_data.update(data)
#     except:
#         print("not a json file apparently: ", self.file_path)

# def _getPR(self):
#     stor = bpy.context.scene.unityProjectRootStor.path
#     if not stor:
#         last_props = bpy.context.window_manager.operator_properties_last('export_scene.fbx')
#         if 'filepath' in last_props:
#             stor = bpy.path.abspath(last_props['filepath'])
#     return stor

# def _setPR(self, value):
#     stor = bpy.context.scene.unityProjectRootStor
#     stor.path = os.path.normpath(bpy.path.abspath(value))

# class UnityProjectRootStor(PropertyGroup):
#     path : StringProperty(
#         name="path",
#         subtype="FILE_PATH",
#         )

# class UnityProjectRoot(PropertyGroup):
#     """append properties from a JSON file"""
#     file_path: bpy.props.StringProperty(
#         name="append",
#         description="Set this to enable project specific help",
#         default="",
#         subtype="FILE_PATH",
#         get=_getPR,
#         set=_setPR,
#         update=_unityProjectRootUpdated)


# classes=(
#     UnityProjectRoot,
#     UnityProjectRootStor,
#     )

# def register():
#     from bpy.utils import register_class
#     for c in classes:
#         register_class(c)
    
#     bpy.types.Scene.unityProjectRoot = PointerProperty(type=UnityProjectRoot)
#     bpy.types.Scene.unityProjectRootStor = PointerProperty(type=UnityProjectRootStor)

# def unregister():
#     from bpy.utils import unregister_class
#     for c in classes:
#         unregister_class(c)

#     del bpy.types.Scene.unityProjectRoot
#     del bpy.types.Scene.unityProjectRootStor