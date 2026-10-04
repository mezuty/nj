import numpy as np, fk
from scipy.optimize import least_squares
from mathutils import Vector
OFF = 1000.0
LIM = {"R": ([-200,-100,-40,-150,-90,-85,-80,-80],[70,100,190,0,90,85,80,80]),
       "L": ([-200,-100,-190,-150,-90,-85,-80,-80],[70,100,40,0,90,85,80,80])}
def seg_dirs(side, chest, up, lo, ha):
    sh,e,w,t,mats = fk.arm_points(side, chest, up, lo, ha)
    W = fk.REST["_obj"].to_3x3()
    return [(W @ m.to_3x3() @ Vector((0,1,0))).normalized() for m in mats], [(W @ m.to_3x3() @ Vector((0,0,1))).normalized() for m in mats]
def to_world(chest, d):
    m = (fk.chest_mat(chest) @ fk.REST["UpTorso"][0].inverted()).to_3x3()
    return (m @ Vector(d)).normalized()
def solve(side, chest, D, frame="chest", prior=None, palm=None, reg=0.0015, w=(1.0,1.0,0.7)):
    """D: (up_dir, lo_dir, hand_dir) segment pointing directions (shoulder->elbow, elbow->wrist, wrist->fingers)."""
    T = [to_world(chest,d) if frame=="chest" else Vector(d).normalized() for d in D]
    P = None if palm is None else (to_world(chest,palm) if frame=="chest" else Vector(palm).normalized())
    p0 = np.array(prior if prior is not None else [0,0,0,-20,0,0,0,0], float)
    lo_b, hi_b = (np.array(LIM[side][0])+OFF, np.array(LIM[side][1])+OFF)
    def unpack(x):
        x=np.asarray(x)-OFF; return list(x[0:3]),[x[3],x[4],0],list(x[5:8])
    def res(x):
        up,lo,ha=unpack(x); Y,Z = seg_dirs(side,chest,up,lo,ha)
        r=[]
        for i in range(3):
            if T[i] is not None: r += list((Y[i]-T[i])*w[i])
        if P is not None: r += list((Z[2]-P)*0.4)
        r += list((np.asarray(x)-OFF-p0)*reg)
        return r
    x0 = np.clip(p0+OFF, lo_b+1e-3, hi_b-1e-3)
    sol = least_squares(res, x0, bounds=(lo_b,hi_b), method="trf", diff_step=1e-6, x_scale=30, max_nfev=5000)
    up,lo,ha = unpack(sol.x); Y,Z = seg_dirs(side,chest,up,lo,ha)
    err=[round(np.degrees(np.arccos(max(-1,min(1,Y[i].dot(T[i]))))),1) for i in range(3)]
    return [round(v,2) for v in up],[round(v,2) for v in lo],[round(v,2) for v in ha],err
