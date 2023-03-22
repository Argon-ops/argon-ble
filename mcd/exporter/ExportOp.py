# import bpy
# from bpy.props import StringProperty, BoolProperty, EnumProperty
# from bpy.types import Operator
# from mcd.exporter.default import DefaultFBXExporter
# from mcd.exporter.edyj import BlenderToUnityFbxExporter
# from mcd.util import DisplayHelper
# from mcd.shareddataobject import SharedDataObject
from mcd.ui.actionstarterlist import CUSTOM_PG_AS_Collection

#TODO: we're getting too many animations exported
#  for each action the action applies to more animations than we intended
#  Propose a bandaid for this: send Unity a look up with each objects animation data
#   (since it seems like the animations listed per object are the 'real' ones that we intended)

def PreExport(context):
    """Make sure that everything is ready to be exported
        
        Ideally we wouldn't need this but some data (playables) exists
         as a list that doesn't read directly from a custom property. 
         This makes sure that the custom property for each playable reflects 
          the state of the playables list.
        UNFORTUNATELY: this means the client has to use our export button;
           can't use the vanilla fbx exporter directly.
    """
    print(F"Pre export get things straightened out here")
    CUSTOM_PG_AS_Collection.syncPlayables()
    from mcd.objectinfo import ObjectInfo
    ObjectInfo.writeObjectInfo(context)
