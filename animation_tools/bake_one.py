"""Bake single-animation clips (every frame keyed). usage: bake_one.py <module> <title prefix per clip as name=title ...>"""
import sys, json, importlib; sys.path.insert(0,'.')
import clipkit
mod = importlib.import_module(sys.argv[1]); TEMPLATE = open("template.py").read()
titles = dict(a.split("=",1) for a in sys.argv[2:])
for name, spec in mod.CLIPS.items():
    D = clipkit.build(mod.CLIPS, name); n = spec["length"]
    keys = {b: [[f]+[round(float(v),3) for v in D[b][f]] for f in range(n+1)] for b in clipkit.BONES}
    body = "{\n" + ",\n".join(f" {b!r}: {json.dumps(k, separators=(',',':'))}" for b,k in keys.items()) + "\n}"
    title = titles.get(name, name) + f"  (slot WW_ANIMS.{spec['slot']})"
    src = TEMPLATE % dict(title=title, action=spec["action"], length=n, markers=spec["markers"], keys=body, notes="\n".join("#  "+l for l in spec["notes"]))
    open(f"../animations/{spec['action']}.py","w").write(src); print(spec["action"], n, "frames")
