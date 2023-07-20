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

from mcd.ui.componentlike.util import ComponentLikeUtils as CLU

import bpy
import re
# from mcd.ui.actionstarterlist.CUSTOM_PG_AS_Collection import CUSTOM_PG_AS_Collection
from mcd.ui.actionstarterlist import CUSTOM_PG_AS_Collection as CPACModule
from mcd.ui.componentlike.adjunct import NumExtraPlayables

def AppendNewPlayableToInteractionHandlerLike(playableName : str):
    neps = NumExtraPlayables.AddSubtractNumExtraPlayables(True, bpy.context)
    CLU.setValueAtKey(F"mel_interaction_handler_playable{neps}", playableName)


class CU_OT_PlayableCreate(bpy.types.Operator):
    """Add a Playable"""
    bl_idname = "view3d.viewport_rename"
    bl_label = "Add a Playable"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "new_name"

    new_name : bpy.props.StringProperty(
        name="New Name"
    )
    playableType : bpy.props.EnumProperty(
        name="Playable Type",
        items=CPACModule.getPlayableTypes(),
    )
    should_append : bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return True 

    def execute(self, context):
        from mcd.ui.actionstarterlist import ActionStarterList

        scn = context.scene
        item = scn.as_custom.add()
        item.id = len(scn.as_custom)

        item.name = ActionStarterList.enforceUnique(self.new_name, context)
        item.playableType = self.playableType

        CPACModule.CUSTOM_PG_AS_Collection.InitPlayable(item)

        # can we launch the playable editor pop up? <--Yes. 
        # 
        # TODO: can we use getattr(bpy.ops, CU_OT_PPPopup.bl_idname) # to preserve intellisensing where this op comes from
        #  TODO: also add an entry in the InteractionHandler if this new pop up was called from IH.
        bpy.ops.view3d.playable_pick_popup('INVOKE_DEFAULT', playableId=item.internalId)

        if self.should_append:
            AppendNewPlayableToInteractionHandlerLike(item.name)

        scn.as_custom_index = len(scn.as_custom)-1
        info = '%s added to list' % (item.name)
        self.report({'INFO'}, info)
        return {'FINISHED'}


    def invoke(self, context, event):
        from mcd.ui.actionstarterlist import ActionStarterList
        # from mcd.ui.actionstarterlist.CUSTOM_PG_AS_Collection import CUSTOM_PG_AS_Collection

        wm = context.window_manager
        dpi = context.preferences.system.pixel_size
        ui_size = context.preferences.system.ui_scale
        dialog_size = int(450 * dpi * ui_size)
        self.new_name = ActionStarterList.enforceUnique("Playable", context)

        return wm.invoke_props_dialog(self, width=dialog_size)

    def draw(self, context):
        row = self.layout
        row.row()
        row.prop(self, "new_name", text="Name")
        row.prop(self, "playableType", text="Playable Type")
        # row.prop(self, "data_flag")
        row.row()


# ------------------------------------------------------------------------
#    register, unregister and hotkey
# ------------------------------------------------------------------------

addon_keymaps = []

def register():
    from bpy.utils import register_class

    addon_keymaps.clear()
    register_class(CU_OT_PlayableCreate)

    # handle the keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(CU_OT_PlayableCreate.bl_idname, type='R', value='PRESS', ctrl=True)
        addon_keymaps.append((km, kmi))

def unregister():
    from bpy.utils import unregister_class

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    unregister_class(CU_OT_PlayableCreate)

