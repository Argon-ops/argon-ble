import bpy
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       BoolProperty,
                       CollectionProperty,)
from bpy.types import (PropertyGroup,)
from bb.mcd.ui.componentlike.util import ComponentLikeUtils as CLU


class SleepStateSettings(PropertyGroup):
    """
    Define properties for component-likes that need to support sleep-state configuration

    Component-likes that need to support sleep-state configuration should multi-inherit from this
    class and AbstractComponentLike
    """

    IS_SLEEPSTATE_CLASS = 42

    Suffixes = {
        "_set_initial_sleep_state": 0
    }

    setInitialSleepState: EnumProperty(
        description="This component implements ISleep, meaning that it can be put in a sleeping (unresponsive) or waking (responsive) state. This field defines what its initial state should be set to at start up",
        items=(
            ('DoNothing', 'Don\'t set initial state', 'Do nothing at start up'),
            ('Awake', 'Awake', 'Set enabled at start up'),
            ('Asleep', 'Asleep', 'Set disabled at start up')
        ),
        get=lambda self: CLU.getIntFromKey(
            self.Append("_set_initial_sleep_state")),
        set=lambda self, value: CLU.setValueAtKey(
            self.Append("_set_initial_sleep_state"), value)
    )

    @classmethod
    def displaySleepSettings(cls, box):
        # (!) Assumes that the class referenced by 'cls' is also an AbstractComponentLike
        self = cls.GetSceneInstance()
        boxb = box.box()
        boxb.row().prop(self, "setInitialSleepState", text="Initial Sleep State")


classes = (
    SleepStateSettings,
)


def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class
    for c in classes:
        unregister_class(c)
