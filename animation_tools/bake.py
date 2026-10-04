"""Sample dense curves -> sparse keys -> standalone Blender script."""
import sys, os, json, numpy as np; sys.path.insert(0,'.')
import ww_lasso_lash as anim
def keyframes(n, step, fast):
    fr = set(range(0, n+1, step)) | {n}
    if fast: fr |= set(range(fast[0], fast[1]+1))
    return sorted(fr)
def bake(spec, action, title, notes, path, step=2, fast=None, extra=()):
    D = anim.build(spec); n = spec["length"]; fr = keyframes(n, step, fast)
    for f in extra: fr = sorted(set(fr)|{f})
    fr = sorted(set(fr) | {k[0] for keys in spec['tracks'].values() for k in keys})
    keys = {b: [[f]+[round(float(v),3) for v in D[b][f]] for f in fr] for b in anim.BONES}
    body = "{\n" + ",\n".join(f" {b!r}: {json.dumps(k, separators=(',',':'))}" for b,k in keys.items()) + "\n}"
    src = open("template.py").read() % dict(title=title, action=action, length=n, markers=spec["markers"], keys=body, notes=notes)
    open(path,"w").write(src)
    np.save("work/"+os.path.basename(path).replace(".py","_dense.npy"), np.stack([D[b] for b in anim.BONES]))
    return fr
if __name__ == "__main__":
    import os; os.makedirs("../animations", exist_ok=True); os.makedirs("work", exist_ok=True)
    w = bake(anim.WINDUP, "WonderWoman_LassoLash_Windup", "Wonder Woman - Lasso Lash (Q) - 1/2 WINDUP  (slot WW_ANIMS.LashWindup)",
      "#  Game: played at speed 1.2 for castTime 0.28 s -> 20 anim frames; clip is 24 f so the\n"
      "#  LashCrack track (fade 0.04) always takes over during the anticipation hang (f19-24).\n"
      "#  Frame map: 0 ready -> 0-18 lasso hand rises, elbow folds back, chest winds right,\n"
      "#  left hand aims at the target -> 19 COIL (whip cocked behind the head) -> 19-24 hang.\n"
      "#  Last pose == frame 0 of the LashCrack animation.",
      "../animations/WonderWoman_LassoLash_Windup.py", step=2)
    c = bake(anim.CRACK, "WonderWoman_LassoLash_Crack", "Wonder Woman - Lasso Lash (Q) - 2/2 CRACK  (slot WW_ANIMS.LashCrack)",
      "#  Game: played at speed 1.4; crackTime 0.20 s -> HIT at f17 (rope tip reaches strikePoint),\n"
      "#  recoilTime 0.32 s -> server calls track:Stop(0.2) at ~f44; clip ends at rest on f50.\n"
      "#  Frame map: 0 coil (== Windup last pose) -> 0-8 chest unwinds -> 8-13 elbow drives over\n"
      "#  the top, hand drags behind -> 13-17 forearm + wrist whip -> 17 HIT (arm at target, wrist\n"
      "#  snapped down) -> 17-23 follow-through -> 23-35 reel the rope back in -> 35-50 settle to rest.",
      "../animations/WonderWoman_LassoLash_Crack.py", step=2, fast=(0,24))
    print("windup keys", w); print("crack keys", c)
