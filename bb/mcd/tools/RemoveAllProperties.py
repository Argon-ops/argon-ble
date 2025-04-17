
import bpy


def RM_ALL_PROPERTIES_FOR_REAL():

    _rmArgonDataOnObjects([ob for ob in bpy.context.selected_objects])
    # for o in bpy.context.scene.objects:
    #     print(F"{o.name}")

def _rmArgonDataOnObjects(obs):
    for o in obs:
        for key, val in o.items():
            print(F"got key: {key}")



classes = (
    # InputOperator,
)


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)



def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)

