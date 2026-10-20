"""Merge code stats (gear_base.json), pack attribute overrides (attributesetter), Keeper gates (progression_lock),
recipes/loot (rec.json) and names (lang.json) into the wiki's gear table GE.
Act numbers follow the wiki ladder: 0, 2 (after Iron Colossus) ... 12."""
import sys, json, glob, re, collections, math
S = sys.argv[1]; OUT = sys.argv[2]
base = json.load(open(S + '/gear_base.json'))
gates = json.load(open(S + '/gates.json'))
rec = json.load(open(S + '/rec.json'))
lang = json.load(open(S + '/lang.json'))
rel = json.load(open(S + '/relic_acts.json'))  # relic id -> t, plus NM names
AS = {}
for f in sorted(glob.glob(S + '/pack/src/overrides/kubejs/data/linggango/attributesetter/item/*.json')):
    for k, v in json.load(open(f)).items():
        AS.setdefault(k, []).extend(v)

GATE_ACT = {'iron': 2, 'golden': 3, 'emerald': 4, 'diamond': 5, 'netherite': 6, 'elvenite': 7, 'voiderite': 8, 'bloody': 10, 'helionite': 11}
GATE_NAME = {2: 'Iron Colossus', 3: 'the Goblin Lord', 4: 'Arion', 5: 'Eldorath', 6: 'Zoranth the Forgotten', 7: 'the Elvenite Paladin',
             8: 'Vaedric', 10: 'Sanghor', 11: 'Zoranth Newborn'}
ORDER = [0, 2, 3, 4, 5, 6, 6.1, 6.2, 6.3, 7, 8, 9, 10, 11, 12]
oi = ORDER.index
gate = {}
for tag, ids in gates.items():
    m = re.match(r'forge:(\w+?)_(tools|armor)$', tag)
    if not m: continue
    a = GATE_ACT[m.group(1)]
    for i in ids:
        if i not in gate or oi(a) > oi(gate[i]): gate[i] = a
# jar-side forge:*_tools / *_armor tags (Armageddon ships its own)
for tag, ids in rec['tags'].items():
    m = re.match(r'forge:(\w+?)_(tools|armor)$', tag)
    if m and m.group(1) in GATE_ACT:
        for i in ids:
            if i.startswith('#'): continue
            a = GATE_ACT[m.group(1)]
            if i not in gate or oi(a) > oi(gate[i]): gate[i] = a

# materials: vanilla progression gates the pack does not tag (dimension / vanilla boss), plus relic acts
MAT = {}
for i in ['minecraft:netherite_scrap', 'minecraft:netherite_ingot', 'minecraft:ancient_debris', 'minecraft:blaze_rod', 'minecraft:blaze_powder',
          'minecraft:ghast_tear', 'minecraft:quartz', 'minecraft:magma_cream', 'minecraft:wither_skeleton_skull', 'minecraft:nether_wart',
          'minecraft:glowstone_dust', 'minecraft:netherite_block', 'minecraft:crimson_stem', 'minecraft:warped_stem', 'minecraft:soul_sand',
          'minecraft:netherite_upgrade_smithing_template', 'minecraft:shroomlight', 'minecraft:basalt', 'minecraft:blackstone']:
    MAT[i] = 5
for i in ['minecraft:nether_star', 'minecraft:beacon']: MAT[i] = 6.2
for i in ['minecraft:dragon_egg', 'minecraft:dragon_head', 'minecraft:elytra', 'minecraft:shulker_shell', 'minecraft:chorus_fruit',
          'minecraft:popped_chorus_fruit', 'minecraft:end_rod', 'minecraft:purpur_block', 'minecraft:end_crystal']: MAT[i] = 6.3
for i in ['deeperdarker:warden_carapace', 'deeperdarker:heart_of_the_deep', 'deeperdarker:soul_crystal', 'deeperdarker:reinforced_echo_shard']: MAT[i] = 6.1
for k, v in rel['t'].items(): MAT.setdefault(k, v)
KEEPER_ENT = {'the_iron_colossus': 2, 'gobelin_lord': 3, 'the_gobelin_lord': 3, 'arion': 4, 'eldorath': 5, 'zoranth': 6,
              'warden': 6.1, 'wither': 6.2, 'ender_dragon': 6.3, 'elvenite_paladin': 7, 'vaedric': 8, 'discord': 9,
              'sanghor': 10, 'newborn': 11, 'nyxaris': 12}
def loot_act(tb):
    t = tb.split(':', 1)[1]
    for k, a in KEEPER_ENT.items():
        if k in t: return a
    if 'nether' in t or 'bastion' in t or 'fortress' in t: return 5
    if 'end_city' in t or 'end' == t.split('/')[-1]: return 6.3
    return 0

tagmap = {k: v for k, v in rec['tags'].items()}
memo = {}
def item_act(i, d=0):
    """earliest act an ingredient can be had"""
    if i.startswith('#'):
        vs = [x for x in tagmap.get(i[1:], []) if not x.startswith('#')]
        if not vs: return 0
        return min((item_act(x, d + 1) for x in vs[:12]), key=oi)
    if i in memo: return memo[i]
    if d > 6: return 0
    memo[i] = 0
    best = None
    if i in gate: best = gate[i]
    if i in MAT: best = MAT[i] if best is None else max(best, MAT[i], key=oi)
    if best is None:
        opts = []
        for r in rec['recipes'].get(i, [])[:4]:
            if any(x == i for x in r['ing']) or not valid(r): continue
            a = [item_act(x, d + 1) for x in r['ing']]
            opts.append(max(a, key=oi) if a else 0)
        for tb in rec['loot'].get(i, [])[:8]:
            opts.append(loot_act(tb))
        best = min(opts, key=oi) if opts else 0
    memo[i] = best
    return best

def nm(i):
    ns, n = i.split(':', 1)
    v = lang.get(i) or rel['nm'].get(i) or n.replace('_', ' ').title()
    return re.sub(r'§.', '', v).strip()

# ---------------- gear set ----------------
ids = set(gate) | set(AS)
for i, b in base.items():
    if b.get('k') or any(c in ('SwordItem', 'ArmorItem', 'BowItem', 'CrossbowItem', 'TridentItem', 'ProjectileWeaponItem', 'DiggerItem', 'AxeItem') for c in b.get('cls', [])):
        ids.add(i)
ids = {i for i in ids if i in lang or i in base}

TOOL = re.compile(r'(pickaxe|shovel|_hoe$|paxel|excavator|hammer_drill|_drill$|multitool|aiot|scythe_tool|mattock)')
def kind(i, b):
    c = ' '.join(b.get('cls', [])); k = b.get('k', '')
    n = i.split(':')[1]
    if k == 'armor' or 'ArmorItem' in c or re.search(r'_(helmet|chestplate|leggings|boots|hood|robe|cap|tunic|pants|crown|mask|greaves|sabatons|gauntlets)$', n):
        return 'armor'
    if TOOL.search(n) or k in ('pickaxe', 'shovel', 'hoe'): return 'tool'
    if re.search(r'Bow|Crossbow|Gun|Rifle|Pistol|Launcher|Blaster|Cannon|Shotgun|Sniper|Musket|Slingshot|Thrown|Javelin', c) or re.search(r'(bow|crossbow|gun|rifle|pistol|launcher|blaster|cannon|shotgun|sniper|revolver|musket|blunderbuss|minigun|repeater|slingshot)$', n) or k in ('bow', 'crossbow'):
        return 'ranged'
    if re.search(r'Staff|Wand|Scepter|Spell|Tome|Grimoire|Rod|Focus|Magic', c) or re.search(r'(staff|wand|scepter|sceptre|tome|grimoire|rod|orb|focus|codex)$', n):
        return 'magic'
    if re.search(r'Shield', c) or n.endswith('shield'): return 'shield'
    if k in ('sword', 'axe', 'trident', 'tool', 'tiered') or re.search(r'Sword|Axe|Weapon|Blade|Dagger|Spear|Hammer|Mace|Katana|Scythe|Halberd|Glaive|Lance|Club|Whip|Sickle|Tiered', c):
        return 'melee'
    return None

# attributes -> (role, weight) for armor/weapon role reading
def attr_key(a): return a.split(':')[-1].replace('generic.', '')
SPELL = re.compile(r'spell_power|spell_potency|mana|cast_time|cooldown_reduction|spell_resist|ars_nouveau|mana_regen')
SUMMON = re.compile(r'summon|minion|servant|sentry')
RANGED = re.compile(r'arrow|projectile|draw_speed|bow_|ranged')
MELEE = re.compile(r'attack_damage|attack_speed|crit|life_steal|lifesteal|armor_shred|armor_pierce|entity_reach|sweep')

def collect(i, b):
    """returns per-slot sums: {attr: {'add':x,'mul':y}} including code modifiers + pack attributesetter"""
    s = collections.defaultdict(lambda: {'add': 0.0, 'mul': 0.0})
    srcs = []
    for sl, ml in (b.get('mods') or {}).items():
        if sl not in ('MAINHAND', 'HEAD', 'CHEST', 'LEGS', 'FEET', 'field'): continue
        for a, amt, op in ml:
            k = attr_key(a); add = 'ADDITION' in str(op) or str(op) == '0'
            if k in ('attack_damage', 'attack_speed') and add:
                continue  # the weapon's own base (SwordItem or hand-built), read separately
            if k in ('armor', 'armor_toughness', 'knockback_resistance') and add and b.get('k') == 'armor':
                continue  # the armor piece's own base values
            s[k]['add' if add else 'mul'] += amt
            srcs.append(('code', k, amt, op))
        break
    for e in AS.get(i, []):
        k = attr_key(e['attribute']); op = e.get('operation', 'ADDITION')
        s[k]['add' if op == 'ADDITION' else 'mul'] += e['value']
        srcs.append(('pack', k, e['value'], op))
    return s, srcs

NS = set(json.load(open(S + '/ns2jar.json'))) | {'minecraft', 'forge', 'c', 'kubejs'}
def valid(r):
    # a recipe that names an item of a mod missing from the pack can never be crafted
    return all((x.lstrip('#').split(':')[0] in NS) for x in r['ing'] if ':' in x and not x.startswith('#'))
GE = []
skipped = collections.Counter()
for i in sorted(ids):
    b = base.get(i, {})
    kd = kind(i, b)
    if kd in (None, 'tool', 'shield'): skipped[kd] += 1; continue
    s, srcs = collect(i, b)
    # how to get
    allr = [r for r in rec['recipes'].get(i, []) if i not in r['ing']]
    rs = [r for r in allr if valid(r)][:2]
    lt = rec['loot'].get(i, [])[:6]
    ga = gate.get(i, 0)
    ra = min([max([item_act(x) for x in r['ing']] or [0], key=oi) for r in rs], key=oi) if rs else None
    la = min([loot_act(t) for t in lt], key=oi) if lt else None
    src_act = [x for x in (ra, la) if x is not None]
    sa = min(src_act, key=oi) if src_act else 0
    act = max(ga, sa, key=oi)
    if not rs and not lt and (i not in gate or allr): skipped['nosource'] += 1; continue
    g = {'id': i, 'n': nm(i), 'ns': i.split(':')[0], 'k': kd, 'a': act, 'ga': ga}
    if kd == 'armor':
        g['sl'] = b.get('slot') or next((t for t, p in (('HELMET', r'(helmet|hood|cap|crown|mask|hat)'), ('CHESTPLATE', r'(chestplate|robe|tunic|chest)'), ('LEGGINGS', r'(leggings|pants|greaves)'), ('BOOTS', r'(boots|sabatons|shoes)')) if re.search(p, i.split(':')[1])), None)
        for k2, f in (('arm', 'arm'), ('tough', 'tough'), ('kbr', 'kbr')):
            v = b.get(f)
            if isinstance(v, (int, float)): g[k2] = v
        for sl, ml in (b.get('mods') or {}).items():  # pieces that build their own modifier map replace the material values
            for a, amt, op in ml:
                k = attr_key(a)
                if 'ADDITION' in str(op) and k in ('armor', 'armor_toughness', 'knockback_resistance'):
                    g[{'armor': 'arm', 'armor_toughness': 'tough', 'knockback_resistance': 'kbr'}[k]] = amt
    else:
        if isinstance(b.get('dmg'), (int, float)): g['dmg'] = round(b['dmg'] + 1, 2)
        if isinstance(b.get('spd'), (int, float)): g['spd'] = round(b['spd'] + 4, 2)
        if g.get('dmg') is None:  # weapons with modifiers built by hand in code
            for sl, ml in (b.get('mods') or {}).items():
                for a, amt, op in ml:
                    if attr_key(a) == 'attack_damage' and 'ADDITION' in str(op): g['dmg'] = round(amt + 1, 2)
                    if attr_key(a) == 'attack_speed' and 'ADDITION' in str(op): g['spd'] = round(amt + 4, 2)
        # sanity: vanilla-style attack speed is 0 < speed <= 4 (a dagger is ~2.5); other values mean the mod computes it differently
        if g.get('spd') is not None and not (0 < g['spd'] <= 4.0): g.pop('spd'); g.pop('dmg', None); g['bad'] = 1
        if g.get('dmg') is not None and (g['dmg'] <= 1 or g['dmg'] > 80): g.pop('dmg'); g.pop('spd', None); g['bad'] = 1
    if kd == 'armor' and (g.get('arm') or 0) > 30: g.pop('arm'); g['bad'] = 1
    g['at'] = {k: [round(v['add'], 4), round(v['mul'], 4)] for k, v in s.items() if v['add'] or v['mul']}
    g['src'] = [[x[0], x[1], round(x[2], 4), x[3][:4]] for x in srcs]
    g['rc'] = [{'t': r['t'], 'i': r['ing'][:12]} for r in rs]
    g['lt'] = lt
    g['cls'] = b.get('cls', [])[:3]
    GE.append(g)

# ---------- armor sets ----------
SLOTW = r'(helmet|chestplate|leggings|boots|hood|robe|cap|tunic|pants|crown|mask|greaves|sabatons|hat|chest|legs|feet|head|armor|armour|helm|plate|leggins|shoes|robes)'
def setkey(i):
    n = i.split(':')[1]
    toks = [t for t in n.split('_') if not re.fullmatch(SLOTW, t)]
    return i.split(':')[0] + ':' + ('_'.join(toks) or n)
sets = collections.defaultdict(list)
for g in GE:
    if g['k'] == 'armor': sets[setkey(g['id'])].append(g)

# ---------- scoring ----------
def A(g, k, part='add'):
    v = g['at'].get(k); return v[0 if part == 'add' else 1] if v else 0.0
def sumk(g, rx, part='add'):
    return sum(v[0 if part == 'add' else 1] for k, v in g['at'].items() if re.search(rx, k))
def melee_score(g):
    if g.get('dmg') is None: return None
    hit = (g['dmg'] + A(g, 'attack_damage')) * (1 + A(g, 'attack_damage', 'mul'))
    spd = max(0.25, (g.get('spd') or 1.6) + A(g, 'attack_speed')) * (1 + A(g, 'attack_speed', 'mul'))
    cc = sumk(g, r'crit(ical)?_(strike_)?chance'); cd = sumk(g, r'crit(ical)?_(strike_)?damage') + sumk(g, r'crit(ical)?_(strike_)?damage', 'mul')
    ls = sumk(g, r'life_?steal')
    return hit * spd * (1 + min(cc, 1) * (0.5 + cd)) * (1 + 0.5 * ls) * (1 + 0.05 * A(g, 'entity_reach'))
def role_off(g):
    """offence bonus per role from attributes (fractions)"""
    o = {}
    o['MA'] = sumk(g, r'spell_power|spell_potency', 'mul') + sumk(g, r'spell_power|spell_potency') + 0.5 * sumk(g, r'cooldown_reduction|cast_time', 'mul') + sumk(g, r'max_mana') / 200 + 0.5 * sumk(g, r'mana_regen', 'mul')
    o['SU'] = sumk(g, SUMMON.pattern, 'mul') + sumk(g, SUMMON.pattern) * (0.05 if True else 1)
    o['RA'] = sumk(g, RANGED.pattern, 'mul') + sumk(g, RANGED.pattern)
    o['ME'] = A(g, 'attack_damage', 'mul') + A(g, 'attack_speed', 'mul') + sumk(g, r'crit') * 0.5 + sumk(g, r'life_?steal') + A(g, 'attack_damage') / 10
    return {k: max(0.0, v) for k, v in o.items()}
for g in GE:
    sc = {}
    off = role_off(g)
    if g['k'] == 'melee':
        m = melee_score(g)
        if m is not None: sc['ME'] = round(m, 3)
    elif g['k'] == 'ranged':
        sc['RA'] = round(1 + off['RA'] * 2 + 0.3 * sumk(g, r'crit'), 3)
    elif g['k'] == 'magic':
        sc['MA'] = round(1 + off['MA'] * 2, 3)
        if off['SU'] > 0: sc['SU'] = round(1 + off['SU'] * 2, 3)
    g['off'] = {k: round(v, 3) for k, v in off.items() if v > 0.0005}
    g['sc'] = sc
SETS = []
for k, ps in sorted(sets.items()):
    ps.sort(key=lambda g: ['HELMET', 'CHESTPLATE', 'LEGGINGS', 'BOOTS', None].index(g.get('sl')) if g.get('sl') in ('HELMET', 'CHESTPLATE', 'LEGGINGS', 'BOOTS') else 4)
    arm = sum((g.get('arm') or 0) + A(g, 'armor') for g in ps); tough = sum((g.get('tough') or 0) + A(g, 'armor_toughness') for g in ps)
    hp = sum(A(g, 'max_health') for g in ps); kbr = sum((g.get('kbr') or 0) + A(g, 'knockback_resistance') for g in ps)
    dtk = -sum(A(g, 'damage_taken') + A(g, 'damage_taken', 'mul') for g in ps)
    off = collections.Counter()
    for g in ps:
        for r, v in g['off'].items(): off[r] += v
    defense = arm + 0.8 * tough + 0.5 * hp + 10 * kbr + 60 * max(0, dtk)
    known = any(g.get('arm') is not None for g in ps)
    act = max((g['a'] for g in ps), key=oi)
    sc = {'TA': round(defense, 3)}
    for r, v in off.items():
        if v > 0.02: sc[r] = round(v * 100 + defense * 0.25, 3)
    ws = [p['n'].split() for p in ps]; pre = []
    for col in zip(*ws):
        if all(w == col[0] for w in col): pre.append(col[0])
        else: break
    name = ' '.join(pre) if pre and len(ps) > 1 else re.sub(r'\s+(Helmet|Chestplate|Leggings|Boots|Hood|Robe|Cap|Tunic|Pants|Crown|Mask|Greaves|Sabatons|Hat)$', '', ps[0]['n'])
    name = re.sub(r"\s+(Armor|Armour)$", '', name).strip() or ps[0]['n']
    SETS.append({'k': k, 'n': name, 'p': [g['id'] for g in ps], 'a': act, 'arm': round(arm, 2), 'tough': round(tough, 2), 'hp': round(hp, 2),
                 'kbr': round(kbr, 3), 'dtk': round(dtk, 3), 'off': {r: round(v, 3) for r, v in off.items() if v > 0.0005}, 'sc': sc, 'kn': known})
json.dump({'GE': GE, 'GS': SETS}, open(OUT, 'w'))
c = collections.Counter(g['k'] for g in GE)
print('gear', len(GE), dict(c), 'sets', len(SETS), 'skipped', dict(skipped))
print('melee with dmg', sum(1 for g in GE if g['k'] == 'melee' and g.get('dmg') is not None), '/', c['melee'])
print('armor with arm', sum(1 for g in GE if g['k'] == 'armor' and g.get('arm') is not None), '/', c['armor'])
print('acts', collections.Counter(g['a'] for g in GE))
