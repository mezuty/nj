from ivy_lib import *
import pickle, sys, numpy as np
arm = load()
dense = pickle.load(open(f"{SCR}/{sys.argv[1]}", 'rb'))
dg = bpy.context.evaluated_depsgraph_get()
def verts(name):
    o = bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = o.to_mesh(); M = o.matrix_world
    v = np.array([(M @ x.co)[:] for x in me.vertices]); o.to_mesh_clear(); return v
frames = [int(x) for x in sys.argv[2].split(',')]
for f in frames:
    reset_pose(arm)
    for b, (l, r) in dense[f].items(): set_chan(arm, b, loc=l, rot=r)
    bpy.context.view_layer.update()
    L = verts('LeftHand'); R = verts('RightHand')
    xgap = R[:, 0].min() - L[:, 0].max()
    # min vertex distance (subsample)
    d = np.sqrt(((L[::3, None, :] - R[None, ::3, :]) ** 2).sum(-1)).min()
    print(f"f{f:3d}  x-gap {xgap:+.3f}   min-vertex-dist {d:.3f}   L.maxx {L[:,0].max():+.2f} R.minx {R[:,0].min():+.2f}")
