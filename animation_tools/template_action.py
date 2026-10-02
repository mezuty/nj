%(header)simport bpy

ARMATURE_NAME = "Roblox_R15"
ACTION_NAME   = %(name)r
FPS           = 60
LOOP_END      = %(end)d          # last frame of the action
CYCLIC        = %(cyclic)r       # loops only if True (idles / walk cycles); one-shot actions must NOT cycle
MARKERS       = %(markers)r      # timeline markers, e.g. {"HIT": 16} (gameplay sync points)
GROUP_ORDER   = %(group_order)r

# bone -> {"loc"|"rot"|"quat": [value per key]},  KEY_FRAMES gives the frame of each key
KEY_FRAMES = %(key_frames)r
DATA = {
%(data)s
}


def iter_fcurves(action):
    """Works on Blender 4.x (legacy) and 5.x (layered / slotted actions)."""
    if hasattr(action, "layers"):
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        yield fc
    else:
        for fc in action.fcurves:
            yield fc


def main():
    arm = bpy.data.objects.get(ARMATURE_NAME)
    if arm is None or arm.type != 'ARMATURE':
        arm = bpy.context.active_object
    if arm is None or arm.type != 'ARMATURE':
        raise RuntimeError("Select the Roblox_R15 armature (or keep it named '%%s')." %% ARMATURE_NAME)

    scene = bpy.context.scene
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # ---- 1. wipe the old animation completely --------------------------------
    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = None
    for old in [a for a in bpy.data.actions if a.name == ACTION_NAME or a.name.startswith(ACTION_NAME + ".")]:
        bpy.data.actions.remove(old)
    for pb in arm.pose.bones:                       # back to rest so nothing lingers
        pb.location = (0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)

    # ---- 2. rig + scene settings ---------------------------------------------
    props = arm.pose.bones.get("PROPERTIES")
    if props is not None:
        for k in ("ARM_IK_FK.L", "ARM_IK_FK.R", "LEG_IK_FK.L", "LEG_IK_FK.R"):
            if k in props.keys():
                props[k] = 0.0                      # FK mode
    scene.render.fps = FPS
    scene.render.fps_base = 1.0
    scene.frame_start = 0
    scene.frame_end = LOOP_END

    # ---- 3. new action + keys (only the bones listed in DATA) -----------------
    action = bpy.data.actions.new(ACTION_NAME)
    action.use_fake_user = True
    arm.animation_data.action = action

    for bone in GROUP_ORDER:
        pb = arm.pose.bones[bone]
        chans = DATA[bone]
        for i, frame in enumerate(KEY_FRAMES):
            if "loc" in chans:
                pb.location = chans["loc"][i]
            if "rot" in chans:
                pb.rotation_euler = chans["rot"][i]
            if "quat" in chans:
                pb.rotation_quaternion = chans["quat"][i]
            if "loc" in chans:
                pb.keyframe_insert("location", frame=frame, group=bone)
            if "rot" in chans:
                pb.keyframe_insert("rotation_euler", frame=frame, group=bone)
            if "quat" in chans:
                pb.keyframe_insert("rotation_quaternion", frame=frame, group=bone)

    # ---- 4. polish the curves: BEZIER + AUTO_CLAMPED (+ seamless cycle only for loops) ----
    for fc in iter_fcurves(action):
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = 'AUTO_CLAMPED'
            kp.handle_right_type = 'AUTO_CLAMPED'
        if CYCLIC and not any(m.type == 'CYCLES' for m in fc.modifiers):
            fc.modifiers.new('CYCLES')
        fc.update()
    try:
        action.use_frame_range = True
        action.frame_start = 0
        action.frame_end = LOOP_END
        action.use_cyclic = CYCLIC
    except Exception:
        pass

    # ---- 5. gameplay sync markers (re-created every run) ---------------------------
    for m in list(scene.timeline_markers):
        if m.name in MARKERS:
            scene.timeline_markers.remove(m)
    for mname, mframe in MARKERS.items():
        scene.timeline_markers.new(mname, frame=mframe)

    scene.frame_set(0)
    n = sum(1 for _ in iter_fcurves(action))
    print("[%%s] done: %%d curves, %%d keys, frames 0-%%d @ %%d fps, markers %%s" %% (ACTION_NAME, n, len(KEY_FRAMES), LOOP_END, FPS, MARKERS))


main()
