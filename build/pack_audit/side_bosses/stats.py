"""Side-boss base stats (health, armor, toughness, attack damage, knockback resistance) read from the mod jars.
Usage: stats.py W  (W holds attrs.json, reg.json, cfg.json, cfg2.json from attrs.py, reg.py and cfg.py in this folder)
Writes build/patches/side_stats.json: {boss name: [{entity, hp, armor, tough, dmg, kbr, hits, src}, ...]}.
Order of the facts: the pack's entitybalance.json override, then the mod's config default, then the value in the
entity's attribute builder. The pack's own config files are not read (the modpack zip is not on the CDN under a
known name), so a config value the pack changed would show the mod's default: every config-read value says so."""
import json, sys, pathlib, re
W = sys.argv[1]; H = pathlib.Path(__file__).resolve().parents[2] / "patches"
A = json.load(open(W + "/attrs.json")); R = json.load(open(W + "/reg.json"))
CF = {**json.load(open(W + "/cfg.json")), **json.load(open(W + "/cfg2.json"))}
EB = json.loads((H / "entitybalance.json").read_text())
SB = json.loads((H / "side_bosses.json").read_text()); BX = json.loads((H / "boss_extra.json").read_text())
CLS = {c: m for v in A.values() for c, m in v.items()}
SIMPLE = {c.split(".")[-1]: c for c in CLS}
REG = {}
for j in R:
    for k, c in R[j].items(): REG.setdefault(j.split("-")[0].split("_")[0].lower() + ":" + k, c); REG.setdefault(k, c)
# entities whose registry the reader could not follow (static-init registries, MCreator, Kotlin): class by hand
MAN = {"block_factorys_bosses:infernal_dragon": "InfernalDragonEntity", "block_factorys_bosses:underworld_knight": "UnderworldKnightEntity",
       "block_factorys_bosses:yeti": "YetiEntity", "born_in_chaos_v1:lord_pumpkinhead": "LordPumpkinheadEntity",
       "goety:apostle": "Apostle", "goety:brood_mother": "AbstractBroodMother", "goety:crone": "Crone", "goety:ender_keeper": "EnderKeeper",
       "goety:heresiarch": "Heresiarch", "goety:hostile_redstone_golem": "HostileRedstoneGolem", "goety:minister": "Minister",
       "goety:redstone_monstrosity": "HostileRedstoneMonstrosity", "goety:skull_lord": "SkullLord", "goety:vizier": "Vizier", "goety:wight": "Wight",
       "goety:wither_necromancer": "AbstractWitherNecromancer", "meetyourfight:bellringer": "BellringerEntity",
       "meetyourfight:dame_fortuna": "DameFortunaEntity", "meetyourfight:rosalyne": "RosalyneEntity", "meetyourfight:swampjaw": "SwampjawEntity",
       "mutantmonsters:mutant_enderman": "MutantEnderman", "soulsweapons:moonknight_phase_2": "Moonknight",
       "terramity:enchanter_merlin": "EnchanterMerlinEntity", "terramity:gob": "GobEntity", "terramity:gundalf": "GundalfEntity",
       "terramity:sorceress_circe": "SorceressCirceEntity", "terramity:super_sniffer": "SuperSnifferEntity", "terramity:trial_guardian": "TrialGuardianEntity",
       "terramity:ultra_sniffer": "UltraSnifferEntity", "terramity:virtue": "VirtueEntity"}
# bosses whose numbers live only in a config class
BOMD = {"bosses_of_mass_destruction:" + k: v for k, v in {"gauntlet": "GauntletConfig", "lich": "LichConfig", "obsidilith": "ObsidilithConfig", "void_blossom": "VoidBlossomConfig"}.items()}
HITS = {"fdbosses:malkuth": ("MalkuthConfig", "malkuthMaxHits"), "fdbosses:chesed": ("ChesedConfig", "chesedMaxHits")}
KEYS = ("hp", "armor", "tough", "dmg", "kbr")

def cfgval(expr):
    m = re.match(r"(\w+)\.(\w+)", str(expr))
    if not m: return None
    c = {"AttributesConfig": "AttributesConfig", "BossConfig": "BossConfig"}.get(m.group(1))
    return CF.get(c, {}).get(m.group(2))

def one(e):
    o = {"entity": e}; src = []
    if e in BOMD:
        c = CF[BOMD[e]]; o.update({k: c[f] for k, f in (("hp", "health"), ("armor", "armor"), ("dmg", "attack")) if f in c}); src.append("mod config default")
    elif e in HITS:
        c, f = HITS[e]; o["hits"] = int(CF[c][f]); src.append("mod config default: the fight ends after this many hits, not on health")
    elif e == "goety_revelation:apollyon":
        o["hp"] = CF["ModConfig"]["APOLLYON_HEALTH"]; src.append("mod config default (Goety Revelation)")
    else:
        c = MAN.get(e) and SIMPLE.get(MAN[e]) or REG.get(e) or REG.get(e.split(":")[1])
        if not c or c not in CLS: return None
        ENT[e] = c
        meth = next(iter(CLS[c].values())); used = False
        for k, v in meth:
            if k not in KEYS: continue
            if isinstance(v, (int, float)): o[k] = v
            else:
                cv = cfgval(v)
                if cv is not None: o[k] = cv; used = True
        src.append("entity attribute builder (" + c.split(".")[-1] + ")" + (" + mod config defaults" if used else ""))
    over = EB.get(e)
    if over:
        for x in over:
            k = {"max_health": "hp", "armor": "armor", "attack_damage": "dmg", "armor_toughness": "tough", "knockback_resistance": "kbr"}.get(x["attribute"].split(".")[-1])
            if not k: continue
            if x["operation"] == "BASE": o[k] = x["value"]
            elif x["operation"] == "ADDITION": o[k] = o.get(k, 0) + x["value"]
        src.insert(0, "pack override (entitybalance.json)")
    for k in KEYS:
        if k in o: o[k] = round(float(o[k]), 2)
    o["src"] = "; ".join(src)
    return o

out = {}; miss = []; ENT = {}
rows = [(n, v["entity"]) for n, v in SB.items()] + [(r[0], r[6]) for r in BX if r[0] not in SB]
for n, e in rows:
    es = e if isinstance(e, list) else [e]
    st = []
    for s in filter(None, map(one, es)):  # a second entity with the same numbers (Moonknight's phase 2) adds nothing
        if not any({k: v for k, v in x.items() if k != "entity"} == {k: v for k, v in s.items() if k != "entity"} for x in st): st.append(s)
    if st: out[n] = st
    else: miss.append(n)
(H / "side_stats.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
json.dump(ENT, open(W + "/ent_class.json", "w"), indent=0)  # entity id -> class, for renders.py
print(len(out), "bosses with stats; none for:", miss)
