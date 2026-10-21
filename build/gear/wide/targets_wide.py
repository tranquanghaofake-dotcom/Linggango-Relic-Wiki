"""Wide gear target list over every jar.
Writes targets.json (ns -> [names], the explicit gear targets), targets_meta.json (id -> evidence list) and
ns_plan.json (ns -> {jars, want_all: every lang item name of the ns for class-based discovery}).
Evidence kinds: tag:<tag>  as:<file>  gate:<tag>  gated:<tier>  missing (equip_missing.json)  wiki (current GE)
                class~:<Class>/<kind> (name matches a gear class; confirmed later by the extractor)."""
import json, re, glob, os, sys, collections
G = sys.argv[1]; W = os.path.dirname(G)
K = G + '/pack/src/overrides/kubejs'
rec = json.load(open(G + '/rec.json')); tags = rec['tags']
lang = json.load(open(G + '/lang.json')); ns2jar = json.load(open(G + '/ns2jar.json'))
cg = json.load(open(G + '/clsgraph.json'))
# nested jar-in-jar mods (gx/nested, see tools/nest.py): add their namespaces and en_us names
import zipfile
for j in sorted(glob.glob(G + '/nested/*.jar')):
    z = zipfile.ZipFile(j); b = os.path.basename(j)
    for n in z.namelist():
        m = re.match(r'(assets|data)/([a-z0-9_.-]+)/', n)
        if m and b not in ns2jar.setdefault(m.group(2), []): ns2jar[m.group(2)].append(b)
        if re.match(r'assets/[^/]+/lang/en_us\.json$', n):
            try: d = json.loads(z.read(n).decode('utf8', 'ignore'))
            except Exception: continue
            for k, v in d.items():
                mm = re.match(r'item\.([a-z0-9_]+)\.([a-z0-9_/]+)$', k)
                if mm and isinstance(v, str): lang.setdefault(mm.group(1) + ':' + mm.group(2), v)
json.dump(ns2jar, open(G + '/ns2jar_wide.json', 'w')); json.dump(lang, open(G + '/lang_wide.json', 'w'))

def res(t, seen=None):
    seen = seen if seen is not None else set(); out = set()
    if t in seen: return out
    seen.add(t)
    for x in tags.get(t, []):
        x = x.rstrip('?')
        if x.startswith('#'): out |= res(x[1:], seen)
        else: out.add(x)
    return out

ev = collections.defaultdict(set)
# 1. gear tags
TAGRX = re.compile(r'^(minecraft:(swords|axes|trimmable_armor)|forge:(tools|armors)(/.*)?)$')
for t in tags:
    if TAGRX.match(t):
        for i in res(t): ev[i].add('tag:' + t)
# 2. attributesetter
for f in sorted(glob.glob(K + '/data/linggango/attributesetter/item/*.json')):
    for k in json.load(open(f)):
        ids = res(k[1:]) if k.startswith('#') else ({k} if ':' in k else set())
        for i in ids: ev[i].add('as:' + os.path.basename(f)[:-5])
# 3. gate tags: progression_lock forge:<tier>_tools/_armor, and linggango_tweaks gated/<tier>
for t, ids in json.load(open(G + '/gates.json')).items():
    for i in ids:
        for x in (res(i[1:]) if i.startswith('#') else {i}): ev[x].add('gate:' + t)
for f in glob.glob(K + '/data/linggango_tweaks/tags/items/gated/*.json'):
    tier = os.path.basename(f)[:-5]
    for v in json.load(open(f))['values']:
        v = v['id'] if isinstance(v, dict) else v
        for x in (res(v[1:]) if v.startswith('#') else {v}): ev[x].add('gated:' + tier)
# 4. earlier audit list + current wiki ids
for m in json.load(open(W + '/equip_missing.json')): ev[m['id']].add('missing')
s = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src', 'gear_data.js')).read()
GE, _ = json.JSONDecoder().raw_decode(s, s.index('[', s.index('const GE=')))
for e in GE: ev[e['id']].add('wiki')
# 5. name -> gear class (camel match), confirmed later in the VM
jar_ns = collections.defaultdict(set)
for ns, js in ns2jar.items():
    for j in js: jar_ns[j].add(ns)
lang_ns = collections.defaultdict(set)
for i in lang:
    ns, p = i.split(':', 1); lang_ns[ns].add(p)
bysimple = collections.defaultdict(list)
for c, k in cg['gear'].items():
    sn = c.split('/')[-1].split('$')[-1].lower()
    for suf in ('item', 'armoritem', 'armor', 'weapon', ''):
        if suf and sn.endswith(suf) and len(sn) > len(suf) + 2: bysimple[sn[:-len(suf)]].append((c, k))
    bysimple[sn].append((c, k))
gear_ns = collections.Counter()
for c in list(cg['gear']) + cg['attr']:
    for ns in jar_ns.get(cg['jar'].get(c), ()):
        if ns in lang_ns: gear_ns[ns] += 1
for ns in gear_ns:
    for p in lang_ns[ns]:
        for c, k in bysimple.get(p.replace('_', ''), [])[:2]:
            if any(ns in jar_ns.get(cg['jar'][c], ()) for _ in [0]): ev[ns + ':' + p].add('class~:%s/%s' % (c.split('/')[-1], k))

# ---- exclusions: curios accessories, pure tools, ids of mods not in the pack, vanilla (handled separately)
curio = set()
for t in tags:
    if t.startswith('curios:'): curio |= res(t)
TOOL = re.compile(r'(pickaxe|shovel|(^|_)hoe(_|$)|paxel|excavator|_drill$|^drill|multitool|aiot|mattock|fishing_rod|shears|wrench|spanner|_spade$|_saw$|lumber_axe|hammer_drill|_trowel$|^trowel)')
WTAG = re.compile(r'^tag:(minecraft:(swords|axes)|forge:tools/(swords?|axes?|bows?|crossbows?|tridents?|melee_weapon|ranged_weapon|weapons|daggers?|knives|scythes?|sickles?|whips?|claws?|hammers?|shields?)(/.*)?)$')
WNAME = re.compile(r'(sword|blade|scythe|sickle|dagger|katana|spear|halberd|glaive|mace|warhammer|battle|greataxe|cleaver|rapier|saber|sabre|claymore|lance|knife|_axe$|^axe_)')
def is_tool(i, e):
    """a pure tool: named as one (pickaxe/shovel/hoe/paxel/wrench/saw/...) or tagged wrench/fishing rod/mining tool,
    and not tagged as a weapon. Tool-class items with weapon names (infernal_forge, devastation, mossy_hammer) stay."""
    p = i.split(':')[1]
    tool_tag = any(re.match(r'tag:forge:tools/(paxels?|mining_tool|wrench(es)?|fishing_rods)$', x) for x in e)
    if not (TOOL.search(p) or tool_tag): return False
    return not any(WTAG.match(x) for x in e)
NS = set(ns2jar)
GEAR_EV = re.compile(r'^(tag:|as:|gate:|missing|wiki|class~:)')
STRONG = re.compile(r'^(tag:|as:|gate:|missing|wiki)')
hints = collections.defaultdict(set)
targets = collections.defaultdict(set); meta = {}; dropped = collections.Counter(); drop_ids = collections.defaultdict(list)
for i, e in sorted(ev.items()):
    if ':' not in i: continue
    ns, p = i.split(':', 1)
    why = None
    if ns == 'minecraft': why = 'vanilla (added from the server jar)'
    elif ns not in NS: why = 'namespace not in pack'
    elif i in curio and not any(x.startswith(('class~:', 'tag:minecraft:trimmable', 'tag:forge:armors', 'wiki')) for x in e): why = 'curios accessory'
    elif is_tool(i, e): why = 'pure tool'
    elif not any(GEAR_EV.match(x) for x in e): why = 'gated item with no gear evidence (kept as discovery-only want)'
    if why:
        dropped[why] += 1; drop_ids[why].append(i)
        if why.startswith('gated item'): meta[i] = sorted(e) + ['gated_only']
        continue
    meta[i] = sorted(e)
    if any(STRONG.match(x) for x in e): targets[ns].add(p)
    else: hints[ns].add(p)  # only a class-name match: the extractor must confirm a gear class
plan = {}
SHARED = {'minecraft', 'forge', 'c', 'curios', 'realmrpg', 'common'}  # shared asset namespaces: vanilla is added from the server jar
for ns in sorted((set(targets) | set(gear_ns) | set(hints)) - SHARED):
    js = ns2jar.get(ns, [])
    plan[ns] = {'jars': js, 'gear_classes': gear_ns.get(ns, 0), 'explicit': sorted(targets.get(ns, ())), 'hints': sorted(hints.get(ns, ())),
                'want_all': sorted(lang_ns.get(ns, set()) | targets.get(ns, set()))}
json.dump({k: sorted(v) for k, v in sorted(targets.items())}, open(G + '/targets.json', 'w'))
json.dump(meta, open(G + '/targets_meta.json', 'w'), indent=0)
json.dump(plan, open(G + '/ns_plan.json', 'w'))
json.dump({k: sorted(v) for k, v in drop_ids.items()}, open(G + '/targets_dropped.json', 'w'), indent=1)
json.dump(sorted(curio), open(G + '/curio_ids.json', 'w'))
print('hint-only', sum(len(v) for v in hints.values()), 'explicit targets', sum(len(v) for v in targets.values()), 'in', len(targets), 'ns; plan ns', len(plan), 'dropped', dict(dropped))
print('evidence', collections.Counter(x.split(':')[0] for i in meta for x in meta[i]))
