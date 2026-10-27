"""Shortlist: effect families (frame sets) picked from the catalog, each tied to a place on the wiki.
Writes <assets>/shortlist.md, <assets>/shortlist.png (one row per family, frames at integer scale) and sets status=shortlist.
Usage: python3 -I shortlist.py <assets>"""
import sys,os,re,csv,json
from PIL import Image
A=sys.argv[1]
F=[ # (name, id regex, use on the wiki)
 ('Goety big fire',r'^goety:.*/particle/big_fire_\d+\.png','Nether Act air (envFx nether) and the forge room fire, instead of the single vanilla lava spark'),
 ('Goety soul fire drop',r'^goety:.*/particle/big_soul_fire_drop_\d+\.png','soul sand / soul soil Act air; crypt room'),
 ('Goety end fire',r'^goety:.*/particle/end_fire_\d+\.png','End Act air; Ender Dragon card on Bosses'),
 ('Goety frost',r'^goety:.*/particle/frost_\d+\.png','Ice Hermit / frost side bosses; frost damage stat lines'),
 ('Goety electric',r'^goety:.*/particle/electric(_\d+)?\.png','storm and lightning bosses; Ranged weapon hover'),
 ('Goety sparkle',r'^goety:.*/particle/sparkle_\d+\.png','tooltip particles for Epic and above; Must-Have shimmer'),
 ('Goety god rays',r'^goety:.*/particle/god_ray\d+\.png','beaten-Act check and Keeper reveal on The Path'),
 ('Goety spiral',r'^goety:.*/particle/spiral(ling)?\.png','ritual room (Mechanics) and summon pages'),
 ('Goety wraith burst',r'^goety:.*/particle/wraith_burst\d+\.png',"Goety's Bosses group cards"),
 ('Goety mine pulse',r'^goety:.*/particle/mine_pulse\d*\.png','shockwave under a Keeper card on hover'),
 ("Alex's Caves lightning",r'^alexs-caves:.*/particle/tremorzilla_lightning_\d+\.png','Toxic Caves / atomic boss side pages'),
 ("Alex's Caves tephra flame",r'^alexs-caves:.*/particle/tephra_flame_\d+\.png','volcanic bosses (Ignis, Primordial Caves)'),
 ("Alex's Caves water tremor",r'^alexs-caves:.*/particle/water_tremor_\d+\.png','ripple under drowned / ocean bosses'),
 ('BoMD disappearing swirl',r'^bosses-of-mass-destruction-forge:.*/particle/disappearing_swirl\d+\.png','teleport / vanish effect on boss cards'),
 ('BoMD down sparkle',r'^bosses-of-mass-destruction-forge:.*/particle/downsparkle_\d+\.png','loot falling into an item frame'),
 ('BoMD eye open',r'^bosses-of-mass-destruction-forge:.*/particle/eye_open_\d+\.png','"watched" mark for Keeper-gated items'),
 ('Hexerei star brush',r'^hexerei:.*/particle/star_brush_\d+\.png','twinkle for the gold Act (gilded blackstone) and Legendary'),
 ('Hexerei owl teleport',r'^hexerei:.*/particle/owl_teleport_\d+\.png','page transition puff'),
 ('Soulslike Weaponry particles',r'^mariums-soulslike-weaponry:.*/particle/(moonveil|nightfall|soul_spark|dazzling|sun)_particle?\w*\.png','Soulslike weapon pages (CC0)'),
 ('Soulslike Weaponry effect icons',r'^mariums-soulslike-weaponry:.*/mob_effect/(bleed|blight|bloodthirsty|blade_dance)\.png','stat line icons (bleed, blight…)'),
 ('Blood Magic ritual circle',r'^blood-magic:.*/textures/models/(simpletranscircle|mobsacrificeswirl)\.png','ritual room floor (Mechanics) — CC BY 4.0'),
 ('Vanilla 26.3 trial spawner detection',r'^minecraft-26\.3:.*/particle/trial_spawner_detection(_ominous)?_\d\.png','Keeper "awake" mark (newer than 1.20.1: decoration only)'),
 ('Vanilla 26.3 gust',r'^minecraft-26\.3:.*/particle/gust_\d+\.png','wind / Ranged hover (newer than 1.20.1)'),
 ('Vanilla crit',r'^minecraft-26\.3:.*/particle/(critical_hit|enchanted_hit)\.png','hit particles on the Equipment S row'),
 ('Generator slash (12 themes)',r'^lgw-fxgen:.*/slash\.png','weapon hover by damage type, replacing the single vanilla sweep'),
 ('Generator magic circle',r'^lgw-fxgen:.*/magic_circle\.png','Mage gear and ritual room'),
 ('Generator shockwave',r'^lgw-fxgen:.*/shockwave\.png','Keeper card hover'),
 ('Generator sparkle',r'^lgw-fxgen:.*/sparkle\.png','tooltip rarity particles'),
 ('Generator burst',r'^lgw-fxgen:.*/burst\.png','crit on the S row'),
 ('Generator embers',r'^lgw-fxgen:.*/embers\.png','Act air for themes without a vanilla particle (poison, frost, arcane)'),
 ('OpenGameArt 16x16 explosion (CC0)',r'^opengameart-cc0:16x16-explosion/','explosion bosses'),
 ('OpenGameArt sword slash (CC0)',r'^opengameart-cc0:pixel-art-sword-slash-effect/','Melee weapon hover'),
]
R=list(csv.DictReader(open(os.path.join(A,'catalog.csv')))); K=list(R[0].keys())
nat=lambda s:[int(t) if t.isdigit() else t for t in re.split(r'(\d+)',s)]
rows=[];md=['# Shortlist','','Effect families picked from `catalog.csv` (status `shortlist`), each with the place it would go. Nothing here is in the site yet: adding one is a separate change through `build/pack_audit/scenes.py`, and a change to the overall look needs the owner first.','',
 '| # | Family | Files | Tier · licence | Source | Use on the wiki |','|---|---|---|---|---|---|']
for i,(name,rx,use) in enumerate(F,1):
    m=[r for r in R if re.search(rx,r['id']) and not r['duplicate_of']]
    m.sort(key=lambda r:nat(r['id']))
    if not m: md.append(f'| {i} | {name} | 0 | – | – | {use} (nothing matched) |'); continue
    for r in m: r['status']='shortlist'; r['use_on_wiki']=use
    md.append(f"| {i} | {name} | {len(m)} | {m[0]['tier']} · {m[0]['license']} | {m[0]['source']} | {use} |")
    rows.append((i,name,m))
with open(os.path.join(A,'catalog.csv'),'w',newline='') as f: w=csv.DictWriter(f,fieldnames=K); w.writeheader(); w.writerows(R)
open(os.path.join(A,'shortlist.md'),'w').write('\n'.join(md)+'\n')
# preview: one row per family, up to 12 frames, height 48 px (integer scale)
H=56; out=[]
for i,name,m in rows:
    ims=[]
    for r in m[:12]:
        im=Image.open(os.path.join(A,r['out_path'])); im.seek(0); im=im.convert('RGBA')
        fw=int(r['frame_w'] or 0); n=int(r['frames'] or 1)
        if n>1 and fw and fw<im.width: im=im.crop((fw*(n//2),0,fw*(n//2+1),im.height))   # a middle frame of a side-by-side strip
        k=max(1,min(6,48//max(im.size))) if max(im.size)<=48 else 0
        im=im.resize((im.width*k,im.height*k),Image.NEAREST) if k else im.resize((max(1,im.width*48//max(im.size)),max(1,im.height*48//max(im.size))),Image.NEAREST)
        ims.append(im)
    out.append((i,name,ims))
Wd=min(1600,max(sum(x.width+6 for x in ims) for _,_,ims in out)+60); sheet=Image.new('RGBA',(Wd,H*len(out)),(30,30,34,255))
from PIL import ImageDraw
d=ImageDraw.Draw(sheet)
for j,(i,name,ims) in enumerate(out):
    y=j*H; d.text((6,y+4),str(i),fill=(200,200,200,255)); x=40
    if j%2: d.rectangle((0,y,Wd,y+H-1),fill=(36,36,41,255)); d.text((6,y+4),str(i),fill=(200,200,200,255))
    for im in ims:
        if x+im.width>Wd: break
        sheet.alpha_composite(im,(x,y+(H-im.height)//2)); x+=im.width+6
sheet.save(os.path.join(A,'shortlist.png'),optimize=True)
print(len(rows),'families,',sum(len(m) for _,_,m in rows),'files')
