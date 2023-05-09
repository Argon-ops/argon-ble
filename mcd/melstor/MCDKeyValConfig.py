
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
        "hint" : "PRIMITIVE",
        "default" : 0,
        "help" : "Destroy this game object and its children during post-processing"
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
        "help" : "Add a particle system component during import"
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
}
"""