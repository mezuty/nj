import sys, glob
from PIL import Image, ImageDraw
files = sys.argv[2:]; out = sys.argv[1]
ims = [Image.open(f).convert("RGB") for f in files]
w,h = ims[0].size; cols = min(len(ims), 6); rows = (len(ims)+cols-1)//cols
sheet = Image.new("RGB",(w*cols,h*rows),"white")
for i,(f,im) in enumerate(zip(files,ims)):
    d=ImageDraw.Draw(im); d.text((5,5),f.split('/')[-1][:-4],fill=(255,0,0))
    sheet.paste(im,((i%cols)*w,(i//cols)*h))
sheet.save(out)
