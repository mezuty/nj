from ivy_lib import *
import math, os
from ivy_body5 import cr, bump, sstep, lerp, N, TAU, w     # N = 360 (6 s @ 60 fps)

# ---------------------------------------------------------------- story (frames on the 360 loop)  -- "Azarath"
#   floating lotus meditation (head bowed, hands low) -> hands lift and swirl dark energy -> she turns to the camera and PUSHES it -> sinks back into stillness
def wf(f): return sstep((f - 64) / 50.0) * (1.0 - sstep((f - 160) / 30.0))       # hands floating up beside her, swirling energy
def wp(f): return sstep((f - 160) / 30.0) * (1.0 - sstep((f - 232) / 36.0))      # the push
def wm(f): return 1.0 - wf(f) - wp(f)                                            # meditation
def rise(f): return 0.32 * (sstep((f - 70) / 60.0) - sstep((f - 250) / 70.0))    # how far she lifts

BYAW    = [(0, -0.30), (60, -0.30), (120, -0.10), (190, 0.00), (240, -0.10), (300, -0.30), (360, -0.30)]       # slowly turns to face the camera
H_PITCH = [(0, -0.28), (60, -0.30), (110, 0.08), (165, 0.10), (196, 0.04), (240, -0.10), (290, -0.28), (360, -0.28)]
H_YAW   = [(0, 0.00), (80, 0.06), (130, -0.06), (196, 0.00), (260, 0.10), (330, 0.00), (360, 0.00)]
H_TILT  = [(0, 0.08), (100, 0.00), (196, 0.00), (300, 0.08), (360, 0.08)]

# arm poses in mirrored param space (ux, uy, uz, lx, ly, hx, hz):  U=(ux,-sg*uy,sg*uz)  L=(lx,-sg*ly)  H=(hx,0,sg*hz)
MED  = (-0.25, 0.15, 0.25, -0.45, 0.00, 0.20, 0.10)       # hands resting low beside her thighs
FLT  = (-0.35, 0.20, 0.65, -1.15, 0.20, 0.55, 0.10)       # hands floated up and out, palms open
PUSH = (-1.30, 0.00, 0.25, -0.12, 0.00, -0.65, 0.00)      # arms thrust forward, palms out
LEG  = tuple(float(x) for x in os.environ.get('RAVEN_LEG', '-1.22,0.20,1.05,2.20,0.0').split(','))                     # lotus: thigh flex, twist, abduct, knee flex, foot

def body_channels(f):
    t = w(f)
    b = math.sin(3 * t)                                    # slow breath (120 f)
    R = rise(f); Rn = R / 0.32
    byaw = cr(f, BYAW)
    hp, hy, ht = cr(f, H_PITCH), cr(f, H_YAW), cr(f, H_TILT)
    push = bump(f, 200, 28)                                # the energy leaves her hands
    ch = {}
    # ---- she hovers: slow bob, rises as she chants, turns to the camera for the push
    ch['TORSO'] = (
        (0.03 * math.sin(t + 0.4),
         -0.14 + R + 0.045 * math.sin(3 * t - 0.4) + 0.015 * math.sin(5 * t + 1.0),
         0.0 - 0.04 * push + 0.02 * math.sin(2 * t)),
        (-0.02 + 0.012 * b - 0.07 * push,
         byaw + 0.02 * math.sin(2 * t),
         0.02 * math.sin(2 * t + 0.6)))
    ch['UpTorso'] = ((0, 0, 0),
        (-0.06 + 0.10 * Rn + 0.022 * b + 0.03 * push,                     # slumped in meditation, chest opens as she chants
         0.18 * cr(f - 8, BYAW) * 0 + 0.015 * math.sin(2 * t - 0.8),
         0.03 * math.sin(2 * t - 0.5)))
    ch['HEAD'] = ((0, 0, 0),
        (hp + 0.012 * math.sin(3 * t + 0.6),
         hy + 0.008 * math.sin(2 * t + 1.0),
         ht + 0.008 * math.sin(t)))
    # ---- arms: meditation -> float + swirl -> push -> back.  upper arm / forearm / wrist lag 0 / 6 / 12 f
    for side, sg in (('R', 1), ('L', -1)):
        ph0 = 0.0 if side == 'R' else math.pi                     # the two hands swirl in opposite phase
        lag = 0 if side == 'R' else 8
        g = lambda d: (f - lag - d) % N
        m0, f0, p0 = wm(g(0)), wf(g(0)), wp(g(0)); m1, f1, p1 = wm(g(6)), wf(g(6)), wp(g(6)); m2, f2, p2 = wm(g(12)), wf(g(12)), wp(g(12))
        mix = lambda i, a, bb, c: MED[i] * a + FLT[i] * bb + PUSH[i] * c
        ux, uy, uz = mix(0, m0, f0, p0), mix(1, m0, f0, p0), mix(2, m0, f0, p0)
        lx, ly = mix(3, m1, f1, p1), mix(4, m1, f1, p1)
        hx, hz = mix(5, m2, f2, p2), mix(6, m2, f2, p2)
        # dark energy swirls in each palm: small circles (period 60 f), forearm 90 deg behind the shoulder, wrist behind that
        fw = (f - lag) % N
        e = f0 * sstep((fw - 80) / 24.0) * (1.0 - sstep((fw - 150) / 20.0))
        sp = TAU * (fw - 90) / 60.0 + ph0
        ux += 0.10 * math.sin(sp) * e; lx += 0.20 * math.sin(sp - 1.6) * e; hx += 0.22 * math.sin(sp - 3.0) * e; hz += 0.14 * math.cos(sp - 2.2) * e
        # the push: thrust, then a recoil
        ux += -0.14 * bump(g(0), 200, 28); lx += 0.10 * bump(g(6), 200, 28); hx += -0.20 * bump(g(12), 202, 30)
        # relaxed: breath lifts the hands a hair
        ux += 0.03 * b * m0; hx += 0.05 * math.sin(2 * t - 0.6) * m2
        ch[f'FK_UpperArm.{side}'] = ((0, 0, 0), (ux, -sg * uy, sg * uz))
        ch[f'FK_LowerArm.{side}'] = ((0, 0, 0), (lx, -sg * ly, 0))
        ch[f'FK_Hand.{side}'] = ((0, 0, 0), (hx, 0, sg * hz))
    # ---- legs: cross-legged lotus; they drift a beat behind the body like they're weightless
    for side, sg in (('R', 1), ('L', -1)):
        lg = 0.9 if side == 'R' else 1.1
        ch[f'FK_UpperLeg.{side}'] = ((0, 0, 0), (LEG[0] + 0.04 * math.sin(3 * t - lg), -sg * LEG[1], sg * (LEG[2] + 0.03 * math.sin(2 * t - lg))))
        ch[f'FK_LowerLeg.{side}'] = ((0, 0, 0), (LEG[3] + 0.06 * math.sin(3 * t - lg - 0.6), 0.0, 0.0))
        ch[f'FK_Foot.{side}'] = ((0, 0, 0), (LEG[4] + 0.06 * math.sin(3 * t - lg - 1.2), 0.0, 0.0))
    return ch
