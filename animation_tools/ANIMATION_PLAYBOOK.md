# Animation Playbook — how these idle loops get made

Paste this file (or the "Prompt to give Claude" section) at the start of a new session and Claude can
reproduce the whole workflow: same quality, same checks, same delivery format.

---

## 1. Prompt to give Claude (copy/paste)

> Use the workflow in `animation_tools/ANIMATION_PLAYBOOK.md` and the tools in `animation_tools/`.
> Rig: the attached MrXen0 R15 `.blend` (60 fps, front = +Y). Make a **[CHARACTER] idle loop** for a
> **[main menu / in-game / etc.]**. Personality: **[adjectives + references]**.
> Loop length: **[e.g. 6 s]**. Full-body or upper-body-only: **[...]**. Must stay in frame: **[yes/no]**.
> Props/capes/weapons in the rig: **[none / list]**.
> Deliver ONE self-contained `.py` I can paste into Blender's Scripting tab, committed to the repo and sent as a file.
> Before sending, run every check in the playbook and tell me the numbers. Don't reuse the vocabulary of earlier characters.

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

## 4. Quality gates (all must pass before delivering)

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
| Clean re-run | `rerun_check.py` — run script twice on the original file | exactly 1 action, no leftovers |
| Key rules | only animated FK bones keyed; PROPERTIES IK_FK = 0; scene 60 fps | — |

## 5. Rig facts (MrXen0 R15 v1.2) — measured, not guessed

* Scene 60 fps. Units = studs (hip height 2.0, head top ≈ 5.3 standing). Armature origin ≈ (−0.02, −0.03, 0.11).
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

(Rejected and why: *Ivy bubbly*/*Harley bubbly* — too alike; *Catwoman crouched predator* — not feminine/feline power.)

## 7. Lessons learned from feedback

* **Personality = different movement vocabulary, not different numbers.** Same sway + hand-on-hip with new amplitudes reads as "reheated".
* Power/femininity/menace come from *posture and economy*: upright + long line (Catwoman), stillness + weight (Batman), asymmetry + irregularity (Harley).
* Always verify **contact poses with real mesh measurements** — eyeballing a gap on blocky limbs is unreliable (Batman clasp).
* Measure **clipping** when a pose pulls limbs toward the body; route transitions around the torso (elbows arc out).
* Keep **every pose reachable on this rig** — test statically first.
* Quote real numbers in the delivery message (hover height, gap, jerk, deviation) and be upfront about assumptions
  (no props, cape/glow are separate effects) and limits (checked headlessly with renders, not real-time playback).

## 8. File map (`animation_tools/`, flat so imports work)

* `ivy_lib.py` — rig loading, pose setters, analytic FK, `LegSolver`, `ArmSolver`, render + contact-sheet helpers.
* `ivy_body.py` Ivy (bubbly) · `ivy_body2.py` Ivy (seductive) · `ivy_body3.py` Harley (bubbly, rejected) ·
  `ivy_body4.py` Harley (psycho) · `ivy_body5.py` Catwoman v1 (rejected; **also holds the shared helpers `cr`, `bump`, `sstep`**) ·
  `ivy_body6.py` Catwoman · `ivy_body7.py` Batman · `ivy_body8.py` Starfire.
* `run_bodyN.py` — generates dense data (+ solves legs) · `build_finalN.py` + `templateN.py` — bakes the delivered script.
* `verifyN.py`, `seam8.py`, `rerun8.py`, `extents.py`, `gap.py`, `clipscan2.py`, `prev_act8.py` — quality gates & previews.
* `t_sweep.py`, `t_mir.py`, `gapscan.py` — pose exploration / search for contact poses. `rig_dump.py` — rig inspection.
* Delivered scripts live in `../animations/`. Working data goes to `work/` (`ANIM_WORKDIR`); put `rig.blend` there.
