import json,zipfile,glob,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import lootlib  # vanilla 1.20.1 loot rules (rolls, conditions, composite entries, nested tables; luck 0)
W=sys.argv[1];I=json.load(open(W+'/sb_idx.json'));M=json.load(open(W+'/tools2/map.json'))
LANG={}
for j in sorted(glob.glob(W+'/pack/mods/*.jar'))+[W+'/mc_client.jar']:
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
  for j in sorted(glob.glob(W+'/pack/mods/*.jar')):
    try:z=zipfile.ZipFile(j);return json.loads(z.read(f'data/{ns}/loot_tables/{p}.json')),'jar'
    except KeyError:continue
    except Exception:continue
  return None,None
def walk(tid,out):
  t,src=load(tid)
  if not t:return src
  for i,o in lootlib.chances(t,lambda n:load(n)[0]).items():
    if i not in out or o['p']>out[i]['p']:out[i]=o  # several entities or tables of one boss: the best one per item
  return src
ALT={'Yeti':['block_factorys_bosses:bosses/yeti'],'Underworld Knight':['block_factorys_bosses:bosses/underworld_knight'],'Infernal Dragon':['block_factorys_bosses:bosses/infernal_dragon'],'Cloud Golem':['legendary_monsters:entities/cloud_golem'],'Gauntlet':['bosses_of_mass_destruction:chests/gauntlet'],'Obsidilith':['bosses_of_mass_destruction:chests/obsidilith'],'Lord Pumpkinhead':['born_in_chaos_v1:entities/lord_pumpkinhead_head']}
R={}
for b,ids in M.items():
  out={};srcs=[]
  for eid in ids:
    ns,p=eid.split(':');s=walk(f'{ns}:entities/{p}',out);srcs.append(s)
  for t in ALT.get(b,[]):srcs.append(t+' '+str(walk(t,out)))
  L=[]
  for k,o in out.items():
    ns,p=k.split(':');v=o['p']
    n=LANG.get(f'item.{ns}.{p}') or LANG.get(f'block.{ns}.{p}') or p.replace('_',' ').title()
    L.append({'id':k,'n':n,'chance':(f'{v*100:.0f}%' if v>=0.01 else f'{v*100:.1f}%'),'count':lootlib.count_text(o),**({'cond':o['cond']} if o['cond'] else {})})
  R[b]={'src':srcs,'drops':L}
json.dump(R,open(W+'/sb_loot.json','w'),ensure_ascii=False,indent=0)
for b,v in R.items():print(b,v['src'],[(d['id'],d['chance']) for d in v['drops']])
