#!/usr/bin/env python3
"""Every spell in the pack, read from the jars -> build/patches/spells.json.
Usage: python3 -I spells.py MODS_DIR SRG_SERVER_JAR SPELL_CONFIG_DIR
  MODS_DIR          the server pack's mods/ (383 jars of 6.6.6hf)
  SRG_SERVER_JAR    libraries/net/minecraft/server/1.20.1-*/server-1.20.1-*-srg.jar (class hierarchy of vanilla, field names of MobEffects)
  SPELL_CONFIG_DIR  the pack's config/irons_spellbooks_spell_config (per-spell files that override the jar's defaults)
A spell is a non-abstract class that extends io.redspace.ironsspellbooks.api.spells.AbstractSpell (Iron's Spells 'n Spellbooks and every addon that
adds spells to its registry). Its constructor says what the spell is: the id (ResourceLocation.fromNamespaceAndPath), DefaultConfig (min rarity,
school, max level, cooldown), and the fields baseManaCost, manaCostPerLevel, baseSpellPower, spellPowerPerLevel, castTime (ticks); getCastType() says
INSTANT, LONG or CONTINUOUS. The pack's config/irons_spellbooks_spell_config/<ns>/<spell>.json overrides what it names (rarity, max level, school,
cooldown, multipliers, enabled, allow_crafting). Name and description are the mod's own lang (spell.<ns>.<name>, .guide). The status effects a spell
puts on someone are the effect registry fields its class reads (resolved to ids through the registry's static initialiser).
Damage formulas live in each spell's getDamage() and are not read: the page says so. Nothing is guessed: what the scan cannot read stays null."""
import sys, os, re, json, zipfile, glob, collections, base64
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '..', 'gear'))
import classlib as CL
OUT = os.path.join(H, '..', 'patches')
AS = 'io/redspace/ironsspellbooks/api/spells/AbstractSpell'
INTF = {'baseManaCost': 'mana', 'manaCostPerLevel': 'manaPer', 'baseSpellPower': 'power', 'spellPowerPerLevel': 'powerPer', 'castTime': 'castTime'}


def num(k, i):
    m = i.mnemonic
    if m.startswith('iconst_'): return -1 if m == 'iconst_m1' else int(m[7:])
    if m in ('bipush', 'sipush'): return i.operands[0].value
    if m in ('dconst_0', 'dconst_1'): return float(m[7:])
    if m in ('fconst_0', 'fconst_1', 'fconst_2'): return float(m[7:])
    if m in ('ldc', 'ldc_w', 'ldc2_w'):
        t, v = CL.const(k, i.operands[0].value); return v if t in 'IJFD' else None
    return None


def read_ctor(cp, k):
    r = {}; strs = []; last = None; rar = sch = None
    for m in [x for x in k.methods if x.name.value == '<init>' and x.code][:1]:
        ins, _ = CL.code(k, m)
        for i in ins:
            mn = i.mnemonic
            if mn in ('ldc', 'ldc_w'):
                t, v = CL.const(k, i.operands[0].value)
                if t == 'S': strs.append(v)
            v = num(k, i)
            if v is not None: last = v
            if mn == 'getstatic':
                o, nm, d = CL.ref(k, i.operands[0].value)
                if o.endswith('SpellRarity'): rar = nm.lower()
                elif nm.endswith('_RESOURCE'): sch = nm[:-9].lower()
                elif d == 'Lnet/minecraft/resources/ResourceLocation;' and 'School' in o: sch = nm.replace('_RESOURCE', '').lower()
            elif mn == 'putfield':
                o, nm, d = CL.ref(k, i.operands[0].value)
                if nm in INTF and last is not None: r[INTF[nm]] = last
            elif mn.startswith('invoke') and mn != 'invokedynamic':
                o, nm, d = CL.ref(k, i.operands[0].value)
                if o.endswith('DefaultConfig'):
                    if nm == 'setMinRarity': r['rarity'] = rar
                    elif nm == 'setSchoolResource': r['school'] = sch
                    elif nm == 'setMaxLevel': r['maxLevel'] = last
                    elif nm == 'setCooldownSeconds': r['cooldown'] = last
                    elif nm == 'setAllowCrafting': r['craft'] = bool(last)
                elif o.endswith('ResourceLocation') and (nm == 'fromNamespaceAndPath' or (nm == '<init>' and d == '(Ljava/lang/String;Ljava/lang/String;)V')) and len(strs) >= 2 and 'id' not in r:
                    r['id'] = strs[-2] + ':' + strs[-1]
    return r


def cast_type(cp, k):
    m = CL.method(k, 'getCastType')
    if m and m.code:
        for i in CL.code(k, m)[0]:
            if i.mnemonic == 'getstatic':
                o, nm, d = CL.ref(k, i.operands[0].value)
                if o.endswith('CastType'): return nm
    return None


def main(mods_dir, srg_jar, cfg_dir):
    jars = sorted(glob.glob(os.path.join(mods_dir, '*.jar')))
    cp = CL.ClassPath([srg_jar] + jars, sort=False)
    lang = {}; modname = {}; jarmods = {}; iconidx = {}   # iconidx: (ns, spell) -> (jar, entry), assets/<ns>/textures/gui/spell_icons/<spell>.png
    for p in jars:
        z = zipfile.ZipFile(p); mt = CL.mods_toml(z)
        ids = [m.get('modId') for m in mt.get('mods', [])]; jarmods[p] = ids
        for m in mt.get('mods', []): modname[m.get('modId')] = m.get('displayName')
        for n in z.namelist():
            mi = re.fullmatch(r'assets/([a-z0-9_.-]+)/textures/gui/spell_icons/([^/]+)\.png', n)
            if mi: iconidx.setdefault((mi.group(1), mi.group(2)), (p, n))
            if re.fullmatch(r'assets/[a-z0-9_.-]+/lang/en_us\.json', n):
                try: d = json.loads(re.sub(r',(\s*[}\]])', r'\1', z.read(n).decode('utf-8', 'replace')))
                except Exception: continue
                for kk, v in d.items():
                    if isinstance(v, str) and (kk.startswith('spell.') or kk.startswith('school.')): lang.setdefault(kk, v)
    # effect registry fields -> registry name (static initialiser: the last plain name written before putstatic), so a spell's reads of MobEffectRegistry.X become ids
    fmap = {}
    def field_name(owner, field):
        if owner not in fmap:
            fmap[owner] = {}; k = cp.cf(owner)
            m = k and CL.method(k, '<clinit>')
            if m and m.code:
                ls = None
                for i in CL.code(k, m)[0]:
                    if i.mnemonic in ('ldc', 'ldc_w'):
                        t, v = CL.const(k, i.operands[0].value)
                        if t == 'S' and re.fullmatch(r'[a-z0-9_]+', v): ls = v
                    elif i.mnemonic == 'putstatic':
                        o, nm, d = CL.ref(k, i.operands[0].value)
                        if o == owner and ls: fmap[owner][nm] = ls
        return fmap[owner].get(field)
    eff_ids = {r['id'] for r in json.load(open(os.path.join(OUT, 'effects.json'), encoding='utf-8'))['effects']}
    spells = {}
    for p in jars:
        z = zipfile.ZipFile(p)
        for n in z.namelist():
            if not n.endswith('.class') or '$' in n or n.startswith('META-INF'): continue
            if b'AbstractSpell' not in z.read(n): continue
            cn = n[:-6]; k = cp.cf(cn)
            if not k or k.access_flags.get('acc_abstract') or AS not in cp.supers(cn)[1:]: continue
            r = read_ctor(cp, k)
            if 'id' not in r: continue
            r['ct'] = cast_type(cp, k)
            # effects: registry fields this class (and its nested classes) read
            fx = set()
            for c in [cn] + [x for x in cp.idx if x.startswith(cn + '$')]:
                ck = cp.cf(c)
                if not ck: continue
                for o, nm, d in CL.field_refs(ck):
                    if ('MobEffect' in o or 'MobEffects' in o) or d in ('Lnet/minecraftforge/registries/RegistryObject;', 'Lnet/minecraft/world/effect/MobEffect;'):
                        name = field_name(o, nm)
                        if not name: continue
                        ns = 'minecraft' if o == 'net/minecraft/world/effect/MobEffects' else next((i for i in jarmods.get(cp.jar(o), []) if i + ':' + name in eff_ids), None)
                        if ns and ns + ':' + name in eff_ids: fx.add(ns + ':' + name)
            r['fx'] = sorted(fx); r['jar'] = os.path.basename(p); r['cls'] = cn
            spells.setdefault(r['id'], r)
    rows = []; icons = {}
    for sid, r in sorted(spells.items()):
        ns, name = sid.split(':', 1)
        if (ns, name) in iconidx: icons[sid] = base64.b64encode(zipfile.ZipFile(iconidx[(ns, name)][0]).read(iconidx[(ns, name)][1])).decode()
        ov = {}
        f = os.path.join(cfg_dir, ns, name + '.json')
        if os.path.exists(f):
            try: ov = {kk.split(':', 1)[1]: v for kk, v in json.load(open(f)).items() if kk.startswith('irons_spellbooks:')}
            except Exception: ov = {}
        sch = ov.get('school', 'x:' + (r.get('school') or '')).split(':', 1)[1] or None
        row = {'id': sid, 'ns': ns, 'name': lang.get('spell.%s.%s' % (ns, name)), 'guide': lang.get('spell.%s.%s.guide' % (ns, name)), 'mod': modname.get(ns) or ns,
               'school': sch, 'schoolName': lang.get('school.%s.%s' % (ns if ('school.%s.%s' % (ns, sch)) in lang else 'irons_spellbooks', sch)) if sch else None,
               'rarity': ov.get('min_rarity', r.get('rarity')), 'maxLevel': ov.get('max_level', r.get('maxLevel')), 'cooldown': ov.get('cooldown_in_seconds', r.get('cooldown')),
               'mana': r.get('mana'), 'manaPer': r.get('manaPer'), 'manaMul': ov.get('mana_cost_multiplier'), 'power': r.get('power'), 'powerPer': r.get('powerPer'), 'powerMul': ov.get('power_multiplier'),
               'castTime': r.get('castTime'), 'cast': r['ct'], 'craft': ov.get('allow_crafting', r.get('craft')), 'enabled': ov.get('enabled', True), 'fx': r['fx'], 'cfg': bool(ov)}
        if sid == 'irons_spellbooks:none': continue   # NoneSpell: the empty slot, not a spell
        rows.append(row)
    json.dump({'spells': rows}, open(os.path.join(OUT, 'spells.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    json.dump({k: v for k, v in icons.items() if k in {r['id'] for r in rows}}, open(os.path.join(OUT, 'spell_icons.json'), 'w'), separators=(',', ':'), sort_keys=True)
    c = collections.Counter(r['mod'] for r in rows)
    print('spells', len(rows), dict(c), 'no name', sum(1 for r in rows if not r['name']), 'no school', sum(1 for r in rows if not r['school']), 'no cast type', sum(1 for r in rows if not r['cast']),
          'with effects', sum(1 for r in rows if r['fx']), 'icons', len(icons), 'config overrides', sum(1 for r in rows if r['cfg']), 'disabled', sum(1 for r in rows if not r['enabled']))


if __name__ == '__main__': main(*sys.argv[1:4])
