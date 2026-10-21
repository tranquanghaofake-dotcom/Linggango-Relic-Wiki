import json,re,subprocess,os
S='.'
def MR(slug,key):
  g=json.load(open(f'gal/{slug}.json'))['gallery']
  if isinstance(key,int): return g[key]['raw_url']
  for x in g:
    if key.lower() in ((x.get('title') or '')+' '+(x.get('description') or '')).lower(): return x['raw_url']
  raise Exception(slug+key)
mw={l.split('\t')[0]:l.split('\t')[1].strip() for l in open('mg/mcw.tsv')}
def MW(p): return mw[p]
MG=lambda p:'https://www.minecraft-guides.com/wp-content/uploads/'+p
m={
"Iron Colossus (Keeper)":MR('armageddon',5),"Goblin Lord (Keeper)":MW('Dark Forest'),"Arion (Keeper)":MW('Savanna'),"Eldorath (Keeper)":MR('armageddon',8),
"Zoranth the Forgotten (Keeper)":MW('Badlands'),"Elvenite Paladin (Keeper)":MW('Jagged Peaks'),"Vaedric (Keeper)":MW('Soul Sand Valley'),
"The Calamities: Bringer, Famine, Chaos, Discord (Keeper)":MW('Basalt Deltas'),"Sanghor (Keeper)":MW('Crimson Forest'),"Zoranth Newborn (Keeper)":MW('End Highlands'),"Nyxaris (Keeper)":MW('The End'),
"Swampjaw":MR('meet-your-fight','Swampjaw'),"Bellringer":MR('meet-your-fight','Bellringer'),"Dame Fortuna":MR('meet-your-fight','Dame'),"Rosalyne":MR('meet-your-fight','Rosalyne'),
"Draugr → Night Shade":MR('mariums-soulslike-weaponry',"Old Champion"),"Moonknight":MR('mariums-soulslike-weaponry','Fallen Icon'),"Accursed Lord":MR('mariums-soulslike-weaponry','Decaying'),"Chaos Monarch":MR('mariums-soulslike-weaponry','Monarch'),
"Returning Knight":MW('Plains'),"Day Stalker":MW('Badlands'),"Night Prowler":MW('Dark Forest'),
"Frostbitten Golem":MR('legendary-monsters','Frostbitten'),"Skeletosaurus":MR('legendary-monsters','Skeletosaurus'),"Overgrown Colossus":MR('legendary-monsters','Overgrown'),"Cloud Golem":MR('legendary-monsters','Cloud Golem'),"Ancient Guardian":MR('legendary-monsters','Ancient Guardian'),"Dune Sentinel":MW('Desert'),"The Obliterator":MW('End Highlands'),
"Yeti":MR('bossesrise','Yeti'),"Underworld Knight":MR('bossesrise','Underworld'),"Infernal Dragon":MR('bossesrise','Infernal'),
"Frostmaw":MR('mowzies-mobs','Frostmaw'),"Umvuthi":MR('mowzies-mobs','Umvuthi,'),"Naga":MR('mowzies-mobs','Naga'),"Ferrous Wroughtnaut":MR('mowzies-mobs','Wroughtnaut'),
"Dead King":MW('Ancient City'),"Tyros (fire boss)":MW('Nether Wastes'),"The Nightwarden":MW('Deep Dark'),
"Netherite Monstrosity":MG('2025/08/STRUCTURE_SoulForge.png'),"Ignis":MG('2025/09/STRUCTURE_BurningArena.png'),"The Harbinger":MG('2025/08/AncientFactory.png'),"The Leviathan":MG('2025/08/STRUCTURE_SunkenCity.png'),
"Ender Guardian":MG('2025/08/RuinedCitadel.png'),"Ancient Remnant":MG('2025/07/STRUCTURE_CursedPyramid.png'),"Maledictus":MG('2025/06/Structure_FrostedPrison.png'),"Scylla":MG('2025/07/STRUCTURE_Aprocolis.png'),
"Lich":MG('2024/05/LichTower.jpg'),"Gauntlet":MG('2024/05/GauntletArena-1.jpg'),"Void Blossom":MG('2024/05/VoidBlossomCave.jpg'),"Obsidilith":MR('bosses-of-mass-destruction-forge','End Boss'),
"Luxtructosaurus":MR('alexs-caves','Primordial'),"Forsaken":MR('alexs-caves','Forlorn'),
"Vizier":MR('goety','Illager Assault'),"Apostle":MW('Nether Wastes'),"Redstone Monstrosity":MR('goety','Dark Manor'),
"Malkuth":MW('Snowy Plains'),"Chesed":MR('qliphoth-awakening','Chesed'),"Geburah":MW('Nether Wastes'),
"Corpse Warlock":MR('eeeab-s-mobs','Corpse'),"Immortal":MW('Soul Sand Valley'),"Nameless Guardian":MW('Desert'),"Realm Warden":MW('Ocean'),"Relic Annihilator":MW('Stony Peaks'),
"Super Sniffer":MR('terramity','Super Sniffer'),"Ultra Sniffer":MR('terramity','Prismatic'),"Gundalf, Circe, Merlin (Shadow Wizards)":MR('terramity','Gundalf'),"Gob, King of Gnomes":MR('terramity','Chthonic Dungeon'),"Trial Guardian":MR('terramity','Trial Spire'),"Virtue":MR('terramity','Overgrown Facility'),
"Forgotten Guardian":MR('the-undergarden','Catacombs Entrance'),"Wither":MW('Soul Sand Valley'),"Ender Dragon":MW('The End'),"Lord Pumpkinhead":MR('borninchaos','Lord Pumpkinhead'),
# missing
"Tongbi, the Sculptor":MW('Stony Peaks'),"Sandworm":MW('Desert'),"Possessed Paladin":MW('Dark Forest'),"Withered Abomination":MR('legendary-monsters','Withered'),"Lava Eater":MR('legendary-monsters','Lava eater'),"Warped Fungussus":MR('legendary-monsters','Warped Fungussus'),"Shulker Mimic":MR('legendary-monsters','Shulker Mimic'),
"Wilden Chimera":MW('Plains'),"Amethyst Crab":MW('Beach'),"Aptrgangr":MG('2025/03/FrostedPrison1.jpg'),"Kobolediator":MG('2025/08/CursedPyramid.png'),"Wadjet":MG('2025/07/STRUCTURE_CursedPyramidWM.png'),"Ender Golem":MG('2023/11/RuinedCitadelOutside.jpg'),"Ignited Berserker":MG('2024/08/BurningArena.png'),"Clawdian":MG('2024/08/SunkenCity.png'),
"Dark Doppelganger":MW('Deep Dark'),"Fairkeepers Boros & Ouros":MW('Jungle'),"Chaos Spawner":MW('Stony Peaks'),"Crone":MW('Witch Hut'),"Skull Lord":MW('Snowy Taiga'),"Minister":MW('Pillager Outpost'),"Brood Mother":MW('Dark Forest'),"Redstone Golem":MR('goety','Redstone Golem'),"Heresiarch":MW('Woodland Mansion'),
"Wither Necromancer":MW('Nether Wastes'),"Wight":MW('Snowy Taiga'),"Wildfire":MW('Basalt Deltas'),"Endersent":MW('End City'),"Ender Keeper":MW('End Highlands'),"Apollyon":MR('goety-revelation','Nether'),
"Mutant Zombie / Creeper / Skeleton":MW('Plains'),"Mutant Enderman":MW('Windswept Hills'),"Enraged Dead King":MW('Ancient City'),
"The Hollow Man":MW('Dark Forest'),"Gargamaw, the Grotesque Consumer":MW('Crimson Forest'),"Gomoria, the Fleshmonger Monk":MW('Crimson Forest'),"Valamon, the Corpse Butcher":MW('Badlands'),"Morphegor, the Splitting Tyrant":MW('Swamp'),"Baal, the Motionless Calamity":MW('Basalt Deltas'),
"Dead Horn":MW('Soul Sand Valley'),"Void Worm":MW('End Highlands'),"Cruncher":MR('species','Cruncher'),"Archmages (Adam, Cade, Cameron, Josh, Matthew, Nick, Ryan)":MW('Plains'),"Mahoraga":MW('Stony Peaks'),
"Masticator":MR('the-undergarden','Smogstem'),"Stalker":MR('deeperdarker','Ancient Temple'),"The Black Charro":MR('myths-and-legends','Umbral Wasteland'),"Warborn Aegis":MW('Jagged Peaks'),"Elder Guardian":MW('Ocean Monument'),"Warden":MW('Ancient City'),
}
B=[r[0] for r in json.load(open('bossr.json'))]; A=[x['name'] for x in json.load(open('boss_audit.json'))['missing']]
print('unmapped',[n for n in B+A if n not in m],'extra',[n for n in m if n not in B+A])
os.makedirs('boss_bg',exist_ok=True);out={}
for n in B+A:
  u=m.get(n)
  if not u: continue
  ext=re.search(r'\.(png|jpe?g|webp)',u.split('?')[0].lower()).group(1).replace('jpeg','jpg')
  f='boss_bg/'+re.sub(r'[^A-Za-z0-9]+','_',n).strip('_')[:60]+'.'+ext
  if not os.path.exists(f) or os.path.getsize(f)<5000:
    subprocess.run(['curl','-sS','-L','-A','Mozilla/5.0','-o',f,u])
  ok=os.path.exists(f) and os.path.getsize(f)>5000
  if ok: out[n]={'file':f,'url':u.split('?')[0] if 'minecraft.wiki' in u else u}
  else: print('FAIL',n,u)
json.dump(out,open('boss_bg.json','w'),indent=1,ensure_ascii=False);print(len(out),len(B),len(A))
