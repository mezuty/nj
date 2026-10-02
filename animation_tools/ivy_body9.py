from ivy_lib import *
import math
from ivy_body5 import cr, bump, sstep, lerp, N, TAU, w     # N = 360 (6 s @ 60 fps)

# ---------------------------------------------------------------- story (frames on the 360 loop)
# right arm: akimbo (fist on hip)  ->  lasso at her side, twirling  ->  rope snaps taut, hand pulled back to the hip
def w_las(f):  return sstep((f - 56) / 50.0) * (1.0 - sstep((f - 252) / 22.0))        # 0 = hip, 1 = holding the lasso
def e_twirl(f): return sstep((f - 104) / 28.0) * (1.0 - sstep((f - 214) / 32.0))      # twirl amplitude envelope (period 30 f, 2 Hz)
TW0, TW_P = 100, 30.0
import os
TWP = dict(ux=float(os.environ.get('TW_UX', 0.65)), lx=float(os.environ.get('TW_LX', 1.20)), hx=float(os.environ.get('TW_HX', 0.40)),
           pl=float(os.environ.get('TW_PL', -1.6)), ph=float(os.environ.get('TW_PH', -3.0)))

H_YAW   = [(0, 0.00), (50, 0.06), (100, -0.26), (160, -0.30), (214, -0.22), (252, 0.04), (284, 0.02), (306, 0.48), (338, 0.44), (352, 0.06), (360, 0.00)]
H_PITCH = [(0, 0.12), (60, 0.12), (104, 0.00), (214, 0.00), (252, 0.14), (290, 0.16), (306, 0.12), (338, 0.14), (360, 0.12)]
H_TILT  = [(0, 0.04), (80, 0.06), (130, -0.05), (214, -0.04), (252, 0.08), (300, 0.06), (340, 0.10), (360, 0.04)]

# arm poses in mirrored param space (ux, uy, uz, lx, ly, hx, hz):  U=(ux,-sg*uy,sg*uz)  L=(lx,-sg*ly)  H=(hx,0,sg*hz)
AKIMBO = (0.20, 0.25, 0.60, -1.25, 0.20, 0.30, 0.0)
LASSO  = (-0.30, 0.15, 0.50, -0.85, 0.00, 0.10, 0.10)

def body_channels(f):
    t = w(f)
    b = math.sin(4 * t)                                   # slow regal breath (90 f)
    L_, E = w_las(f), e_twirl(f)
    ph = TAU * (f - TW0) / TW_P                           # lasso phase
    tw = E * math.sin(ph)
    snap = bump(f, 262, 20)                               # rope goes taut
    hy, hp, ht = cr(f, H_YAW), cr(f, H_PITCH), cr(f, H_TILT)
    ch = {}
    ch['TORSO'] = (
        (0.04 * math.sin(t + 0.4) + 0.018 * E * math.sin(ph - 0.8),
         -0.12 + 0.012 * b + 0.012 * E * math.sin(2 * ph - 0.5) - 0.025 * snap,
         -0.01 + 0.02 * math.sin(2 * t) - 0.02 * snap),
        (-0.02 + 0.012 * b + 0.03 * snap,
         0.03 * math.sin(t) + 0.04 * hy + 0.035 * E * math.sin(ph - 1.2),
         0.02 * math.sin(t + 0.5) + 0.02 * E * math.sin(ph + 0.4)))
    ch['UpTorso'] = ((0, 0, 0),
        (0.08 + 0.035 * b - 0.05 * snap + 0.02 * math.sin(2 * t - 0.8),                  # chest proud and lifted
         0.35 * cr(f - 6, H_YAW) - 0.03 * E * math.sin(ph - 0.6),
         -0.02 * math.sin(t) + 0.12 * cr(f - 6, H_TILT) + 0.02 * E * math.sin(ph + 1.0)))
    ch['HEAD'] = ((0, 0, 0),
        (hp + 0.012 * math.sin(4 * t + 0.6) - 0.10 * snap,
         hy + 0.008 * math.sin(2 * t + 1.0),
         ht + 0.008 * math.sin(t)))
    for side, sg in (('L', -1), ('R', 1)):
        if side == 'L':                                   # left fist stays on the hip: breathes, elbow bobs with the twirl's reaction
            P = [AKIMBO[i] for i in range(7)]
            ux, uy, uz, lx, ly, hx, hz = P
            uz += 0.02 * b + 0.015 * E * math.sin(ph + 0.6)
            ux += 0.03 * math.sin(2 * t - 0.5)
            lx += 0.03 * b; hx += 0.04 * math.sin(4 * t - 0.8)
        else:
            wU, wL, wH = w_las(f), w_las(f - 5), w_las(f - 10)
            eU, eL, eH = e_twirl(f), e_twirl(f - 5), e_twirl(f - 10)
            def twirl(lag, a, phase, E_=None):
                ff = f - lag
                return a * e_twirl(ff) * math.sin(TAU * (ff - TW0) / TW_P + phase)
            ux = lerp(AKIMBO[0], LASSO[0], wU) + twirl(0, TWP['ux'], 0.0)              # shoulder drives the swing...
            uy = lerp(AKIMBO[1], LASSO[1], wU)
            uz = lerp(AKIMBO[2], LASSO[2], wU) + twirl(0, 0.06, 1.57)
            lx = lerp(AKIMBO[3], LASSO[3], wL) + twirl(5, TWP['lx'], TWP['pl'])             # ...forearm trails it 5 f...
            ly = lerp(AKIMBO[4], LASSO[4], wL) + twirl(5, 0.15, -0.6)
            hx = lerp(AKIMBO[5], LASSO[5], wH) + twirl(10, TWP['hx'], TWP['ph'])            # ...and the wrist whips 10 f behind
            hz = lerp(AKIMBO[6], LASSO[6], wH)
            # the snap: forearm flexes, wrist whips, elbow draws back to the hip
            lx += -0.22 * bump(f - 5, 262, 20); hx += -0.50 * bump(f - 10, 262, 22); ux += 0.10 * bump(f, 262, 20)
            # breathing while holding the hip
            uz += 0.02 * b * (1 - wU); lx += 0.03 * b * (1 - wL)
        ch[f'FK_UpperArm.{side}'] = ((0, 0, 0), (ux, -sg * uy, sg * uz))
        ch[f'FK_LowerArm.{side}'] = ((0, 0, 0), (lx, -sg * ly, 0))
        ch[f'FK_Hand.{side}'] = ((0, 0, 0), (hx, 0, sg * hz))
    return ch

# ---- feet: wide proud stance, right foot a touch forward, toes slightly out
FOOT_OFF = {'L': Vector((-0.24, 0.0, 0)), 'R': Vector((0.24, 0.14, 0))}
FOOT_YAW = {'L': 0.12, 'R': -0.12}
def foot_adjust(f, side):
    return 0.0, 0.0, 0.0
