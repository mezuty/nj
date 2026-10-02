import bpy, runpy
bpy.ops.wm.open_mainfile(filepath=__import__("os").environ.get("ANIM_WORKDIR", "./work") + "/rig.blend")
arm=bpy.data.objects['Roblox_R15']; print("before:", arm.animation_data.action.name)
for i in range(2): runpy.run_path("../animations/Raven_Idle.py")
print("actions:", [a.name for a in bpy.data.actions if 'Raven' in a.name], "assigned:", arm.animation_data.action.name)
a=arm.animation_data.action
F=[fc for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
print("curves", len(F), "bones", len({fc.data_path.split('"')[1] for fc in F}), "leg/pelvis keyed:", any('LowerTorso' in fc.data_path or 'LowTorso' in fc.data_path for fc in F))
