import bpy

# selection = bpy.context.selected_objects

    
# def listActions(b):
#     print(F"actions of {b.name}")
#     if not b.animation_data:
#         print(F"no anim data for: {b.name}")
#         print(F"-----")
#         return
#     if b.animation_data.action:
#         print(F"found action for {b.name} : {b.animation_data.action.name}")
#     # Actions spread themselves to objects that don't seem to be associated with them.
#     #   i.e. the action isn't listed under the object's animations--yet it still turns up as an ObName|ActionName in Unity
#     #  YOU'D THINK: that we'd find a trace of this hard to find linkage in nla_tracks but no.
#     #  FOR NOW: this spreading is actually what we want?? it reflects what you see in BLe when you play the action??
#     for track in b.animation_data.nla_tracks:
#         for s in track.strips:
#             print(F"found nla track strip with action: {s.action.name}")
    
# for ob in selection:
#     listActions(ob)


owner = object()
bpy.msgbus.clear_by_owner(owner)

# subscribe_to = bpy.context.object.location
subscribe_to = (bpy.types.Action, "name") # OKAY this does the trick


def msgbus_callback(*args):
    # This will print:
    # Something changed! (1, 2, 3)
    print("Something changed!", args)


bpy.msgbus.subscribe_rna(
    key=subscribe_to,
    owner=owner,
    args=(1, 2, 3),
    notify=msgbus_callback,
)