import bpy, runpy, numpy as np
bpy.ops.wm.open_mainfile(filepath=__import__("os").environ.get("ANIM_WORKDIR", "./work") + "/rig.blend")
arm = bpy.data.objects['Roblox_R15']; bpy.context.view_layer.objects.active = arm
runpy.run_path("../animations/Raven_Idle.py")
names = [o.name for o in bpy.data.objects if o.type == 'MESH' and o.parent == arm]
def allverts():
    dg = bpy.context.evaluated_depsgraph_get(); out = []
    for n in names:
        o = bpy.data.objects[n].evaluated_get(dg); me = o.to_mesh(); M = o.matrix_world
        out.append(np.array([(M @ v.co)[:] for v in me.vertices])); o.to_mesh_clear()
    return np.vstack(out)
mn = np.array([1e9]*3); mx = np.array([-1e9]*3); feet_min = 1e9; feet_max = -1e9
for f in range(0, 361, 6):
    bpy.context.scene.frame_set(f); bpy.context.view_layer.update()
    V = allverts(); mn = np.minimum(mn, V.min(0)); mx = np.maximum(mx, V.max(0))
    dg = bpy.context.evaluated_depsgraph_get()
    for n in ('LeftFoot', 'RightFoot'):
        o = bpy.data.objects[n].evaluated_get(dg); me = o.to_mesh(); M = o.matrix_world
        z = min((M @ v.co).z for v in me.vertices); o.to_mesh_clear(); feet_min = min(feet_min, z); feet_max = max(feet_max, z)
print("EXTENTS x[%.2f, %.2f] (width %.2f)  y[%.2f, %.2f]  z[%.2f, %.2f] (height %.2f)" % (mn[0], mx[0], mx[0]-mn[0], mn[1], mx[1], mn[2], mx[2], mx[2]-mn[2]))
print("FLOAT: lowest foot sole over loop %.2f, highest %.2f  (rest floor = 0.106) -> feet clear the ground by %.2f to %.2f studs" % (feet_min, feet_max, feet_min - 0.106, feet_max - 0.106))
