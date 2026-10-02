from ivy_lib import *
import pickle, sys, numpy as np
dense = pickle.load(open(f"{SCR}/dense10.pkl", 'rb')); arm = load()
f0 = int(sys.argv[1]); P = int(sys.argv[2]) if len(sys.argv) > 2 else 30
pts = []
for f in range(f0, f0 + P + 1):
    reset_pose(arm)
    for b, (l, r) in dense[f].items(): set_chan(arm, b, loc=l, rot=r)
    bpy.context.view_layer.update()
    M = pose_mat(arm, 'UpTorso').inverted()                      # path relative to the chest, so body sway is removed
    pts.append(np.array((M @ pose_mat(arm, 'FK_Hand.R').translation)[:]))
P_ = np.array(pts); c = P_ - P_.mean(0)
u, s, vt = np.linalg.svd(c); print("principal spreads (studs): %.2f  %.2f  %.3f  (circle = first two similar, third ~0)" % tuple(s / np.sqrt(len(c)) * 2 ** 0.5))
print("roundness (minor/major): %.2f   path closes: gap start-end %.3f studs" % (s[1] / s[0], np.linalg.norm(P_[0] - P_[-1])))
sp = np.linalg.norm(np.diff(P_, axis=0), axis=1) * 60; print("hand speed along path: min %.1f max %.1f studs/s (even = steady twirl)" % (sp.min(), sp.max()))
