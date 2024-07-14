
config = """
{
    "mel_mesh_collider" : {
        "default" : {
            "convex" : true,
            "isTrigger" : false
        },
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a mesh collider component"
    },
    "mel_static_flags" : {
        "default" : {
            "testIsOn" : false
        },
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Apply static flags"
    },
    "mel_rigidbody" : {
        "default" : { 
            "todoDecideWhatThisVarMeans" : "ok"
        },
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a rigidbody to this game object"
    },
    "mel_no_renderer" : {
        "hint" : "TAG",
        "help" : "Remove this game object's renderer during import"
    },
    "mel_destroy" : {
        "hint" : "CUSTOM_INSPECTOR",
        "default" : {
            "meaningless-key" : 41
        },
        "help" : "Destroy this game object and possibly its children during post-processing"
    },
    "mel_force_pcw" : {
        "hint" : "CUSTOM_INSPECTOR",
        "default" : {
            "meaningless-key" : 41
        },
        "help" : "Force the import script to add PlayableClipWrappers for any animation clips associated with this object"
    },
    "mel_tag" : {
        "default" : "",
        "hint" : "PRIMITIVE",
        "help" : "Set this game object's tag. Case-insensitive"
    },
    "mel_layer" : {
        "default" : "",
        "hint" : "PRIMITIVE",
        "help" : "Set this game object's layer. Case-insensitive"
    },
    "mel_layer_cam_lock_pickable" : {
        "default" : { "isTrigger" : false },
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Put this object on the Argon-specific layer 'CamLockPickable'"
    }, 
    "mel_replace_with_prefab" : {
        "default" : "prefab-name",
        "hint" : "PRIMITIVE",
        "help" : "Replace this mesh with a prefab"
    },
    "mel_off_mesh_link" : {
        "default" : { "meaningless-key" : 42 },
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add and configure an off mesh link on this game object"
    },
    "mel_box_collider" : {
        "default" : { "isTrigger" : false },
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a box collider component to this game object. Size will match the object's bounds"
    },
    "mel_scene_objects_referencer" : {
        "default" : { },
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a SceneObjectsReferencer component"
    },
    "mel_interaction_handler" : {
        "default" : {
            "playable" : "",
            "allows_interrupt" : false,
            "enter_signal" : 1.0,
            "interaction_type" : 0
        },
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Adds a interaction handler component"
    },
    "mel_interaction_highlighter" : {
        "default" : {},
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Adds an object highlighter."
    },
    "mel_enable_receiver" : {
        "default" : {},
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Adds a enable receiver component"
    },
    "mel_object_enable" : {
        "default" : {},
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Adds an object enable component"
    },
    "mel_screen_overlay_enable" : {
        "default" : {},
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a screen overlay enable component"
    },
    "mel_audio_enable" : {
        "default" : {},
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add an audio enable component"
    },
    "mel_swap_material_enable" : {
        "default" : {},
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a swap material enable component"
    },
    "mel_slider_collider" : {
        "default" : {},
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a slider collider component"
    },
    "mel_particle_system" : {
        "default" : {
            "default_name" : ""
        },
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a particle system prefab during import"
    },
    "mel_visual_effect" : {
        "default" : {
            "default_name" : ""
        },
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a visual effect prefab during import"
    },
    "mel_re2_pick_session" : {
        "default" : {
            "default_name" : ""
        },
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a Resident Evil 2 style pick session component"
    },
    "mel_spawner" : {
        "default" : {},
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a prefab spawner"
    },
    "mel_component_by_name" : {
        "default" : {},
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add the specified component during import"
    },
    "mel_cam_lock_session_enable" : {
        "default" : {},
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a CamLockSessionEnable component"
    },
    "mel_disable_component" : {
        "default" : {},
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Disable the specified component(s) attached to this object during import. Separate component names with commas."
    },
    "mel_text_mesh" : {
        "default" : {},
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a text mesh to the current game object"
    },
    "mel_playable_scalar_adapter" : {
        "default" : {},
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a Playable Scalar Adapter"
    },
    "mel_cam_swap_managed" : {
        "hint" : "TAG",
        "help" : "Add this object's camera component to the list of cameras that are managed by CamSwap"
    },
    "test_mreceptacle" : {
        "default" : {
            "aa" : "hello",
            "bb" : 23
        },
        "hint" : "CUSTOM_COMPONENT",
        "help" : "Experiment with custom component definitions. Shouldn't really be defined here but putting here for now",
        "apply_class" : "FakeComponent"
    }

}
"""

graveyard="""
{
    "mel_action_starter" : {
        "default" : { 
            "animName" : "",
            "fakeOtherKey" : 23
        },
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Adds an animation action starter to this object."
    },
    "mel_light_enable" : {
        "default" : {},
        "hint" : "CUSTOM_INSPECTOR",
        "help" : "Add a light during import"
    },
}
"""