from ivy_lib import *
import math
from ivy_body5 import cr, bump, sstep, lerp, N, TAU, w     # N = 360 (6 s @ 60 fps)

# ---------------------------------------------------------------- story (frames on the 360 loop)
SW_UP0, SW_UP1 = 66, 108        # right arm lifts, cocked, wrist back
SW_HIT0, SW_HIT1 = 120, 138     # the lazy swat (quick, smooth arc outward)
SW_DN0, SW_DN1 = 138, 176       # follow-through, floats home
LF0, LF1, LF2, LF3 = 186, 222, 246, 288    # left arm: graceful reach out and back
def e_cock(f): return sstep((f - SW_UP0) / (SW_UP1 - SW_UP0)) - sstep((f - 124) / 16.0)
def e_hit(f):  return sstep((f - SW_HIT0) / (SW_HIT1 - SW_HIT0)) - sstep((f - SW_DN0) / (SW_DN1 - SW_DN0))
def e_reach(f): return sstep((f - LF0) / (LF1 - LF0)) - sstep((f - LF2) / (LF3 - LF2))
def wt(f):      # weight state: 0 = on the back leg (front toe pointed) -> 1 = rolled onto the front leg
    return sstep((f - 166) / 36.0) - sstep((f - 290) / 40.0)

YAW   = [(0, 0.05), (46, -0.05), (84, -0.34), (122, -0.30), (150, -0.02), (176, 0.08), (214, 0.16), (252, 0.52), (296, 0.46), (326, 0.12), (360, 0.05)]
PITCH = [(0, 0.14), (60, 0.16), (100, 0.22), (130, 0.20), (160, 0.14), (214, 0.12), (252, 0.02), (296, 0.04), (330, 0.12), (360, 0.14)]
TILT  = [(0, 0.06), (70, 0.04), (106, -0.07), (140, 0.04), (180, 0.10), (230, 0.12), (262, 0.17), (300, 0.12), (336, 0.07), (360, 0.06)]
CHEST_YAW = [(0, 0.0), (66, 0.0), (108, -0.24), (118, -0.24), (134, 0.30), (160, 0.10), (196, 0.0), (252, 0.10), (300, 0.04), (330, 0.0), (360, 0.0)]

def body_channels(f):
    t = w(f)
    p = wt(f)
    pop = bump(f, 204, 26)                      # hip "arrives" with a little pop
    s2, s3 = math.sin(2 * t), math.sin(3 * t)
    hy, hp, ht = cr(f, YAW), cr(f, PITCH), cr(f, TILT)
    cy = cr(f - 4, CHEST_YAW)
    ch = {}
    ch['TORSO'] = (
        (0.12 - 0.20 * p + 0.04 * s2 + 0.03 * pop,
         -0.13 + 0.012 * s3 - 0.025 * bump(f, 186, 40),
         0.05 - 0.19 * p + 0.012 * math.sin(2 * t + 1.0)),
        (-0.02 + 0.015 * s3,
         0.14 - 0.28 * p + 0.05 * s2 - 0.10 * cy,
         0.115 * (1 - 2 * p) + 0.02 * s2 + 0.04 * pop))
    ch['UpTorso'] = ((0, 0, 0),
        (0.07 + 0.025 * math.sin(3 * t - 0.5) + 0.03 * math.sin(2 * t - 1.5) + 0.03 * e_reach(f),         # shoulders back, ribcage lifted
         -0.16 * (1 - 2 * p) * 0.5 + 0.05 * math.sin(2 * t - 0.5) + 0.55 * cy + 0.20 * hy,
         -0.15 * (1 - 2 * p) - 0.03 * s2 + 0.20 * cr(f - 8, TILT)))
    ch['HEAD'] = ((0, 0, 0),
        (hp + 0.012 * math.sin(3 * t + 0.8),
         hy + 0.012 * math.sin(2 * t + 1.0),
         ht + 0.012 * math.sin(3 * t)))
    # ---- LEFT arm: long relaxed line, fingers trailing; lifts into an elegant reach as the weight rolls over
    er = [e_reach(f - lg) for lg in (0, 5, 10)]
    rl_U = (0.04 + 0.10 * math.sin(2 * t - 0.8), 0.10, -0.20 - 0.05 * math.sin(2 * t - 0.2))
    rl_L = (-0.30 - 0.10 * (0.5 + 0.5 * math.sin(2 * t - 1.4)), 0.0)
    rl_H = (0.10 * math.sin(2 * t - 2.0), 0.0, -0.10 + 0.10 * math.sin(2 * t - 1.3))
    re_U, re_L, re_H = (-0.55 + 0.04 * math.sin(3 * t - 0.5), 0.20, -0.36), (-0.60 + 0.04 * math.sin(3 * t - 1.0), 0.20), (0.18, 0.0, 0.12 + 0.10 * math.sin(2 * t))
    UL = [lerp(rl_U[i], re_U[i], er[0]) for i in range(3)]
    LL = [lerp(rl_L[i], re_L[i], er[1]) for i in range(2)]
    HL = [lerp(rl_H[i], re_H[i], er[2]) for i in range(3)]
    ch['FK_UpperArm.L'] = ((0, 0, 0), tuple(UL)); ch['FK_LowerArm.L'] = ((0, 0, 0), (LL[0], LL[1], 0)); ch['FK_Hand.L'] = ((0, 0, 0), tuple(HL))
    # ---- RIGHT arm: relaxed -> slow lift, wrist cocked -> lazy cat-swat (wrist whips, trails) -> floats home
    ek = [e_cock(f - lg) for lg in (0, 5, 10)]
    eh = [e_hit(f - lg) for lg in (0, 3, 7)]
    rr_U = (0.04 + 0.10 * math.sin(2 * t + 0.4), -0.10, 0.20 + 0.05 * math.sin(2 * t + 0.1))
    rr_L = (-0.35 - 0.10 * (0.5 + 0.5 * math.sin(2 * t - 0.6)), 0.0)
    rr_H = (0.10 + 0.06 * math.sin(2 * t - 1.2), 0.0, 0.05 + 0.08 * math.sin(2 * t - 0.9))
    ck_U, ck_L, ck_H = (-0.55, -0.20, 0.25), (-1.25, -0.20), (0.35, 0.0, 0.10)
    sw_U, sw_L, sw_H = (-0.25, -0.10, 0.75), (-0.40, 0.30), (-0.20, 0.0, -0.40)
    UR = [lerp(rr_U[i], ck_U[i], ek[0]) for i in range(3)]
    LR = [lerp(rr_L[i], ck_L[i], ek[1]) for i in range(2)]
    HR = [lerp(rr_H[i], ck_H[i], ek[2]) for i in range(3)]
    # alive in the cock: slow wrist roll and drift (never frozen)
    HR[2] += 0.10 * math.sin(TAU * (f - 90) / 60.0) * ek[2]
    UR = [lerp(UR[i], sw_U[i], eh[0]) for i in range(3)]
    LR = [lerp(LR[i], sw_L[i], eh[1]) for i in range(2)]
    HR = [lerp(HR[i], sw_H[i], eh[2]) for i in range(3)]
    HR[2] += -0.18 * bump(f - 6, 140, 26)                       # wrist whips past, then trails back
    ch['FK_UpperArm.R'] = ((0, 0, 0), tuple(UR)); ch['FK_LowerArm.R'] = ((0, 0, 0), (LR[0], LR[1], 0)); ch['FK_Hand.R'] = ((0, 0, 0), tuple(HR))
    return ch

# ---- feet: model stance.  front foot (left) pointed on its toe while she is weighted back; rolls flat as weight comes forward
FOOT_OFF = {'L': Vector((-0.06, 0.50, 0)), 'R': Vector((0.08, -0.14, 0))}
FOOT_YAW = {'L': 0.10, 'R': -0.12}
def foot_adjust(f, side):
    p = wt(f)
    if side == 'L':
        return 0.50 * (1 - p), 0.0, 0.0
    return 0.26 * p, 0.0, 0.0
