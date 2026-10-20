#!/usr/bin/env python3
"""Write build/src/wiki_data.js from the pack-read JSON in build/patches: boss summons (summons.json),
Goety rituals (goety.json, from build/pack_audit/goety.py) and AE2 storage facts (ae2.json)."""
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
(H.parent / "src" / "wiki_data.js").write_text(out, encoding="utf-8")
print("wiki_data.js", len(out) // 1024, "kB")
