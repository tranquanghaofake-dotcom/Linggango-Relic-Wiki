#!/usr/bin/env python3
"""Write build/src/wiki_data.js from the pack-read JSON in build/patches: boss summons (summons.json),
Goety rituals (goety.json, from build/pack_audit/goety.py), AE2 storage facts (ae2.json) and side-boss stats
(side_stats.json, from build/pack_audit/side_bosses/stats.py) and portraits (side_imgs.json, from renders.py + jrender.js + pack.py),
Keeper portraits (boss_portraits.json, from build/pack_audit/boss_portraits.js)."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent
J = lambda f: json.loads((H / f).read_text(encoding="utf-8"))
a = J("ae2.json"); a["gates"] = {k: sorted(set(v)) for k, v in a["gates"].items()}
out = "const SUM=" + json.dumps(J("summons.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const GOETY=" + json.dumps(J("goety.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const AE2=" + json.dumps(a, ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const PIMG=" + json.dumps(J("pack_imgs.json"), separators=(",", ":")) + ";\n"
out += "const BINFO=" + json.dumps(J("boss_info.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const BIMG=" + json.dumps(J("boss_imgs.json"), separators=(",", ":")) + ";\n"
out += "const ARMR=" + json.dumps(J("armor_renders.json"), separators=(",", ":")) + ";\n"
out += "const GUIDE=" + json.dumps(J("guides.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const SIDEB=" + json.dumps(J("side_bosses.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const NAMEID=" + json.dumps(J("name_ids.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const TAGID=" + json.dumps(J("tag_ids.json"), ensure_ascii=False, separators=(",", ":")) + ",MOBID=" + json.dumps(J("mob_ids.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const BACT=" + json.dumps(J("boss_acts.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const BGRAPH=" + json.dumps(J("boss_graph.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const SSTAT=" + json.dumps(J("side_stats.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const SDROP=" + json.dumps(J("side_drops.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
out += "const SIMG=" + json.dumps(J("side_imgs.json"), separators=(",", ":")) + ";\n"
out += "const BPORT=" + json.dumps(J("boss_portraits.json"), separators=(",", ":")) + ";\n"
_cm = J("curio_measure.json")
out += "const CM=" + json.dumps(_cm["curios"], ensure_ascii=False, separators=(",", ":")) + ",CMREF=" + json.dumps(_cm["ref_hit"]) + ";\n"
out += "const CTIER=" + json.dumps(J("curio_tiers.json"), separators=(",", ":")) + ";\n"
out += "const BEXTRA=" + json.dumps(J("boss_extra.json"), ensure_ascii=False, separators=(",", ":")) + ";\n"
(H.parent / "src" / "wiki_data.js").write_text(out, encoding="utf-8")
print("wiki_data.js", len(out) // 1024, "kB")
