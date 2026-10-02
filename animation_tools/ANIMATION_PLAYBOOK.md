# Animation Playbook — how these animations get made (idle loops AND actions)

The method is the same for **every** animation type: loops (idles, walks, hovers) and one-shot actions
(punches, kicks, spells, dashes, jumps, hit reactions, grabs, emotes…). Sections 1–8 are the shared core
(written around idle loops); **section 9 adds everything specific to actions**.
Paste this file (or a prompt below) at the start of a new session and Claude can reproduce the whole workflow:
same quality, same checks, same delivery format.

---

## 1. Prompt to give Claude (copy/paste)

> Use the workflow in `animation_tools/ANIMATION_PLAYBOOK.md` and the tools in `animation_tools/`.
> Rig: the attached MrXen0 R15 `.blend` (60 fps, front = +Y). Make a **[CHARACTER] idle loop** for a
> **[main menu / in-game / etc.]**. Personality: **[adjectives + references]**.
> Loop length: **[e.g. 6 s]**. Full-body or upper-body-only: **[...]**. Must stay in frame: **[yes/no]**.
> Props/capes/weapons in the rig: **[none / list]**.
> Deliver ONE self-contained `.py` I can paste into Blender's Scripting tab, committed to the repo and sent as a file.
> Before sending, run every check in the playbook and tell me the numbers. Don't reuse the vocabulary of earlier characters.

**Prompt for an ACTION (punch, spell, dash, hit reaction…):**

> Use `animation_tools/ANIMATION_PLAYBOOK.md` (core + section 9) and the tools in `animation_tools/`.
> Make a **[ACTION]** for **[CHARACTER]**. Timing from the game: **windup [x] s, strike/cast [x] s, channel [x] s (if sustained),
> recovery [x] s**, **damage/impact at [x] s**. Target: **[victim distance + height / none]**. **[Full-body | upper-body only (cast-while-moving)]**.
> Root movement allowed: **[none / lunge / dash distance]**. Ready/idle pose it must start and end on: **[describe or "the [X] idle's frame 0"]**.
> Marker names the engine needs: **[HIT, ...]**. Deliver one `.py` per variant, verify every action gate, report the numbers.

---

## 2. The method in one paragraph

**Author the motion as math, not by hand-keying.** Every animation is a Python function
`body_channels(frame) -> {bone: (location, rotation)}` built from smooth building blocks (sine layers on
integer cycles per loop, Catmull-Rom/Hermite paths, smootherstep envelopes). Because the function is smooth and
periodic, the result is smooth and loops by construction. Where physics matters (planted feet, hands meeting) a
small numerical solver finds the joint angles. Then the dense 60 fps curve is **sampled into sparse keys**,
**baked as data into a standalone Blender script**, and the *real keyed action* is re-loaded in headless Blender
and **measured and rendered** before it is delivered.

## 3. Pipeline (do these in order)

1. **Read the rig, never assume.** `rig_dump.py` lists bones/constraints/actions. Open the .blend with
   `bpy.ops.wm.open_mainfile` (forgetting this shows Blender's default cube scene). Pose bones are driven by
   `Copy Transforms` from the FK controls (`FK_*`, `TORSO`, `UpTorso`, `HEAD`) – only key those.
2. **Rig facts to verify once** (already measured, see §5): axes, rotation signs, left/right, units.
3. **Choreograph before coding.** Write a timeline in frames (events, holds, transitions) and give each character
   a *different movement vocabulary* (see §6). Pick the loop length from the beat (30 f = 1 beat @ 120 BPM, 60 f = 1 s).
4. **Test poses statically first.** `t_sweep.py` / `t_mir.py` render candidate arm poses (front / 3-quarter / top)
   so impossible poses (e.g. hand-to-mouth on blocky arms) are found *before* animating.
5. **Write `ivy_bodyN.py`** (the character's `body_channels`) from the building blocks:
   * sine layers with **integer cycles per loop** (loop is automatically seamless),
   * `cr()` periodic Catmull-Rom for head/story paths (organic, no dead stops), `bump()` for crisp accents,
   * `sstep()` envelopes to blend poses; **lag joints** (upper arm 0 f → forearm +5 f → wrist +10 f; legs lag the pelvis);
   * never leave a pure hold — add 1–2° drift / breathing so he/she is "alive in the hold".
6. **Solve what must be physical** (`LegSolver`, `ArmSolver` in `ivy_lib.py`): damped-least-squares IK
   on exact analytic FK (matches Blender to 1e-7). Feet stay planted; heel/toe-pivot lifts are target transforms.
7. **Run `run_bodyN.py`** → dense per-frame data (`work/denseN.pkl`) + prints jerk/knee ranges.
8. **Bake** with `build_finalN.py <key spacing>` into `animations/<Name>_Idle.py` (template + data, ~30–60 KB).
   Key spacing: 6 f for slow motion, 3–4 f when there are fast wiggles/bounces. Pick the *largest* spacing that keeps the
   keyed-vs-source deviation < ~1° and foot error < 0.01 stud.
9. **Verify the keyed action** (not the source data) in headless Blender — see §4.
10. **Look at renders** (contact sheets via `prev_act8.py`), fix what looks wrong, repeat 5–9.
11. **Deliver:** commit + push to the working branch, send the `.py` file, summarise in plain language with the numbers.

Setup for the toolchain (any Linux box, no GUI needed):
```
python3 -m venv venv && venv/bin/pip install bpy        # Blender as a Python module (Python 3.11, bpy 5.0.x)
export ANIM_WORKDIR=./work; cp MrXen0_R15RIG_v1.2.blend work/rig.blend
cd animation_tools && ../venv/bin/python run_body8.py && ../venv/bin/python build_final8.py 6
```
Rendering uses Cycles on CPU (no GPU/EGL in the container); 10–12 samples is enough for pose review.
Do **not** name a script `inspect.py` (shadows the stdlib and crashes bpy).

## 4. Quality gates for LOOPS (all must pass before delivering; actions: see §9)

| Gate | How | Target |
|---|---|---|
| Curve type | all keys `BEZIER`, handles `AUTO_CLAMPED`, `CYCLES` modifier on every F-curve | 100% |
| Loop seam | `seam8.py` — tangent mismatch at first/last key | 0.0 |
| Smoothness | max 3rd difference ("jerk") of every channel on the *dense* data | < ~0.02 rad (fast intentional snaps may be ~0.04) |
| Fidelity | keyed action vs dense source, every channel, every frame | < ~1.2° |
| Feet planted | foot ankle vs target over all frames (`verify*.py`) | < 0.01 stud (n/a when airborne) |
| Contact poses | `hand_gap_check.py` (e.g. knuckle crack) measures real mesh gap | 0 to −0.05 stud |
| No clipping | `torso_clip_check.py` — oriented-box test arms vs torso | worst < ~0.07 stud (arms hanging against torso graze ~0.04 by design) |
| Stays in frame | `frame_extents_check.py` — world bounding box over the loop | report width/height/hover |
| Self-intersection | `selfclip.py` (all limb pairs; threshold 0.07) — standing poses should pass; seated/folded poses: report constant hidden overlaps honestly | worst < 0.07 (standing) |
| Floor contact | `floor_check.py` — lowest foot point per frame vs floor 0.106 (toe-pointing may dip ~0.03 at the toe edge) | no sinking > 0.03 stud while grounded |
| Clean re-run | `rerun_check.py` — run script twice on the original file | exactly 1 action, no leftovers |
| Key rules | only animated FK bones keyed; PROPERTIES IK_FK = 0; scene 60 fps | — |

## 5. Rig facts (MrXen0 R15 v1.2) — measured, not guessed

* Scene 60 fps. Units = studs (hip height 2.0, head top ≈ 5.3 standing). Armature origin ≈ (−0.02, −0.03, 0.11).
  **Floor (sole of the foot mesh at rest) = world z 0.106.** (An early check used 0.21 — wrong; always measure the rest pose with `floor_probe.py`/`floor_check.py` instead of assuming.)
* **Front = +Y.** Character's **left = −X** (`.L` bones), right = +X. Camera for front view sits at +Y.
* FK arm/leg bones: local X → world −X, local Y → down, local Z → world −Y.
  * Arm **X**: − = forward, + = back. Arm **Z**: right arm + = outward (abduct), left arm − = outward.
  * Arm **Y** = twist about the bone (forearm roll / upper-arm rotation). Mirror recipe used everywhere:
    `U=(ux, −sg·uy, sg·uz)`, `L=(lx, −sg·ly)`, `H=(hx, 0, sg·hz)` with `sg = +1` right, `−1` left.
  * Leg **X**: knee flex = `FK_LowerLeg` + X. Foot X + = toes down (point). 
  * Hand **X** + = fingers curl toward the body (beckon/cup); hand mesh is a flat 1×1×0.3 plate.
* `TORSO`/`UpTorso`/`HEAD` local axes: X → +X, Y → up, Z → −Y.
  * `TORSO.location`: **+Y = up**, **−Z = forward**, +X = right. `TORSO` is **Quaternion** mode (convert the Euler).
  * Rotation: X + = lean back, Y + = turn to character's left, Z + = lean to character's left.
  * `UpTorso` = chest only; `TORSO` rotates the whole body incl. pelvis. Partial/upper-body exports must not key `TORSO`.
* Leg geometry: thigh 0.82 + shin 0.93 = 1.75 = full standing reach. **Near-straight legs are ill-conditioned**
  (tiny pelvis moves → huge knee changes → snapping). Keep a soft crouch (pelvis ≈ −0.12…−0.25) or the knee will pop.
* Feet are 1×1 and touch at default stance: any wider/narrower or yawed stance must be planned to avoid overlap.
* Blocky 1-stud arms rotate about the *inner top corner* of the shoulder: wide abduction lifts the whole block;
  hand-to-mouth is impossible, hands-to-chest-centre is possible (arms cross in front).
* Blender 5.x actions are *slotted/layered*: iterate `action.layers → strips → channelbags → fcurves`
  (the templates handle 4.x and 5.x). Insert keys with `pose_bone.keyframe_insert(...)`.

## 6. Character vocabularies used so far (so new ones don't repeat)

| Character | Feel | Signature moves |
|---|---|---|
| Poison Ivy (seductive) | slow, languid, 6 s | slow hip figure-8 weight shift, body-roll ripple, chin-down gaze, hand-at-hip anchor, come-hither curls |
| Harley Quinn (psycho) | unhinged, 6 s | hunched pigeon-toed stagger, forward/back rock, limp pendulum arms (2 s vs 3 s swing), giggle fit, creeping head tilt → snap |
| Catwoman | upright poised power, 6 s | model stance w/ pointed front toe, hip pop weight roll, long S-curve, lazy cat-swat, chin up |
| Batman | heavy, economical, 6 s | wide planted stance, deep slow breath, knuckle crack, neck roll, cold scan, heavy exhale |
| Starfire | weightless, warm, 6 s | hover 0.8 stud, trailing legs, starbolt cupped hands, joyful open-arm embrace, gentle turn |
| Mera | fluid, regal, commanding; one 6 s tide | water-body vocabulary: slow spine swell, arms that ripple like a travelling wave (shoulder → elbow +0.9 rad → wrist +1.8 rad lag), summon → conduct the current (sweeps) → crashing-wave release → ebb, hips lean against the sweep |
| Superman | noble, open, optimistic strength; 6 s | classic hero stance (fists on hips, chest broad, chin up), sky call (rise on toes, gaze up), coil → FLIGHT LAUNCH (right fist overhead, left arm streams back, lifts ~0.4 stud, feet together/toes pointed), soft landing, horizon glance |
| Raven | still, inward, mystical; 6 s | floating cross-legged lotus (~0.7 stud up), head bowed, slow turn to the camera; hands float up and swirl dark energy in opposite-phase circles, then a palms-out PUSH with recoil; sinks back to stillness |
| Wonder Woman (v2 "Amazon grace") | graceful strength, 6 s | narrow tall stagger, weight softly on one leg, S-curve (hips turned / chest counter-rotated), soft hand at waist, flowing lasso twirl (round ~0.46-stud circle, 1.5 Hz, bent elbow, wrist trails like a ribbon), wide landing arc, hair-toss, look-off |

(Rejected and why: *Wonder Woman v1* — wide stance, flared elbows, fists on hips and a puffed chest read masculine; *Ivy bubbly*/*Harley bubbly* — too alike; *Catwoman crouched predator* — not feminine/feline power.)

## 7. Lessons learned from feedback

* **Personality = different movement vocabulary, not different numbers.** Same sway + hand-on-hip with new amplitudes reads as "reheated".
* Power/femininity/menace come from *posture and economy*: upright + long line (Catwoman), stillness + weight (Batman), asymmetry + irregularity (Harley).
* **Seated/lotus on 1-stud limbs:** a workable lotus is thigh flex ≈ −1.22, twist 0.20, abduct 1.05, knee flex ≈ 2.2, foot 0 (mirrored `(tx, −sg·ty, sg·tz)`), pelvis lowered ≈ −0.14 and hovered. True crossed shins always intersect, so use the V-shaped 'butterfly lotus'. Folding legs creates *constant* overlaps with the pelvis (≈0.16 stud, inside the body) — run `selfclip.py` (all limb pairs, both directions) and `pairdepth.py` (one pair over chosen frames) and read the per-frame values: a flat value across the whole loop is an intrinsic property of the pose (report it), a value that spikes at some frames is a bug to fix.
* **Never gate motion with hard booleans** (`* (R > 0.2)`): the term jumps when the condition flips (Superman: a 0.016-stud pelvis pop → leg jerk 0.17). Use a smooth envelope (`sstep((R-0.10)/0.22)`). The dense jerk check finds these instantly.
* **Airborne / lift-off:** raise TORSO and move foot *targets* up with it (`foot_adjust` can return `dx`: feet slide together only while off the ground). Pointed toes + forward lean pull the ankles toward the hips and fold the legs — let the feet hang lower than the pelvis rise (`dz = R - 0.12·sstep(R/0.25)`) to keep flying legs long.
* **Lagged/wrapped timing:** when a joint is delayed (`f - lag`), always wrap with `% N` in a loop — an un-wrapped tail of an envelope leaks past frame 360 and makes a one-frame pop at the seam (found on Mera's left hand: jerk 0.113 → 0.002 after wrapping).
* **Gender-coding is mostly posture, not amplitude.** Wide stance, flared elbows, puffed chest, fists and hard snaps read masculine; narrower tall stagger, a hip shift with counter-rotated chest (S-curve), relaxed shoulders, rounded elbows, soft open wrists, longer limb lag and flowing arcs read graceful. Ask which feel is wanted before choosing a base stance.
* **Circular / looping gestures (lasso twirl, stirring, waving) must be measured as paths**, not eyeballed: `twirl_path.py` (closed? planar? round? radius? even speed?) and
  `twirl_scan.py` (grid-search amplitudes/phase lags for a round circle). Circles come from two joints 90° out of phase; a wrist rotation alone does not move the wrist point. A nearly straight arm makes a *flat* ellipse (both joints push the hand along the same line) — bend the elbow ~85° at the circle's centre for a round one.
  Abducting the upper arm more *increases* shoulder-into-chest clipping on blocky arms; keep circles in front/low-side and measure with `torso_clip_check`/`clipscan2.py` and `head_clear.py`.
  Fast cycles (period ≤ 30 f) with big swings need **3-frame keys**; finer (2 f) can be *worse* because auto-clamped handles over-correct — always measure keyed-vs-source.
* Always verify **contact poses with real mesh measurements** — eyeballing a gap on blocky limbs is unreliable (Batman clasp).
* Measure **clipping** when a pose pulls limbs toward the body; route transitions around the torso (elbows arc out).
* Keep **every pose reachable on this rig** — test statically first.
* **A check that fails is information, not an obstacle**: every demo-punch failure (start-velocity metric, IK twist pops, fist-offset error, overshoot past reach) pointed at a real
  cause. Fix the cause (or fix a *wrong metric* and say so), never loosen a threshold just to pass.
* Quote real numbers in the delivery message (hover height, gap, jerk, deviation) and be upfront about assumptions
  (no props, cape/glow are separate effects) and limits (checked headlessly with renders, not real-time playback).

## 9. ACTIONS (one-shot animations) — what changes vs loops

Everything in sections 2–5 still applies (motion as math → solvers for physical contact → bake → measure the real keyed action).
What changes:

| | Loop (idle/walk/hover) | One-shot action (punch/spell/dash/hit-react) |
|---|---|---|
| Timeline | seamless cycle, frame N == frame 0 | **lifecycle**: anticipation → action/impact → follow-through → recovery |
| Length | chosen from the beat | **derived from game timing**: `frames = FPS × (cast + channel + recovery)` — never guess |
| Seam | `CYCLES` modifier on every F-curve | **no** modifier. First & last pose identical (the engine's idle/ready pose), **zero velocity at both ends** so it blends |
| Sync | none | **timeline markers** at gameplay moments (`HIT`, `WINDUP_END`, `CAST`, `RELEASE`…) — `build_action.py --markers HIT=16` |
| Keys | even spacing | **dense where fast** (`--fast 8-24` = every frame in the strike), sparse where slow (`--step 2`) |
| Contact | feet planted | feet planted **with ball-of-foot pivots / steps**, fists/hands **aimed at a world target** |
| Export | usually full-body | **full-body *or* upper-body-only** (cast/shoot while walking) → `--bones upper` strips TORSO/legs/root |

**Lifecycle rules** (from the original brief):
* *Instant attack:* `Anticipation → Impact/Apex → Follow-through → Recovery (back to ready)`.
* *Channeled/sustained:* `Windup → Activation apex → **Sustained hold** → Wind-down`. The pose must be held for the **entire** gameplay duration with
  a living hold (breathing / strain / recoil on a 10–12 f cadence); only recover after it ends. Frame count must cover the whole effect.
* Anticipation is a *real* wind-back (hips/chest rotate away, weight shifts back); follow-through overshoots slightly then settles.

**Kinetic chain (what makes a punch/kick feel powerful):** motion starts in the core and ripples out with 1–3 frame offsets:
`hips (peak velocity first) → chest → shoulder → elbow → wrist/fist (last)`. Verify the order with peak-velocity frames.
Peak fist speed should land **1–3 frames before impact** and the fist should **stop at the victim** (no pass-through).

**Aimed contact via IK (not hand-posed):** define the victim contact point in world space; each frame solve the arm (`ArmSolver`) so the fist path
runs guard → target in the *current* chest frame. Three traps found while building the demo — all caught by the checks:
1. **Calibrate the fist offset on the real mesh.** The hand is a 1-stud plate, so "wrist → front face" is ~0.58, not a guess.
   `run_action_demo.py` solves once, measures the mesh at the hit frame, then re-solves with the measured offset.
2. **IK is redundant (8 joints chase a 3-D point)**, so twist joints drift and *jump* between equivalent solutions → visible pops.
   Fix: temporal-continuity term (`solver.cont = (q_prev, weights)` in `ivy_lib.ArmSolver`). Jerk dropped 0.119 → 0.027.
3. **Don't let a Hermite/ease overshoot push the fist past reach** (the victim stops it): key the arrival frame at progress 1.0 with a tiny (≤1%) compression,
   then retract. Fully-straight arms/legs are ill-conditioned — keep targets slightly inside full reach.

**Full-body vs upper-body-only:** an upper-body action must **not** key `TORSO`, legs or root (the engine's locomotion owns them): the chest carries *all*
rotation, there is no lunge, so design a shorter standoff (demo: 2.02 vs 2.15 studs). Generate the dense data with the partial flag
(`run_action_demo.py upper`), bake with `--bones upper`, and verify “no TORSO/leg/foot tracks”. Stripping tracks *after* solving a full-body version
would leave the arm aimed for a body that isn’t there — always re-solve for the partial case.

**Action quality gates** (`verify_action.py` runs these on the real keyed action, running the script twice):

| Gate | Target |
|---|---|
| Single action after 2 runs; all keys BEZIER + AUTO_CLAMPED; **no** CYCLES modifier | PASS |
| Markers present at the right frames | PASS |
| Keyed vs dense deviation | < ~1.7° (demo: 0.1–0.25°) |
| Jerk **outside** the strike window (windup-1 … impact+6) | < 0.03 (impact + hit-stop are intentional snaps) |
| First vs last pose identical; velocity 0 at both ends (end-handle slope) | < 1e-3 / < 0.002 per frame |
| Fist front face vs victim surface at HIT | within ±0.08 stud |
| Peak fist speed frame | within 4 frames before impact |
| Pass-through after impact | < 0.15 stud |
| Feet: ball-of-foot drift (pivots) | < 0.03 stud |
| Upper-body variant: no TORSO/leg/foot tracks | PASS |

**Recipes for other action types** (same tools; swap the body function):
| Type | Key ingredients |
|---|---|
| Kick | planted standing foot + hip lead; `LegSolver` aimed at a world target with the *kicking* foot as the end effector; counter-balance arms; chamber → extend → snap-back |
| Spell / projectile / beam (instant) | windup (arms gather), release at the marker, recoil, recovery; hand aimed along the cast direction (`ArmSolver`), head tracks the target |
| Channeled spell / beam | the sustained-hold rules above; frame count = full channel duration; living hold; wind-down after |
| Dash / lunge / slide | TORSO root motion (**+Y up, −Z forward**) with the extra distance baked in; legs from `LegSolver` with moving foot targets or authored trailing legs; lean into direction |
| Jump / flip / spin | airborne (no planting): authored legs, **TORSO quaternion** for rotations > 180° (builder keeps quaternion sign continuity); anticipation crouch, apex, landing absorption |
| Hit reaction / knockback | impulse on TORSO + chest, head whip with lag, arms flail through momentum, settle; start from ready pose, end on ready/idle |
| Grab / paired / execution | design around the exact standoff distance, aggressor eye-line on the victim, victim posture reflects the force; one dense file per participant, shared timing |
| Walk / run cycle | loop rules + foot contacts: planted stance phase (`LegSolver`) and swing phase (arc), arms counter-swing, pelvis bob at 2× step frequency |
| Emote / dance / taunt | loop or one-shot; same vocabulary rules as idles (give each character its own movement language) |

**Delivery for actions:** one `.py` per variant (e.g. `*_Action.py` full-body, `*_UpperBody.py`), header listing the frame map and marker names,
then the gate numbers in the message. The two demos in `../animations/` (`Demo_Punch_Action.py`, `Demo_Punch_UpperBody.py`) are **validated demos of the
pipeline with assumed timing/target**, not final fight moves — give real timing/target numbers and a ready pose and they become production moves.

## 10. File map (`animation_tools/`, flat so imports work)

* `ivy_lib.py` — rig loading, pose setters, analytic FK, `LegSolver`, `ArmSolver`, render + contact-sheet helpers.
* `ivy_body.py` Ivy (bubbly) · `ivy_body2.py` Ivy (seductive) · `ivy_body3.py` Harley (bubbly, rejected) ·
  `ivy_body4.py` Harley (psycho) · `ivy_body5.py` Catwoman v1 (rejected; **also holds the shared helpers `cr`, `bump`, `sstep`**) ·
  `ivy_body6.py` Catwoman · `ivy_body7.py` Batman · `ivy_body8.py` Starfire · `ivy_body9.py` Wonder Woman v1 (rejected: too masculine) · `ivy_body10.py` Wonder Woman v2 · `ivy_body11.py` Mera · `ivy_body12.py` Superman · `ivy_body13.py` Raven.
* `run_bodyN.py` — generates dense data (+ solves legs) · `build_finalN.py` + `templateN.py` — bakes the delivered script.
* `verifyN.py`, `seam8.py`, `rerun8.py`, `extents.py`, `gap.py`, `clipscan2.py`, `prev_act8.py` — quality gates & previews.
* `t_sweep.py`, `t_mir.py`, `gapscan.py` — pose exploration / search for contact poses. `rig_dump.py` — rig inspection.
* **Actions:** `action_demo_punch.py` (timing spec, keys, target, guard poses) + `run_action_demo.py full|upper` (solves + fist calibration) →
  `build_action.py` (generic baker: `--step --fast --markers --bones all|upper --cyclic`) + `template_action.py` →
  `verify_action.py` (action gates) · `punch_reach.py` (reach/chain-order report) · `prev_action.py` (renders with a target marker).
  `PUNCH_TY` env var sets the victim distance (used by the generator *and* the verifier).
* Delivered scripts live in `../animations/`. Working data goes to `work/` (`ANIM_WORKDIR`); put `rig.blend` there.
