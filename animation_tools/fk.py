"""Analytic FK for the MrXen0 rig (chest + arms + head), matches Blender pose evaluation."""
import math, json, os
import numpy as np
from mathutils import Matrix, Euler, Vector, Quaternion
D2R = math.pi/180
CHAINS = {
 "R": ["FK_UpperArm.R","FK_LowerArm.R","FK_Hand.R"],
 "L": ["FK_UpperArm.L","FK_LowerArm.L","FK_Hand.L"],
}
REST = {}
def load_rest(ob):
    for n in ["ROOT","TORSO","UpTorso","FK_UpperArm.R","FK_LowerArm.R","FK_Hand.R","FK_UpperArm.L","FK_LowerArm.L","FK_Hand.L","HEAD","MCH_Head","MCH_INT_Head"]:
        b = ob.data.bones[n]
        REST[n] = (b.matrix_local.copy(), b.parent.name if b.parent else None, b.length)
    REST["_obj"] = ob.matrix_world.copy()
def basis(rot):
    return Euler([v*D2R for v in rot],'XYZ').to_matrix().to_4x4()
def chest_mat(chest):
    # ROOT, TORSO at rest pose (upper-body only: TORSO never keyed)
    mt = REST["TORSO"][0]
    mu = mt @ (mt.inverted() @ REST["UpTorso"][0]) @ basis(chest)
    return mu
def arm_points(side, chest, up, lo, hand):
    names = CHAINS[side]
    m = chest_mat(chest)
    par = REST["UpTorso"][0]
    out = []
    for n, r in zip(names, (up, lo, hand)):
        ml = REST[n][0]
        m = m @ (par.inverted() @ ml) @ basis(r)
        par = ml
        out.append(m)
    W = REST["_obj"]
    sh = W @ out[0].translation; el = W @ out[1].translation; wr = W @ out[2].translation
    tip = W @ (out[2] @ Vector((0, REST[names[2]][2], 0, 1))).to_3d() if False else W @ (out[2] @ Vector((0, 0.55, 0)))
    palm = (W.to_3x3() @ out[2].to_3x3() @ Vector((0,0,1)))  # hand local Z
    return sh, el, wr, tip, out
