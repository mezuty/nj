from ivy_lib import *
import pickle, sys, os
dense = pickle.load(open(f"{SCR}/{sys.argv[1]}", 'rb'))
frames = [int(x) for x in sys.argv[2].split(',')]
views = sys.argv[3].split(',')
out = sys.argv[4]
arm = load(); setup_render(420, 520, 12); VIEWS["3q"]=((6,8,3.5),(0,0,3.0)); VIEWS["front"]=((0,10.5,3.3),(0,0,3.0))
paths = []
for v in views:
    for f in frames:
        reset_pose(arm)
        for b, (l, r) in dense[f].items(): set_chan(arm, b, loc=l, rot=r)
        bpy.context.view_layer.update()
        p = f"{SCR}/_f_{v}_{f}.png"; render_view(p, v); paths.append(p)
contact_sheet(paths, int(sys.argv[5]) if len(sys.argv)>5 else len(frames), f"{SCR}/{out}")
for p in paths: os.remove(p)
