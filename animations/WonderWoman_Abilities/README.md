# Wonder Woman ability animations (one per ability)

Seven animations, one for each ability in `WonderWomanKitEvent`. Each one covers the whole cast from first windup to recovery, and its length is the ability's client `Duration`
(0.9 / 3.4 / 3.0 / 1.0 / 2.6 / 2.5 / 4.0 s). Phases are placed on the real server timeline from `ABILITY_CONFIG` and the handlers, so the animation lines up with the effects
(rope spin, throw, reel, strikes, beam, finale...). Play each at speed 1 as a single track.

**How to use:** open your MrXen0 R15 `.blend` -> Scripting tab -> open a script -> Run Script. It removes its own previous action first, keys only the animated FK controls
(Bezier + auto-clamped, no `CYCLES`) and adds the gameplay markers below as timeline markers. Run as many as you like; each stays in the file as its own action.

**Upper-body** (`Q`, `E`, `R` - the rope abilities, she can still move while casting): only `UpTorso`, `HEAD` and the arm/hand controls are keyed. No `TORSO`, leg or foot tracks.
**Full-body** (`F`, `C`, `T`, `V` - the rooted / hovering abilities): `TORSO` and legs are keyed too. Planted-foot sections use solved legs (ankles stay put); hovering sections blend into hand-authored hanging legs.

Notes: the throw time of `E`/`R` depends on target distance in your code (0.2-0.5 s / 0.28-0.55 s); the clips use the middle of that range. Target/victim reactions are not included.

| Key | File | Length | Mode | Server timeline used | Markers (clip time) | What it shows |
|---|---|---|---|---|---|---|
| Q | `WW_LassoLash.py` | 0.90 s / 55 f | upper body | castTime 0.28 / crackTime 0.2 / recoilTime 0.32 | WINDUP_END@0.28s (f17), HIT@0.48s (f29) | Whip winds back overhead (rope trailing), sweeps forward-down and cracks at HIT with wrist lag, recoils to ready. |
| E | `WW_LassoOfTruth.py` | 3.40 s / 205 f | upper body | cast 0.45 | throw ~0.35 (distance based) | cinch 0.18 | reel 0.45 | compel 0.9 | hurl 0.42 | retract 0.32 | SPIN_END@0.45s (f27), RELEASE@0.60s (f36), CLAIM@0.98s (f59), COMPEL@1.43s (f86), HURL@2.33s (f140), SLAM@2.75s (f165) | Overhead lasso spin -> release flick (RELEASE) -> arm out as the loop flies/cinches -> hand-over-hand reel -> braced compel hold (strain) -> haul up and over the head (HURL) -> pull down at SLAM -> recover. |
| R | `WW_HestiasSnare.py` | 3.00 s / 181 f | upper body | cast 0.5 | throw ~0.4 + drop 0.14 | cinch 0.6 | bind 0.3 | lift 0.28 | slam 0.16 | retract 0.3 | SPIN_END@0.50s (f30), RELEASE@0.66s (f40), LAND@1.04s (f62), CINCH@1.04s (f62), BIND@1.64s (f98), LIFT@1.94s (f116), SLAM@2.38s (f143) | Bigger overhead spin -> sling at the ground target (RELEASE) -> pull in (cinch) -> squeeze (bind) -> LIFT overhead -> SLAM down -> recover. |
| F | `WW_BraceletClash.py` | 1.00 s / 61 f | full body | cast 0.55 -> burst -> recover 0.3 | CHARGE_END@0.55s (f33), CLASH@0.55s (f33) | Crouch and gather with the bracelets apart around the core -> clash (CLASH) -> arms blast wide in a braced stance -> settle. |
| C | `WW_Godkiller.py` | 2.60 s / 157 f | full body | draw 0.18 | dash (distance/160) | pass 0.12 | still 0.5 | 4 cuts x 0.1 | cleave+fissure 0.22 | pillar 0.45 | finish 0.15 | DRAW_END@0.18s (f11), DASH@0.18s (f11), SLASH@0.33s (f20), SHEATHE@0.45s (f27), CUT1@0.95s (f57), CUT2@1.05s (f63), CUT3@1.15s (f69), CUT4@1.25s (f75), CLEAVE_IMPACT@1.35s (f81), PILLAR@1.57s (f94) | Quick-draw lunge -> sword dash with a SLASH across the body -> stand and sheathe -> thumb flick with four sword twitches (CUT1-4) -> raise and cleave (CLEAVE_IMPACT), PILLAR, recover. |
| T | `WW_GoldenEagle.py` | 2.50 s / 151 f | full body | spread 0.4 | rise 0.25 | 10 feathers x 0.055 + big at 1.32 | fold 0.22 | descend 0.25 | SPREAD_END@0.40s (f24), RISE_END@0.65s (f39), FEATHERS@0.65s (f39), BIG@1.32s (f79), FOLD@1.95s (f117), LAND@2.42s (f145) | Crouch, arms thrown wide into the wing V (SPREAD_END), rise (legs relax into a hang), wing flaps + feather volley (FEATHERS), two-fist BIG push, wings fold (FOLD), soft landing (LAND). |
| V | `WW_WrathOfZeus.py` | 4.00 s / 241 f | full body | cast 0.35 | rise 0.35 | 3 strikes x 0.33 | torrent 1.3 | finale | descend 0.35 | CAST_END@0.35s (f21), RISE_END@0.70s (f42), STRIKE1@0.70s (f42), STRIKE2@1.03s (f62), STRIKE3@1.36s (f82), BEAM_START@1.69s (f101), FINALE@2.99s (f179), LAND@3.34s (f200) | Gather crouch, arms sweep to the sky, rise; three escalating lightning pulses (STRIKE1-3); both arms thrust at the target (BEAM_START) with a metered recoil cadence; pulled-back FINALE thrust; descend (LAND). |
