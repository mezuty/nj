from ivy_lib import *
import sys, os, numpy as np
arm = load(); setup_render(520, 520, 14)
VIEWS['zf'] = ((0, 11, 2.2), (0, 0, 2.2)); VIEWS['q3'] = ((6, 9, 3.0), (0, 0.6, 2.2)); VIEWS['sd'] = ((11, 0.5, 2.2), (0, 0.5, 2.2)); VIEWS['top'] = ((0, 1.0, 14), (0, 0.8, 2.0)); VIEWS['hi'] = ((0, 7, 6.5), (0, 0.8, 1.7)); VIEWS['hi3'] = ((5, 6, 5.5), (0, 0.8, 1.7))
def verts(name):
    o = bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get()); me = o.to_mesh(); M = o.matrix_world
    v = np.array([(M @ x.co)[:] for x in me.vertices]); o.to_mesh_clear(); return v
sets = {}
for a in sys.argv[2:]:
    k, r, l = a.split(':'); sets[k] = (tuple(float(x) for x in r.split(',')), tuple(float(x) for x in l.split(',')))
paths = []
for k, (qr, ql) in sets.items():
    reset_pose(arm); set_chan(arm, 'TORSO', loc=(0, -0.14, 0), rot=(0, 0, 0))
    for side, q in (('R', qr), ('L', ql)):
        set_chan(arm, f'FK_UpperLeg.{side}', rot=(q[0], q[1], q[2])); set_chan(arm, f'FK_LowerLeg.{side}', rot=(q[3], 0, 0)); set_chan(arm, f'FK_Foot.{side}', rot=(q[4], 0, 0))
    bpy.context.view_layer.update()
    L = verts('LeftLowerLeg'); R = verts('RightLowerLeg')
    d = np.sqrt(((L[::3, None] - R[None, ::3]) ** 2).sum(-1)).min()
    print(k, "shin-shin min dist %.2f | lowest z %.2f" % (d, min(L[:, 2].min(), R[:, 2].min(), verts('LeftFoot')[:, 2].min(), verts('RightFoot')[:, 2].min())))
    for v in ('zf', 'hi', 'hi3', 'sd'):
        pth = f"{SCR}/_l2_{k}_{v}.png"; render_view(pth, v); paths.append(pth)
contact_sheet(paths, 4, f"{SCR}/{sys.argv[1]}")
for pth in paths: os.remove(pth)
