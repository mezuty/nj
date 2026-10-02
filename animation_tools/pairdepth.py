import sys
_a = list(sys.argv); sys.argv = [_a[0], _a[1], "0.07"]
exec(open('selfclip.py').read().split("parts = [")[0])
A, B = _a[2], _a[3]
for f in [int(x) for x in _a[4].split(',')]:
    reset_pose(arm)
    for b, (l, r) in dense[f].items(): set_chan(arm, b, loc=l, rot=r)
    bpy.context.view_layer.update()
    print("f%3d  %s in %s: %.3f | %s in %s: %.3f" % (f, A, B, obb_depth(verts(A), B), B, A, obb_depth(verts(B), A)))
