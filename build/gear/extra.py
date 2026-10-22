"""Weapons the wide scan left out because they are plain Items (no readable stats): Iron's staffs, Ars Nouveau spell
books, a few modded guns. Reads recipes, loot and gates the way gear_data.py does and writes patches/gear_extra.json.
Usage: extra.py W   (W = the work dir of build.sh: gates.json, rec.json, lang.json, relic_acts.json, ns2jar.json)
The list is hand-picked (extra_ids.json): each id exists in the pack's jars, has a valid recipe or a loot table, and its
Act comes out of the same ingredient/boss rules as every other item; items whose only ingredients are unmapped modded
materials (Act would read 0 for the wrong reason) were left out."""
import sys, json, os, re, pathlib
W = os.path.abspath(sys.argv[1]); H = pathlib.Path(__file__).resolve().parent
src = (H / 'gear_data.py').read_text()
sys.argv = ['x', W, '/dev/null']
os.chdir(W)
exec(src[:src.index('# ---------------- gear set ----------------')])
NS = set(json.load(open(W + '/ns2jar.json'))) | {'minecraft', 'forge', 'c', 'kubejs'}
def valid(r): return all((x.lstrip('#').split(':')[0] in NS) for x in r['ing'] if ':' in x and not x.startswith('#'))
ids = json.load(open(H / 'extra_ids.json'))
out = []
for k, lst in ids.items():
    for i in lst:
        allr = [r for r in rec['recipes'].get(i, []) if i not in r['ing']]
        rs = [r for r in allr if valid(r)][:2]; lt = rec['loot'].get(i, [])[:6]
        ga = gate.get(i, 0)
        ra = min([max([item_act(x) for x in r['ing']] or [0], key=oi) for r in rs], key=oi) if rs else None
        la = min([loot_act(t) for t in lt], key=oi) if lt else None
        sa = min([x for x in (ra, la) if x is not None] or [0], key=oi)
        act = max(ga, sa, key=oi)
        ns = i.split(':')[0]
        out.append({'id': i, 'n': nm(i), 'ns': ns, 'k': k, 'a': act, 'ga': ga, 'at': {}, 'src': [],
                    'rc': [{'t': r['t'], 'i': r['ing'][:12]} for r in rs], 'lt': lt, 'cls': [], 'off': {}, 'sc': {}})
json.dump(out, open(H.parent / 'patches' / 'gear_extra.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(out), 'extra weapons')
