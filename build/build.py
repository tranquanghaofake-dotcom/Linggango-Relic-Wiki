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
                % (w, base64.b64encode((B / "fonts" / f).read_bytes()).decode()) for w, f in ((400, "Monocraft.woff2"), (700, "Monocraft-Bold.woff2"))) + style
import hashlib
tpl = read(S / "template.html")
NAMES = ["data.js", "gear_data.js", "wiki_data.js", "scenes.js", "uiicons.js", "rooms.js", "fx3d.js", "app.js", "gear.js", "ux.js"]

# dist: one self-contained file for offline use
html = tpl.replace("{{STYLE}}", "<style>\n" + style + "\n</style>")
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
def put(name, text):
    h = hashlib.sha1(text.encode()).hexdigest()[:10]
    stem, ext = name.rsplit(".", 1)
    fn = f"{stem}.{h}.{ext}"
    (A / fn).write_text(text, encoding="utf-8")
    return "static/" + fn
site = tpl.replace("{{STYLE}}", '<link rel="stylesheet" href="%s">' % put("style.css", style))
for name in NAMES:
    site = site.replace("<script>\n{{%s}}\n</script>" % name, '<script defer src="%s"></script>' % put(name, read(S / name)))
assert "{{" not in site, "template slot left unfilled"
(ROOT / "index.html").write_text(site, encoding="utf-8")
print("index.html", round(len(site.encode()) / 1e3, 1), "kB + static/;", dist, round(len(html.encode()) / 1e6, 2), "MB")
