# What are Custom Properties in Blender
Any object in blender can have custom properties assigned to it.
For example:

`some_cube['durability'] = 16`

In this case, **some_cube** is a reference to a scene object and 'durability' is 
a quality of the cube that we care about.

These custom properties will transfer to an FBX file when you export from Blender.

## How Argon Makes Custom Properties Editable in the UI
Argon works off of a list of 'base' keys defined in a json object.
Currently that json object is in this file: **MCDKeyValueConfig.py**

When an object is selected, Argon does the following:

* Goes through all base keys.
    * For each base key:
        *   checks if that key is defined on the selected object
        *   If it is, Argon makes its value or values editable in the UI. 
        
There two ways to make the value or values editable. The simple case and the less simple case 

* In the **simple case**, the base key just holds a single primitive type.
    For example, the base key "mel_layer" holds a string representing the name of a layer in Unity (e.g. "IgnoreCollisions").
    In this case, the inspector module doesn't need to defer to a ComponentLike class. It just draws an editable property using blender's prop() method.
    (The relevant code is in Inspector.py)

* In the **less simple case**, the base key is associated with a set of values. Usually this is because the base key represents a Unity component. 
* For example, the base key **"mel_mesh_collider"** represents a MeshCollider in Unity.
* When a mesh_collider component is added to an object, the object will end up having the following keys defined on it:
    * "mel_mesh_collider"  -- the base key. holds no actual data; just a marker
    * "mel_mesh_collider_convex"  -- holds a bool value
    * "mel_mesh_collider_is_trigger" -- holds another bool value
    
If **"mel_mesh_collider"** is defined on the active object, the inspector code finds the custom-component display class--or the 'ComponentLike' class--that knows how to display it.
**"mel_mesh_collider's"** ComponentLike class is **MeshColliderLike.py.**


## About ComponentLikes
Custom components display classes--**ComponentLikes**--usually show sets of properties: for example, as mentioned above, MeshColliderLike handles displaying and editing the 'convex' and 'isTrigger' properties.

### ComponentLikes are Like Singletons
Argon (usually) only creates **one instance** of each ComponentLike class per scene. (And each of these instances
    is defined on the .Scene object.) Each ComponentLike class **is like an informal singleton**.
    
For example, there is only one instance of MeshColliderLike. And the Scene owns it. It's defined like this:  
    
    bpy.types.Scene.meshColliderLike = bpy.props.PointerProperty(type=MeshColliderLike)

### How ComponentLikes Do Their Job
There is only one instance of each ComponentLike per Blender scene. ComponentLikes don't own references to the objects that they target. They just define fields (of type bpy_struct, Property) that Blender knows how to draw. The getter and setter functions defined in each field handle the actual reading and writing of data to the target object.

### How ComponentLikes Do Their Job in More Detail

Each ComponentLike class defines fields (instance variables) for each value that it needs to expose to the user. Each field defines a getter and setter that reads and writes to the actual relevant value by reading and writing from/to **a custom property of the active object.**

In other words, each field in a display class, is **just a wrapper** around a custom property **on the current select object**; it doesn't own any actual data, so it doesn't duplicate any data.

For example, MeshColliderLike defines an **isTrigger** field:
    
    isTrigger : BoolProperty(
        name="isTrigger",
        default = False,
        get=getIsTrigger,
        set=setIsTrigger)
    

Notice the `getIsTrigger` and `setIsTrigger` functions. **isTrigger** doesn't own any references to any specific object--even objects that have the "mel_mesh_collider" property. 

When the user edits the isTrigger field of the active object, the isTrigger field's setter function writes the new bool value to a custom prop on the active object. I.e. something like this happens: 

    active_ob["mel_mesh_collider_is_trigger"] = val

Similarly, isTrigger's getter function reads from the active object. I.e. something like this happens:

    return active_ob["mel_collider_is_trigger"]

To see which properties exist on an object in Blender and see their values: select the object, click the Object Properties tab (the square icon in the Properties window) and looking under Custom Properties.

### Why
Why have only one instance of each custom component class? With many custom component classes and potentially many objects in a scene, assigning an instance of each class to each object might lead to performance issues.

These custom display classes seem like they should really just be a collection of static functions. Why aren't they just a collection of static functions? They would be except that the fields need to be non-static Blender Properties (e.g. IntProperty, BoolProperty) so that we can draw them with Blender's UI functions.




