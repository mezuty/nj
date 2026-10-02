from ivy_lib import *
import math
N = 240
TAU = 2 * math.pi
def w(f): return TAU * f / N

def sstep(x):  # smootherstep 0..1
    x = min(max(x, 0.0), 1.0)
    return x * x * x * (x * (x * 6 - 15) + 10)

# wave arm timeline (frames).  everything is expressed on the 240-frame loop.
RAISE0, RAISE1 = 70, 108       # arm lifts
WAVE0, WAVE1 = 100, 198        # side-to-side waving window (amplitude ramps in/out)
LOWER0, LOWER1 = 198, 238      # arm floats back down

def env_up(f):
    """0 = relaxed, 1 = wave pose (arm raised)."""
    return sstep((f - RAISE0) / (RAISE1 - RAISE0)) - sstep((f - LOWER0) / (LOWER1 - LOWER0))

def env_wave(f):
    return sstep((f - WAVE0) / 16.0) * (1.0 - sstep((f - (WAVE1 - 16)) / 16.0))

def lerp(a, b, t): return a + (b - a) * t

def body_channels(f):
    t = w(f)
    ch = {}
    e = env_up(f)              # raised-arm amount, also drives upper-body "joy"
    sway = math.sin(4 * t)
    # ---- pelvis (TORSO): local x = right, y = up, z = -forward
    loc = (0.17 * sway,
           -0.20 - (0.062 + 0.012 * e) * math.cos(8 * t) + 0.012 * math.cos(16 * t),
           -0.05 * math.sin(8 * t + 0.6))
    rot = (0.03 * math.sin(8 * t + 0.4),
           0.085 * math.cos(4 * t),
           0.075 * sway)
    ch['TORSO'] = (loc, rot)
    # ---- chest: counter-rotates, lags the pelvis, arches when the arm lifts (inhale / joy)
    ch['UpTorso'] = ((0, 0, 0),
        (0.03 * math.sin(2 * t) - 0.035 * math.cos(8 * t - 0.5) + 0.05 * e,
         -0.095 * math.cos(4 * t - 0.25),
         -0.11 * math.sin(4 * t - 0.30)))
    # ---- head: chin dips on landings, cute tilt; leans toward the waving hand
    ch['HEAD'] = ((0, 0, 0),
        (-0.03 + 0.04 * math.cos(8 * t - 0.9) - 0.03 * e,
         0.10 * math.sin(2 * t + 1.0) - 0.05 * e,
         0.09 * math.sin(2 * t + 0.3) + 0.03 * math.sin(4 * t - 1.2) + 0.10 * e))   # +z = lean to character's left
    # ---- RIGHT arm (anchor): soft bend, hand resting forward of the hip, lagging the bounce
    ch['FK_UpperArm.R'] = ((0, 0, 0),
        (0.08 + 0.035 * math.sin(8 * t - 1.0), -0.10 + 0.04 * math.sin(4 * t - 0.6), 0.25 + 0.04 * math.sin(4 * t - 0.8)))
    ch['FK_LowerArm.R'] = ((0, 0, 0), (-0.85 + 0.06 * math.sin(8 * t - 1.5), 0.03 * math.sin(4 * t - 1.4), 0))
    ch['FK_Hand.R'] = ((0, 0, 0),
        (-0.10 + 0.07 * math.sin(8 * t - 2.2), 0.06 * math.sin(4 * t - 1.8), 0.10 * math.sin(8 * t - 2.6) + 0.05))
    # ---- LEFT arm: relaxed swing -> raise -> bubbly wave -> float down.  joints lag 0/4/8 frames
    eu, el, eh = env_up(f), env_up(f - 4), env_up(f - 8)
    def osc(lag, ph=0.0):
        ff = f - lag
        return env_wave(ff) * math.sin(TAU * (ff - WAVE0) / 30.0 + ph)
    lowU = (0.05 + 0.04 * math.sin(8 * t - 0.8) + 0.03 * math.sin(4 * t), 0.10, -0.18 - 0.03 * math.sin(4 * t - 1.0))
    wavU = (-0.30, -0.02, -0.40)
    U = [lerp(lowU[i], wavU[i], eu) for i in range(3)]
    U[1] += 0.30 * osc(0)                                   # forearm sweeps side to side (upper-arm twist)
    U[0] += -0.03 * osc(3, 1.57)                            # tiny forward/back so the hand traces a loop, not a line
    lowL = (-0.5 + 0.05 * math.sin(8 * t - 1.3), 0.0)
    wavL = (-1.85 + 0.05 * math.sin(8 * t - 0.4), 0.0)
    L = [lerp(lowL[i], wavL[i], el) for i in range(2)]
    L[1] += 0.18 * osc(4, -0.3)                             # forearm roll lags the upper arm
    lowH = (-0.10 + 0.08 * math.cos(4 * t), 0.0, 0.10 * math.sin(4 * t + 1.0))   # lazy figure-8 drift
    wavH = (-0.08, 0.0, 0.0)
    H = [lerp(lowH[i], wavH[i], eh) for i in range(3)]
    H[2] += 0.42 * osc(8, -0.2)                             # wrist flick drags behind and whips
    H[0] += 0.12 * osc(10, 1.2)
    ch['FK_UpperArm.L'] = ((0, 0, 0), tuple(U))
    ch['FK_LowerArm.L'] = ((0, 0, 0), (L[0], L[1], 0))
    ch['FK_Hand.L'] = ((0, 0, 0), tuple(H))
    return ch

def heel(f, side):
    t = w(f)
    ph = 0.3 if side == 'L' else 0.3 + math.pi
    return 0.22 * ((1 + math.sin(4 * t + ph)) / 2) ** 1.8
