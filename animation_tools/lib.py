import bpy, math, os
from mathutils import Vector, Euler, Matrix
D2R = math.pi/180
WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work")

def open_rig():
    bpy.ops.wm.open_mainfile(filepath=os.path.join(WORK, "rig.blend"))
    ob = bpy.data.objects["Roblox_R15"]
    if ob.animation_data: ob.animation_data.action = None
    reset_pose(ob)
    p = ob.pose.bones["PROPERTIES"]
    for k in ("ARM_IK_FK.L","ARM_IK_FK.R","LEG_IK_FK.L","LEG_IK_FK.R"): p[k] = 0.0
    return ob

def reset_pose(ob):
    for pb in ob.pose.bones:
        pb.location = (0,0,0); pb.rotation_euler = (0,0,0)
        pb.rotation_quaternion = (1,0,0,0); pb.scale = (1,1,1)

def set_pose(ob, ch):
    """ch: {bone: (x,y,z) degrees}"""
    for b, r in ch.items():
        ob.pose.bones[b].rotation_euler = Euler([v*D2R for v in r], 'XYZ')
    bpy.context.view_layer.update()

def mesh_world(name):
    dg = bpy.context.evaluated_depsgraph_get()
    o = bpy.data.objects[name].evaluated_get(dg)
    return [o.matrix_world @ v.co for v in o.data.vertices]

def bone_head(ob, name):
    return ob.matrix_world @ ob.pose.bones[name].head
def bone_tail(ob, name):
    return ob.matrix_world @ ob.pose.bones[name].tail

def setup_render(res=360, samples=8):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    sc.render.resolution_x = res; sc.render.resolution_y = res
    sc.render.film_transparent = False
    for o in bpy.data.objects:
        if o.name.startswith("WGT"): o.hide_render = True
    cam = bpy.data.objects.get("ReviewCam")
    if not cam:
        cd = bpy.data.cameras.new("ReviewCam"); cd.type='ORTHO'; cd.ortho_scale = 7.5
        cam = bpy.data.objects.new("ReviewCam", cd); sc.collection.objects.link(cam)
    sc.camera = cam
    return cam

VIEWS = {  # name: (location, look-at)
    "front": (Vector((0, 12, 3.2)), Vector((0, 0, 3.2))),
    "q34":   (Vector((-8, 8, 5.0)), Vector((0, 0.5, 3.2))),
    "side":  (Vector((12, 0.5, 3.2)), Vector((0, 0.5, 3.2))),
    "rq34":  (Vector((8, 8, 5.0)), Vector((0, 0.5, 3.2))),
    "top":   (Vector((0, 0.5, 14)), Vector((0, 0.5, 3.2))),
    "back":  (Vector((3, -11, 4.5)), Vector((0, 0, 3.4))),
}
def aim(cam, view):
    loc, tgt = VIEWS[view]
    cam.location = loc
    d = (tgt - loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y' if view != "top" else 'Y').to_euler()

def render(path, cam, view):
    aim(cam, view)
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
