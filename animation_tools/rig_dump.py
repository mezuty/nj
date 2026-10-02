import bpy
bpy.ops.wm.open_mainfile(filepath=__import__("os").environ.get("ANIM_WORKDIR", "./work") + "/rig.blend")
print("VER", bpy.app.version_string)
sc=bpy.context.scene
print("scene",sc.name,"fps",sc.render.fps,"range",sc.frame_start,sc.frame_end)
for o in bpy.data.objects:
    print("OBJ",o.name,o.type,o.parent.name if o.parent else None, tuple(round(x,3) for x in o.location))
print("ACTIONS",[a.name for a in bpy.data.actions])
for o in bpy.data.objects:
    if o.type=='ARMATURE':
        print("ARM",o.name, "anim", o.animation_data.action.name if o.animation_data and o.animation_data.action else None)
        for b in o.pose.bones:
            print("  PB",b.name,"parent",b.parent.name if b.parent else None,"rotmode",b.rotation_mode,"cust",list(b.keys()), "cons",[c.type+":"+c.name for c in b.constraints], "locks", tuple(b.lock_location),tuple(b.lock_rotation))
