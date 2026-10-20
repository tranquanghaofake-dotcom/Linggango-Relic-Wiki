import json,sys,base64,io,glob,os
from PIL import Image
W=sys.argv[1]
A=json.load(open(W+'/boss_geo_out.json'));B=json.load(open(W+'/boss_geo_out_b.json'))
useA={'Gundalf, Circe, Merlin (Shadow Wizards)','Chesed'}
def fit(im):
  im=im.convert('RGBA');bb=im.getbbox()
  if bb:im=im.crop(bb)
  s=max(im.size);c=Image.new('RGBA',(s,s),(0,0,0,0));c.paste(im,((s-im.width)//2,(s-im.height)//2));return c.resize((256,256),Image.LANCZOS)
def enc(im):
  o=io.BytesIO();im.save(o,'WEBP',quality=88,method=6);return base64.b64encode(o.getvalue()).decode()
I={};S={}
for k in B:
  im=Image.open(io.BytesIO(base64.b64decode((A if k in useA else B)[k])));I[k]=enc(fit(im));S[k]='render'
D=json.load(open(W+'/wimg/dl.json'))
D['Luxtructosaurus']={'file':W+'/wimg/Luxtructosaurus.webp','page':'https://alexscaves.wiki.gg/wiki/File:Luxtructosaurus.webp','url':'https://alexscaves.wiki.gg/images/Luxtructosaurus.webp'}
for k,v in D.items():
  im=Image.open(v['file']);im.seek(0);I[k]=enc(fit(im.convert('RGBA')));S[k]=v['url'].split('?')[0] if 'wiki.gg' in v['url'] else v['url']
json.dump({'img':I,'src':S},open(W+'/sb_imgs.json','w'))
print(len(I))
