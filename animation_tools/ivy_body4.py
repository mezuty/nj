from ivy_lib import *
import math
N = 360                      # 6 s @ 60 fps
TAU = 2 * math.pi
def w(f): return TAU * f / N
def sstep(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * x * (x * (x * 6 - 15) + 10)
def lerp(a, b, t): return a + (b - a) * t
def bump(f, c, wd):                       # smooth 0..1..0 pulse centred on c, total width wd (C1)
    x = (f - (c - wd / 2)) / wd
    return math.sin(math.pi * x) ** 2 if 0 <= x <= 1 else 0.0

def hermite(f, keys):
    """C1 cubic-Hermite path through (frame, value, slope) keys; flat outside."""
    if f <= keys[0][0]: return keys[0][1]
    if f >= keys[-1][0]: return keys[-1][1]
    for (f0, v0, m0), (f1, v1, m1) in zip(keys, keys[1:]):
        if f0 <= f <= f1:
            h = f1 - f0; s = (f - f0) / h
            h00 = 2*s**3 - 3*s**2 + 1; h10 = s**3 - 2*s**2 + s; h01 = -2*s**3 + 3*s**2; h11 = s**3 - s**2
            return h00*v0 + h10*h*m0 + h01*v1 + h11*h*m1

# ---- story timeline (frames on the 360 loop)
GIG0, GIG1 = 58, 150            # giggle fit window
R_UP0, R_UP1, R_DN0, R_DN1 = 60, 102, 148, 198      # right hand -> chin
L_UP0, L_UP1, L_DN0, L_DN1 = 52, 84, 146, 190       # left hand clutches chest
def env(f, a, b, c, d): return sstep((f - a) / (b - a)) - sstep((f - c) / (d - c))
def e_gig(f): return sstep((f - (GIG0 + 12)) / 16.0) * (1.0 - sstep((f - (GIG1 - 16)) / 16.0))

# head tilt story: slow creep to a crooked tilt, violent-but-smooth snap to the other side, linger, ease home
TILT = [(160, 0.0, 0.0), (252, 0.50, 0.012), (265, -0.62, 0.0), (292, -0.50, 0.0015), (336, -0.50, 0.0), (360, 0.0, 0.0)]
PITCH = [(160, 0.0, 0.0), (252, -0.20, -0.001), (265, 0.08, 0.0), (300, 0.04, 0.0), (340, 0.04, 0.0), (360, 0.0, 0.0)]
YAW = [(160, 0.0, 0.0), (252, 0.22, 0.003), (265, -0.30, 0.0), (300, -0.24, 0.0), (340, -0.24, 0.0), (360, 0.0, 0.0)]

def body_channels(f):
    t = w(f)
    r = math.sin(3 * t)                      # forward/back rock (120 f)
    g = e_gig(f)
    q = lambda lag=0, ph=0.0: e_gig(f - lag) * math.sin(TAU * (f - lag - GIG0) / 14.0 + ph)   # silent-laugh quiver
    tilt = hermite(f, TILT); pitch = hermite(f, PITCH); yaw = hermite(f, YAW)
    tilt_l = hermite((f - 5) % N, TILT)
    jolt = bump(f, 261, 22)                 # body jolts as the head snaps
    ch = {}
    # ---- pelvis: crouched, rocking over the staggered feet; dips and bobs through the giggle
    loc = (0.04 * math.sin(3 * t + 0.9) + 0.07 * jolt + 0.025 * q(0, 0.5),
           -0.24 - 0.03 * g + 0.025 * math.cos(6 * t) + 0.018 * q(0),
           -0.08 - 0.10 * r - 0.03 * jolt)
    rot = (-0.05 - 0.05 * r - 0.04 * g,
           0.07 * math.sin(3 * t + 0.4) - 0.07 * jolt,
           0.05 * math.sin(3 * t - 0.3) + 0.06 * jolt)
    ch['TORSO'] = (loc, rot)
    # ---- chest: hunched, drapes after the pelvis, quivers with the laugh, whips with the head snap
    ch['UpTorso'] = ((0, 0, 0),
        (-0.20 - 0.07 * r - 0.08 * g + 0.045 * q(0, 0.0) + 0.04 * math.sin(2 * t + 0.5),
         0.09 * math.sin(3 * t - 0.8) + 0.30 * (-yaw) * 0 + 0.14 * hermite((f - 4) % N, YAW) + 0.04 * q(2, 1.0),
         0.07 + 0.32 * tilt_l + 0.035 * q(3, 0.7) + 0.05 * math.sin(3 * t - 0.6)))
    # ---- head: looks up through the hair; laughs; creeps to a crooked tilt; snaps
    ch['HEAD'] = ((0, 0, 0),
        (0.20 + 0.04 * math.sin(3 * t - 1.4) - 0.25 * g + pitch - 0.055 * q(6, 0.0),
         0.06 * math.sin(2 * t + 1.3) + yaw + 0.12 * g * math.sin(TAU * (f - GIG0) / 56.0),
         0.14 + 0.08 * math.sin(3 * t - 1.0) + tilt + 0.20 * g * math.sin(TAU * (f - GIG0) / 28.0 - 0.6)))
    # ---- dangling pendulum arms (left on a 120 f swing, right on a 180 f swing => never lines up with the left)
    rise_L = [env(f - lg, L_UP0, L_UP1, L_DN0, L_DN1) for lg in (0, 5, 10)]
    rise_R = [env(f - lg, R_UP0, R_UP1, R_DN0, R_DN1) for lg in (0, 5, 10)]
    dangU_L = (0.08 + 0.30 * math.sin(3 * t - 0.4), 0.15, -0.14 - 0.07 * math.sin(3 * t + 0.8))
    dangL_L = (-0.28 - 0.26 * (0.5 + 0.5 * math.sin(3 * t - 1.5)), 0.0)
    dangH_L = (0.10 * math.sin(3 * t - 2.3), 0.0, -0.12 * math.sin(3 * t - 1.9))
    clU, clL, clH = (-0.40, 0.70, -0.10), (-1.40, 0.80), (0.10, 0.0, 0.0)
    UL = [lerp(dangU_L[i], clU[i], rise_L[0]) for i in range(3)]
    LL = [lerp(dangL_L[i], clL[i], rise_L[1]) for i in range(2)]
    HL = [lerp(dangH_L[i], clH[i], rise_L[2]) for i in range(3)]
    UL[0] += 0.03 * q(0, 0.2); HL[0] += 0.10 * q(8, 0.8)
    ch['FK_UpperArm.L'] = ((0, 0, 0), tuple(UL)); ch['FK_LowerArm.L'] = ((0, 0, 0), (LL[0], LL[1], 0)); ch['FK_Hand.L'] = ((0, 0, 0), tuple(HL))
    dangU_R = (0.10 + 0.28 * math.sin(2 * t + 1.0), -0.10, 0.20 + 0.08 * math.sin(2 * t + 0.2))
    dangL_R = (-0.25 - 0.22 * (0.5 + 0.5 * math.sin(2 * t - 0.4)), 0.0)
    dangH_R = (0.12 * math.sin(2 * t - 1.0), 0.0, 0.10 * math.sin(2 * t - 1.6))
    chU, chL, chH = (-1.10, -0.80, 0.0), (-2.20, -0.90), (0.30, 0.0, 0.0)
    UR = [lerp(dangU_R[i], chU[i], rise_R[0]) for i in range(3)]
    LR = [lerp(dangL_R[i], chL[i], rise_R[1]) for i in range(2)]
    HR = [lerp(dangH_R[i], chH[i], rise_R[2]) for i in range(3)]
    UR[0] += 0.03 * q(0, 1.6); HR[0] += 0.12 * q(8, 0.2)
    # finger twitches while the head creeps: irregular, smooth flicks of the wrist
    tw = 0.30 * bump(f, 202, 16) + 0.24 * bump(f, 219, 14) - 0.30 * bump(f, 234, 16) + 0.34 * bump(f, 249, 18)
    HR[2] += tw * (1 - rise_R[2]); HR[0] += 0.5 * tw * (1 - rise_R[2])
    # the snap flings the dangling arms through momentum (they lag the jolt)
    UL[0] += 0.14 * bump(f - 6, 265, 30); UR[0] += -0.12 * bump(f - 8, 265, 30)
    ch['FK_UpperArm.R'] = ((0, 0, 0), tuple(UR)); ch['FK_LowerArm.R'] = ((0, 0, 0), (LR[0], LR[1], 0)); ch['FK_Hand.R'] = ((0, 0, 0), tuple(HR))
    return ch

# ---- feet: staggered, pigeon-toed.  heel pops on the back foot when she rocks forward
FOOT_OFF = {'L': Vector((-0.12, 0.30, 0)), 'R': Vector((0.12, -0.14, 0))}
FOOT_YAW = {'L': -0.26, 'R': 0.26}                 # toes turned in
def heel(f, side):
    r = math.sin(3 * w(f))
    return 0.26 * ((1 + r) / 2) ** 1.6 if side == 'R' else 0.0
