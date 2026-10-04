"""Run each delivered script twice on the original rig and measure the REAL keyed actions. usage: verify_clips.py <module>"""
import sys, math, importlib, numpy as np; sys.path.insert(0,'.')
import bpy
from mathutils import Vector
from lib import WORK
import clipkit
mod = importlib.import_module(sys.argv[1]); C = mod.CLIPS
ARMS=("RightUpperArm","RightLowerArm","RightHand","LeftUpperArm","LeftLowerArm","LeftHand")
PAIRS=[(a,b) for a in ARMS for b in ("UpperTorso","Head","LowerTorso")]+[("RightHand","LeftHand"),("RightLowerArm","LeftLowerArm"),("RightHand","LeftLowerArm"),("LeftHand","RightLowerArm")]
keyed = {}
for name, spec in C.items():
    bpy.ops.wm.open_mainfile(filepath=WORK+"/rig.blend"); n_before = len(bpy.data.actions)
    path = f"../animations/{spec['action']}.py"; src = open(path).read()
    for _ in range(2): exec(compile(src, path, "exec"), {"__name__": "__main__"})
    ob = bpy.data.objects["Roblox_R15"]; act = bpy.data.actions[spec["action"]]
    fcs = [fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
    bones = sorted({fc.data_path.split('"')[1] for fc in fcs}); n = spec["length"]
    dense = np.load(f"work/{spec['action']}_dense.npy")
    vals = np.zeros((len(clipkit.BONES), n+1, 3)); dev = (0, None)
    for fc in fcs:
        bi = clipkit.BONES.index(fc.data_path.split('"')[1])
        vals[bi,:,fc.array_index] = [math.degrees(fc.evaluate(f)) for f in range(n+1)]
        d = np.abs(vals[bi,:,fc.array_index]-dense[bi,:,fc.array_index]); i = int(d.argmax())
        if d[i] > dev[0]: dev = (round(float(d[i]),3), (clipkit.BONES[bi], fc.array_index, i))
    keyed[name] = vals
    j = np.abs(np.diff(np.radians(vals),3,axis=1)).max(axis=2).max(axis=0)
    w = spec.get("strike")
    jo = j if not w else np.concatenate([j[:max(0,w[0]-1)], j[w[1]:]])
    sl = []
    for fc in fcs:
        k0, k1 = fc.keyframe_points[0], fc.keyframe_points[-1]
        sl.append(abs((k0.handle_right[1]-k0.co[1])/((k0.handle_right[0]-k0.co[0]) or 1e-9)))
        sl.append(abs((k1.co[1]-k1.handle_left[1])/((k1.co[0]-k1.handle_left[0]) or 1e-9)))
    # clipping per frame on the evaluated meshes
    loc = {o.name: [v.co.copy() for v in o.data.vertices] for o in bpy.data.objects if o.type=='MESH' and o.parent==ob}
    box = {k: (Vector([min(v[i] for v in vs) for i in range(3)]), Vector([max(v[i] for v in vs) for i in range(3)])) for k,vs in loc.items()}
    def pen(a, b, M):
        inv = M[b].inverted(); lo, hi = box[b]; wv = 0
        for v in loc[a]:
            p = inv @ (M[a] @ v); wv = max(wv, min(min(p[i]-lo[i] for i in range(3)), min(hi[i]-p[i] for i in range(3))))
        return wv
    clip = []
    for f in range(n+1):
        bpy.context.scene.frame_set(f); M = {k: bpy.data.objects[k].matrix_world.copy() for k in loc}
        clip.append(max((round(max(pen(a,b,M),pen(b,a,M)),3), f, a, b) for a,b in PAIRS))
    print(f"=== {name}  ({spec['action']}, {n} f, slot {spec['slot']} x{spec['speed']})")
    print("  actions after 2 runs:", sum(a.name == spec['action'] for a in bpy.data.actions), "| other actions kept:", len(bpy.data.actions) == n_before+1)
    print("  keyed bones:", len(bones), "| forbidden (TORSO/legs/feet/root):", [b for b in bones if b in ("TORSO","ROOT") or "Leg" in b or "Foot" in b])
    print("  bezier+auto_clamped:", all(k.interpolation=='BEZIER' and k.handle_left_type=='AUTO_CLAMPED' and k.handle_right_type=='AUTO_CLAMPED' for fc in fcs for k in fc.keyframe_points), "| modifiers:", sum(len(fc.modifiers) for fc in fcs))
    print("  markers:", {m.name: m.frame for m in act.pose_markers})
    print("  keyed vs source max deg:", dev)
    print("  jerk outside action window:", round(float(jo.max()),4), "| inside:", round(float(j.max()),4), "| end-handle slope max:", round(max(sl),5))
    print("  worst clip:", max(clip), "| frames > 0.07:", [c[1] for c in clip if c[0] > 0.07])
print("=== handoffs (deg, max over all bones)")
for name, spec in C.items():
    if spec.get("pin"):
        src, pf = spec["pin"]; print(f"  {src} f{pf} -> {name} f0:", round(float(np.abs(keyed[src][:,pf]-keyed[name][:,0]).max()),4))
if "Throw" in keyed and "Hold" in keyed:
    d = [float(np.abs(keyed["Throw"][:,f]-keyed["Hold"][:,0]).max()) for f in range(30,54)]
    print("  Throw f30..53 vs Hold f0 (any handoff frame):", round(min(d),2), "-", round(max(d),2))
if "Hurl" in keyed:
    print("  Hurl last vs first-frame zero velocity: end slope covered above; Hurl f30 -> Hold f0 replay crossfades over 0.15 s")
if "Spin" in keyed:
    print("  Spin f0 vs rest:", round(float(np.abs(keyed['Spin'][:,0]).max()),4))
