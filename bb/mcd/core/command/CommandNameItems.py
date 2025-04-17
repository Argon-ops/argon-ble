
import bpy

from bpy.props import (IntProperty,
                       EnumProperty,
                       StringProperty,)


from bpy.types import (Operator,
                       PropertyGroup,
                       UIList,)


from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU
from bb.mcd.core.command import AddCommandPopup


# region list operators

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

    targetCommandIndex: IntProperty()

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
                    info = 'Item "%s" moved to position %d' % (
                        item.commandName, scn.compositeCmdCmdNamesIdx + 1)
                    self.report({'INFO'}, info)

                elif self.action == 'UP' and idx >= 1:
                    cnames.move(idx, idx-1)
                    scn.compositeCmdCmdNamesIdx -= 1
                    info = 'Item "%s" moved to position %d' % (
                        item.commandName, scn.compositeCmdCmdNamesIdx + 1)
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

# endregion


def TEST_storePlayableName(targetObject, idx : int, storeStrAttr : str = "playAfterStor"):
    print(F"Called from the CommandName.commandName prop: {targetObject.name} | idx: {idx} | store attr: {storeStrAttr}")
    CLU.storePlayableName(targetObject, idx, storeStrAttr)


class PG_AS_CommandName(PropertyGroup):
    """A PropertyGroup that wraps around the enum 'commandName' so that we can use it in a Blender Collection type.
    
        Used with Composite Commands
    """

    """
    defines the command name. commandName is an Enum that uses a separate string 'commandNameStor' to store its value
    """
    commandName: EnumProperty(
        items=lambda self, context: CLU.playablesItemCallback(context),
        get=lambda self: CLU.playableEnumIndexFromName(self.commandNameStor),
        set=lambda self, value: TEST_storePlayableName( # WANT --> # CLU.storePlayableName(
            self, value, "commandNameStor")
    )

    commandNameStor: StringProperty(
        description="PRIVATE",
    )


class CUSTOM_UL_AS_CommandNameItems(UIList):
    """A UIList for the command names owned by composite commands
    """
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        from bb.mcd.core.command import CUSTOM_PG_AS_Collection
        row = layout.row()
        row.prop(item, "commandName", text="Command: ")
        row.operator(CUSTOM_PG_AS_Collection.CU_OT_PlayablePickPopup.bl_idname,
                     text="", icon="GREASEPENCIL").playableName = item.commandName

        # REMOVING: don't include this add new button
        #   because without the callback we don't have a way of assigning the newly created command 
        #    to this commandNames slot.
        # Add new
        # plusOp = row.operator(
        #     AddCommandPopup.CU_OT_PlayableCreate.bl_idname, icon='ADD', text="New Command")
        # plusOp.should_insert = True
        # plusOp.insert_at_idx = len(bpy.context.scene.as_custom)

        # REMOVING this callback assignment: we are blaming this callback for a bug. CPG 18 in the Jira
        # def assignToCommandList(newCommand):
        #     print(F"assignToCommandList for item: {item.name} | newCommand: {newCommand.name}")
        #     item.commandName = newCommand.name

        # # set the module's dedicated callback function object
        # AddCommandPopup.OnCommandCreated = assignToCommandList

    def invoke(self, context, event):
        pass


def DrawList(layout, playable):

    row = layout.row()
    row.template_list("CUSTOM_UL_AS_CommandNameItems", "custom_def_list", playable, "commandNames",
                      bpy.context.scene, "compositeCmdCmdNamesIdx", rows=5)
    col = row.column(align=True)

    targetIndex = bpy.context.scene.as_custom.keys().index(playable.name)
    addOp = col.operator(
        OT_CompositeCommandNamesActions.bl_idname, icon='ADD', text="")
    addOp.action = 'ADD'
    addOp.targetCommandIndex = targetIndex
    removeOp = col.operator(
        OT_CompositeCommandNamesActions.bl_idname, icon='REMOVE', text="")
    removeOp.action = 'REMOVE'
    removeOp.targetCommandIndex = targetIndex
    col.separator()
    upOp = col.operator(
        OT_CompositeCommandNamesActions.bl_idname, icon='TRIA_UP', text="")
    upOp.action = 'UP'
    upOp.targetCommandIndex = targetIndex
    downOp = col.operator(
        OT_CompositeCommandNamesActions.bl_idname, icon='TRIA_DOWN', text="")
    downOp.action = 'DOWN'
    downOp.targetCommandIndex = targetIndex
    
    row = layout.row()
    # Add new button here: we are no longer supporting a per-row add new button
    plusOp = row.operator(
        AddCommandPopup.CU_OT_PlayableCreate.bl_idname, icon='ADD', text="New Command")
    plusOp.should_insert = True
    plusOp.insert_at_idx = len(bpy.context.scene.as_custom)


classes = (
    PG_AS_CommandName,
    CUSTOM_UL_AS_CommandNameItems,
    OT_CompositeCommandNamesActions,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.compositeCmdCmdNamesIdx = IntProperty(
        name="CommandNamesIndex")


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.compositeCmdCmdNamesIdx
