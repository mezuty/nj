from ivy_body import *
import pickle, os, sys, json
arm = load(); setup_render(300, 400, 10)
VIEWS['zf']=((0,10,3.0),(0,0,3.0)); VIEWS['sideR']=((10,2,3.2),(0,0.5,3.0)); VIEWS['sideL']=((-10,2,3.2),(0,0.5,3.0)); VIEWS['top']=((0,1,16),(0,0,3.0)); VIEWS['z3']=((6,8,3.4),(0,0,3.0))
side = sys.argv[1]
cands = json.loads(sys.argv[2])
out = sys.argv[3]
views = sys.argv[4].split(',')
paths=[]
for k,c in cands.items():
    reset_pose(arm)
    set_chan(arm, f'FK_UpperArm.{side}', rot=tuple(c[0])); set_chan(arm, f'FK_LowerArm.{side}', rot=tuple(c[1])); set_chan(arm, f'FK_Hand.{side}', rot=tuple(c[2]))
    bpy.context.view_layer.update()
    for v in views:
        p=f"{SCR}/_s_{k}_{v}.png"; render_view(p,v); paths.append(p)
    M=pose_mat(arm,f'FK_Hand.{side}').translation; E=pose_mat(arm,f'FK_LowerArm.{side}').translation
    print(k,"elbow",tuple(round(x,2) for x in E),"wrist",tuple(round(x,2) for x in M))
contact_sheet(paths, len(views), f"{SCR}/{out}")
for p in paths: os.remove(p)
