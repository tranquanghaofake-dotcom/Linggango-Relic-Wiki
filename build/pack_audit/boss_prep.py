import json,zipfile,glob,base64,io,re
from PIL import Image
B=json.load(open('boss_info.json'))
K={'iron_colossus':['the_iron_colossus'],'goblin_lord':['the_gobelin_lord'],'arion':['arion_tyrantofthe_emerald_wrath_ravager','arion_tyrant_of_the_emerald_wrath_soldat'],'eldorath':['eldoraththe_ancient_builder'],'zoranth_forgotten':['zoranththe_forgotten_one'],'elvenite_paladin':['the_elvenite_paladin'],'vaedric':['vaedricthe_fallen_wanderer'],'discord':['bringer_of_doom','bringer_of_doom_p_2','the_famine','the_chaos','the_discord'],'sanghor':['sanghor_lord_of_blood','sanghor_lord_of_bloodp_2'],'zoranth_newborn':['zoranth_newborn_of_the_zenith'],'nyxaris':['nyxaris_the_veil_of_oblivion'],'warden':['warden'],'wither':['wither'],'ender_dragon':['ender_dragon']}
Z={}
for j in glob.glob('pack/mods/*.jar')+['mc_client.jar']:
  try:z=zipfile.ZipFile(j)
  except:continue
  for n in z.namelist():
    if n.startswith('assets/'):Z.setdefault(n,z)
rd=lambda n:Z[n].read(n) if n in Z else None
def model_tex(iid,d=0):
  ns,p=iid.split(':');b=rd(f'assets/{ns}/models/item/{p}.json')
  if not b or d>5:return None
  m=json.loads(b);t=(m.get('textures') or {}).get('layer0')
  if t:
    tn,tp=(t.split(':')+[''])[:2] if ':' in t else ('minecraft',t);return f'assets/{tn}/textures/{tp}.png'
  par=m.get('parent','')
  if ':' in par and '/item/' in par and not par.startswith('minecraft:item/'): return model_tex(par.replace('/item/',':',0).replace(par.split(':')[1],par.split(':')[1].split('item/')[-1]),d+1) if False else None
  return None
def icon(iid):
  n=model_tex(iid) or (f'assets/{iid.split(":")[0]}/textures/item/{iid.split(":")[1]}.png')
  b=rd(n)
  if not b:return None
  im=Image.open(io.BytesIO(b)).convert('RGBA')
  if im.height>im.width:im=im.crop((0,0,im.width,im.width))
  o=io.BytesIO();im.save(o,'PNG');return base64.b64encode(o.getvalue()).decode()
out={};geo={};icons={}
for k,ids in K.items():
  phases=[]
  for e in ids:
    v=B.get(e)
    if not v:continue
    at=[]
    for a in v.get('attacks',[]):
      x={'n':a['name'],'d':a['desc']}
      if a.get('phase'):x['ph']=a['phase']
      if a.get('geo') and a.get('tex') and a['geo'] in Z and a['tex'] in Z:
        gid=a['geo'].rsplit('/',1)[1];x['img']=gid;geo[gid]={'geo':json.loads(rd(a['geo'])),'tex':base64.b64encode(rd(a['tex'])).decode()}
      elif a.get('proj') and a['proj'].split(':')[0]!='minecraft':
        ic=icon(a['proj'])
        if ic: icons[a['proj']]=ic;x['ic']=a['proj']
      at.append(x)
    phases.append({'e':e,'at':at,'alias':v.get('alias_of')})
  drops=[]
  for e in ids:
    for dd in B.get(e,{}).get('drops',[]):
      if dd.get('count')=='0':continue
      if any(z['id']==dd['id'] for z in drops):continue
      drops.append({k2:dd[k2] for k2 in ('id','n','chance','count','via','note') if dd.get(k2)})
      ic=icon(dd['id'])
      if ic: icons[dd['id']]=ic
  out[k]={'drops':drops,'ph':phases}
json.dump(out,open('/home/user/Linggango-Relic-Wiki/build/patches/boss_info.json','w'),ensure_ascii=False)
json.dump(geo,open('atk_geo.json','w'));json.dump(icons,open('atk_icons.json','w'))
print(len(geo),'geo',len(icons),'icons',{k:(len(v['drops']),sum(len(p['at']) for p in v['ph'])) for k,v in out.items()})
