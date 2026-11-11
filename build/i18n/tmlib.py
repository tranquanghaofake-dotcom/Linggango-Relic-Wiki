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

# References: a translation may name an item or a term by its English between ⟦ ⟧, and the build writes that name in the language of the page ("Lleva la ⟦Frozen Blade⟧" shows
# the Spanish name of the Frozen Blade). One source for each name: change it in names.json and every sentence follows. ⟦English|gen⟧ asks for a case form (ru): forms/<lang>.json
# holds {"English": {"gen": "..."}}; a form that is missing leaves the English name, never a wrong case. See docs/I18N.md, "Names inside sentences".
REF = re.compile(r"\u27e6([^\u27e7|]+?)(?:\|(\w+))?\u27e7")

LEAD_ART = {"pt": {"own": ["O", "A", "Os", "As"], "before": {"o", "a", "os", "as", "um", "uma", "uns", "umas", "do", "da", "dos", "das", "no", "na", "nos", "nas", "ao", "à", "aos", "às", "pelo", "pela", "pelos", "pelas", "num", "numa"}},
            "es": {"own": ["El", "La", "Los", "Las"], "before": {"el", "la", "los", "las", "un", "una", "unos", "unas", "del", "al"}}}

def load_forms(lang):
    p = os.path.join(HERE, "forms", lang + ".json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

def resolve_refs(lang, t, lookup, forms=None):
    """t with every reference written in the language: lookup(english) -> its translation (or None), forms = case forms of this language. English stays where nothing is known."""
    if "\u27e6" not in t: return t
    forms = load_forms(lang) if forms is None else forms
    def sub(m):
        en, case = m.group(1), m.group(2)
        if case: r = forms.get(en, {}).get(case) or en
        else:
            r = lookup(en); r = r if isinstance(r, str) and r else en
        if lang in LEAD_ART and r != en:   # "del ⟦The Eye⟧": the name's own article goes when one stands before it ("del ojo", not "del el ojo")
            before = re.search(r"([\w'’À-ÿ]+)\W*$", m.string[:m.start()]); w = (before.group(1) if before else "").lower()
            if w in LEAD_ART[lang]["before"]:
                a = re.match(r"(%s)\s+(\S)" % "|".join(LEAD_ART[lang]["own"]), r)
                if a: r = a.group(2).lower() + r[a.end():] if lang == "es" else a.group(2) + r[a.end():]
        return r
    return REF.sub(sub, t)

def resolve_value(lang, t, lookup, forms=None):
    return resolve_refs(lang, t, lookup, forms) if isinstance(t, str) else {k: resolve_refs(lang, v, lookup, forms) for k, v in t.items()}

def official_names_by_english(lang):
    """{English name: the game's own name} from official/<lang>.json (names are by id there; the English of an id is read from data.js and gear_data.js)."""
    en_of = {}
    for f in ("data.js", "gear_data.js"):
        p = os.path.join(SRC, f)
        if not os.path.exists(p): continue
        for m in re.finditer(r'\{"id":"([^"]+)","n":"((?:[^"\\]|\\.)*)"', open(p, encoding="utf-8").read()): en_of[m.group(1)] = json.loads('"' + m.group(2) + '"')
    p = os.path.join(HERE, "official", lang + ".json")
    o = json.load(open(p, encoding="utf-8"))["names"] if os.path.exists(p) else {}
    return {en_of[i]: t for i, t in o.items() if i in en_of}

def name_lookup(lang, tm=None):
    """English -> translation for references: our entries first, then the game's own names."""
    tm = load_tm(lang) if tm is None else tm; off = official_names_by_english(lang)
    mine = {e["en"]: e["t"] for e in tm.values() if isinstance(e["t"], str)}
    return lambda en: mine.get(en) or off.get(en)

def resolved_tm(lang, tm=None):
    """A copy of the TM with every reference written out: what the reader sees (for the tools that read the text: qa.py, terms.py, status.py)."""
    tm = load_tm(lang) if tm is None else tm; look = name_lookup(lang, tm); forms = load_forms(lang)
    return {k: dict(e, t=resolve_value(lang, e["t"], look, forms)) for k, e in tm.items()}

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
