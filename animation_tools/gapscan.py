from ivy_lib import *
import pickle, numpy as np, itertools
arm = load()
dense = pickle.load(open(f"{SCR}/dense7.pkl", 'rb'))
def verts(name):
    o = bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = o.to_mesh(); M = o.matrix_world
    v = np.array([(M @ x.co)[:] for x in me.vertices]); o.to_mesh_clear(); return v
def gap_for(ux, uy, uz, lx, ly, hx, f=114):
    reset_pose(arm)
    for b, (l, r) in dense[f].items():
        if b.startswith('FK_') and ('Arm' in b or 'Hand' in b): continue
        set_chan(arm, b, loc=l, rot=r)
    for side, sg in (('L', -1), ('R', 1)):
        set_chan(arm, f'FK_UpperArm.{side}', rot=(ux, -sg * uy, sg * uz)); set_chan(arm, f'FK_LowerArm.{side}', rot=(lx, -sg * ly, 0)); set_chan(arm, f'FK_Hand.{side}', rot=(hx, 0, 0))
    bpy.context.view_layer.update()
    L = verts('LeftHand'); R = verts('RightHand'); LA = verts('LeftLowerArm'); RA = verts('RightLowerArm')
    return R[:, 0].min() - L[:, 0].max(), (L[:,2].min(), L[:,2].max(), L[:,1].mean())
print("baseline b (0.30,0.60,0.10 / 1.20,0.70):", gap_for(-0.30, 0.60, 0.10, -1.20, 0.70, 0.0))
print("pose a   (0.40,0.70,0.10 / 1.40,0.80):", gap_for(-0.40, 0.70, 0.10, -1.40, 0.80, 0.0))
res = []
for uy, ly, lx, uz in itertools.product((0.7, 0.9, 1.1, 1.3), (0.7, 0.9, 1.1, 1.3), (-1.0, -1.3), (0.1, 0.3)):
    g, ex = gap_for(-0.30, uy, uz, lx, ly, 0.0)
    res.append((abs(g), g, uy, ly, lx, uz, ex))
res.sort()
for r in res[:8]: print("gap %+.3f  uy %.1f ly %.1f lx %.1f uz %.1f  hand z[%.2f,%.2f] y %.2f" % (r[1], r[2], r[3], r[4], r[5], *r[6]))
