#!/usr/bin/env python3
"""Hand corrections to curios, kept out of data.js so the file is only rewritten by scripts. curio_fix.json maps a curio
id to the fields to set (an entry with no such id is appended when it carries "n"; null removes the curio). Runs first in
apply_all.sh, so the derived passes (curio_recipes, boss_stats, boss_order) see the corrected data; running it again
changes nothing."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent
P = H.parent / "src" / "data.js"
FIX = {k: v for k, v in json.loads((H / "curio_fix.json").read_text(encoding="utf-8")).items() if not k.startswith("_")}
s = P.read_text(encoding="utf-8"); D, e = json.JSONDecoder().raw_decode(s, 8)
by = {d["id"]: d for d in D}; n = 0
for k, v in FIX.items():
    if v is None:
        if k in by: D.remove(by.pop(k)); n += 1
    elif k in by:
        for f, x in v.items():
            if by[k].get(f) != x: by[k][f] = x; n += 1
    elif "n" in v:
        D.append({"id": k, **v}); n += 1
    else:
        raise SystemExit(f"curio_fix: {k} is not in data.js and has no \"n\" to add it")
if n: P.write_text("const D=" + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + s[e:], encoding="utf-8")
print(f"curio_fix: {len(FIX)} curios, {n} changes")
