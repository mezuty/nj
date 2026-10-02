import bpy, math, numpy as np
from mathutils import Matrix, Vector, Euler, Quaternion

SCR = __import__('os').environ.get('ANIM_WORKDIR', './work')

def load():
    bpy.ops.wm.open_mainfile(filepath=f"{SCR}/rig.blend")
    arm = bpy.data.objects['Roblox_R15']
    arm.animation_data.action = None
    reset_pose(arm)
    return arm

def reset_pose(arm):
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()

def set_chan(arm, bone, loc=None, rot=None):
    pb = arm.pose.bones[bone]
    if loc is not None:
        pb.location = loc
    if rot is not None:
        if pb.rotation_mode == 'QUATERNION':
            pb.rotation_quaternion = Euler(rot, 'XYZ').to_quaternion()
        else:
            pb.rotation_euler = rot

def rest_mat(arm, name):
    return arm.data.bones[name].matrix_local.copy()

def pose_mat(arm, name):
    return arm.pose.bones[name].matrix.copy()

def basis(loc, rot):
    return Matrix.Translation(loc) @ Euler(rot, 'XYZ').to_matrix().to_4x4()

class LegSolver:
    """Analytic-FK + damped least squares foot placement for one leg."""
    def __init__(self, arm, side):
        self.arm = arm
        self.side = side
        self.names = [f'FK_UpperLeg.{side}', f'FK_LowerLeg.{side}', f'FK_Foot.{side}']
        self.R = [rest_mat(arm, n) for n in self.names]
        self.Rp = rest_mat(arm, 'LowerTorso')
        self.prior = np.array([0, 0, 0, 0, 0, 0, 0], float)

    def chain(self, Mp, q):
        # q = [ux,uy,uz, lx, fx,fy,fz]
        Bu = basis((0, 0, 0), (q[0], q[1], q[2]))
        Bl = basis((0, 0, 0), (q[3], 0, 0))
        Bf = basis((0, 0, 0), (q[4], q[5], q[6]))
        Mu = Mp @ self.Rp.inverted() @ self.R[0] @ Bu
        Ml = Mu @ self.R[0].inverted() @ self.R[1] @ Bl
        Mf = Ml @ self.R[1].inverted() @ self.R[2] @ Bf
        return Mf

    def residual(self, Mp, q, target, w_rot=0.35):
        Mf = self.chain(Mp, q)
        dp = (target.translation - Mf.translation)
        Rerr = (target.to_3x3() @ Mf.to_3x3().inverted())
        rv = Rerr.to_quaternion()
        ax = Vector((rv.x, rv.y, rv.z)) * 2.0
        if rv.w < 0: ax = -ax
        # regularisation on twist / abduction / foot yaw+roll
        reg = np.array([0.0, 0.015 * q[1], 0.015 * q[2], 0.0, 0, 0.0, 0.0])
        return np.concatenate([[dp.x, dp.y, dp.z], [ax.x * w_rot, ax.y * w_rot, ax.z * w_rot], reg[1:3]])

    def solve(self, Mp, target, q0=None, iters=40):
        q = np.array(q0 if q0 is not None else [-0.2, 0, 0, 0.4, -0.2, 0, 0], float)
        lam = 1e-3
        r = self.residual(Mp, q, target)
        cost = float(r @ r)
        for it in range(iters):
            J = np.zeros((len(r), 7))
            for i in range(7):
                dq = q.copy(); dq[i] += 1e-5
                J[:, i] = (self.residual(Mp, dq, target) - r) / 1e-5
            A = J.T @ J + lam * np.eye(7)
            step = np.linalg.solve(A, -J.T @ r)
            qn = q + step
            qn[3] = max(qn[3], 0.0)       # no knee hyper-extension
            rn = self.residual(Mp, qn, target)
            cn = float(rn @ rn)
            if cn < cost:
                q, r, cost = qn, rn, cn; lam = max(lam * 0.4, 1e-7)
                if np.abs(step).max() < 1e-7: break
            else:
                lam *= 5
        return q, cost


# ---------------------------------------------------------------- rendering
def setup_render(w=300, h=420, samples=12):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = samples
    sc.cycles.device = 'CPU'
    sc.cycles.use_denoising = False
    sc.render.resolution_x = w; sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (0.62, 0.66, 0.72, 1); bg.inputs[1].default_value = 1.4
    for o in bpy.data.objects:
        if o.name.startswith('WGT'): o.hide_render = True; o.hide_viewport = True
    return sc

VIEWS = {
    'front': ((0, 15, 3.4), (0, 0, 2.9)),
    '3q':    ((9, 11, 3.6), (0, 0, 2.9)),
    'side':  ((-15, 0, 3.4), (0, 0, 2.9)),
}

def render_view(path, view='front'):
    sc = bpy.context.scene
    cam = bpy.data.objects['PreviewCam']; sc.camera = cam
    loc, tgt = VIEWS[view]
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 50
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)

def contact_sheet(paths, cols, out):
    imgs = []
    for p in paths:
        im = bpy.data.images.load(p)
        w, h = im.size
        a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
        imgs.append(a); bpy.data.images.remove(im)
    rows = (len(imgs) + cols - 1) // cols
    H, W = imgs[0].shape[:2]
    sheet = np.ones((rows * H, cols * W, 4), np.float32)
    for i, a in enumerate(imgs):
        r, c = divmod(i, cols)
        sheet[(rows - 1 - r) * H:(rows - r) * H, c * W:(c + 1) * W] = a
    im = bpy.data.images.new('sheet', cols * W, rows * H, alpha=True)
    im.pixels = sheet.ravel().tolist()
    im.filepath_raw = out; im.file_format = 'PNG'; im.save()


class ArmSolver:
    """FK + DLS: place the wrist (FK_Hand head) at a target, soft-prior on joint angles."""
    def __init__(self, arm, side):
        self.arm = arm; self.side = side
        self.names = [f'FK_UpperArm.{side}', f'FK_LowerArm.{side}', f'FK_Hand.{side}']
        self.R = [rest_mat(arm, n) for n in self.names]
        self.Rp = rest_mat(arm, 'UpTorso')

    def chain(self, Mp, q):
        Bu = basis((0, 0, 0), (q[0], q[1], q[2]))
        Bl = basis((0, 0, 0), (q[3], q[4], 0))
        Bh = basis((0, 0, 0), (q[5], q[6], q[7]))
        Mu = Mp @ self.Rp.inverted() @ self.R[0] @ Bu
        Ml = Mu @ self.R[0].inverted() @ self.R[1] @ Bl
        Mh = Ml @ self.R[1].inverted() @ self.R[2] @ Bh
        return Mu, Ml, Mh

    def residual(self, Mp, q, tpos, prior, pw, trot=None, rw=0.3):
        Mu, Ml, Mh = self.chain(Mp, q)
        dp = tpos - Mh.translation
        res = [dp.x, dp.y, dp.z]
        if getattr(self, 'elbow_t', None) is not None:
            de = (self.elbow_t - Ml.translation) * self.elbow_w
            res += [de.x, de.y, de.z]
        if trot is not None:
            Rerr = trot @ Mh.to_3x3().inverted()
            qq = Rerr.to_quaternion()
            ax = Vector((qq.x, qq.y, qq.z)) * (2.0 if qq.w >= 0 else -2.0)
            res += [ax.x * rw, ax.y * rw, ax.z * rw]
        res += list((np.array(q) - np.array(prior)) * np.array(pw))
        if getattr(self, 'cont', None) is not None:          # temporal continuity: stay near the previous frame's solution (kills IK twist-jumps)
            res += list((np.array(q) - np.array(self.cont[0])) * np.array(self.cont[1]))
        return np.array(res)

    def solve(self, Mp, tpos, prior, pw, q0=None, trot=None, rw=0.3, iters=60):
        q = np.array(q0 if q0 is not None else prior, float)
        lam = 1e-3
        r = self.residual(Mp, q, tpos, prior, pw, trot, rw); cost = float(r @ r)
        n = len(q)
        for it in range(iters):
            J = np.zeros((len(r), n))
            for i in range(n):
                dq = q.copy(); dq[i] += 1e-5
                J[:, i] = (self.residual(Mp, dq, tpos, prior, pw, trot, rw) - r) / 1e-5
            step = np.linalg.solve(J.T @ J + lam * np.eye(n), -J.T @ r)
            qn = q + step
            rn = self.residual(Mp, qn, tpos, prior, pw, trot, rw); cn = float(rn @ rn)
            if cn < cost:
                q, r, cost = qn, rn, cn; lam = max(lam * 0.4, 1e-7)
                if np.abs(step).max() < 1e-7: break
            else:
                lam *= 5
        return q, cost
