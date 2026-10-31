"""Side-boss base stats (health, armor, toughness, attack damage, knockback resistance) read from the mod jars.
Usage: stats.py W  (W holds attrs.json, reg.json, cfg.json, cfg2.json from attrs.py, reg.py and cfg.py in this folder;
reg.py also writes the ent_class.json renders.py reads; attrs.py and cfg.py are still to be rewritten)
Writes build/patches/side_stats.json: {boss name: [{entity, hp, armor, tough, dmg, kbr, hits, src}, ...]}.
Optional third argument: the pack's overrides folder (the modpack zip's `overrides/`, CurseForge 1343057 file 9304214 is
`Linggango-V6.6.6hf.zip`). Order of the facts, each one over the one before: the value in the entity's attribute builder
(or the mod's config default), the pack's entitybalance.json, then the pack's own config files (PACK below: a value
replaces, a multiplier multiplies, Iron's "additional" values add). Hardmode is applied on the page, not here."""
import json, sys, pathlib, re, tomllib
W = sys.argv[1]; OV = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else None; H = pathlib.Path(__file__).resolve().parents[2] / "patches"
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

# the pack's config files: (stat, set | mul | add, (file, key path...)); "cap" = most damage one hit can do to the boss
def _ld(f):
    p = OV / "config" / f if (OV / "config" / f).exists() else OV / "defaultconfigs" / f
    t = p.read_text(encoding="utf-8")
    if f.endswith(".toml"): return tomllib.loads(t)
    t = re.sub(r"(?m)^\s*//.*$", "", t); t = re.sub(r",(\s*[}\]])", r"\1", t)  # json5: comments, trailing commas
    return json.loads(t)
_CACHE = {}
def cfg_get(path):
    f, *keys = path
    if f not in _CACHE: _CACHE[f] = _ld(f)
    d = _CACHE[f]
    def find(d, k):  # a key anywhere below d (TOML sections nest; the files name each key once)
        if isinstance(d, dict):
            if k in d: return d[k]
            for v in d.values():
                r = find(v, k)
                if r is not None: return r
        return None
    for k in keys:
        d = find(d, k)
        if d is None: return None
    return float(d) if isinstance(d, (int, float)) else None
CA, MY, BR, TE, GO, SW, LM, MZ, BM = "cataclysm.toml", "meetyourfight-common.toml", "bosses_rise_config.toml", "TerramityCommonConfig.toml", "goety/goety-attributes.toml", "soulsweapons/soulsweapons_boss_config.json", "legendary_monsters-common.toml", "mowziesmobs-common.toml", "bosses_of_mass_destruction.json5"
def cata(n, cap): return [("hp", "mul", (CA, n + "HealthMultiplier")), ("dmg", "mul", (CA, n + "DamageMultiplier")), ("cap", "set", (CA, cap))]
def goety(n): return [("hp", "set", (GO, n + "Health")), ("dmg", "set", (GO, n + "Damage")), ("armor", "set", (GO, n + "Armor")), ("cap", "set", (GO, n + "DamageCap"))]
def souls(n): return [("hp", "set", (SW, n + "_health")), ("armor", "set", (SW, n + "_armor"))]
def leg(n): return [("hp", "mul", (LM, n + " Health Multiplier")), ("dmg", "mul", (LM, n + " Damage Multiplier"))]
def mow(n): return [("hp", "mul", (MZ, n, "combat_config", "health_multiplier")), ("dmg", "mul", (MZ, n, "combat_config", "attack_multiplier"))]
def myf(n): return [("hp", "mul", (MY, n, "health")), ("dmg", "mul", (MY, n, "damage"))]
def br(n): return [("hp", "set", (BR, n + " Health")), ("armor", "set", (BR, n + " Armor")), ("dmg", "set", (BR, n + " Damage"))]
def bomd(n): return [("hp", "set", (BM, n, "health")), ("armor", "set", (BM, n, "armor")), ("dmg", "set", (BM, n, "attack"))]
PACK = {"cataclysm:ignis": cata("Ignis", "IgnisDamageCap"), "cataclysm:ender_guardian": cata("EnderGuardian", "EnderGuardianDamageCap"),
        "cataclysm:netherite_monstrosity": cata("Monstrosity", "MonstrosityDamageCap"), "cataclysm:the_harbinger": cata("Harbinger", "The Harbinger DamageCap"),
        "cataclysm:the_leviathan": cata("Leviathan", "LeviathanDamageCap"), "cataclysm:ancient_remnant": cata("AncientRemnant", "AncientRemnantCap"),
        "cataclysm:maledictus": cata("Maledictus", "MaledictusDamageCap"), "cataclysm:scylla": cata("Scylla", "Scylla DamageCap"),
        "meetyourfight:swampjaw": myf("swampjaw"), "meetyourfight:bellringer": myf("bellringer"), "meetyourfight:dame_fortuna": myf("fortuna"), "meetyourfight:rosalyne": myf("rosalyne"),
        "block_factorys_bosses:yeti": br("Yeti"), "block_factorys_bosses:infernal_dragon": br("Dragon"), "block_factorys_bosses:underworld_knight": br("Knight"),
        "terramity:gob": [("hp", "set", (TE, "Gob, King of Gnomes Health"))], "terramity:super_sniffer": [("hp", "set", (TE, "Super Sniffer Health"))],
        "terramity:ultra_sniffer": [("hp", "set", (TE, "Ultra Sniffer Health"))], "terramity:trial_guardian": [("hp", "set", (TE, "Trial Guardian Health"))],
        "terramity:virtue": [("hp", "set", (TE, "Virtue Health"))], "terramity:enchanter_merlin": [("hp", "set", (TE, "Enchanter Merlin Health"))],
        "terramity:sorceress_circe": [("hp", "set", (TE, "Sorceress Circe Health"))], "terramity:gundalf": [("hp", "set", (TE, "Archmage Gundalf Health"))],
        "goety:apostle": goety("apostle"), "goety:vizier": goety("vizier"), "goety:minister": goety("minister"), "goety:crone": goety("crone"),
        "goety:heresiarch": goety("heresiarch"), "goety:skull_lord": goety("skullLord"), "goety:wither_necromancer": goety("witherNecromancer"),
        "goety:brood_mother": goety("broodMother"), "goety:wight": goety("wight"), "goety:ender_keeper": goety("enderKeeper"),
        "goety:hostile_redstone_golem": goety("redstoneGolem"), "goety:redstone_monstrosity": goety("redstoneMonstrosity"),
        "soulsweapons:accursed_lord_boss": souls("decaying_king"), "soulsweapons:returning_knight": souls("returning_knight"), "soulsweapons:draugr_boss": souls("old_champions_remains"),
        "soulsweapons:night_shade": souls("frenzied_shade"), "soulsweapons:chaos_monarch": souls("chaos_monarch"), "soulsweapons:moonknight": souls("fallen_icon"),
        "soulsweapons:day_stalker": souls("day_stalker"), "soulsweapons:night_prowler": souls("night_prowler"),
        "legendary_monsters:ancient_guardian": leg("Ancient Guardian"), "legendary_monsters:posessed_paladin": leg("Posessed Paladin"), "legendary_monsters:overgrown_colossus": leg("Overgrown Colosuss"),
        "legendary_monsters:cloud_golem": leg("Cloud Golem"), "legendary_monsters:frostbitten_golem": leg("Frostbitten Golem"), "legendary_monsters:dune_sentinel": leg("Dune Sentinel"),
        "legendary_monsters:skeletosaurus": leg("Skeletosaurus"), "legendary_monsters:endersent": leg("Endersent"), "legendary_monsters:chorusling": leg("Chorusling"),
        "legendary_monsters:the_obliterator": leg("The Obliterator"), "legendary_monsters:lava_eater": leg("Lava Eater"), "legendary_monsters:shulker_mimic": leg("Shulker Mimic"),
        "legendary_monsters:withered_abomination": leg("Withered Abomination"),
        "mowziesmobs:frostmaw": mow("frostmaw"), "mowziesmobs:umvuthi": mow("umvuthi"), "mowziesmobs:ferrous_wroughtnaut": mow("ferrous_wroughtnaut"), "mowziesmobs:sculptor": mow("sculptor"),
        "mowziesmobs:naga": mow("naga"),
        "bosses_of_mass_destruction:lich": bomd("lichConfig"), "bosses_of_mass_destruction:obsidilith": bomd("obsidilithConfig"),
        "bosses_of_mass_destruction:gauntlet": bomd("gauntletConfig"), "bosses_of_mass_destruction:void_blossom": bomd("voidBlossomConfig"),
        "irons_spellbooks:fire_boss": [("hp", "add", ("irons_spellbooks-server.toml", "Tyros", "additionalHealth")), ("dmg", "add", ("irons_spellbooks-server.toml", "Tyros", "additionalAttackDamage"))],
        "goety_revelation:apollyon": [("hp", "set", ("goety_revelation.toml", "apollyon_health"))],
        "eeeabsmobs:corpse_warlock": [("hp", "mul", ("eeeabsmobs-common.toml", "Corpse Warlock", "Health Multiplier"))],
        "eeeabsmobs:relic_annihilator": [("hp", "mul", ("eeeabsmobs-common.toml", "Relic Annihilator", "Health Multiplier"))]}

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
    if OV and e in PACK:
        got = []
        for k, how, path in PACK[e]:
            v = cfg_get(path)
            if v is None: continue
            if how == "set": o[k] = v
            elif how == "mul": o[k] = o[k] * v if o.get(k) is not None else None
            elif how == "add": o[k] = (o.get(k) or 0) + v
            got.append(f"{k} {'x' if how == 'mul' else '+' if how == 'add' else '='}{v:g}")
        o = {k: v for k, v in o.items() if v is not None}
        if got: src.insert(0, "pack config " + path[0] + " (" + ", ".join(got) + ")")
    for k in KEYS + ("cap",):
        if k in o: o[k] = round(float(o[k]), 2)
    o["src"] = "; ".join(src)
    return o

out = {}; miss = []
rows = [(n, v["entity"]) for n, v in SB.items()] + [(r[0], r[6]) for r in BX if r[0] not in SB]
for n, e in rows:
    es = e if isinstance(e, list) else [e]
    st = []
    for s in filter(None, map(one, es)):  # a second entity with the same numbers (Moonknight's phase 2) adds nothing
        if not any({k: v for k, v in x.items() if k != "entity"} == {k: v for k, v in s.items() if k != "entity"} for x in st): st.append(s)
    if st: out[n] = st
    else: miss.append(n)
(H / "side_stats.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
print(len(out), "bosses with stats; none for:", miss)
