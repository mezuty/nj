from ivy_lib import *
import math, os
from ivy_body5 import cr, bump, sstep, lerp, N, TAU, w     # N = 360 (6 s @ 60 fps)

# ---------------------------------------------------------------- story (frames on the 360 loop)  -- "Man of Steel"
#   hero stance (fists on hips, chest out) -> sky call (rises on his toes, gaze up) -> crouch -> FLIGHT LAUNCH (fist overhead, lifts off) -> settles -> hero stance
def wo(f):   return sstep((f - 150) / 30.0) * (1.0 - sstep((f - 236) / 44.0))              # arm weight: akimbo -> flight pose
def rise(f): return 0.40 * (sstep((f - 162) / 34.0) - sstep((f - 240) / 46.0))              # height off the ground (studs)
def crouch(f): return bump(f, 150, 38)                                                       # coil before launch
def sky(f):  return bump(f, 96, 72)                                                          # rise on the toes, gaze to the sky
def tg(f):   return sstep((f - 178) / 22.0) * (1.0 - sstep((f - 236) / 24.0))                # feet come together while airborne
def land(f): return bump(f, 284, 30)                                                         # touchdown absorption

H_YAW   = [(0, 0.05), (30, 0.30), (62, -0.05), (100, 0.00), (150, 0.00), (250, 0.00), (290, 0.12), (320, -0.28), (344, -0.20), (360, 0.05)]
H_PITCH = [(0, 0.16), (60, 0.18), (98, 0.44), (130, 0.38), (152, 0.10), (186, 0.34), (232, 0.34), (264, 0.14), (300, 0.16), (360, 0.16)]
H_TILT  = [(0, 0.00), (98, 0.05), (190, 0.00), (320, -0.06), (360, 0.00)]

# arm poses in mirrored param space (ux, uy, uz, lx, ly, hx, hz):  U=(ux,-sg*uy,sg*uz)  L=(lx,-sg*ly)  H=(hx,0,sg*hz)
AKIMBO = (0.20, 0.25, 0.60, -1.25, 0.20, 0.30, 0.0)       # fists on hips, elbows wide
UP     = (-2.85, 0.05, 0.12, -0.08, 0.00, 0.00, 0.0)      # right fist overhead
BACK   = (0.40, 0.20, 0.20, -0.10, 0.00, 0.00, 0.0)       # left arm streams back along the body

def body_channels(f):
    t = w(f)
    b = math.sin(4 * t)                                    # deep, slow breath (90 f)
    O, C, S, G, L = wo(f), crouch(f), sky(f), tg(f), land(f)
    R = rise(f)
    FL = sstep((R - 0.10) / 0.22)                          # smooth 'airborne' envelope (never a hard on/off gate)
    hy, hp, ht = cr(f, H_YAW), cr(f, H_PITCH), cr(f, H_TILT)
    ch = {}
    ch['TORSO'] = (
        (0.03 * math.sin(t + 0.4),
         -0.11 + 0.012 * b + 0.04 * S - 0.15 * C + R - 0.08 * L + 0.02 * math.sin(2 * t + 0.5) + 0.03 * math.sin(TAU * (f - 190) / 90.0) * FL,
         0.0 - 0.05 * C - 0.04 * O),
        (-0.02 + 0.012 * b - 0.20 * C - 0.22 * O + 0.04 * L,                       # coils forward, then leans into the flight line
         0.03 * math.sin(t) + 0.03 * hy,
         0.015 * math.sin(2 * t + 0.4)))
    ch['UpTorso'] = ((0, 0, 0),
        (0.10 + 0.035 * b + 0.07 * S + 0.12 * O - 0.10 * C - 0.08 * L,             # chest broad and lifted - arches in flight
         0.25 * cr(f - 6, H_YAW) - 0.05 * O,
         -0.01 * math.sin(t) + 0.06 * O))
    ch['HEAD'] = ((0, 0, 0),
        (hp + 0.010 * math.sin(4 * t + 0.6),
         hy + 0.008 * math.sin(2 * t + 1.0),
         ht + 0.008 * math.sin(t) + 0.04 * O))
    for side, sg in (('R', 1), ('L', -1)):
        g = lambda d: (f - d) % N
        aO, aO1, aO2 = wo(g(0)), wo(g(5)), wo(g(10))
        tgt = UP if side == 'R' else BACK
        P = [lerp(AKIMBO[i], tgt[i], (aO, aO, aO, aO1, aO1, aO2, aO2)[i]) for i in range(7)]
        ux, uy, uz, lx, ly, hx, hz = P
        # breathing: fists stay on the hips, elbows lift with the chest
        uz += 0.025 * b * (1 - aO) + 0.10 * S * (1 - aO)                           # elbows flare wider as he rises to the sky
        lx += 0.03 * b * (1 - aO1)
        # anticipation: arms pull back and in before the launch
        ux += 0.35 * bump(f, 148, 28) * (1 if side == 'R' else 0.6)
        uz += -0.10 * bump(f, 148, 28)
        # alive in the flight hold: tiny drift, streaming left arm flutters
        ux += (0.03 * math.sin(TAU * (f - 190) / 90.0) if side == 'R' else 0.06 * math.sin(TAU * (f - 190) / 45.0 + 0.8)) * aO * FL
        ch[f'FK_UpperArm.{side}'] = ((0, 0, 0), (ux, -sg * uy, sg * uz))
        ch[f'FK_LowerArm.{side}'] = ((0, 0, 0), (lx, -sg * ly, 0))
        ch[f'FK_Hand.{side}'] = ((0, 0, 0), (hx, 0, sg * hz))
    return ch

# ---- feet: wide heroic stance; they leave the ground, come together and point their toes in flight
FOOT_OFF = {'L': Vector((-0.20, 0.0, 0)), 'R': Vector((0.20, 0.0, 0))}
FOOT_YAW = {'L': 0.0, 'R': 0.0}
def foot_adjust(f, side):
    R = rise(f); G = tg(f); S = sky(f)
    a = 0.40 * sstep(R / 0.35) + 0.16 * S * (1 - sstep(R / 0.10))                  # toes point in flight; heels lift when he rises to the sky
    dx = (0.20 if side == 'L' else -0.20) * G                                       # feet slide together only while airborne
    dz = R - 0.12 * sstep(R / 0.25)                                                 # feet hang a little lower than the pelvis rise: long, straight flying legs
    return a, 0.0, dz, dx
