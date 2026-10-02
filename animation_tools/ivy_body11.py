from ivy_lib import *
import math, os
from ivy_body5 import cr, bump, sstep, lerp, N, TAU, w     # N = 360 (6 s @ 60 fps) - one slow "tide"

# ---------------------------------------------------------------- story (frames on the 360 loop)  -- "Tide"
#   sides, palms open  ->  arms rise and she SUMMONS the water  ->  conducts the current (sweeps)  ->  the wave CRASHES  ->  ebb
def wf(f): return sstep((f - 70) / 60.0) * (1.0 - sstep((f - 246) / 30.0))        # arms forward / commanding
def wc(f): return sstep((f - 246) / 30.0) * (1.0 - sstep((f - 300) / 50.0))        # the crash (arms sweep down and out)
def wr(f): return 1.0 - wf(f) - wc(f)                                              # resting at her sides
SWEEP = [(0, 0.0), (130, 0.0), (168, -0.9), (206, 0.9), (240, -0.5), (272, 0.0), (360, 0.0)]      # current direction: -1 = her left, +1 = her right
def sweep(f): return cr(f, SWEEP)

H_YAW   = [(0, 0.04), (60, 0.00), (110, 0.10), (168, -0.20), (206, 0.30), (244, -0.05), (270, 0.00), (310, 0.10), (340, 0.06), (360, 0.04)]
H_PITCH = [(0, 0.10), (60, 0.12), (120, 0.18), (200, 0.18), (250, 0.14), (272, -0.10), (300, 0.02), (330, 0.10), (360, 0.10)]
H_TILT  = [(0, 0.05), (90, 0.10), (168, 0.14), (206, -0.14), (250, 0.00), (280, 0.10), (330, 0.06), (360, 0.05)]

# arm poses in mirrored param space (ux, uy, uz, lx, ly, hx, hz):  U=(ux,-sg*uy,sg*uz)  L=(lx,-sg*ly)  H=(hx,0,sg*hz)
REST  = (0.00, 0.20, 0.30, -0.35, 0.10, 0.10, 0.15)       # arms soft at her sides, palms a little open
FWD   = (-1.00, 0.10, 0.35, -0.60, 0.00, 0.40, 0.00)      # arms forward at chest height, hands commanding the water
CRASH = (0.10, 0.10, 0.85, -0.15, 0.00, -0.45, 0.20)      # arms sweep down and wide as the wave breaks

def body_channels(f):
    t = w(f)
    F, C = wf(f), wc(f)
    b = math.sin(3 * t)                                    # tidal breath (120 f)
    s, sl = sweep(f), sweep(f - 8)
    hy, hp, ht = cr(f, H_YAW), cr(f, H_PITCH), cr(f, H_TILT)
    ripple = lambda lag: math.sin(2 * t - lag)             # slow swell travelling up the spine (180 f)
    ch = {}
    # ---- body = the tide: rises as she summons, leans with the current, dips and exhales on the crash; spine ripples hips -> chest -> head
    ch['TORSO'] = (
        (-0.10 * s + 0.03 * math.sin(t + 0.4),
         -0.17 + 0.05 * F - 0.11 * C + 0.012 * b + 0.010 * math.sin(2 * t),
         0.0 - 0.04 * C + 0.02 * math.sin(2 * t - 0.5)),
        (-0.02 + 0.012 * b - 0.03 * C,
         0.14 * sl + 0.04 * math.sin(t),
         -0.07 * s + 0.035 * ripple(0.0)))
    ch['UpTorso'] = ((0, 0, 0),
        (0.04 + 0.07 * F + 0.025 * b - 0.12 * C,                                                   # chest lifts as she summons, folds on the crash
         0.20 * cr(f - 8, SWEEP) + 0.30 * cr(f - 6, H_YAW) * 0.4,
         0.10 * cr(f - 8, SWEEP) * -1 + 0.04 * ripple(0.7) + 0.05 * cr(f - 8, H_TILT)))          # counter-roll: S-curve against the hips
    ch['HEAD'] = ((0, 0, 0),
        (hp + 0.012 * math.sin(3 * t + 0.6),
         hy + 0.30 * sl * 0 + 0.010 * math.sin(2 * t + 1.0),
         ht + 0.035 * ripple(1.4)))
    for side, sg in (('R', 1), ('L', -1)):
        lag = 0 if side == 'R' else 10                     # the right hand leads, the left follows the current
        g = lambda d: (f - lag - d) % N                    # lagged, wrapped time: the loop closes seamlessly
        wR, wF, wC = wr(g(0)), wf(g(0)), wc(g(0))
        wR1, wF1, wC1 = wr(g(6)), wf(g(6)), wc(g(6))           # forearm 6 f behind
        wR2, wF2, wC2 = wr(g(12)), wf(g(12)), wc(g(12))        # wrist 12 f behind: the arm ripples like water
        mix = lambda i, a, bb, c: REST[i] * a + FWD[i] * bb + CRASH[i] * c
        ux, uy, uz = mix(0, wR, wF, wC), mix(1, wR, wF, wC), mix(2, wR, wF, wC)
        lx, ly = mix(3, wR1, wF1, wC1), mix(4, wR1, wF1, wC1)
        hx, hz = mix(5, wR2, wF2, wC2), mix(6, wR2, wF2, wC2)
        sc = sweep(f - lag)
        # current: right arm abducts as the sweep goes to her right, the left arm crosses in front of her (and vice-versa)
        uz = mix(2, wR, wF, wC) + (0.45 * sc if side == 'R' else -0.45 * sc) * wF
        # travelling wave along the arm while she conducts: shoulder (0) -> elbow (-0.9 rad) -> wrist (-1.8 rad)
        ph = TAU * (f - 150) / 90.0
        fw = (f - lag) % N
        envw = wF * sstep((fw - 120) / 30.0) * (1.0 - sstep((fw - 236) / 24.0))
        ux += 0.07 * math.sin(ph - lag * 0.07) * envw
        lx += 0.20 * math.sin(ph - 0.9 - lag * 0.07) * envw
        hx += 0.26 * math.sin(ph - 1.8 - lag * 0.07) * envw
        hz += 0.30 * sc * wF + 0.10 * math.sin(ph - 2.4) * envw                               # wrist rolls with the current
        # relaxed arms drift with the tide; the crash ends in an open-handed flick
        ux += 0.04 * math.sin(2 * t - 0.5 - lag * 0.05) * wR; lx += 0.04 * b * wR1
        hx += -0.30 * bump(g(12), 296, 36)
        ch[f'FK_UpperArm.{side}'] = ((0, 0, 0), (ux, -sg * uy, sg * uz))
        ch[f'FK_LowerArm.{side}'] = ((0, 0, 0), (lx, -sg * ly, 0))
        ch[f'FK_Hand.{side}'] = ((0, 0, 0), (hx, 0, sg * hz))
    return ch

# ---- feet: confident, grounded stagger (right forward), weight shifts with the current
FOOT_OFF = {'L': Vector((-0.06, -0.05, 0)), 'R': Vector((0.08, 0.26, 0))}
FOOT_YAW = {'L': 0.10, 'R': -0.14}
def foot_adjust(f, side):
    return 0.0, 0.0, 0.0
