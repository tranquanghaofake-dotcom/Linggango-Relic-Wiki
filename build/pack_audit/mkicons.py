"""Resolve item icons for a list of ids: flat layer0 textures directly, block/Java-element models
into java_icons_req.json for the three.js renderer. Usage: mkicons.py ids.json"""
import json,zipfile,glob,base64,io,sys
from PIL import Image
ids=json.load(open(sys.argv[1]))
Z={}
for j in glob.glob('pack/mods/*.jar')+['mc_client.jar']:
  try:z=zipfile.ZipFile(j)
  except:continue
  for n in z.namelist():
    if n.startswith('assets/'):Z.setdefault(n,z)
rd=lambda n:Z[n].read(n) if n in Z else None
def rl(s,kind):
  ns,p=s.split(':',1) if ':' in s else ('minecraft',s);return f'assets/{ns}/{kind}/{p}'
def b64(n,crop=True):
  b=rd(n)
  if not b:return None
  im=Image.open(io.BytesIO(b)).convert('RGBA')
  if crop and im.height>im.width:im=im.crop((0,0,im.width,im.width))
  o=io.BytesIO();im.save(o,'PNG');return base64.b64encode(o.getvalue()).decode()
def model(path,d=0,tex=None):
  tex=dict(tex or {})
  b=rd(rl(path,'models')+'.json')
  if not b or d>8:return None
  m=json.loads(b);t=dict(m.get('textures') or {});t.update(tex)
  if 'elements' in m:return ('el',m['elements'],t,(m.get('display') or {}).get('gui'))
  if 'layer0' in t and not m.get('parent','').startswith('builtin'):return ('flat',t['layer0'])
  par=m.get('parent')
  if par and not par.startswith('builtin'):
    r=model(par,d+1,t)
    return r
  return None
flat={};java={};miss=[]
for iid in ids:
  ns,nm=iid.split(':')
  r=model(f'{ns}:item/{nm}') or model(f'{ns}:block/{nm}')
  if not r:miss.append(iid);continue
  if r[0]=='flat':
    v=b64(rl(r[1],'textures')+'.png')
    if v:flat[iid]=v
    else:miss.append(iid)
    continue
  T={}
  for k,v in r[2].items():
    seen=0
    while isinstance(v,str) and v.startswith('#') and seen<6:v=r[2].get(v[1:]);seen+=1
    if isinstance(v,str):
      x=b64(rl(v,'textures')+'.png',False)
      if x:T[k]=x
  if T:java[iid]={'el':r[1],'tex':T,'gui':r[3]}
  else:miss.append(iid)
json.dump(flat,open('mk_flat.json','w'));json.dump(java,open('java_icons.json','w'))
print('flat',len(flat),'java',len(java),'miss',miss)
