exec(open('gapscan.py').read().split("print(\"baseline")[0])
import sys
dense = pickle.load(open(f"{SCR}/{sys.argv[1]}", 'rb'))
def obb_inside(Vw, name, shrink=0.03):
    o = bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get())
    Minv = o.matrix_world.inverted()
    loc = np.array([(x.co)[:] for x in bpy.data.objects[name].data.vertices])
    lo = loc.min(0) + shrink; hi = loc.max(0) - shrink
    Vl = np.array([(Minv @ Vector(v))[:] for v in Vw])
    ins = np.all((Vl > lo) & (Vl < hi), axis=1)
    depth = np.minimum(Vl - lo, hi - Vl).min(1)
    return ins, depth
worst_all = 0
for f in range(0, 360, 6):
    reset_pose(arm)
    for b, (l, r) in dense[f].items(): set_chan(arm, b, loc=l, rot=r)
    bpy.context.view_layer.update()
    pen = 0.0; wn = ''
    for n in ('LeftUpperArm', 'RightUpperArm', 'LeftLowerArm', 'RightLowerArm', 'LeftHand', 'RightHand'):
        V = verts(n)
        for tn in ('UpperTorso', 'LowerTorso'):
            ins, d = obb_inside(V, tn)
            if ins.any():
                dd = float(d[ins].max())
                if dd > pen: pen, wn = dd, f"{n}->{tn}"
    worst_all = max(worst_all, pen)
    if pen > 0.02: print(f"f{f:3d} clip depth {pen:.3f} {wn}")
print("WORST clip depth over loop:", round(worst_all, 3))
