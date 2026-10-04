"""Static pose exploration: render + clip depth for a set of named poses.  usage: posecheck.py <module> <prefix> views..."""
import sys, importlib; sys.path.insert(0,'.')
from lib import *
import bpy
from mathutils import Vector
ob = open_rig()
loc = {o.name: [v.co.copy() for v in o.data.vertices] for o in bpy.data.objects if o.type=='MESH' and o.parent==ob}
box = {k: (Vector([min(v[i] for v in vs) for i in range(3)]), Vector([max(v[i] for v in vs) for i in range(3)])) for k,vs in loc.items()}
def pen(a,b):
    Ma=bpy.data.objects[a].matrix_world; Mb=bpy.data.objects[b].matrix_world; inv=Mb.inverted(); lo,hi=box[b]; w=0
    for v in loc[a]:
        p=inv@(Ma@v); d=min(min(p[i]-lo[i] for i in range(3)),min(hi[i]-p[i] for i in range(3))); w=max(w,d)
    return w
ARMS=("RightUpperArm","RightLowerArm","RightHand","LeftUpperArm","LeftLowerArm","LeftHand")
PAIRS=[(a,b) for a in ARMS for b in ("UpperTorso","Head","LowerTorso")]+[("RightHand","LeftHand"),("RightLowerArm","LeftLowerArm"),("RightHand","LeftLowerArm"),("LeftHand","RightLowerArm"),("RightLowerArm","LeftUpperArm"),("LeftLowerArm","RightUpperArm")]
def clip_report():
    r=max(((max(pen(a,b),pen(b,a)),a,b) for a,b in PAIRS)); return (round(r[0],3),r[1],r[2])
def hand_pos(side):
    hb=ob.pose.bones["RightHand" if side=="R" else "LeftHand"]; return ob.matrix_world@(hb.matrix@Vector((0,0.3,0)))
if __name__=="__main__":
    mod=importlib.import_module(sys.argv[1]); prefix=sys.argv[2]; views=sys.argv[3:]
    cam=setup_render(260,6) if views else None
    for name,pose in mod.POSES.items():
        reset_pose(ob); set_pose(ob,pose)
        print(f"{name:12s} clip {clip_report()}  Rhand {tuple(round(c,2) for c in hand_pos('R'))}  Lhand {tuple(round(c,2) for c in hand_pos('L'))}")
        for v in views: render(f"{WORK}/../renders/{prefix}_{name}_{v}.png",cam,v)
