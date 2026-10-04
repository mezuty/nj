import sys, importlib; sys.path.insert(0,'.')
import numpy as np, clipkit
mod = importlib.import_module(sys.argv[1]); C = mod.CLIPS
for name, spec in C.items():
    D = clipkit.build(C, name); n = spec["length"]; win = spec.get("strike")
    print(f"== {name} ({n} f)")
    for b, a in D.items():
        r = np.radians(a); j = np.abs(np.diff(r,3,axis=0)).max(axis=1)
        jo = j if not win else np.concatenate([j[:max(0,win[0]-1)], j[win[1]:]])
        v = np.abs(np.diff(r,axis=0)).max(axis=1)
        print(f"  {b:14s} jerk_out {jo.max():.4f} jerk_all {j.max():.4f} peakvel@{int(v.argmax()):2d} ({np.degrees(v.max()):.1f} deg/f)")
    if spec.get("pin"):
        src, pf = spec["pin"]; P = clipkit.build(C, src)
        print("  pin mismatch deg", max(np.abs(P[b][pf]-D[b][0]).max() for b in D).round(4))
