#!/usr/bin/env python3
"""The game's own translations, for the wiki's languages (docs/plans/2026-11-08-multilingual.md, step L1).

Names, effects, tooltips and Patchouli books belong to the mods and the game, which ship them in several languages. The wiki's
English strings are verbatim copies of `en_us`, so an English string finds its key and the key finds the official text.

  fetch   <manifest.json> <cache dir>   every jar of the CurseForge pack: keep only the lang and Patchouli files of LANGS, drop
                                        the jar. Resumable (a mod with a `.done` file is skipped). Needs the network:
                                        api.cfwidget.com (file names) and edge.forgecdn.net (jars).
  vanilla <cache dir> [1.20.1]          Minecraft's own lang files: en_us from the client jar, the others from the asset index.

  build   <cache dir>                   which of the wiki's own strings (build/src/*_data.js: run apply_all.sh first) have an official
                                        translation: writes `official/<lang>.json` = {names: id -> name, text: English -> text} for ru,
                                        pt (pt_br only), es (es_mx then es_es), vi, and prints the coverage. A string the game
                                        itself leaves in English (key missing, or same text) is left out: the wiki keeps English too.

The cache is raw material (tens of MB); it is not committed. The committed result is `build/i18n/official/<lang>.json`.
"""
import io, json, os, re, sys, time, urllib.request, urllib.parse, zipfile, concurrent.futures as cf

LANGS = ["en_us", "ru_ru", "pt_br", "pt_pt", "es_es", "es_mx", "vi_vn"]
_L = "|".join(LANGS)
WANT = [re.compile(r"^assets/[^/]+/lang/(%s)\.json$" % _L),
        re.compile(r"^(assets|data)/[^/]+/patchouli_books/[^/]+/(%s)/" % _L),
        re.compile(r"^(assets|data)/[^/]+/patchouli_books/[^/]+/book\.json$")]


def get(u, t=120, tries=4):
    err = None
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=t).read()
        except Exception as e:
            err = e; time.sleep(2 ** i)
    raise err


def keep(z, out):
    n = 0
    for name in z.namelist():
        if name.endswith("/") or not any(r.match(name) for r in WANT): continue
        p = os.path.join(out, name); os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f: f.write(z.read(name))
        n += 1
    return n


def fetch(manifest, cache):
    files = json.load(open(manifest))["files"]; os.makedirs(cache, exist_ok=True)
    mp = os.path.join(cache, "index.json"); idx = json.load(open(mp)) if os.path.exists(mp) else {}

    def job(f):
        pid, fid = str(f["projectID"]), f["fileID"]; out = os.path.join(cache, pid)
        if os.path.exists(os.path.join(out, ".done")): return pid, "have"
        try:
            d = json.loads(get("https://api.cfwidget.com/%s" % pid))
            nm = [x["name"] for x in d.get("files", []) if x["id"] == fid]
            if not nm: return pid, "NOFILE " + str(d.get("title"))
            data = get("https://edge.forgecdn.net/files/%d/%d/%s" % (fid // 1000, fid % 1000, urllib.parse.quote(nm[0])), 300)
            n = keep(zipfile.ZipFile(io.BytesIO(data)), out)
            os.makedirs(out, exist_ok=True); open(os.path.join(out, ".done"), "w").close()
            idx[pid] = {"title": d.get("title"), "type": d.get("type"), "file": nm[0], "fid": fid, "kept": n}
            return pid, "ok %d" % n
        except Exception as e:
            return pid, "ERR " + str(e)[:90]

    bad = 0
    with cf.ThreadPoolExecutor(6) as ex:
        for i, (pid, r) in enumerate(ex.map(job, files), 1):
            if not r.startswith(("ok", "have")): bad += 1; print(pid, (idx.get(pid) or {}).get("title"), r, flush=True)
            if i % 25 == 0:
                json.dump(idx, open(mp, "w"), indent=0); print("%d/%d" % (i, len(files)), flush=True)
    json.dump(idx, open(mp, "w"), indent=0)
    print("done:", len(files), "files,", bad, "not fetched")


def vanilla(cache, ver="1.20.1"):
    out = os.path.join(cache, "vanilla"); os.makedirs(out, exist_ok=True)
    man = json.loads(get("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"))
    v = json.loads(get([x["url"] for x in man["versions"] if x["id"] == ver][0]))
    z = zipfile.ZipFile(io.BytesIO(get(v["downloads"]["client"]["url"], 300)))
    open(os.path.join(out, "en_us.json"), "wb").write(z.read("assets/minecraft/lang/en_us.json"))
    objs = json.loads(get(v["assetIndex"]["url"]))["objects"]
    for lang in LANGS[1:]:
        o = objs.get("minecraft/lang/%s.json" % lang)
        if not o: print("vanilla: no", lang); continue
        open(os.path.join(out, lang + ".json"), "wb").write(get("https://resources.download.minecraft.net/%s/%s" % (o["hash"][:2], o["hash"])))
    print("vanilla", ver, sorted(os.listdir(out)))


# ---- build: which of the wiki's own strings have an official translation ------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, "..", "src")
# wiki language -> lang files, first one that has the key wins (D1: pt is Brazilian only; D2: Spanish tries Mexican first)
OUT = {"ru": ["ru_ru"], "pt": ["pt_br"], "es": ["es_mx", "es_es"], "vi": ["vi_vn"]}
DATA = {"data.js": ["D"], "gear_data.js": ["GE"],
        "wiki_data.js": ["SUM", "GOETY", "AE2", "BINFO", "GUIDE", "SIDEB", "SSTAT", "SDROP", "BEXTRA", "BGRAPH"]}
strip = lambda s: re.sub("§.", "", s).strip()


def load_wiki():
    """The generated data files (apply_all.sh writes them), read as JSON: {variable: value}."""
    out = {}
    for f, names in DATA.items():
        s = open(os.path.join(SRC, f), encoding="utf-8").read()
        for n in names:
            m = re.search(r"(?:^|[;\n])const %s=" % n, s)
            out[n] = json.JSONDecoder().raw_decode(s, m.end())[0]
    return out


def load_lang(cache):
    """{lang code: {key: text}} merged over every mod and vanilla (a key found first is kept; keys carry the namespace)."""
    L = {}
    def add(code, d):
        m = L.setdefault(code, {})
        for k, v in d.items():
            if isinstance(v, str) and v and k not in m: m[k] = v
    for p in sorted(os.listdir(cache)):
        for lp in glob_lang(os.path.join(cache, p)):
            try: add(os.path.basename(lp)[:-5], json.load(open(lp, encoding="utf-8")))
            except Exception: pass
    vd = os.path.join(cache, "vanilla")
    for f in os.listdir(vd): add(f[:-5], json.load(open(os.path.join(vd, f), encoding="utf-8")))
    return L


def glob_lang(d):
    a = os.path.join(d, "assets")
    for ns in (os.listdir(a) if os.path.isdir(a) else []):
        ld = os.path.join(a, ns, "lang")
        for f in (os.listdir(ld) if os.path.isdir(ld) else []):
            if f.endswith(".json"): yield os.path.join(ld, f)


def strings(o, acc):
    if isinstance(o, str): acc.append(o)
    elif isinstance(o, list): [strings(x, acc) for x in o]
    elif isinstance(o, dict): [strings(x, acc) for x in o.values()]


def build(cache):
    L, W = load_lang(cache), load_wiki(); en = L["en_us"]
    key_of = lambda i: next((k for t in ("item", "block") for k in ["%s.%s.%s" % (t, i.split(":")[0], i.split(":")[1].replace("/", "."))] if k in en), None)
    # some mods' lang files end a value with a stray comma ("Pergamino de Historia,"): dropped when the English has none
    tidy = lambda t, e: t if e.rstrip().endswith(",") else re.sub(r"[,\s]+$", "", t)
    pick = lambda lang, k: next((tidy(strip(L[c][k]), en[k]) for c in OUT[lang] if c in L and k in L[c]), None)
    rev = {}
    for k, v in en.items():
        v = strip(v)
        if len(v) >= 8: rev.setdefault(v, []).append(k)
    ids = [(d["id"], d["n"]) for d in W["D"]] + [(g["id"], g["n"]) for g in W["GE"]]
    allstr = []; strings(W, allstr)
    text = sorted({s for s in allstr if len(s) >= 8 and s in rev})
    print("wiki: %d item ids, %d strings (%d unique) of which %d are verbatim en_us text" % (len(ids), len(allstr), len(set(allstr)), len(text)))
    for lang in OUT:
        names, tx, amb = {}, {}, 0
        for i, n in ids:
            k = key_of(i); t = pick(lang, k) if k else None
            if t and t != strip(en[k]) and i not in names: names[i] = t
        for s in text:
            ts = {pick(lang, k) for k in rev[s]} - {None, s}
            if len(ts) == 1: tx[s] = ts.pop()
            elif len(ts) > 1: amb += 1
        d = os.path.join(HERE, "official"); os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, lang + ".json"), "w", encoding="utf-8") as f:
            f.write('{"names":' + json.dumps(names, ensure_ascii=False, sort_keys=True, indent=0).replace("\n}", "}") + ',\n"text":'
                    + json.dumps(tx, ensure_ascii=False, sort_keys=True, indent=0).replace("\n}", "}") + "}\n")
        print("%s (%s): names %d/%d (%.0f%%); text %d/%d (%.0f%%), %d ambiguous skipped"
              % (lang, "+".join(OUT[lang]), len(names), len(ids), 100 * len(names) / len(ids), len(tx), len(text), 100 * len(tx) / len(text), amb))


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 3 and a[0] == "fetch": fetch(a[1], a[2])
    elif len(a) >= 2 and a[0] == "vanilla": vanilla(a[1], *(a[2:3]))
    elif len(a) >= 2 and a[0] == "build": build(a[1])
    else: sys.exit(__doc__)
