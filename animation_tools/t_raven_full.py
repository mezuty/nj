from ivy_lib import *
import sys, os
import ivy_body13 as B
arm = load(); setup_render(520, 560, 12)
VIEWS['zf'] = ((0, 12, 3.0), (0, 0, 3.0)); VIEWS['q3'] = ((7, 9, 3.6), (0, 0.4, 2.9)); VIEWS['hi'] = ((0, 8, 6.0), (0, 0.6, 2.4))
frames = [int(x) for x in sys.argv[2].split(',')]; paths = []
for f in frames:
    reset_pose(arm)
    for b, (l, r) in B.body_channels(f).items(): set_chan(arm, b, loc=l, rot=r)
    bpy.context.view_layer.update()
    for v in ('zf', 'q3', 'hi'):
        p = f"{SCR}/_rf_{f}_{v}.png"; render_view(p, v); paths.append(p)
contact_sheet(paths, 3, f"{SCR}/{sys.argv[1]}")
for p in paths: os.remove(p)
