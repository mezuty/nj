# =====================================================================================
#  WW LASHWINDUP  (kit slot WW_ANIMS.LashWindup, played at speed 1.2)
#  Rig: MrXen0 R15 (Roblox_R15) | 60 fps | 25 frames (0.416667 s) | UPPER-BODY ONLY (cast-while-moving: no TORSO / legs / feet tracks)
#  HOW TO USE: open your MrXen0 R15 .blend -> Scripting tab -> Open/paste this file -> Run Script.
#  It removes the old animation first (unassigns the current action, deletes any earlier copy of
#  "WW_LashWindup", clears the pose), then keys ONLY the animated FK controls with BEZIER / AUTO_CLAMPED
#  curves. Frame map: no markers
# =====================================================================================
import bpy

ACTION_NAME = "WW_LashWindup"
FRAME_END = 24
CYCLIC = False
FRAMES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 24]
# bone -> {data_path: [per-key rows]}   (radians / studs; TORSO is quaternion)
DATA = {"UpTorso":{"rotation_euler":[[-0.0,0.0,0.0],[-0.0,0.0,0.0],[-0.0,0.0,0.0],[0.00132,-0.00288,0.0],[0.00496,-0.01087,0.0],[0.01042,-0.02302,0.0],[0.01719,-0.03839,0.0],[0.02478,-0.05602,0.0],[0.03269,-0.07495,0.0],[0.04042,-0.09423,0.0],[0.04748,-0.11291,0.0],[0.05381,-0.13144,0.0004],[0.06089,-0.15446,0.00268],[0.06862,-0.18131,0.00662],[0.07671,-0.21068,0.01181],[0.08488,-0.24126,0.01785],[0.09283,-0.27175,0.02434],[0.10029,-0.30085,0.03087],[0.10695,-0.32726,0.03704],[0.11254,-0.34966,0.04243],[0.11676,-0.36676,0.04665],[0.11933,-0.37725,0.0493],[0.12,-0.38,0.05],[0.12,-0.38,0.05],[0.12,-0.38,0.05],[0.12,-0.38,0.05]]},"HEAD":{"rotation_euler":[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.00064,0.00281,0.0],[0.00429,0.01875,0.0],[0.01059,0.04631,0.0],[0.01889,0.08267,0.0],[0.02856,0.12497,0.0],[0.03895,0.1704,0.0],[0.04939,0.2161,0.0],[0.05926,0.25926,0.0],[0.06789,0.29703,0.0],[0.07465,0.32658,0.0],[0.07887,0.34507,0.0],[0.08,0.35,0.0],[0.08,0.35,0.0]]},"FK_UpperArm.R":{"rotation_euler":[[0.05,-0.0,0.06],[0.06957,-0.0,0.06677],[0.12154,-0.0,0.08527],[0.19577,-0.0,0.11277],[0.28216,-0.0,0.14651],[0.37056,-0.0,0.18378],[0.45087,-0.0,0.22183],[0.51296,-0.0,0.25794],[0.54671,-0.0,0.28936],[0.52675,-0.0012,0.31546],[0.39466,-0.00803,0.34293],[0.16627,-0.01985,0.37178],[-0.13494,-0.03543,0.40115],[-0.48547,-0.05356,0.43015],[-0.86185,-0.07303,0.45792],[-1.24057,-0.09262,0.48359],[-1.59815,-0.11111,0.50628],[-1.9111,-0.1273,0.52512],[-2.15593,-0.13996,0.53925],[-2.30916,-0.14789,0.54778],[-2.35,-0.15,0.55],[-2.35,-0.15,0.55],[-2.35,-0.15,0.55],[-2.35,-0.15,0.55],[-2.35,-0.15,0.55],[-2.35,-0.15,0.55]]},"FK_LowerArm.R":{"rotation_euler":[[-0.12,-0.0,0.0],[-0.12,-0.0,0.0],[-0.12,-0.0,0.0],[-0.12,-0.0,0.0],[-0.12804,-0.0,0.0],[-0.15072,-0.0,0.0],[-0.1859,-0.0,0.0],[-0.23141,-0.0,0.0],[-0.28512,-0.0,0.0],[-0.34486,-0.0,0.0],[-0.40849,-0.0,0.0],[-0.47385,-0.0,0.0],[-0.54672,-0.0008,0.0],[-0.65473,-0.00536,0.0],[-0.79284,-0.01323,0.0],[-0.95231,-0.02362,0.0],[-1.12441,-0.03571,0.0],[-1.3004,-0.04868,0.0],[-1.47154,-0.06174,0.0],[-1.62911,-0.07407,0.0],[-1.76436,-0.08487,0.0],[-1.86857,-0.09331,0.0],[-1.93298,-0.09859,0.0],[-1.95,-0.1,0.0],[-1.95,-0.1,0.0],[-1.95,-0.1,0.0]]},"FK_Hand.R":{"rotation_euler":[[0.15,0.0,0.0],[0.15,0.0,0.0],[0.15,0.0,0.0],[0.15,0.0,0.0],[0.15,0.0,0.0],[0.15,0.0,0.0],[0.15,0.0,0.0],[0.15196,0.0,0.0],[0.15715,0.0,0.0],[0.16458,0.0,0.0],[0.17322,0.0,0.0],[0.18206,0.0,0.0],[0.19009,0.0,0.0],[0.1963,0.0,0.0],[0.19967,0.0,0.0],[0.19639,0.0,0.0008],[0.1759,0.0,0.00536],[0.14046,0.0,0.01323],[0.09372,0.0,0.02362],[0.03932,0.0,0.03571],[-0.01908,-0.0,0.04868],[-0.07785,-0.0,0.06174],[-0.13333,-0.0,0.07407],[-0.18189,-0.0,0.08487],[-0.21989,-0.0,0.09331],[-0.21989,-0.0,0.09331]]},"FK_UpperArm.L":{"rotation_euler":[[0.05,0.0,-0.06],[0.0325,0.0,-0.07175],[-0.01477,0.0,-0.10324],[-0.08392,0.0,-0.14886],[-0.16709,0.0,-0.203],[-0.2564,0.0,-0.26003],[-0.34398,0.0,-0.31435],[-0.42196,0.0,-0.36033],[-0.48246,0.0,-0.39235],[-0.52307,0.0,-0.40883],[-0.56144,0.0,-0.42298],[-0.59914,0.0,-0.43632],[-0.63552,0.0,-0.44874],[-0.66992,0.0,-0.4601],[-0.70167,0.0,-0.47029],[-0.73013,0.0,-0.47918],[-0.75462,0.0,-0.48666],[-0.7745,0.0,-0.4926],[-0.78911,0.0,-0.49688],[-0.79778,0.0,-0.49937],[-0.8,0.0,-0.5],[-0.8,0.0,-0.5],[-0.8,0.0,-0.5],[-0.8,0.0,-0.5],[-0.8,0.0,-0.5],[-0.8,0.0,-0.5]]},"FK_LowerArm.L":{"rotation_euler":[[-0.12,0.0,0.0],[-0.12,0.0,0.0],[-0.12,0.0,0.0],[-0.12,0.0,0.0],[-0.12946,0.0,0.0],[-0.15487,0.0,0.0],[-0.19178,0.0,0.0],[-0.23573,0.0,0.0],[-0.28228,0.0,0.0],[-0.32697,0.0,0.0],[-0.36535,0.0,0.0],[-0.39296,0.0,0.0],[-0.40851,0.0,0.0],[-0.42228,0.0,0.0],[-0.4354,0.0,0.0],[-0.44774,0.0,0.0],[-0.45913,0.0,0.0],[-0.46943,0.0,0.0],[-0.47849,0.0,0.0],[-0.48616,0.0,0.0],[-0.49229,0.0,0.0],[-0.49673,0.0,0.0],[-0.49934,0.0,0.0],[-0.5,0.0,0.0],[-0.5,0.0,0.0],[-0.5,0.0,0.0]]},"FK_Hand.L":{"rotation_euler":[[0.15,0.0,-0.0],[0.15,0.0,-0.0],[0.15,0.0,-0.0],[0.15,0.0,-0.0],[0.15,0.0,-0.0],[0.15,0.0,-0.0],[0.15,0.0,-0.0],[0.15196,0.0,-0.0],[0.15715,0.0,-0.0],[0.16458,0.0,-0.0],[0.17322,0.0,-0.0],[0.18206,0.0,-0.0],[0.19009,0.0,-0.0],[0.1963,0.0,-0.0],[0.19967,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0]]}}
# gameplay sync markers (frame numbers) - the HIT/SLAM/etc. moments the ability script fires its effects on
MARKERS = {}


def find_rig():
    ob = bpy.data.objects.get("Roblox_R15")
    if ob is None or ob.type != 'ARMATURE':
        for o in bpy.data.objects:
            if o.type == 'ARMATURE' and "FK_UpperArm.R" in o.pose.bones:
                return o
        raise RuntimeError("Roblox_R15 armature not found - open the MrXen0 R15 rig first.")
    return ob


def iter_fcurves(action):
    if hasattr(action, "layers"):                      # Blender 4.4+/5.x slotted actions
        for layer in action.layers:
            for strip in layer.strips:
                for bag in getattr(strip, "channelbags", []):
                    for fc in bag.fcurves:
                        yield fc
    else:
        for fc in action.fcurves:
            yield fc


def main():
    rig = find_rig()
    bpy.context.view_layer.objects.active = rig
    scene = bpy.context.scene
    scene.render.fps = 60
    scene.render.fps_base = 1.0

    # ---- 1. remove the old animation (no lingering keys) --------------------------------
    if rig.animation_data is None:
        rig.animation_data_create()
    rig.animation_data.action = None
    for act in list(bpy.data.actions):
        if act.name == ACTION_NAME or act.name.startswith(ACTION_NAME + "."):
            act.use_fake_user = False
            bpy.data.actions.remove(act)
    for pb in rig.pose.bones:                            # clean slate
        pb.location = (0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.scale = (1, 1, 1)
    props = rig.pose.bones.get("PROPERTIES")
    if props is not None:                               # FK mode
        for k in ("ARM_IK_FK.L", "ARM_IK_FK.R", "LEG_IK_FK.L", "LEG_IK_FK.R"):
            if k in props:
                props[k] = 0.0

    # ---- 2. new action ---------------------------------------------------------------------
    action = bpy.data.actions.new(ACTION_NAME)
    action.use_fake_user = True
    rig.animation_data.action = action
    for bone, chans in DATA.items():
        pb = rig.pose.bones[bone]
        pb.rotation_mode = 'QUATERNION' if "rotation_quaternion" in chans else 'XYZ'
    for i, f in enumerate(FRAMES):
        for bone, chans in DATA.items():
            pb = rig.pose.bones[bone]
            for path, rows in chans.items():
                setattr(pb, path, rows[i])
                pb.keyframe_insert(path, frame=f, group=bone)

    # ---- 3. smooth curves ----------------------------------------------------------------
    n = 0
    for fc in iter_fcurves(rig.animation_data.action):
        for k in fc.keyframe_points:
            k.interpolation = 'BEZIER'
            k.handle_left_type = 'AUTO_CLAMPED'
            k.handle_right_type = 'AUTO_CLAMPED'
        if CYCLIC and not any(m.type == 'CYCLES' for m in fc.modifiers):
            fc.modifiers.new('CYCLES')
        fc.update()
        n += 1
    action = rig.animation_data.action
    try:
        action.use_frame_range = True
        action.frame_start = 0
        action.frame_end = FRAME_END
        action.use_cyclic = CYCLIC
    except Exception:
        pass
    for m in list(scene.timeline_markers):
        if m.name in MARKERS:
            scene.timeline_markers.remove(m)
    for nm, fr in MARKERS.items():
        scene.timeline_markers.new(nm, frame=fr)
        try:
            pm = action.pose_markers.new(nm)
            pm.frame = fr
        except Exception:
            pass
    scene.frame_start = 0
    scene.frame_end = FRAME_END
    scene.frame_set(0)
    print("[%s] done: %d keyed frames, %d F-curves, %d bones" % (ACTION_NAME, len(FRAMES), n, len(DATA)))


main()
