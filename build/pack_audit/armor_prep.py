import json,zipfile,glob,re,base64
s=open('/home/user/Linggango-Relic-Wiki/build/src/gear_data.js').read()
i=s.index('GS=[');GS,_=json.JSONDecoder().raw_decode(s,i+3)
Z={}
for j in glob.glob('pack/mods/*.jar'):
  try:z=zipfile.ZipFile(j)
  except:continue
  for n in z.namelist():
    if n.startswith('assets/') and (n.endswith('.png') or n.endswith('.geo.json')): Z.setdefault(n,z)
b64=lambda n:base64.b64encode(Z[n].read(n)).decode()
steve=base64.b64encode(zipfile.ZipFile('mc_client.jar').read('assets/minecraft/textures/entity/player/wide/steve.png')).decode()
out={'_steve':steve};why={}
for g in GS:
  ns,stem=g['k'].split(':')
  bn=lambda n:n.rsplit('/',1)[1]
  # GeckoLib armor geo
  geos=[n for n in Z if n.startswith(f'assets/{ns}/geo/') and n.endswith('.geo.json') and stem in bn(n) and 'armor' in n]
  if not geos: geos=[n for n in Z if n.startswith(f'assets/{ns}/geo/armor') and stem in bn(n)]
  if geos:
    gn=sorted(geos,key=len)[0];st=bn(gn)[:-9]
    tx=[n for n in Z if n.startswith(f'assets/{ns}/textures/') and n.endswith('.png') and (bn(n)[:-4]==st or bn(n)[:-4] in (stem,stem+'_armor',st+'_texture') ) ]
    tx+= [n for n in Z if n.startswith(f'assets/{ns}/textures/') and '/armor' in n and stem in bn(n) and 'layer' not in n and n not in tx]
    if tx:
      out[g['k']]={'mode':'geo','geo':json.loads(Z[gn].read(gn)),'tex':b64(tx[0])};why[g['k']]=[gn,tx[0]];continue
  c=[n for n in Z if n.startswith(f'assets/{ns}/textures/') and '/armor' in n and n.endswith('.png') and re.search(r'(^|_)'+re.escape(stem)+r'(_|$)',bn(n)[:-4])]
  l1=[n for n in c if re.search(r'layer_?1|_1\.png$|outer',n)];l2=[n for n in c if re.search(r'layer_?2|_2\.png$|inner|legging',n)]
  if l1 or l2:
    a=(l1 or l2)[0];b=(l2 or l1)[0]
    out[g['k']]={'mode':'biped','l1':b64(a),'l2':b64(b)};why[g['k']]=[a,b]
json.dump(out,open('armor_in.json','w'));json.dump(why,open('armor_why.json','w'),indent=0)
print(len(out)-1,'of',len(GS),sum(1 for v in out.values() if isinstance(v,dict) and v['mode']=='geo'),'geo')
