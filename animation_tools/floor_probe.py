import bpy, runpy, sys, numpy as np
from mathutils import Matrix
bpy.ops.wm.open_mainfile(filepath="./work/rig.blend")
arm = bpy.data.objects['Roblox_R15']; bpy.context.view_layer.objects.active = arm
def lowest():
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get(); out = {}
    for n in ('LeftFoot', 'RightFoot'):
        o = bpy.data.objects[n].evaluated_get(dg); me = o.to_mesh(); M = o.matrix_world
        zs = [(M @ v.co).z for v in me.vertices]; out[n] = round(min(zs), 3); o.to_mesh_clear()
    return out
arm.animation_data.action = None
for pb in arm.pose.bones: pb.location = (0,0,0); pb.rotation_euler = (0,0,0); pb.rotation_quaternion = (1,0,0,0)
print("REST (no action):", lowest())
for script in sys.argv[1:]:
    runpy.run_path(script); bpy.context.scene.frame_set(0); print(script.split('/')[-1], "frame 0:", lowest())
