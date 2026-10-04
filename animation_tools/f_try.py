def both(ch, u, l, h=(0,0,0)):
    return {"UpTorso":ch,"FK_UpperArm.R":u,"FK_LowerArm.R":l,"FK_Hand.R":h,"FK_UpperArm.L":(u[0],-u[1],-u[2]),"FK_LowerArm.L":l,"FK_Hand.L":(h[0],-h[1],-h[2])}
POSES = {
 "wing80": both((8,0,0),(0,0,80),(0,0,0)),
 "wing80b": both((8,0,0),(15,0,80),(-15,0,0)),
 "wing60b": both((8,0,0),(20,0,60),(-10,0,0)),
 "wing100": both((8,0,0),(10,0,100),(-10,0,0)),
 "beam30": both((-6,0,0),(-85,-30,0),(-5,0,0),(-25,0,0)),
 "beam20": both((-6,0,0),(-85,-20,0),(-5,0,0),(-25,0,0)),
 "zeus_up": both((10,0,0),(-165,0,0),(-25,0,0),(-15,0,0)),
}
