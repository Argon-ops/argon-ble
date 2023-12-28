import bpy
from bpy.props import (StringProperty,)

from bb.mcd.util import (ObjectLookupHelper, DisplayHelper)
from bb.mcd.cduoperator.AddKeyToSelected import CUSTOM_OT_AddKeyToSelected

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
        for key in ObjectLookupHelper._getAllPrefsKeys(context): 
            # if all selected have this key, just draw a label don't provide an operator
            if ObjectLookupHelper._allSelectedHaveKey(key, context):
                layout.label(text=F"{DisplayHelper._trimMelPrefix(key)}")
                continue
            layout.operator(CUSTOM_OT_AddKeyToSelected.bl_idname, text=F"{DisplayHelper._trimMelPrefix(key)}").target_key = key

def register():
    from bpy.utils import register_class
    register_class(CDU_MT_AddKeyMenu)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(CDU_MT_AddKeyMenu)