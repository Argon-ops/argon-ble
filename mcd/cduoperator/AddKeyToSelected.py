import bpy
from bpy.props import (StringProperty,
                       IntProperty,
                       PointerProperty, 
                       CollectionProperty,
                       )

from bpy.types import (Operator, 
                       PropertyGroup,)

from mcd.util import ObjectLookupHelper
from mcd.lookup import KeyValDefault
from mcd.ui.componentlike import StorageRouter

""" NOTES:
    We can envision one scheme where: Each playable type adds a pointer instance of itself to the scene.
    Somehow...given a string, someone knows which of these types to ask to draw but how...
"""

class DDemoType(PropertyGroup):
    """just a test"""
    bl_idname="ddemo.delme"
    bl_label = "label fake"
    bl_description = "a description would go here if there were one"
    bl_options = {'REGISTER', 'UNDO'}

    n : IntProperty(
        default=42,
    )

class CUSTOM_OT_AddKeyToSelected(Operator):
    """Add key to all selected objects"""
    bl_idname = "custom.add_key_to_selected"
    bl_label = "Add key to selected objects"
    bl_description = "a description would go here if there were one"
    bl_options = {'REGISTER', 'UNDO'}

    target_key : StringProperty(
        name="target key",
        default=""
        )

    def invoke(self, context, event):
        print(F"invoke for addKeyToSel")
        return self.execute(context)
    
    def DtestObjects(self, context):
        print(F"will try to add test prop group...")
        ob = context.selected_objects[0]
        ob['testkey'] =  IntProperty(name='hi') # bpy.types.PointerProperty(type=DDemoType)
        print(F" ob test key.n {ob['testkey'].n}")

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        if len(self.target_key) == 0:
            return {'FINISHED'}
 
        default = KeyValDefault.getDefaultValue(self.target_key)
        StorageRouter.handleSetDefaultValue(self.target_key, default, context.selected_objects)
        
        # set this as the highlighted key
        ObjectLookupHelper._setSelectedIndex(context, self.target_key)

        self.target_key = ""

        self.DtestObjects(context)
        return {'FINISHED'}

classes = (
    CUSTOM_OT_AddKeyToSelected,
    DDemoType,
)

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)
    # register_class(CUSTOM_OT_AddKeyToSelected)

def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)
    # unregister_class(CUSTOM_OT_AddKeyToSelected)