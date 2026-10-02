"""Reach / chain-order report for a dense action.  usage: punch_reach.py dense.pkl"""
from ivy_lib import *
import pickle, sys, numpy as np
from action_demo_punch import TARGET, F_HIT, N_ACTION
dense = pickle.load(open(f"{SCR}/{sys.argv[1]}", 'rb'))
arm = load()
tgt = np.array((TARGET + arm.location)[:])
def verts(name):
    o = bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get()); me = o.to_mesh(); M = o.matrix_world
    v = np.array([(M @ x.co)[:] for x in me.vertices]); o.to_mesh_clear(); return v
rows = []
for f in range(N_ACTION):
    reset_pose(arm)
    for b, (l, r) in dense[f].items(): set_chan(arm, b, loc=l, rot=r)
    bpy.context.view_layer.update()
    H = verts('RightHand'); W = pose_mat(arm, 'FK_Hand.R').translation
    d = np.sqrt(((H - tgt) ** 2).sum(1)).min()
    rows.append((f, np.array(W[:]), d, H[:, 1].max()))
d_hit = rows[F_HIT][2]
print("hand-mesh closest vertex to target at HIT frame %d: %.3f studs" % (F_HIT, d_hit))
print("closest approach over action: %.3f at frame %d" % (min(r[2] for r in rows), min(rows, key=lambda r: r[2])[0]))
W = np.array([r[1] for r in rows]); sp = np.linalg.norm(np.diff(W, axis=0), axis=1) * 60
print("peak wrist speed %.1f studs/s at frame %d (hit=%d)" % (sp.max(), int(sp.argmax()) + 1, F_HIT))
print("wrist y(forward) at f0 %.2f, f12 %.2f, f16 %.2f, f19 %.2f, f46 %.2f" % tuple(W[i][1] for i in (0, 12, 16, 19, 46)))
# kinetic chain: frame of peak angular speed for hips -> chest -> upper arm -> forearm -> wrist
def peak(bone, ax):
    k = np.array([dense[f][bone][1][ax] for f in range(N_ACTION)]); return int(np.abs(np.diff(k)).argmax()) + 1
chain = [("hips yaw", 'TORSO', 1), ("chest yaw", 'UpTorso', 1), ("upper arm X", 'FK_UpperArm.R', 0), ("forearm X", 'FK_LowerArm.R', 0), ("wrist X", 'FK_Hand.R', 0)]
print("peak-velocity frame per joint:", {n: peak(b, a) for n, b, a in chain if b in dense[0]})
W16 = rows[F_HIT][1]; wt = tgt - np.array([0, 0.68, 0]) - np.array(arm.location[:])   # armature-space wrist target
print("wrist at HIT %s  wrist target %s  error %.3f" % (tuple(np.round(W16, 2)), tuple(np.round(wt, 2)), np.linalg.norm(W16 - wt)))
reset_pose(arm)
for b, (l, r) in dense[F_HIT].items(): set_chan(arm, b, loc=l, rot=r)
bpy.context.view_layer.update()
H = verts('RightHand'); print("hand mesh bbox at HIT  x[%.2f,%.2f] y[%.2f,%.2f] z[%.2f,%.2f]   target %s" % (H[:,0].min(), H[:,0].max(), H[:,1].min(), H[:,1].max(), H[:,2].min(), H[:,2].max(), tuple(np.round(tgt, 2))))

print("FRONT FACE of fist at HIT: y=%.2f  vs victim surface y=%.2f  -> penetration/gap %+.3f studs (+ = into victim)" % (H[:,1].max(), tgt[1], H[:,1].max() - tgt[1]))
