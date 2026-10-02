from ivy_body2 import *
import pickle, sys
arm = load()
legs = {s: LegSolver(arm, s) for s in 'LR'}
R0 = {s: pose_mat(arm, f'FK_Foot.{s}') for s in 'LR'}
off = arm.location
pivot = {}
for s in 'LR':
    a = R0[s].translation
    pivot[s] = Vector((a.x, 0.38 - off.y, 0.21 - off.z))
dense = {}
q_prev = {s: None for s in 'LR'}
maxcost = 0
for f in range(N):
    ch = body_channels(f)
    for b in ('TORSO',): set_chan(arm, b, loc=ch[b][0], rot=ch[b][1])
    bpy.context.view_layer.update()
    Mp = pose_mat(arm, 'LowerTorso')
    row = dict(ch)
    for s in 'LR':
        a = heel(f, s)
        Rx = Matrix.Rotation(-a, 4, 'X')
        T = Matrix.Translation(pivot[s]) @ Rx @ Matrix.Translation(-pivot[s]) @ R0[s]
        q0 = q_prev[s] if q_prev[s] is not None else [-0.15, 0, 0, 0.3, -0.15, 0, 0]
        q, c = legs[s].solve(Mp, T, q0)
        if c > 2e-5: print("poor solve", f, s, c)
        maxcost = max(maxcost, c)
        q_prev[s] = q
        row[f'FK_UpperLeg.{s}'] = ((0, 0, 0), tuple(q[0:3]))
        row[f'FK_LowerLeg.{s}'] = ((0, 0, 0), (q[3], 0, 0))
        row[f'FK_Foot.{s}'] = ((0, 0, 0), tuple(q[4:7]))
    dense[f] = row
print("max cost", maxcost)
# periodicity of solved legs
for s in 'LR':
    print(s, "wrap diff", max(abs(a - b) for a, b in zip(list(dense[0][f'FK_UpperLeg.{s}'][1]) + [dense[0][f'FK_LowerLeg.{s}'][1][0]], list(dense[N-1][f'FK_UpperLeg.{s}'][1]) + [dense[N-1][f'FK_LowerLeg.{s}'][1][0]])))
pickle.dump(dense, open(f"{SCR}/dense2.pkl", 'wb'))
