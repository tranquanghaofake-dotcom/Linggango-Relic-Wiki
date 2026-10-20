import json,zipfile,glob,re,base64,io
from PIL import Image
miss=json.load(open('missmap.json'))
Z={}
for j in glob.glob('pack/mods/*.jar'):
  try:z=zipfile.ZipFile(j)
  except:continue
  for n in z.namelist():
    if n.startswith('assets/') and (n.endswith('.png') or n.endswith('.json')): Z.setdefault(n,z)
def rd(n): return Z[n].read(n)
flat={};geo={}
for mid in miss:
  ns,nm=mid.split(':');base=re.sub(r'_level_(one|two|three)$','',nm)
  P=[n for n in Z if n.startswith(f'assets/{ns}/textures/') and n.endswith('.png')]
  pick=None
  for suf in ('_inventory','_gui','_icon',''):
    c=[n for n in P if n.rsplit('/',1)[1]==base+suf+'.png' and '/models/' not in n and '/armor/' not in n and '/entity/' not in n and '/block/' not in n]
    if c: pick=c[0];break
  if pick:
    im=Image.open(io.BytesIO(rd(pick))).convert('RGBA')
    if im.height>im.width: im=im.crop((0,0,im.width,im.width))  # animated strip: first frame
    if im.width<=64:
      b=io.BytesIO();im.save(b,'PNG');flat[mid]=base64.b64encode(b.getvalue()).decode();continue
  G=[n for n in Z if n.startswith(f'assets/{ns}/geo') and n.endswith('.geo.json') and base in n.rsplit('/',1)[1] and 'projectile' not in n and 'entity' not in n]
  G.sort(key=lambda n:(n.rsplit('/',1)[1]!=base+'.geo.json',len(n)))
  if not G: continue
  g=G[0];stem=g.rsplit('/',1)[1][:-9]
  T=[n for n in P if n.rsplit('/',1)[1] in (stem+'.png',base+'.png',base+'_item.png') and '/entity/' not in n]
  T.sort(key=lambda n:('/models/item' not in n and '/weapons/' not in n and '/staves/' not in n and '/item/' not in n))
  if not T: continue
  geo[mid]={'geo':json.loads(rd(g)),'tex':base64.b64encode(rd(T[0])).decode(),'src':[g,T[0]]}
json.dump(flat,open('flat_icons.json','w'));json.dump(geo,open('geo_icons.json','w'))
print('flat',len(flat),'geo',len(geo),'none',[m for m in miss if m not in flat and m not in geo])
