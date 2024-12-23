bl_info = {
    "name": "Argon",
    "location": "View3D > Sidebar > Argon",
    "blender": (2, 80, 0), # Don't use 2, 78 or register won't be called
    "category": "3D View", 
    'version': (0, 0, 1),
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
}

# See notes at the end of this file for a reminder of what/how to import modules using this list



modulesFullNames = [
    'bb.mcd.util.RelevantPropertyNameHelper',
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
    'bb.mcd.ui.componentlike.adjunct.AddSubtractExtraPlayables',

    'bb.mcd.ui.export.ExportBox',
    'bb.mcd.ui.materiallist.MaterialList',
    'bb.mcd.ui.command.CommandNameItems',
    'bb.mcd.ui.command.CUSTOM_PG_AS_Collection',
    'bb.mcd.ui.command.CommandsList',

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

    'bb.mcd.prefs.MelCustomDataUtilPreferences', # may have to stuff the prefs back into MelCDUBA. because its bl_idname has to match...etc.
    'bb.mcd.exporter.edyj.BlenderToUnityFbxExporter',
    'bb.mcd.exporter.default.DefaultFBXExporter',
    'bb.mcd.ui.componentlike.RigidbodyLike',
    'bb.mcd.ui.componentlike.ReplaceWithPrefabLike',
    'bb.mcd.ui.componentlike.LightEnableLike',
    'bb.mcd.ui.componentlike.OffMeshLinkLike',

    'bb.mcd.ui.componentlike.InteractionHandlerLike',
    'bb.mcd.ui.componentlike.InteractionHighlighterLike',
    'bb.mcd.ui.componentlike.LayerCamLockPickableLike',
    'bb.mcd.ui.componentlike.EnableReceiverLike',
    'bb.mcd.ui.componentlike.ParticleSystemLike',
    'bb.mcd.ui.componentlike.VisualEffectLike',
    'bb.mcd.ui.componentlike.SceneObjectsReferencerLike',
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
    'bb.mcd.ui.componentlike.util.ColliderLikeShared',
    'bb.mcd.ui.componentlike.router.CLikeToDefaultSetterMap',
    'bb.mcd.ui.componentlike.preexport.ComponentLikePreExport',
    'bb.mcd.ui.CustomComponentInspector',
    'bb.mcd.ui.CustomComponentFilePickPopup',
    'bb.mcd.ui.materiallist.MaterialListPanel',
    'bb.mcd.shareddataobject.SharedDataObject', 
    'bb.mcd.ui.command.AddCommandPopup',
    'bb.mcd.ui.command.CommandsPanel',
    'bb.mcd.foo.objectinfo.ObjectInfo',

    'bb.mcd.exporter.ExportOp',
    'bb.mcd.settings.GlobalSettings',
    'bb.mcd.settings.IsArgonMarker',
    'bb.mcd.foo.ScratchPad',
    ]


import sys
import importlib

for fullName in modulesFullNames: 
    print(F"mod full name {fullName}")
    if fullName in sys.modules:
        try:
            importlib.reload(sys.modules[fullName])
        except Exception as mnfe:
            print(F"### Exception for module: {fullName}. Restarting blender may resolve this. ###")
            raise mnfe 
    else:
        print(F"# was not in sys.modules")
        globals()[fullName] = importlib.import_module(fullName)
        # setattr(globals()[fullName], 'modulesNames', modulesFullNames) # DELME ? Do we not need this line? each module gets a copy of moduleFullNames but we don't use this...Did we actually need to use it?

print(F"%%% finished reloading")

def register():
    for currentModuleName in modulesFullNames: 
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                print(F"REGISTER: {currentModuleName} ")
                sys.modules[currentModuleName].register()
 
def unregister():
    for currentModuleName in modulesFullNames: 
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                print(F"UNREGISTER: {currentModuleName}")
                sys.modules[currentModuleName].unregister()


#region deferred setup

#####################################################################################################                
#  Hacky work around to allow modules to do some set up, soon after--but not during--register.
#  Needed because access to certain blender data (e.g. bpy.data) is restricted / inaccessible during
#     addon register() (when you're formally adding the addon as a zip)
#   Assumes the user will click somewhere before anything too critical happens.(!!) 
#   CONSIDER: It may be possible to add this addon and then close blender without ever triggering the depsgraph event
#####################################################################################################                

import bpy

def _removeFunction(fn_list, fn):
    fn_name = fn.__name__
    fn_module = fn.__module__
    for i in range(len(fn_list) - 1, -1, -1):
        if fn_list[i].__name__ == fn_name and fn_list[i].__module__ == fn_module:
            del fn_list[i]

def _deferredSetup_UNIQUENAME_135A(scene, despgraph):
    for cm in modulesFullNames:
        if cm in sys.modules:
            if hasattr(sys.modules[cm], "defer"):
                sys.modules[cm].defer()
    _removeFunction(bpy.app.handlers.depsgraph_update_post, _deferredSetup_UNIQUENAME_135A)

def scheduleDeferred():
    _removeFunction(bpy.app.handlers.depsgraph_update_post, _deferredSetup_UNIQUENAME_135A)
    bpy.app.handlers.depsgraph_update_post.append(_deferredSetup_UNIQUENAME_135A)
    
scheduleDeferred()

#endregion
 

if 'DEBUG_MODE' in sys.argv and __name__ == "__main__":
    print(F"will register")
    register()


#########################################################################################################
## QUICK GUIDE ##########################################################################################
#########################################################################################################
        
# HOW TO ZIP FOR DISTRIBUTION AS AN ADDON:
    #   
    #  run this command (just using built in Windows 'compress' didn't work for us.) 
    #   7z a -tzip bb.zip -w .\bb\
    #   (Also, used this terminal https://github.com/microsoft/terminal not the default PowerShell)
    #  
     
# THE IMPORT STATEMENTS HAVE TO FOLLOW THE FORMULA : <project-dir>.<sub-dirA>.<sub-dirB>.<sub-dirN>
    #
    # In other words, they need to be absolute paths starting from project-dir.
    # In our case bb is the name of the project-dir, so:
    #
    # Example: from bb.mcd.util import ObjectLookupHelper
    #
    # This way, they import correctly when loading from a zip as a formal addon AND 
    #    when loading via the boot2.py script
