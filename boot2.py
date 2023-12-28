import os
import sys

############################################################
############################################################
# WHEN TO USE THIS BOOT FILE:
#  This boot script (along with __init__.py) enables 'hot reloading' multi-file blender addons. 
#   
#   Follows techniques found here: https://b3d.interplanety.org/en/creating-multifile-add-on-for-blender/
#    See also the top level __init__.py
#
# TO USE: load this file into Blender's script window and hit play
############################################################


def get_project_dir():
    # should return the parent folder of the project folder.
    #  want to add specifically this folder to system path.
    #   edit as needed

    # the folder containing this boot script happens to be the one we want
    import bpy
    from pathlib import Path
    path = Path(bpy.context.space_data.text.filepath)
    return path.parent.absolute().__str__()

    # But no need to provide the path dynamically if this file moved somewhere.
    #  I.e. something like this would be fine:
    # return "E:\\temp\\checktwo\\argon-blender"  



containing = get_project_dir() 

# The name of the top parent module inside of the containing folder 
#  Changing the folder name requires renaming all import statements project-wide
root_module = "bb"

init_file = os.path.join(root_module, "__init__.py")
 
if containing not in sys.path:
    sys.path.append(containing)
 
full_file_path = os.path.join(containing, init_file)
 
if 'DEBUG_MODE' not in sys.argv:
    sys.argv.append('DEBUG_MODE')

exec(compile(open(full_file_path).read(), init_file, 'exec'))
 
if 'DEBUG_MODE' in sys.argv:
    sys.argv.remove('DEBUG_MODE')


