bl_info = {
    "name": "BMelCustomDataUtilBAB",
    "location": "View3D > Sidebar > MelPropHelper",
    "blender": (2, 80, 0), # Don't use 2, 78 or register won't be called
    "category": "3D View", 
    'version': (0, 0, 1),
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
}

# See notes at the end of this file for a reminder of what/how to import modules using this list
modulesFullNames = [
    'bb.more_stuff_here.more',
    'bb.mcd.melstor.MCDKeyValConfig',
    'bb.mcd.lookup.KeyValDefault',
    'bb.mcd.util.ObjectLookupHelper',
    'bb.mcd.util.AppHandlerHelper',    
    'bb.mcd.ui.KeyValItem',
    'bb.mcd.ui.Inspector',
    'bb.mcd.ui.InspectorPopup',
    'bb.mcd.ui.componentlike.StaticFlags',
    'bb.mcd.MelCustomDataUtilBA',
    'bb.mcd.cduoperator.SelectByKey',
    'bb.mcd.cduoperator.AddKeyToSelected',
    'bb.mcd.util.DisplayHelper',
    'bb.mcd.ui.componentlike.adjunct.NumExtraPlayables',

    # scene level var declarations
    'bb.mcd.ui.export.ExportBox',
    'bb.mcd.ui.materiallist.MaterialList',
    'bb.mcd.ui.actionstarterlist.CommandNameItems',
    'bb.mcd.ui.actionstarterlist.CUSTOM_PG_AS_Collection',
    'bb.mcd.ui.actionstarterlist.ActionStarterList',

    'bb.mcd.ui.actionstarterlist.OT_TarAnimsList',
    'bb.mcd.util.JsonFromItem',
    'bb.mcd.cduoperator.SetKeyValue',
    'bb.mcd.ui.SelectByKeyMenu',
    'bb.mcd.ui.AddKeyMenu',
    'bb.mcd.ui.componentlike.util.ComponentLikeUtils',
    'bb.mcd.ui.componentlike.enablefilter.EnableFilterSettings',
    'bb.mcd.ui.componentlike.enablefilter.SleepStateSettings',
    'bb.mcd.ui.componentlike.util.ObjectPointerMsgbusUtils',
    'bb.mcd.ui.componentlike.AbstractPerObjectData',
    'bb.mcd.ui.componentlike.AbstractComponentLike',
    'bb.mcd.ui.componentlike.StorageRouter',
    'bb.mcd.ui.componentlike.AbstractDefaultSetter',
    'bb.mcd.ui.componentlike.MeshColliderLike',
    'bb.mcd.ui.componentlike.BoxColliderLike',
    # 'bb.mcd.ui.componentlike.ActionStarterLike',
    'bb.mcd.prefs.MelCustomDataUtilPreferences', # may have to stuff the prefs back into MelCDUBA. because its bl_idname has to match...etc.
    'bb.mcd.exporter.edyj.BlenderToUnityFbxExporter',
    'bb.mcd.exporter.default.DefaultFBXExporter',
    'bb.mcd.ui.componentlike.RigidbodyLike',
    'bb.mcd.ui.componentlike.LightEnableLike',
    'bb.mcd.ui.componentlike.OffMeshLinkLike',
    'bb.mcd.ui.componentlike.unityinfo.UnityPaths',
    'bb.mcd.ui.componentlike.InteractionHandlerLike',
    'bb.mcd.ui.componentlike.InteractionHighlighterLike',
    'bb.mcd.ui.componentlike.LayerCamLockPickableLike',
    'bb.mcd.ui.componentlike.EnableReceiverLike',
    'bb.mcd.ui.componentlike.ParticleSystemLike',
    'bb.mcd.ui.componentlike.VisualEffectLike',
    'bb.mcd.ui.componentlike.RE2PickSessionLike',
    'bb.mcd.ui.componentlike.DestroyLike',
    'bb.mcd.ui.componentlike.ForcePCWLike',
    'bb.mcd.ui.componentlike.ScreenOverlayEnableLike',
    'bb.mcd.ui.componentlike.AudioEnableLike',
    'bb.mcd.ui.componentlike.SwapMaterialEnableLike',
    'bb.mcd.ui.componentlike.ObjectEnableLike',
    'bb.mcd.ui.componentlike.SliderColliderLike',
    'bb.mcd.ui.componentlike.ComponentByNameLike',
    'bb.mcd.ui.componentlike.SpawnerLike',
    'bb.mcd.ui.componentlike.CamLockSessionEnableLike',
    'bb.mcd.ui.componentlike.DisableComponentLike',
    'bb.mcd.ui.componentlike.TextMeshLike',
    'bb.mcd.ui.componentlike.PlayableScalarAdapterLike',
    'bb.mcd.ui.materiallist.MaterialListPanel',
    'bb.mcd.shareddataobject.SharedDataObject',
    # 'bb.mcd.ui.materiallist.MaterialListExporter',
    # 'bb.mcd.ui.componentlike.actionstarters.ActionStarterData',
    'bb.mcd.ui.actionstarterlist.PlusActionStarterPopup',
    'bb.mcd.ui.actionstarterlist.ActionStarterPanel',
    'bb.mcd.objectinfo.ObjectInfo',
    'bb.mcd.ui.componentlike.enablereceiverbutton.EnableReceiverButton',
    'bb.mcd.exporter.ExportOp',
    'bb.mcd.settings.GlobalSettings',
    'bb.mcd.foo.ScratchPad',
    ]

import sys
import importlib

# modulesFullNames = {}
# print(F"DEBUG MODE? {'DEBUG_MODE' in sys.argv }")
# for currentModuleName in modulesNames:
#     modulesFullNames[currentModuleName] = ('{}'.format(currentModuleName)) 
#     # if 'DEBUG_MODE' in sys.argv:
#     #     modulesFullNames[currentModuleName] = ('{}'.format(currentModuleName))
#     # else:
#     #     modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))
#     print(F" FULL NAME: {modulesFullNames[currentModuleName] } | __name__ is {__name__} curModuleName: {currentModuleName}")
 

for fullName in modulesFullNames: #.values():
    if fullName in sys.modules:
        importlib.reload(sys.modules[fullName])
    else:
        globals()[fullName] = importlib.import_module(fullName)
        # setattr(globals()[fullName], 'modulesNames', modulesFullNames) # DELME ? FIXME: Do we not need this line? each module gets a copy of moduleFullNames but we don't use this...Did we actually need to use it?

def register():
    print(F"register $$$$")
    for currentModuleName in modulesFullNames: #.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                print(F"REG: {currentModuleName} ")
                sys.modules[currentModuleName].register()
 
def unregister():
    print(F"unregister ####")
    for currentModuleName in modulesFullNames: #.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                print(F"UNREG: {currentModuleName}")
                sys.modules[currentModuleName].unregister()

#region deferred setup
                
#  hacky work around to allow modules to do some set up
#  soon after--but not during--register.
#  Needed because access to certain blender data (e.g. bpy.data) is restricted / inaccessible during
     # addon register() (when youre formally adding the addon as a zip)
#   Assumes the user will click somewhere
#  before anything too critical happens. CONSIDER: It may be possible to 
#  add this addon and then close blender without ever triggering the depsgraph event
                
import bpy

def _removeFunction(fn_list, fn):
    fn_name = fn.__name__
    fn_module = fn.__module__
    for i in range(len(fn_list) - 1, -1, -1):
        if fn_list[i].__name__ == fn_name and fn_list[i].__module__ == fn_module:
            del fn_list[i]

def _deferredSetup_UNIQUENAME_135A(scene, despgraph):
    print(F"deferred setup")
    for cm in modulesFullNames.values():
        if cm in sys.modules:
            if hasattr(sys.modules[cm], "defer"):
                sys.modules[cm].defer()
    _removeFunction(bpy.app.handlers.depsgraph_update_post, _deferredSetup_UNIQUENAME_135A)

def scheduleDeferred():
    _removeFunction(bpy.app.handlers.depsgraph_update_post, _deferredSetup_UNIQUENAME_135A)
    bpy.app.handlers.depsgraph_update_post.append(_deferredSetup_UNIQUENAME_135A)
    
scheduleDeferred()

#endregion
 
if __name__ == "__main__":
    register()


# HOW TO ZIP FOR DISTRIBUTION AS AN ADDON:
    #   
    #  use this zip command (just using built in Windows compress didn't work for us)
    #   7z a -tzip bb.zip -w .\bb\
    #  
     
# THE IMPORT STATEMENTS HAVE TO FOLLOW THE FORMULA : <project-dir>.<sub-dirA>.<sub-dirB>
    # because, this way, they import correctly when loading from a zip as a formal addon AND 
    #    when loading via the boot2.py script
