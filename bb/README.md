# Introduction
Argon is a plugin for Unity that lets you configure Unity game objects from within Blender.

Argon has two parts:

* a Blender addon that exports FBX files marked up with custom properties 
* a Unity plugin that imports those files and applies those properties as Unity components.

The import script sets up connections between components as needed.

# Minimum Requirements

* Blender 3.2.1
* Unity 2021.3.55f1

# Installation

* Download the Unity importer. The Unity importer is hosted in a separate repository [here](https://github.com/melsov/argon-slim)
* 
* Install the package using the Unity Package Manager
* Open Blender and open a Preferences view
* Go to Add-ons
* Click the ‘Install…’ button
* Find and install Argon_Plugin_Source.zip under Resources/Blender
* The Argon plugin activation box should come into view (possibly after several seconds)
* Click the check box to activate it
* You should see a new tab on the right side of your 3D views in Blender that is titled ‘Argon’ (Press ‘n’ if you don’t see any right side tabs)

# About the Blender Plugin
Some background that may help if you want to work on the Blender plugin.

## What are Custom Properties in Blender
Any object in blender can have custom properties assigned to it.
In a python script, you assign a custom property like this:

`some_cube['durability'] = 16`

In this case, **some_cube** is a reference to a scene object and the key **durability** is 
a quality of the cube that we care about.

These custom properties will transfer to an FBX file when you export from Blender.

## How Argon Uses Custom Properties
Argon uses custom properties to pass data from Blender to Unity. 

The import script in Unity looks for the presence of certain 'base' keys when it decides what do to with an object.

## Kinds of Keys 
Argon works off of a set of 'base' keys.

**mel_mesh_collider** is an example of a base key.

When the import script sees this key, it adds a MeshCollider to the object that owns the key.

In Blender, when the plugin adds **mel_mesh_collider** to an object it also adds some extra keys:

`mel_mesh_collider_convex`

`mel_mesh_collider_is_trigger`

These keys store the actual configuration data for the MeshCollider component.

Some base keys don't add extra keys because they only store one primitive value.
For example, **mel_layer** just needs to store a string representing the name of a physics layer in Unity.

The default base keys are defined in a json object in the file: **MCDKeyValueConfig.py**

## How Argon Makes Custom Properties Editable in the UI
When an object is selected in Blender, Argon does the following:

* Go through all base keys.
    * For each base key:
        *   check if that key is defined on the selected object
        *   If it is, make its value or values editable in the UI. 

        
There are two ways to make the value or values editable: the single primitive value case and the collection of values case 

* In the **single primitive value case**, the base key just holds a single primitive type.
    For example, the base key **mel_layer** holds a string representing the name of a layer in Unity (e.g. "IgnoreCollisions").
    In this case, the inspector module doesn't need to defer to a ComponentLike class. It just draws an editable property using Blender's prop() method.
    (The relevant code is in Inspector.py)

* In the **collection of values case**, the base key is associated with a set of values. Usually this is because the base key represents a Unity component. 
    * For example, the base key **"mel_mesh_collider"** represents a MeshCollider in Unity.
    * When a mesh_collider component is added to an object, the object will end up having the following keys defined on it:
        * "mel_mesh_collider"  -- the base key. holds no actual data; it's just a marker
        * "mel_mesh_collider_convex"  -- holds a bool value
        * "mel_mesh_collider_is_trigger" -- holds another bool value
        
If **"mel_mesh_collider"** is defined on the active object, the inspector finds the custom-component display class--or the 'ComponentLike' class--that knows how to display it.
**"mel_mesh_collider's"** ComponentLike class is **MeshColliderLike.py.**


## About ComponentLikes
Custom components display classes--**ComponentLikes**--usually manage sets of properties: for example, as mentioned above, MeshColliderLike handles displaying and editing the 'convex' and 'isTrigger' properties.

### ComponentLikes are Like Static Classes
Argon only creates **one instance** of each ComponentLike class per scene. (And each of these instances
    is owned by the .Scene object.)  Each ComponentLike class **is like a static class**.
    
For example, there is only one instance of MeshColliderLike. And the Scene owns it. It's defined like this:  
    
    bpy.types.Scene.meshColliderLike = bpy.props.PointerProperty(type=MeshColliderLike)

### How ComponentLikes Do Their Job
There is only one instance of each ComponentLike per Blender scene. ComponentLikes don't own references to the objects that they target. They just define fields (of type bpy_struct, Property) that Blender knows how to draw. The getter and setter functions defined in each field in a ComponentLike handle the actual reading and writing of data from/to the target object.

### How ComponentLikes Do Their Job in More Detail

Each ComponentLike class defines fields (instance variables) for each value that it needs to expose to the user. Each field defines a getter and setter that reads and writes to the actual relevant value by reading and writing from/to **a custom property of the active object.**

In other words, each field in a display class, is **just a wrapper** around a custom property **on the current select object**; it doesn't own any actual data, (so it doesn't duplicate any data).

For example, MeshColliderLike defines an **isTrigger** field:
    
    isTrigger : BoolProperty(
        name="isTrigger",
        default = False,
        get=getIsTrigger,
        set=setIsTrigger)
    

When the user edits the isTrigger field of the active object, the isTrigger field's setter function `setIsTrigger` writes the new bool value to a custom prop on the active object. I.e. something like this happens: 

    active_ob["mel_mesh_collider_is_trigger"] = val

Similarly, isTrigger's getter function `getIsTrigger` reads from the active object. I.e. something like this happens:

    return active_ob["mel_collider_is_trigger"]

To see which properties exist on an object in Blender and see their values: select the object, click the Object Properties tab (the square icon in the Properties window) and looking under Custom Properties.

### Why are ComponentLikes Only Instanced Once Per Scene?
Why have only one instance of each custom component class? With many custom component classes and potentially many objects in a scene, assigning an instance of each class to each object might lead to performance issues.

### These Custom Display Classes Seem Like They Should Really Just Be a Collection of Static Functions.
Why aren't they just a collection of static functions? They would be except that the fields need to be non-static Blender Properties (e.g. IntProperty, BoolProperty) so that we can draw them with Blender's UI functions.




