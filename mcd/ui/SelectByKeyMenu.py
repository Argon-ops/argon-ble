import bpy
from bpy.props import (StringProperty,)

from mcd.util import (ObjectLookupHelper, DisplayHelper)
from mcd.cduoperator import SelectByKey

class CDU_MT_SelectByKeyMenu(bpy.types.Menu):
    """Menu for the select by key operator"""
    name : StringProperty(name="_select_by_key")
    bl_label="Select all with key"
    bl_idname="OBJECT_MT_selectbykey"

    @classmethod
    def poll(cls, context):
        return True 

    def draw(self, context):
        for key in ObjectLookupHelper._getAllPrefsKeys(context):
            self.layout.operator(SelectByKey.CDU_OT_SelectByKey.bl_idname, text=F"{DisplayHelper._trimMelPrefix(key)}").target_key = key

def register():
    from bpy.utils import register_class
    register_class(CDU_MT_SelectByKeyMenu)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(CDU_MT_SelectByKeyMenu)