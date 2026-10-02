from ivy_body6 import *
import runpy, math, pickle
arm = load()
bpy.context.view_layer.objects.active = arm
runpy.run_path("../animations/Catwoman_Idle.py")
act = arm.animation_data.action
def fcs():
    for l in act.layers:
        for s in l.strips:
            for cb in s.channelbags:
                for fc in cb.fcurves: yield fc
F = list(fcs())
print("action", act.name, "slots", [s.name_display for s in act.slots], "curves", len(F), "keys/curve", len(F[0].keyframe_points))
print("interp set", {kp.interpolation for fc in F for kp in fc.keyframe_points}, {kp.handle_left_type for fc in F for kp in fc.keyframe_points}, {kp.handle_right_type for fc in F for kp in fc.keyframe_points})
print("bones keyed", sorted({fc.data_path.split('"')[1] for fc in F}))
print("modifiers", {m.type for fc in F for m in fc.modifiers}, "fps", bpy.context.scene.render.fps, "range", bpy.context.scene.frame_start, bpy.context.scene.frame_end)
print("PROPERTIES", {k: arm.pose.bones['PROPERTIES'][k] for k in ('ARM_IK_FK.L','ARM_IK_FK.R','LEG_IK_FK.L','LEG_IK_FK.R')})
# deviation keyed-vs-dense
dense = pickle.load(open(f"{SCR}/dense6.pkl","rb"))
maxdev = 0; worst=None
for fc in F:
    bone = fc.data_path.split('"')[1]; prop = fc.data_path.split('.')[-1]; i = fc.array_index
    for f in range(N):
        v = fc.evaluate(f)
        if prop == 'rotation_quaternion':
            q = Euler(dense[f][bone][1], 'XYZ').to_quaternion()[i]
        elif prop == 'location': q = dense[f][bone][0][i]
        else: q = dense[f][bone][1][i]
        d = abs(v - q)
        if d > maxdev: maxdev, worst = d, (bone, prop, i, f)
print("max channel deviation vs dense (rad/units)", round(maxdev, 4), worst)
# loop seam: value+velocity continuity
sm = 0
for fc in F:
    v = [fc.evaluate(f) for f in (-2, -1, 0, 1, N-2, N-1, N, N+1)]
    vel_end = v[6] - v[5]; vel_start = v[3] - v[2]
    sm = max(sm, abs(v[6] - v[2]), abs(vel_end - vel_start) * 10)
print("loop seam max (value diff, 10x velocity diff)", round(sm, 5))
# jerk: max third difference
mj = 0; wj=None
for fc in F:
    vals = [fc.evaluate(f) for f in range(-3, N + 4)]
    for k in range(3, len(vals)):
        j = abs(vals[k] - 3*vals[k-1] + 3*vals[k-2] - vals[k-3])
        if j > mj: mj, wj = j, (fc.data_path, fc.array_index, k - 3)
print("max 3rd difference (jerk proxy)", round(mj, 5), wj)
# foot slide
off = arm.location
R0 = None
def ank(s): return pose_mat(arm, f'FK_Foot.{s}')
reset = {}
saved = {}
bpy.context.scene.frame_set(0)
act_tmp = arm.animation_data.action
arm.animation_data.action = None; reset_pose(arm); R0 = {s: ank(s) for s in 'LR'}; arm.animation_data.action = act_tmp
pivot = {s: Vector((R0[s].translation.x, 0.38 - off.y, 0.21 - off.z)) for s in 'LR'}
maxerr = 0
for f in range(0, N + 1):
    bpy.context.scene.frame_set(f); bpy.context.view_layer.update()
    for s in 'LR':
        a_, dy_, dz_ = foot_adjust(f % N, s)
        T = Matrix.Translation(pivot[s]) @ Matrix.Rotation(-a_, 4, 'X') @ Matrix.Translation(-pivot[s]) @ R0[s]
        ank0 = T.translation.copy()
        T = Matrix.Translation(ank0) @ Matrix.Rotation(FOOT_YAW[s], 4, 'Z') @ Matrix.Translation(-ank0) @ T
        T = Matrix.Translation(FOOT_OFF[s] + Vector((0, dy_, dz_))) @ T
        e = (ank(s).translation - T.translation).length
        maxerr = max(maxerr, e)
print("max foot-plant error over all frames (studs)", round(maxerr, 4))
pickle.dump(None, open(f"{SCR}/_ok", "wb"))
