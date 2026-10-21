"""Merge ext_raw/<ns>.json (+ fallback.json + vanilla_gear.json) into gear_base.json and extract_report.json.
gear_base.json keeps the convention gear_data.py expects (dmg/spd = SwordItem-style modifier amounts) and adds
dmg_total / spd_total (what the tooltip shows: +1 base attack damage, +4 base attack speed), src, ev, and why (when a
stat could not be read)."""
import json, glob, os, sys, collections, re
G = sys.argv[1]
meta = json.load(open(G + '/targets_meta.json')); plan = json.load(open(G + '/ns_plan.json'))
van = json.load(open(G + '/vanilla_gear.json')); vchk = json.load(open(G + '/vanilla_check.json'))
fb = json.load(open(G + '/fallback.json')) if os.path.exists(G + '/fallback.json') else {}
s = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src', 'gear_data.js')).read()
GE, _ = json.JSONDecoder().raw_decode(s, s.index('[', s.index('const GE=')))
cur = {e['id']: e for e in GE}
num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)

def flat(rec): return [a for sl, l in (rec.get('mods') or {}).items() for a in l]
def totals(rec):
    """tooltip values: attack damage incl. base 1, attack speed incl. base 4"""
    k = rec.get('kind') or rec.get('k')
    if k == 'armor': return
    if num(rec.get('dmg')): rec['dmg_total'] = round(rec['dmg'] + 1, 4); rec['dmg_from'] = rec.get('dmg_from', 'ctor')
    if num(rec.get('spd')): rec['spd_total'] = round(rec['spd'] + 4, 4)
    m = rec.get('mods') or {}
    for sl in ('MAINHAND', 'field'):
        for a, amt, op in m.get(sl, []):
            if op != 'ADDITION': continue
            if a.endswith('attack_damage') and 'dmg_total' not in rec: rec['dmg_total'] = round(amt + 1, 4); rec['dmg_from'] = 'modifiers:' + sl
            if a.endswith('attack_speed') and 'spd_total' not in rec: rec['spd_total'] = round(amt + 4, 4)
def armor_vals(rec):
    if (rec.get('kind') or rec.get('k')) != 'armor': return
    for sl, l in (rec.get('mods') or {}).items():
        for a, amt, op in l:
            if op != 'ADDITION': continue
            f = {'generic.armor': 'arm_mod', 'generic.armor_toughness': 'tough_mod', 'generic.knockback_resistance': 'kbr_mod'}.get(a)
            if f and f not in rec: rec[f] = amt
def has_stats(rec):
    k = rec.get('kind') or rec.get('k')
    if k == 'item': return True  # plain Item subclass: no base attack/armor stats in code
    if k == 'attr': return bool(rec.get('mods')) or num(rec.get('dmg_total'))
    if k == 'armor': return num(rec.get('arm')) or num(rec.get('arm_mod'))
    if k in ('bow', 'crossbow', 'ranged', 'shield'): return True  # no melee base stats by design
    return num(rec.get('dmg_total'))

out = {}; fails = {}; per = {}; nongear = {}; hint_miss = {}; crashes = {}
for f in sorted(glob.glob(G + '/' + os.environ.get('RAW', 'ext_raw') + '/*.json')):
    d = json.load(open(f)); ns = os.path.basename(f)[:-5]; info = d['info']
    if 'crash' in info: crashes[ns] = info['crash']
    ex = set(plan.get(ns, {}).get('explicit', []))
    c = collections.Counter(explicit=len(ex), secs=info.get('secs', 0))
    for i, rec in d['records'].items():
        nm = i.split(':', 1)[1]
        rec['ev'] = [x for x in meta.get(i, []) if x != 'gated_only'] or ['discovered:class ' + (rec.get('cls') or ['?'])[0]]
        out[i] = rec; c['found'] += 1
        if nm not in ex: c['discovered'] += 1
    for i, why in d['fail'].items(): fails[i] = {'stage': 'registration', 'reason': why}
    nongear.update(d.get('nongear', {}))
    if d.get('hint_miss'): hint_miss[ns] = d['hint_miss']
    per[ns] = c
# fallbacks (class constructor / config / tier enum), computed by fallback.py for items mjvm left without stats
for i, r in fb.items():
    if i in out and has_stats(dict(out[i], **{})):
        pass
    if r.get('rec'):
        base = out.get(i, {})
        nr = dict(base); nr.update({k: v for k, v in r['rec'].items() if v is not None})
        nr['src'] = r['src']; nr.setdefault('ev', [x for x in meta.get(i, []) if x != 'gated_only'] or ['fallback'])
        if base.get('src') == 'mjvm': nr['src_note'] = 'mjvm: ' + (base.get('why_no_dmg') or 'no stats') + '; filled by ' + r['src']
        out[i] = nr; fails.pop(i, None)
        ns = i.split(':')[0]; per.setdefault(ns, collections.Counter())
        if i not in [k for k in out if k in fb] or True: per[ns]['fallback'] += 1
    elif r.get('why'):
        if i in fails: fails[i]['fallback'] = r['why']
for i, rec in van.items():
    rec = dict(rec); rec['ev'] = ['vanilla:minecraft Items.<clinit> (server-1.20.1 srg jar)']
    out[i] = rec
per['minecraft'] = collections.Counter(found=len(van), explicit=len(van))
# stats, totals, stat failures
for i, rec in out.items():
    totals(rec); armor_vals(rec)
    if not has_stats(rec):
        why = rec.get('why_no_dmg') or rec.get('error') or ('armor value not produced by the material / modifiers' if (rec.get('kind') or rec.get('k')) == 'armor'
              else 'constructor not modelled: no SwordItem/DiggerItem damage and no attack_damage modifier' if not rec.get('k') else 'damage not numeric')
        rec['why'] = why
        fails[i] = {'stage': 'stats', 'reason': why, 'cls': rec.get('cls', [])[:3]}
    rec.pop('why_no_dmg', None) if has_stats(rec) else None
for i, f in fails.items():
    ns = i.split(':')[0]; per.setdefault(ns, collections.Counter())[('fail_' + f['stage'])] += 1
for i, rec in out.items():
    ns = i.split(':')[0]
    if has_stats(rec): per.setdefault(ns, collections.Counter())['with_stats'] += 1
json.dump(dict(sorted(out.items())), open(G + '/gear_base.json', 'w'), indent=0)
newv = sorted(set(out) - set(cur)); gone = sorted(set(cur) - set(out))
kinds = collections.Counter((r.get('kind') or r.get('k') or '?') for r in out.values())
rep = {
    'items_total': len(out),
    'with_stats': sum(1 for r in out.values() if has_stats(r)),
    'kinds': dict(kinds),
    'src': dict(collections.Counter(r.get('src') for r in out.values())),
    'new_vs_current': len(newv), 'current_GE': len(cur), 'current_missing_from_new': len(gone),
    'failed': len(fails), 'failed_registration': sum(1 for f in fails.values() if f['stage'] == 'registration'),
    'failed_stats': sum(1 for f in fails.values() if f['stage'] == 'stats'),
    'per_mod': {ns: dict(c) for ns, c in sorted(per.items())},
    'failures': dict(sorted(fails.items())),
    'fail_reasons': dict(collections.Counter(re.sub(r'\(.*?\)', '(..)', f['reason']) for f in fails.values()).most_common()),
    'nongear_explicit': nongear, 'hint_unconfirmed': hint_miss, 'crashes': crashes,
    'dropped_targets': {k: len(v) for k, v in json.load(open(G + '/targets_dropped.json')).items()},
    'new_ids': newv, 'current_ids_not_extracted': {i: (fails.get(i) or {'reason': 'not a target / excluded: ' + ','.join(meta.get(i, ['no evidence']))})['reason'] for i in gone},
    'vanilla_check': {'mismatch': vchk['mismatch'], 'tiers': vchk['tiers'], 'armor_materials': vchk['armor_materials'], 'trident_modifiers': vchk['trident_modifiers']},
    'conventions': {'dmg/spd': 'modifier amounts as SwordItem/DiggerItem store them (gear_data.py adds base 1 / 4)',
                    'dmg_total/spd_total': 'tooltip values incl. base 1 attack damage / 4 attack speed',
                    'arm/tough/kbr': 'armor material values (per piece); arm_mod etc. = values from hand-built modifiers',
                    'pack attributesetter rebalances': 'not merged here (gear_data.py adds them)'},
}
json.dump(rep, open(G + '/extract_report.json', 'w'), indent=1)
print({k: rep[k] for k in ('items_total', 'with_stats', 'new_vs_current', 'current_missing_from_new', 'failed', 'failed_registration', 'failed_stats', 'kinds', 'src')})
print(rep['fail_reasons'])
