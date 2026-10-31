#!/usr/bin/env python3
"""Write build/src/wiki_data.js from the pack-read JSON in build/patches: boss summons (summons.json),
Goety rituals (goety.json, from build/pack_audit/goety.py), AE2 storage facts (ae2.json) and side-boss stats
(side_stats.json, from build/pack_audit/side_bosses/stats.py, with the pack's soul_bosses.json pins laid over it) and portraits (side_imgs.json, from renders.py + jrender.js + pack.py),
Keeper portraits (boss_portraits.json, from build/pack_audit/boss_portraits.js).
Pictures that only detail pages show (armour stands, guide-book pages, Goety ritual layouts) go to build/src/wiki_pics.js
instead: the offline file inlines it, the site loads it after the first page is drawn (build.py, app.js picsLoaded)."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent
J = lambda f: json.loads((H / f).read_text(encoding="utf-8"))
a = J("ae2.json"); a["gates"] = {k: sorted(set(v)) for k, v in a["gates"].items()}
_g = J("goety.json"); _gi = {k: t.pop("img") for k, t in _g["types"].items() if t.get("img")}   # -> wiki_pics.js
_gu = J("guides.json"); _ui = {k: g.pop("i") for k, g in _gu.items() if g.get("i")}
out = "const SUM=" + json.dumps(J("summons.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const GOETY=" + json.dumps(_g, ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const AE2=" + json.dumps(a, ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const PIMG=" + json.dumps(J("pack_imgs.json"), separators=(",", ":")) + ";\n"
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
_cm = J("curio_measure.json")
out += "const CM=" + json.dumps(_cm["curios"], ensure_ascii=False, separators=(",", ":")) + ",CMREF=" + json.dumps(_cm["ref_hit"]) + ";\n"
out += "const CTIER=" + json.dumps(J("curio_tiers.json"), separators=(",", ":")) + ";\n"
out += "const BEXTRA=" + json.dumps(J("boss_extra.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
(H.parent / "src" / "wiki_data.js").write_text(out, encoding="utf-8")
pics = ("Object.assign(ARMR," + json.dumps(J("armor_renders.json"), separators=(",", ":")) + ");\n"
        + "for(const [k,v] of Object.entries(" + json.dumps(_ui, separators=(",", ":")) + "))if(GUIDE[k])GUIDE[k].i=v;\n"
        + "for(const [k,v] of Object.entries(" + json.dumps(_gi, separators=(",", ":")) + "))if(GOETY.types[k])GOETY.types[k].img=v;\n"
        + "window.PICS=1;if(typeof picsLoaded==='function')picsLoaded();\n")
(H.parent / "src" / "wiki_pics.js").write_text(pics, encoding="utf-8")
print("wiki_data.js", len(out) // 1024, "kB + wiki_pics.js", len(pics) // 1024, "kB")
