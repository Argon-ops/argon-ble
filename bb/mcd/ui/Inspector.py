import bpy
from bpy.types import (Panel,)
from bb.mcd.util import CurrentItemIndex
from bb.mcd.ui.componentlike import StorageRouter
from bb.mcd.lookup import KeyValDefault
from bb.mcd.util import DisplayHelper
from bb.mcd.util import ObjectLookupHelper
from bb.mcd.cduoperator.SetKeyValue import CUSTOM_OT_SetDefaultValue
from bb.mcd.ui import CustomComponentInspector


def _displayPrimitive(box, key, item):
    row = box.row()
    split = row.split(factor=.35)
    split.label(text=F"{DisplayHelper._trimMelPrefix(key)}:")
    split.prop(item, item.relevant_prop_name, text="")

def _displayEmptyBox(box):
    row = box.row()
    row.label(text=" ")
    row.label(text=" ")

def _drawHelpToggleTriangle(row, context):
    row.prop(context.scene, "inspectorShowHelp", 
        icon="TRIA_DOWN" if context.scene.inspectorShowHelp else "TRIA_UP",
        icon_only=True, emboss=False)

def _drawHeader(box, key, context):
    row = box.row()
    _drawHelpToggleTriangle(row, context)
    row.label(text=DisplayHelper._trimMelPrefix(key))

def _drawMixed(box, key):
    row = box.row()
    row.operator(CUSTOM_OT_SetDefaultValue.bl_idname, text="make uniform").target_key = key

def _drawHelp(help, box, context):
    if help and context.scene.inspectorShowHelp:
        box = box.box()
        row = box.row()
        row.label(text=F"{help}")

def drawCurrentItemDetails(layout, context):
    key = CurrentItemIndex.getFocusedKey(context)
    item = CurrentItemIndex.getFocusedItem(context)

    box = layout.box()

    if item is None:
        _displayEmptyBox(box)
        return

    if len(context.selected_objects) == 0:
        _displayEmptyBox(box)
        return
    
    if ObjectLookupHelper._isMixedValues(key, context):
        if StorageRouter._isMultiSelectAllowed(key):
            _drawMixed(box, key)

    if ObjectLookupHelper._isKeyInActiveOject(key, context) == False:
        _displayEmptyBox(box)
        return

    _drawHeader(box, key, context)
    _drawHelp(KeyValDefault.getHelp(key), box, context = context)

    # nothing to display for tags. they're just present or absent.
    if KeyValDefault.getHandlingHint(key) == KeyValDefault.EHandlingHint.TAG:
        _displayEmptyBox(box)
        return
    
    # TODO: handle keys that are custom type definitions (==KeyValDefault.EHandlingHint.CUSTOM_COMPO_DEF)
    #  They will be defined in with a JSON object
    #   Then, there's a function that knows how to display values and read them from selected objs.
    if KeyValDefault.getHandlingHint(key) == KeyValDefault.EHandlingHint.CUSTOM_COMPONENT:
        import json
        box.label(text="CustomCompo ")
        CustomComponentInspector.displayCustomCompos(box, key)
        return

    # check for keys that display as objects
    if StorageRouter.displayItem(key, box, context) == True:
        return

    # this must be a primitive
    _displayPrimitive(box, key, item)


def register():
    bpy.types.Scene.inspectorShowHelp = bpy.props.BoolProperty()

def unregister():
    del bpy.types.Scene.inspectorShowHelp