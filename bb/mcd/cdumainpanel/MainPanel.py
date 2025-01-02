from bpy.app.handlers import persistent
from bb.mcd.core.customcomponent import CustomComponentFilePickPopup
from bb.mcd.settings import GlobalSettings
from bb.mcd.core.command import CommandsPanel
from bb.mcd.core.export import ExportBox
from bb.mcd.core.materiallist import MaterialListPanel
from bb.mcd.cdumainpanel import Inspector
from bb.mcd.cdumenu.AddKeyMenu import CDU_MT_AddKeyMenu
from bb.mcd.util import DisplayHelper
from bb.mcd.util import RelevantPropertyNameHelper
from bb.mcd.util import ObjectLookupHelper
from bb.mcd.cdumenu.SelectByKeyMenu import CDU_MT_SelectByKeyMenu
from bb.mcd.lookup.KeyValItem import CUSTOM_PG_KeyValItem
from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList,
                       AddonPreferences)
from bpy.props import (IntProperty,
                       BoolProperty,
                       FloatProperty,
                       StringProperty,
                       CollectionProperty)
import bpy
import json
bl_info = {
    "name": "mel-custom-properties-helper-2",
    "description": "",
    "author": "melsov",
    "version": (0, 2),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > MelPropHelper",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}


class CDU_OT_actions(Operator):
    """Handle removing a component-like key from an object"""
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
        idx = scn.componentLikesIndex

        try:
            item = scn.componentLikes[idx]
        except IndexError:
            pass
        else:
            if self.action == 'REMOVE':
                from bb.mcd.core.componentlike import StorageRouter
                StorageRouter.handleRemoveKey(item.key, context)

                scn.componentLikesIndex = ObjectLookupHelper._nextRelevantIndex(
                    context, scn.componentLikesIndex)

        return {"FINISHED"}



class CDU_UL_PerObjectItems(UIList):
    """A list that filters items based on whether the item's key

        appears as a custom property key on the selected object{s}.
        (Used to display the keys owned by the selected object{s})"""

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

        flags = list(map(lambda kv: _shouldIncludeKey(kv.key, context), kvs))
        order = []
        # TODO: support sorting alphabetical
        return flags, order

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.35)
        split.label(text=F"{DisplayHelper._trimMelPrefix(item.key)}")
        split = split.split(factor=.77)
        split.label(text="")  # empty label helps formatting

        if index == context.scene.componentLikesIndex:
            split.operator(CDU_OT_actions.bl_idname, icon='X',
                           text="").action = 'REMOVE'

#region draw-functions

def _drawInspectorListAndDetails(layout, context):
    scn = bpy.context.scene
    box = layout.box()
    row = box.row()

    # draw the key select uilist
    row.template_list("CDU_UL_PerObjectItems", "custom_def_list", scn, "componentLikes",
                      scn, "componentLikesIndex", rows=5)

    row = box.row()  
    prefs_items = ObjectLookupHelper._getPrefItems(context)

    # no config file?
    if len(prefs_items.values()) == 0:
        layout.row().label(text="There's a problem", icon="ERROR")
        return

    Inspector.drawCurrentItemDetails(row, context)


def _drawInspector(layout, context, wantSelByKey=True, wantShowInspectorToggle=True):
    box = layout.box()
    row = box.row()

    if wantShowInspectorToggle:
        DisplayHelper._drawShowHideTriangle(
            row, context.scene, "show_inspector", context.scene.show_inspector)
        row.label(
            text=F"Inspector: {ObjectLookupHelper._selectedObjectNames(context) }")
        if not context.scene.show_inspector:
            return

    box = box.box()

    box.row().menu(CDU_MT_AddKeyMenu.bl_idname, icon="KEY_HLT")

    _drawInspectorListAndDetails(layout, context)


def _drawSelByKey(box):
    box.row().menu(CDU_MT_SelectByKeyMenu.bl_idname, icon="RESTRICT_SELECT_OFF")

#endregion


class CDU_PT_CustomPropHelper(Panel):
    """Defines the main panel for Argon: interact with custom properties on selected objects."""
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

        _drawInspector(layout, context)

        # export box
        box = layout.box()
        ExportBox.Draw(box, context)

        box = layout.box()
        MaterialListPanel.Draw(box, context)

        box = layout.box()
        CommandsPanel.Draw(box, context)

        box = layout.box()
        GlobalSettings.DrawGlobalsButton(box)

        CustomComponentFilePickPopup.DrawInPanel(layout.box())

        box = layout.box()
        _drawSelByKey(box)


#region register/unregister

classes = (
    CDU_OT_actions,
    CDU_UL_PerObjectItems,
    CDU_PT_CustomPropHelper,
)


@persistent
def syncDisplayKVs(scene):
    """ Reload key-values in scene.componentLikes 

    They should match the key-values defined in prefs 
    plus any custom key-values loaded from a file. 
    """
    if not hasattr(scene, 'componentLikes'):
        print("scene has no attrib named 'componentLikes'. bye")
        return

    scene.componentLikes.clear()

    pref_items = ObjectLookupHelper._getPrefItems(bpy.context)
    for key, defaultValueInfo in pref_items.items():
        dval = scene.componentLikes.add()
        dval.key = key
        dval.relevant_prop_name = RelevantPropertyNameHelper._getPropNameForType(
            defaultValueInfo.default)
        dval.hint = defaultValueInfo.hint

    # UNRELATED CODE THAT SHOULD MOVE
    from bb.mcd.core.customcomponent import CustomComponentInspector
    CustomComponentInspector.DisplayListUtils.FillDisplayListWithBlanks(
        bpy.context)


@persistent
def handleSelectionChanged(scene):
    """ Update the selected key index if we need to """
    if len(bpy.context.selected_objects) == 0:
        scene.componentLikesIndex = -1


def refreshHandlerCallbacks():
    # REMINDER: we are registering callbacks that happen every time the user clicks.
    #  (Why do we need to reload scene.componentLikes so frequently? Ideally we wouldn't)

    h = bpy.app.handlers
    handlerses = [
        h.depsgraph_update_pre,         # handler for any click on the uilist
        # h.load_post  # sadly this doesn't do anything because there's no 'scene' object when load_post fires
    ]

    for handlers in handlerses:
        [handlers.remove(h)
         for h in handlers if h.__name__ == "syncDisplayKVs"]
        handlers.append(syncDisplayKVs)

    for handlers in handlerses:
        [handlers.remove(h) for h in handlers if h.__name__ ==
         "handleSelectionChanged"]
        handlers.append(handleSelectionChanged)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    # define a collection of KeyValItems and an index
    bpy.types.Scene.componentLikes = CollectionProperty(
        type=CUSTOM_PG_KeyValItem)
    bpy.types.Scene.componentLikesIndex = IntProperty()
    bpy.types.Scene.show_inspector = BoolProperty(default=True)

    refreshHandlerCallbacks()


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.componentLikes
    del bpy.types.Scene.componentLikesIndex
    del bpy.types.Scene.show_inspector

#endregion