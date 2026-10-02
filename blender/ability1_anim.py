"""
Ability 1 - Channeled upper-body cast (cast-while-moving) for the MrXen0 R15 rig.

HOW TO USE
  1. Open your .blend with the R15 rig.
  2. Select the rig armature (or leave it unselected; the first armature is used).
  3. Scripting tab -> New -> paste this file -> Run Script.
  4. Export with the Roblox animation addon as usual.

Edit the TIMING block to match the ability's real cast/channel/recovery data.
If a bone name doesn't match your rig, the script prints the rig's bone names;
fix the BONE_CANDIDATES table and re-run.

Rig conventions used (from the spec):
  front = +Y world
  FK_UpperArm: -X = reach forward, +X = pull back
  UpTorso / HEAD: -X = lean/tilt forward
  TORSO is never keyed (upper-body cast so hips/legs stay with locomotion)
"""

import bpy
import math
from mathutils import Euler

# ---------------------------------------------------------------- TIMING ---
FPS = 60
CAST_TIME = 0.35      # windup until activation apex (seconds)
CHANNEL_TIME = 2.0    # sustained hold while the ability is firing (seconds)
RECOVERY_TIME = 0.5   # wind-down back to rest (seconds)
ACTION_NAME = "Ability1_Channel"

W = round(FPS * CAST_TIME)              # apex / activation frame
H = W + round(FPS * CHANNEL_TIME)       # end of channel
E = H + round(FPS * RECOVERY_TIME)      # last frame (back at rest)
WIND = round(W * 0.55)                  # deepest point of the windup
BEAT = 12                               # metered cadence for hold drift

# ----------------------------------------------------------------- BONES ---
# Tried in order; first name that exists on the rig wins.
BONE_CANDIDATES = {
    "chest":   ["UpTorso", "UpperTorso"],
    "head":    ["HEAD", "Head"],
    "r_upper": ["FK_UpperArm.R", "FK_UpperArm_R", "FK_RightUpperArm", "FK_UpperArm.r"],
    "r_lower": ["FK_LowerArm.R", "FK_LowerArm_R", "FK_RightLowerArm", "FK_LowerArm.r"],
    "r_hand":  ["FK_Hand.R", "FK_Hand_R", "FK_RightHand", "FK_Hand.r"],
    "l_upper": ["FK_UpperArm.L", "FK_UpperArm_L", "FK_LeftUpperArm", "FK_UpperArm.l"],
    "l_lower": ["FK_LowerArm.L", "FK_LowerArm_L", "FK_LeftLowerArm", "FK_LowerArm.l"],
    "l_hand":  ["FK_Hand.L", "FK_Hand_L", "FK_LeftHand", "FK_Hand.l"],
}

# Kinetic-chain lag (frames) behind the chest.
LAG = {"chest": 0, "head": 2, "r_upper": 3, "r_lower": 6, "r_hand": 9,
       "l_upper": 5, "l_lower": 8, "l_hand": 11}

REST = (0.0, 0.0, 0.0)

# ----------------------------------------------------------------- POSES ---
# Degrees (X, Y, Z). Right arm = lead/conductor, left arm = anchor/stabilizer.
# Elbow flex assumed -X (same direction as a forward reach; knees are +X).
# Y/Z signs on arms are small - flip them if they twist the wrong way on your rig.
POSES = {
    #            windup (inhale/chamber)   apex (release)        hold base              recovery drift
    "chest":   [(8.0, 0.0, 5.0),          (-6.0, 0.0, -3.0),    (-4.0, 0.0, -2.0),     (-2.0, 0.0, -1.0)],
    "head":    [(-5.0, 0.0, 3.0),         (3.0, 2.0, 1.0),      (2.0, 2.0, 1.0),       (1.0, 1.0, 0.0)],
    "r_upper": [(35.0, 0.0, 6.0),         (-82.0, 0.0, -5.0),   (-78.0, 0.0, -4.0),    (-60.0, 0.0, -2.0)],
    "r_lower": [(-75.0, 0.0, 0.0),        (-14.0, 0.0, 0.0),    (-18.0, 0.0, 0.0),     (-32.0, 0.0, 0.0)],
    "r_hand":  [(18.0, 0.0, 6.0),         (-22.0, 0.0, -4.0),   (-12.0, 0.0, -3.0),    (6.0, 0.0, 0.0)],
    "l_upper": [(15.0, 0.0, 3.0),         (-28.0, 0.0, 4.0),    (-25.0, 0.0, 3.0),     (-15.0, 0.0, 1.0)],
    "l_lower": [(-35.0, 0.0, 0.0),        (-58.0, 0.0, 0.0),    (-55.0, 0.0, 0.0),     (-30.0, 0.0, 0.0)],
    "l_hand":  [(12.0, 0.0, -8.0),        (8.0, 0.0, -15.0),    (10.0, 0.0, -12.0),    (4.0, 0.0, -4.0)],
}

# Living hold: layered sin/cos at different frequencies (degrees of drift).
# (ampX, ampY, ampZ, phase) - small, so the hold breathes instead of freezing.
DRIFT = {
    "chest":   (1.2, 0.0, 0.8, 0.0),
    "head":    (0.8, 1.0, 0.6, 0.6),
    "r_upper": (1.8, 0.0, 1.5, 0.3),
    "r_lower": (1.5, 0.0, 0.0, 0.9),
    "r_hand":  (3.0, 0.0, 2.5, 1.4),
    "l_upper": (1.2, 0.0, 1.0, 2.0),
    "l_lower": (1.5, 0.0, 0.0, 2.4),
    "l_hand":  (2.5, 0.0, 2.0, 2.9),
}


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def build_keys(key):
    """Return sorted [(frame, (x, y, z)), ...] for one bone."""
    windup, apex, hold, recover = POSES[key]
    lag = LAG[key]
    ax, ay, az, ph = DRIFT[key]
    k = {}

    k[0] = REST
    k[WIND + lag] = windup
    k[W + lag] = apex
    settle = W + lag + 15                      # cushioned glide from apex into hold
    k[settle] = hold

    # Hold phase: drift on a steady beat, never a dead freeze.
    f = settle + BEAT
    while f <= H - BEAT // 2:
        t = (f - settle) / FPS
        k[f] = add(hold, (ax * math.sin(t * 1.2 * math.tau + ph),
                          ay * math.sin(t * 0.8 * math.tau + ph),
                          az * math.cos(t * 1.9 * math.tau + ph)))
        f += BEAT
    k[H] = hold

    # Wind-down: upper chain leads, hands trail. Lose tension, float to rest.
    rec_lag = {"chest": 0, "head": 2, "r_upper": 0, "r_lower": 3, "r_hand": 6,
               "l_upper": 2, "l_lower": 5, "l_hand": 8}[key]
    k[H + 8 + rec_lag] = recover
    k[E - 8 + rec_lag] = REST                  # all bones land by E (max lag 8)
    return sorted(k.items())


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
    names = {}
    missing = []
    for key, cands in BONE_CANDIDATES.items():
        hit = next((c for c in cands if c in arm.pose.bones), None)
        if hit:
            names[key] = hit
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

    # Reset pose (not keyed) so no leftover posing lingers.
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)

    act = bpy.data.actions.new(ACTION_NAME)
    ad.action = act
    return act


def set_fk_mode(arm):
    props = arm.pose.bones.get("PROPERTIES")
    if not props:
        print("WARNING: PROPERTIES bone not found; set FK mode manually.")
        return
    for p in ("ARM_IK_FK.L", "ARM_IK_FK.R", "LEG_IK_FK.L", "LEG_IK_FK.R"):
        if p in props.keys():
            props[p] = 0.0
        else:
            print(f"WARNING: PROPERTIES has no '{p}' property.")


def key_bone(pb, keys):
    """Insert keys ONLY on this bone, respecting its rotation mode."""
    prev_q = None
    for frame, deg in keys:
        eul = Euler(tuple(math.radians(d) for d in deg), 'XYZ')
        if pb.rotation_mode == 'QUATERNION':
            q = eul.to_quaternion()
            if prev_q is not None and prev_q.dot(q) < 0:   # keep hemisphere -> no flips
                q.negate()
            prev_q = q
            pb.rotation_quaternion = q
            pb.keyframe_insert("rotation_quaternion", frame=frame, group=pb.name)
        elif pb.rotation_mode == 'AXIS_ANGLE':
            pb.rotation_mode = 'XYZ'
            pb.rotation_euler = eul
            pb.keyframe_insert("rotation_euler", frame=frame, group=pb.name)
        else:
            pb.rotation_euler = eul.to_matrix().to_euler(pb.rotation_mode)
            pb.keyframe_insert("rotation_euler", frame=frame, group=pb.name)


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


def smooth_curves(arm):
    for fc in all_fcurves(arm):
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = 'AUTO_CLAMPED'
            kp.handle_right_type = 'AUTO_CLAMPED'
        fc.update()


# ------------------------------------------------------------------- RUN ---
def main():
    arm = find_armature()
    bpy.context.view_layer.objects.active = arm
    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')

    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.render.fps_base = 1.0
    scene.frame_start = 0
    scene.frame_end = E

    bones = resolve_bones(arm)
    clear_old_animation(arm)
    set_fk_mode(arm)

    for key, bone_name in bones.items():
        key_bone(arm.pose.bones[bone_name], build_keys(key))

    smooth_curves(arm)
    scene.frame_set(0)
    print(f"[{ACTION_NAME}] done: windup 0-{W}, channel {W}-{H}, recovery {H}-{E} "
          f"({E} frames @ {FPS} fps). Keyed: {', '.join(bones.values())}")


main()
