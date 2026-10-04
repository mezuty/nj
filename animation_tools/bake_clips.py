"""Bake every clip of an ability module into standalone Blender scripts. usage: bake_clips.py <module>"""
import sys, os, json, importlib, numpy as np; sys.path.insert(0,'.')
import clipkit
TEMPLATE = open("template.py").read()
def keyframes(spec):
    n = spec["length"]; fr = set(range(0, n+1, 2)) | {n}
    if spec.get("strike"): fr |= set(range(spec["strike"][0], min(n, spec["strike"][1])+1))
    if spec.get("pin_vel"): fr |= {0,1,2,3}
    if spec.get("dense_keys"): fr |= set(range(spec["dense_keys"][0], spec["dense_keys"][1]+1))
    fr |= {k[0] for keys in spec["tracks"].values() for k in keys}
    return sorted(fr)
def bake(mod_name, title_prefix):
    mod = importlib.import_module(mod_name); C = mod.CLIPS
    os.makedirs("../animations", exist_ok=True); os.makedirs("work", exist_ok=True)
    for i, (name, spec) in enumerate(C.items()):
        D = clipkit.build(C, name); fr = keyframes(spec)
        keys = {b: [[f]+[round(float(v),3) for v in D[b][f]] for f in fr] for b in clipkit.BONES}
        body = "{\n" + ",\n".join(f" {b!r}: {json.dumps(k, separators=(',',':'))}" for b,k in keys.items()) + "\n}"
        notes = "#  Game: slot WW_ANIMS.%s, played at speed %.1f. Set priority = Action on export.\n" % (spec["slot"], spec["speed"])
        notes += "\n".join("#  " + l for l in spec["notes"])
        title = f"{title_prefix} - {i+1}/{len(C)} {name.upper()}  (slot WW_ANIMS.{spec['slot']})"
        src = TEMPLATE % dict(title=title, action=spec["action"], length=spec["length"], markers=spec["markers"], keys=body, notes=notes)
        path = f"../animations/{spec['action']}.py"; open(path, "w").write(src)
        np.save(f"work/{spec['action']}_dense.npy", np.stack([D[b] for b in clipkit.BONES]))
        print(name, "->", path, len(fr), "keys/bone")
if __name__ == "__main__":
    bake(sys.argv[1], sys.argv[2])
