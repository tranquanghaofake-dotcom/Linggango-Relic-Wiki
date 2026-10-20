"""Build index.html from the v5 wiki (original/Linggango_Relic_Wiki.v5.html):
- "Path" -> "Act" in every reader-facing string (hash routes #act/... unchanged)
- gear data (GE, GS, GNS) + gear icons, the gear module and its CSS
usage: python3 build/gear/patch_wiki.py <gear.json> <gear_icons.json> <gns.json>"""
import sys, re, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, 'original', 'Linggango_Relic_Wiki.v5.html')
gear = json.load(open(sys.argv[1])); icons = json.load(open(sys.argv[2])); gns = json.load(open(sys.argv[3]))
s = open(BASE, encoding='utf8').read()

def act_words(t):
    t = t.replace('The Path', 'The Acts')
    t = re.sub(r'\bPaths\b', 'Acts', t)
    t = re.sub(r'\bPath\b', 'Act', t)
    # lowercase prose only: not <path>, .path, "path", path:, ip-path, regex groups
    t = re.sub(r'(?<![<\w/."\'-])paths\b(?![=:"\'\w-])', 'acts', t)
    t = re.sub(r'(?<![<\w/."\'-])path\b(?![=:"\'\w)-])', 'act', t)
    t = t.replace("boss path)", "boss act)").replace("a path's Keeper", "an Act's Keeper").replace('"side path"', '"side act"')
    t = t.replace('"path "+v===f.pl', '"act "+v===f.pl||"path "+v===f.pl')
    return t

parts = re.split(r'(<script>.*?</script>|<style>.*?</style>)', s, flags=re.S)
scripts = [i for i, p in enumerate(parts) if p.startswith('<script>')]
data_i, three_i, app_i = scripts[0], scripts[1], scripts[2]
for i, p in enumerate(parts):
    if i == three_i: continue
    if p.startswith('<style>'): continue
    if i == data_i:
        # only the prose fields of the relic data ("why", "src", "fx" strings), never ids or base64
        parts[i] = re.sub(r'"((?:[^"\\]|\\.){0,600})"', lambda m: '"' + act_words(m.group(1)) + '"' if ('Path' in m.group(1) or 'path' in m.group(1)) and ' ' in m.group(1) else m.group(0), p)
        continue
    parts[i] = act_words(p)
app = parts[app_i]
# old guide text said "Act"; it was converted to "Path" for display. Now the wiki says Act again.
app = re.sub(r'function pathText\(s\)\{[^}]*\}', 'function pathText(s){return String(s)}', app)
# search: act:IV works like path:IV
app = app.replace('path:"p",', 'path:"p",act:"p",acts:"p",')
parts[app_i] = app
s = ''.join(parts)
assert 'function pathText(s){return String(s)}' in s
# nav link
s = s.replace('<a href="#slot/*">Artifacts</a>', '<a href="#gear">Gear</a><a href="#slot/*">Artifacts</a>', 1)
# CSS
css = open(os.path.join(ROOT, 'build', 'gear', 'gear.css'), encoding='utf8').read()
k = s.index('</style>', s.index('<style>', 200))
s = s[:k] + '\n' + css + s[k:]
# data + icons after the data script, module after the app script
gd = '<script>\nconst GE=%s,GS=%s,GNS=%s;\nObject.assign(IC,%s);\n</script>' % (
    json.dumps(gear['GE'], separators=(',', ':')), json.dumps(gear['GS'], separators=(',', ':')),
    json.dumps(gns, separators=(',', ':')), json.dumps({k: v for k, v in icons.items()}, separators=(',', ':')))
mod = '<script>\n' + open(os.path.join(ROOT, 'build', 'gear', 'gear.js'), encoding='utf8').read() + '\n</script>'
idx = [m.end() for m in re.finditer(r'</script>', s)]
# order in the file: data, three.js, app
s = s[:idx[0]] + '\n' + gd + s[idx[0]:]
idx = [m.end() for m in re.finditer(r'</script>', s)]
s = s[:idx[-1]] + '\n' + mod + s[idx[-1]:]
for out in (os.path.join(ROOT, 'index.html'), os.path.join(ROOT, 'dist', 'Linggango_Relic_Wiki.html')):
    open(out, 'w', encoding='utf8').write(s)
print('wrote', len(s) / 1e6, 'MB')
