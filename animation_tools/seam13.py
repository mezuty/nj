from ivy_body import *
import runpy
arm = load(); bpy.context.view_layer.objects.active = arm
runpy.run_path("../animations/Raven_Idle.py")
act = arm.animation_data.action
F=[fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
worst=0; wc=None
for fc in F:
    k0=fc.keyframe_points[0]; k1=fc.keyframe_points[-1]
    sr0=(k0.handle_right[1]-k0.co[1])/(k0.handle_right[0]-k0.co[0])
    sl1=(k1.co[1]-k1.handle_left[1])/(k1.co[0]-k1.handle_left[0])
    d=abs(sr0-sl1)
    if d>worst: worst,wc=d,(fc.data_path,fc.array_index,sr0,sl1)
print("max tangent mismatch at loop seam (units/frame):", round(worst,6), wc)
# eval-based central-difference velocity either side of seam
w2=0
for fc in F:
    a=(fc.evaluate(360)-fc.evaluate(358))/2; b=(fc.evaluate(362)-fc.evaluate(360))/2
    w2=max(w2,abs(a-b))
print("max (v_before - v_after) at seam:", round(w2,6))
