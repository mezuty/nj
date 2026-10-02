"""Lowest point of each foot mesh per frame vs the floor (rest floor 0.106).  usage: floor_check.py ../animations/X.py"""
import bpy, runpy, sys, numpy as np
bpy.ops.wm.open_mainfile(filepath=__import__("os").environ.get("ANIM_WORKDIR", "./work") + "/rig.blend")
arm = bpy.data.objects['Roblox_R15']; bpy.context.view_layer.objects.active = arm
runpy.run_path(sys.argv[1]); scene = bpy.context.scene
rows = []
for f in range(0, scene.frame_end + 1, 3):
    scene.frame_set(f); bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get(); lo = 9
    for n in ('LeftFoot', 'RightFoot'):
        o = bpy.data.objects[n].evaluated_get(dg); me = o.to_mesh(); M = o.matrix_world
        lo = min(lo, min((M @ v.co).z for v in me.vertices)); o.to_mesh_clear()
    rows.append((f, lo))
worst = min(rows, key=lambda r: r[1])
print("FLOOR: lowest foot point %.3f at frame %d  (floor = 0.106 -> %+.3f studs %s the floor)" % (worst[1], worst[0], worst[1] - 0.106, "below" if worst[1] < 0.106 - 0.005 else "above"))
bad = [(f, round(z - 0.106, 3)) for f, z in rows if z < 0.106 - 0.02]
print("frames more than 0.02 below the floor:", bad[:25], "..." if len(bad) > 25 else "")
