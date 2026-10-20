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
html = read(S / "template.html").replace("{{STYLE}}", "<style>\n" + style + "\n</style>")
for name in ["data.js", "gear_data.js", "wiki_data.js", "fx3d.js", "app.js", "gear.js"]:
    html = html.replace("{{%s}}" % name, read(S / name))
for out in (ROOT / "index.html", ROOT / "dist" / "Linggango_Relic_Wiki.html"):
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
print(ROOT / "index.html", round(len(html.encode()) / 1e6, 2), "MB")
