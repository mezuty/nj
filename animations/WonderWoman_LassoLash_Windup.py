# =============================================================================
#  Wonder Woman - Lasso Lash (Q) - 1/2 WINDUP  (slot WW_ANIMS.LashWindup)
#  Rig: MrXen0 R15 v1.2  |  60 fps  |  front = +Y  |  UPPER-BODY ONLY (cast while moving / flying)
#
#  HOW TO USE: Blender > Scripting tab > New > paste this whole file > Run Script.
#  - Deletes any previous "WonderWoman_LassoLash_Windup" action first (no leftover keys), resets the
#    pose, sets FK mode, then builds a fresh action and makes it the active one.
#  - Only these bones are keyed: UpTorso, HEAD, FK arm/forearm/hand (L + R).
#    TORSO, legs, feet and root are NOT keyed, so Roblox walk/fly keeps the lower body.
#  - All curves BEZIER + AUTO_CLAMPED, no cycles modifier (one-shot).
#  - Running it twice is safe: you still get exactly one action.
#
#  Game: played at speed 1.2 for castTime 0.28 s -> 20 anim frames; clip is 24 f so the
#  LashCrack track (fade 0.04) always takes over during the anticipation hang (f19-24).
#  Frame map: 0 ready -> 0-18 lasso hand rises, elbow folds back, chest winds right,
#  left hand aims at the target -> 19 COIL (whip cocked behind the head) -> 19-24 hang.
#  Last pose == frame 0 of the LashCrack animation.
# =============================================================================
import bpy, math

ACTION_NAME = "WonderWoman_LassoLash_Windup"
FRAME_END   = 24
MARKERS     = {'COIL': 19}          # action pose markers (Action editor > Marker > Show Pose Markers)
# bone -> list of [frame, rotX, rotY, rotZ]  (degrees, Euler XYZ)
KEYS = {
 'UpTorso': [[0,0.0,0.0,0.0],[2,0.178,-0.69,-0.167],[4,0.66,-2.54,-0.615],[6,1.356,-5.179,-1.256],[8,2.212,-8.375,-2.036],[9,2.682,-10.102,-2.459],[10,3.169,-11.87,-2.894],[12,4.161,-15.386,-3.765],[14,5.123,-18.646,-4.583],[16,5.99,-21.371,-5.282],[18,6.699,-23.294,-5.8],[19,6.991,-23.928,-5.984],[20,7.26,-24.413,-6.136],[21,7.521,-24.823,-6.27],[22,7.759,-25.169,-6.387],[24,8.0,-25.5,-6.5]],
 'HEAD': [[0,-0.0,-0.0,-0.0],[2,-0.137,-0.0,-0.0],[4,-0.603,0.586,0.025],[6,-1.4,2.159,0.217],[8,-2.414,4.403,0.549],[9,-2.972,5.714,0.754],[10,-3.549,7.118,0.979],[12,-4.706,10.089,1.476],[14,-5.784,13.078,1.999],[16,-6.681,15.849,2.511],[18,-7.294,18.165,2.971],[19,-7.502,19.08,3.169],[20,-7.684,19.8,3.34],[21,-7.845,20.339,3.48],[22,-7.993,20.751,3.591],[24,-8.267,21.393,3.762]],
 'FK_UpperArm.R': [[0,0.0,0.0,0.0],[2,-5.201,0.0,0.072],[4,-18.959,0.0,0.261],[6,-38.256,0.0,0.525],[8,-61.097,0.0,0.836],[9,-73.174,0.0,1.0],[10,-85.295,0.0,1.164],[12,-108.502,0.0,1.475],[14,-128.37,0.0,1.737],[16,-142.56,0.0,1.917],[18,-149.375,0.0,1.991],[19,-150.67,0.0,1.999],[20,-151.461,0.0,2.0],[21,-152.082,0.0,2.0],[22,-152.57,0.0,2.0],[24,-153.0,0.0,2.0]],
 'FK_LowerArm.R': [[0,0.0,0.0,0.0],[2,-1.905,0.0,0.0],[4,-6.457,0.0,0.0],[6,-12.419,0.0,0.0],[8,-21.62,0.0,0.0],[9,-28.018,0.0,0.0],[10,-35.404,0.0,0.0],[12,-52.065,0.0,0.0],[14,-69.432,0.0,0.0],[16,-85.328,0.0,0.0],[18,-97.581,0.0,0.0],[19,-101.753,0.0,0.0],[20,-104.609,0.0,0.0],[21,-106.399,0.0,0.0],[22,-107.724,0.0,0.0],[24,-109.0,0.0,0.0]],
 'FK_Hand.R': [[0,0.0,0.0,0.0],[2,1.044,0.0,0.0],[4,3.362,0.0,0.0],[6,5.827,0.0,0.0],[8,7.477,0.0,0.0],[9,7.59,0.0,0.0],[10,6.932,0.0,0.0],[12,3.0,0.0,0.0],[14,-3.619,0.0,0.0],[16,-11.524,0.0,0.0],[18,-19.286,0.0,0.0],[19,-22.68,0.0,0.0],[20,-25.587,0.0,0.0],[21,-27.901,0.0,0.0],[22,-29.762,0.0,0.0],[24,-32.0,0.0,0.0]],
 'FK_UpperArm.L': [[0,0.0,0.0,0.0],[2,-2.879,-0.538,-0.986],[4,-10.354,-1.931,-3.539],[6,-20.584,-3.832,-7.025],[8,-32.292,-6.0,-11.0],[9,-38.265,-7.102,-13.02],[10,-44.071,-8.168,-14.975],[12,-54.434,-10.055,-18.434],[14,-61.898,-11.38,-20.863],[16,-65.352,-11.934,-21.88],[18,-66.205,-11.999,-21.999],[19,-66.428,-12.0,-22.0],[20,-66.62,-12.0,-22.0],[21,-66.778,-12.0,-22.0],[22,-66.899,-12.0,-22.0],[24,-67.0,-12.0,-22.0]],
 'FK_LowerArm.L': [[0,0.0,0.0,0.0],[2,-0.724,0.097,0.0],[4,-2.656,0.352,0.0],[6,-5.392,0.708,0.0],[8,-8.672,1.129,0.0],[9,-10.43,1.35,0.0],[10,-12.214,1.571,0.0],[12,-15.708,1.992,0.0],[14,-18.849,2.345,0.0],[16,-21.33,2.588,0.0],[18,-22.924,2.688,0.0],[19,-23.462,2.698,0.0],[20,-23.926,2.7,0.0],[21,-24.341,2.7,0.0],[22,-24.684,2.7,0.0],[24,-25.0,2.7,0.0]],
 'FK_Hand.L': [[0,0.0,0.0,0.0],[2,-1.077,0.0,0.0],[4,-3.567,0.0,0.0],[6,-6.42,0.0,0.0],[8,-8.781,0.0,-0.0],[9,-9.488,0.0,-0.004],[10,-9.763,0.0,-0.029],[12,-9.041,0.0,-0.268],[14,-7.078,0.0,-0.788],[16,-4.458,0.0,-1.412],[18,-1.751,0.0,-1.932],[19,-0.524,0.0,-2.09],[20,0.593,0.0,-2.166],[21,1.655,0.0,-2.159],[22,2.74,0.0,-2.1],[24,4.0,0.0,-2.0]]
}

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
    print("[WonderWoman_LassoLash_Windup] built: %d bones, %d curves, frames 0-%d" % (len(KEYS), len(_fcurves(act)), FRAME_END))

main()
