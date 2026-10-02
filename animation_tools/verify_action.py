"""
Quality gates for a baked ONE-SHOT ACTION (run the generated script in headless Blender and measure the REAL keyed result).
usage: python verify_action.py ../animations/Demo_Punch_Action.py dense_punch_full.pkl [upper]
"""
from ivy_lib import *
import runpy, sys, pickle, numpy as np
from action_demo_punch import TARGET, F_HIT, F_WIND, N_ACTION, FOOT_OFF, FOOT_YAW, hermite, HEEL_R, PIVOT_YAW
script, densef = sys.argv[1], sys.argv[2]; upper = len(sys.argv) > 3 and sys.argv[3] == 'upper'
dense = pickle.load(open(f"{SCR}/{densef}", 'rb'))
arm = load(); bpy.context.view_layer.objects.active = arm
for i in range(2): runpy.run_path(script)                                     # run twice: must be idempotent
act = arm.animation_data.action; scene = bpy.context.scene
F = [fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
ok = lambda c: "PASS" if c else "FAIL"
print("== STRUCTURE")
print(" ", ok(len([a for a in bpy.data.actions if a.name == act.name]) == 1), "single action after 2 runs:", act.name)
print(" ", ok(all(kp.interpolation == 'BEZIER' and kp.handle_left_type == 'AUTO_CLAMPED' and kp.handle_right_type == 'AUTO_CLAMPED' for fc in F for kp in fc.keyframe_points)), "all keys BEZIER + AUTO_CLAMPED")
print(" ", ok(not any(m.type == 'CYCLES' for fc in F for m in fc.modifiers)), "no Cycles modifier (one-shot, not a loop)")
mk = {m.name: m.frame for m in scene.timeline_markers}; print(" ", ok(mk.get('HIT') == F_HIT and mk.get('WINDUP_END') == F_WIND), "markers", mk)
keyed = sorted({fc.data_path.split('"')[1] for fc in F}); print("  keyed bones:", keyed)
if upper: print(" ", ok(not any(b in keyed for b in ('TORSO',)) and not any('Leg' in b or 'Foot' in b for b in keyed)), "upper-body filter: no TORSO / leg / foot tracks")
print("  frame range", scene.frame_start, scene.frame_end, "| fps", scene.render.fps)
print("== FIDELITY / SMOOTHNESS")
def ev(fc, f): return fc.evaluate(f)
maxdev = 0
for fc in F:
    b = fc.data_path.split('"')[1]; prop = fc.data_path.split('.')[-1]; i = fc.array_index
    for f in range(N_ACTION):
        v = ev(fc, f)
        if prop == 'rotation_quaternion': q = Euler(dense[f][b][1], 'XYZ').to_quaternion()[i]
        elif prop == 'location': q = dense[f][b][0][i]
        else: q = dense[f][b][1][i]
        maxdev = max(maxdev, abs(v - q))
print("  keyed-vs-dense max deviation %.4f rad (%.2f deg) %s" % (maxdev, np.degrees(maxdev), ok(maxdev < 0.03)))
jerk = {}
for fc in F:
    vals = np.array([ev(fc, f) for f in range(N_ACTION)])
    j = np.abs(vals[3:] - 3 * vals[2:-1] + 3 * vals[1:-2] - vals[:-3])
    for k in range(len(j)):
        fr = k + 3
        if not (F_WIND - 1 <= fr <= F_HIT + 6): jerk[(fc.data_path, fc.array_index)] = max(jerk.get((fc.data_path, fc.array_index), 0), j[k])
print("  max jerk OUTSIDE the strike window %.4f %s   (strike window frames %d-%d excluded: impact + hit-stop are intentional snaps)" % (max(jerk.values()), ok(max(jerk.values()) < 0.03), F_WIND - 1, F_HIT + 6))
print("== BLENDABILITY (starts and ends on the ready pose, at rest)")
d0 = max(abs(ev(fc, 0) - ev(fc, N_ACTION - 1)) for fc in F)
def end_slope(fc, first):                       # slope of the end handle = velocity at the very first / last frame
    kp = fc.keyframe_points[0] if first else fc.keyframe_points[-1]; h = kp.handle_right if first else kp.handle_left
    return abs((h[1] - kp.co[1]) / (h[0] - kp.co[0])) if abs(h[0] - kp.co[0]) > 1e-9 else 0.0
v0 = max(end_slope(fc, True) for fc in F); v1 = max(end_slope(fc, False) for fc in F)
print("  first-vs-last pose max difference %.5f %s | velocity at frame 0: %.5f/f, at last frame: %.5f/f %s" % (d0, ok(d0 < 1e-3), v0, v1, ok(v0 < 0.002 and v1 < 0.002)))
print("== GAMEPLAY SYNC")
tgt = np.array((TARGET + arm.location)[:])
def verts(name):
    o = bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get()); me = o.to_mesh(); M = o.matrix_world
    v = np.array([(M @ x.co)[:] for x in me.vertices]); o.to_mesh_clear(); return v
W = []; front = []
for f in range(N_ACTION):
    scene.frame_set(f); bpy.context.view_layer.update()
    W.append(np.array(pose_mat(arm, 'FK_Hand.R').translation[:])); front.append(verts('RightHand')[:, 1].max())
W = np.array(W); sp = np.linalg.norm(np.diff(W, axis=0), axis=1) * scene.render.fps
pk = int(sp.argmax()) + 1
print("  fist FRONT FACE at HIT frame: y=%.2f vs victim surface y=%.2f -> gap %+.3f studs %s" % (front[F_HIT], tgt[1], front[F_HIT] - tgt[1], ok(abs(front[F_HIT] - tgt[1]) < 0.08)))
print("  peak fist speed %.1f studs/s at frame %d (impact %d) %s" % (sp.max(), pk, F_HIT, ok(F_HIT - 4 <= pk <= F_HIT)))
print("  fist never passes the victim by more than %.3f studs %s" % (max(0, max(front) - tgt[1]), ok(max(front) - tgt[1] < 0.15)))
if not upper:
    print("== FEET (planted; right foot pivots on its ball)")
    R0 = {}; arm.animation_data.action = None; reset_pose(arm)
    for s in 'LR': R0[s] = pose_mat(arm, f'FK_Foot.{s}')
    arm.animation_data.action = act
    off = arm.location; piv = {s: Vector((R0[s].translation.x, 0.38 - off.y, 0.21 - off.z)) for s in 'LR'}
    ball = {s: [] for s in 'LR'}; ank_err = 0
    for f in range(N_ACTION):
        scene.frame_set(f); bpy.context.view_layer.update()
        for s in 'LR':
            M = pose_mat(arm, f'FK_Foot.{s}'); ball[s].append(np.array((M @ (R0[s].inverted() @ piv[s]))[:]))
    for s in 'LR':
        B = np.array(ball[s]); print("  %s foot ball-of-foot drift over the whole action: %.3f studs %s" % (s, np.abs(B - B[0]).max(), ok(np.abs(B - B[0]).max() < 0.03)))
print("RESULT: see PASS/FAIL lines above")
