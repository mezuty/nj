from ivy_lib import *
import math
N = 360                      # 6 s @ 60 fps; one hip-sway cycle = 120 f (2 s), breath = 120 f
TAU = 2 * math.pi
def w(f): return TAU * f / N

def sstep(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * x * (x * (x * 6 - 15) + 10)
def lerp(a, b, t): return a + (b - a) * t

# left-arm story (frames on the 360 loop)
LIFT0, LIFT1 = 92, 172       # arm drifts up to the "offer" pose
BECK0, BECK1 = 166, 292      # two slow come-hither curls (period 60)
LOW0, LOW1 = 288, 352        # arm trails back down

def env_up(f):
    return sstep((f - LIFT0) / (LIFT1 - LIFT0)) - sstep((f - LOW0) / (LOW1 - LOW0))
def env_beck(f):
    return sstep((f - BECK0) / 14.0) * (1.0 - sstep((f - (BECK1 - 14)) / 14.0))

def body_channels(f):
    t = w(f)
    e = env_up(f)
    s3 = math.sin(3 * t)
    ch = {}
    # ---- pelvis: slow hip figure-8 over a weight shift (contrapposto).  x=right, y=up, z=-forward
    loc = (0.22 * s3,
           -0.14 + 0.03 * math.cos(6 * t + 0.3),
           -0.06 * math.sin(6 * t + 0.4))
    rot = (0.04 * math.sin(6 * t + 0.2),
           0.10 * math.cos(3 * t),
           0.115 * s3)                                # loaded hip lifts (hip pop)
    ch['TORSO'] = (loc, rot)
    # ---- chest: counter-rotates and ripples after the hips (body-roll), breathes slowly, arches when the arm offers
    ch['UpTorso'] = ((0, 0, 0),
        (0.045 + 0.04 * math.sin(3 * t + 1.0) + 0.05 * math.sin(6 * t - 1.4) + 0.04 * e,
         -0.10 * math.cos(3 * t - 0.55),
         -0.15 * math.sin(3 * t - 0.55)))
    # ---- head: chin slightly down (looking through the lashes), lazy tilt, slow gaze drift; lags the chest most
    ch['HEAD'] = ((0, 0, 0),
        (-0.07 + 0.03 * math.sin(3 * t - 1.2) - 0.03 * e,
         0.15 * math.sin(t + 0.6) - 0.06 * e,
         0.04 + 0.10 * math.sin(3 * t - 1.1) + 0.05 * e))
    # ---- RIGHT arm: confident hand-at-hip anchor, elbow lags the sway
    ch['FK_UpperArm.R'] = ((0, 0, 0),
        (0.12 + 0.03 * math.sin(3 * t - 1.3), -0.10 + 0.05 * math.sin(3 * t - 1.1), 0.31 + 0.05 * math.sin(3 * t - 1.0)))
    ch['FK_LowerArm.R'] = ((0, 0, 0), (-0.82 + 0.05 * math.sin(3 * t - 1.6), 0.03 * math.sin(3 * t - 1.5), 0))
    ch['FK_Hand.R'] = ((0, 0, 0),
        (-0.10 + 0.08 * math.sin(3 * t - 2.2), 0.06 * math.sin(3 * t - 1.9), 0.06 + 0.08 * math.sin(3 * t - 2.5)))
    # ---- LEFT arm: languid drift -> slow lift -> come-hither curls -> trailing release.  lags: 0 / 5 / 10 frames
    eu, el, eh = env_up(f), env_up(f - 5), env_up(f - 10)
    def curl(lag):                                   # 0..1..0, period 60, 2 pulses in the window
        ff = f - lag
        return env_beck(ff) * (0.5 - 0.5 * math.cos(TAU * (ff - BECK0 - 4) / 60.0))
    lowU = (0.05 + 0.04 * math.sin(3 * t - 0.9), 0.10, -0.20 - 0.04 * math.sin(3 * t - 1.0))
    offU = (-0.52, 0.25, -0.26)
    U = [lerp(lowU[i], offU[i], eu) for i in range(3)]
    U[0] += 0.05 * curl(0)                           # whole arm draws back a hair on each curl
    U[1] += 0.06 * math.sin(3 * t) * eu
    lowL = (-0.50 + 0.05 * math.sin(3 * t - 1.4), 0.0)
    offL = (-1.50, 0.32)
    L = [lerp(lowL[i], offL[i], el) for i in range(2)]
    L[0] += -0.14 * curl(5)                          # forearm leads the pull-in
    L[1] += 0.10 * curl(5)
    lowH = (-0.10 + 0.09 * math.cos(3 * t), 0.0, 0.10 * math.sin(3 * t + 1.0))   # lazy figure-8 in the fingers
    offH = (0.12, 0.0, -0.05)
    H = [lerp(lowH[i], offH[i], eh) for i in range(3)]
    H[0] += 0.85 * curl(11)                          # fingers curl last and trail through
    H[2] += 0.10 * math.sin(TAU * (f - 12) / 60.0) * env_beck(f)
    ch['FK_UpperArm.L'] = ((0, 0, 0), tuple(U))
    ch['FK_LowerArm.L'] = ((0, 0, 0), (L[0], L[1], 0))
    ch['FK_Hand.L'] = ((0, 0, 0), tuple(H))
    return ch

def heel(f, side):
    t = w(f)
    ph = -0.5 if side == 'L' else -0.5 + math.pi
    return 0.17 * ((1 + math.sin(3 * t + ph)) / 2) ** 1.5
