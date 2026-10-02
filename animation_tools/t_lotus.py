from ivy_lib import *
import sys, json, os, numpy as np
arm = load(); setup_render(420, 460, 12)
VIEWS['zf'] = ((0, 11, 2.8), (0, 0, 2.8)); VIEWS['q3'] = ((6, 9, 3.4), (0, 0.6, 2.8)); VIEWS['sd'] = ((11, 0.5, 2.8), (0, 0.5, 2.8))
LEG = (-1.25, 0.2, 0.95, 2.2, 0.0)
cands = json.loads(sys.argv[1]); paths = []
for k, p in cands.items():
    ux, uy, uz, lx, ly, hx, hz = p
    reset_pose(arm); set_chan(arm, 'TORSO', loc=(0, -0.14, 0), rot=(0, 0, 0))
    for side, sg in (('L', -1), ('R', 1)):
        set_chan(arm, f'FK_UpperLeg.{side}', rot=(LEG[0], -sg * LEG[1], sg * LEG[2])); set_chan(arm, f'FK_LowerLeg.{side}', rot=(LEG[3], 0, 0)); set_chan(arm, f'FK_Foot.{side}', rot=(LEG[4], 0, 0))
        set_chan(arm, f'FK_UpperArm.{side}', rot=(ux, -sg * uy, sg * uz)); set_chan(arm, f'FK_LowerArm.{side}', rot=(lx, -sg * ly, 0)); set_chan(arm, f'FK_Hand.{side}', rot=(hx, 0, sg * hz))
    bpy.context.view_layer.update()
    wr = pose_mat(arm, 'FK_Hand.R').translation; kn = pose_mat(arm, 'FK_LowerLeg.R').translation
    print(k, "wrist R %s  knee R %s  dist %.2f" % (tuple(round(x, 2) for x in wr), tuple(round(x, 2) for x in kn), (wr - kn).length))
    for v in ('zf', 'q3', 'sd'):
        pth = f"{SCR}/_t_{k}_{v}.png"; render_view(pth, v); paths.append(pth)
contact_sheet(paths, 3, f"{SCR}/{sys.argv[2]}")
for pth in paths: os.remove(pth)
