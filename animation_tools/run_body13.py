from ivy_body13 import *
import pickle, numpy as np
dense = {f: body_channels(f) for f in range(N)}
pickle.dump(dense, open(f"{SCR}/dense13.pkl", 'wb'))
res = []
for b in dense[0]:
    for ax in range(3):
        k = np.array([dense[f][b][1][ax] for f in range(N)]); kk = np.concatenate([k[-3:], k, k[:3]])
        j = np.abs(kk[3:] - 3*kk[2:-1] + 3*kk[1:-2] - kk[:-3]); res.append((j.max(), b, ax, int(j.argmax())))
res.sort(reverse=True); print("top jerk", [(round(a, 4), b, c, d) for a, b, c, d in res[:5]])
ys = [dense[f]['TORSO'][0][1] for f in range(N)]; print("hover height range (studs):", round(min(ys), 2), round(max(ys), 2))
print("wrap check: max |f359->f0 step| vs typical:", max(abs(dense[0][b][1][i] - dense[N-1][b][1][i]) for b in dense[0] for i in range(3)))
