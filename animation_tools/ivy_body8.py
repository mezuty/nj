from ivy_lib import *
import math
from ivy_body5 import cr, bump, sstep, lerp, N, TAU, w     # N = 360 (6 s @ 60 fps)

# ---------------------------------------------------------------- story (frames on the 360 loop)
def wc(f): return sstep((f - 48) / 56.0) * (1.0 - sstep((f - 164) / 50.0))        # starbolt charge: hands cup in front of her
def wo(f): return sstep((f - 164) / 50.0) * (1.0 - sstep((f - 282) / 58.0))       # joyful open-armed embrace
def wr(f): return 1.0 - wc(f) - wo(f)                                              # relaxed, welcoming

BYAW   = [(0, 0.00), (120, 0.00), (190, 0.16), (240, 0.30), (282, -0.18), (332, -0.04), (360, 0.00)]
H_PITCH = [(0, 0.04), (60, 0.04), (100, -0.16), (160, -0.16), (200, 0.10), (280, 0.14), (330, 0.06), (360, 0.04)]
H_YAW   = [(0, 0.00), (50, 0.14), (100, 0.00), (160, 0.00), (200, -0.10), (250, 0.18), (290, -0.12), (330, 0.10), (360, 0.00)]
H_TILT  = [(0, 0.06), (70, 0.14), (120, 0.08), (170, 0.06), (220, 0.20), (270, 0.12), (320, 0.04), (360, 0.06)]

# arm poses (ux, uy, uz, lx, ly, hx, hz) mirrored per side: U=(ux,-sg*uy,sg*uz) L=(lx,-sg*ly) H=(hx,0,sg*hz)
REL  = (0.00, 0.30, 0.40, -0.45, 0.20, 0.20, 0.10)
CUP  = (-0.85, 0.35, 0.30, -0.95, 0.55, 0.90, 0.0)
OPEN = (-0.15, 0.30, 1.05, -0.50, 0.20, -0.20, 0.15)

def body_channels(f):
    t = w(f)
    c, o, r = wc(f), wo(f), wr(f)
    ch = {}
    by = cr(f, BYAW)
    hp, hy, ht = cr(f, H_PITCH), cr(f, H_YAW), cr(f, H_TILT)
    # ---- hover: ~0.8 stud off the ground, rising a little more as she opens her arms; slow bob + a second, quicker breath
    ch['TORSO'] = (
        (0.06 * math.sin(t) + 0.03 * math.sin(2 * t + 0.6),
         0.80 + 0.12 * c + 0.28 * o + 0.12 * math.sin(3 * t) + 0.03 * math.sin(5 * t + 1.0),
         -0.03 + 0.05 * math.sin(2 * t + 0.8) - 0.03 * c),
        (-0.04 + 0.03 * math.sin(3 * t - 1.0) - 0.03 * c,
         0.13 * math.sin(t - 0.5) + by,
         0.05 * math.sin(2 * t + 0.3)))
    ch['UpTorso'] = ((0, 0, 0),
        (0.04 + 0.03 * math.sin(3 * t - 1.4) + 0.08 * o - 0.06 * c,           # chest opens in the embrace, curls toward the orb
         -0.55 * cr(f - 8, BYAW) - 0.04 * math.sin(t - 0.5),
         -0.04 * math.sin(2 * t + 0.3) - 0.10 * cr(f - 6, H_TILT) * 0.5))
    ch['HEAD'] = ((0, 0, 0),
        (hp + 0.025 * math.sin(3 * t - 1.8),
         hy + 0.02 * math.sin(2 * t + 1.0),
         ht + 0.02 * math.sin(3 * t)))
    # ---- arms: relaxed -> cupped starbolt -> open embrace -> back; upper arm / forearm / wrist lag 0 / 5 / 10 frames
    for side, sg in (('L', -1), ('R', 1)):
        wU = (wr(f), wc(f), wo(f)); wL = (wr(f - 5), wc(f - 5), wo(f - 5)); wH = (wr(f - 10), wc(f - 10), wo(f - 10))
        mix = lambda i, ww: REL[i] * ww[0] + CUP[i] * ww[1] + OPEN[i] * ww[2]
        ux, uy, uz = mix(0, wU), mix(1, wU), mix(2, wU)
        lx, ly = mix(3, wL), mix(4, wL)
        hx, hz = mix(5, wH), mix(6, wH)
        # floaty overlap while relaxed
        ux += 0.06 * math.sin(3 * t - 1.0) * wU[0]; uz += 0.04 * math.sin(3 * t - 1.4) * wU[0]
        lx += 0.08 * math.sin(3 * t - 1.8) * wL[0]
        hx += 0.10 * math.sin(3 * t - 2.4) * wH[0]
        # the starbolt: hands breathe apart/together and circle it
        uy += 0.07 * math.sin(TAU * (f - 104) / 60.0) * wU[1]
        hz += 0.22 * math.sin(TAU * (f - 104) / 60.0 - 0.8) * wH[1]
        hx += 0.10 * math.sin(TAU * (f - 104) / 60.0 - 1.6) * wH[1]
        # open embrace: a ripple runs out through the wrists
        hz += 0.18 * math.sin(TAU * (f - 214) / 48.0 - 1.0) * wH[2]
        lx += 0.05 * math.sin(TAU * (f - 214) / 48.0 - 0.4) * wL[2]
        ch[f'FK_UpperArm.{side}'] = ((0, 0, 0), (ux, -sg * uy, sg * uz))
        ch[f'FK_LowerArm.{side}'] = ((0, 0, 0), (lx, -sg * ly, 0))
        ch[f'FK_Hand.{side}'] = ((0, 0, 0), (hx, 0, sg * hz))
    # ---- legs dangle and trail (overlap: they lag the bob by ~10-20 f); knees tuck a little more as she rises
    lift = o
    ch['FK_UpperLeg.L'] = ((0, 0, 0), (-0.22 + 0.10 * math.sin(3 * t - 1.2) + 0.04 * math.sin(2 * t - 0.5) - 0.06 * lift, 0.0, -0.05))
    ch['FK_LowerLeg.L'] = ((0, 0, 0), (0.45 + 0.14 * math.sin(3 * t - 1.9) + 0.15 * lift, 0.0, 0.0))
    ch['FK_Foot.L'] = ((0, 0, 0), (0.55 + 0.10 * math.sin(3 * t - 2.4), 0.0, 0.0))
    ch['FK_UpperLeg.R'] = ((0, 0, 0), (0.12 + 0.10 * math.sin(3 * t - 1.6) + 0.04 * math.sin(2 * t + 0.4), 0.0, 0.05))
    ch['FK_LowerLeg.R'] = ((0, 0, 0), (0.85 + 0.12 * math.sin(3 * t - 2.3) + 0.10 * lift, 0.0, 0.0))
    ch['FK_Foot.R'] = ((0, 0, 0), (0.60 + 0.10 * math.sin(3 * t - 2.8), 0.0, 0.0))
    return ch
