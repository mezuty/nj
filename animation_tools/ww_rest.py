"""Wonder Woman - Bracelet Clash (F, redone), Godkiller (C), Golden Eagle (T), Wrath of Zeus (V).
ONE animation each, speed 1.0, real-time frames @60fps, upper body only (TORSO/legs never keyed)."""
import numpy as np
from clipkit import ramp, bump
Z3 = (0,0,0)
def mir(v): return (v[0], -v[1], -v[2])
def sym(keysR):           # left arm = mirror of right, optional frame lag
    return [(f, mir(v)) for f, v in keysR]
def lagk(keys, d): return [(min(f+d, keys[-1][0]) if 0 < f < keys[-1][0] else f, v) for f, v in keys]
def col(fn): return lambda f: np.column_stack([fn(np.asarray(f, float)), 0*np.asarray(f, float), 0*np.asarray(f, float)])

# ======================= F: Bracelet Clash (bracelets really bang together) =======================
# forearms vertical in front of the face; inner-shoulder Y swings them apart / together (pec-deck path)
FX, FL = (-50, -95)
def armR(y, x=FX): return (x, y, 0)
CLASH = dict(action="WonderWoman_BraceletClash", slot="BraceletClash", speed=1.0, length=64, sigma=0,
  markers={"GUARD": 8, "OPEN": 28, "CLASH": 33, "SERVER_STOP": 51},
  notes=("Game: ONE track, playAnim(..., WW_ANIMS.BraceletClash, 0.06, 1) at cast start. Priority = Action.",
         "0-8 forearms snap up in front of the face, bracelets almost touching -> 8-22 charging: arms tremble",
         "on a 10-frame beat while the core grows -> 22-28 arms swing wide apart, chest opens ->",
         "28-33 slam inward: BRACELETS BANG TOGETHER at 33 (castTime 0.55, shockwave fires) ->",
         "33-37 they spring apart from the clink, 37-44 settle close -> lower to rest by 64."),
  head=dict(chin=lambda f: -3*ramp(f,0,8) + 4*bump(f,27,3) - 2*ramp(f,40,64), nod=lambda f: -6*bump(f,34.5,2.2)),
  tracks={
   "UpTorso":      [(0,Z3),(8,(-4,0,0)),(22,(-7,0,0)),(28,(8,0,0)),(33,(-9,0,0)),(37,(-4,0,0)),(44,(-6,0,0)),(64,Z3)],
   "FK_UpperArm.R":[(0,Z3),(8,armR(-44,-44)),(22,armR(-46,-44)),(28,armR(32,-55)),(33,armR(-60,-42)),(37,armR(-47,-44)),(44,armR(-54,-43)),(64,Z3)],
   "FK_LowerArm.R":[(0,Z3),(9,(-104,0,0)),(23,(-106,0,0)),(29,(-88,0,0)),(33,(-108,0,0)),(38,(-100,0,0)),(45,(-106,0,0)),(64,Z3)],
   "FK_Hand.R":    [(0,Z3),(10,(-6,0,0)),(24,(-6,0,0)),(30,(10,0,0)),(34,(-12,0,0)),(39,(0,0,0)),(64,Z3)],
  },
  add={"FK_UpperArm.R": col(lambda f: 2.5*np.sin(2*np.pi*f/10)*ramp(f,8,12)*(1-ramp(f,20,23))),
       "FK_LowerArm.R": col(lambda f: 3*np.sin(2*np.pi*(f-1)/10)*ramp(f,8,12)*(1-ramp(f,20,23))),
       "UpTorso":       col(lambda f: 0.8*np.sin(2*np.pi*f/10)*ramp(f,8,12)*(1-ramp(f,20,23)))})
for b in ("FK_UpperArm","FK_LowerArm","FK_Hand"):
    CLASH["tracks"][b+".L"] = sym(CLASH["tracks"][b+".R"])
CLASH["add"]["FK_UpperArm.L"] = CLASH["add"]["FK_UpperArm.R"]; CLASH["add"]["FK_LowerArm.L"] = CLASH["add"]["FK_LowerArm.R"]

# ======================= C: Godkiller (sword in right hand) =======================
# server (fixed dashTime 0.22, contact holds until it ends): draw 0-11 | dash 11-24 | SLASH 24-31 (pass) |
# sheathe/still 31-61 | flick + 4 cuts 61,67,73,79 | raise 74-82, CLEAVE lands 85 (turn + plant) |
# fissure 85-98 | PILLAR 98 | hold -> finish 125 | stop ~134 | rest 150
GODKILLER = dict(action="WonderWoman_Godkiller", slot="Godkiller", speed=1.0, length=150,
  markers={"DRAWN": 11, "DASH": 11, "SLASH": 24, "STILL": 31, "FLICK": 61, "CUT2": 67, "CUT3": 73, "CUT4": 79, "CLEAVE": 85, "PILLAR": 98, "SERVER_STOP": 134},
  notes=("Game: ONE track, playAnim(..., WW_ANIMS.Godkiller, 0.05, 1) at cast start. Priority = Action.",
         "Needs the fixed dash (dashTime = 0.22) + contact hold so the slash always starts at frame 24.",
         "0-11 sword drawn low, body coils -> 11-24 dash: leaning in, blade trailing behind ->",
         "24-31 rising slash straight through the target as she passes -> 31-61 back to them, blade lowered,",
         "dead still (cut marks appear) -> 61 wrist flick, small accents on each released cut 61/67/73/79 ->",
         "74-82 both hands raise the sword overhead -> CLEAVE planted into the ground at 85 -> holds the",
         "planted blade, head lifts as the pillar launches them (98) -> rises and lowers the sword, rest by 150."),
  head=dict(chin=lambda f: -4*ramp(f,0,11)*(1-ramp(f,26,32)) - 6*ramp(f,34,44)*(1-ramp(f,58,63)) + 12*bump(f,106,7) - 3*ramp(f,86,90)*(1-ramp(f,96,100)),
            nod=lambda f: -6*bump(f,62,2) - 7*bump(f,86.5,2.4)),
  tracks={
   "UpTorso":      [(0,Z3),(11,(-8,-20,0)),(24,(-14,-24,0)),(28,(-4,10,4)),(31,(-2,22,5)),(44,(0,4,0)),(61,(1,0,0)),(74,(4,0,0)),
                    (82,(10,0,0)),(85,(-22,0,0)),(92,(-16,0,0)),(125,(-12,0,0)),(150,Z3)],
   "FK_UpperArm.R":[(0,Z3),(11,(20,0,0)),(24,(36,0,0)),(28,(-55,0,0)),(31,(-112,0,0)),(44,(-30,0,0)),(56,(-6,0,0)),(61,(-8,0,0)),
                    (74,(-20,0,0)),(82,(-165,0,0)),(85,(-42,0,0)),(92,(-38,0,0)),(125,(-36,0,0)),(150,Z3)],
   "FK_LowerArm.R":[(0,Z3),(11,(-30,0,0)),(24,(-22,0,0)),(27,(-40,0,0)),(31,(-6,0,0)),(44,(-25,0,0)),(56,(-20,0,0)),(60,(-40,0,0)),
                    (63,(-6,0,0)),(74,(-15,0,0)),(82,(-40,0,0)),(85,(-8,0,0)),(92,(-12,0,0)),(125,(-14,0,0)),(150,Z3)],
   "FK_Hand.R":    [(0,Z3),(11,(30,0,0)),(24,(35,0,0)),(28,(0,0,0)),(31,(-25,0,0)),(44,(20,0,0)),(60,(25,0,0)),(63,(-15,0,0)),
                    (67,(5,0,0)),(82,(-20,0,0)),(85,(15,0,0)),(125,(15,0,0)),(150,Z3)],
   "FK_UpperArm.L":[(0,Z3),(11,(-45,0,0)),(24,(-35,0,0)),(28,(5,0,0)),(31,(25,0,-6)),(44,(5,0,-4)),(61,(0,0,-4)),(74,(-20,0,0)),
                    (83,(-160,0,0)),(86,(-40,0,0)),(92,(-36,0,0)),(125,(-34,0,0)),(150,Z3)],
   "FK_LowerArm.L":[(0,Z3),(11,(-40,0,0)),(24,(-35,0,0)),(31,(-30,0,0)),(44,(-12,0,0)),(74,(-15,0,0)),(83,(-40,0,0)),(86,(-10,0,0)),(125,(-14,0,0)),(150,Z3)],
   "FK_Hand.L":    [(0,Z3),(11,(5,0,0)),(31,(10,0,0)),(83,(-20,0,0)),(86,(15,0,0)),(125,(15,0,0)),(150,Z3)],
  },
  add={"UpTorso": col(lambda f: -1.5*sum(bump(f,c,1.6) for c in (61,67,73,79)) + 0.7*np.sin(2*np.pi*f/40)*ramp(f,34,44)*(1-ramp(f,56,60))
                                + 0.8*np.sin(2*np.pi*f/36)*ramp(f,100,110)*(1-ramp(f,120,126))),
       "FK_UpperArm.R": col(lambda f: -2*sum(bump(f,c+1,1.6) for c in (67,73,79)))})

# ======================= T: Golden Eagle =======================
# server (fixed fireTime 1.25): spread 0-24 (castTime 0.4) | rise 24-39 | fire 39: feathers 39-69, BIG 79 |
# hold to 114 | fold 114-127 | descend 127-142 -> stop ~142 | rest 155
WING_U, WING_L, WING_H = (15,0,80), (-15,0,0), (10,0,0)            # arms out like wings (shoulder sink hidden)
EAGLE = dict(action="WonderWoman_GoldenEagle", slot="GoldenEagle", speed=1.0, length=155,
  markers={"WINGS_OPEN": 24, "RISE": 24, "FIRE": 39, "BIG_FEATHER": 79, "FOLD": 114, "DESCEND": 127, "SERVER_STOP": 142},
  notes=("Game: ONE track, playAnim(..., WW_ANIMS.GoldenEagle, 0.08, 1) at cast start. Priority = Action.",
         "Needs the fixed fire phase (fireTime = 1.25) so the fold always starts at frame 114.",
         "0-24 arms unfold out to the sides with the golden wings, chest lifts -> 24-39 rising, wing-beat",
         "with the arms -> 39-69 feather barrage: two big forward wing-sweeps with the arms (feathers fly",
         "off the wing tips) -> 69-79 right arm draws back and spears forward: BIG feather 79 -> proud hold",
         "with a breathing wing-beat -> 114-127 arms fold in as the wings close -> 127-155 lower and settle."),
  head=dict(chin=lambda f: 4*ramp(f,8,24)*(1-ramp(f,36,42)) - 3*ramp(f,40,48)*(1-ramp(f,110,120)), nod=lambda f: -5*bump(f,80.5,2.2)),
  tracks={
   "UpTorso":      [(0,Z3),(24,(9,0,0)),(39,(6,0,0)),(48,(-6,0,0)),(55,(4,0,0)),(64,(-6,0,0)),(72,(6,-14,0)),(79,(-8,18,2)),(86,(-5,12,1)),
                    (114,(-3,8,0)),(127,(2,2,0)),(155,Z3)],
   "FK_UpperArm.R":[(0,Z3),(24,WING_U),(39,(10,0,80)),(48,(-70,0,35)),(55,(15,0,80)),(64,(-70,0,35)),(72,(30,0,30)),(79,(-92,0,0)),
                    (86,(-88,0,0)),(114,(-80,0,4)),(127,(-20,0,10)),(155,Z3)],
   "FK_LowerArm.R":[(0,Z3),(25,WING_L),(40,(-20,0,0)),(49,(-5,0,0)),(56,(-25,0,0)),(65,(-5,0,0)),(73,(-70,0,0)),(80,(-2,0,0)),
                    (87,(-6,0,0)),(114,(-10,0,0)),(127,(-60,0,0)),(155,Z3)],
   "FK_Hand.R":    [(0,Z3),(26,WING_H),(41,(15,0,0)),(50,(-15,0,0)),(57,(15,0,0)),(66,(-15,0,0)),(74,(20,0,0)),(81,(-15,0,0)),(88,(0,0,0)),(155,Z3)],
   "FK_UpperArm.L":[(0,Z3),(24,mir(WING_U)),(39,mir((10,0,80))),(49,mir((-70,0,35))),(56,mir((15,0,80))),(65,mir((-70,0,35))),(72,mir((10,0,70))),
                    (79,mir((25,0,55))),(86,mir((20,0,60))),(114,mir((15,0,62))),(127,mir((-20,0,10))),(155,Z3)],
   "FK_LowerArm.L":[(0,Z3),(25,WING_L),(40,(-20,0,0)),(50,(-5,0,0)),(57,(-25,0,0)),(66,(-5,0,0)),(79,(-15,0,0)),(114,(-15,0,0)),(127,(-60,0,0)),(155,Z3)],
   "FK_Hand.L":    [(0,Z3),(26,mir(WING_H)),(42,mir((15,0,0))),(51,mir((-15,0,0))),(58,mir((15,0,0))),(67,mir((-15,0,0))),(80,mir((15,0,0))),(155,Z3)],
  },
  add={"FK_UpperArm.L": lambda f: np.column_stack([0*f, 0*f, -(6*np.sin(2*np.pi*(np.asarray(f,float)-24)/30)*ramp(f,24,30)*(1-ramp(f,36,40))
                                                         + 4*np.sin(2*np.pi*(np.asarray(f,float)-88)/24)*ramp(f,88,94)*(1-ramp(f,108,114)))]),
       "FK_UpperArm.R": lambda f: np.column_stack([0*f, 0*f, 6*np.sin(2*np.pi*(np.asarray(f,float)-24)/30)*ramp(f,24,30)*(1-ramp(f,36,40))]),
       "UpTorso":       col(lambda f: 0.8*np.sin(2*np.pi*(f-88)/24)*ramp(f,88,94)*(1-ramp(f,108,114)))})

# ======================= V: Wrath of Zeus =======================
# server: charge 0-21 (castTime 0.35) | rise 21-42 | bolts 42, 62, 82 (at the hands) | RELEASE beam 101 |
# torrent 101-179 (ticks every 11.4 f) | FINALE 179 | descend 179-200 | stop ~208 | rest 222
BEAM_U, BEAM_L, BEAM_H = (-85,-30,0), (-5,0,0), (-25,0,0)          # palms driven forward, hands nearly together
TICKS = [101 + 11.4*i for i in range(7)]
ZEUS = dict(action="WonderWoman_WrathOfZeus", slot="WrathOfZeus", speed=1.0, length=222,
  markers={"CHARGE": 0, "RISE": 21, "BOLT1": 42, "BOLT2": 62, "BOLT3": 82, "RELEASE": 101, "FINALE": 179, "DESCEND": 179, "SERVER_STOP": 208},
  notes=("Game: ONE track, playAnim(..., WW_ANIMS.WrathOfZeus, 0.08, 1) at cast start. Priority = Action.",
         "0-21 both arms sweep up overhead calling the storm, chest arches, eyes up -> 21-42 rising, energy",
         "gathering (tremble) -> bolts strike her raised hands at 42 / 62 / 82, each one jolts her harder ->",
         "82-101 drags the lightning down and drives both palms forward: RELEASE 101 -> 101-179 sustained",
         "torrent: leaning into the beam, recoil on every damage tick -> 170-179 fists pull back, FINALE 179",
         "punches down at the target -> 179-200 descends, arms lower -> rest by 222."),
  head=dict(chin=lambda f: 12*ramp(f,4,20)*(1-ramp(f,86,98)) - 3*ramp(f,98,104)*(1-ramp(f,186,200)),
            nod=lambda f: -7*bump(f,181,2.6)),
  tracks={
   "UpTorso":      [(0,Z3),(20,(10,0,0)),(42,(12,0,0)),(82,(14,0,0)),(92,(2,0,0)),(101,(-8,0,0)),(140,(-10,0,0)),(170,(-9,0,0)),
                    (176,(4,0,0)),(179,(-16,0,0)),(186,(-12,0,0)),(200,(-3,0,0)),(222,Z3)],
   "FK_UpperArm.R":[(0,Z3),(16,(-165,0,0)),(42,(-168,0,0)),(82,(-170,0,0)),(92,(-130,-10,0)),(101,BEAM_U),(170,(-86,-30,0)),
                    (176,(10,0,0)),(179,(-55,-12,0)),(186,(-50,-10,0)),(200,(-20,0,0)),(222,Z3)],
   "FK_LowerArm.R":[(0,Z3),(17,(-25,0,0)),(82,(-28,0,0)),(93,(-40,0,0)),(101,BEAM_L),(170,(-6,0,0)),(176,(-100,0,0)),(179,(-10,0,0)),
                    (186,(-14,0,0)),(200,(-30,0,0)),(222,Z3)],
   "FK_Hand.R":    [(0,Z3),(18,(-15,0,0)),(82,(-15,0,0)),(94,(10,0,0)),(101,BEAM_H),(170,BEAM_H),(176,(-10,0,0)),(179,(10,0,0)),(200,(5,0,0)),(222,Z3)],
  },
  add={"FK_UpperArm.R": col(lambda f: -3*sum(bump(f,b+1,2.2)*(0.6+0.25*i) for i,b in enumerate((42,62,82)))
                                       + 2.5*np.sin(2*np.pi*f/9)*ramp(f,22,30)*(1-ramp(f,80,86))
                                       + 4*sum(bump(f,t+1,1.8) for t in TICKS[1:])),
       "FK_LowerArm.R": col(lambda f: -2*np.sin(2*np.pi*(f-1)/9)*ramp(f,22,30)*(1-ramp(f,80,86)) - 3*sum(bump(f,t+2,1.8) for t in TICKS[1:])),
       "UpTorso":       col(lambda f: 3*sum(bump(f,b,2.0)*(0.6+0.25*i) for i,b in enumerate((42,62,82))) + 1.6*sum(bump(f,t,1.8) for t in TICKS[1:]))})
for b in ("FK_UpperArm","FK_LowerArm","FK_Hand"):
    ZEUS["tracks"][b+".L"] = sym(lagk(ZEUS["tracks"][b+".R"], 1))
ZEUS["add"]["FK_UpperArm.L"] = ZEUS["add"]["FK_UpperArm.R"]; ZEUS["add"]["FK_LowerArm.L"] = ZEUS["add"]["FK_LowerArm.R"]

CLIPS = {"Clash": CLASH, "Godkiller": GODKILLER, "Eagle": EAGLE, "Zeus": ZEUS}
