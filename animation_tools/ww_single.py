"""ONE animation per ability (speed 1.0, real-time frames @60fps), built by time-warping the
validated multi-clip curves onto the server's real timeline. Seams are exact pose pins."""
import numpy as np, clipkit, ww_lasso_lash as lash, ww_lasso_truth as truth
from clipkit import PIN, ramp

def sample(D, t):
    """D: {bone: (n+1,3)} dense in anim frames; t: fractional anim frames -> (len(t),3) per bone"""
    out = {}
    for b, a in D.items():
        x = np.arange(len(a)); tt = np.clip(t, 0, len(a)-1)
        out[b] = np.column_stack([np.interp(tt, x, a[:,c]) for c in range(3)])
    return out

def stitch(length, segments):
    """segments: list of (D, real_start, real_end, anim_start, anim_rate)"""
    F = np.arange(length+1, dtype=float); res = {b: np.zeros((length+1,3)) for b in clipkit.BONES}
    for D, r0, r1, a0, rate in segments:
        m = (F >= r0) & (F <= r1) if r1 is not None else (F >= r0)
        s = sample(D, a0 + (F[m]-r0)*rate)
        for b in res: res[b][m] = s[b]
    return res

# ---------------- Q: LassoLash  (castTime 0.28 + crackTime 0.20 -> HIT, recoil 0.32 -> Stop) ----------------
def lasso_lash():
    W = lash.build(lash.WINDUP); C = lash.build(lash.CRACK)
    seam = 0.28*60                                        # 16.8: crack starts when the cast window ends
    D = stitch(53, [(W, 0, seam, 0, 24/seam),             # whole windup (incl. coil hang) fits the cast window
                    (C, seam, None, 0, 1.4)])             # crack at its tuned speed -> HIT at 16.8+17/1.4 = 28.9
    return D, {"COIL": 13, "CRACK": 17, "HIT": 29, "RECOIL_END": 48}

# ---------------- E: LassoOfTruth ----------------
THROW_TIME = 0.35   # server: fixed loop flight time (replaces distance-based 0.2-0.5 s)
CL = dict(truth.CLIPS)
CL["Recover"] = dict(speed=1.0, length=32, pin=("Hurl",40), pin_vel=True, end_rest=True,
   head=dict(chin=lambda f: -2*(1-ramp(f,8,32))),
   tracks={
    "UpTorso":      [(0,PIN),(15,(2,4,0)),(32,(0,0,0))],
    "FK_UpperArm.R":[(0,PIN),(15,(-20,0,0)),(32,(0,0,0))],
    "FK_LowerArm.R":[(0,PIN),(15,(-70,0,0)),(32,(0,0,0))],
    "FK_Hand.R":    [(0,PIN),(17,(-12,0,0)),(32,(0,0,0))],
    "FK_UpperArm.L":[(0,PIN),(14,(-5,0,-8)),(32,(0,0,0))],
    "FK_LowerArm.L":[(0,PIN),(16,(-30,0,0)),(32,(0,0,0))],
    "FK_Hand.L":    [(0,PIN),(18,(6,0,0)),(32,(0,0,0))],
   })
def lasso_of_truth():
    b = lambda n: clipkit.build(CL, n)
    r_spin  = 30/1.1                                     # 27.3  castTime 0.45 s
    r_throw = r_spin + 41/1.3                            # 58.8  = 27.3 + (0.35 flight + 0.18 cinch)*60 ; Hold pinned to Throw f41
    r_hold  = r_throw + 81                               # 139.8 reel 0.45 + compel 0.9
    r_hurl  = r_hold + 40/1.2                            # 173.1 (slam at r_hold + 25 = 164.8)
    D = stitch(205, [(b("Spin"), 0, r_spin, 0, 1.1),
                     (b("Throw"), r_spin, r_throw, 0, 1.3),
                     (b("Hold"), r_throw, r_hold, 0, 1.0),
                     (b("Hurl"), r_hold, r_hurl, 0, 1.2),
                     (b("Recover"), r_hurl, None, 0, 1.0)])
    return D, {"THROW": 27, "RELEASE": 31, "LASSO_LANDS": 48, "CINCHED": 59, "REEL_END": 86,
               "TICK1": 104, "TICK2": 122, "TICK3": 140, "HURL": 140, "SLAM": 165, "SERVER_STOP": 184}
