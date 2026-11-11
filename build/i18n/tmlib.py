"""Translation memory helpers shared by build.py and the tools (docs/plans/2026-11-08-multilingual.md, L4).

A sentence is keyed by the hash of its English text, computed exactly as src/i18n.js `hsh` does (cyrb53 over UTF-16 code units).
tm/<lang>/<domain>.json is {hash: {"en": English, "t": text or {one, few, many, other}}}; a plural sentence's English is "<one>\\u0001<other>".
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

def tm_dir(lang): return os.path.join(HERE, "tm", lang)

def load_tm(lang):
    """{hash: {"en", "t", "s", ...}} from tm/<lang>/<domain>.json (the entry also gets "d": its domain, not written back); tm/<lang>.json is read if the folder does not exist yet."""
    d, tm = tm_dir(lang), {}
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if not f.endswith(".json"): continue
            for k, e in json.load(open(os.path.join(d, f), encoding="utf-8")).items():
                assert k not in tm, "tm/%s: %s is in two domain files (%s and %s)" % (lang, repr(e["en"]), tm[k]["d"], f[:-5])
                e["d"] = f[:-5]; tm[k] = e
        return tm
    p = os.path.join(HERE, "tm", lang + ".json")
    if os.path.exists(p):
        for k, e in json.load(open(p, encoding="utf-8")).items(): e["d"] = e.get("d", "vocab"); tm[k] = e
    return tm

def write_tm(lang, tm):
    """Writes each domain to its own file, entries sorted by English (stable diffs); a domain with no entries has no file; the entry's "d" says where it goes (default vocab)."""
    d = tm_dir(lang); os.makedirs(d, exist_ok=True); by = {}
    for k, e in tm.items(): by.setdefault(e.get("d", "vocab"), {})[k] = {x: y for x, y in e.items() if x != "d"}
    for f in os.listdir(d):
        if f.endswith(".json") and f[:-5] not in by: os.remove(os.path.join(d, f))
    for dom, rows in by.items():
        body = ",\n".join(json.dumps(k, ensure_ascii=False) + ": " + json.dumps(rows[k], ensure_ascii=False) for k in sorted(rows, key=lambda k: rows[k]["en"]))
        open(os.path.join(d, dom + ".json"), "w", encoding="utf-8").write("{\n" + body + "\n}\n")
    old = os.path.join(HERE, "tm", lang + ".json")
    if os.path.exists(old): os.remove(old)

def _nums(t): return sorted(re.findall(r"\d+", re.sub(r"(?<=\d)[.,](?=\d)", "", t)))
def _phs(t): return sorted(re.findall(r"%\d?\$?[sd]|\{\w+\}|\[\]", t))

def official_text_ok(en, t, english):
    """Is a mod's own translation of `en` really a translation of it? A mod's ru_ru.json is often older than its en_us.json, so the key holds the text of another version:
    the numbers differ ("+0.1% Attack Speed" => "+10% Knockback Resistance"), or the text is another English string of the file. Such a pair is not used. `english` = the set of English texts of the file."""
    return _nums(en) == _nums(t) and _phs(en) == _phs(t) and not (t in english and t != en)

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
