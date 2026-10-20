#!/usr/bin/env python3
"""Add icons for gear the first icon pass missed (forge:separate_transforms GUI textures etc.),
from gear_icons.json (made by build/pack_audit/gui_icons.py). Idempotent."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent
P = H.parent / "src" / "gear_data.js"
new = json.loads((H / "gear_icons.json").read_text())
s = P.read_text(encoding="utf-8")
k = "Object.assign(IC,"; i = s.index(k) + len(k)
IC, end = json.JSONDecoder().raw_decode(s, i)
add = {a: b for a, b in new.items() if a not in IC}
IC.update(new)
P.write_text(s[:i] + json.dumps(IC, separators=(",", ":")) + s[end:], encoding="utf-8")
print("added", len(add))
