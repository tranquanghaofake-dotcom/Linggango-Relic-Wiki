"""Translation memory helpers shared by build.py and the tools (docs/plans/2026-11-08-multilingual.md, L4).

A sentence is keyed by the hash of its English text, computed exactly as src/i18n.js `hsh` does (cyrb53 over UTF-16 code units).
tm/<lang>.json is {hash: {"en": English, "t": text or {one, few, many, other}}}; a plural sentence's English is "<one>\\u0001<other>".
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, "..", "src")
M32 = 0xFFFFFFFF
def _imul(a, b): return (a * b) & M32

def hsh(s):
    a, b = 0xdeadbeef, 0x41c6ce57
    u = s.encode("utf-16-le")
    for i in range(0, len(u), 2):
        c = u[i] | (u[i + 1] << 8)
        a = _imul(a ^ c, 2654435761); b = _imul(b ^ c, 1597334677)
    a = _imul(a ^ (a >> 16), 2246822507) ^ _imul(b ^ (b >> 13), 3266489909)
    b = _imul(b ^ (b >> 16), 2246822507) ^ _imul(a ^ (a >> 13), 3266489909)
    n = 4294967296 * (2097151 & b) + (a & M32)
    d = "0123456789abcdefghijklmnopqrstuvwxyz"; out = ""
    while True:
        n, r = divmod(n, 36); out = d[r] + out
        if not n: return out

def load_tm(lang):
    p = os.path.join(HERE, "tm", lang + ".json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

def write_tm(lang, tm):
    os.makedirs(os.path.join(HERE, "tm"), exist_ok=True)
    rows = ",\n".join(json.dumps(k, ensure_ascii=False) + ": " + json.dumps(tm[k], ensure_ascii=False) for k in sorted(tm, key=lambda k: tm[k]["en"]))
    open(os.path.join(HERE, "tm", lang + ".json"), "w", encoding="utf-8").write("{\n" + rows + "\n}\n")

_LIT = r'"((?:[^"\\]|\\.)*)"'
def scan_msgids(files=("app.js", "gear.js", "ux.js", "rooms.js")):
    """The English sentences the code writes out as literals: T("...") and TN(n, "one", "other"). Sentences built from variables are not here: trlog.js finds those."""
    out = set()
    for f in files:
        s = open(os.path.join(SRC, f), encoding="utf-8").read()
        for m in re.finditer(r'\b[TN]\(' + _LIT, s): out.add(json.loads('"' + m.group(1) + '"'))   # N("…") marks a sentence in a constant table (src/i18n.js)
        for m in re.finditer(r'\bT\(`([^`$\\]*)`', s): out.add(m.group(1))   # a sentence with double quotes inside is written between backticks
        for m in re.finditer(r'\bTN\([^"`\n]*?,\s*' + _LIT + r'\s*,\s*' + _LIT, s):
            out.add(json.loads('"' + m.group(1) + '"') + "\u0001" + json.loads('"' + m.group(2) + '"'))
    return out
