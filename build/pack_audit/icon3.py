import json,zipfile,glob,re,base64,io
from PIL import Image
flat=json.load(open('flat_icons.json'));geo=json.load(open('geo_icons.json'))
for k in ['biomancy:caustic_gunblade','hazennstuff:draconic_splitter','hazennstuff:excalibur']: flat.pop(k,None)
miss=json.load(open('missmap.json'))
Z={}
for j in glob.glob('pack/mods/*.jar'):
  try:z=zipfile.ZipFile(j)
  except:continue
  for n in z.namelist(): Z.setdefault(n,z)
def rd(n): return Z[n].read(n) if n in Z else None
def rl(s,kind):
  ns,p=s.split(':',1) if ':' in s else ('minecraft',s)
  return f'assets/{ns}/{kind}/{p}'
def b64png(n,crop=True):
  b=rd(n)
  if not b:return None
  im=Image.open(io.BytesIO(b)).convert('RGBA')
  if crop and im.height>im.width: im=im.crop((0,0,im.width,im.width))
  o=io.BytesIO();im.save(o,'PNG');return base64.b64encode(o.getvalue()).decode()
def model(path,d=0):
  b=rd(rl(path,'models')+'.json')
  if not b or d>6:return None
  m=json.loads(b);tex=dict(m.get('textures') or {})
  if 'elements' in m: return ('el',m,tex)
  if m.get('parent') in ('builtin/entity','minecraft:builtin/entity'): return ('entity',m,tex)
  if 'layer0' in tex and not m.get('parent','').endswith('display'): return ('flat',tex['layer0'])
  if m.get('overrides'):
    r=model(m['overrides'][0]['model'],d+1)
    if r:return r
  if m.get('parent') and not m['parent'].startswith(('item/','minecraft:item/','builtin')):
    r=model(m['parent'],d+1)
    if r and r[0]=='el':
      t=dict(r[2]);t.update(tex);return ('el',r[1],t)
    if r: return r
  if 'layer0' in tex: return ('flat',tex['layer0'])
  return None
java={}
for mid in miss:
  if mid in flat or mid in geo: continue
  ns,nm=mid.split(':');r=model(f'{ns}:item/{nm}')
  if not r: print('?',mid);continue
  if r[0]=='flat':
    v=b64png(rl(r[1],'textures')+'.png')
    if v: flat[mid]=v;continue
  if r[0]=='el':
    T={}
    for k,v in r[2].items():
      while isinstance(v,str) and v.startswith('#'): v=r[2].get(v[1:])
      if v: T[k]=b64png(rl(v,'textures')+'.png',False)
    java[mid]={'el':r[1]['elements'],'tex':T,'gui':(r[1].get('display') or {}).get('gui')};continue
  print('entity',mid)
for mid in ['biomancy:caustic_gunblade','hazennstuff:draconic_splitter','hazennstuff:excalibur']:
  print(mid, mid in geo)
json.dump(flat,open('flat_icons.json','w'));json.dump(java,open('java_icons.json','w'))
print(len(flat),len(java))
