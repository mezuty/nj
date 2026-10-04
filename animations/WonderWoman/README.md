# Wonder Woman ability animations

One Blender script per `WW_ANIMS` slot in your kit (21 clips, 60 fps, MrXen0 R15 rig). Each clip's length is derived from the timing in `ABILITY_CONFIG`
and the playback speed in the matching `playAnim(...)` call, so the animation lines up with when the server fires its VFX.

**How to use:** open your MrXen0 R15 `.blend` -> Scripting tab -> open a script -> Run Script. It removes its own previous action first, keys only the animated FK controls
(Bezier + auto-clamped, no `CYCLES`), and adds the gameplay markers listed below as timeline markers. Run as many as you like; each stays in the file as its own action (fake user).
Export each action with your usual exporter and put the asset ids into `WW_ANIMS`.

**Upper-body clips** (the rope abilities - she can still walk/fly while casting) key only `UpTorso`, `HEAD` and the arm/hand controls. No `TORSO`, leg or foot tracks.
**Full-body clips** (rooted / hovering abilities) also key `TORSO` and the legs. Planted-foot clips use solved legs (ankles stay put); hovering clips use hand-authored hanging legs.

**Chaining:** clips that play back-to-back start exactly where the previous one ends (Windup->Crack, Spin->Throw->Hold->Hurl, Spin->Throw->Heave, Guard->Strike,
Draw->Dash->Sheathe->Flick->Cleave, Spread->Fire, Charge->Release). The last clip of every ability returns to the ready pose.
Marker frames are where the matching gameplay moment lands *inside the clip* (they already include the playback speed).

| Slot | File | Ability | Length | Played at | Mode | Markers | What it shows |
|---|---|---|---|---|---|---|---|
| `WW_ANIMS.LashWindup` | `WW_LashWindup.py` | LassoLash | 0.400 s / 25 f | x1.2 (= 0.33 s in game) | upper body | - | right arm cocks overhead-behind, chest coils right (whip trails behind the hand while the rope lengthens) |
| `WW_ANIMS.LashCrack` | `WW_LashCrack.py` | LassoLash | 0.750 s / 46 f | x1.4 (= 0.54 s in game) | upper body | HIT@f17 | overhead sweep -> forward-down whip snap with wrist lag at HIT, follow-through, recoil to ready |
| `WW_ANIMS.LassoSpin` | `WW_LassoSpin.py` | LassoOfTruth | 0.460 s / 29 f | x1.1 (= 0.42 s in game) | upper body | - | right arm raised, wrist/forearm circle the lasso loop overhead while she faces the target |
| `WW_ANIMS.LassoThrow` | `WW_LassoThrow.py` | LassoOfTruth | 0.750 s / 46 f | x1.3 (= 0.58 s in game) | upper body | RELEASE@f10 | wind-back, release flick toward the target, arm holds out as the loop flies and cinches, ends gripping the rope |
| `WW_ANIMS.LassoHold` | `WW_LassoHold.py` | LassoOfTruth | 1.500 s / 91 f | x1 (= 1.50 s in game) | upper body | HURL_WIND@f81 | hand-over-hand reel (2 pulls), braced two-handed compel hold with strain, then loads the hurl |
| `WW_ANIMS.LassoHurl` | `WW_LassoHurl.py` | LassoOfTruth | 0.930 s / 57 f | x1.2 (= 0.78 s in game) | upper body | SLAM@f30 | both hands haul the rope up and over the head (arch back), then pull down hard at SLAM, recover |
| `WW_ANIMS.SnareSpin` | `WW_SnareSpin.py` | HestiasSnare | 0.550 s / 34 f | x1 (= 0.55 s in game) | upper body | - | bigger overhead lasso spin, left arm out for balance, looking up at the loop |
| `WW_ANIMS.SnareThrow` | `WW_SnareThrow.py` | HestiasSnare | 0.710 s / 44 f | x1.2 (= 0.59 s in game) | upper body | RELEASE@f13 | wind-back, forward-down sling at the ground target, ends gripping the rope low |
| `WW_ANIMS.SnareHeave` | `WW_SnareHeave.py` | HestiasSnare | 1.700 s / 103 f | x1 (= 1.70 s in game) | upper body | LIFT@f54, SLAM@f80 | cinch (pull in), bind (squeeze), LIFT overhead, SLAM down, recover |
| `WW_ANIMS.ClashGuard` | `WW_ClashGuard.py` | BraceletClash | 0.600 s / 37 f | x1 (= 0.60 s in game) | full body | - | crouch and gather: bracelets held apart in front of the chest around the energy core |
| `WW_ANIMS.ClashStrike` | `WW_ClashStrike.py` | BraceletClash | 0.700 s / 43 f | x1.3 (= 0.54 s in game) | full body | CLASH@f3 | bracelets clash (frame 3), arms explode wide, wide braced stance, settle |
| `WW_ANIMS.GodkillerDraw` | `WW_GodkillerDraw.py` | Godkiller | 0.280 s / 18 f | x1.3 (= 0.22 s in game) | full body | - | quick-draw: right hand sweeps across the hip then cocks back with the sword, low sprinter lunge |
| `WW_ANIMS.GodkillerDash` | `WW_GodkillerDash.py` | Godkiller | 0.500 s / 31 f | x1.3 (= 0.38 s in game) | full body | SLASH@f12 | horizontal sword lunge, SLASH across the body as she passes the target, decelerate |
| `WW_ANIMS.GodkillerSheathe` | `WW_GodkillerSheathe.py` | Godkiller | 0.450 s / 28 f | x0.8 (= 0.56 s in game) | full body | - | stands out of the lunge and sheathes the sword at her left hip (slow, calm) |
| `WW_ANIMS.GodkillerFlick` | `WW_GodkillerFlick.py` | Godkiller | 0.650 s / 40 f | x1.4 (= 0.46 s in game) | full body | CUT1@f8, CUT2@f17, CUT3@f25, CUT4@f34 | thumb flick at the hilt; four sword twitches on the CUT beats; sword raised overhead two-handed |
| `WW_ANIMS.GodkillerCleave` | `WW_GodkillerCleave.py` | Godkiller | 1.000 s / 61 f | x1.2 (= 0.83 s in game) | full body | IMPACT@f4, PILLAR@f16 | overhead two-handed cleave planted at IMPACT, drives into the ground, PILLAR erupts, stands and recovers |
| `WW_ANIMS.EagleSpread` | `WW_EagleSpread.py` | GoldenEagle | 0.450 s / 28 f | x1 (= 0.45 s in game) | full body | - | anticipation crouch, arms thrown wide into a V (Back-style overshoot) with chest arch |
| `WW_ANIMS.EagleFire` | `WW_EagleFire.py` | GoldenEagle | 1.450 s / 88 f | x1.2 (= 1.21 s in game) | full body | FEATHERS@f0, BIG@f48 | hovering (legs hang, toes pointed): wing flaps, feather volleys, BIG two-fist push, wings fold, soft landing |
| `WW_ANIMS.ZeusCharge` | `WW_ZeusCharge.py` | WrathOfZeus | 1.750 s / 106 f | x1 (= 1.75 s in game) | full body | STRIKE1@f42, STRIKE2@f62, STRIKE3@f82 | gather crouch, arms sweep to the sky, three escalating lightning pulses (STRIKE1-3), legs dangle as she rises |
| `WW_ANIMS.ZeusRelease` | `WW_ZeusRelease.py` | WrathOfZeus | 1.850 s / 112 f | x1 (= 1.85 s in game) | full body | BEAM_START@f6, FINALE@f83 | hovering, both arms thrust at the target firing the beam with a metered recoil cadence, pulled-back FINALE thrust, descend |
| `WW_ANIMS.Victim` | `WW_Victim.py` | LassoOfTruth / Godkiller / WrathOfZeus (target reaction) | 2.400 s / 145 f | x1 (= 2.40 s in game) | full body | - | snapped rigid in the air: head thrown back, chest arched, arms flung out, legs dangling, slow strain flutter (stopped by the script) |
