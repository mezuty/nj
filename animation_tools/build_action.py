"""
Bake a dense action (pickle {frame: {bone: (loc, euler_rot)}}) into a standalone Blender script.
Works for one-shot ACTIONS (punches, spells, dashes, hit reactions...) and for loops (--cyclic).

  python build_action.py --dense dense_punch_full.pkl --name Punch_Demo --out ../animations/Demo_Punch_Action.py \
      --step 2 --fast 8-24 --markers HIT=16,WINDUP_END=12 --bones all --header header.txt [--cyclic]

--step     key spacing in calm regions;   --fast a-b   every-frame keys in the fast window(s) (repeatable, e.g. --fast 8-24 --fast 40-44)
--bones    all | upper   (upper = the Roblox upper-body whitelist: UpTorso, HEAD, arms.  TORSO/legs/root are NOT keyed)
"""
import bpy, pickle, argparse, os
from mathutils import Euler
ap = argparse.ArgumentParser()
ap.add_argument('--dense', required=True); ap.add_argument('--name', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--step', type=int, default=3); ap.add_argument('--fast', action='append', default=[])
ap.add_argument('--markers', default=''); ap.add_argument('--bones', default='all'); ap.add_argument('--header', default='')
ap.add_argument('--cyclic', action='store_true'); ap.add_argument('--title', default='')
a = ap.parse_args()
SCR = os.environ.get('ANIM_WORKDIR', './work')
dense = pickle.load(open(a.dense if os.path.exists(a.dense) else f"{SCR}/{a.dense}", 'rb'))
N = len(dense); END = N - 1
UPPER = ["UpTorso", "HEAD", "FK_UpperArm.L", "FK_LowerArm.L", "FK_Hand.L", "FK_UpperArm.R", "FK_LowerArm.R", "FK_Hand.R"]
ORDER = ['TORSO', 'UpTorso', 'HEAD', 'FK_UpperArm.R', 'FK_LowerArm.R', 'FK_Hand.R', 'FK_UpperArm.L', 'FK_LowerArm.L', 'FK_Hand.L',
         'FK_UpperLeg.R', 'FK_LowerLeg.R', 'FK_Foot.R', 'FK_UpperLeg.L', 'FK_LowerLeg.L', 'FK_Foot.L']
bones = [b for b in ORDER if b in dense[0] and dense[0][b] is not None]
if a.bones == 'upper':
    bones = [b for b in bones if b in UPPER]           # post-bake filter: strip pelvis/legs/root so engine locomotion owns them
# keys: every STEP frames + every frame inside --fast windows + first/last
fr = set(range(0, N, a.step)) | {0, END}
for w in a.fast:
    lo, hi = (int(x) for x in w.split('-')); fr |= set(range(max(lo, 0), min(hi, END) + 1))
frames = sorted(fr)
def r(v): return [round(float(x), 5) + 0.0 for x in v]
lines = []
for b in bones:
    parts = []
    locs = [dense[f][b][0] for f in frames]
    if any(abs(x) > 1e-6 for l in locs for x in l):
        parts.append('"loc": [' + ", ".join(str(r(l)) for l in locs) + ']')
    if b == 'TORSO':                                    # TORSO is a quaternion bone in this rig
        qs = []; prev = None
        for f in frames:
            q = Euler(dense[f][b][1], 'XYZ').to_quaternion()
            if prev is not None and sum(x * y for x, y in zip(q, prev)) < 0: q = -q
            prev = q; qs.append(r(q))
        parts.append('"quat": ' + str(qs))
    else:
        parts.append('"rot": [' + ", ".join(str(r(dense[f][b][1])) for f in frames) + ']')
    lines.append(f'    "{b}": {{\n        ' + ",\n        ".join(parts) + '\n    },')
markers = {k: int(v) for k, v in (m.split('=') for m in a.markers.split(',') if m)}
header = open(a.header).read() if a.header else f"# {a.title or a.name}\n# Paste into Blender's Scripting tab and press Run Script (Alt+P).\n"
tmpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template_action.py')).read()
out = tmpl % dict(header=header.replace('%', '%%'), name=a.name, end=END, cyclic=a.cyclic, markers=markers, group_order=bones, key_frames=frames, data="\n".join(lines))
open(a.out, 'w').write(out)
print("wrote", a.out, len(out), "bytes |", len(frames), "keys/channel |", len(bones), "bones |", "bones:", a.bones, "| markers", markers)
