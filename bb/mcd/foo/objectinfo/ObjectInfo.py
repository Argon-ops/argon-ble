import bpy
from bb.mcd.shareddataobject import SharedDataObject

def DgetProps(obj):
    try:
        for prop, val in vars(obj).items():
            print(prop, " : ", val)
    except:
        print(F"trouble")

def DgetAnimInfo(lookup):
    for ob in bpy.context.scene.objects :
        print(F" %%% {ob.name} %%% ")
        if ob.type not in ['MESH','ARMATURE']:
            continue
        if ob.animation_data:
            print(F"   anim data action : {ob.animation_data.action.name if ob.animation_data.action else '<actn is None>'} ")
            # for fc in ob.animation_data.action.fcurves:
            #     if fc.data_path.endswith(('location','rotation_euler','rotation_quaternion','scale')):
            #         for key in fc.keyframe_points :
            #             print('frame:',key.co[0],'value:',key.co[1])
            # nla tracks
            if ob.animation_data.nla_tracks:
                tracks = ob.animation_data.nla_tracks
                for track in ob.animation_data.nla_tracks:
                    print(F"   NLA track name: {track.name if track is not None else '<trak is None>'}")
                    for strip in track.strips:
                        print(F"    strip action: {strip.action.name}")
        