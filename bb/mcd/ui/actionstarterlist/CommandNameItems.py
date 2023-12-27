
import bpy

from bpy.props import (IntProperty,
                       EnumProperty,)


from bpy.types import (Operator,
                       PropertyGroup,
                       UIList,)


from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU

#region list operators

class OT_CompositeCommandNamesActions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "composite_command.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))
    
    targetCommandIndex : IntProperty()

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.compositeCmdCmdNamesIdx

        try:
            compositeCommand = scn.as_custom[self.targetCommandIndex]
            cnames = compositeCommand.commandNames
        except IndexError:
            return {"FINISHED"}
        else:
            try:
                item = cnames[idx] 
            except IndexError:
                pass
            else:
                if self.action == 'DOWN' and idx < len(cnames) - 1:
                    cnames.move(idx, idx+1)
                    scn.compositeCmdCmdNamesIdx += 1
                    info = 'Item "%s" moved to position %d' % (item.commandName, scn.compositeCmdCmdNamesIdx + 1)
                    self.report({'INFO'}, info)

                elif self.action == 'UP' and idx >= 1:
                    cnames.move(idx, idx-1)
                    scn.compositeCmdCmdNamesIdx -= 1
                    info = 'Item "%s" moved to position %d' % (item.commandName, scn.compositeCmdCmdNamesIdx + 1)
                    self.report({'INFO'}, info)

                elif self.action == 'REMOVE':
                    cnames.remove(idx)
                    if scn.compositeCmdCmdNamesIdx > 0:
                        scn.compositeCmdCmdNamesIdx -= 1

            if self.action == 'ADD':
                item = cnames.add()
                item.id = len(cnames)
                item.name = "fake_as_name"
                scn.compositeCmdCmdNamesIdx = (len(cnames)-1)
                info = '%s added to list' % (item.name)
                self.report({'INFO'}, info)

        return {"FINISHED"}

#endregion
    
class PG_AS_CommandName(PropertyGroup):
    """Ble needs the string to be wrapped in a property group to use in a list"""
    commandName : EnumProperty(
        items=lambda self, context : CLU.playablesItemCallback(context),
    )

class CUSTOM_UL_AS_CommandNameItems(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        from bb.mcd.ui.actionstarterlist import CUSTOM_PG_AS_Collection
        row = layout.row()
        row.prop(item, "commandName", text="Command: ")
        row.operator(CUSTOM_PG_AS_Collection.CU_OT_PlayablePickPopup.bl_idname, text="", icon="GREASEPENCIL").playableName = item.commandName
        
    def invoke(self, context, event):
        pass


def DrawList(layout, playable):
    row = layout.row()
    row.template_list("CUSTOM_UL_AS_CommandNameItems", "custom_def_list", playable, "commandNames", 
                        bpy.context.scene, "compositeCmdCmdNamesIdx", rows=5)
    col = row.column(align=True)
    
    targetIndex = bpy.context.scene.as_custom.keys().index(playable.name)
    addOp = col.operator(OT_CompositeCommandNamesActions.bl_idname, icon='ADD', text="")
    addOp.action = 'ADD'
    addOp.targetCommandIndex = targetIndex
    removeOp = col.operator(OT_CompositeCommandNamesActions.bl_idname, icon='REMOVE', text="")
    removeOp.action = 'REMOVE'
    removeOp.targetCommandIndex = targetIndex
    col.separator()
    upOp = col.operator(OT_CompositeCommandNamesActions.bl_idname, icon='TRIA_UP', text="")
    upOp.action = 'UP'
    upOp.targetCommandIndex = targetIndex
    downOp = col.operator(OT_CompositeCommandNamesActions.bl_idname, icon='TRIA_DOWN', text="")
    downOp.action = 'DOWN'
    downOp.targetCommandIndex = targetIndex

classes = (
    PG_AS_CommandName,
    CUSTOM_UL_AS_CommandNameItems,
    OT_CompositeCommandNamesActions,
    )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.compositeCmdCmdNamesIdx = IntProperty(name="CommandNamesIndex")

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    del bpy.types.Scene.compositeCmdCmdNamesIdx
