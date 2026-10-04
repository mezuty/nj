import sys, math, numpy as np; sys.path.insert(0,'.')
import bpy
from mathutils import Vector
from lib import open_rig, WORK
import ww_lasso_lash as anim, fk
which = sys.argv[1]   # Windup | Crack
path = f"../animations/WonderWoman_LassoLash_{which}.py"; name = f"WonderWoman_LassoLash_{which}"
dense = np.load(f"work/WonderWoman_LassoLash_{which}_dense.npy")
bpy.ops.wm.open_mainfile(filepath=WORK+"/rig.blend")
n_before = len(bpy.data.actions)
src = open(path).read()
exec(compile(src, path, "exec"), {"__name__":"__main__"}); exec(compile(src, path, "exec"), {"__name__":"__main__"})
ob = bpy.data.objects["Roblox_R15"]; act = bpy.data.actions[name]
R = {}
R["actions_named"] = sum(1 for a in bpy.data.actions if a.name.startswith(name))
R["other_actions_kept"] = (len(bpy.data.actions) == n_before + 1)
R["active_action"] = ob.animation_data.action == act
fcs = [fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
bones = sorted({fc.data_path.split('"')[1] for fc in fcs})
R["keyed_bones"] = bones
R["forbidden_tracks"] = [b for b in bones if b in ("TORSO","ROOT") or "Leg" in b or "Foot" in b]
R["all_bezier_autoclamped"] = all(k.interpolation=='BEZIER' and k.handle_left_type=='AUTO_CLAMPED' and k.handle_right_type=='AUTO_CLAMPED' for fc in fcs for k in fc.keyframe_points)
R["modifiers"] = sum(len(fc.modifiers) for fc in fcs)
R["markers"] = {m.name:m.frame for m in act.pose_markers}
R["fps"] = bpy.context.scene.render.fps
R["IK_FK"] = [ob.pose.bones["PROPERTIES"][k] for k in ("ARM_IK_FK.L","ARM_IK_FK.R","LEG_IK_FK.L","LEG_IK_FK.R")]
n = dense.shape[1]-1
# fidelity
dev = 0; worst=None
for fc in fcs:
    b = fc.data_path.split('"')[1]; bi = anim.BONES.index(b)
    for f in range(n+1):
        d = abs(math.degrees(fc.evaluate(f)) - dense[bi,f,fc.array_index])
        if d > dev: dev, worst = d, (b, fc.array_index, f)
R["max_keyed_vs_source_deg"] = (round(dev,3), worst)
# end handle slopes (rad/frame)
sl = []
for fc in fcs:
    for kp in (fc.keyframe_points[0], fc.keyframe_points[-1]):
        h = kp.handle_right if kp is fc.keyframe_points[0] else kp.handle_left
        sl.append(abs((h[1]-kp.co[1])/((h[0]-kp.co[0]) or 1e-9)))
R["max_end_slope_rad_per_f"] = round(max(sl),5)
# jerk on keyed action sampled per frame
vals = np.zeros((len(anim.BONES),n+1,3))
for fc in fcs:
    bi = anim.BONES.index(fc.data_path.split('"')[1])
    vals[bi,:,fc.array_index] = [fc.evaluate(f) for f in range(n+1)]
j = np.abs(np.diff(vals,3,axis=1)).max(axis=2)
if which=="Crack":
    out = np.concatenate([j[:, 24:]],axis=1); R["jerk_outside_strike(0-23)"] = round(float(out.max()),4); R["jerk_in_strike"] = round(float(j.max()),4)
else:
    R["jerk_max"] = round(float(j.max()),4)
R["first_pose_deg"] = {b: [round(math.degrees(v),2) for v in vals[i,0]] for i,b in enumerate(anim.BONES)} if which=="Windup" else None
R["last_pose_deg_abs_max"] = round(float(np.degrees(np.abs(vals[:,-1])).max()),3)
np.save(f"work/{which}_keyed.npy", np.degrees(vals))
# --- world-space checks per frame: clipping + hand tip
pairs = [(a,b) for a in ("RightUpperArm","RightLowerArm","RightHand","LeftUpperArm","LeftLowerArm","LeftHand") for b in ("UpperTorso","Head","LowerTorso")]
pairs += [("RightHand","LeftHand"),("RightLowerArm","LeftLowerArm"),("RightHand","LeftLowerArm"),("LeftHand","RightLowerArm")]
loc = {o.name: [v.co.copy() for v in o.data.vertices] for o in bpy.data.objects if o.type=='MESH' and o.parent==ob}
box = {k: (Vector([min(v[i] for v in vs) for i in range(3)]), Vector([max(v[i] for v in vs) for i in range(3)])) for k,vs in loc.items()}
def pen(a, b, Ma, Mb):
    inv = Mb.inverted(); lo, hi = box[b]; shrink=0.0; worst = 0.0
    for v in loc[a]:
        p = inv @ (Ma @ v)
        d = min(p[i]-lo[i] for i in range(3)); d = min(d, min(hi[i]-p[i] for i in range(3)))
        worst = max(worst, d)
    return worst
clip = []; tip = []
dg = bpy.context.evaluated_depsgraph_get()
for f in range(n+1):
    bpy.context.scene.frame_set(f)
    M = {k: bpy.data.objects[k].matrix_world.copy() for k in loc}
    w = max(((pen(a,b,M[a],M[b]), max(0,pen(b,a,M[b],M[a])), a, b) for a,b in pairs), key=lambda t:max(t[0],t[1]))
    clip.append((round(max(w[0],w[1]),3), f, w[2], w[3]))
    hb = ob.pose.bones["RightHand"]
    tip.append(ob.matrix_world @ (hb.matrix @ Vector((0,0.55,0))))
R["worst_clip_depth"] = max(clip)
R["clip_frames_over_0.05"] = [c for c in clip if c[0] > 0.05]
sp = [ (tip[f+1]-tip[f]).length for f in range(n)]
R["hand_tip_peak_speed_frame"] = int(np.argmax(sp)); R["hand_tip_peak_speed"] = round(max(sp),3)
if which=="Crack":
    sh = ob.matrix_world @ ob.pose.bones["RightUpperArm"].head
    bpy.context.scene.frame_set(17)
    hb = ob.pose.bones["RightHand"]; wr = ob.matrix_world @ hb.head
    sh = ob.matrix_world @ ob.pose.bones["RightUpperArm"].head
    d = (wr - sh).normalized()
    R["HIT_arm_dir(shoulder->wrist)"] = tuple(round(c,3) for c in d)
    R["HIT_wrist"] = tuple(round(c,2) for c in wr)
for k,v in R.items(): print(f"{k}: {v}")
