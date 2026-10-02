from ivy_lib import *
import math
N = 300                      # 5 s @ 60 fps.  beat = 30 f (bounce), sway = 60 f
TAU = 2 * math.pi
def w(f): return TAU * f / N
def sstep(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * x * (x * (x * 6 - 15) + 10)
def lerp(a, b, t): return a + (b - a) * t

# right-arm "ta-da" flourish timeline
ANT0, ANT1 = 52, 92          # anticipation: arm winds back/down
UP0, UP1 = 92, 132           # sweep up and out
DN0, DN1 = 210, 262          # comes down along a different (front) arc
WIG0, WIG1 = 128, 214        # jazz-hand wiggle window
SHIM0, SHIM1 = 132, 214      # shoulder shimmy window

def e_ant(f): return sstep((f - ANT0) / (ANT1 - ANT0)) - sstep((f - UP0) / 14.0)   # wind-back bump
def e_up(f):  return sstep((f - UP0) / (UP1 - UP0)) - sstep((f - DN0) / (DN1 - DN0))
def e_front(f): return sstep((f - DN0 + 8) / 22.0) * (1 - sstep((f - DN1 + 10) / 26.0))   # descent loops via the front
def e_wig(f): return sstep((f - WIG0) / 20.0) * (1.0 - sstep((f - (WIG1 - 20)) / 20.0))
def e_shim(f): return sstep((f - SHIM0) / 14.0) * (1.0 - sstep((f - (SHIM1 - 14)) / 14.0))

def up(f):                    # springy beat: 0 = dropped on the beat, 1 = apex on toes
    return 0.5 - 0.5 * math.cos(10 * w(f))

def body_channels(f):
    t = w(f)
    ej = e_up(f)              # "joy" amount
    s5 = math.sin(5 * t)
    ch = {}
    loc = (0.16 * (s5 + 0.28 * math.sin(10 * t + 0.8)),
           -0.20 + (0.075 + 0.02 * ej) * up(f),
           -0.045 * math.sin(10 * t + 0.5) - 0.03 * ej)
    rot = (-0.03 + 0.035 * math.sin(10 * t + 0.3),
           0.09 * math.cos(5 * t) + 0.03 * math.sin(10 * t),
           0.085 * s5)
    ch['TORSO'] = (loc, rot)
    shim = e_shim(f) * math.sin(TAU * (f - SHIM0) / 24.0)
    shim2 = e_shim(f) * math.sin(TAU * (f - SHIM0 - 3) / 24.0 + 1.2)
    ch['UpTorso'] = ((0, 0, 0),
        (0.03 * math.sin(2 * t) - 0.04 * math.cos(10 * t - 0.5) + 0.05 * e_ant(f) - 0.06 * ej,
         -0.095 * math.cos(5 * t - 0.3) + 0.10 * shim,
         -0.105 * math.sin(5 * t - 0.35) + 0.07 * shim2))
    ch['HEAD'] = ((0, 0, 0),
        (-0.04 + 0.05 * math.cos(10 * t - 0.9) - 0.04 * ej,
         0.18 * math.sin(2 * t + 1.0) + 0.05 * math.sin(10 * t) - 0.04 * shim,
         0.12 * math.sin(5 * t - 0.5) + 0.05 * math.sin(10 * t + 1.0) + 0.06 * ej))
    # ---- LEFT arm: hand-on-hip anchor with a bouncing elbow
    ch['FK_UpperArm.L'] = ((0, 0, 0),
        (0.12 + 0.045 * math.sin(10 * t - 1.0), 0.10 + 0.05 * math.sin(5 * t - 0.6), -(0.31 + 0.05 * math.sin(5 * t - 0.8) + 0.03 * math.sin(10 * t - 1.2))))
    ch['FK_LowerArm.L'] = ((0, 0, 0), (-0.82 + 0.06 * math.sin(10 * t - 1.5), -0.03 * math.sin(5 * t - 1.4), 0))
    ch['FK_Hand.L'] = ((0, 0, 0),
        (-0.10 + 0.08 * math.sin(10 * t - 2.2), -0.06 * math.sin(5 * t - 1.8), -(0.06 + 0.08 * math.sin(10 * t - 2.6))))
    # ---- RIGHT arm: loose swing -> wind-back -> sweep up -> ta-da + jazz hands -> loops down the front.  lags 0/4/8
    def blend(lag):
        ff = f - lag
        return e_up(ff), e_ant(ff), e_front(ff)
    (u0, a0, fr0), (u1, a1, fr1), (u2, a2, fr2) = blend(0), blend(4), blend(8)
    def wig(lag, ph=0.0):
        ff = f - lag
        return e_wig(ff) * math.sin(TAU * (ff - WIG0) / 24.0 + ph)
    lowU = (0.08 + 0.05 * math.sin(10 * t - 1.0), -0.10 + 0.05 * math.sin(5 * t - 0.6), 0.22 + 0.05 * math.sin(5 * t - 0.8))
    apexU = (-0.22, 0.45, 0.95)
    U = [lerp(lowU[i], apexU[i], u0) for i in range(3)]
    U[0] += 0.42 * a0 - 0.40 * fr0                   # wind back, later descend through the front
    U[2] += -0.10 * a0 + 0.12 * fr0
    U[1] += 0.10 * wig(0, 0.0)
    lowL = (-0.50 + 0.06 * math.sin(10 * t - 1.3), 0.0)
    apexL = (-0.55 + 0.05 * math.sin(10 * t - 0.4), 0.0)
    L = [lerp(lowL[i], apexL[i], u1) for i in range(2)]
    L[0] += 0.18 * a1 - 0.25 * fr1
    L[1] += 0.45 * u1 + 0.25 * wig(4, -0.6)          # forearm turns palm up and rolls
    lowH = (-0.10 + 0.09 * math.cos(5 * t), 0.0, 0.12 * math.sin(5 * t + 1.0))
    apexH = (0.20, 0.0, 0.05)
    H = [lerp(lowH[i], apexH[i], u2) for i in range(3)]
    H[2] += 0.42 * wig(8, -1.2)                      # jazz-hand wiggle trails the forearm
    H[0] += 0.20 * wig(10, 0.4) - 0.25 * a2
    ch['FK_UpperArm.R'] = ((0, 0, 0), tuple(U))
    ch['FK_LowerArm.R'] = ((0, 0, 0), (L[0], L[1], 0))
    ch['FK_Hand.R'] = ((0, 0, 0), tuple(H))
    return ch

def heel(f, side):
    """Both heels spring up with the bounce; the unloaded side lifts a touch more."""
    t = w(f)
    base = 0.26 * up(f) ** 1.4
    sway = math.sin(5 * t + (0.0 if side == 'L' else math.pi))      # >0 : this foot unloaded
    return base + 0.10 * ((1 + sway) / 2) ** 1.6
