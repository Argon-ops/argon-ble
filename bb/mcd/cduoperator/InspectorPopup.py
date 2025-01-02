import bpy

from bpy.props import (IntProperty,
                       BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty,
                       PointerProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)
import json

from bb.mcd.util import ObjectLookupHelper

from bb.mcd.cdumainpanel import MainPanel

#region hide / unhide

_prev_sel = []
_prev_active = None
_targ_needs_to_rehide = False
_targ_collection_rehides = []
_open_popup_instances = 0

def _getCollectionsInScene():
    return [c for c in bpy.data.collections if bpy.context.scene.user_of_id(c)]

def _getParentOf(coll):
    collections_in_scene = _getCollectionsInScene()
    return [c for c in collections_in_scene 
            if c.user_of_id(coll)]

def _saveSelection():
    if _open_popup_instances > 1:
        return
    global _prev_active
    global _prev_sel
    _prev_sel.clear()
    for ob in bpy.context.selected_objects:
        _prev_sel.append(ob)
    _prev_active = bpy.context.view_layer.objects.active

def _unhideCollections(objectName):
    global _targ_collection_rehides
    # for some reason, we need to access the collection this way in order to hide it 
    #   (as opposed to accessing from users_collection). <--This func returns a LayerCollection.
    #    And (it seems) LayerCollection (not Collection) is the thing we have to '.hide_viewport' with (even though they both have a '.hide_viewport' property, wtf?!)
    def findCollection(collName, searchCollection = None):
        if searchCollection is None:
            searchCollection = bpy.context.view_layer.layer_collection
        sus = []
        sus.append(searchCollection)

        while len(sus) > 0:
            sub = sus.pop()
            if sub.name == collName:
                return sub
            [sus.append(ch) for ch in sub.children]

        return None 

    def parentOfCollection(coll):
        if coll == bpy.context.view_layer.layer_collection:
            return None
        # coll is probably a LayerCollection. _getParentOf needs a Collection not a LayerCollection. LayerCollection wraps Collection; exposes its Collection at .collection
        parents = _getParentOf(coll.collection if hasattr(coll, "collection") else coll) 
        if len(parents) == 0: 
            return None
        return findCollection(parents[0].name) 
    
    def allHideableParentCollections(coll):
        result = []
        while True:
            result.append(coll)
            coll = parentOfCollection(coll)
            if coll is None:
                break
        return result

    target = bpy.data.objects[objectName]
    _targ_collection_rehides.clear()
    hideables = allHideableParentCollections(findCollection(target.users_collection[0].name))

    # reverse so we iterate parents first. set each parent visible before checking visiblity of child.
    #   otherwise, is_visible doesn't tell us what we want; it takes parent visibility into account.
    hideables.reverse() 
    for coll in hideables:
        _targ_collection_rehides.append((coll, coll.is_visible))
        coll.hide_viewport = False


def _setVisible(objectName):
    # TODO: try this batFinger: https://blender.stackexchange.com/questions/146685/how-to-obtain-the-parent-of-a-collection-using-python
    #   To traverse parent collections
    global _targ_needs_to_rehide
    
    _targ_needs_to_rehide = False
    target = bpy.data.objects[objectName]

    if not target.visible_get():
        _targ_needs_to_rehide = True
        target.hide_set(False)

def _doUnhiding(objectName):
    if _open_popup_instances > 1:
        return
    _unhideCollections(objectName)
    _setVisible(objectName)


def _rehide(objectName):
    global _targ_needs_to_rehide
    target = bpy.data.objects[objectName]
    target.hide_set(_targ_needs_to_rehide)

    global _targ_collection_rehides
    for rehide_data in _targ_collection_rehides:
        rehide_data[0].hide_viewport = not rehide_data[1]

#endregion

class CU_OT_InspectorPopup(bpy.types.Operator):
    """Edit a Playable. At the moment this just duplicates the in-row edit options. Use if we need more complex options"""
    bl_idname = "view3d.inspector_popup"
    bl_label = "Inspector Popup"
    bl_options = {'REGISTER', 'UNDO'}
    
    objectName : bpy.props.StringProperty(name="internalId") 

    @classmethod
    def poll(cls, context):
        return True 
        
    def execute(self, context):
        global _open_popup_instances
        global _prev_active
        global _prev_sel
        _open_popup_instances -= 1
        if _open_popup_instances == 0:
            _rehide(self.objectName)
            ObjectLookupHelper.selectObjectsInScene(_prev_sel, _prev_active)
        return {'FINISHED'}


    def invoke(self, context, event):
        global _open_popup_instances
        _open_popup_instances += 1

        # the inspector assumes that it should show the current selected object(s)
        #  but we want it to inspect our target object. Select our object and make it visible
        #  but first save the previous selection and visibility state
        _saveSelection()
        _doUnhiding(self.objectName)
        ObjectLookupHelper._selectInScene(self.objectName)

        wm = context.window_manager
        dpi = context.preferences.system.pixel_size
        ui_size = context.preferences.system.ui_scale
        dialog_size = int(450 * dpi * ui_size)
        return wm.invoke_props_dialog(self, width=dialog_size)

    def draw(self, context):
        MainPanel._drawInspector(self.layout, context, False, False) 

classes = (
    CU_OT_InspectorPopup,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
   

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
