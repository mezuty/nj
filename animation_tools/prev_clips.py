import sys; sys.path.insert(0,'.')
import bpy
from lib import WORK, setup_render, render
action=sys.argv[1]; view=sys.argv[2]; frames=[int(x) for x in sys.argv[3].split(',')]
bpy.ops.wm.open_mainfile(filepath=WORK+"/rig.blend")
p=f"../animations/{action}.py"; exec(compile(open(p).read(),p,"exec"),{"__name__":"__main__"})
cam=setup_render(220,6)
for f in frames:
    bpy.context.scene.frame_set(f); render(f"renders/{action}_{view}_{f:02d}.png",cam,view)
