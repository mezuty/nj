import bpy
import pickle, math, sys
from mathutils import Euler
SCR=__import__('os').environ.get('ANIM_WORKDIR', './work')
STEP = int(sys.argv[1]) if len(sys.argv)>1 else 5
dense = pickle.load(open(f"{SCR}/dense9.pkl","rb"))
N=360
frames = list(range(0,N,STEP))+[N]
src = lambda f: dense[f % N]
order = ['TORSO','UpTorso','HEAD','FK_UpperArm.R','FK_LowerArm.R','FK_Hand.R','FK_UpperArm.L','FK_LowerArm.L','FK_Hand.L',
         'FK_UpperLeg.R','FK_LowerLeg.R','FK_Foot.R','FK_UpperLeg.L','FK_LowerLeg.L','FK_Foot.L']
def r(v): return [round(float(x),5)+0.0 for x in v]
lines=[]
for b in order:
    parts=[]
    if b=='TORSO':
        parts.append('"loc": ['+", ".join(str(r(src(f)[b][0])) for f in frames)+']')
        qs=[]; prev=None
        for f in frames:
            q=Euler(src(f)[b][1],'XYZ').to_quaternion()
            if prev is not None and sum(a*c for a,c in zip(q,prev))<0: q=-q
            prev=q; qs.append(r(q))
        parts.append('"quat": '+str(qs))
    else:
        parts.append('"rot": ['+", ".join(str(r(src(f)[b][1])) for f in frames)+']')
    lines.append(f'    "{b}": {{\n        '+",\n        ".join(parts)+'\n    },')
t=open(f"{__import__('os').path.dirname(__import__('os').path.abspath(__file__))}/template9.py").read()
out=t % dict(group_order=order, key_frames=frames, data="\n".join(lines))
open("../animations/WonderWoman_Idle.py","w").write(out)
print("wrote", len(out), "bytes", len(frames), "keys/channel")
