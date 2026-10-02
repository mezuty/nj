"""
DEMO ACTION: straight right punch (cross) - one-shot, NOT a loop.
Shows the action workflow: timing from a spec -> kinetic chain (hips -> chest -> shoulder -> elbow -> wrist) ->
fist IK onto a target in world space -> planted feet with ball-of-foot pivot -> start/end on the same ready pose.
Used by run_action_demo.py (needs Blender / bpy).
"""
from ivy_lib import *
from ivy_body4 import hermite          # C1 cubic-Hermite path through (frame, value, slope) keys
from ivy_body5 import bump, sstep, lerp
import math

# ------------------------------------------------------------------ timing spec (game data -> frames)
FPS = 60
T_WINDUP, T_STRIKE, T_FOLLOW, T_RECOVER = 0.20, 0.067, 0.15, 0.50          # seconds
F_WIND = round(FPS * T_WINDUP)                       # 12  -> end of anticipation
F_HIT = F_WIND + round(FPS * T_STRIKE)               # 16  -> impact / damage frame
F_FOLLOW = F_HIT + round(FPS * T_FOLLOW)             # 25  -> end of follow-through
N_ACTION = F_FOLLOW + round(FPS * T_RECOVER) + 1     # 56 frames: 0..55, last frame == ready pose
MARKERS = {"HIT": F_HIT, "WINDUP_END": F_WIND}

# ------------------------------------------------------------------ world target (armature space): victim's chest
import os
TARGET = Vector((0.45, float(os.environ.get('PUNCH_TY', 2.15)), 3.35))                   # where the FIST SURFACE should land at F_HIT
FIST_LEN = 0.68                                        # wrist -> front face of the hand mesh (measured on the rig: hand plate is 1 stud deep)

# ------------------------------------------------------------------ keys (frame, value, slope).  Hips lead, chest +1-2 f, arm +3 f
Z = lambda *k: list(k)
YAW_HIP   = Z((0, -0.22, 0), (10, -0.42, 0), (14, 0.14, 0.05), (18, 0.19, 0.0), (32, -0.10, -0.012), (50, -0.22, 0), (55, -0.22, 0))
YAW_CHEST = Z((0, 0.0, 0), (11, -0.30, 0), (15, 0.36, 0.05), (19, 0.40, 0.0), (34, 0.05, -0.012), (52, 0.0, 0), (55, 0.0, 0))
PELV_Z    = Z((0, 0.0, 0), (10, 0.08, 0), (15, -0.30, -0.04), (19, -0.32, 0.0), (36, -0.08, 0.012), (52, 0.0, 0), (55, 0.0, 0))
HEEL_R    = Z((0, 0.0, 0), (10, 0.10, 0), (15, 0.50, 0.03), (22, 0.45, 0.0), (36, 0.15, -0.02), (52, 0.0, 0), (55, 0.0, 0))
PIVOT_YAW = Z((0, 0.0, 0), (10, -0.10, 0), (15, 0.45, 0.03), (22, 0.45, 0.0), (36, 0.15, -0.01), (52, 0.0, 0), (55, 0.0, 0))
# fist progress along guard -> target  (negative = wind-back).  fast, still moving at impact, tiny overshoot, quick retract
FIST_E    = Z((0, 0.0, 0), (12, -0.12, 0.0), (16, 1.0, 0.20), (17, 1.006, 0.0), (31, 0.38, -0.055), (46, 0.0, 0.0), (55, 0.0, 0))

GUARD_R = dict(u=(-0.35, -0.30, 0.18), l=(-1.40, -0.35), h=(0.20, 0.0, 0.05))
GUARD_L = dict(u=(-0.55, 0.20, -0.14), l=(-1.25, 0.30), h=(0.15, 0.0, -0.05))

FOOT_OFF = {'L': Vector((-0.10, 0.36, 0)), 'R': Vector((0.12, -0.30, 0))}
FOOT_YAW = {'L': 0.10, 'R': -0.35}                    # blade stance; right foot pivots on its ball during the strike

def torso_channels(f, partial):
    yh, yc = hermite(f, YAW_HIP), hermite(f, YAW_CHEST)
    imp = bump(f, F_HIT, 14)
    if partial:      # upper-body-only: TORSO/legs are NOT keyed (engine locomotion owns them), chest carries all rotation
        return {'TORSO': None,
                'UpTorso': ((0, 0, 0), (-0.10 - 0.10 * imp, yh + yc + 0.22, 0.02 * imp))}
    return {'TORSO': ((0.02 * imp, -0.20 - 0.06 * imp, hermite(f, PELV_Z)), (-0.03 - 0.05 * imp, yh, 0.03 * imp)),
            'UpTorso': ((0, 0, 0), (-0.10 - 0.10 * imp, yc, 0.02 * imp))}
