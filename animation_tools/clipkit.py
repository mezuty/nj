"""Generic multi-clip builder: keyed pose tracks -> smooth dense curves, with additive layers, pins and a gaze-locked head."""
import numpy as np
BONES = ["UpTorso","HEAD","FK_UpperArm.R","FK_LowerArm.R","FK_Hand.R","FK_UpperArm.L","FK_LowerArm.L","FK_Hand.L"]
PIN = "PIN"
s5 = lambda u: u**3*(u*(6*u-15)+10)
def ramp(f, a, b): return s5(np.clip((np.asarray(f, float)-a)/(b-a), 0, 1))
def bump(f, c, w): return np.exp(-0.5*((np.asarray(f, float)-c)/w)**2)

def hermite_track(keys, n, v0=None):
    """Monotone (Fritsch-Carlson) cubic Hermite per component; zero end velocity unless v0 given (deg/frame at f=0)."""
    t = np.array([k[0] for k in keys], float); V = np.array([k[1] for k in keys], float)
    out = np.zeros((n+1, V.shape[1]))
    for c in range(V.shape[1]):
        y = V[:,c]; h = np.diff(t); d = np.diff(y)/h; m = np.zeros(len(y))
        for i in range(1, len(y)-1):
            if d[i-1]*d[i] > 0:
                w1 = 2*h[i]+h[i-1]; w2 = h[i]+2*h[i-1]
                m[i] = (w1+w2)/(w1/d[i-1]+w2/d[i])
        if v0 is not None:
            m[0] = v0[c] if d[0]*v0[c] > 0 else 0.0
            if d[0] != 0: m[0] = np.clip(m[0], -3*abs(d[0]), 3*abs(d[0]))
        for f in range(n+1):
            i = max(min(np.searchsorted(t, f, side="right")-1, len(t)-2), 0)
            s = min(max((f-t[i])/h[i], 0), 1)
            out[f,c] = (2*s**3-3*s**2+1)*y[i]+(s**3-2*s**2+s)*h[i]*m[i]+(-2*s**3+3*s**2)*y[i+1]+(s**3-s**2)*h[i]*m[i+1]
    return out

def smooth(a, sigma, edge=6):
    if sigma <= 0: return a
    r = int(3*sigma)+1; k = np.exp(-0.5*(np.arange(-r,r+1)/sigma)**2); k /= k.sum()
    out = a.copy()
    for c in range(a.shape[1]):
        x = a[:,c]; pad = np.concatenate([np.full(r, x[0]), x, np.full(r, x[-1])])
        out[:,c] = np.convolve(pad, k, mode="valid")
    n = len(a); f = np.arange(n, dtype=float)
    w = s5(np.clip(np.minimum(f, n-1-f)/edge, 0, 1))
    return a + (out-a)*w[:,None]

def head_from_chest(ch, chin, k=(0.55,0.85,0.6), nod=0.0):
    n = len(ch); lag = lambda a, l: np.concatenate([np.repeat(a[:1], l, 0), a[:-l]])
    c2 = lag(ch, 2); c3 = lag(ch, 3); hd = np.zeros_like(ch)
    hd[:,0] = -k[0]*c2[:,0] + chin + nod
    hd[:,1] = -k[1]*c2[:,1]
    hd[:,2] = -k[2]*c3[:,2]
    return hd

_cache = {}
def build(clips, name):
    """clips: dict of specs. Returns {bone: (n+1,3) degrees}."""
    key = (id(clips), name)
    if key in _cache: return _cache[key]
    spec = clips[name]; n = spec["length"]; f = np.arange(n+1)
    pin = None; pin_vel = None
    if spec.get("pin"):
        src, pf = spec["pin"]; P = build(clips, src)
        pin = {b: P[b][pf] for b in BONES}
        if spec.get("pin_vel"):
            ratio = clips[src]["speed"]/spec["speed"]       # same real-time velocity across clip speeds
            pin_vel = {b: (P[b][min(pf+1,len(P[b])-1)]-P[b][max(pf-1,0)])*0.5*ratio for b in BONES}
    D = {}
    for b, keys in spec["tracks"].items():
        ks = [(fr, pin[b] if (isinstance(v,str) and v == PIN) else v) for fr, v in keys]
        D[b] = hermite_track(ks, n, pin_vel[b] if (pin_vel and keys[0][1] == PIN) else None)
        D[b] = smooth(D[b], spec.get("sigma",1.0), edge=spec.get("edge",6))
    for b, fn in spec.get("add", {}).items():
        D[b] = D[b] + fn(f)
    hp = spec["head"]
    hd = smooth(head_from_chest(D["UpTorso"], hp["chin"](f), hp.get("k",(0.55,0.85,0.6)), hp.get("nod", lambda f: 0)(f)), 1.0)
    if pin is not None:                              # start exactly on the previous clip's head pose
        hd += np.outer(1-ramp(f, 0, 8), pin["HEAD"]-hd[0])
    if spec.get("end_rest"):
        hd += np.outer(ramp(f, n-8, n), -hd[-1])
    D["HEAD"] = hd
    out = {b: D[b] for b in BONES}
    _cache[key] = out
    return out
