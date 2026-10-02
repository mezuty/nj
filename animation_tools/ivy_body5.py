from ivy_lib import *
import math
N = 360                      # 6 s @ 60 fps
TAU = 2 * math.pi
def w(f): return TAU * f / N
def sstep(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * x * (x * (x * 6 - 15) + 10)
def lerp(a, b, t): return a + (b - a) * t
def bump(f, c, wd):
    x = (f - (c - wd / 2)) / wd
    return math.sin(math.pi * x) ** 2 if 0 <= x <= 1 else 0.0

def cr(f, pts):
    """periodic Catmull-Rom path through (frame, value) points; pts[0] frame 0, pts[-1] frame N with equal value."""
    f = f % N
    P = pts[:-1]; n = len(P)
    fr = [p[0] for p in P]; va = [p[1] for p in P]
    for i in range(n):
        j = (i + 1) % n
        f0 = fr[i]; f1 = fr[j] + (N if j <= i else 0)
        if f0 <= f <= f1 or (j == 0 and f >= f0):
            def tan(k):
                a, b = (k - 1) % n, (k + 1) % n
                fa = fr[a] - (N if a > k else 0); fb = fr[b] + (N if b < k else 0)
                return (va[b] - va[a]) / (fb - fa)
            h = f1 - f0; s = (f - f0) / h
            v0, v1 = va[i], va[j]; m0, m1 = tan(i), tan(j)
            return ((2*s**3 - 3*s**2 + 1) * v0 + (s**3 - 2*s**2 + s) * h * m0 + (-2*s**3 + 3*s**2) * v1 + (s**3 - s**2) * h * m1)
    return va[0]

# ---------------------------------------------------------------- story
CLAW0, CLAW1, CLAW2, CLAW3 = 58, 96, 126, 150     # right hand rises / inspects / dismissive flick-down
TAP0, TAP1, TAP2, TAP3 = 150, 168, 206, 224       # weight eases back for two paw taps
POU0, POU1, POU2, POU3 = 226, 262, 296, 336       # coil into the pre-pounce crouch, wiggle, release
def e_claw(f): return sstep((f - CLAW0) / (CLAW1 - CLAW0)) - sstep((f - CLAW2) / (CLAW3 - CLAW2))
def e_tap(f): return sstep((f - TAP0) / (TAP1 - TAP0)) - sstep((f - TAP2) / (TAP3 - TAP2))
def e_pou(f): return sstep((f - POU0) / (POU1 - POU0)) - sstep((f - POU2) / (POU3 - POU2))
def e_wig(f): return sstep((f - 250) / 12.0) * (1.0 - sstep((f - 284) / 12.0))

YAW   = [(0, 0.04), (48, 0.10), (68, -0.10), (94, -0.30), (122, -0.28), (140, 0.10), (176, 0.06), (216, 0.00), (262, 0.02), (312, 0.09), (340, 0.05), (360, 0.04)]
PITCH = [(0, 0.22), (48, 0.20), (68, 0.08), (94, -0.06), (122, -0.04), (140, 0.18), (176, 0.16), (216, 0.30), (262, 0.31), (300, 0.25), (340, 0.22), (360, 0.22)]
TILT  = [(0, 0.05), (58, 0.08), (100, 0.17), (124, 0.12), (142, 0.02), (166, 0.20), (206, 0.15), (236, 0.04), (276, 0.02), (322, 0.11), (350, 0.06), (360, 0.05)]

def body_channels(f):
    t = w(f)
    c, tp, pw = e_claw(f), e_tap(f), e_pou(f)
    wig = e_wig(f) * math.sin(TAU * (f - 250) / 22.0)
    r = math.sin(2 * t)
    hy, hp, ht = cr(f, YAW), cr(f, PITCH), cr(f, TILT)
    hy_l = cr(f - 6, YAW)
    tail = bump(f, 312, 28)                  # one crisp "tail flick" of the hips
    ch = {}
    loc = (0.05 * math.sin(2 * t + 0.7) + 0.075 * wig,
           -0.21 + 0.02 * math.sin(4 * t) - 0.05 * pw + 0.012 * math.sin(3 * t),
           -0.02 - 0.05 * r + 0.10 * tp - 0.08 * pw)
    rot = (-0.05 - 0.05 * pw + 0.02 * math.sin(3 * t + 0.3),
           0.12 + 0.05 * math.sin(2 * t) + 0.15 * tail - 0.05 * c,
           0.035 * math.sin(2 * t + 0.4) + 0.03 * wig + 0.05 * tail)
    ch['TORSO'] = (loc, rot)
    ch['UpTorso'] = ((0, 0, 0),
        (-0.13 - 0.10 * pw + 0.026 * math.sin(3 * t - 0.4) + 0.06 * tp - 0.03 * c,
         -0.24 + 0.08 * math.sin(2 * t - 0.4) + 0.30 * hy_l - 0.12 * tail,
         -0.05 + 0.04 * math.sin(2 * t - 0.6) + 0.30 * cr(f - 8, TILT) - 0.02 * wig))
    ch['HEAD'] = ((0, 0, 0),
        (hp + 0.012 * math.sin(6 * t),
         hy + 0.012 * math.sin(4 * t + 1.0),
         ht + 0.012 * math.sin(5 * t)))
    # ---- LEFT arm = lead paw (guard) -> pounce paw.  lags 0/5/10 frames
    ep = [e_pou(f - lg) for lg in (0, 5, 10)]
    rd_U = (-0.45 + 0.03 * math.sin(3 * t - 0.8) + 0.04 * math.sin(2 * t), 0.10, -0.22 - 0.03 * math.sin(2 * t - 0.5))
    rd_L = (-0.90 + 0.04 * math.sin(3 * t - 1.3), 0.0)
    rd_H = (0.15 + 0.06 * math.sin(3 * t - 2.0), 0.0, -0.05 + 0.04 * math.sin(2 * t - 1.0))
    po_U, po_L, po_H = (-0.80, 0.30, -0.12), (-0.70, 0.0), (0.50, 0.0, -0.05)
    UL = [lerp(rd_U[i], po_U[i], ep[0]) for i in range(3)]
    LL = [lerp(rd_L[i], po_L[i], ep[1]) for i in range(2)]
    HL = [lerp(rd_H[i], po_H[i], ep[2]) for i in range(3)]
    HL[0] += 0.10 * wig
    ch['FK_UpperArm.L'] = ((0, 0, 0), tuple(UL)); ch['FK_LowerArm.L'] = ((0, 0, 0), (LL[0], LL[1], 0)); ch['FK_Hand.L'] = ((0, 0, 0), tuple(HL))
    # ---- RIGHT arm: guard -> rises to inspect her claws (turns the hand over, head follows) -> dismissive flick -> pounce paw
    ec = [e_claw(f - lg) for lg in (0, 5, 10)]
    gd_U = (-0.30 + 0.03 * math.sin(3 * t - 1.0) + 0.04 * math.sin(2 * t + 0.8), -0.20, 0.18 + 0.03 * math.sin(2 * t + 0.3))
    gd_L = (-1.00 + 0.04 * math.sin(3 * t - 1.5), -0.10)
    gd_H = (0.20 + 0.06 * math.sin(3 * t - 2.2), 0.0, 0.05 + 0.04 * math.sin(2 * t - 1.2))
    cl_U = (-0.55, -0.35, 0.22)
    roll = lerp(-0.30, 0.28, sstep((f - 84) / 38.0))          # slowly turns the hand over, as if checking the claws
    cl_L = (-1.75, roll)
    cl_H = (0.40 + 0.10 * math.sin(TAU * (f - 90) / 60.0) * ec[2], 0.0, 0.06 * math.sin(TAU * (f - 100) / 48.0) * ec[2])
    UR = [lerp(gd_U[i], cl_U[i], ec[0]) for i in range(3)]
    LR = [lerp(gd_L[i], cl_L[i], ec[1]) for i in range(2)]
    HR = [lerp(gd_H[i], cl_H[i], ec[2]) for i in range(3)]
    # crisp dismissive flick as the hand drops: wrist whips and trails
    HR[0] += -0.45 * bump(f, 136, 26)
    UR[0] += 0.05 * bump(f, 132, 22)
    # pounce paw (right)
    pr_U, pr_L, pr_H = (-0.75, -0.30, 0.10), (-0.80, 0.0), (0.50, 0.0, 0.05)
    UR = [lerp(UR[i], pr_U[i], ep[0]) for i in range(3)]
    LR = [lerp(LR[i], pr_L[i], ep[1]) for i in range(2)]
    HR = [lerp(HR[i], pr_H[i], ep[2]) for i in range(3)]
    HR[0] += 0.10 * wig
    ch['FK_UpperArm.R'] = ((0, 0, 0), tuple(UR)); ch['FK_LowerArm.R'] = ((0, 0, 0), (LR[0], LR[1], 0)); ch['FK_Hand.R'] = ((0, 0, 0), tuple(HR))
    return ch

# ---- feet: in-line "catwalk" stance (front = left).  paw taps lift/slide the front foot; back heel is always slightly up
FOOT_OFF = {'L': Vector((-0.06, 0.32, 0)), 'R': Vector((0.10, -0.24, 0))}
FOOT_YAW = {'L': 0.0, 'R': -0.12}
def foot_adjust(f, side):
    """returns (heel/toe-down angle about toe pivot, extra forward slide, extra lift)."""
    if side == 'L':
        tap = bump(f, 186, 24) * 0 + 0.0
        b1, b2 = bump(f, 177, 20), bump(f, 197, 20)      # two taps
        k = max(b1, b2)
        return 0.55 * k, 0.12 * k, 0.12 * k
    r = math.sin(2 * w(f))
    return 0.10 + 0.07 * (1 + r) / 2 + 0.10 * e_pou(f), 0.0, 0.0
