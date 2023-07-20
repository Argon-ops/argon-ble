import bpy
from bpy.props import (StringProperty,)

from mcd.util import (ObjectLookupHelper, DisplayHelper)
from mcd.cduoperator.AddKeyToSelected import CUSTOM_OT_AddKeyToSelected

class CDU_MT_AddKeyMenu(bpy.types.Menu):
    """ Menu for the Add key operator. """
    name : StringProperty(name="_name")
    bl_label="Add key to selected"
    bl_idname="OBJECT_MT_unusedkeys"

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def draw(self, context):
        layout = self.layout
        unused_keys = ObjectLookupHelper._getUnusedKeys(context=context)
        for key in ObjectLookupHelper._getAllPrefsKeys(context): # unused_keys:
            if ObjectLookupHelper._allSelectedHaveKey(key, context):
                layout.label(text=F"{DisplayHelper._trimMelPrefix(key)}")
                continue
            layout.operator(CUSTOM_OT_AddKeyToSelected.bl_idname, text=F"{DisplayHelper._trimMelPrefix(key)}").target_key = key

def register():
    print(F"__SelByKey register__")
    from bpy.utils import register_class
    register_class(CDU_MT_AddKeyMenu)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(CDU_MT_AddKeyMenu)