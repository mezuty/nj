# =============================================================================
#  %(title)s
#  Rig: MrXen0 R15 v1.2  |  60 fps  |  front = +Y  |  UPPER-BODY ONLY (cast while moving / flying)
#
#  HOW TO USE: Blender > Scripting tab > New > paste this whole file > Run Script.
#  - Deletes any previous "%(action)s" action first (no leftover keys), resets the
#    pose, sets FK mode, then builds a fresh action and makes it the active one.
#  - Only these bones are keyed: UpTorso, HEAD, FK arm/forearm/hand (L + R).
#    TORSO, legs, feet and root are NOT keyed, so Roblox walk/fly keeps the lower body.
#  - All curves BEZIER + AUTO_CLAMPED, no cycles modifier (one-shot).
#  - Running it twice is safe: you still get exactly one action.
#
%(notes)s
# =============================================================================
import bpy, math

ACTION_NAME = "%(action)s"
FRAME_END   = %(length)d
MARKERS     = %(markers)r          # action pose markers (Action editor > Marker > Show Pose Markers)
# bone -> list of [frame, rotX, rotY, rotZ]  (degrees, Euler XYZ)
KEYS = %(keys)s

def _find_rig():
    ob = bpy.data.objects.get("Roblox_R15")
    if ob and ob.type == 'ARMATURE':
        return ob
    for o in bpy.data.objects:
        if o.type == 'ARMATURE' and "UpTorso" in o.pose.bones and "FK_UpperArm.R" in o.pose.bones:
            return o
    raise RuntimeError("MrXen0 R15 rig not found in this .blend")

def _fcurves(action):
    if hasattr(action, "layers") and len(action.layers):          # Blender 4.4+ / 5.x slotted actions
        out = []
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    out.extend(bag.fcurves)
        return out
    return list(getattr(action, "fcurves", []))

def main():
    ob = _find_rig()
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    scene = bpy.context.scene

    # 1) remove the old version of this animation + clear whatever action was playing
    old = bpy.data.actions.get(ACTION_NAME)
    if ob.animation_data:
        ob.animation_data.action = None
    if old:
        bpy.data.actions.remove(old)

    # 2) clean pose (so nothing from the previous animation lingers on un-keyed bones)
    for pb in ob.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)
    props = ob.pose.bones.get("PROPERTIES")
    if props:
        for k in ("ARM_IK_FK.L", "ARM_IK_FK.R", "LEG_IK_FK.L", "LEG_IK_FK.R"):
            if k in props.keys():
                props[k] = 0.0          # FK mode (set, not keyed)

    # 3) fresh action
    act = bpy.data.actions.new(ACTION_NAME)
    act.use_fake_user = True
    ob.animation_data_create()
    ob.animation_data.action = act

    d2r = math.pi / 180.0
    for bone, keys in KEYS.items():
        pb = ob.pose.bones[bone]
        pb.rotation_mode = 'XYZ'
        for f, x, y, z in keys:
            pb.rotation_euler = (x * d2r, y * d2r, z * d2r)
            pb.keyframe_insert(data_path="rotation_euler", frame=f, group=bone)

    # 4) buttery curves: Bezier + auto-clamped, no modifiers (not a loop)
    for fc in _fcurves(act):
        for m in list(fc.modifiers):
            fc.modifiers.remove(m)
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = 'AUTO_CLAMPED'
            kp.handle_right_type = 'AUTO_CLAMPED'
        fc.update()

    for name, f in MARKERS.items():
        act.pose_markers.new(name).frame = f

    scene.render.fps = 60
    scene.render.fps_base = 1.0
    scene.frame_start = 0
    scene.frame_end = FRAME_END
    act.frame_range = (0, FRAME_END)
    scene.frame_set(0)
    print("[%(action)s] built: %%d bones, %%d curves, frames 0-%%d" %% (len(KEYS), len(_fcurves(act)), FRAME_END))

main()
