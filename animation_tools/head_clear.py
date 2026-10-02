exec(open('gapscan.py').read().split("print(\"baseline")[0])
import sys
dense = pickle.load(open(f"{SCR}/{sys.argv[1]}", 'rb'))
worst = 9
for f in range(0, 360, 6):
    reset_pose(arm)
    for b, (l, r) in dense[f].items(): set_chan(arm, b, loc=l, rot=r)
    bpy.context.view_layer.update()
    Hd = verts('Head'); lo, hi = Hd.min(0), Hd.max(0)
    for n in ('RightHand', 'LeftHand', 'RightLowerArm', 'LeftLowerArm'):
        V = verts(n)
        inside = np.all((V > lo + 0.03) & (V < hi - 0.03), axis=1)       # crude (axis-aligned head box)
        d = np.sqrt(((V[::4, None, :] - Hd[None, ::4, :]) ** 2).sum(-1)).min()
        worst = min(worst, d)
        if inside.any(): print(f"f{f}: {n} enters the head box ({inside.sum()} verts)")
print("closest any hand/forearm vertex to the head over the loop: %.2f studs" % worst)
