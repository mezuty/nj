import sys, json, numpy as np; sys.path.insert(0,'.')
import clipkit, ww_single
TEMPLATE = open("template.py").read()
JOBS = [
 ("WonderWoman_LassoLash", "Wonder Woman - Lasso Lash (Q) - SINGLE ANIMATION  (slot WW_ANIMS.LassoLash)", ww_single.lasso_lash,
  ["Game: ONE track, playAnim(..., WW_ANIMS.LassoLash, 0.05, 1) at cast start (speed 1). Priority = Action.",
   "0-13 lasso hand rises and folds back, chest winds, left hand aims -> 13-17 coil hang ->",
   "17 crack begins (castTime 0.28 s) -> 29 HIT (crackTime 0.20 s) -> follow-through -> reel in ->",
   "48 server stops the track (recoil 0.32 s) -> settles to rest by 53."]),
 ("WonderWoman_LassoOfTruth", "Wonder Woman - Lasso of Truth (E) - SINGLE ANIMATION  (slot WW_ANIMS.LassoOfTruth)", ww_single.lasso_of_truth,
  ["Game: ONE track, playAnim(..., WW_ANIMS.LassoOfTruth, 0.08, 1) at cast start (speed 1). Priority = Action.",
   "Needs the fixed throw time (throwTime = 0.35) so the clip and the server stay in sync.",
   "0-27 twirl overhead (castTime 0.45) -> 27-31 cast, RELEASE 31 -> grip on the rope, loop lands 48,",
   "cinch ends 59 -> 59-86 big haul (reel 0.45) -> 86-140 compel hold, strain tug on each tick 104/122/140 ->",
   "140-165 heave overhead and fold forward, SLAM 165 (hurl 0.42) -> rise and reel in -> server stop ~184 -> rest 205."]),
]
for action, title, fn, notes in JOBS:
    D, markers = fn(); n = len(D["UpTorso"])-1
    keys = {b: [[f]+[round(float(v),3) for v in D[b][f]] for f in range(n+1)] for b in clipkit.BONES}
    body = "{\n" + ",\n".join(f" {b!r}: {json.dumps(k, separators=(',',':'))}" for b,k in keys.items()) + "\n}"
    src = TEMPLATE % dict(title=title, action=action, length=n, markers=markers, keys=body, notes="\n".join("#  "+l for l in notes))
    open(f"../animations/{action}.py","w").write(src); print(action, n, "frames")
