import json,sys,re
W=sys.argv[1]
I=json.load(open(W+'/tools2/info.json'));L=json.load(open(W+'/sb_loot.json'));M=json.load(open(W+'/tools2/map.json'))
S=json.load(open(W+'/sb_list.json'))
# pictures: pack.py writes them into build/patches/side_bosses.json (renders only, 2026-10-31); kept from there
IM=json.load(open(__import__('pathlib').Path(__file__).resolve().parents[2]/'patches'/'side_bosses.json',encoding='utf-8'))
MOD={'meetyourfight':"Meet Your Fight",'soulsweapons':"Marium's Soulslike Weaponry",'legendary_monsters':'Legendary Monsters','block_factorys_bosses':"Bosses'Rise",'mowziesmobs':"Mowzie's Mobs",'irons_spellbooks':"Iron's Spells 'n Spellbooks",'cataclysm':"L_Ender's Cataclysm",'alexscaves':"Alex's Caves",'goety':'Goety','fdbosses':'Qliphoth Awakening','eeeabsmobs':"EEEAB's Mobs",'bosses_of_mass_destruction':'Bosses of Mass Destruction','terramity':'Terramity','undergarden':'The Undergarden','traveloptics':"T.O Magic 'n Extras",'born_in_chaos_v1':'Born in Chaos'}
FIX={'Malkuth':'Malkuth','Chesed':'Chesed','Geburah':'Geburah'}
FILL={'minecraft:air','minecraft:dirt','minecraft:vine','minecraft:cobblestone','minecraft:paper','minecraft:feather','minecraft:allium','minecraft:pink_tulip','minecraft:lilac','minecraft:rose_bush','minecraft:peony','minecraft:purpur_block','minecraft:obsidian','minecraft:bone','minecraft:book'}
CODE={'Corpse Warlock':[('eeeabsmobs:heart_of_pagan','Heart of Pagan','always (drop is in code, per guide)'),('eeeabsmobs:soul_summon_necklace','Summoning Soul Necklace','always (drop is in code, per guide)')]}
out={}
for b in S:
  name,act,_,note,ids=b;inf=I[name];lo=L.get(name,{'drops':[]})
  ents=M[name];ns=ents[0].split(':')[0]
  dr=[d for d in lo['drops'] if d['id'] not in FILL]
  GEM=('ruby','sapphire','topaz','onyx','iridescent_shard','diamond','gold_ingot','iridium_chunk','hermit_bean','lost_soul','arcane_essence','scroll','blank_rune')
  pri=sorted([d for d in dr if d['id'] in ids],key=lambda d:(d['id'].split(':')[1] in GEM or 'upgrade_smithing' in d['id'] or 'music_sheet' in d['id']));rest=[d for d in dr if d['id'] not in ids]
  rest.sort(key=lambda d:(d['id'].startswith('minecraft:'),'music' in d['id'],-float(d['chance'].rstrip('%'))))
  sel=(pri+rest)[:6]
  if len(sel)<2:sel=(sel+[d for d in lo['drops'] if d not in sel and d['id']!='minecraft:air'])[:max(2,len(sel))]
  sel=[{'id':d['id'],'n':('Enchanted Book' if d['id']=='minecraft:book' and ns=='meetyourfight' else re.sub(r'§.','',d['n'])),'chance':d['chance']} for d in sel]
  if not sel and name in CODE:sel=[{'id':a,'n':n,'chance':c} for a,n,c in CODE[name]]
  src=list(inf['src'])
  if ns=='fdbosses':src=['https://www.curseforge.com/minecraft/mc-mods/qliphoth-awakening','jar: fdbosses in-game boss skill descriptions (assets/fdbosses/lang/en_us.json)']
  e={'entity':ents[0] if len(ents)==1 else ents,'mod':MOD.get(ns,ns),'find':inf['find'],'drops':sel,'attacks':[{'name':a,'desc':d} for a,d in inf['attacks']],
     'img':IM.get(name,{}).get('img'),'img_src':IM.get(name,{}).get('img_src'),'sources':src}
  if lo.get('src') and any(s and 'override' in str(s) for s in lo['src']):e['drops_note']='pack override loot table (kubejs/data)'
  if not e['img']:e.pop('img');e['img_src']=None
  out[name]=e
json.dump(out,open(W+'/side_bosses.json','w'),ensure_ascii=False)
c=lambda f:sum(1 for v in out.values() if f(v))
print('total',len(out),'img',c(lambda v:v.get('img')),'drops>=2',c(lambda v:len(v['drops'])>=2),'drops0',[k for k,v in out.items() if not v['drops']],'atk>=2',c(lambda v:len(v['attacks'])>=2),'atk0',[k for k,v in out.items() if not v['attacks']])
print('noimg',[k for k,v in out.items() if not v.get('img')])
print('1drop',[k for k,v in out.items() if len(v['drops'])==1])
