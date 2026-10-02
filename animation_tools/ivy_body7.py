from ivy_lib import *
import math
from ivy_body5 import cr, bump, sstep, lerp, N, TAU, w     # N = 360 (6 s @ 60 fps)

# ---------------------------------------------------------------- story (frames on the 360 loop)
CL0, CL1, CL2, CL3 = 44, 90, 150, 196     # hands rise & clasp ... release and drop with weight
def e_clasp(f): return sstep((f - CL0) / (CL1 - CL0)) - sstep((f - CL2) / (CL3 - CL2))
def e_exhale(f): return bump(f, 204, 56)  # heavy exhale as the arms fall

YAW   = [(0, 0.00), (140, 0.00), (178, 0.03), (226, -0.40), (262, -0.46), (284, -0.38), (316, 0.38), (338, 0.34), (352, 0.05), (360, 0.00)]
PITCH = [(0, -0.14), (60, -0.15), (96, -0.22), (122, -0.19), (156, -0.14), (200, -0.12), (262, -0.14), (330, -0.15), (360, -0.14)]
TILT  = [(0, 0.0), (80, 0.0), (104, 0.30), (118, 0.34), (126, 0.15), (146, -0.26), (170, -0.18), (192, 0.0), (360, 0.0)]

def body_channels(f):
    t = w(f)
    b = math.sin(4 * t)                       # slow deep breath, 90 f
    cl = e_clasp(f); ex = e_exhale(f)
    hy, hp, ht = cr(f, YAW), cr(f, PITCH), cr(f, TILT)
    press = bump(f, 100, 26) + bump(f, 128, 26)          # two slow presses of the knuckles
    ch = {}
    ch['TORSO'] = (
        (0.05 * math.sin(t + 0.5) - 0.02 * math.sin(2 * t),
         -0.13 + 0.012 * b - 0.035 * ex + 0.012 * math.sin(2 * t + 0.4),
         -0.01 + 0.02 * math.sin(2 * t) - 0.015 * cl),
        (-0.02 + 0.012 * b + 0.02 * ex,
         0.03 * math.sin(t) + 0.05 * hy,
         0.02 * math.sin(t + 0.5)))
    ch['UpTorso'] = ((0, 0, 0),
        (0.06 + 0.035 * b - 0.07 * cl - 0.06 * ex + 0.012 * math.sin(2 * t - 0.8),    # chest broad and lifted; rolls forward as hands clasp
         0.40 * cr(f - 6, YAW) - 0.02 * math.sin(t),
         -0.02 * math.sin(t) + 0.15 * cr(f - 6, TILT)))
    ch['HEAD'] = ((0, 0, 0),
        (hp + 0.012 * math.sin(4 * t + 0.6),                  # chin down, eyes up
         hy + 0.008 * math.sin(2 * t + 1.0),
         ht + 0.008 * math.sin(t)))
    # ---- arms: flared lats, loose fists, heavy sway; clasp in front for the knuckle-crack
    ec = [e_clasp(f - lg) for lg in (0, 5, 10)]
    ed = [e_exhale(f - lg) for lg in (0, 6, 12)]
    sw = math.sin(t + 0.5)
    for side, sg in (('L', -1), ('R', 1)):
        dU = (0.02 + 0.03 * b + 0.025 * sw * sg, -sg * 0.15, sg * (0.20 + 0.03 * b + 0.015 * math.sin(2 * t)))
        dL = (-0.28 + 0.03 * b, 0.0)
        dH = (0.04 * math.sin(4 * t - 0.8), 0.0, sg * (0.05 + 0.03 * math.sin(3 * t)))
        cU, cL, cH = (-0.98, -sg * 0.47, sg * 0.37), (-0.97, -sg * 0.76), (0.57, 0.0, 0.0)
        U = [lerp(dU[i], cU[i], ec[0]) for i in range(3)]
        flare = bump(f, 70, 56) + bump(f, 176, 56)          # elbows arc outward as the hands come in / drop away
        U[2] += sg * 0.34 * flare
        U[0] += -0.10 * flare
        L = [lerp(dL[i], cL[i], ec[1]) for i in range(2)]
        H = [lerp(dH[i], cH[i], ec[2]) for i in range(3)]
        L[0] += -0.07 * press * ec[1]                      # knuckle press: forearms drive in
        H[0] += 0.18 * press * ec[2]
        U[0] += 0.05 * ed[0]; L[0] += 0.08 * ed[1]; H[0] += 0.10 * ed[2]      # arms fall with weight, hands trail
        ch[f'FK_UpperArm.{side}'] = ((0, 0, 0), tuple(U)); ch[f'FK_LowerArm.{side}'] = ((0, 0, 0), (L[0], L[1], 0)); ch[f'FK_Hand.{side}'] = ((0, 0, 0), tuple(H))
    return ch

# ---- feet: wide, planted, toes slightly out
FOOT_OFF = {'L': Vector((-0.28, 0.08, 0)), 'R': Vector((0.28, -0.08, 0))}
FOOT_YAW = {'L': 0.14, 'R': -0.14}
def foot_adjust(f, side):
    return 0.0, 0.0, 0.0
