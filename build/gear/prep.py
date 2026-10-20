"""Inputs for the gear build: Keeper gate tags (progression_lock KubeJS), namespace -> jar, en_us names,
gear id targets, mod display names, and relic acts/names from the v5 wiki."""
import sys, json, zipfile, glob, re, collections, subprocess, os
W = sys.argv[1]; H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(H))
K = W + '/pack/src/overrides/kubejs/server_scripts/progression_lock'
js = r'''const fs=require("fs");const T={};
global.ServerEvents={tags:(t,f)=>{if(t!=="item")return;f({add:(tag,xs)=>{(T[tag]=T[tag]||new Set());[].concat(xs).forEach(x=>T[tag].add(x))},remove(){},removeAll(){},get:()=>({add(){},remove(){}})})}};
for(const f of ["tags.js","tags_gapfill.js","removed_tags.js"])eval(fs.readFileSync(process.argv[1]+"/"+f,"utf8"));
console.log(JSON.stringify(Object.fromEntries(Object.entries(T).map(([k,v])=>[k,[...v]]))))'''
json.dump(json.loads(subprocess.check_output(['node', '-e', js, K])), open(W + '/gates.json', 'w'))
ns2jar = collections.defaultdict(set); lang = {}; gns = {}
def langs(d):
    for k, v in d.items():
        m = re.match(r'item\.([a-z0-9_]+)\.([a-z0-9_/]+)$', k)
        if m and isinstance(v, str): lang[m.group(1) + ':' + m.group(2)] = v
for j in sorted(glob.glob(W + '/pack/mods/*.jar')):
    try: z = zipfile.ZipFile(j)
    except Exception: continue
    for n in z.namelist():
        m = re.match(r'(assets|data)/([a-z0-9_.-]+)/', n)
        if m: ns2jar[m.group(2)].add(os.path.basename(j))
        if re.match(r'assets/[^/]+/lang/en_us\.json$', n):
            raw = z.read(n).decode('utf8', 'ignore')
            try: langs(json.loads(raw))
            except Exception: langs(dict(re.findall(r'"([^"]+)"\s*:\s*"((?:[^"\\]|\\.)*)"', raw)))
    try:
        t = z.read('META-INF/mods.toml').decode('utf8', 'ignore')
        for blk in re.split(r'\[\[mods\]\]', t)[1:]:
            a = re.search(r'modId\s*=\s*"([^"]+)"', blk); b = re.search(r'displayName\s*=\s*"([^"]+)"', blk)
            if a and b: gns[a.group(1)] = b.group(1)
    except KeyError: pass
for f in glob.glob(W + '/pack/src/overrides/kubejs/assets/*/lang/en_us.json'):
    try: langs(json.load(open(f)))
    except Exception: pass
json.dump({k: sorted(v) for k, v in ns2jar.items()}, open(W + '/ns2jar.json', 'w'))
json.dump(lang, open(W + '/lang.json', 'w')); json.dump(gns, open(W + '/gns.json', 'w'))
g = json.load(open(W + '/gates.json')); ids = {x for v in g.values() for x in v}
for f in glob.glob(W + '/pack/src/overrides/kubejs/data/linggango/attributesetter/item/*.json'): ids |= set(json.load(open(f)))
nss = {i.split(':')[0] for i in ids}; t = collections.defaultdict(set)
for i in ids: t[i.split(':')[0]].add(i.split(':')[1])
for k in lang:
    ns, n = k.split(':')
    if ns in nss: t[ns].add(n)
json.dump({k: sorted(v) for k, v in t.items()}, open(W + '/targets.json', 'w'))
# relic acts and names from the v5 wiki's data script
s = open(ROOT + '/original/Linggango_Relic_Wiki.v5.html', encoding='utf8').read()
data = re.findall(r'<script>(.*?)</script>', s, re.S)[0]
open(W + '/_d.js', 'w', encoding='utf8').write(data.replace('window.B3=B3;', '') + ';const t={};D.forEach(d=>t[d.id]=d.t);process.stdout.write(JSON.stringify({t,nm:NM}))')
out = subprocess.check_output(['node', W + '/_d.js'], cwd=W); os.remove(W + '/_d.js')
open(W + '/relic_acts.json', 'wb').write(out)
print('prep: gates', len(ids), 'lang', len(lang), 'mods', len(gns))
