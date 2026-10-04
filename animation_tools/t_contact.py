import sys; sys.path.insert(0,'.')
import importlib, clipkit
from posecheck import ob, pen, reset_pose, set_pose
import ww_rest
D = clipkit.build(ww_rest.CLIPS, "Clash")
for f in (31,32,33,34,35,37):
    reset_pose(ob); set_pose(ob, {b: tuple(D[b][f]) for b in clipkit.BONES})
    wr=ob.matrix_world@ob.pose.bones["RightHand"].head; wl=ob.matrix_world@ob.pose.bones["LeftHand"].head
    print(f, "Y", round(D["FK_UpperArm.R"][f][1],1), "wrist gap(centres)", round((wr-wl).length,3), "forearm overlap", round(max(pen("RightLowerArm","LeftLowerArm"),pen("LeftLowerArm","RightLowerArm")),3), "head", round(max(pen("RightHand","Head"),pen("LeftHand","Head"),pen("RightLowerArm","Head")),3))
