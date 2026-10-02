from ivy_body8 import *
import runpy, sys, os
arm = load(); bpy.context.view_layer.objects.active = arm
runpy.run_path("../animations/Starfire_Idle.py")
frames=[int(x) for x in sys.argv[1].split(',')]; views=sys.argv[2].split(','); out=sys.argv[3]; cols=int(sys.argv[4])
setup_render(330,440,10); VIEWS["3q"]=((7,9,3.4),(0,0,2.9)); VIEWS["front"]=((0,12,3.6),(0,0,3.3)); VIEWS["side"]=((-12,0,3.6),(0,0,3.3)); VIEWS["3q"]=((7,9.5,3.8),(0,0,3.3))
paths=[]
for v in views:
    for f in frames:
        bpy.context.scene.frame_set(f); bpy.context.view_layer.update()
        p=f"{SCR}/_a_{v}_{f}.png"; render_view(p,v); paths.append(p)
contact_sheet(paths, cols, f"{SCR}/{out}")
for p in paths: os.remove(p)
