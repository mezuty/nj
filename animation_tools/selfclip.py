"""General self-intersection check between limb pairs (oriented-box vertex test, both directions).  usage: selfclip.py dense.pkl [thresh]"""
exec(open('gapscan.py').read().split("print(\"baseline")[0])
import sys, itertools
dense = pickle.load(open(f"{SCR}/{sys.argv[1]}", 'rb')); TH = float(sys.argv[2]) if len(sys.argv) > 2 else 0.07
def obb_depth(Vw, name, shrink=0.04):
    o = bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get()); Minv = o.matrix_world.inverted()
    loc = np.array([x.co[:] for x in bpy.data.objects[name].data.vertices]); lo = loc.min(0) + shrink; hi = loc.max(0) - shrink
    Vl = np.array([(Minv @ Vector(v))[:] for v in Vw]); ins = np.all((Vl > lo) & (Vl < hi), axis=1)
    return float(np.minimum(Vl - lo, hi - Vl).min(1)[ins].max()) if ins.any() else 0.0
parts = ['UpperArm', 'LowerArm', 'Hand', 'UpperLeg', 'LowerLeg', 'Foot']
names = [f'{s}{p}' for s in ('Left', 'Right') for p in parts] + ['LowerTorso', 'UpperTorso', 'Head']
skip = lambda a, b: a == b or {a, b} <= {'LowerTorso', 'UpperTorso', 'Head'} or any(a.endswith(x) and b.endswith(x) and a[:4] == b[:4] for x in parts) or \
    (a[:4] == b[:4] and False)
rel = {('UpperArm', 'LowerArm'), ('LowerArm', 'Hand'), ('UpperLeg', 'LowerLeg'), ('LowerLeg', 'Foot'), ('UpperArm', 'UpperTorso'), ('UpperLeg', 'LowerTorso'), ('Head', 'UpperTorso'), ('LowerTorso', 'UpperTorso')}
def parent_pair(a, b):
    sa, sb = a.replace('Left', '').replace('Right', ''), b.replace('Left', '').replace('Right', '')
    same = (a.startswith('Left') and b.startswith('Left')) or (a.startswith('Right') and b.startswith('Right')) or not (a[:4] in ('Left', 'Righ') and b[:4] in ('Left', 'Righ'))
    return same and ((sa, sb) in rel or (sb, sa) in rel)
pairs = [(a, b) for a, b in itertools.combinations(names, 2) if not parent_pair(a, b)]
worst = {}
for f in range(0, 360, 6):
    reset_pose(arm)
    for b, (l, r) in dense[f].items(): set_chan(arm, b, loc=l, rot=r)
    bpy.context.view_layer.update()
    V = {n: verts(n) for n in names}
    for a, b in pairs:
        d = max(obb_depth(V[a], b), obb_depth(V[b], a))
        if d > worst.get((a, b), (0, 0))[0]: worst[(a, b)] = (d, f)
bad = sorted(((d, f, a, b) for (a, b), (d, f) in worst.items() if d > TH), reverse=True)
print("SELFCLIP pairs over %.2f stud: %d" % (TH, len(bad)))
for d, f, a, b in bad[:12]: print("  %.3f  f%d  %s <-> %s" % (d, f, a, b))
print("SELFCLIP worst overall: %.3f" % max([d for d, _ in worst.values()] + [0]))
