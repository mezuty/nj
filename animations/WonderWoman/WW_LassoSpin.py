# =====================================================================================
#  WW LASSOSPIN  (kit slot WW_ANIMS.LassoSpin, played at speed 1.1)
#  Rig: MrXen0 R15 (Roblox_R15) | 60 fps | 29 frames (0.483333 s) | UPPER-BODY ONLY (cast-while-moving: no TORSO / legs / feet tracks)
#  HOW TO USE: open your MrXen0 R15 .blend -> Scripting tab -> Open/paste this file -> Run Script.
#  It removes the old animation first (unassigns the current action, deletes any earlier copy of
#  "WW_LassoSpin", clears the pose), then keys ONLY the animated FK controls with BEZIER / AUTO_CLAMPED
#  curves. Frame map: no markers
# =====================================================================================
import bpy

ACTION_NAME = "WW_LassoSpin"
FRAME_END = 28
CYCLIC = False
FRAMES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 28]
# bone -> {data_path: [per-key rows]}   (radians / studs; TORSO is quaternion)
DATA = {"UpTorso":{"rotation_euler":[[-0.0,0.0,0.0],[-0.0,0.0,0.0],[-0.0,0.0,0.0],[0.0047,-0.00391,0.0],[0.01717,-0.01431,0.0],[0.03499,-0.02915,0.0],[0.05572,-0.04643,0.0],[0.07694,-0.06411,0.0],[0.09621,-0.08017,0.0],[0.11111,-0.09259,0.0],[0.11921,-0.09934,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0],[0.12,-0.1,0.0]]},"HEAD":{"rotation_euler":[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.00587,0.00783,0.0],[0.02146,0.02861,0.0],[0.04373,0.05831,0.0],[0.06965,0.09286,0.0],[0.09617,0.12823,0.0],[0.12026,0.16035,0.0],[0.13889,0.18519,0.0],[0.14901,0.19868,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0],[0.15,0.2,0.0]]},"FK_UpperArm.R":{"rotation_euler":[[0.05,-0.0,0.06],[-0.04199,-0.00391,0.07135],[-0.28622,-0.01431,0.10149],[-0.63513,-0.02915,0.14455],[-1.04113,-0.04643,0.19465],[-1.45665,-0.06411,0.24593],[-1.83411,-0.08017,0.29251],[-2.12593,-0.09259,0.33789],[-2.28452,-0.09934,0.39367],[-2.3,-0.1,0.42931],[-2.3,-0.1,0.42762],[-2.3,-0.1,0.39647],[-2.3,-0.1,0.35954],[-2.3,-0.1,0.32201],[-2.3,-0.1,0.28624],[-2.3,-0.1,0.25448],[-2.3,-0.1,0.22872],[-2.3,-0.1,0.21058],[-2.3,-0.1,0.2012],[-2.3,-0.1,0.20117],[-2.3,-0.1,0.21049],[-2.3,-0.1,0.22858],[-2.3,-0.1,0.25429],[-2.3,-0.1,0.28607],[-2.3,-0.1,0.3247],[-2.3,-0.1,0.35537],[-2.3,-0.1,0.3597],[-2.3,-0.1,0.35129],[-2.3,-0.1,0.35],[-2.3,-0.1,0.35]]},"FK_LowerArm.R":{"rotation_euler":[[-0.12,-0.0,0.0],[-0.12,-0.0,0.0],[-0.12,-0.0,0.0],[-0.12,-0.0,0.0],[-0.18185,-0.0,0.0],[-0.34606,-0.0,0.0],[-0.58064,-0.0,0.0],[-0.86045,-0.0,0.0],[-1.15195,-0.0,0.0],[-1.38676,-0.0,0.0],[-1.53019,-0.0,0.0],[-1.58361,-0.0,0.0],[-1.5494,-0.0,0.0],[-1.51425,-0.0,0.0],[-1.49077,-0.0,0.0],[-1.48043,-0.0,0.0],[-1.4839,-0.0,0.0],[-1.50094,-0.0,0.0],[-1.53049,-0.0,0.0],[-1.57069,-0.0,0.0],[-1.61901,-0.0,0.0],[-1.67243,-0.0,0.0],[-1.72757,-0.0,0.0],[-1.78093,-0.0,0.0],[-1.81593,-0.0,0.0],[-1.79794,-0.0,0.0],[-1.74178,-0.0,0.0],[-1.70347,-0.0,0.0],[-1.7,-0.0,0.0],[-1.7,-0.0,0.0]]},"FK_Hand.R":{"rotation_euler":[[0.15,0.0,0.0],[0.15,0.0,0.0],[0.15,0.0,0.0],[0.15,0.0,0.0],[0.15,0.0,0.0],[0.15,0.0,0.0],[0.15,0.0,0.0],[0.14449,0.0,0.01761],[0.14319,0.0,0.10238],[0.20707,0.0,0.21682],[0.33268,0.0,0.27406],[0.45479,0.0,0.25129],[0.5572,0.0,0.20264],[0.63612,0.0,0.14126],[0.68472,0.0,0.071],[0.69994,0.0,-0.00372],[0.68905,0.0,-0.0782],[0.65371,0.0,-0.14777],[0.59615,0.0,-0.20806],[0.51998,0.0,-0.25527],[0.42999,0.0,-0.28644],[0.33182,0.0,-0.29962],[0.23166,0.0,-0.29397],[0.13591,0.0,-0.26966],[0.0761,0.0,-0.20509],[0.11534,0.0,-0.10014],[0.22248,0.0,-0.02245],[0.29364,0.0,-0.00054],[0.3,0.0,0.0],[0.3,0.0,0.0]]},"FK_UpperArm.L":{"rotation_euler":[[0.05,0.0,-0.06],[0.01281,0.0,-0.08114],[-0.08592,0.0,-0.13726],[-0.22697,0.0,-0.21743],[-0.3911,0.0,-0.31073],[-0.55907,0.0,-0.40621],[-0.71166,0.0,-0.49294],[-0.82963,0.0,-0.56],[-0.89374,0.0,-0.59644],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6],[-0.9,0.0,-0.6]]},"FK_LowerArm.L":{"rotation_euler":[[-0.12,0.0,0.0],[-0.12,0.0,0.0],[-0.12,0.0,0.0],[-0.12,0.0,0.0],[-0.13096,0.0,0.0],[-0.16006,0.0,0.0],[-0.20163,0.0,0.0],[-0.25001,0.0,0.0],[-0.29952,0.0,0.0],[-0.34449,0.0,0.0],[-0.37926,0.0,0.0],[-0.39816,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0],[-0.4,0.0,0.0]]},"FK_Hand.L":{"rotation_euler":[[0.15,0.0,-0.0],[0.15,0.0,-0.0],[0.15,0.0,-0.0],[0.15,0.0,-0.0],[0.15,0.0,-0.0],[0.15,0.0,-0.0],[0.15,0.0,-0.0],[0.15196,0.0,-0.0],[0.15715,0.0,-0.0],[0.16458,0.0,-0.0],[0.17322,0.0,-0.0],[0.18206,0.0,-0.0],[0.19009,0.0,-0.0],[0.1963,0.0,-0.0],[0.19967,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0],[0.2,0.0,-0.0]]}}
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
