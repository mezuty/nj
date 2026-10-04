"""Wonder Woman - Lasso Lash (Q). Caster, upper-body only. Motion authored as smooth curves.
Game timing (server LassoLash): LashWindup plays at speed 1.2 for castTime 0.28 s;
LashCrack plays at speed 1.4 for crackTime 0.20 s -> impact, then recoilTime 0.32 s -> track:Stop(0.2).
Anim-time frames @60fps:  windup 0.28*1.2*60 = 20.2 f (clip 24 f, last 4 f = anticipation hang)
                          crack impact 0.20*1.4*60 = 16.8 -> HIT = 17, stop at (0.2+0.32)*1.4*60 = 43.7 f (clip 50 f)."""
import numpy as np
BONES = ["UpTorso","HEAD","FK_UpperArm.R","FK_LowerArm.R","FK_Hand.R","FK_UpperArm.L","FK_LowerArm.L","FK_Hand.L"]
Z3 = (0,0,0)
# --- key poses (deg, Euler XYZ) ---
C_REST=(0,0,0); C_COIL=(7,-24,-6); C_COIL2=(8,-25.5,-6.5)
RU = dict(rest=Z3, coil=(-150,0,2), coil2=(-153,0,2), over=(-140,0,2), ext=(-112,6,0), hit=(-89,8,0), follow=(-64,0,0), reel=(-14,0,3))
RL = dict(rest=Z3, coil=(-105,0,0), coil2=(-109,0,0), lag=(-97,0,0), ext=(-30,0,0), hit=(-4,0,0), follow=(-14,0,0), reel=(-74,0,0))
RH = dict(rest=Z3, coil=(-28,0,0), coil2=(-32,0,0), drag=(-40,0,0), ext=(-14,0,0), snap=(34,0,0), settle=(24,0,0), reel=(-8,0,0))
LU = dict(rest=Z3, aim=(-65.7,-12,-22), aim2=(-67,-12,-22), pull=(26,0,-8))
LL = dict(rest=Z3, aim=(-23,2.7,0), aim2=(-25,2.7,0), pull=(-61.2,6.5,0))
LH = dict(rest=Z3, aim=(0.6,0,-2.2), aim2=(4,0,-2), pull=(10.1,-1.2,6.8))
def mix(a,b,t): return tuple(x+(y-x)*t for x,y in zip(a,b))

WINDUP = dict(length=24, markers={"COIL":19}, tracks={
 "UpTorso":      [(0,C_REST),(19,C_COIL),(24,C_COIL2)],
 "FK_UpperArm.R":[(0,RU["rest"]),(18,RU["coil"]),(24,RU["coil2"])],
 "FK_LowerArm.R":[(0,RL["rest"]),(6,(-12,0,0)),(20,RL["coil"]),(24,RL["coil2"])],
 "FK_Hand.R":    [(0,RH["rest"]),(9,(8,0,0)),(21,RH["coil"]),(24,RH["coil2"])],
 "FK_UpperArm.L":[(0,LU["rest"]),(16,LU["aim"]),(24,LU["aim2"])],
 "FK_LowerArm.L":[(0,LL["rest"]),(18,LL["aim"]),(24,LL["aim2"])],
 "FK_Hand.L":    [(0,LH["rest"]),(10,(-10,0,0)),(20,LH["aim"]),(24,LH["aim2"])],
})
CRACK = dict(length=50, markers={"WHIP":0,"HIT":17,"RECOIL_END":44}, tracks={
 "UpTorso":      [(0,C_COIL2),(7,(2,-6,1)),(14,(-8,13,6.5)),(18,(-9.5,16,7.5)),(26,(-5,10,4)),(36,(-1.5,3,-1)),(50,C_REST)],
 "FK_UpperArm.R":[(0,RU["coil2"]),(8,RU["over"]),(13,RU["ext"]),(17,RU["hit"]),(23,RU["follow"]),(35,RU["reel"]),(50,RU["rest"])],
 "FK_LowerArm.R":[(0,RL["coil2"]),(11,RL["lag"]),(15,RL["ext"]),(17,RL["hit"]),(23,RL["follow"]),(35,RL["reel"]),(50,RL["rest"])],
 "FK_Hand.R":    [(0,RH["coil2"]),(12,RH["drag"]),(15,RH["ext"]),(17,RH["snap"]),(21,RH["settle"]),(36,RH["reel"]),(50,RH["rest"])],
 "FK_UpperArm.L":[(0,LU["aim2"]),(12,LU["pull"]),(30,mix(LU["pull"],Z3,0.55)),(50,Z3)],
 "FK_LowerArm.L":[(0,LL["aim2"]),(14,LL["pull"]),(32,mix(LL["pull"],Z3,0.55)),(50,Z3)],
 "FK_Hand.L":    [(0,LH["aim2"]),(16,LH["pull"]),(34,mix(LH["pull"],Z3,0.5)),(50,Z3)],
})

def hermite_track(keys, n):
    """Monotone (Fritsch-Carlson) cubic Hermite per component, zero velocity at both ends -> no overshoot, C1."""
    t = np.array([k[0] for k in keys], float); V = np.array([k[1] for k in keys], float)
    out = np.zeros((n+1, V.shape[1]))
    for c in range(V.shape[1]):
        y = V[:,c]; h = np.diff(t); d = np.diff(y)/h; m = np.zeros(len(y))
        for i in range(1, len(y)-1):
            if d[i-1]*d[i] > 0:
                w1 = 2*h[i]+h[i-1]; w2 = h[i]+2*h[i-1]
                m[i] = (w1+w2)/(w1/d[i-1]+w2/d[i])
        for f in range(n+1):
            i = min(np.searchsorted(t, f, side="right")-1, len(t)-2); i = max(i,0)
            s = (f-t[i])/h[i]; s = min(max(s,0),1)
            h00=2*s**3-3*s**2+1; h10=s**3-2*s**2+s; h01=-2*s**3+3*s**2; h11=s**3-s**2
            out[f,c] = h00*y[i]+h10*h[i]*m[i]+h01*y[i+1]+h11*h[i]*m[i+1]
    return out

def smooth(a, sigma, edge=6):
    """Gaussian smoothing, faded out over `edge` frames at both ends so end poses stay exact with zero velocity."""
    if sigma <= 0: return a
    r = int(3*sigma)+1; k = np.exp(-0.5*(np.arange(-r,r+1)/sigma)**2); k/=k.sum()
    out = a.copy()
    for c in range(a.shape[1]):
        x = a[:,c]
        pad = np.concatenate([np.full(r, x[0]), x, np.full(r, x[-1])])
        out[:,c] = np.convolve(pad, k, mode="valid")
    n = len(a); f = np.arange(n, dtype=float)
    u = np.clip(np.minimum(f, n-1-f)/edge, 0, 1); w = u**3*(u*(6*u-15)+10)
    return a + (out-a)*w[:,None]

def head_from_chest(ch, chin, nod=None):
    """Eyes stay on the target: head counter-rotates the chest yaw with a 2-frame lag, counters pitch/tilt."""
    n = len(ch); lag = lambda a, l: np.concatenate([np.repeat(a[:1], l, 0), a[:-l]])
    c2 = lag(ch, 2); c3 = lag(ch, 3)
    hd = np.zeros_like(ch)
    hd[:,1] = -0.85*c2[:,1]
    hd[:,0] = -0.55*c2[:,0] + chin
    hd[:,2] = -0.6*c3[:,2]
    if nod is not None: hd[:,0] += nod
    return hd

def build(spec, sigma=1.0):
    n = spec["length"]; dense = {}
    for b, keys in spec["tracks"].items():
        dense[b] = smooth(hermite_track(keys, n), sigma)
    f = np.arange(n+1)
    if spec is WINDUP:
        chin = -4*np.clip(f/18,0,1)**2*(3-2*np.clip(f/18,0,1))
        dense["HEAD"] = head_from_chest(dense["UpTorso"], chin)
    else:
        env = lambda a,b: np.clip((f-a)/(b-a),0,1); ss = lambda x: x*x*(3-2*x)
        chin = -4*(1-ss(env(26,50)))                     # chin down, releases in recovery
        nod = -5*np.exp(-0.5*((f-19.5)/2.6)**2)           # impact nod, lags HIT by ~2 f
        hd = smooth(head_from_chest(dense["UpTorso"], chin, nod), 1.0)
        start = build(WINDUP)["HEAD"][-1]          # crack starts exactly where the windup ends
        u0 = np.clip(f/8.0,0,1); u1 = np.clip((f-(n-8))/8.0,0,1); s5 = lambda u: u**3*(u*(6*u-15)+10)
        hd += np.outer(1-s5(u0), start-hd[0]) + np.outer(s5(u1), -hd[-1])
        dense["HEAD"] = hd
    return {b: dense[b] for b in BONES}
