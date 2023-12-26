
bl_info = {
    "name": "mel-custom-properties-helper-2",
    "description": "",
    "author": "melsov",
    "version": (0, 2),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > MelPropHelper",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View" 
}

import json
import bpy
from bpy.props import (IntProperty,
                       BoolProperty,
                       FloatProperty,
                       StringProperty,
                       CollectionProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList,
                       AddonPreferences)

from bb.mcd.ui.KeyValItem import CUSTOM_PG_KeyValItem
from bb.mcd.ui.SelectByKeyMenu import CDU_MT_SelectByKeyMenu
from bb.mcd.util import ObjectLookupHelper
from bb.mcd.util import DisplayHelper
from bb.mcd.ui.AddKeyMenu import CDU_MT_AddKeyMenu
from bb.mcd.cduoperator.SetKeyValue import CUSTOM_OT_SetDefaultValue
from bb.mcd.ui import Inspector
from bb.mcd.lookup import KeyValDefault
from bb.mcd.exporter.default import DefaultFBXExporter
from bb.mcd.ui.componentlike.unityinfo import UnityPaths
from bb.mcd.ui.materiallist import MaterialList
from bb.mcd.ui.materiallist import MaterialListPanel
from bb.mcd.ui.materiallist import MaterialListExporter
from bb.mcd.ui.export import ExportBox

from bb.mcd.ui.actionstarterlist import ActionStarterPanel

# from more_stuff_here import more
# more.more_stuff()

# -------------------------------------------------------------------
#   Operators
# -------------------------------------------------------------------

class CDU_OT_actions(Operator):
    """Remove items"""
    bl_idname = "custom.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.custom_index

        try:
            item = scn.custom[idx]
        except IndexError:
            pass
        else:
            if self.action == 'REMOVE':
                from bb.mcd.ui.componentlike import StorageRouter
                StorageRouter.handleRemoveKey(item.key, context) #.selected_objects)
                scn.custom_index = ObjectLookupHelper._nextRelevantIndex(context, scn.custom_index)                
              
        return {"FINISHED"}

# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

class CDU_UL_PerObjectItems(UIList):
    """Draw each key-val row that's defined as a property of the selected objects."""

    def filter_items(self, context, data, propname):

        kvs = getattr(data, propname)

        if len(context.selected_objects) == 0:
            return [~self.bitflag_filter_item] * len(kvs), []
        
        def _shouldIncludeKey(key, context) -> int:
            # filter using the search bar if it's shown
            if self.use_filter_show and len(self.filter_name) > 0 and self.filter_name not in key:
                return ~self.bitflag_filter_item
            
            if ObjectLookupHelper._allSelectedHaveKey(key, context):
                return self.bitflag_filter_item
            return ~self.bitflag_filter_item
       
        flags = list(map(lambda kv : _shouldIncludeKey(kv.key, context), kvs))
        order = []
        # TODO: support sorting alphabetical 
        return flags, order

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.35)
        split.label(text=F"{DisplayHelper._trimMelPrefix(item.key)}")
        split = split.split(factor=.77)
        split.label(text="") # empty label helps formatting

        if index == context.scene.custom_index:
            split.operator(CDU_OT_actions.bl_idname, icon='X', text="").action = 'REMOVE'

def _drawInspectorListAndDetails(layout, context):
    scn = bpy.context.scene
    box = layout.box()
    row = box.row() # layout.row()
    # draw the key select uilist
    row.template_list("CDU_UL_PerObjectItems", "custom_def_list", scn, "custom", 
        scn, "custom_index", rows=5)

    row = box.row() # layout.row()
    prefs_items = ObjectLookupHelper._getPrefItems(context)

    # no config file? 
    if len(prefs_items.values()) == 0:
        row.label(text="you need to add some key-value pairs", icon="QUESTION")
        row = layout.row()
        row.label(text="see the preferences for this add-on", icon="ERROR")
        return
    
    Inspector.drawCurrentItemDetails(row, context)


def drawInspector(layout, context, wantSelByKey=True, wantShowInspectorToggle=True):
    box = layout.box()
    row = box.row()

    if wantShowInspectorToggle:
        DisplayHelper._drawShowHideTriangle(row, context.scene, "show_inspector", context.scene.show_inspector)
        row.label(text=F"Inspector: {ObjectLookupHelper._selectedObjectNames(context) }")
        if not context.scene.show_inspector:
            return

    box = box.box()
    row = box.row()
    row.menu(CDU_MT_AddKeyMenu.bl_idname, icon="KEY_HLT")
    if wantSelByKey:
        row = box.row()
        row.menu(CDU_MT_SelectByKeyMenu.bl_idname, icon="RESTRICT_SELECT_OFF")

    _drawInspectorListAndDetails(layout, context)
  

class CDU_PT_CustomPropHelper(Panel):
    """Main panel: interact with custom properties on selected objects."""
    bl_idname = 'TEXT_PT_argon_panel'
    bl_space_type = "VIEW_3D" 
    bl_region_type = "UI"
    bl_category = "Argon"
    bl_label = "ARGON Custom Properties"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        drawInspector(layout, context)
        
        # export box
        box = layout.box()
        ExportBox.Draw(box, context)
        
        # box = layout.box()
        # box.prop(context.scene.unityProjectRoot, "file_path", text="Unity Project Root")

        box = layout.box()
        MaterialListPanel.Draw(box, context)

        box = layout.box()
        ActionStarterPanel.Draw(box, context)

        box = layout.box()
        from bb.mcd.settings import GlobalSettings
        GlobalSettings.DrawGlobalsButton(box)
        

# MORE TODOs:
#   bring back the load config file button if only for dbug. but maybe not only?

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    CDU_OT_actions,
    CDU_UL_PerObjectItems,
    CDU_PT_CustomPropHelper,
    )

from bpy.app.handlers import persistent

@persistent
def syncDisplayKVs(scene):
    """ Reload key-values based on the key-values defined in prefs. """
    if hasattr(scene, 'custom') == False:
        print("scene has no custom attrib bye")
        return

    # FIXME TODO: when we first addKeyToselected 
    #   we're finding that this list (scene.custom) has no 
    #    entries.   When was this function supposed to be called??
    # 
    pref_items = ObjectLookupHelper._getPrefItems(bpy.context) 
    # spam to show how often
    # print(F"Hi hi hi from syncDisplayKV. we have {len(pref_items.items())} items to add")
    scene.custom.clear()
    for key, defaultValueInfo in pref_items.items():
        dval = scene.custom.add()
        dval.key = key
        dval.relevant_prop_name = ObjectLookupHelper._getPropNameForType(defaultValueInfo.default)
        dval.handlingHint = defaultValueInfo.handlingHint

    def DmessWithTestInt():
        # works as expected
        try:
            ob = bpy.context.selected_objects[0]
            testint = ob.testint
            ob.testint = testint + 1 
            # print(F"TESTING: {ob.testint}")
        except BaseException as e:
            pass
            # print(F"something failed with testint {str(e)}")
    DmessWithTestInt()

@persistent
def handleSelectionChanged(scene):
    """ Update the selected key index if we need to """
    if len(bpy.context.selected_objects) == 0:
        scene.custom_index = -1

def refreshHandlerCallbacks():
    h = bpy.app.handlers
    handlerses = [
        h.depsgraph_update_pre,         # handler for any click on the uilist
        # h.load_post  # sadly this doesn't do anything because there's no 'scene' object when load_post fires
        ]

    for handlers in handlerses:
        [handlers.remove(h) for h in handlers if h.__name__ == "syncDisplayKVs"]
        handlers.append(syncDisplayKVs)

    for handlers in handlerses:
        [handlers.remove(h) for h in handlers if h.__name__ == "handleSelectionChanged"]
        handlers.append(handleSelectionChanged)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # define a collection of KeyValItems and an index
    bpy.types.Scene.custom = CollectionProperty(type=CUSTOM_PG_KeyValItem)
    bpy.types.Scene.custom_index = IntProperty()
    
    bpy.types.Scene.show_inspector = BoolProperty(default=True)

    bpy.types.Object.testint = IntProperty()

    refreshHandlerCallbacks()
    # are we allowed to sync
    # print(F"CALL sync Display from register...")
    # syncDisplayKVs(bpy.types.Scene)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.custom
    del bpy.types.Scene.custom_index
    del bpy.types.Scene.show_inspector

    del bpy.types.Object.testint

if __name__ == "__main__":
    register()

if __name__ != "__main__":
    print(F"This isn't main its: {__name__} . package: {__package__}")

"""
NOTES:
  One tricky option for storing data per blend file is apparently
    storing it in a text data block whose name begins with a dot: ".my-data"
    CREDIT: https://blender.stackexchange.com/questions/8442/trouble-getting-windowmanager-properties-to-save-its-contents-with-blend-file
    HOW: https://blender.stackexchange.com/questions/177742/how-do-i-create-a-text-datablock-and-populate-it-with-text-with-python
    

    # By the way: you can expose single object properties with .prop: 
            # https://blender.stackexchange.com/questions/148924/add-custom-property-to-panel
            # but we need to support multi object prop editing. hence this list of keys approach

# credit: GUIList demo by p2or: https://gist.github.com/p2or/30b8b30c89871b8ae5c97803107fd494 

"""
