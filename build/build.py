#!/usr/bin/env python3
"""Assemble index.html and dist/Linggango_Relic_Wiki.html from build/src.

src/template.html  page shell with {{STYLE}} and {{<script file>}} slots
src/v5.css         the v5 + gear stylesheet (base layer; its !important flags are dropped so the skin wins)
style.game.css     the Minecraft GUI skin (loaded after the base)
"""
import pathlib, re, sys

B = pathlib.Path(__file__).resolve().parent
S = B / "src"
ROOT = B.parent
read = lambda p: p.read_text(encoding="utf-8")

def base_css():
    css = read(S / "v5.css")
    if "--raw" in sys.argv:
        return css
    # keep !important only where it guards hidden content or reduced motion
    out, depth, buf = [], 0, ""
    for block in re.split(r"(@media[^{]*\{)", css):
        out.append(block)
    css = "".join(out)
    def strip(m):
        sel = m.group(1)
        if "[hidden]" in sel:
            return m.group(0)
        return sel + "{" + m.group(2).replace("!important", "") + "}"
    reduced = re.compile(r"@media \(prefers-reduced-motion:reduce\)\{(?:[^{}]*\{[^{}]*\})*\}")
    keep = {}
    def hold(m):
        k = f"/*RM{len(keep)}*/"; keep[k] = m.group(0); return k
    css = reduced.sub(hold, css)
    css = re.sub(r"([^{}]+)\{([^{}]*)\}", strip, css)
    for k, v in keep.items():
        css = css.replace(k, v)
    return css

style = base_css() if "--raw" in sys.argv else base_css() + "\n" + read(B / "style.game.css")
# the display face, embedded so the offline file and the site look the same (fonts/README.md)
import base64
style = "".join('@font-face{font-family:Monocraft;font-weight:%d;font-display:swap;src:url(data:font/woff2;base64,%s) format("woff2")}\n'
                % (w, base64.b64encode((B / "fonts" / f).read_bytes()).decode()) for w, f in ((400, "Monocraft.woff2"), (700, "Monocraft-Bold.woff2"))) \
    + '@font-face{font-family:"Jersey 15";font-weight:400;font-display:swap;src:url(data:font/woff2;base64,%s) format("woff2")}\n' % base64.b64encode((B / "fonts" / "Jersey15.woff2").read_bytes()).decode() + style
# faces for the other languages (docs/plans/2026-11-08-multilingual.md, 13.1): Monocraft's own Cyrillic for ru (the faces above stop at Latin-1), and VT323 for Vietnamese
# titles and labels (html[lang=vi] in style.game.css), which no pixel font with Cyrillic covers. The offline file inlines them; the site serves them as files that the
# browser fetches only when text needs them (unicode-range for Cyrillic, the family itself for VT323), so an English reader downloads none of it.
EXTRA = [("Monocraft", "400", "U+0400-04FF,U+2116", "Monocraft-Cyrillic.woff2", ""), ("Monocraft", "700", "U+0400-04FF,U+2116", "Monocraft-Bold-Cyrillic.woff2", ""),
         ("VT323 vi", "400 900", None, "VT323-Vietnamese.woff2", "size-adjust:127%;")]   # 127%: VT323 is drawn smaller than Monocraft (the image the owner chose V2 from used 19 px for 15 px)
faces = lambda url: "".join('@font-face{font-family:"%s";font-weight:%s;font-display:swap;%s%ssrc:url(%s) format("woff2")}\n' % (fam, w, "unicode-range:%s;" % r if r else "", x, url(f)) for fam, w, r, f, x in EXTRA)
import hashlib
tpl = read(S / "template.html")
NAMES = ["data.js", "gear_data.js", "wiki_data.js", "wiki_pics.js", "scenes.js", "uiicons.js", "rooms.js", "i18n.js", "app.js", "gear.js", "ux.js"]
LATE = {"wiki_pics.js"}   # site only: pictures of detail pages, fetched after the first page is drawn (app.js loadPics)

# interface strings: build/i18n/ui.json -> one pack per language (docs/plans/2026-11-08-multilingual.md). English stays in the HTML and the JS
# (src/i18n.js), so the table is checked against it: every key used exists, English matches, {x} and tags match in every language
import json
def ui_packs():
    UI = json.loads(read(B / "i18n" / "ui.json")); ws = lambda x: re.sub(r"\s+", " ", x).strip(); used = {}
    for m in re.finditer(r'<(\w+)\b([^>]*?)\bdata-lgh?="([\w.]+)"([^>]*)>(.*?)</\1>', tpl, re.S):
        used[m.group(3)] = ws(m.group(5))
    for m in re.finditer(r'<\w+\b([^>]*\bdata-lga="([^"]+)"[^>]*)>', tpl):
        for pr in m.group(2).split(";"):
            a, k = pr.split("="); used[k] = ws(re.search(r'\b%s="([^"]*)"' % a, m.group(1)).group(1))
    for f in ("app.js", "gear.js", "ux.js", "rooms.js"):   # t("key", "English"): keys are written out in full so they can be found here
        for m in re.finditer(r'\bt\("([\w.]+)"\s*,\s*("(?:[^"\\]|\\.)*")', read(S / f)): used[m.group(1)] = ws(json.loads(m.group(2)))
        for m in re.finditer(r'\btn\("([\w.]+)"', read(S / f)): used.setdefault(m.group(1), None)
    for k, en in used.items():
        assert k in UI, "i18n: key %s is used but not in build/i18n/ui.json" % k
        assert en is None or ws(UI[k]["en"]) == en, "i18n: English of %s differs from the page: %r vs %r" % (k, ws(UI[k]["en"]), en)
    assert not set(UI) - set(used), "i18n: keys in ui.json that nothing uses: %s" % sorted(set(UI) - set(used))
    ph = lambda x: sorted(re.findall(r"\{\w+\}", json.dumps(x))); tags = lambda x: re.findall(r"</?\w+|href=\"[^\"]*\"", json.dumps(x))
    out = {}
    for lang in ("vi", "ru", "pt", "es"):
        out[lang] = {k: v[lang] for k, v in UI.items() if v.get(lang)}
        for k, t in out[lang].items():
            assert ph(t) == ph(UI[k]["en"]), "i18n: %s %s: {placeholders} differ from English" % (lang, k)
            assert tags(t) == tags(UI[k]["en"]), "i18n: %s %s: tags or links differ from English" % (lang, k)
    print("i18n:", len(UI), "keys;", ", ".join("%s %d" % (l, len(p)) for l, p in out.items()))
    return out
PACKS = ui_packs()
# sentences written in the code, keyed by the hash of their English (i18n/tmlib.py, tm/<lang>.json): checked here, shipped as the pack's `tr`
sys.path.insert(0, str(B / "i18n")); import tmlib, harvest
def official_overlay():
    """The game's own names and texts (i18n/official/<lang>.json, made by i18n/harvest.py) keyed like a sentence: by the hash of the English a page shows."""
    W = harvest.load_wiki(); en_of = {d["id"]: d["n"] for d in W["D"]}; en_of.update({g["id"]: g["n"] for g in W["GE"]})
    out = {}
    for lang in ("vi", "ru", "pt", "es"):
        p = B / "i18n" / "official" / (lang + ".json"); o = json.loads(read(p)) if p.exists() else {"names": {}, "text": {}}; tr = {}
        for i, t in o["names"].items():
            if i in en_of: tr[tmlib.hsh(en_of[i])] = t
        for en, t in o["text"].items(): tr.setdefault(tmlib.hsh(en), t)
        out[lang] = tr
    return out
def add_tm(packs):
    need = tmlib.scan_msgids(); logp = B / "i18n" / "tr_log.json"
    if logp.exists(): need |= set(json.loads(read(logp)))   # sentences built from variables, listed by i18n/trlog.js
    keepp = B / "i18n" / "keep.json"; keeps = json.loads(read(keepp)) if keepp.exists() else {}   # stay English by design: {"all": [...], "<lang>": [...]} (proper names, rarity names; vi keeps the game's slot and school names)
    seen = {}
    for n in need:
        assert seen.setdefault(tmlib.hsh(n), n) == n, "i18n: two sentences share a hash: %r and %r" % (seen[tmlib.hsh(n)], n)
    ph = lambda x: set(re.findall(r"\{\w+\}", x)); tg = lambda x: sorted(set(re.findall(r"</?\w+|href=\"[^\"]*\"", x)))
    for lang, pk in packs.items():
        keep = set(keeps.get("all", [])) | set(keeps.get(lang, []))
        tm, tr = tmlib.load_tm(lang), {}
        for k, e in tm.items():
            en, t = e["en"], e["t"]
            assert tmlib.hsh(en) == k, "i18n: tm/%s.json key %s is not the hash of %r" % (lang, k, en)
            forms = [t] if isinstance(t, str) else list(t.values())
            assert (isinstance(t, dict) and "other" in t and set(t) <= {"zero", "one", "two", "few", "many", "other"}) if "\u0001" in en else isinstance(t, str), "i18n: %s %r: plural forms are wrong" % (lang, en)
            for f in forms:
                assert ph(f) <= ph(en) and (not isinstance(t, str) or ph(f) == ph(en)), "i18n: %s %r: {placeholders} differ from English: %r" % (lang, en, f)
                assert tg(f) == tg(en) or ("\u0001" in en and set(tg(f)) <= set(tg(en))), "i18n: %s %r: tags or links differ from English" % (lang, en)
            tr[k] = t
        n0 = len(tr)
        kept = {tmlib.hsh(x) for x in keep}   # English on purpose (vi keeps slot and school names): the game's own translation of it is not merged either
        for k, t in OFFICIAL[lang].items():
            if k not in kept: tr.setdefault(k, t)   # a sentence of ours always wins over the game's text for the same English
        print("i18n %s: %d names and texts from the game's own translations added" % (lang, len(tr) - n0))
        pk["tr"] = tr; pk["keep"] = sorted(keep)   # keep: sentences that stay English on purpose (checks/i18n.js tells them from untranslated ones)
        miss = sorted(n for n in need if tmlib.hsh(n) not in tr and n not in keep)
        print("i18n %s: %d translated sentences; %d of %d sentences asked for are translated or kept in English on purpose%s" % (lang, len(tm), len(need) - len(miss), len(need), "" if not miss else "; untranslated: " + "; ".join(repr(m.replace("\u0001", " | "))[:48] for m in miss[:6]) + (" …" if len(miss) > 6 else "")))
OFFICIAL = official_overlay()
add_tm(PACKS)
PACKS_JS = "window.I18N=" + json.dumps(PACKS, ensure_ascii=False, separators=(",", ":")) + ";"

# dist: one self-contained file for offline use
html = tpl.replace("{{STYLE}}", "<style>\n" + style + faces(lambda f: "data:font/woff2;base64," + base64.b64encode((B / "fonts" / f).read_bytes()).decode()) + "\n</style>").replace("{{i18n_packs.js}}", PACKS_JS)
for name in NAMES:
    html = html.replace("{{%s}}" % name, read(S / name))
dist = ROOT / "dist" / "Linggango_Relic_Wiki.html"
dist.parent.mkdir(exist_ok=True)
dist.write_text(html, encoding="utf-8")

# site: a small index.html plus content-hashed files in static/, so browsers cache them
# and a rebuild always loads the new version
A = ROOT / "static"
A.mkdir(exist_ok=True)
for old in A.glob("*"):
    old.unlink()
def put(name, text, data=None):
    h = hashlib.sha1(data if data is not None else text.encode()).hexdigest()[:10]
    stem, ext = name.rsplit(".", 1)
    fn = f"{stem}.{h}.{ext}"
    if data is None: (A / fn).write_text(text, encoding="utf-8")
    else: (A / fn).write_bytes(data)
    return "static/" + fn
site = tpl.replace("{{STYLE}}", '<link rel="stylesheet" href="%s">' % put("style.css", style + faces(lambda f: put(f, "", (B / "fonts" / f).read_bytes()).split("/")[-1]))).replace("<script>\n{{i18n_packs.js}}\n</script>\n", "")
for lang, pk in PACKS.items():   # one small file per language, fetched only when a reader picks it (src/i18n.js langPack)
    site = site.replace("<html", '<html data-lang-%s="%s"' % (lang, put("lang-%s.js" % lang, "(window.I18N=window.I18N||{}).%s=%s;" % (lang, json.dumps(pk, ensure_ascii=False, separators=(",", ":"))))), 1)
for name in NAMES:
    if name in LATE:
        site = site.replace("<script>\n{{%s}}\n</script>\n" % name, "").replace("<html", '<html data-pics="%s"' % put(name, read(S / name)), 1)
        continue
    site = site.replace("<script>\n{{%s}}\n</script>" % name, '<script defer src="%s"></script>' % put(name, read(S / name)))
assert "{{" not in site, "template slot left unfilled"
(ROOT / "index.html").write_text(site, encoding="utf-8")
print("index.html", round(len(site.encode()) / 1e3, 1), "kB + static/;", dist, round(len(html.encode()) / 1e6, 2), "MB")
