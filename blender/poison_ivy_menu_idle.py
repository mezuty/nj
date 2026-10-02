"""
Poison Ivy - Main Menu Idle (seamless loop, full body) for the MrXen0 R15 rig.

Pose: confident contrapposto. Weight on her right leg, hip cocked, chest
counter-tilted into an S-curve. Right hand is the "magic" hand: held palm-up at
lower-chest height, slowly weaving a figure-8 as if coaxing a vine to grow.
Left hand hangs soft at her hip. Head tilted, chin slightly down, eyes drifting
between the camera and her magic hand. Left hand is planted sharply on her hip:
elbow cocked out to the side, wrist bent so the hand presses onto the hip. The
script solves that pose against the rig's real hip position, so it lands on the
hip regardless of the rig's arm axis conventions.

HOW TO USE
  Select the Roblox_R15 armature -> Scripting tab -> Open this file -> Run Script.
  Or: blender "MyRig.blend" --python poison_ivy_menu_idle.py
  When exporting, set the animation to Looped in Roblox.

Everything is built from periodic waves with whole-number cycles per loop, so
the last frame equals the first (no pop at the loop point), and every curve gets
a Cycles modifier so Blender's handles flow smoothly across the loop seam.

Legs are switched to IK so her feet stay planted while the hips sway (FK legs
would make the feet slide). Set LEGS_IK = False to keep FK legs.
"""

import bpy
import math
from mathutils import Euler, Matrix, Vector

# ---------------------------------------------------------------- TIMING ---
FPS = 60
LOOP_SECONDS = 6.0          # one full loop
BEAT = 12                   # key spacing (metered cadence); must divide L
ACTION_NAME = "PoisonIvy_MenuIdle"
LEGS_IK = True

L = round(FPS * LOOP_SECONDS)   # 360 frames

# Arm abduction (sideways, local Z) is mirrored per side. If an arm swings INTO
# the body instead of away from it, flip that side's sign.
ABDUCT = {"L": 1.0, "R": -1.0}

# ----------------------------------------------------------------- BONES ---
BONE_CANDIDATES = {
    "torso":   ["TORSO"],
    "chest":   ["UpTorso", "UpperTorso"],
    "head":    ["HEAD", "Head"],
    "r_upper": ["FK_UpperArm.R", "FK_UpperArm_R", "FK_RightUpperArm", "FK_UpperArm.r"],
    "r_lower": ["FK_LowerArm.R", "FK_LowerArm_R", "FK_RightLowerArm", "FK_LowerArm.r"],
    "r_hand":  ["FK_Hand.R", "FK_Hand_R", "FK_RightHand", "FK_Hand.r"],
    "l_upper": ["FK_UpperArm.L", "FK_UpperArm_L", "FK_LeftUpperArm", "FK_UpperArm.l"],
    "l_lower": ["FK_LowerArm.L", "FK_LowerArm_L", "FK_LeftLowerArm", "FK_LowerArm.l"],
    "l_hand":  ["FK_Hand.L", "FK_Hand_L", "FK_LeftHand", "FK_Hand.l"],
}
OPTIONAL = {"torso"}   # skipped with a warning if missing

# ------------------------------------------------------------------ MOTION ---
# Per bone:
#   base: resting pose in degrees (X, Y, Z)
#         X = pitch (-X forward), Y = twist along the bone, Z = side tilt / abduction
#   osc:  list of (axis, amplitude_deg, cycles_per_loop, phase_deg)
#   lag:  frames this bone trails the core (kinetic chain / overlap)
# cycles_per_loop must be whole numbers so the loop is seamless.
# Breathing = 3 cycles (2 s), weight sway = 1 cycle (6 s), figure-8 = 2:4.
r, l = ABDUCT["R"], ABDUCT["L"]
MOTION = {
    # Pelvis: hip cocked up on her right (+Z), slightly turned, tiny forward tilt.
    "torso": {
        "base": (-2.0, 5.0, 3.0),
        "osc": [("z", 1.0, 1, 0), ("y", 1.5, 1, 90), ("x", 0.5, 3, 0)],
        "lag": 0,
    },
    # Chest: counter-tilt for the S-curve, lifted (+X = arch back, confident).
    "chest": {
        "base": (3.0, -4.0, -4.0),
        "osc": [("x", 1.6, 3, 0), ("z", 0.8, 1, 180), ("y", 1.2, 1, 270)],
        "lag": 4,
    },
    # Head: chin down, tilted; yaw drifts between camera (~+1) and magic hand (~-9).
    "head": {
        "base": (-4.0, -4.0, 5.0),
        "osc": [("y", 5.0, 1, 200), ("z", 1.5, 2, 30), ("x", 0.8, 3, 60)],
        "lag": 8,
    },
    # Lead (magic) arm: elbow tucked, forearm forward at lower-chest height.
    # Upper arm + forearm + hand trace a figure-8 (Lissajous 2:4), lagging down the chain.
    "r_upper": {
        "base": (-28.0, 0.0, 4.0 * r),
        "osc": [("z", 3.0 * r, 2, 0), ("x", 2.5, 4, 0), ("x", 1.0, 3, 0)],
        "lag": 3,
    },
    "r_lower": {
        "base": (-75.0, 0.0, 0.0),
        "osc": [("x", 5.0, 4, 0), ("y", 8.0, 2, 0)],
        "lag": 8,
    },
    "r_hand": {
        "base": (-10.0, 0.0, 6.0 * r),
        "osc": [("x", 10.0, 4, 0), ("z", 9.0 * r, 2, 0), ("y", 7.0, 2, 90)],
        "lag": 14,
    },
    # Hand-on-hip arm: crisp and planted. "base" here is only a fallback - the real
    # pose is solved against the hip in solve_hand_on_hip(). Motion is kept tiny
    # (breathing only) so the hand doesn't slide on the hip.
    "l_upper": {
        "base": (10.0, 0.0, 40.0 * l),
        "osc": [("x", 0.6, 3, 0)],
        "lag": 6,
    },
    "l_lower": {
        "base": (-100.0, 0.0, 0.0),
        "osc": [("x", 0.8, 3, 0)],
        "lag": 9,
    },
    "l_hand": {
        "base": (0.0, 0.0, -30.0 * l),
        "osc": [("z", 0.8, 3, 0)],
        "lag": 12,
    },
}

# Where the wrist sits relative to the left hip joint, in upper-arm lengths:
# out to the side of the hip, up at the waist, a touch behind centre.
HIP_OUT = 0.60
HIP_UP = 0.35
HIP_BACK = 0.10
HIP_BONE_CANDIDATES = ["LeftUpperLeg", "FK_UpperLeg.L", "FK_UpperLeg_L",
                       "IK_UpperLeg.L", "UpperLeg.L", "Thigh.L"]

# Pelvis translation (local axes: x = side, y = up, -z = forward).
# Slight drop so planted IK legs keep a soft knee; breathing bob; weight drift.
TORSO_LOC = {
    "base": (0.0, -0.04, 0.0),
    "osc": [("x", 0.02, 1, 0), ("y", 0.008, 3, 180)],
    "lag": 0,
}

AXIS = {"x": 0, "y": 1, "z": 2}


def sample(spec, frame):
    """Value of a channel spec at a frame (periodic over L)."""
    v = list(spec["base"])
    t = frame - spec["lag"]
    for axis, amp, n, ph in spec["osc"]:
        v[AXIS[axis]] += amp * math.sin(math.tau * n * t / L + math.radians(ph))
    return tuple(v)


def key_frames():
    if L % BEAT:
        raise ValueError(f"BEAT ({BEAT}) must divide the loop length ({L}).")
    return list(range(0, L + 1, BEAT))


# ---------------------------------------------------------------- HELPERS ---
def find_armature():
    obj = bpy.context.active_object
    if obj and obj.type == 'ARMATURE':
        return obj
    for o in bpy.context.scene.objects:
        if o.type == 'ARMATURE':
            return o
    raise RuntimeError("No armature found in the scene.")


def resolve_bones(arm):
    names, missing = {}, []
    for key, cands in BONE_CANDIDATES.items():
        hit = next((c for c in cands if c in arm.pose.bones), None)
        if hit:
            names[key] = hit
        elif key in OPTIONAL:
            print(f"WARNING: no bone for '{key}', skipping it.")
        else:
            missing.append(key)
    if missing:
        print("\n=== Bones on this rig ===")
        for pb in arm.pose.bones:
            print("  ", pb.name)
        raise RuntimeError(f"Could not find bones for {missing}. "
                           "Add the right names to BONE_CANDIDATES (list printed in System Console).")
    return names


def clear_old_animation(arm):
    ad = arm.animation_data_create()
    old = ad.action
    ad.action = None
    for track in list(ad.nla_tracks):
        ad.nla_tracks.remove(track)
    if old and old.users == 0 and not old.use_fake_user:
        bpy.data.actions.remove(old)
    stale = bpy.data.actions.get(ACTION_NAME)
    if stale:
        bpy.data.actions.remove(stale)

    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)

    act = bpy.data.actions.new(ACTION_NAME)
    ad.action = act
    return act


def set_ik_fk(arm):
    props = arm.pose.bones.get("PROPERTIES")
    if not props:
        print("WARNING: PROPERTIES bone not found; set IK/FK manually.")
        return
    leg = 1.0 if LEGS_IK else 0.0     # 0 = FK, 1 = IK on this rig
    for p, val in (("ARM_IK_FK.L", 0.0), ("ARM_IK_FK.R", 0.0),
                   ("LEG_IK_FK.L", leg), ("LEG_IK_FK.R", leg)):
        if p in props.keys():
            props[p] = val
        else:
            print(f"WARNING: PROPERTIES has no '{p}' property.")


def rot4(deg):
    return Euler(tuple(math.radians(d) for d in deg), 'XYZ').to_matrix().to_4x4()


def find_left_hip(arm):
    for name in HIP_BONE_CANDIDATES:
        if name in arm.pose.bones:
            return arm.pose.bones[name]
    for pb in arm.pose.bones:
        n = pb.name.lower()
        if ("upperleg" in n or "thigh" in n) and (n.endswith((".l", "_l")) or "left" in n):
            return pb
    return None


def solve_hand_on_hip(arm, bones):
    """Search arm angles so the left wrist lands on the hip, elbow out and back."""
    pbu, pbl, pbh = (arm.pose.bones[bones[k]] for k in ("l_upper", "l_lower", "l_hand"))
    hip = find_left_hip(arm)
    if hip is None or pbl.parent != pbu or pbh.parent != pbl:
        print("WARNING: couldn't solve hand-on-hip (hip bone or arm chain not found); "
              "using fallback angles.")
        return None

    bpy.context.view_layer.update()
    W = arm.matrix_world
    s = pbu.bone.length
    hip_w = W @ hip.head
    out = 1.0 if (W @ pbu.head).x > (W @ arm.pose.bones[bones["chest"]].head).x else -1.0
    OUT, UP, FWD = Vector((out, 0, 0)), Vector((0, 0, 1)), Vector((0, 1, 0))
    target = hip_w + OUT * (HIP_OUT * s) + UP * (HIP_UP * s) - FWD * (HIP_BACK * s)

    if pbu.parent:
        base_u = W @ pbu.parent.matrix @ pbu.parent.bone.matrix_local.inverted() @ pbu.bone.matrix_local
    else:
        base_u = W @ pbu.bone.matrix_local
    off_l = pbu.bone.matrix_local.inverted() @ pbl.bone.matrix_local
    off_h = pbl.bone.matrix_local.inverted() @ pbh.bone.matrix_local

    best = None
    for ux in range(-10, 35, 5):
        for uy in range(-90, 91, 15):
            for uz in [z * sg for z in range(20, 65, 5) for sg in (1, -1)]:
                ml0 = base_u @ rot4((ux, uy, uz)) @ off_l
                elbow = ml0.translation
                for lx in range(-60, -145, -10):
                    ml = ml0 @ rot4((lx, 0, 0))
                    wrist = (ml @ off_h).translation
                    rel = elbow - wrist
                    score = ((wrist - target).length / s
                             + max(0.0, 0.25 - rel.dot(OUT) / s)    # elbow flared out to the side
                             + max(0.0, rel.dot(FWD) / s)           # elbow not in front of the hand
                             + 0.0002 * (abs(ux) + abs(uy) + abs(uz) + abs(lx + 95)))
                    if best is None or score < best[0]:
                        best = (score, (ux, uy, uz), (lx, 0, 0), ml)

    # Wrist: fingers point down and forward, wrapping slightly over the front of the hip.
    _, upper, lower, ml = best
    mh0 = ml @ off_h
    wrist = mh0.translation
    want = (-UP * 0.7 + FWD * 0.45 - OUT * 0.25).normalized()
    hbest = None
    for hx in range(-70, 75, 5):
        for hz in range(-70, 75, 5):
            mh = mh0 @ rot4((hx, 0, hz))
            d = ((mh @ Vector((0, pbh.bone.length, 0))) - wrist).normalized()
            score = d.angle(want) + 0.001 * (abs(hx) + abs(hz))
            if hbest is None or score < hbest[0]:
                hbest = (score, (hx, 0, hz))

    err = (wrist - target).length / s
    print(f"Hand-on-hip solved: upper {upper}, lower {lower}, hand {hbest[1]} "
          f"(wrist off target by {err:.2f} arm-lengths)")
    return {"l_upper": upper, "l_lower": lower, "l_hand": hbest[1]}


def pose_base(arm, bones):
    """Put the core in its base pose (unkeyed) so the hip solve sees the real posture."""
    for key in ("torso", "chest", "head"):
        if key in bones:
            pb = arm.pose.bones[bones[key]]
            m = rot4(MOTION[key]["base"])
            if pb.rotation_mode == 'QUATERNION':
                pb.rotation_quaternion = m.to_quaternion()
            else:
                pb.rotation_euler = m.to_euler(pb.rotation_mode if pb.rotation_mode != 'AXIS_ANGLE' else 'XYZ')
            if key == "torso":
                pb.location = TORSO_LOC["base"]


def key_rotation(pb, keys):
    prev_q = None
    for frame, deg in keys:
        eul = Euler(tuple(math.radians(d) for d in deg), 'XYZ')
        if pb.rotation_mode == 'QUATERNION':
            q = eul.to_quaternion()
            if prev_q is not None and prev_q.dot(q) < 0:
                q.negate()
            prev_q = q
            pb.rotation_quaternion = q
            pb.keyframe_insert("rotation_quaternion", frame=frame, group=pb.name)
        else:
            if pb.rotation_mode == 'AXIS_ANGLE':
                pb.rotation_mode = 'XYZ'
            pb.rotation_euler = eul.to_matrix().to_euler(pb.rotation_mode)
            pb.keyframe_insert("rotation_euler", frame=frame, group=pb.name)


def key_location(pb, keys):
    for frame, loc in keys:
        pb.location = loc
        pb.keyframe_insert("location", frame=frame, group=pb.name)


def all_fcurves(arm):
    act = arm.animation_data.action
    try:
        return list(act.fcurves)                 # Blender <= 4.x
    except AttributeError:                       # Blender 5.x layered actions
        slot = arm.animation_data.action_slot
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                bag = strip.channelbag(slot)
                if bag:
                    out.extend(bag.fcurves)
        return out


def smooth_and_cycle(arm):
    for fc in all_fcurves(arm):
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = 'AUTO_CLAMPED'
            kp.handle_right_type = 'AUTO_CLAMPED'
        if not any(m.type == 'CYCLES' for m in fc.modifiers):
            fc.modifiers.new('CYCLES')       # cycle-aware handles: smooth loop seam
        fc.update()


# ------------------------------------------------------------------- RUN ---
def main():
    arm = find_armature()
    bpy.context.view_layer.objects.active = arm
    if not bpy.app.background and bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')

    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.render.fps_base = 1.0
    scene.frame_start = 0
    scene.frame_end = L

    bones = resolve_bones(arm)
    clear_old_animation(arm)
    set_ik_fk(arm)

    pose_base(arm, bones)
    solved = solve_hand_on_hip(arm, bones)
    if solved:
        for key, base in solved.items():
            MOTION[key]["base"] = base

    frames = key_frames()
    for key, bone_name in bones.items():
        pb = arm.pose.bones[bone_name]
        key_rotation(pb, [(f, sample(MOTION[key], f)) for f in frames])
        if key == "torso":
            key_location(pb, [(f, sample(TORSO_LOC, f)) for f in frames])

    smooth_and_cycle(arm)
    scene.frame_set(0)
    print(f"[{ACTION_NAME}] done: {L}-frame loop @ {FPS} fps, legs {'IK' if LEGS_IK else 'FK'}. "
          f"Keyed: {', '.join(bones.values())}")


main()

# Headless run (blender -b file.blend --python poison_ivy_menu_idle.py): save the result.
if bpy.app.background and bpy.data.filepath:
    bpy.ops.wm.save_mainfile()
    print(f"Saved {bpy.data.filepath}")
