"""Generate the dense data for the demo punch.  usage: python run_action_demo.py [full|upper]"""
from action_demo_punch import *
import pickle, sys, numpy as np
mode = sys.argv[1] if len(sys.argv) > 1 else 'full'
partial = (mode == 'upper')
arm = load()
legs = {s: LegSolver(arm, s) for s in 'LR'}
armsol = {s: ArmSolver(arm, s) for s in 'LR'}
R0 = {s: pose_mat(arm, f'FK_Foot.{s}') for s in 'LR'}
off = arm.location
pivot = {s: Vector((R0[s].translation.x, 0.38 - off.y, 0.21 - off.z)) for s in 'LR'}

def foot_target(f, s):
    ank = R0[s].translation
    base = Matrix.Translation(FOOT_OFF[s]) @ Matrix.Translation(ank) @ Matrix.Rotation(FOOT_YAW[s], 4, 'Z') @ Matrix.Translation(-ank)
    if s == 'R':
        inner = Matrix.Translation(pivot[s]) @ Matrix.Rotation(hermite(f, PIVOT_YAW), 4, 'Z') @ Matrix.Rotation(-hermite(f, HEEL_R), 4, 'X') @ Matrix.Translation(-pivot[s]) @ R0[s]
    else:
        inner = R0[s]
    return base @ inner

def apply_torso(ch):
    for b in ('TORSO', 'UpTorso'):
        if ch[b] is not None: set_chan(arm, b, loc=ch[b][0], rot=ch[b][1])
    bpy.context.view_layer.update()

# ---- ready pose: where the guard hand sits in chest space (used as the start/end of the fist path)
reset_pose(arm)
ch0 = torso_channels(0, partial); apply_torso(ch0)
solR = armsol['R']; Mchest0 = pose_mat(arm, 'UpTorso')
q_guard_R = [*GUARD_R['u'], *GUARD_R['l'], *GUARD_R['h']]
_, _, Mh = solR.chain(Mchest0, q_guard_R)
guard_local = Mchest0.inverted() @ Mh.translation
wrist_target = TARGET - Vector((0, FIST_LEN, 0))
print("guard wrist (chest-local)", tuple(round(x, 2) for x in guard_local), " wrist target", tuple(round(x, 2) for x in wrist_target))

def solve_all(fist_len):
    dense = {}; qprev = {s: None for s in 'LR'}; arm_prev = None; maxcost = 0; maxarm = 0
    wrist_target = TARGET - Vector((0, fist_len, 0))
    for f in range(N_ACTION):
        reset_pose(arm)
        ch = torso_channels(f, partial); apply_torso(ch)
        Mchest = pose_mat(arm, 'UpTorso')
        row = {b: v for b, v in ch.items() if v is not None}
        # ---- legs (full body only): planted feet, right foot pivots on the ball
        if not partial:
            Mp = pose_mat(arm, 'LowerTorso')
            for s in 'LR':
                q0 = qprev[s] if qprev[s] is not None else [-0.4, 0, 0, 0.9, -0.4, 0, 0]
                q, c = legs[s].solve(Mp, foot_target(f, s), q0); qprev[s] = q; maxcost = max(maxcost, c)
                row[f'FK_UpperLeg.{s}'] = ((0, 0, 0), tuple(q[0:3])); row[f'FK_LowerLeg.{s}'] = ((0, 0, 0), (q[3], 0, 0)); row[f'FK_Foot.{s}'] = ((0, 0, 0), tuple(q[4:7]))
        # ---- right (punching) arm: fist path guard -> target, solved by IK every frame in the *current* chest frame
        e = hermite(f, FIST_E)
        p_guard = Mchest @ guard_local
        p = p_guard + (wrist_target - p_guard) * e
        p.z += 0.10 * bump(f, 14, 12) * 0                       # (arc term available; straight line for a cross)
        prior = q_guard_R; pw = [0.04, 0.04, 0.04, 0.03, 0.15, 0.08, 0.08, 0.08]
        q0 = arm_prev if arm_prev is not None else prior
        solR.cont = (q0, [0.10] * 8) if arm_prev is not None else None
        q, c = solR.solve(Mchest, p, prior, pw, q0=q0); arm_prev = q; maxarm = max(maxarm, c)
        if c > 1e-3: print(f'  IK residual high at f{f}: cost {c:.4f}  e={e:+.3f}  wrist-err {(solR.chain(Mchest, q)[2].translation - p).length:.3f}')
        row['FK_UpperArm.R'] = ((0, 0, 0), tuple(q[0:3])); row['FK_LowerArm.R'] = ((0, 0, 0), (q[3], q[4], 0)); row['FK_Hand.R'] = ((0, 0, 0), tuple(q[5:8]))
        # ---- left (lead) arm keeps the guard, drags slightly behind the chest rotation (lag), recoils on impact
        lag = hermite(f - 3, YAW_CHEST) - hermite(f, YAW_CHEST)
        gl = GUARD_L
        row['FK_UpperArm.L'] = ((0, 0, 0), (gl['u'][0] + 0.05 * bump(f, F_HIT + 3, 14), gl['u'][1] + 0.25 * lag, gl['u'][2]))
        row['FK_LowerArm.L'] = ((0, 0, 0), (gl['l'][0] - 0.06 * bump(f, F_HIT + 3, 14), gl['l'][1], 0))
        row['FK_Hand.L'] = ((0, 0, 0), gl['h'])
        # ---- head keeps its eyes on the target: cancel body yaw, chin tucked behind the shoulder
        ytot = (hermite(f, YAW_HIP) if not partial else 0.0) + hermite(f, YAW_CHEST) + (0.22 if partial else 0.0) * 0
        row['HEAD'] = ((0, 0, 0), (-0.12 - 0.03 * bump(f, F_HIT, 12), -0.85 * (hermite(f, YAW_HIP) + hermite(f, YAW_CHEST)), 0.0))
        dense[f] = row
    print("legs max cost %.2e  arm IK max cost %.2e" % (maxcost, maxarm))
    return dense

def measure_front_offset(dense):
    """real hand-mesh front face (world y) minus wrist y at the HIT frame"""
    reset_pose(arm)
    for b, (l, r) in dense[F_HIT].items(): set_chan(arm, b, loc=l, rot=r)
    bpy.context.view_layer.update()
    o = bpy.data.objects['RightHand'].evaluated_get(bpy.context.evaluated_depsgraph_get()); me = o.to_mesh(); M = o.matrix_world
    fy = max((M @ v.co).y for v in me.vertices); o.to_mesh_clear()
    return fy - (pose_mat(arm, 'FK_Hand.R').translation.y + arm.location.y)

dense = solve_all(0.68)                       # pass 1: rough fist offset
FIST_LEN_MEASURED = measure_front_offset(dense)
print("calibrated fist offset (wrist -> front face of the hand at HIT): %.3f studs (was 0.68)" % FIST_LEN_MEASURED)
dense = solve_all(FIST_LEN_MEASURED)          # pass 2: final
pickle.dump(dense, open(f"{SCR}/dense_punch_{mode}.pkl", 'wb'))
