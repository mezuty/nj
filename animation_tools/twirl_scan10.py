from ivy_lib import *
import numpy as np, itertools, os
arm = load()
import importlib
res = []
for cl, ux, lx, pl, hx, ph in itertools.product((-0.9, -1.2, -1.5), (0.35, 0.5, 0.65), (0.6, 0.9), (-1.2, -1.6, -2.0), (0.4,), (-3.0,)):
    os.environ.update(TW_CL=str(cl), TW_UX=str(ux), TW_LX=str(lx), TW_PL=str(pl), TW_HX=str(hx), TW_PH=str(ph))
    import ivy_body10; importlib.reload(ivy_body10)
    pts = []
    for f in range(150, 191):
        reset_pose(arm)
        for b, (l, r) in ivy_body10.body_channels(f).items():
            if b.startswith('FK_') and ('Leg' in b or 'Foot' in b): continue
            set_chan(arm, b, loc=l, rot=r)
        bpy.context.view_layer.update()
        pts.append(np.array((pose_mat(arm, 'UpTorso').inverted() @ pose_mat(arm, 'FK_Hand.R').translation)[:]))
    P = np.array(pts); c = P - P.mean(0); u, s, vt = np.linalg.svd(c)
    rad = s[0] / np.sqrt(len(c)) * 2 ** 0.5; rnd = s[1] / s[0]; planar = s[2] / s[0]
    res.append((abs(rad - 0.6) + 1.2 * (1 - rnd) + 2 * planar, rad, rnd, planar, (cl, ux, lx, pl, hx, ph)))
res.sort()
for r in res[:6]: print("score %.3f radius %.2f roundness %.2f planarity-err %.2f  centre-elbow %.2f ux %.2f lx %.2f pl %.1f hx %.2f ph %.1f" % (r[0], r[1], r[2], r[3], *r[4]))
