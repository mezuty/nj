from ivy_lib import *
import math, os
from ivy_body5 import cr, bump, sstep, lerp, N, TAU, w     # N = 360 (6 s @ 60 fps)

# ---------------------------------------------------------------- story (frames on the 360 loop)  -- "Amazon grace"
# right arm: soft hand-on-hip -> floats out into a long line holding the lasso -> flowing twirl -> sweeps back in a wide arc, lands on the hip
def w_las(f):  return sstep((f - 60) / 56.0) * (1.0 - sstep((f - 240) / 52.0))
def e_twirl(f): return sstep((f - 108) / 36.0) * (1.0 - sstep((f - 196) / 44.0))      # amplitude envelope
TW0, TW_P = 100, 40.0                                                                   # 1.5 Hz: slower, more flowing than a 2 Hz twirl
TWP = dict(ux=float(os.environ.get('TW_UX', 0.65)), lx=float(os.environ.get('TW_LX', 0.90)), hx=float(os.environ.get('TW_HX', 0.40)),
           pl=float(os.environ.get('TW_PL', -1.6)), ph=float(os.environ.get('TW_PH', -3.0)), uz=float(os.environ.get('TW_UZ', 0.10)))

H_YAW   = [(0, 0.04), (52, 0.10), (100, -0.20), (170, -0.24), (236, -0.10), (262, 0.10), (296, 0.40), (332, 0.34), (352, 0.08), (360, 0.04)]
H_PITCH = [(0, 0.10), (60, 0.10), (110, 0.02), (200, 0.02), (250, 0.06), (272, 0.22), (300, 0.14), (336, 0.12), (360, 0.10)]
H_TILT  = [(0, 0.09), (70, 0.08), (130, 0.02), (200, 0.00), (250, 0.06), (270, -0.12), (292, 0.14), (330, 0.12), (360, 0.09)]     # hair-toss: tilt flows through at 270

# arm poses in mirrored param space (ux, uy, uz, lx, ly, hx, hz):  U=(ux,-sg*uy,sg*uz)  L=(lx,-sg*ly)  H=(hx,0,sg*hz)
HIP   = (0.10, 0.15, 0.32, -0.95, 0.10, 0.20, 0.0)          # soft hand at the waist, rounded elbow
LASSO = (float(os.environ.get('TW_CU', -0.50)), 0.10, float(os.environ.get('TW_CZ', 0.55)), float(os.environ.get('TW_CL', -1.50)), 0.00, 0.00, 0.10)   # arm floats out, elbow softly bent (rounder circles)

def body_channels(f):
    t = w(f)
    b = math.sin(4 * t)                                   # slow breath (90 f), small
    E = e_twirl(f)
    ph = TAU * (f - TW0) / TW_P
    land = bump(f, 284, 40)                               # the lasso comes home: soft landing + hair toss
    hy, hp, ht = cr(f, H_YAW), cr(f, H_PITCH), cr(f, H_TILT)
    ch = {}
    # pelvis: weight softly on the back (left) leg - hip gently shifted, a long S-curve; narrow, tall, graceful
    ch['TORSO'] = (
        (-0.07 + 0.035 * math.sin(t + 0.4) + 0.014 * E * math.sin(ph - 0.8),
         -0.09 + 0.010 * b + 0.010 * E * math.sin(2 * ph - 0.5) + 0.012 * land,
         0.0 + 0.02 * math.sin(2 * t) - 0.015 * land),
        (-0.02 + 0.010 * b,
         0.12 + 0.03 * math.sin(t) + 0.03 * hy + 0.03 * E * math.sin(ph - 1.2) + 0.04 * land,      # hips turned 3/4
         -0.06 + 0.02 * math.sin(t + 0.5) + 0.018 * E * math.sin(ph + 0.4)))                        # loaded (left) hip lifted
    ch['UpTorso'] = ((0, 0, 0),
        (0.03 + 0.025 * b + 0.04 * land + 0.015 * math.sin(2 * t - 0.8),                            # chest open but relaxed, not puffed
         -0.16 + 0.30 * cr(f - 8, H_YAW) - 0.025 * E * math.sin(ph - 0.6) - 0.05 * land,            # counter-rotates to face the camera
         0.07 - 0.02 * math.sin(t) + 0.14 * cr(f - 8, H_TILT) + 0.02 * E * math.sin(ph + 1.0)))      # counter roll (S-curve)
    ch['HEAD'] = ((0, 0, 0),
        (hp + 0.010 * math.sin(4 * t + 0.6),
         hy + 0.008 * math.sin(2 * t + 1.0),
         ht + 0.008 * math.sin(t)))
    for side, sg in (('L', -1), ('R', 1)):
        if side == 'L':
            ux, uy, uz, lx, ly, hx, hz = HIP
            uz += 0.015 * b + 0.012 * E * math.sin(ph + 0.6)
            ux += 0.025 * math.sin(2 * t - 0.5)
            lx += 0.025 * b; hx += 0.05 * math.sin(3 * t - 0.8)                 # fingers breathe
        else:
            wU, wL, wH = w_las(f), w_las(f - 6), w_las(f - 12)               # longer lags = more flow
            def tw(lag, a, phase): ff = f - lag; return a * e_twirl(ff) * math.sin(TAU * (ff - TW0) / TW_P + phase)
            ux = lerp(HIP[0], LASSO[0], wU) + tw(0, TWP['ux'], 0.0)
            uy = lerp(HIP[1], LASSO[1], wU)
            uz = lerp(HIP[2], LASSO[2], wU) + tw(0, TWP['uz'], 1.57)
            lx = lerp(HIP[3], LASSO[3], wL) + tw(6, TWP['lx'], TWP['pl'])
            ly = lerp(HIP[4], LASSO[4], wL) + tw(6, 0.12, -0.6)
            hx = lerp(HIP[5], LASSO[5], wH) + tw(12, TWP['hx'], TWP['ph'])
            hz = lerp(HIP[6], LASSO[6], wH) + tw(12, 0.10, -1.0)
            hx += -0.30 * bump(f - 12, 290, 34)                                   # wrist opens in a flourish as the hand lands
            uz += 0.015 * b * (1 - wU); lx += 0.025 * b * (1 - wL)
        ch[f'FK_UpperArm.{side}'] = ((0, 0, 0), (ux, -sg * uy, sg * uz))
        ch[f'FK_LowerArm.{side}'] = ((0, 0, 0), (lx, -sg * ly, 0))
        ch[f'FK_Hand.{side}'] = ((0, 0, 0), (hx, 0, sg * hz))
    return ch

# ---- feet: narrow, tall stagger - right foot forward and turned out, left behind carrying the weight
FOOT_OFF = {'L': Vector((-0.04, -0.05, 0)), 'R': Vector((0.06, 0.30, 0))}
FOOT_YAW = {'L': 0.10, 'R': -0.18}
def foot_adjust(f, side):
    return 0.0, 0.0, 0.0
