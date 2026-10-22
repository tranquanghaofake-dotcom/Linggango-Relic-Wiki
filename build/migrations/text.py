#!/usr/bin/env python3
"""Wording pass over build/src/data.js (idempotent): one way to write slot bonuses,
full stops on source lines, possessives, and "hardest ingredient" lines that named a
crafted curio as if it came straight from a boss bag."""
import json, pathlib, re
P = pathlib.Path(__file__).resolve().parents[1] / "src" / "data.js"
s = P.read_text(encoding="utf-8")
D, end = json.JSONDecoder().raw_decode(s, 8)
rest = s[end:]
byname = {d["n"]: d for d in D}
pl = lambda n, w: f"+{n} {w} slot" + ("" if n == "1" else "s")

def fx(d):
    t = re.sub(r"^Spellbook (\d+) slot;", r"\1-slot spellbook;", d["fx"])
    t = re.sub(r"\b(Moderate|moderate|high|very high) \+movement speed", lambda m: "+movement speed (" + m.group(1).lower() + ")", t)
    t = t.replace("Moderate +movement speed", "+Movement speed (moderate)")
    t = re.sub(r"^10% dodge", "+10% dodge", t)
    t = t.replace("Place blocks faster (-1 tick)", "Place blocks faster (-1 tick right-click delay)")
    t = re.sub(r"\+(\d+) slots? ([A-Z][a-z]+)", lambda m: pl(m.group(1), m.group(2)), t)
    if "+slot minion" in t:
        n = next((re.search(r"\d+", x).group() for x in d["st"] if x.startswith("Minion slots")), None)
        if n: t = t.replace("+slot minion", pl(n, "minion"))
    return t

def src(x):
    x = x.replace("The Calamities's", "The Calamities'")
    x = re.sub(r"(?<!the )(?<!The )\b(Ender Dragon|Elvenite Paladin|Goblin Lord|Iron Colossus|Warden|Wither)'s", r"the \1's", x)
    m = re.match(r"Hardest ingredient: (.+?) — from (.+?treasure bag.*)$", x)
    if m and m.group(1) in byname and byname[m.group(1)].get("g") != "Loot":
        k = byname[m.group(1)]
        key = re.search(r"Hardest ingredient: ([^—]+?) —", " ".join(k["src"]))
        via = f" with {key.group(1)}" if key else ""
        x = f"Hardest ingredient: {m.group(1)}, itself crafted{via} from {m.group(2)}"
    if re.search(r"[A-Za-z0-9)%]$", x): x += "."
    return x

n = 0
for d in D:
    a = (d["fx"], list(d["src"]))
    d["fx"] = fx(d); d["src"] = [src(x) for x in d["src"]]
    n += (d["fx"], d["src"]) != a
P.write_text("const D=" + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + rest, encoding="utf-8")
print("changed", n)
