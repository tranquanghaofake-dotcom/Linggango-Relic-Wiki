import json,sys,base64,io
from PIL import Image,ImageDraw
d=json.load(open(sys.argv[1]));cell=int(sys.argv[3]) if len(sys.argv)>3 else 200
ks=list(d);cols=6;rows=(len(ks)+cols-1)//cols
S=Image.new('RGBA',(cols*cell,rows*(cell+14)),(90,90,100,255));D=ImageDraw.Draw(S)
for i,k in enumerate(ks):
  im=Image.open(io.BytesIO(base64.b64decode(d[k]))).convert('RGBA').resize((cell,cell))
  x,y=(i%cols)*cell,(i//cols)*(cell+14);S.alpha_composite(im,(x,y));D.text((x+2,y+cell),k[:30],fill=(255,255,255,255))
S.save(sys.argv[2])
