import json,zipfile,glob,sys,base64,io
from PIL import Image
W=sys.argv[1]
S={"Draugr → Night Shade":("soulsweapons/geo/entity/draugr_boss.geo.json","soulsweapons/textures/entity/draugr_boss.png"),
"Umvuthi":("mowziesmobs/geo/umvuthi.geo.json","mowziesmobs/textures/entity/umvuthi.png"),
"Dead King":("irons_spellbooks/geo/dead_king.geo.json","irons_spellbooks/textures/entity/dead_king/dead_king.png"),
"Returning Knight":("soulsweapons/geo/entity/returning_knight.geo.json","soulsweapons/textures/entity/returning_knight.png"),
"Malkuth":("fdbosses/bedrock/models/malkuth.geo.json","fdbosses/textures/entities/malkuth/malkuth.png"),
"Lich":("bosses_of_mass_destruction/geo/lich.geo.json","bosses_of_mass_destruction/textures/entity/lich.png"),
"Super Sniffer":("terramity/geo/super_sniffer.geo.json","terramity/textures/entities/super_sniffer_base.png"),
"Gundalf, Circe, Merlin (Shadow Wizards)":("terramity/geo/gundalf.geo.json","terramity/textures/entities/gundalf.png"),
"Gauntlet":("bosses_of_mass_destruction/geo/gauntlet.geo.json","bosses_of_mass_destruction/textures/entity/gauntlet.png"),
"Obsidilith":("bosses_of_mass_destruction/geo/obsidilith.geo.json","bosses_of_mass_destruction/textures/entity/obsidilith.png"),
"Void Blossom":("bosses_of_mass_destruction/geo/void_blossom.geo.json","bosses_of_mass_destruction/textures/entity/void_blossom.png"),
"Chesed":("fdbosses/bedrock/models/chesed.geo.json","fdbosses/textures/entities/chesed.png"),
"Moonknight":("soulsweapons/geo/entity/moonknight.geo.json","soulsweapons/textures/entity/moonknight/moonknight_phase_1.png"),
"Accursed Lord":("soulsweapons/geo/entity/accursed_lord.geo.json","soulsweapons/textures/entity/accursed_lord.png"),
"Tyros (fire boss)":("irons_spellbooks/geo/tyros.geo.json","irons_spellbooks/textures/entity/fire_boss/tyros.png"),
"Gob, King of Gnomes":("terramity/geo/gob.geo.json","terramity/textures/entities/gob.png"),
"Trial Guardian":("terramity/geo/trial_guardian.geo.json","terramity/textures/entities/trial_guardian.png"),
"Geburah":("fdbosses/bedrock/models/geburah.geo.json","fdbosses/textures/entities/geburah/geburah.png"),
"Day Stalker":("soulsweapons/geo/entity/day_stalker.geo.json","soulsweapons/textures/entity/day_stalker.png"),
"Night Prowler":("soulsweapons/geo/entity/night_prowler.geo.json","soulsweapons/textures/entity/night_prowler.png"),
"Chaos Monarch":("soulsweapons/geo/entity/chaos_monarch.geo.json","soulsweapons/textures/entity/chaos_monarch.png"),
"The Nightwarden":("traveloptics/geo/nightwarden.geo.json","traveloptics/textures/models/entity/nightwarden/nightwarden.png"),
"Virtue":("terramity/geo/virtue.geo.json","terramity/textures/entities/virtue.png"),
"Ultra Sniffer":("terramity/geo/ultra_sniffer.geo.json","terramity/textures/entities/ultra_sniffer_ultra.png"),
"Lord Pumpkinhead":("born_in_chaos_v1/geo/lordofpumpkins.geo.json","born_in_chaos_v1/textures/entities/lordofpumpkins.png")}
Z={}
for j in glob.glob(W+'/pack/mods/*.jar'):
  try:z=zipfile.ZipFile(j)
  except:continue
  for n in z.namelist():
    if n.startswith('assets/'):Z.setdefault(n,z)
out={}
for k,(g,t) in S.items():
  g='assets/'+g;t='assets/'+t
  if g not in Z or t not in Z:print('MISS',k,g in Z,t in Z);continue
  geo=json.loads(Z[g].read(g));im=Image.open(io.BytesIO(Z[t].read(t)));d=geo.get('minecraft:geometry',[{}])[0].get('description',{})
  print(k,im.size,d.get('texture_width'),d.get('texture_height'))
  out[k]={'geo':geo,'tex':base64.b64encode(Z[t].read(t)).decode()}
json.dump(out,open(W+'/boss_geo_in.json','w'))
