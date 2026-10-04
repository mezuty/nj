"""Wonder Woman - Hestia's Snare (R) and Bracelet Clash (F). ONE animation each, speed 1.0, real-time frames @60fps.
R timeline (server, with fixed throwTime 0.4): spin 0-30 | throw 30-54 | drop 54-62 | cinch 62-98 (tick 82) |
  bind 98-116 | lift 116-133 | slam 133-143 IMPACT | retract 143-161 -> stop ~161 | rest 178
F timeline: guard + charge 0-33 (castTime 0.55) | CLASH 33 (strike burst) | recoil | stop ~51 (0.3 s) | rest 64"""
import numpy as np
from clipkit import ramp, bump
Z3 = (0,0,0)
def mir(v): return (v[0], -v[1], -v[2])

# ---------------- R: Hestia's Snare ----------------
OM = 2*np.pi/27       # loop orbit: 14 rad/s -> one circle every ~27 frames
def big_twirl(f):     # whole-arm circles from the shoulder (E twirls from the wrist)
    e = ramp(f, 8, 16)*(1-ramp(f, 27, 32)); w = OM*np.asarray(f, float)
    return np.column_stack([10*np.cos(w)*e, 0*w, 5*np.sin(w)*e])
def lag(fn, d): return lambda f: fn(np.asarray(f, float)-d)

SNARE = dict(action="WonderWoman_HestiasSnare", slot="HestiasSnare", speed=1.0, length=178,
  markers={"SPIN": 16, "THROW": 30, "RELEASE": 34, "RING_LANDS": 62, "TICK": 82, "BIND": 98, "LIFT": 116, "TOP": 133, "SLAM": 143, "SERVER_STOP": 161},
  notes=("Game: ONE track, playAnim(..., WW_ANIMS.HestiasSnare, 0.08, 1) at cast start. Priority = Action.",
         "Needs the fixed throw time (throwTime = 0.4) so the clip and the server stay in sync.",
         "0-30 straight lasso arm swings big circles from the shoulder, left hand marks the spot ->",
         "30-46 high lob, RELEASE 34, eyes follow the loop up -> arm follows it down onto the ground (62) ->",
         "62-98 two-hand cinch: hauls the rope back to the hips, tug on the damage tick (82) ->",
         "98-116 re-grip and load low -> 116-133 explosive heave straight up overhead (targets rise) ->",
         "133-143 whips everything down, chest crunches: SLAM 143 -> rebound, reel the rope in, rest by 178."),
  head=dict(chin=lambda f: 9*bump(f,44,6) - 10*ramp(f,50,62)*(1-ramp(f,108,118)) + 10*bump(f,129,6) - 3*ramp(f,140,145)*(1-ramp(f,160,176)),
            nod=lambda f: -8*bump(f,145.5,2.6)),
  tracks={
   "UpTorso":      [(0,Z3),(14,(2,6,6)),(28,(5,-8,3)),(36,(-4,10,4)),(46,(0,6,2)),(62,(-6,2,0)),(80,(4,-4,0)),(98,(12,-8,0)),
                    (108,(6,-4,0)),(116,(-10,0,0)),(122,(4,0,0)),(132,(14,0,0)),(139,(-6,0,0)),(143,(-24,0,0)),(149,(-18,0,0)),(161,(-4,-4,0)),(178,Z3)],
   "FK_UpperArm.R":[(0,Z3),(9,(-95,0,0)),(16,(-160,0,0)),(30,(-165,0,0)),(34,(-125,0,0)),(38,(-108,0,0)),(46,(-105,0,0)),(62,(-58,0,0)),
                    (80,(-25,0,0)),(98,(15,0,0)),(116,(-30,0,0)),(122,(-100,0,0)),(133,(-165,0,0)),(138,(-130,0,0)),(143,(-40,0,0)),
                    (150,(-38,0,0)),(161,(10,0,0)),(178,Z3)],
   "FK_LowerArm.R":[(0,Z3),(10,(-35,0,0)),(17,(-10,0,0)),(30,(-12,0,0)),(33,(-25,0,0)),(37,(-3,0,0)),(46,(-6,0,0)),(62,(-12,0,0)),
                    (82,(-40,0,0)),(98,(-75,0,0)),(116,(-25,0,0)),(124,(-30,0,0)),(133,(-35,0,0)),(140,(-25,0,0)),(143,(-10,0,0)),
                    (150,(-14,0,0)),(161,(-70,0,0)),(178,Z3)],
   "FK_Hand.R":    [(0,Z3),(18,(-15,0,0)),(30,(-15,0,0)),(33,(-30,0,0)),(36,(15,0,0)),(44,(5,0,0)),(62,Z3),(98,(-10,0,0)),(116,Z3),
                    (133,(-20,0,0)),(141,(-30,0,0)),(143,(10,0,0)),(161,(-10,0,0)),(178,Z3)],
   "FK_UpperArm.L":[(0,Z3),(14,(-50,0,-6)),(30,(-50,0,-6)),(40,(-20,0,-6)),(60,(-58,0,0)),(82,(-22,0,0)),(98,(8,0,0)),(117,(-30,0,0)),
                    (123,(-100,0,0)),(134,(-165,0,0)),(139,(-130,0,0)),(144,(-40,0,0)),(152,(-30,0,0)),(165,(-6,0,-6)),(178,Z3)],
   "FK_LowerArm.L":[(0,Z3),(16,(-8,0,0)),(30,(-8,0,0)),(40,(-30,0,0)),(60,(-20,0,0)),(84,(-45,0,0)),(98,(-65,0,0)),(117,(-25,0,0)),
                    (125,(-30,0,0)),(134,(-35,0,0)),(141,(-25,0,0)),(144,(-10,0,0)),(165,(-20,0,0)),(178,Z3)],
   "FK_Hand.L":    [(0,Z3),(18,(10,0,0)),(40,(5,0,0)),(60,Z3),(98,(-10,0,0)),(117,Z3),(134,(-20,0,0)),(142,(-30,0,0)),(144,(10,0,0)),(178,Z3)],
  },
  add={
   "FK_UpperArm.R": big_twirl,
   "FK_LowerArm.R": lambda f: np.column_stack([6*np.cos(OM*np.asarray(f,float)-0.8)*ramp(f,8,16)*(1-ramp(f,27,32)), 0*f, 0*f]),
   "FK_Hand.R":     lambda f: np.column_stack([10*np.cos(OM*np.asarray(f,float)-1.6)*ramp(f,8,16)*(1-ramp(f,27,32)), 0*f, 8*np.sin(OM*np.asarray(f,float)-1.6)*ramp(f,8,16)*(1-ramp(f,27,32))]),
   "UpTorso":       lambda f: np.column_stack([2*bump(f,82,3.5), 1.2*np.sin(OM*np.asarray(f,float)+np.pi)*ramp(f,8,16)*(1-ramp(f,27,32)), 0*f]),
   "FK_UpperArm.L": lambda f: np.column_stack([4*bump(f,83,3.5), 0*f, 0*f]),
  })

# ---------------- F: Bracelet Clash ----------------
G_U, G_L, G_H = (-45,0,3), (-100,0,0), (-5,0,10)       # bracelets up, flanking the face
O_U, O_L, O_H = (25,0,4), (-60,0,0), (15,0,0)          # arms flung back, chest open
C_U, C_L, C_H = (-62,0,2), (-85,0,0), (0,0,22)         # forearms smash forward together, hands tilted in
def strain(f, amp):   # charging tremor on a steady 10-frame cadence
    return amp*np.sin(2*np.pi*np.asarray(f,float)/10)*ramp(f,8,12)*(1-ramp(f,20,23))
CLASH = dict(action="WonderWoman_BraceletClash", slot="BraceletClash", speed=1.0, length=64,
  markers={"GUARD": 8, "OPEN": 29, "CLASH": 33, "SERVER_STOP": 51},
  notes=("Game: ONE track, playAnim(..., WW_ANIMS.BraceletClash, 0.06, 1) at cast start. Priority = Action.",
         "0-8 bracelets snap up beside the face -> 8-22 charging: arms tremble on a 10-frame beat while the",
         "core grows, chest presses forward -> 22-29 arms fling back, chest opens -> 29-33 forearms smash",
         "forward together: CLASH 33 (= castTime 0.55, shockwave fires) -> recoil from the blast -> lower to rest by 64."),
  head=dict(chin=lambda f: -3*ramp(f,0,8) + 5*bump(f,28,3) - 2*ramp(f,40,64), nod=lambda f: -7*bump(f,34.5,2.4)),
  tracks={
   "UpTorso":      [(0,Z3),(8,(-3,0,0)),(22,(-6,0,0)),(29,(10,0,0)),(33,(-10,0,0)),(37,(-3,0,0)),(44,(-6,0,0)),(64,Z3)],
   "FK_UpperArm.R":[(0,Z3),(8,G_U),(22,(-50,0,3)),(29,O_U),(33,C_U),(37,(-56,0,6)),(44,(-58,0,3)),(64,Z3)],
   "FK_LowerArm.R":[(0,Z3),(9,G_L),(23,(-104,0,0)),(30,O_L),(34,C_L),(38,(-80,0,0)),(45,(-84,0,0)),(64,Z3)],
   "FK_Hand.R":    [(0,Z3),(10,G_H),(24,G_H),(30,O_H),(34,C_H),(39,(-10,0,15)),(46,(0,0,15)),(64,Z3)],
   "FK_UpperArm.L":[(0,Z3),(8,mir(G_U)),(22,mir((-50,0,3))),(29,mir(O_U)),(33,mir(C_U)),(37,mir((-56,0,6))),(44,mir((-58,0,3))),(64,Z3)],
   "FK_LowerArm.L":[(0,Z3),(9,G_L),(23,(-104,0,0)),(30,O_L),(34,C_L),(38,(-80,0,0)),(45,(-84,0,0)),(64,Z3)],
   "FK_Hand.L":    [(0,Z3),(10,mir(G_H)),(24,mir(G_H)),(30,mir(O_H)),(34,mir(C_H)),(39,mir((-10,0,15))),(46,mir((0,0,15))),(64,Z3)],
  },
  add={
   "FK_UpperArm.R": lambda f: np.column_stack([strain(f,2.5), 0*f, 0*f]),
   "FK_UpperArm.L": lambda f: np.column_stack([strain(np.asarray(f)-2,2.5), 0*f, 0*f]),
   "FK_LowerArm.R": lambda f: np.column_stack([strain(np.asarray(f)-1,3), 0*f, 0*f]),
   "FK_LowerArm.L": lambda f: np.column_stack([strain(np.asarray(f)-3,3), 0*f, 0*f]),
   "UpTorso":       lambda f: np.column_stack([strain(f,0.8), 0*f, 0*f]),
  })
CLIPS = {"Snare": SNARE, "Clash": CLASH}
