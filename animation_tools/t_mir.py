from ivy_lib import *
import sys, json, os
arm = load(); setup_render(330, 440, 10)
VIEWS['zf']=((0,10,3.0),(0,0,3.0)); VIEWS['z3']=((6,8,3.4),(0,0,3.0)); VIEWS['top']=((0,1,16),(0,0,3.0))
cands=json.loads(sys.argv[1]); paths=[]
for k,p in cands.items():
    ux,uy,uz,lx,ly,hx=p[:6]; hz=p[6] if len(p)>6 else 0.0
    reset_pose(arm)
    for side,sg in (('L',-1),('R',1)):
        set_chan(arm,f'FK_UpperArm.{side}',rot=(ux,-sg*uy,sg*uz)); set_chan(arm,f'FK_LowerArm.{side}',rot=(lx,-sg*ly,0)); set_chan(arm,f'FK_Hand.{side}',rot=(hx,0,sg*hz))
    bpy.context.view_layer.update()
    wl=pose_mat(arm,'FK_Hand.L').translation; wr=pose_mat(arm,'FK_Hand.R').translation
    print(k,"wristR",tuple(round(x,2) for x in wr),"wrist-sep",round(abs(wr.x-wl.x),2))
    for v in ('zf','z3','top'):
        pth=f"{SCR}/_m_{k}_{v}.png"; render_view(pth,v); paths.append(pth)
contact_sheet(paths,3,f"{SCR}/{sys.argv[2]}")
for pth in paths: os.remove(pth)
