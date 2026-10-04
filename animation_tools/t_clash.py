import sys; sys.path.insert(0,'.')
from posecheck import ob, pen, reset_pose, set_pose, loc, box
import bpy
from mathutils import Vector
def poke(a, b):
    """how far arm `a` vertices exit through the far side of torso `b` (visible poke-through): max depth beyond torso centre plane"""
    Ma=bpy.data.objects[a].matrix_world; Mb=bpy.data.objects[b].matrix_world; inv=Mb.inverted(); lo,hi=box[b]; w=0
    for v in loc[a]:
        p=inv@(Ma@v)
        if all(lo[i]<p[i]<hi[i] for i in range(3)):
            w=max(w, min(p[0]-lo[0], hi[0]-p[0]))   # depth across the torso width
    return w
for ch in ((-8,0,0),):
  for X,LX in ((-58,-88),(-50,-95),(-65,-80)):
    for Y in range(-30,-61,-5):
        reset_pose(ob)
        set_pose(ob,{"UpTorso":ch,"FK_UpperArm.R":(X,Y,0),"FK_LowerArm.R":(LX,0,0),"FK_UpperArm.L":(X,-Y,0),"FK_LowerArm.L":(LX,0,0)})
        wr=ob.matrix_world@ob.pose.bones["RightHand"].head; wl=ob.matrix_world@ob.pose.bones["LeftHand"].head
        el=ob.matrix_world@ob.pose.bones["RightLowerArm"].head
        fa=max(pen("RightLowerArm","LeftLowerArm"),pen("LeftLowerArm","RightLowerArm"))
        print(f"X{X} LX{LX} Y{Y}: wristR {tuple(round(c,2) for c in wr)} elbowR {tuple(round(c,2) for c in el)} forearm overlap {fa:.2f} torso-width poke {poke('RightUpperArm','UpperTorso'):.2f} head {max(pen('RightLowerArm','Head'),pen('RightHand','Head')):.2f}")
