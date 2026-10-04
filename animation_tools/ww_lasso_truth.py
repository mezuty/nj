"""Wonder Woman - Lasso of Truth (E). Caster, upper-body only (server never roots her; flight allowed).
Server timeline (real s) -> clip frames @60fps (anim time = real * speed):
  LassoSpin  x1.1  castTime 0.45            -> Throw takes over at f30           (clip 34 f)
  LassoThrow x1.3  travel 0.2-0.5 + cinch 0.18 -> Hold takes over at f30..f53     (clip 58 f, settles into GRIP by f24)
  LassoHold  x1.0  reel 0.45 + compel 0.9   -> reel ends f27, ticks f45/63/81, Hurl at f81 (clip 88 f)
                   (also replayed after the slam for the 0.32 s retract: f0-19 = reel the rope in)
  LassoHurl  x1.2  hurlTime 0.42            -> SLAM f30, Hold replays at f30 (fade .15) (clip 40 f)"""
import numpy as np
from clipkit import PIN, ramp, bump
Z3 = (0,0,0)
# ---- key poses (deg, Euler XYZ). Untwisted arms only: Y-twist on this rig drives the elbow into the torso.
SPIN  = dict(ch=(2,6,7),   ru=(-168,0,0), rl=(-25,0,0), rh=(-20,0,0), lu=(0,0,-14), ll=(-36,0,0), lh=(10,0,0))
GRIP  = dict(ch=(-4,8,0),  ru=(-80,0,0),  rl=(-15,0,0), rh=(5,0,0),   lu=(-72,0,0),  ll=(-25,0,0), lh=(0,0,0))
HAUL  = dict(ch=(10,-14,-3), ru=(6,0,0),  rl=(-84,0,0), rh=(-10,0,0), lu=(-80,0,0),  ll=(-10,0,0), lh=(0,0,0))
OMEGA = 2*np.pi/26          # twirl: 16 rad/s real at x1.1 -> one loop orbit every ~26 anim frames

def _twirl(f, amp):
    e = ramp(f, 9, 20); w = OMEGA*np.asarray(f, float)
    return lambda ph, a: np.column_stack([a[0]*np.sin(w+ph)*e, a[1]*np.cos(w+ph)*e, a[2]*np.cos(w+ph)*e])
def tw(ph, a): return lambda f: _twirl(f, None)(ph, a)

TICKS = (45, 63, 81)
def tug(f):   # strain pulse on every damage tick (0.3 s cadence), smooth bumps
    return sum(bump(f, t-1.5, 3.2) for t in TICKS) * ramp(f, 27, 34)
def breathe(f, a, period=36, ph=0.0):
    return a*np.sin(2*np.pi*np.asarray(f,float)/period + ph) * ramp(f, 26, 36)

CLIPS = {
 "Spin": dict(action="WonderWoman_LassoOfTruth_Spin", slot="LassoSpin", speed=1.1, length=34, dense_keys=(0,34),
   markers={"SPIN_FULL":16, "THROW_HANDOFF":30},
   notes=("Lasso hand rises through the front to straight overhead and twirls the loop (circle every ~26 f,",
          "matching the server's 16 rad/s orbit); left fist settles low and out; chest lifts and tilts away;",
          "eyes on the target. Throw takes over at f30 (its first frame == this clip's f30)."),
   head=dict(chin=lambda f: -2*ramp(f,0,14)),
   tracks={
    "UpTorso":      [(0,Z3),(12,SPIN["ch"]),(34,(2.5,7,7.5))],
    "FK_UpperArm.R":[(0,Z3),(9,(-95,0,0)),(17,SPIN["ru"]),(34,(-170,0,0))],
    "FK_LowerArm.R":[(0,Z3),(10,(-45,0,0)),(18,SPIN["rl"]),(34,(-26,0,0))],
    "FK_Hand.R":    [(0,Z3),(11,(15,0,0)),(19,SPIN["rh"]),(34,(-21,0,0))],
    "FK_UpperArm.L":[(0,Z3),(14,SPIN["lu"]),(34,(-2,0,-15))],
    "FK_LowerArm.L":[(0,Z3),(16,SPIN["ll"]),(34,(-38,0,0))],
    "FK_Hand.L":    [(0,Z3),(18,SPIN["lh"]),(34,(12,0,0))],
   },
   add={
    "FK_UpperArm.R": tw(0.0, (4,0,5)),
    "FK_LowerArm.R": tw(-0.7, (10,0,0)),
    "FK_Hand.R":     tw(-1.4, (16,0,14)),
    "UpTorso":       tw(np.pi, (0,1.2,0.8)),
   }),
 "Throw": dict(action="WonderWoman_LassoOfTruth_Throw", slot="LassoThrow", speed=1.3, length=58,
   pin=("Spin",30), pin_vel=True, strike=(0,14),
   markers={"RELEASE":5, "GRIP":24, "HOLD_HANDOFF_MIN":30, "HOLD_HANDOFF_MAX":53},
   notes=("f0 == Spin f30 (keeps the twirl's momentum) -> chest whips left, overhead arm drives down and",
          "forward -> RELEASE f5 (loop leaves the hand, arm pointing at the target, fingers flick) -> follow-",
          "through -> left hand joins the rope -> GRIP by f24: both hands forward on the taut rope, living",
          "hold to f58 so the Hold clip can take over anywhere from f30 (close target) to f53 (max range)."),
   head=dict(chin=lambda f: -3+0*f),
   tracks={
    "UpTorso":      [(0,PIN),(6,(-8,16,3)),(12,(-6,13,2)),(24,GRIP["ch"]),(58,(-3.75,7.75,0))],
    "FK_UpperArm.R":[(0,PIN),(3,(-150,0,0)),(6,(-96,6,0)),(10,(-88,4,0)),(24,GRIP["ru"]),(58,(-79.5,0,0))],
    "FK_LowerArm.R":[(0,PIN),(4,(-45,0,0)),(7,(-4,0,0)),(11,(-8,0,0)),(24,GRIP["rl"]),(58,(-15.5,0,0))],
    "FK_Hand.R":    [(0,PIN),(5,(-30,0,0)),(8,(-12,0,0)),(12,(8,0,0)),(24,GRIP["rh"]),(58,(5.5,0,0))],
    "FK_UpperArm.L":[(0,PIN),(6,(18,0,-12)),(16,(-40,0,-4)),(26,GRIP["lu"]),(58,(-72.5,0,0))],
    "FK_LowerArm.L":[(0,PIN),(6,(-50,0,0)),(18,(-45,0,0)),(28,GRIP["ll"]),(58,(-25.5,0,0))],
    "FK_Hand.L":    [(0,PIN),(8,(10,0,0)),(28,GRIP["lh"]),(58,(0.5,0,0))],
   },
   add={"UpTorso": lambda f: np.column_stack([breathe(f,0.6,40), 0*f, 0*f])}),
 "Hold": dict(action="WonderWoman_LassoOfTruth_Hold", slot="LassoHold", speed=1.0, length=88, strike=(10,30), pin=("Throw",41),
   markers={"REEL_END":27, "TICK1":45, "TICK2":63, "TICK3":81, "HURL_HANDOFF":81},
   notes=("f0 == Throw grip pose. 0-6 hands re-grip and reach -> 6-27 big haul (accelerates with the",
          "server's ease-in reel): chest swings from left-turned to right-turned and leans back, right fist",
          "rips back to the ribs, left hand slides forward along the rope -> 27-88 COMPEL: braced on the",
          "taut rope, chin down, a strain tug on every damage tick (f45/63/81) + breathing. Hurl at f81.",
          "Also replayed after the slam: its first 19 f read as reeling the lasso back in."),
   head=dict(chin=lambda f: -3-1*ramp(f,4,27)),
   tracks={
    "UpTorso":      [(0,PIN),(6,(-7,10,1)),(22,(8,-10,-2)),(27,HAUL["ch"]),(88,(10.5,-14.5,-3))],
    "FK_UpperArm.R":[(0,PIN),(6,(-86,0,0)),(18,(-30,0,0)),(27,HAUL["ru"]),(88,(7,0,0))],
    "FK_LowerArm.R":[(0,PIN),(6,(-12,0,0)),(20,(-60,0,0)),(27,HAUL["rl"]),(88,(-85,0,0))],
    "FK_Hand.R":    [(0,PIN),(8,(8,0,0)),(22,(-5,0,0)),(27,HAUL["rh"]),(88,(-11,0,0))],
    "FK_UpperArm.L":[(0,PIN),(14,(-66,0,0)),(27,HAUL["lu"]),(88,(-81,0,0))],
    "FK_LowerArm.L":[(0,PIN),(14,(-35,0,0)),(27,HAUL["ll"]),(88,(-11,0,0))],
    "FK_Hand.L":    [(0,PIN),(16,(6,0,0)),(27,HAUL["lh"]),(88,(2,0,0))],
   },
   add={
    "UpTorso":       lambda f: np.column_stack([1.6*tug(f)+breathe(f,0.8), breathe(f,0.6,48,1.0), 0*f]),
    "FK_UpperArm.R": lambda f: np.column_stack([4.0*tug(f), 0*f, 0*f]),
    "FK_LowerArm.R": lambda f: np.column_stack([-3.0*tug(np.asarray(f)-1), 0*f, 0*f]),
    "FK_Hand.R":     lambda f: np.column_stack([-4.0*tug(np.asarray(f)-2), 0*f, 0*f]),
    "FK_UpperArm.L": lambda f: np.column_stack([2.0*tug(np.asarray(f)-1)+breathe(f,0.8,36,2.0), 0*f, 0*f]),
    "FK_LowerArm.L": lambda f: np.column_stack([-2.0*tug(np.asarray(f)-2), 0*f, 0*f]),
   }),
 "Hurl": dict(action="WonderWoman_LassoOfTruth_Hurl", slot="LassoHurl", speed=1.2, length=40,
   pin=("Hold",81), pin_vel=True, strike=(4,36),
   markers={"LIFT":5, "APEX":21, "SLAM":30},
   notes=("f0 == Hold f81. 0-5 dip and load -> 5-21 heave: arms drive up past the face to straight",
          "overhead while the chest arches back (target rises over her, APEX f21) -> 21-30 the chest",
          "folds forward hard and both fists pull down onto the shoulders, flipping the target over her",
          "back -> SLAM f30 -> 30-40 absorb the recoil (Hold replays from f30 with a 0.15 s fade)."),
   head=dict(chin=lambda f: -2+0*f, k=(0.25,0.85,0.6), nod=lambda f: -7*bump(f,31.5,3.0)),
   tracks={
    "UpTorso":      [(0,PIN),(6,(-4,-11,-2)),(14,(10,-4,0)),(21,(14,-6,0)),(27,(-18,8,3)),(30,(-26,10,4)),(34,(-23,9,3.5)),(40,(-20,8,3))],
    "FK_UpperArm.R":[(0,PIN),(5,(20,0,0)),(14,(-110,0,0)),(21,(-165,0,0)),(30,(-150,0,0)),(40,(-146,0,0))],
    "FK_LowerArm.R":[(0,PIN),(5,(-95,0,0)),(13,(-70,0,0)),(21,(-50,0,0)),(30,(-120,0,0)),(40,(-116,0,0))],
    "FK_Hand.R":    [(0,PIN),(6,(-15,0,0)),(21,(-20,0,0)),(28,(-35,0,0)),(30,(-30,0,0)),(40,(-25,0,0))],
    "FK_UpperArm.L":[(0,PIN),(6,(-60,0,0)),(14,(-118,0,0)),(21,(-165,0,0)),(30,(-145,0,0)),(40,(-142,0,0))],
    "FK_LowerArm.L":[(0,PIN),(6,(-36,0,0)),(14,(-62,0,0)),(21,(-50,0,0)),(30,(-115,0,0)),(40,(-110,0,0))],
    "FK_Hand.L":    [(0,PIN),(21,(-20,0,0)),(30,(-30,0,0)),(40,(-25,0,0))],
   }),
}
