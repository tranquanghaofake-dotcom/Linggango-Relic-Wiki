"""Index recipes and loot tables from mod jars + pack datapacks (kubejs/data), minus recipes the pack's
KubeJS scripts remove. Writes rec.json: {recipes: out_id -> [{t,ing:[ids/#tags],src}], loot: id -> [table], removed:[...]}"""
import sys, json, glob, zipfile, re, os, collections
S = sys.argv[1]
recipes = collections.defaultdict(list); loot = collections.defaultdict(set); tags = collections.defaultdict(set)
def ings(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ('result', 'output', 'results', 'outputs', 'conditions'): continue
            if k == 'item' and isinstance(v, str): acc.append(v)
            elif k == 'tag' and isinstance(v, str): acc.append('#' + v)
            else: ings(v, acc)
    elif isinstance(o, list):
        for x in o: ings(x, acc)
    elif isinstance(o, str) and re.match(r'^#?[a-z0-9_.-]+:[a-z0-9_/.-]+$', o): acc.append(o)
def outs(o):
    r = []
    for k in ('result', 'output', 'results', 'outputs'):
        v = o.get(k)
        for x in (v if isinstance(v, list) else [v]):
            if isinstance(x, str): r.append(x)
            elif isinstance(x, dict):
                i = x.get('item') or x.get('id') or (x.get('stack') or {}).get('item') if isinstance(x.get('stack'), dict) else x.get('item') or x.get('id')
                if isinstance(i, str): r.append(i)
    return r
def lootitems(o, acc):
    if isinstance(o, dict):
        if o.get('type') in ('minecraft:item', 'item') and isinstance(o.get('name'), str): acc.add(o['name'])
        for v in o.values(): lootitems(v, acc)
    elif isinstance(o, list):
        for x in o: lootitems(x, acc)
def feed(path, raw, src):
    m = re.match(r'data/([^/]+)/(recipes|loot_tables|tags/items)/(.+)\.json$', path)
    if not m: return
    try: o = json.loads(raw)
    except Exception: return
    ns, kind, p = m.groups()
    if kind == 'recipes':
        if not isinstance(o, dict): return
        a = []; ings(o, a)
        for out in outs(o): recipes[out].append({'id': ns + ':' + p, 't': str(o.get('type', '')), 'ing': a[:16], 'src': src})
    elif kind == 'loot_tables':
        a = set(); lootitems(o, a)
        for i in a: loot[i].add(ns + ':' + p)
    else:
        for v in (o.get('values', []) if isinstance(o, dict) else []):
            v = v.get('id') if isinstance(v, dict) else v
            if isinstance(v, str): tags[ns + ':' + p].add(v)
for j in sorted(glob.glob(S + '/pack/mods/*.jar')):
    try: z = zipfile.ZipFile(j)
    except Exception: continue
    for n in z.namelist():
        if n.startswith('data/') and n.endswith('.json') and ('/recipes/' in n or '/loot_tables/' in n or '/tags/items/' in n):
            feed(n, z.read(n), os.path.basename(j))
root = S + '/pack/src/overrides/kubejs'
for dp, _, fs in os.walk(root + '/data'):
    for f in fs:
        fp = os.path.join(dp, f); rel = os.path.relpath(fp, root)
        # kubejs datapack overrides replace same-path files
        feed(rel, open(fp, 'rb').read(), 'pack')
# KubeJS recipe removals / additions (regex over the scripts)
removed = set(); added = collections.defaultdict(list)
for f in glob.glob(root + '/server_scripts/**/*.js', recursive=True):
    t = open(f, encoding='utf8', errors='ignore').read()
    for m in re.finditer(r"remove\(\s*\{[^}]*output\s*:\s*['\"]([a-z0-9_]+:[a-z0-9_/]+)['\"]", t): removed.add(m.group(1))
    for m in re.finditer(r"\.(shaped|shapeless|smithing|custom|recipes\.[a-z_.]+)\(\s*(?:Item\.of\()?['\"](?:\d+x )?([a-z0-9_]+:[a-z0-9_/]+)['\"](.{0,900}?)\)\s*(?:\.id\(|;|\n)", t, re.S):
        a = re.findall(r"['\"](#?[a-z0-9_]+:[a-z0-9_/]+)['\"]", m.group(3))
        added[m.group(2)].append({'id': 'kubejs:' + os.path.basename(f), 't': 'kubejs:' + m.group(1), 'ing': a[:16], 'src': 'pack'})
for k in removed: recipes.pop(k, None)
for k, v in added.items(): recipes[k] = v + recipes.get(k, [])
json.dump({'recipes': recipes, 'loot': {k: sorted(v) for k, v in loot.items()}, 'tags': {k: sorted(v) for k, v in tags.items()}, 'removed': sorted(removed)}, open(S + '/rec.json', 'w'))
print(len(recipes), len(loot), len(tags), len(removed), sum(len(v) for v in added.values()))
