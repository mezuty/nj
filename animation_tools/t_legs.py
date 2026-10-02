from ivy_lib import *
import sys, json, os, numpy as np
arm = load(); setup_render(420, 460, 12)
VIEWS['zf'] = ((0, 11, 2.4), (0, 0, 2.4)); VIEWS['sd'] = ((11, 0.5, 2.4), (0, 0.5, 2.4)); VIEWS['top'] = ((0, 1.2, 14), (0, 0.8, 2.0)); VIEWS['q3'] = ((6, 9, 3.2), (0, 0.6, 2.2))
def verts(name):
    o = bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get()); me = o.to_mesh(); M = o.matrix_world
    v = np.array([(M @ x.co)[:] for x in me.vertices]); o.to_mesh_clear(); return v
cands = json.loads(sys.argv[1]); paths = []
for k, p in cands.items():
    tx, ty, tz, kx, fx = p[:5]; ky = p[5] if len(p) > 5 else 0.0; ty2 = p[6] if len(p) > 6 else 0.0
    reset_pose(arm)
    set_chan(arm, 'TORSO', loc=(0, -0.55, 0), rot=(0, 0, 0))
    for side, sg in (('L', -1), ('R', 1)):
        set_chan(arm, f'FK_UpperLeg.{side}', rot=(tx, -sg * ty, sg * tz)); set_chan(arm, f'FK_LowerLeg.{side}', rot=(kx, -sg * ky, 0)); set_chan(arm, f'FK_Foot.{side}', rot=(fx, 0, 0))
    bpy.context.view_layer.update()
    L = verts('LeftLowerLeg'); R = verts('RightLowerLeg'); LF = verts('LeftFoot'); RF = verts('RightFoot')
    gap = R[:, 0].min() - L[:, 0].max()
    d = np.sqrt(((L[::3, None] - R[None, ::3]) ** 2).sum(-1)).min()
    zlo = min(LF[:, 2].min(), RF[:, 2].min(), L[:, 2].min(), R[:, 2].min())
    ak_l = pose_mat(arm, 'FK_Foot.L').translation; ak_r = pose_mat(arm, 'FK_Foot.R').translation
    print(k, "ankles L %s R %s | shin x-gap %+.2f  min shin-shin dist %.2f | lowest point z %.2f" % (tuple(round(x, 2) for x in ak_l), tuple(round(x, 2) for x in ak_r), gap, d, zlo))
    for v in ('zf', 'q3', 'sd'):
        pth = f"{SCR}/_l_{k}_{v}.png"; render_view(pth, v); paths.append(pth)
contact_sheet(paths, 3, f"{SCR}/{sys.argv[2]}")
for pth in paths: os.remove(pth)
