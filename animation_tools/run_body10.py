from ivy_body10 import *
import pickle, numpy as np
arm = load()
legs = {s: LegSolver(arm, s) for s in 'LR'}
R0 = {s: pose_mat(arm, f'FK_Foot.{s}') for s in 'LR'}
off = arm.location
pivot = {s: Vector((R0[s].translation.x, 0.38 - off.y, 0.21 - off.z)) for s in 'LR'}
def target(f, s):
    a, dy, dz = foot_adjust(f, s)
    T = Matrix.Translation(pivot[s]) @ Matrix.Rotation(-a, 4, 'X') @ Matrix.Translation(-pivot[s]) @ R0[s]
    ank = T.translation.copy()
    T = Matrix.Translation(ank) @ Matrix.Rotation(FOOT_YAW[s], 4, 'Z') @ Matrix.Translation(-ank) @ T
    return Matrix.Translation(FOOT_OFF[s] + Vector((0, dy, dz))) @ T
if __name__ == "__main__":
    dense = {}; q_prev = {s: None for s in 'LR'}; maxcost = 0
    for f in range(N):
        ch = body_channels(f)
        set_chan(arm, 'TORSO', loc=ch['TORSO'][0], rot=ch['TORSO'][1]); bpy.context.view_layer.update()
        Mp = pose_mat(arm, 'LowerTorso'); row = dict(ch)
        for s in 'LR':
            q0 = q_prev[s] if q_prev[s] is not None else [-0.4, 0, 0, 0.9, -0.4, 0, 0]
            q, c = legs[s].solve(Mp, target(f, s), q0)
            if c > 1e-4: print("poor solve", f, s, round(c, 6))
            maxcost = max(maxcost, c); q_prev[s] = q
            row[f'FK_UpperLeg.{s}'] = ((0, 0, 0), tuple(q[0:3])); row[f'FK_LowerLeg.{s}'] = ((0, 0, 0), (q[3], 0, 0)); row[f'FK_Foot.{s}'] = ((0, 0, 0), tuple(q[4:7]))
        dense[f] = row
    print("max cost", maxcost)
    pickle.dump(dense, open(f"{SCR}/dense10.pkl", 'wb'))
    for nm in ('UpperLeg', 'LowerLeg', 'Foot'):
        for s in 'LR':
            k = np.array([dense[f][f'FK_{nm}.{s}'][1][0] for f in range(N)]); dd = np.diff(np.concatenate([k, k[:1]]))
            print(nm, s, "range", k.min().round(2), k.max().round(2), "max step", abs(dd).max().round(4))
    res = []
    for b in dense[0]:
        for ax in range(3):
            k = np.array([dense[f][b][1][ax] for f in range(N)]); kk = np.concatenate([k[-3:], k, k[:3]])
            j = np.abs(kk[3:] - 3*kk[2:-1] + 3*kk[1:-2] - kk[:-3]); res.append((j.max(), b, ax, int(j.argmax())))
    res.sort(reverse=True); print("top jerk", [(round(a, 4), b, c, d) for a, b, c, d in res[:5]])
