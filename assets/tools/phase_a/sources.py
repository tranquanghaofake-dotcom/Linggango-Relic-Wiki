"""Phase A of PROMPT_ASSETS.md: one row per project of Linggango V6.6.6hf (+ the pack's own overrides) with licence evidence and a tier.
Usage: python3 -I sources.py <work dir with scan.json> <out csv>"""
import json,sys,csv
P,OUT=sys.argv[1],sys.argv[2]; d=json.load(open(P+'/scan.json'))
OPEN={'MIT','LGPL','GPL','Apache','BSD','MPL','CC0','CC-BY','OSS-other'}
# checked by hand (repo LICENSE / README at HEAD, 2026-10-27); key = CurseForge title prefix
MANUAL={
 "Create":("B","high","Create Team licence: code MIT-like, assets All Rights Reserved (repo LICENSE.md 'Assets License (All Rights Reserved)')"),
 "Saint's Dragons":("B","high","dual licence: code MIT, art & audio All Rights Reserved (repo LICENSE.md part 2)"),
 "Starcatcher":("B","high","README: every asset All Rights Reserved except the main fishing rod (custom licence)"),
 "Opposing Force":("B","high","repo LICENSE: textures/ and sounds/ All Rights Reserved, the rest MIT"),
 "Goety: Awaken":("B","high","mods.toml: 'Code: LGPL-2.1 | Assets: ARR'"),
 "Celestisynth: Wishes":("B","medium","1.3.4 (pack) was released under MIT (jar mods.toml; repo LICENSE MIT at d1d6103, 2024-10-05); relicensed All Rights Reserved on 2026-08-31 (ab4f16a), assets 'may not be extracted without permission'. Ask before use"),
 "Terra Curio":("X","high","modid confluence: Terraria accessories (Cell Phone, Ankh Shield, Aglet…) — Re-Logic's art, not the mod author's to license"),
 "Terra GUI":("X","high","Terraria GUI resource pack — Re-Logic's art"),
 "Fresh mowzie's mobs":("B","medium","MIT on Modrinth, but retextures Mowzie's Mobs (custom licence): the pack author cannot license Mowzie's part"),
 "Sweety's Items":("A","medium","GPL-3.0; retextures of Alex's Mobs items (LGPL-3.0 per its mods.toml)"),
 "Alex's Caves":("A","medium","LGPL-3.0 declared in mods.toml and Modrinth; repo has no LICENSE file"),
 "Alex's Mobs":("A","medium","LGPL-3.0 in mods.toml, GPL-3.0 on Modrinth (comply with GPL-3.0); repo has no LICENSE file"),
 "Hexerei":("A","medium","MIT in mods.toml, LGPL-3.0 on Modrinth (comply with LGPL-3.0); repo has no LICENSE file"),
 "Brutality - A Terramity Addon":("A","low","MIT in mods.toml only (no repo); check that no Terramity (ARR) or Terraria art is reused before use"),
 "Lethality - A Terramity Addon":("A","low","MIT in mods.toml only (no repo); same check as Brutality"),
 "Macabre":("A","low","Academic Free License 3.0 in mods.toml only (no repo); AFL is a software licence, read before use"),
 "Linggango Textures":("A-perm","high","All Rights Reserved; used with Misanthropy's permission (v38). Part is Coquet by jekaloic"),
 "Linggango - FTB Quests Theme":("A-perm","high","no licence; used with Misanthropy's permission (v38)"),
 "Mellow":("A","high","MIT or Apache-2.0 (LICENSE, LICENSE-APACHE in the zip): shader code, no image assets"),
 "Blood Magic":("A","high","CC BY 4.0 (repo LICENSE.md)"),
 "Goety - The Dark Arts":("A","high","MIT (repo LICENSE.txt, whole repo); already used at 02adbe7491"),
 "Marium's Soulslike Weaponry":("A","high","CC0-1.0 (repo LICENSE, mods.toml, Modrinth)"),
 "Dungeon Now Loading":("A","medium","CC0-1.0 file in the jar and mods.toml; MIT on Modrinth"),
 "Ribbits":("B","high","repo LICENSE: all assets owned by Refresh Studios and Bonsai Studios, All Rights Reserved"),
 "Ars Elemental":("A","high","GPL-3.0 (repo LICENSE); mods.toml says LGPL-3.0, comply with GPL-3.0"),
 "Tome of Blood":("A","medium","LGPL-3.0 in mods.toml; README: part of the assets by Gronglegrowth under CC BY 4.0 (credit them)"),
 "EEEAB's Mobs":("A","high","LGPL-3.0 (repo LICENSE.txt)"),
 "Bosses of Mass Destruction":("A","high","LGPL-3.0 (original repo miyo6032 LICENSE; this is the Forge port)"),
 "Immersive Weathering":("A","high","LGPL-3.0 (repo LICENSE)"),
 "Just Dire Things":("A","high","MIT (repo LICENSE.txt)"),
 "Mekanism":("A","high","MIT (repo LICENSE)"),
 "Nature's Aura":("A","high","MIT (repo LICENSE)"),
 "Farmer's Delight":("A","high","MIT (repo LICENSE)"),
 "Mystical Agriculture":("A","high","MIT (repo LICENSE)"),
 "Industrial Foregoing":("A","high","MIT (repo LICENSE)"),
 "Ars Additions":("A","high","LGPL-3.0 (repo LICENSE)"),
 "Applied Energistics 2":("A-SA","high","code LGPL-3.0, textures CC BY-NC-SA 3.0 (repo README/LICENSE, checked in v37); embed byte for byte. Matches only the main mod, not addons"),
 "Quark":("A-SA","medium","CC BY-NC-SA 3.0 on Modrinth (Quark licence based on it); embed byte for byte"),
 "Deeper and Darker":("A-SA","medium","CC BY-NC-SA 4.0 on Modrinth (deeper-and-darker); the jar declares none; embed byte for byte"),
 "Jaden's Nether Expansion":("B","high","mods.toml says CC BY-NC-SA, Modrinth says CC BY-NC-ND: take the stricter (ND) until the author clarifies"),
}
EXACT={'Create','Applied Energistics 2','Quark','Deeper and Darker'}
rows=[]
def tier(r):
    for k,v in MANUAL.items():
        if r['title']==k or (k not in EXACT and r['title'].startswith(k)): return v
    l=r['lic']; parts=set(l.split('/'))
    if 'Misanthropy' in r['authors'] and l not in OPEN: return ("B","high","Misanthropy's own project; permission so far covers Linggango Textures and the FTB theme only")
    if r['asset_exc']: return ("B","medium","asset exception in a licence file: "+r['asset_exc'][0][1][:160])
    if l in('ARR',) : return ("B","high","All Rights Reserved")
    if l=='CC-ND': return ("B","high","NoDerivatives (CC BY-NC-ND)")
    if l=='none': return ("B","low","no licence found (= all rights reserved)")
    if 'custom' in parts: return ("B","low","custom/own licence: read it before use")
    if 'CC-BY-NC-SA' in parts or 'CC-BY-SA' in parts: return ("A-SA","medium","ShareAlike: embed byte for byte")
    if parts<=OPEN: return ("A","medium" if len(parts)>1 else "medium","open licence declared by the jar/Modrinth; repo not checked for an asset exception")
    return ("B","low","unclassified: "+l)
for r in d.values():
    t,conf,note=tier(r); c=r.get('counts',{}); mr=r.get('mr') or {}
    lf=';'.join(f"{s}:{v}" for s,v in r['lic_sources'])
    rows.append({'cf_project':r['pid'],'cf_file':r['fid'],'type':r['type'],'title':r['title'],'file':r['file'],'authors':' '.join(r['authors']),
      'cf_url':r.get('cf_url') or '','modrinth':mr.get('slug',''),'source':mr.get('source') or r.get('toml_url') or '',
      'lic_toml':(r.get('toml_license') or '').strip()[:80],'lic_modrinth':mr.get('license',''),'lic_evidence':lf,'lic_class':r['lic'],
      'tier':t,'confidence':conf,'nc':int('NC' in r['lic'] ),'sa':int('SA' in r['lic']),
      'particle':c.get('particle',0),'particle_json':r.get('particle_json',0),'entity_fx':c.get('entity_fx',0),'other_fx':c.get('other_fx',0),
      'mob_effect':c.get('mob_effect',0),'gui':c.get('gui',0),'block':c.get('block',0),'item':c.get('item',0),'entity':c.get('entity',0),
      'animated':r.get('anim',0),'fx_score':round(r['fx']),'note':note})
EXTRA=[
 {'type':'Pack overrides','title':'Complementary Reimagined r5.5.1 + Euphoria Patches 1.6.8','file':'overrides/shaderpacks/ (457 files, 233 .glsl)','authors':'Complementary Development, SpacEagle17',
  'source':'https://complementary.dev','lic_class':'custom','tier':'B','confidence':'high',
  'note':'Complementary License 1.5: content creation (screenshots) allowed; redistribution/modification only per §1.2/§1.3. Euphoria License 1.1 §2.1: no direct redistribution. Learn techniques, do not copy GLSL'},
 {'type':'Pack overrides','title':'Linggango quest images (kubejs/assets/customtextures)','file':'overrides/kubejs/assets/customtextures (~300 png)','authors':'Misanthropy',
  'lic_class':'none','tier':'B','confidence':'high','note':"pack has no licence; Misanthropy's permission so far covers Linggango Textures and the FTB theme only"},
 {'type':'Pack overrides','title':'Pack-generated resource packs (linggango_machinery_resources, mod_resources, Moonlight dynamic, betterfoliage generated, netherexp jne_*)','file':'built in game or inside mods',
  'lic_class':'-','tier':'B','confidence':'low','note':"follow the licence of the mod that ships them; JNE is CC BY-NC-ND"},
 {'type':'Base game','title':'Minecraft 1.20.1 (vanilla)','file':'InventivetalentDev/minecraft-assets@1.20.1','authors':'Mojang',
  'lic_class':'Minecraft Usage Guidelines','tier':'A','confidence':'high','note':'fan content, non-commercial, disclaimer in the footer; already in the site'},
]
keys=list(rows[0].keys())
for e in EXTRA: rows.append({k:e.get(k,'') for k in keys})
rows.sort(key=lambda r:(r['tier'],-int(r['fx_score'] or 0)))
with open(OUT,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rows)
import collections
print(collections.Counter(r['tier'] for r in rows)); print(collections.Counter((r['tier'],r['confidence']) for r in rows))
