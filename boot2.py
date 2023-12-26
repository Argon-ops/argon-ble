import os
import sys

# USE THIS BOOT FILE:
#  To 'hot reload' your multi-file blender addon. 
#   Follows techniques found here: https://b3d.interplanety.org/en/creating-multifile-add-on-for-blender/


def get_project_dir():
    # should return the parent folder of the project folder.
    #  we want to put specifically this folder to systhem path.
    #   edit as needed
    return "E:\\temp\\ble-zip-import-test\\bb_zip_import_me"  

containing = get_project_dir() 

init_file = os.path.join("bb", "__init__.py")
 
if containing not in sys.path:
    sys.path.append(containing)
 
full_file_path = os.path.join(containing, init_file)
 
if 'DEBUG_MODE' not in sys.argv:
    sys.argv.append('DEBUG_MODE')

print(F"Boot from PROJ DIR: {containing} FILE: {init_file}")
 
exec(compile(open(full_file_path).read(), init_file, 'exec'))
 
if 'DEBUG_MODE' in sys.argv:
    sys.argv.remove('DEBUG_MODE')


