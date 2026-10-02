"""Scan crossing geometries: solve both legs per candidate, apply, and measure static self-overlap (leg-leg + leg-torso) so we pick the least-clipping crossed pose."""
from ivy_lib import *
import random, math, numpy as np, itertools
random.seed(7)
arm = load()
reset_pose(arm); set_chan(arm, 'TORSO', loc=(0, -0.14, 0), rot=(0, 0, 0)); bpy.context.view_layer.update()
Mp = pose_mat(arm, 'LowerTorso'); Rp = rest_mat(arm, 'LowerTorso')
R = {s: [rest_mat(arm, n) for n in (f'FK_UpperLeg.{s}', f'FK_LowerLeg.{s}', f'FK_Foot.{s}')] for s in 'LR'}
hip = {s: (Mp @ Rp.inverted() @ R[s][0]).translation for s in 'LR'}; zh = hip['R'].z
def fk(s, q):
    Bu = basis((0, 0, 0), (q[0], q[1], q[2])); Bl = basis((0, 0, 0), (q[3], 0, 0)); Bf = basis((0, 0, 0), (q[4], 0, 0))
    Mu = Mp @ Rp.inverted() @ R[s][0] @ Bu; Ml = Mu @ R[s][0].inverted() @ R[s][1] @ Bl; Mf = Ml @ R[s][1].inverted() @ R[s][2] @ Bf
    return Ml.translation, Mf.translation
LO = [-2.1, -1.9, -1.4, 0.2, -0.7]; HI = [-0.2, 1.9, 1.4, 2.6, 0.8]
def solve(s, T):
    def cost(q):
        K, A = fk(s, q); return 3 * (K - T['K']).length_squared + 3 * (A - T['A']).length_squared + 0.05 * q[4] ** 2 + 0.03 * q[1] ** 2 + 0.05 * (q[0] + 1.35) ** 2
    best = None
    for i in range(7000):
        q = [random.uniform(LO[j], HI[j]) for j in range(5)]; c = cost(q)
        if best is None or c < best[0]: best = (c, q)
    c, q = best; step = 0.15
    for it in range(1600):
        q2 = [min(max(q[j] + random.gauss(0, step), LO[j]), HI[j]) for j in range(5)]; c2 = cost(q2)
        if c2 < c: c, q = c2, q2
        if it % 400 == 399: step *= 0.5
    return c, q
def verts(name):
    o = bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get()); me = o.to_mesh(); M = o.matrix_world
    v = np.array([(M @ x.co)[:] for x in me.vertices]); o.to_mesh_clear(); return v
def obb_depth(Vw, name, shrink=0.04):
    o = bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get()); Minv = o.matrix_world.inverted()
    loc = np.array([x.co[:] for x in bpy.data.objects[name].data.vertices]); lo = loc.min(0) + shrink; hi = loc.max(0) - shrink
    Vl = np.array([(Minv @ Vector(v))[:] for v in Vw]); ins = np.all((Vl > lo) & (Vl < hi), axis=1)
    return float(np.minimum(Vl - lo, hi - Vl).min(1)[ins].max()) if ins.any() else 0.0
pairs = [('LeftLowerLeg', 'RightLowerLeg'), ('LeftFoot', 'RightFoot'), ('LeftFoot', 'RightLowerLeg'), ('RightFoot', 'LeftLowerLeg'), ('LeftUpperLeg', 'RightUpperLeg'),
         ('LeftFoot', 'RightUpperLeg'), ('RightFoot', 'LeftUpperLeg'), ('LeftLowerLeg', 'RightUpperLeg'), ('RightLowerLeg', 'LeftUpperLeg'), ('LeftUpperLeg', 'UpperTorso'), ('RightUpperLeg', 'UpperTorso')]
res = []
for zsep, ax, kx, kzl in itertools.product((0.40, 0.60, 0.80), (0.0, 0.08), (0.80, 0.92), (0.10, 0.30)):
    T = {'R': dict(K=Vector((kx, 0.74, zh)), A=Vector((-ax, 0.95, zh - 0.12))),
         'L': dict(K=Vector((-kx, 0.74, zh - kzl)), A=Vector((ax, 0.68, zh - 0.12 - zsep)))}
    qs = {}; cs = 0
    for s in 'RL':
        c, q = solve(s, T[s]); qs[s] = q; cs += c
    reset_pose(arm); set_chan(arm, 'TORSO', loc=(0, -0.14, 0), rot=(0, 0, 0))
    for s in 'RL':
        q = qs[s]; set_chan(arm, f'FK_UpperLeg.{s}', rot=(q[0], q[1], q[2])); set_chan(arm, f'FK_LowerLeg.{s}', rot=(q[3], 0, 0)); set_chan(arm, f'FK_Foot.{s}', rot=(q[4], 0, 0))
    bpy.context.view_layer.update()
    V = {n: verts(n) for pr in pairs for n in pr}
    depth = max(max(obb_depth(V[a], b), obb_depth(V[b], a)) for a, b in pairs)
    shin = max(obb_depth(V['LeftLowerLeg'], 'RightLowerLeg'), obb_depth(V['RightLowerLeg'], 'LeftLowerLeg'))
    res.append((depth + 2 * cs, depth, shin, cs, (zsep, ax, kx, kzl), qs))
res.sort(key=lambda r: r[0])
for r in res[:5]: print("score %.3f  worst-overlap %.3f  shin-shin %.3f  solve-cost %.3f  zsep %.2f ankle-x %.2f knee-x %.2f kneeL-drop %.2f" % (r[0], r[1], r[2], r[3], *r[4]))
b = res[0]
print("BEST_R=" + ",".join(f"{x:.3f}" for x in b[5]['R'])); print("BEST_L=" + ",".join(f"{x:.3f}" for x in b[5]['L']))
