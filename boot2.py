import os
import sys

def get_project_dir():
    """get the directory path containing this boot script"""
    # NO LONGER needs to next to """get our particular directory which must be next to this .blend"""
    import bpy
    import pathlib

    # TEST
    DcurDir = bpy.context.space_data.text.filepath # $ os.path.dirname(os.path.realpath(__file__))
    print(F"cur dir type: {type(DcurDir)} ::  {os.path.dirname(DcurDir)}")
    return os.path.dirname(DcurDir)

    # PREV
    # path = pathlib.Path(bpy.data.filepath)
    # path_containing_blend = path.parent.resolve()
    # path_containing_blend = str(path_containing_blend) #very important, otherwise it will be a Path-object and unusable for sys.path
    # project_folder_name = 'bb'
    # return F"{path_containing_blend}\\{project_folder_name}"  

filesDir = get_project_dir() 

initFile = "__init__.py"
 
if filesDir not in sys.path:
    sys.path.append(filesDir)
 
file = os.path.join(filesDir, initFile)
 
if 'DEBUG_MODE' not in sys.argv:
    sys.argv.append('DEBUG_MODE')

print(F"PROJ DIR: {filesDir} ")
print(F"FILE: {file}")
 
exec(compile(open(file).read(), initFile, 'exec'))
 
if 'DEBUG_MODE' in sys.argv:
    sys.argv.remove('DEBUG_MODE')

# print(F"my package is named: {__package__}")
# __package__ = "bob.the.package"
# print(F"my package is named: {__package__}")


# HOW TO Package this project as an addon
#   The main thing is that the absolute import paths work differently
#     It may be that we could finesse the top level __init__
#       so that we didn't have to adjust anythhing. But for now, what works is:
#     adding the parent folder (named 'bb' at the moment) to each import statement.
#    so mcd.some.module becomes bb.mcd.some.module  
#    Use a replace-all command to make this easier (and making a copy of the entire project is recommend)
# 


# NOTES: feel free to ignore:
# S.O. regarding reloading modules from blender's python editor: https://blender.stackexchange.com/a/255605/100992

# This script follows: https://b3d.interplanety.org/en/creating-multifile-add-on-for-blender/
# It performs a number of contortions that enable reloading/re-running multi-file add-ons
#   from blender's editor window. See also the project dir's __init__.py (more contortions)
