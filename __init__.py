bl_info = {
    'name': 'MelCustomDataUtilBA',
    # 'category': 'All',
    'version': (0, 0, 1),
    'blender': (2, 78, 0),
    "location": "View3D > Sidebar > MelPropHelper",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View" 
}




# See notes at the end of this file for a reminder of what/how to import modules using this list
modulesNames = [
    'more_stuff_here.more',
    'mcd.melstor.MCDKeyValConfig',
    'mcd.lookup.KeyValDefault',
    'mcd.util.ObjectLookupHelper',
    'mcd.util.AppHandlerHelper',    
    'mcd.ui.KeyValItem',
    'mcd.ui.Inspector',
    'mcd.ui.InspectorPopup',
    'mcd.ui.componentlike.StaticFlags',
    'mcd.MelCustomDataUtilBA',
    'mcd.cduoperator.SelectByKey',
    'mcd.cduoperator.AddKeyToSelected',
    'mcd.util.DisplayHelper',
    'mcd.ui.componentlike.adjunct.NumExtraPlayables',

    # scene level var declarations
    'mcd.ui.export.ExportBox',
    'mcd.ui.materiallist.MaterialList',
    'mcd.ui.actionstarterlist.CUSTOM_PG_AS_Collection',
    'mcd.ui.actionstarterlist.ActionStarterList',

    'mcd.ui.actionstarterlist.OT_TarAnimsList',
    'mcd.util.JsonFromItem',
    'mcd.cduoperator.SetKeyValue',
    'mcd.ui.SelectByKeyMenu',
    'mcd.ui.AddKeyMenu',
    'mcd.ui.componentlike.util.ComponentLikeUtils',
    'mcd.ui.componentlike.enablefilter.EnableFilterSettings',
    'mcd.ui.componentlike.enablefilter.SleepStateSettings',
    'mcd.ui.componentlike.util.ObjectPointerMsgbusUtils',
    'mcd.ui.componentlike.AbstractPerObjectData',
    'mcd.ui.componentlike.AbstractComponentLike',
    'mcd.ui.componentlike.StorageRouter',
    'mcd.ui.componentlike.AbstractDefaultSetter',
    'mcd.ui.componentlike.MeshColliderLike',
    'mcd.ui.componentlike.BoxColliderLike',
    # 'mcd.ui.componentlike.ActionStarterLike',
    'mcd.prefs.MelCustomDataUtilPreferences', # may have to stuff the prefs back into MelCDUBA. because its bl_idname has to match...etc.
    'mcd.exporter.edyj.BlenderToUnityFbxExporter',
    'mcd.exporter.default.DefaultFBXExporter',
    'mcd.ui.componentlike.RigidbodyLike',
    'mcd.ui.componentlike.LightEnableLike',
    'mcd.ui.componentlike.OffMeshLinkLike',
    'mcd.ui.componentlike.unityinfo.UnityPaths',
    'mcd.ui.componentlike.InteractionHandlerLike',
    'mcd.ui.componentlike.InteractionHighlighterLike',
    'mcd.ui.componentlike.EnableReceiverLike',
    'mcd.ui.componentlike.ParticleSystemLike',
    'mcd.ui.componentlike.ScreenOverlayEnableLike',
    'mcd.ui.componentlike.AudioEnableLike',
    'mcd.ui.componentlike.ObjectEnableLike',
    'mcd.ui.componentlike.SliderColliderLike',
    'mcd.ui.componentlike.ComponentByNameLike',
    'mcd.ui.componentlike.SpawnerLike',
    'mcd.ui.componentlike.CamLockSessionEnableLike',
    'mcd.ui.componentlike.DisableComponentLike',
    'mcd.ui.componentlike.TextMeshLike',
    'mcd.ui.materiallist.MaterialListPanel',
    'mcd.shareddataobject.SharedDataObject',
    'mcd.ui.materiallist.MaterialListExporter',
    # 'mcd.ui.componentlike.actionstarters.ActionStarterData',
    'mcd.ui.actionstarterlist.PlusActionStarterPopup',
    'mcd.ui.actionstarterlist.ActionStarterPanel',
    'mcd.objectinfo.ObjectInfo',
    'mcd.ui.componentlike.enablereceiverbutton.EnableReceiverButton',
    ]





import sys
import importlib

def TryLoadMCDTest(moduleFolder="mcd"):
    # TRY TECHNIQUE FROM:
    #  https://b3d.interplanety.org/en/how-to-import-a-python-module-by-the-absolute-path/
    def get_current_dir():
        return "C:\\Users\\melsov\\AppData\\Roaming\\Blender Foundation\\Blender\\3.2\\scripts"
        """get our particular directory which must be next to this .blend"""
        import bpy
        import pathlib
        path = pathlib.Path(bpy.data.filepath)
        path_containing_blend = path.parent.resolve()
        path_containing_blend = str(path_containing_blend) #very important, otherwise it will be a Path-object and unusable for sys.path
        project_folder_name = 'bb'
        return F"{path_containing_blend}\\{project_folder_name}"  
    
    moduleFolder = moduleFolder.replace(".", "\\") # note this is windows centric yikes

    path = F"{get_current_dir()}\\addons\\bb\\{moduleFolder}\\__init__.py"
    name = "mcd"

    import importlib
    import sys
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

# if 'DEBUG_MODE' not in sys.argv:
#     TryLoadMCDTest("mcd")
#     TryLoadMCDTest("mcd.melstor")
#     TryLoadMCDTest("more_stuff_here")

 
modulesFullNames = {}
print(F"DEBUG MODE? {'DEBUG_MODE' in sys.argv }")
for currentModuleName in modulesNames:
    if 'DEBUG_MODE' in sys.argv:
        modulesFullNames[currentModuleName] = ('{}'.format(currentModuleName))
    else:
        modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))
    # print(F" MODULE NAMES: {modulesFullNames[currentModuleName] } ")
 
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)
 
def register():
    print(F"welcome to register bb")
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            # print(F" curr module: {currentModuleName}")
            if hasattr(sys.modules[currentModuleName], 'register'):
                print(F"REG: {currentModuleName} ")
                sys.modules[currentModuleName].register()
 
def unregister():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                print(F"UNREG: {currentModuleName}")
                sys.modules[currentModuleName].unregister()
 
print(F" is name main?? {__name__}")
if __name__ == "__main__":
    print(F" will register")
    register()


# HOW TO DO A MULTI-FILE MODULE:
#  add the modules absolute name to moduleNames list
#   (where absolute name means its 'dot' name relative to the project folder root 
#      which we should have added to sys.path; but not starting with a dot)
#   if the module includes blender class(es) that should register,
#    you probably want to include register/unregister definitions in the module file. 
#    its easiest to keep track of who is registering when this way.
#  even if there are no blender classes in the module, still add its name to moduleNames
#   because this way it will be reloaded. meaning changes to the file will show up right away; without restarting blender
#  if a module needs to import another module, just use "import othermodule" or "from another.thing import something"
#   QUESTION: do we actually need to import or are we merely making intellisense work?
#     ANSWER: seems like it's doing more? a brief test suggested that without an import statement at the top of the module
#       the (not) imported function worked but it was a previous cached version..
# Lastly, it seems that we still need to restart blender entirely when we add a new file.