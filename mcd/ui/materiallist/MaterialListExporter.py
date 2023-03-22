import bpy

from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty,
                       PointerProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)
import json

from mcd.ui.materiallist import MaterialList
from bpy_extras.io_utils import ExportHelper

def getJSON(context):
    itemLookup = MaterialList.MaterialMapToDictionary(context)
    return json.dumps(itemLookup)

def write_some_data(context, filepath):
    print("running write_some_data...")
    jsonItems = getJSON(context)
    print(F"here's the data {jsonItems}")
    f = open(filepath, 'w', encoding='utf-8')
    f.write(jsonItems)
    # f.write("Hello World %s" % use_some_setting)
    f.close()

class CDU_OT_MaterialListExporter(Operator, ExportHelper):
    """Add key to all selected objects"""
    bl_idname = "cdu.exportmateriallist"
    bl_label = "Export material list"
    bl_description = "Export a material list to JSON"
    bl_options = {'REGISTER', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def invoke(self, context, event):
        print(F"invoke for addKeyToSel")
        return self.execute(context)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        raise BaseException("this works but don't use it. just bundle the material map with the fbx. thnx")
        self.filepath = "E:\\unities\\TestMicroFPS\\Assets\\Mazer\\blender_tool\\MelCustomDataUtilBA\\src\\demo\\"
        write_some_data(context, self.filepath)
        print(F"execute ExportMatList this file path: {self.filepath}")
        return {'FINISHED'}


def register():
    from bpy.utils import register_class
    register_class(CDU_OT_MaterialListExporter)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(CDU_OT_MaterialListExporter)