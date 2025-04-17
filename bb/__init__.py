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


modulesFullNames = [
    'bb.mcd.util.RelevantPropertyNameHelper',
    'bb.more_stuff_here.more',
    'bb.mcd.configs.MCDKeyValConfig',
    'bb.mcd.lookup.KeyValDefault',
    'bb.mcd.util.ObjectLookupHelper',
    'bb.mcd.util.AppHandlerHelper',    
    'bb.mcd.lookup.KeyValItem',
    'bb.mcd.cdumainpanel.Inspector',
    'bb.mcd.cduoperator.InspectorPopup',
    'bb.mcd.core.componentlike.StaticFlags',
    'bb.mcd.cdumainpanel.MainPanel',
    'bb.mcd.cduoperator.SelectByKey',
    'bb.mcd.cduoperator.AddKeyToSelected',
    'bb.mcd.util.DisplayHelper',
    'bb.mcd.core.componentlike.adjunct.AddSubtractExtraPlayables',

    'bb.mcd.cdumainpanel.ExportBox',
    'bb.mcd.core.materiallist.MaterialList',
    'bb.mcd.core.command.CommandNameItems',
    'bb.mcd.core.command.CUSTOM_PG_AS_Collection',
    'bb.mcd.core.command.CommandsList',

    'bb.mcd.util.JsonFromItem',
    'bb.mcd.cduoperator.SetKeyValue',
    'bb.mcd.cdumenu.SelectByKeyMenu',
    'bb.mcd.cdumenu.AddKeyMenu',
    'bb.mcd.core.componentlike.util.ComponentLikeUtils',
    'bb.mcd.core.componentlike.enablefilter.EnableFilterSettings',
    'bb.mcd.core.componentlike.enablefilter.SleepStateSettings',
    'bb.mcd.core.componentlike.util.ObjectPointerMsgbusUtils',
    'bb.mcd.core.componentlike.AbstractPerObjectData',
    'bb.mcd.core.componentlike.AbstractComponentLike',
    'bb.mcd.core.componentlike.StorageRouter',
    'bb.mcd.core.componentlike.AbstractDefaultSetter',
    'bb.mcd.core.componentlike.MeshColliderLike',
    'bb.mcd.core.componentlike.BoxColliderLike',

    'bb.mcd.prefs.MelCustomDataUtilPreferences', # may have to stuff the prefs back into MelCDUBA. because its bl_idname has to match...etc.
    'bb.mcd.exporter.edyj.BlenderToUnityFbxExporter',
    'bb.mcd.exporter.default.DefaultFBXExporter',
    'bb.mcd.core.componentlike.RigidbodyLike',
    'bb.mcd.core.componentlike.ReplaceWithPrefabLike',
    'bb.mcd.core.componentlike.LightEnableLike',
    'bb.mcd.core.componentlike.OffMeshLinkLike',

    'bb.mcd.core.componentlike.InteractionHandlerLike',
    'bb.mcd.core.componentlike.InteractionHighlighterLike',
    'bb.mcd.core.componentlike.LayerCamLockPickableLike',
    'bb.mcd.core.componentlike.EnableReceiverLike',
    'bb.mcd.core.componentlike.ParticleSystemLike',
    'bb.mcd.core.componentlike.VisualEffectLike',
    'bb.mcd.core.componentlike.SceneObjectsReferencerLike',
    'bb.mcd.core.componentlike.RE2PickSessionLike',
    'bb.mcd.core.componentlike.DestroyLike',
    'bb.mcd.core.componentlike.ForcePCWLike',
    'bb.mcd.core.componentlike.ScreenOverlayEnableLike',
    'bb.mcd.core.componentlike.AudioEnableLike',
    'bb.mcd.core.componentlike.SwapMaterialEnableLike',
    'bb.mcd.core.componentlike.ObjectEnableLike',
    'bb.mcd.core.componentlike.SliderColliderLike',
    'bb.mcd.core.componentlike.ComponentByNameLike',
    'bb.mcd.core.componentlike.SpawnerLike',
    'bb.mcd.core.componentlike.CamLockSessionEnableLike',
    'bb.mcd.core.componentlike.DisableComponentLike',
    'bb.mcd.core.componentlike.TextMeshLike',
    'bb.mcd.core.componentlike.PlayableScalarAdapterLike',
    'bb.mcd.core.componentlike.util.ColliderLikeShared',
    'bb.mcd.core.componentlike.router.CLikeToDefaultSetterMap',
    'bb.mcd.core.componentlike.preexport.ComponentLikePreExport',
    'bb.mcd.core.customcomponent.CustomComponentInspector',
    'bb.mcd.core.customcomponent.CustomComponentFilePickPopup',
    'bb.mcd.cdumainpanel.MaterialListPanel',
    'bb.mcd.shareddataobject.SharedDataObject', 
    'bb.mcd.core.command.AddCommandPopup',
    'bb.mcd.cdumainpanel.CommandsPanel',
    'bb.mcd.foo.objectinfo.ObjectInfo',

    'bb.mcd.exporter.ExportOp',
    'bb.mcd.settings.GlobalSettings',
    'bb.mcd.settings.IsArgonMarker',
    'bb.mcd.tools.RemoveAllProperties',
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
     
# THE IMPORT STATEMENTS HAVE TO FOLLOW THE FORMULA : <project-dir>.<sub-dir-A>.<sub-dir-B>.<sub-dir-C>
    #
    # In other words, they need to be absolute paths starting from project-dir.
    # In our case bb is the name of the project-dir, so:
    #
    # Example: from bb.mcd.util import ObjectLookupHelper
    #
    # This way, they import correctly when loading from a zip as a formal addon AND 
    #    when loading via the boot2.py script
