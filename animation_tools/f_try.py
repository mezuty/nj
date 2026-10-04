def M(u,l,h): return (u,l,h)
def both(ch, u, l, h): 
    return {"UpTorso":ch,"FK_UpperArm.R":u,"FK_LowerArm.R":l,"FK_Hand.R":h,
            "FK_UpperArm.L":(u[0],-u[1],-u[2]),"FK_LowerArm.L":l,"FK_Hand.L":(h[0],-h[1],-h[2])}
POSES = {
 "guard": both((-3,0,0),(-45,0,3),(-100,0,0),(-5,0,10)),
 "open":  both((10,0,0),(-10,0,75),(-80,0,0),(10,0,0)),
 "open60":both((10,0,0),(-15,0,60),(-85,0,0),(10,0,0)),
 "clash": both((-10,0,0),(-55,-8,3),(-85,0,0),(0,0,22)),
 "mid":   both((0,0,0),(-32,-4,38),(-82,0,0),(5,0,12)),
 "snare_spin": {"UpTorso":(2,6,6),"FK_UpperArm.R":(-160,0,0),"FK_LowerArm.R":(-10,0,0),"FK_UpperArm.L":(-50,0,-6),"FK_LowerArm.L":(-8,0,0),"FK_Hand.L":(10,0,0)},
 "snare_cinch": {"UpTorso":(12,-8,0),"FK_UpperArm.R":(15,0,0),"FK_LowerArm.R":(-75,0,0),"FK_UpperArm.L":(12,0,0),"FK_LowerArm.L":(-70,0,0)},
}
