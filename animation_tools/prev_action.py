"""Contact sheet of an action's dense data with a red marker where the fist should land.  usage: prev_action.py dense.pkl frames views out.png cols"""
from ivy_lib import *
import pickle, sys, os
from action_demo_punch import TARGET
dense = pickle.load(open(f"{SCR}/{sys.argv[1]}", 'rb')); frames = [int(x) for x in sys.argv[2].split(',')]
views = sys.argv[3].split(','); out = sys.argv[4]; cols = int(sys.argv[5])
arm = load(); setup_render(480, 520, 12)
VIEWS['front'] = ((0, 12, 3.6), (0, 0.8, 3.3)); VIEWS["3q"] = ((8, 6, 3.8), (0, 1.0, 3.3)); VIEWS['side'] = ((-12, 1.0, 3.4), (0, 1.0, 3.3)); VIEWS['top'] = ((0, 1.0, 14), (0, 1.0, 3.0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=tuple(TARGET + arm.location))
m = bpy.context.object; mat = bpy.data.materials.new('t'); mat.diffuse_color = (1, 0, 0, 1); m.data.materials.append(mat)
mat.use_nodes = True; mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (1, 0.05, 0.05, 1)
paths = []
for v in views:
    for f in frames:
        reset_pose(arm)
        for b, (l, r) in dense[f].items(): set_chan(arm, b, loc=l, rot=r)
        bpy.context.view_layer.update()
        p = f"{SCR}/_a_{v}_{f}.png"; render_view(p, v); paths.append(p)
contact_sheet(paths, cols, f"{SCR}/{out}")
for p in paths: os.remove(p)
