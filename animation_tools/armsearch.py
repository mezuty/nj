"""Find a clip-free arm pose (small twist) whose hand reaches a world target. usage: armsearch.py side chest target [Xrange]"""
import sys, itertools; sys.path.insert(0,'.')
import numpy as np
from posecheck import ob, pen, reset_pose, set_pose, PAIRS
import fk
from mathutils import Vector
fk.load_rest(ob)
side=sys.argv[1]; chest=eval(sys.argv[2]); tgt=Vector(eval(sys.argv[3]))
extra=eval(sys.argv[4]) if len(sys.argv)>4 else {}
n=fk.CHAINS[side]; cands=[]
for X in range(-180,61,6):
    for Y in range(-30,31,10):
        for Z in (range(-10,61,6) if side=="L" else range(-60,11,6)):
            for LX in range(-140,1,8):
                sh,e,w,t,mats=fk.arm_points(side,chest,(X,Y,-Z if side=="R" else -Z) if False else (X,Y,(Z if side=="R" else -Z)),(LX,0,0),(0,0,0))
                hp=(w+t)*0.5
                cands.append(((hp-tgt).length+0.002*abs(Y)+0.001*abs(Z),X,Y,(Z if side=="R" else -Z),LX))
cands.sort(); out=[]
for c in cands[:60]:
    reset_pose(ob); p={"UpTorso":chest, n[0]:(c[1],c[2],c[3]), n[1]:(c[4],0,0)}; p.update(extra); set_pose(ob,p)
    arm=[x for x in ("RightUpperArm","RightLowerArm","RightHand","LeftUpperArm","LeftLowerArm","LeftHand") if x.startswith("Right" if side=="R" else "Left")]
    d=max(max(pen(a,b),pen(b,a)) for a,b in PAIRS if a in arm or b in arm)
    out.append((round(c[0]+2*max(0,d-0.03),3),round(c[0],3),round(d,3),c[1:]))
out.sort()
for o in out[:6]: print(o)
