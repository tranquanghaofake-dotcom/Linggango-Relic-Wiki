#!/usr/bin/env python3
"""Write build/src/wiki_data.js from the pack-read JSON in build/patches: boss summons (summons.json),
Goety rituals (goety.json, from build/pack_audit/goety.py), AE2 storage facts (ae2.json) and side-boss stats
(side_stats.json, from build/pack_audit/side_bosses/stats.py, with the pack's soul_bosses.json pins laid over it) and portraits (side_imgs.json, from renders.py + jrender.js + pack.py),
Keeper portraits (boss_portraits.json, from build/pack_audit/boss_portraits.js).
Pictures that only detail pages show (armour stands, guide-book pages, Goety ritual layouts, Act titles and side-boss landscapes, the walk loops) go to build/src/wiki_pics.js
instead: the offline file inlines it, the site loads it after the first page is drawn (build.py, app.js picsLoaded)."""
import json, pathlib, re
H = pathlib.Path(__file__).resolve().parent
J = lambda f: json.loads((H / f).read_text(encoding="utf-8"))
a = J("ae2.json"); a["gates"] = {k: sorted(set(v)) for k, v in a["gates"].items()}
_g = J("goety.json"); _gi = {k: t.pop("img") for k, t in _g["types"].items() if t.get("img")}   # -> wiki_pics.js
_gu = J("guides.json"); _ui = {k: g.pop("i") for k, g in _gu.items() if g.get("i")}
out = "const SUM=" + json.dumps(J("summons.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const GOETY=" + json.dumps(_g, ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const AE2=" + json.dumps(a, ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const BINFO=" + json.dumps(J("boss_info.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const BIMG=" + json.dumps(J("boss_imgs.json"), separators=(",", ":")) + ";\n"
out += "const ARMR={};\n"
out += "const GUIDE=" + json.dumps(_gu, ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const SIDEB=" + json.dumps(J("side_bosses.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const NAMEID=" + json.dumps(J("name_ids.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const TAGID=" + json.dumps(J("tag_ids.json"), ensure_ascii=False, separators=(",", ":")) + ",MOBID=" + json.dumps(J("mob_ids.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const BACT=" + json.dumps(J("boss_acts.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const BGRAPH=" + json.dumps(J("boss_graph.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
# linggango_tweaks BossSouls retunes every entity in kubejs/data/linggango_tweaks/soul_bosses/*.json (merged into
# soul_bosses.json) on spawn and again 20 ticks later: max health = health and armor = armor exactly (so Hardmode's
# x2.1 on spawn is undone), and the damage it deals to players is multiplied by damage.
_ss = J("side_stats.json"); _SB = J("soul_bosses.json")
for _rows in _ss.values():
    for _r in _rows:
        _t = _SB.get(_r["entity"])
        if not _t: continue
        _r["hp"] = float(_t["health"])
        if _t.get("armor", -1) >= 0: _r["armor"] = float(_t["armor"])
        if "damage" in _t: _r["dmg_mult"] = _t["damage"]
        _r["pinned"] = 1
        _r["src"] = "pack soul_bosses (linggango_tweaks BossSouls pins health and armor); " + _r["src"]
out += "const SSTAT=" + json.dumps(_ss, ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const SDROP=" + json.dumps(J("side_drops.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const SIMG=" + json.dumps(J("side_imgs.json"), separators=(",", ":")) + ";\n"
out += "const BPORT=" + json.dumps(J("boss_portraits.json"), separators=(",", ":")) + ";\n"
out += "const BFIG=" + json.dumps(J("boss_figs.json"), separators=(",", ":")) + ";\n"  # the home page's staircase figures (boss_portraits.js --figs)
_cm = J("curio_measure.json")
out += "const CM=" + json.dumps(_cm["curios"], ensure_ascii=False, separators=(",", ":")) + ",CMREF=" + json.dumps(_cm["ref_hit"]) + ";\n"
out += "const CTIER=" + json.dumps(J("curio_tiers.json"), separators=(",", ":")) + ";\n"
out += "const THREAT=" + json.dumps(J("effect_threat.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const UPTIME=" + json.dumps(J("effect_uptime.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const CCH=" + json.dumps(J("curio_chance.json")["curios"], ensure_ascii=False, separators=(",", ":")) + ";\n"   # curios sampled in game for their chances (pack_audit/measure/import_chance.py)
out += "const CCD=" + (json.dumps(J("curio_cond.json")["curios"], ensure_ascii=False, separators=(",", ":")) if (H / "curio_cond.json").exists() else "{}") + ";\n"   # curios sampled in game in conditions (pack_audit/measure/import_cond.py)
out += "const BEXTRA=" + json.dumps(J("boss_extra.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
(H.parent / "src" / "wiki_data.js").write_text(out, encoding="utf-8")
# every status effect in the pack (pack_audit/effects.py), the gear that gives each one (gear_fx.json) and the icons the licences allow: only the Effects page shows them, so they go to wiki_pics.js
_ef = J("effects.json")
# descriptions the wiki wrote from an effect's bytecode (pack_audit digest of its class and the methods that read it) for effects whose mod ships no
# text: filled in only where the jar has none, and marked (dc) so the page says where it comes from
_ed = J("effect_desc.json")
assert set(_ed) <= {e["id"] for e in _ef["effects"]}, "effect_desc.json names an effect the game does not register: " + ", ".join(sorted(set(_ed) - {e["id"] for e in _ef["effects"]}))
for _e in _ef["effects"]:
    if _e["id"] in _ed:
        assert not _e["desc"], "effect_desc.json describes " + _e["id"] + ", which has the mod's own text"
        _e["desc"] = _ed[_e["id"]]["d"]; _e["dc"] = 1
# an attribute's name from its mod's lang (effects.py aname); one whose key the jars do not hold (a library nested in another jar) reads as its id's last
# part ("forge:step_height_addition" -> "Step Height Addition"), never as the id run together
_ea = {k: (re.sub(r"[^A-Za-z0-9' ]+", "", re.sub(r"§.", "", v or "")).strip() or k.split(":")[1].split(".")[-1].replace("_", " ").title()) for k, v in _ef["attrs"].items()}
def _slim(r):
    o = {"i": r["id"], "n": r["name"] or "", "m": r["mod"]}
    for k, f in (("cat", "k"), ("color", "c"), ("desc", "d"), ("mods", "a")):
        if r[k] not in (None, [], ""): o[f] = r[k][0] if k == "cat" else r[k]
    if r.get("dc"): o["dc"] = 1
    if r["icon"]: o["p"] = 1
    if not r["reg"]: o["u"] = 1
    return o
# gear_fx.py names an effect by the namespace of the item's own mod; for these mods the effect really belongs to the library mod they use
# (14 ids the game does not register, found against patches/game_registry.json on 2026-11-14): goetyawaken:wane is goety:wane, and so on
_EFNS = {"goetyawaken": "goety", "lethality": "terramity", "brutality": "terramity", "traveloptics": "cataclysm"}
_gids = {e["id"] for e in _ef["effects"]}
def _eid(i):
    if i in _gids: return i
    ns, path = i.split(":", 1)
    j = _EFNS.get(ns, "") + ":" + path
    return j if j in _gids else None
_eg = {}
for _it, _v in J("gear_fx.json").items():
    for _f in _v.get("fx", []):
        if "effect" not in _f or not _eid(_f["effect"]): continue   # fire, healing and the like are not status effects
        _row = [_it, _f["when"], _f.get("level"), _f.get("ticks")]
        if _row not in _eg.setdefault(_eid(_f["effect"]), []): _eg[_eid(_f["effect"])].append(_row)
# every spell (pack_audit/spells.py) and its icon: only the Spells page shows them, so they go to wiki_pics.js
def _sp(r):
    o = {"i": r["id"], "n": r["name"] or "", "m": r["mod"]}
    g = _pw["spells"].get(r["id"])   # the running game's school, levels and on/off (spell_power.json) over the jar reading
    if g: r = dict(r, school=g["school"].split(":")[1], schoolName=g["schoolName"], maxLevel=g["lv"][1], enabled=g["enabled"])
    for k, f in (("school", "s"), ("schoolName", "sn"), ("rarity", "r"), ("maxLevel", "L"), ("cooldown", "c"), ("mana", "ma"), ("manaPer", "mp"), ("manaMul", "mm"), ("castTime", "t"), ("cast", "k"), ("guide", "g"), ("fx", "f")):
        if r[k] not in (None, [], ""): o[f] = r[k]
    if not r["enabled"]: o["x"] = 1
    if r["craft"] is False: o["nc"] = 1
    return o
_sl = J("spells.json")["spells"]; _si = J("spell_icons.json")
# the running game's view of each Iron's spell (pack_audit/spell_power.py from kubejs lgw_spellpower.js): school, levels, on/off, what spell power changes
_pw = J("spell_power.json") if (H / "spell_power.json").exists() else {"spells": {}, "goety": {}}
_en = lambda r: (_pw["spells"].get(r["id"]) or r)["enabled"]
# the Goety focuses (pack_audit/spell_systems.py -> spells_goety.json): name, description, mod, type, soul cost, cast and cooldown ticks
def _gsp(r):
    o = {"i": r["id"], "n": r["name"] or "", "m": r["mod"]}
    for k, f in (("type", "y"), ("typeName", "yn"), ("cost", "c"), ("cast", "t"), ("cooldown", "cd"), ("guide", "g")):
        if r[k] not in (None, [], ""): o[f] = r[k]
    return o
_gl = J("spells_goety.json")["spells"]; _gi2 = J("spell_icons_goety.json")
# the Ars Nouveau glyphs (spell_systems.py -> spells_ars.json): name, description, mod, kind (form, effect, augment, filter), tier, mana cost, on or off
def _asp(r):
    o = {"i": r["id"], "n": r["name"] or "", "m": r["mod"]}
    for k, f in (("kind", "k"), ("tier", "r"), ("cost", "c"), ("guide", "g")):
        if r[k] not in (None, [], ""): o[f] = r[k]
    if r["enabled"] is False: o["x"] = 1
    return o
_al = J("spells_ars.json")["spells"]; _ai = J("spell_icons_ars.json")
# the Brutality spells (spell_systems.py -> spells_brutality.json): school, how it is cast, its other categories, base mana, damage, cooldown and cast
# ticks with what one level adds; u: the mod's files give it no name (nor description, nor icon)
def _bsp(r):
    o = {"i": r["id"], "n": r["name"] or "", "m": r["mod"]}
    for k, f in (("school", "s"), ("cast", "k"), ("tags", "tg"), ("mana", "ma"), ("manaLv", "mal"), ("damage", "d"), ("damageLv", "dl"),
                 ("cooldown", "cd"), ("cooldownLv", "cdl"), ("castTicks", "t"), ("castLv", "tl"), ("guide", "g")):
        if r[k] not in (None, [], ""): o[f] = r[k]
    if not r["name"]: o["u"] = 1
    return o
_bl = J("spells_brutality.json")["spells"]; _bi = J("spell_icons_brutality.json")
# spell ids whose clip a person looked at and approved (build/clips/approved.json). The clips live on the workspace branch (clips/), fetched into
# build/clips3 (or $LGW_CLIPS) by build/clips_fetch.sh; a build without them lists none (build.py applies the same rule and copies the files)
import os as _os
_cdir = pathlib.Path(_os.environ.get("LGW_CLIPS") or (H.parent / "clips3"))
_appr = sorted(json.loads((H.parent / "clips" / "approved.json").read_text()))
assert all(c in {r["id"] for r in _sl + _gl + _al + _bl} for c in _appr), "an approved clip that is not a spell of spells.json or spells_<system>.json"
_clips = [c for c in _appr if (_cdir / (c.replace(":", "__") + ".mp4")).exists()]
# why a spell has no clip (build/clips/noclip.json, from the clip reviews in docs/NOTES.md): every spell the pack leaves on has an approved clip or
# a reason, never both; a spell the pack turns off needs neither (the page says it is off)
_why = json.loads((H.parent / "clips" / "noclip.json").read_text())
# what spell power changes in each Iron's spell (pack_audit/spell_power.py, from the running game: kubejs lgw_spellpower.js) and the enchantments each Goety
# focus accepts: [school power name, lowest level, highest level, [[line label, value at the lowest level, at the highest, flags]]]; flags: p the school's
# power changes it, g the general Spell Power does, l the level does
_ppw = {k: [v["attr"], v["lv"][0], v["lv"][1], [[r["t"], r.get("a"), r["b"], "".join(f for f in "pgl" if r.get(f))] for r in v["rows"]]] for k, v in _pw["spells"].items()}
assert not _pw["spells"] or set(_ppw) == {r["id"] for r in _sl}, "spell_power.json and spells.json list different spells"
_on = {r["id"] for r in _sl if _en(r) is not False} | {r["id"] for r in _al if r["enabled"] is not False} | {r["id"] for r in _gl + _bl}
assert not set(_why) & set(_appr), "noclip.json gives a reason for a spell with an approved clip: " + ", ".join(sorted(set(_why) & set(_appr)))
assert set(_why) <= _on, "noclip.json names a spell that is not on (or not a spell): " + ", ".join(sorted(set(_why) - _on))
assert _on <= set(_why) | set(_appr), "a spell with neither an approved clip nor a reason in noclip.json: " + ", ".join(sorted(_on - set(_why) - set(_appr)))
pics = ("Object.assign(ARMR," + json.dumps(J("armor_renders.json"), separators=(",", ":")) + ");\n"
        + "for(const [k,v] of Object.entries(" + json.dumps(_ui, separators=(",", ":")) + "))if(GUIDE[k])GUIDE[k].i=v;\n"
        + "for(const [k,v] of Object.entries(" + json.dumps(_gi, separators=(",", ":")) + "))if(GOETY.types[k])GOETY.types[k].img=v;\n"
        + "window.PIMG=" + json.dumps(J("pack_imgs.json"), separators=(",", ":")) + ";\n"   # Act titles and side-boss landscapes (the hub's open Act panel redraws when they arrive: app.js pathRefill)
        + "window.BWALK=" + json.dumps(J("boss_walks.json"), separators=(",", ":")) + ";\n"   # the walk loops of the home page's figures (boss_portraits.js --figs)
        + "window.EFX=" + json.dumps([_slim(r) for r in _ef["effects"]], ensure_ascii=False, separators=(",", ":")) + ";window.EFXA=" + json.dumps(_ea, ensure_ascii=False, separators=(",", ":")) + ";window.EFXU=" + str(len(_ef["unconfirmed"])) + ";window.EFXG=" + json.dumps(_eg, separators=(",", ":")) + ";\n"
        + "window.EFXI=" + json.dumps(J("effect_icons.json"), separators=(",", ":")) + ";\n"
        # measured in game (pack_audit/measure/import_fx.py): what each effect did at level I and II on a test pig and the tester, and the potions and foods that give it
        + "window.EFXM=" + json.dumps(J("effect_measure.json"), ensure_ascii=False, separators=(",", ":")) + ";window.EFXS=" + json.dumps(J("effect_sources.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
        + "window.SPL=" + json.dumps([_sp(r) for r in _sl], ensure_ascii=False, separators=(",", ":")) + ";window.SPLI=" + json.dumps(_si, separators=(",", ":")) + ";window.SPCLIP=" + json.dumps(_clips) + ";window.SPWHY=" + json.dumps(_why, ensure_ascii=False, separators=(",", ":")) + ";window.SPPOW=" + json.dumps({"g": _pw.get("general"), "s": _ppw, "goety": _pw.get("goety", {})}, ensure_ascii=False, separators=(",", ":")) + ";\n"
        + "window.GSPL=" + json.dumps([_gsp(r) for r in _gl], ensure_ascii=False, separators=(",", ":")) + ";window.GSPLI=" + json.dumps(_gi2, separators=(",", ":")) + ";\n"   # Spells > Goety (spell_systems.py)
        + "window.ASPL=" + json.dumps([_asp(r) for r in _al], ensure_ascii=False, separators=(",", ":")) + ";window.ASPLI=" + json.dumps(_ai, separators=(",", ":")) + ";\n"   # Spells > Ars Nouveau
        + "window.BSPL=" + json.dumps([_bsp(r) for r in _bl], ensure_ascii=False, separators=(",", ":")) + ";window.BSPLI=" + json.dumps(_bi, separators=(",", ":")) + ";\n"   # Spells > Brutality
        + "window.PICS=1;if(typeof picsLoaded==='function')picsLoaded();\n")
(H.parent / "src" / "wiki_pics.js").write_text(pics, encoding="utf-8")
print("wiki_data.js", len(out) // 1024, "kB + wiki_pics.js", len(pics) // 1024, "kB")
