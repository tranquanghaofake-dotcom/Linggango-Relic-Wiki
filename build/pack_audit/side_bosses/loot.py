import json,zipfile,glob,sys,os
W=sys.argv[1];I=json.load(open(W+'/sb_idx.json'));M=json.load(open(W+'/tools2/map.json'))
LANG={}
for j in glob.glob(W+'/pack/mods/*.jar')+[W+'/mc_client.jar']:
  try:z=zipfile.ZipFile(j)
  except:continue
  for n in z.namelist():
    if n.endswith('lang/en_us.json'):
      try:LANG.update({k:v for k,v in json.loads(z.read(n).decode('utf8','ignore')).items() if k.startswith(('item.','block.'))})
      except:pass
if os.path.exists(W+'/mc_en_us.json'):
  LANG.update({k:v for k,v in json.load(open(W+'/mc_en_us.json')).items() if k.startswith(('item.','block.'))})
OV=W+'/pack/src/overrides/kubejs/data'
def load(tid):
  ns,p=tid.split(':',1);f=f'{OV}/{ns}/loot_tables/{p}.json'
  if os.path.exists(f):return json.load(open(f)),'pack override'
  for j in glob.glob(W+'/pack/mods/*.jar'):
    try:z=zipfile.ZipFile(j);return json.loads(z.read(f'data/{ns}/loot_tables/{p}.json')),'jar'
    except KeyError:continue
    except Exception:continue
  return None,None
def cch(conds):
  c=1.0;pl=False
  for x in conds or []:
    t=x.get('condition','').split(':')[-1]
    if t in('random_chance','random_chance_with_looting'):c*=x.get('chance',1)
    if t=='killed_by_player':pl=True
  return c
def walk(tid,mult,out,d=0):
  t,src=load(tid)
  if not t or d>4:return src
  for pool in t.get('pools',[]):
    r=pool.get('rolls',1)
    if isinstance(r,dict):r=r.get('max',r.get('min',1)) if 'max' in r else r.get('value',1)
    pc=cch(pool.get('conditions'))
    ents=[]
    def flat(es):
      for e in es:
        ty=e.get('type','').split(':')[-1]
        if ty in('alternatives','group','sequence'):flat(e.get('children',[]))
        else:ents.append(e)
    flat(pool.get('entries',[]))
    tw=sum(e.get('weight',1) for e in ents) or 1
    for e in ents:
      ty=e.get('type','').split(':')[-1];w=e.get('weight',1)
      p=1-(1-w/tw)**max(1,int(r)) if len(ents)>1 else 1
      p*=pc*cch(e.get('conditions'))*mult
      if ty=='item':
        nm=e['name'];out[nm]=max(out.get(nm,0),p)
      elif ty=='loot_table':walk(e['name'],p,out,d+1)
  return src
ALT={'Yeti':['block_factorys_bosses:bosses/yeti'],'Underworld Knight':['block_factorys_bosses:bosses/underworld_knight'],'Infernal Dragon':['block_factorys_bosses:bosses/infernal_dragon'],'Cloud Golem':['legendary_monsters:entities/cloud_golem'],'Gauntlet':['bosses_of_mass_destruction:chests/gauntlet'],'Obsidilith':['bosses_of_mass_destruction:chests/obsidilith'],'Lord Pumpkinhead':['born_in_chaos_v1:entities/lord_pumpkinhead_head']}
R={}
for b,ids in M.items():
  out={};srcs=[]
  for eid in ids:
    ns,p=eid.split(':');s=walk(f'{ns}:entities/{p}',1,out);srcs.append(s)
  for t in ALT.get(b,[]):srcs.append(t+' '+str(walk(t,1,out)))
  L=[]
  for k,v in out.items():
    ns,p=k.split(':')
    n=LANG.get(f'item.{ns}.{p}') or LANG.get(f'block.{ns}.{p}') or p.replace('_',' ').title()
    L.append({'id':k,'n':n,'chance':(f'{v*100:.0f}%' if v>=0.01 else f'{v*100:.1f}%')})
  R[b]={'src':srcs,'drops':L}
json.dump(R,open(W+'/sb_loot.json','w'),ensure_ascii=False,indent=0)
for b,v in R.items():print(b,v['src'],[(d['id'],d['chance']) for d in v['drops']])
