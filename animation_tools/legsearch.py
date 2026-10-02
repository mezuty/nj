"""Search leg joint angles for a cross-legged sit: knees out, shins sweeping FORWARD and INWARD to the centre (right shin resting over the left).
   Pure analytic FK (fast).  usage: legsearch.py"""
from ivy_lib import *
import random, math, numpy as np
random.seed(5)
arm = load()
reset_pose(arm); set_chan(arm, 'TORSO', loc=(0, -0.14, 0), rot=(0, 0, 0)); bpy.context.view_layer.update()
Mp = pose_mat(arm, 'LowerTorso'); Rp = rest_mat(arm, 'LowerTorso')
R = {s: [rest_mat(arm, n) for n in (f'FK_UpperLeg.{s}', f'FK_LowerLeg.{s}', f'FK_Foot.{s}')] for s in 'LR'}
hip = {s: (Mp @ Rp.inverted() @ R[s][0]).translation for s in 'LR'}
print("hips", {s: tuple(round(x, 2) for x in hip[s]) for s in 'LR'})
def fk(s, q):
    Bu = basis((0, 0, 0), (q[0], q[1], q[2])); Bl = basis((0, 0, 0), (q[3], 0, 0)); Bf = basis((0, 0, 0), (q[4], 0, 0))
    Mu = Mp @ Rp.inverted() @ R[s][0] @ Bu; Ml = Mu @ R[s][0].inverted() @ R[s][1] @ Bl; Mf = Ml @ R[s][1].inverted() @ R[s][2] @ Bf
    return Ml.translation, Mf.translation, Mf
# targets: knees out ~30 deg; ankles at the centre line, in front; RIGHT shin on top of the LEFT (stacked in z)
zh = hip['R'].z
T = {'R': dict(K=Vector((0.86, 0.74, zh + 0.00)), A=Vector((-0.08, 0.92, zh - 0.22))),
     'L': dict(K=Vector((-0.86, 0.74, zh - 0.10)), A=Vector((0.08, 0.66, zh - 0.62)))}
LO = [-2.1, -1.9, -1.4, 0.2, -0.7]; HI = [-0.2, 1.9, 1.4, 2.6, 0.8]
def cost(s, q):
    K, A, Mf = fk(s, q)
    c = 3 * (K - T[s]['K']).length_squared + 3 * (A - T[s]['A']).length_squared + 0.05 * (q[4]) ** 2 + 0.03 * q[1] ** 2 + 0.05 * (q[0] + 1.35) ** 2
    # foot plate should lie flat-ish relative to the shin: keep foot roll/yaw small by penalising Mf's z-axis tilt
    return c
sol = {}
for s in 'LR':
    best = None
    for i in range(30000):
        q = [random.uniform(LO[j], HI[j]) for j in range(5)]
        c = cost(s, q)
        if best is None or c < best[0]: best = (c, q)
    c, q = best; step = 0.15
    for it in range(4000):
        q2 = [min(max(q[j] + random.gauss(0, step), LO[j]), HI[j]) for j in range(5)]
        c2 = cost(s, q2)
        if c2 < c: c, q = c2, q2
        if it % 1000 == 999: step *= 0.5
    K, A, _ = fk(s, q); sol[s] = q
    print(s, "cost %.4f" % c, "q =", [round(x, 3) for x in q], "| knee", tuple(round(x, 2) for x in K), "ankle", tuple(round(x, 2) for x in A))
print("RAVEN_LEG_R=" + ",".join(f"{x:.3f}" for x in sol['R']))
print("RAVEN_LEG_L=" + ",".join(f"{x:.3f}" for x in sol['L']))
