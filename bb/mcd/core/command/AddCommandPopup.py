# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# <pep8 compliant>

from bb.mcd.core.componentlike.util import ComponentLikeUtils as CLU

import bpy

# from bb.mcd.core.command import CUSTOM_PG_AS_Collection as CPACModule
from bb.mcd.core.componentlike.adjunct import AddSubtractExtraPlayables
from bb.mcd.core.command import CommandTypes as CT


def AppendNewPlayableToInteractionHandlerLike(playableName: str):
    neps = AddSubtractExtraPlayables.AddSubtractNumExtraPlayables(
        True, bpy.context)
    print(F"Will INSERT at IDX {neps} name: {playableName}")
    CLU.setValueAtKey(F"mel_interaction_handler_playable{neps}", playableName)


def SetNewPlayableAtInteractionHandlerLike(playableName: str, playableIdx: int) -> None:
    key = F"mel_interaction_handler_playable{('' if playableIdx == 0 else str(playableIdx))}"
    print(F"Will Append at {key} name: {playableName}")
    CLU.setValueAtKey(key, playableName)


def FakeInitPlayable(playable):
    pass


def OnCommandCreated(as_custom_idx): return as_custom_idx  


class CU_OT_PlayableCreate(bpy.types.Operator):
    """Add a Command."""
    bl_idname = "view3d.viewport_rename"
    bl_label = "Add a Command"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "new_name"

    new_name: bpy.props.StringProperty(
        name="New Name"
    )
    playableType: bpy.props.EnumProperty(
        name="Playable Type",
        items=CT.getPlayableTypes(),  # CPACModule.getPlayableTypes(),
    )
    should_append: bpy.props.BoolProperty()
    should_insert: bpy.props.BoolProperty()
    insert_at_idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        from bb.mcd.core.command import CommandsList

        scn = context.scene
        item = scn.as_custom.add()
        item.id = len(scn.as_custom)

        item.name = CommandsList.enforceUnique(self.new_name, context)
        item.playableType = self.playableType

        # CPACModule.CUSTOM_PG_AS_Collection.InitPlayable(item)
        #  TODO: the above method did nothing and was part of a circular import chain
        #    for now do this to unravel the chain. But also this function stands in as a
        #   reminder that we might want to let playables init
        FakeInitPlayable(item)

        bpy.ops.view3d.playable_pick_popup(
            'INVOKE_DEFAULT', playableName=item.name)

        if self.should_insert:
            SetNewPlayableAtInteractionHandlerLike(
                item.name, self.insert_at_idx)
        elif self.should_append:
            AppendNewPlayableToInteractionHandlerLike(item.name)

        scn.as_custom_index = len(scn.as_custom)-1
        info = '%s added to list' % (item.name)

        # call our callback
        OnCommandCreated(item)

        self.report({'INFO'}, info)
        return {'FINISHED'}

    def invoke(self, context, event):
        from bb.mcd.core.command import CommandsList

        wm = context.window_manager
        dpi = context.preferences.system.pixel_size
        ui_size = context.preferences.system.ui_scale
        dialog_size = int(450 * dpi * ui_size)
        self.new_name = CommandsList.enforceUnique("Playable", context)

        return wm.invoke_props_dialog(self, width=dialog_size)

    def draw(self, context):
        row = self.layout
        row.row()
        row.prop(self, "new_name", text="Name")
        row.prop(self, "playableType", text="Playable Type")
        row.row()


# ------------------------------------------------------------------------
#    register, unregister and hotkey
# ------------------------------------------------------------------------


def register():
    from bpy.utils import register_class
    register_class(CU_OT_PlayableCreate)


def unregister():
    from bpy.utils import unregister_class
    unregister_class(CU_OT_PlayableCreate)
