import sys; sys.path.insert(0,'.')
from posecheck import ob, pen, reset_pose, set_pose
for X in (-38,-42,-46):
  for LX in (-95,-102,-108):
    for Y in (-52,-56,-60,-64):
        reset_pose(ob); set_pose(ob,{"UpTorso":(-9,0,0),"FK_UpperArm.R":(X,Y,0),"FK_LowerArm.R":(LX,0,0),"FK_Hand.R":(-12,0,0),"FK_UpperArm.L":(X,-Y,0),"FK_LowerArm.L":(LX,0,0),"FK_Hand.L":(-12,0,0)})
        wr=ob.matrix_world@ob.pose.bones["RightHand"].head; wl=ob.matrix_world@ob.pose.bones["LeftHand"].head
        ov=max(pen("RightLowerArm","LeftLowerArm"),pen("LeftLowerArm","RightLowerArm"),pen("RightHand","LeftHand"))
        hd=max(pen("RightHand","Head"),pen("LeftHand","Head"),pen("RightLowerArm","Head"),pen("LeftLowerArm","Head"))
        print(f"X{X} LX{LX} Y{Y} gap {round((wr-wl).length-1.0,3)} overlap {ov:.3f} head {hd:.3f} wristZ {wr.z:.2f}")
