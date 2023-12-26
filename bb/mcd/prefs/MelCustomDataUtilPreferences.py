import bpy
from bpy.props import (CollectionProperty, 
                        StringProperty, 
                        FloatProperty, 
                        IntProperty)
from bpy.types import (AddonPreferences, 
                        PropertyGroup)
import json

class CUSTOM_PG_PrefsKV(PropertyGroup):
    """ Key value type for use with prefs. 
    
        Duplicates the fields in CUSTOM_PG_KeyValItem.
        But without the val/vint/vfloat getter and setter functions """

    # CONSIDER: can a property group own another property group?
    #  So we could define a PG_MultiType? In this way, we'd remove
    #   the duplicate code? The MultiType decides what type exists and HOW one could read/write them (to an object)
    #    This class and its sibling KeyValItem class decide WHETHER to read/write them??? 
    #  BASICALLY feels like we need deeper knowledge of the question 'what are prop group getters and setters'.
    #    do 'getters and setters' change the location where data is stored? 
    #   Also, deeper knowledge of what Blender can store and persist as a pref
    
    key: StringProperty(
        name="key",
        default="")
    val: StringProperty(
        name="val",
        default="")
    vint : IntProperty(
        name="vint",
        default=0)
    vfloat : FloatProperty(
        name="vfloat",
        default=0.0)
    relevant_prop_name : StringProperty(
        name="type-index",
        default="val")

def _getPrefsFromJSON(file_path):
    try:
        with open(bpy.path.abspath(file_path)) as json_file:
            data = json.load(json_file)
            return data
    except:
        print("not a json file apparently: ", file_path)

def _onPrefsFileUpdated(self, context):
    kv_data = _getPrefsFromJSON(self.filepath)
    # reset our list
    self.custom.clear() 
    for key, val in kv_data.items():
        item = self.custom.add()
        item.key = key
        if isinstance(val, str):
            item.val = val
            item.relevant_prop_name = "val"
        elif isinstance(val, int):
            item.vint = val
            item.relevant_prop_name = "vint"
        else:
            item.vfloat = val
            item.relevant_prop_name = "vfloat"

class MelCustomDataUtilPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__ # guess we need package? # __name__ # suspect this will break these preferences and we'll have to put them back into the main file?
    custom: CollectionProperty(type=CUSTOM_PG_PrefsKV) 

    filepath: StringProperty(
        name="Key-value config (json format)",
        description="Set a key-value config file. The values \n are used to determine the expected type for each key. Valid types are string, int and float.",
        subtype='FILE_PATH',
        update=_onPrefsFileUpdated
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Set a key-value config file. The values are used to determine the expected type for each key. Valid types are string, int and float.", icon="BRUSH_CLAY")
        layout.label(text="Example contents: ")
        example = """
        {
            "some-key" : "some-value", 
            "another-key" : "another-value",
            "an-int-key" : 23,
            "a-float-key" : 23.0
        }
        """
        layout.label(text=example)

        layout.prop(self, "filepath")
        layout.label(text=F"{len(self.custom)} keys: { ', '.join([item.key for item in self.custom.values()])}")


classes = (
    CUSTOM_PG_PrefsKV,
    MelCustomDataUtilPreferences
    )

def register():
    print(F" register prefs module our name is: {__name__} pack is {__package__}")
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)