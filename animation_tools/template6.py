# =============================================================================
#  CATWOMAN - MAIN MENU IDLE LOOP  ("Poise")               Roblox R15 / MrXen0 rig
# -----------------------------------------------------------------------------
#  HOW TO USE
#    1. Open your MrXen0_R15RIG .blend in Blender (5.0+ recommended).
#    2. Scripting workspace -> Text Editor -> New -> paste this whole file.
#    3. Press  Run Script  (Alt+P).  Done - the armature now has the action
#       "Catwoman_Idle" assigned and the timeline set to 60 fps, frames 0-360.
#
#  WHAT IT DOES
#    * deletes any old "Catwoman_Idle" action first (no lingering keyframes)
#    * sets the rig to FK mode (ARM_IK_FK / LEG_IK_FK = 0)
#    * keys ONLY the animated FK controls (full-body loop, so legs/pelvis are keyed)
#    * all curves BEZIER + AUTO_CLAMPED, with a Cycles modifier so the loop seam
#      is smooth (frame 360 == frame 0)
#
#  TIMING (60 fps):   360 frames = 6.0 s - upright, poised, controlled power
#    stance  : tall model stance - weight on the back leg, front foot pointed on its toe,
#              ribcage lifted, shoulders back, chin up, hips popped into a long S-curve
#    0-66    : poised sway, gaze locked on the camera
#    66-176  : right arm lifts slowly with the wrist cocked, then a lazy cat-swat
#              (quick smooth arc, wrist whips past and trails) while her head turns away in disdain
#    166-290 : hips roll the weight onto the front foot with a hip pop; the left arm
#              floats into an elegant reach and settles; head glances over the shoulder
#    290-360 : weight glides back, foot re-points, head returns to the camera
#
#  This is a FULL-BODY loop (idle display) - export it as a Looped animation and do
#  NOT apply the upper-body-only bone filter.
# =============================================================================
import bpy

ARMATURE_NAME = "Roblox_R15"
ACTION_NAME   = "Catwoman_Idle"
FPS           = 60
LOOP_END      = 360
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

    # ---- 4. polish the curves: BEZIER + AUTO_CLAMPED + seamless cycle ----------
    for fc in iter_fcurves(action):
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = 'AUTO_CLAMPED'
            kp.handle_right_type = 'AUTO_CLAMPED'
        if not any(m.type == 'CYCLES' for m in fc.modifiers):
            fc.modifiers.new('CYCLES')
        fc.update()
    try:
        action.use_frame_range = True
        action.frame_start = 0
        action.frame_end = LOOP_END
        action.use_cyclic = True
    except Exception:
        pass

    scene.frame_set(0)
    n = sum(1 for _ in iter_fcurves(action))
    print("[Catwoman_Idle] done: %%d curves, %%d keys each, frames 0-%%d @ %%d fps" %% (n, len(KEY_FRAMES), LOOP_END, FPS))


main()
