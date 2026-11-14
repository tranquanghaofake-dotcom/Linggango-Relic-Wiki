#!/usr/bin/env python3
"""Every status effect in the pack, read from the jars -> build/patches/effects.json (+ effect_icons.json).
Usage: python3 -I effects.py MODS_DIR SRG_SERVER_JAR VANILLA_CLIENT_JAR
  The list itself is the game's: patches/game_registry.json (pack_audit/kubejs/server_scripts/lgw_registry.js run in the server pack) names every
  registered effect with its category, colour and attribute modifiers; the jars add names, descriptions and icons. Without that file the list falls
  back to the jar scan below.
  MODS_DIR            the server pack's mods/ (383 jars of 6.6.6hf, build/README.md "pack_audit")
  SRG_SERVER_JAR      libraries/net/minecraft/server/1.20.1-*/server-1.20.1-*-srg.jar of the same pack (vanilla MobEffects, SRG member names)
  VANILLA_CLIENT_JAR  Mojang's client.jar 1.20.1 (vanilla names and icons)
What is read, per effect (the game's registry id is namespace:name):
  registration  a class that mentions the MOB_EFFECT registry and puts a name next to a register call (DeferredRegister.register(name, supplier),
                or vanilla's MobEffects.register(id, name, effect)); the effect's constructor gives category and colour, addAttributeModifier calls
                give the attribute modifiers (attribute, amount, operation). Anything the scan cannot read stays null, never guessed.
  lang          effect.<ns>.<name> is the name; any effect.<ns>.<name>.<x> key with text is the mod's own description
  texture       assets/<ns>/textures/mob_effect/<name>.png, kept only where the licence in the jar's mods.toml allows (build/README.md, Licence rules)
An effect found only in lang or textures (no registration seen) is listed with reg=false and src naming where it was seen."""
import sys, os, re, io, json, zipfile, glob, base64, collections
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '..', 'gear'))
import classlib as CL
OUT = os.path.join(H, '..', 'patches')
ATT = 'Lnet/minecraft/world/entity/ai/attributes/Attribute;'
ADD = '(' + ATT + 'Ljava/lang/String;DLnet/minecraft/world/entity/ai/attributes/AttributeModifier$Operation;)Lnet/minecraft/world/effect/MobEffect;'
OK_LIC = re.compile(r'\b(MIT|Apache|CC0|CC[- ]BY|LGPL|Unlicense|BSD|MPL)\b|LESSER GENERAL PUBLIC', re.I)   # CC BY(-NC) and the like; ARR_NO is never matched
BAD_LIC = re.compile(r'all\s*rights|ARR|proprietary|custom|no\s*derivatives|\bND\b', re.I)
NO_ICON = {'irons_spellbooks', 'terramity', 'relics', 'ars_nouveau', 'cataclysm', 'L_Ender', 'goety'}   # build/README.md: All Rights Reserved or unclear, even when the jar says otherwise


def ins_int(k, i):
    m = i.mnemonic
    if m.startswith('iconst_'): return -1 if m == 'iconst_m1' else int(m[7:])
    if m in ('bipush', 'sipush'): return i.operands[0].value
    if m in ('ldc', 'ldc_w'):
        t, v = CL.const(k, i.operands[0].value); return v if t == 'I' else None
    return None


def ins_dbl(k, i):
    m = i.mnemonic
    if m in ('dconst_0', 'dconst_1'): return float(m[7:])
    if m == 'ldc2_w':
        t, v = CL.const(k, i.operands[0].value); return v if t in 'DJ' else None
    if m in ('fconst_0', 'fconst_1', 'fconst_2'): return float(m[7:])
    if m in ('ldc', 'ldc_w'):
        t, v = CL.const(k, i.operands[0].value); return v if t == 'F' else None
    return None


def read_region(cp, k, ins, attr_name, seen=None):
    """category, colour, ctor class and attribute modifiers found in a run of instructions"""
    cat = col = None; ctor = []; mods = []; last = 0
    for n, i in enumerate(ins):
        m = i.mnemonic
        if m == 'getstatic':
            o, nm, d = CL.ref(k, i.operands[0].value)
            if o.endswith('MobEffectCategory') and cat is None:
                cat = nm.lower()
                for j in ins[n + 1:n + 4]:
                    v = ins_int(k, j)
                    if v is not None: col = v; break
        elif m == 'new':
            c = CL.class_name(k, i.operands[0].value)
            if not c.startswith('java/'): ctor.append(c)
        elif m.startswith('invoke'):
            if m == 'invokedynamic': continue
            o, nm, d = CL.ref(k, i.operands[0].value)
            if d == ADD:
                seg = ins[last:n]; at = op = am = None
                for j in reversed(seg):
                    if j.mnemonic == 'getstatic':
                        oo, nn, dd = CL.ref(k, j.operands[0].value)
                        if op is None and oo.endswith('AttributeModifier$Operation'): op = nn; continue
                        if at is None and dd in (ATT, 'Lnet/minecraftforge/registries/RegistryObject;', 'Ljava/util/function/Supplier;'): at = attr_name(oo, nn); continue
                    if am is None and ins_dbl(k, j) is not None: am = ins_dbl(k, j)
                    if at and op and am is not None: break
                mods.append({'attr': at, 'amount': am, 'op': op})
            last = n + 1
    return cat, col, ctor, mods


def main(mods_dir, srg_jar, client_jar):
    jars = sorted(glob.glob(os.path.join(mods_dir, '*.jar')))
    cp = CL.ClassPath([srg_jar] + jars, sort=False)
    alang = {}; lang = collections.defaultdict(dict); tex = {}; jarns = collections.defaultdict(set); jarinfo = {}; nsjar = {}
    for p in jars + [client_jar]:
        try: z = zipfile.ZipFile(p)
        except Exception: continue
        mt = CL.mods_toml(z) if p != client_jar else {}
        ids = [m.get('modId') for m in mt.get('mods', [])]; disp = {m.get('modId'): m.get('displayName') for m in mt.get('mods', [])}
        jarinfo[p] = {'ids': ids, 'lic': str(mt.get('license', '')), 'disp': disp}
        for n in z.namelist():
            m = re.match(r'assets/([a-z0-9_.-]+)/lang/en_us\.json$', n)
            if m:
                try: d = json.loads(re.sub(r',(\s*[}\]])', r'\1', z.read(n).decode('utf-8', 'replace')))
                except Exception: continue
                for kk, v in d.items():
                    if kk.startswith('effect.') and isinstance(v, str): lang[m.group(1)][kk] = v
                    elif kk.startswith('attribute.') and isinstance(v, str): alang.setdefault(kk, v)
                jarns[p].add(m.group(1)); nsjar.setdefault(m.group(1), p)
            m = re.match(r'assets/([a-z0-9_.-]+)/textures/mob_effect/(.+)\.png$', n)
            if m: tex[(m.group(1), m.group(2))] = (p, z.read(n)); jarns[p].add(m.group(1)); nsjar.setdefault(m.group(1), p)
        for i in ids: jarns[p].add(i); nsjar.setdefault(i, p)
    # attribute registry names: a static field of an Attribute type -> the string put next to it in <clinit> (vanilla Attributes, mod attribute holders)
    amap = {}
    def attr_name(owner, field):
        key = (owner, field)
        if key not in amap:
            k = cp.cf(owner); r = None
            if k:
                m = CL.method(k, '<clinit>')
                if m and m.code:
                    ins, _ = CL.code(k, m); ls = None
                    for i in ins:
                        if i.mnemonic in ('ldc', 'ldc_w'):
                            t, v = CL.const(k, i.operands[0].value); ls = v if t == 'S' else ls
                        elif i.mnemonic == 'putstatic':
                            o, nm, d = CL.ref(k, i.operands[0].value)
                            if o == owner: amap[(owner, nm)] = ls
            r = amap.get(key)
            amap.setdefault(key, None)
        return amap.get(key)
    is_effect = lambda c: c != 'net/minecraft/world/effect/MobEffectInstance' and 'net/minecraft/world/effect/MobEffect' in cp.supers(c)   # MobEffect itself or a subclass (not an instance: potions are built from those)
    # registration classes: the bytes mention the MOB_EFFECT registry (or are vanilla's MobEffects)
    regs = {}   # (ns, name) -> row
    classes = []
    for p in [srg_jar] + jars:
        z = zipfile.ZipFile(p)
        for n in z.namelist():
            if not n.endswith('.class') or n.startswith('META-INF'): continue
            if p == srg_jar and n != 'net/minecraft/world/effect/MobEffects.class': continue
            if p != srg_jar and not (b'MOB_EFFECT' in (d := z.read(n))): continue
            classes.append((p, n[:-6]))
    for p, cn in classes:
        k = cp.cf(cn)
        if not k: continue
        van = cn == 'net/minecraft/world/effect/MobEffects'
        strs = set(CL.strings(k))
        for m in k.methods:
            if not m.code: continue
            ins, _ = CL.code(k, m); ls = None; handle = None; start = 0
            for n, i in enumerate(ins):
                mn = i.mnemonic
                if mn in ('ldc', 'ldc_w'):
                    t, v = CL.const(k, i.operands[0].value)
                    if t == 'S' and re.fullmatch(r'[a-z0-9_./-]+', v): ls = v
                elif mn == 'invokedynamic':
                    try: handle = [a for t, a in CL.bootstrap(k, i.operands[0].value)[3] if t == 'H'][0]
                    except Exception: handle = None
                elif mn.startswith('invoke') and mn != 'invokedynamic':
                    o, nm, d = CL.ref(k, i.operands[0].value)
                    reg = (d.startswith('(Ljava/lang/String;') and 'Supplier;' in d) or (van and d.startswith('(ILjava/lang/String;'))
                    if reg and ls:
                        region = ins[start:n]; cat, col, ctor, mods = read_region(cp, k, region, attr_name)
                        if handle and handle.owner == cn:
                            lm = CL.method(k, handle.name, handle.desc)
                            if lm and lm.code:
                                li, _ = CL.code(k, lm); c2 = read_region(cp, k, li, attr_name)
                                cat, col, ctor, mods = cat or c2[0], col if col is not None else c2[1], ctor + c2[2], mods + c2[3]
                        ec = next((c for c in ctor if is_effect(c)), None)
                        if not ec: ls = None; handle = None; start = n + 1; continue   # an item, a block, a spell...: not a MobEffect
                        if cp.cf(ec):   # the effect's own constructor (and its superclasses) may set category, colour and modifiers
                            for sc in cp.supers(ec)[:4]:
                                ck = cp.cf(sc)
                                if not ck or sc.startswith('net/minecraft/'): break
                                im = CL.method(ck, '<init>')
                                for im in [x for x in ck.methods if x.name.value == '<init>' and x.code][:3]:
                                    ii, _ = CL.code(ck, im); c3 = read_region(cp, ck, ii, attr_name)
                                    cat, col, mods = cat or c3[0], col if col is not None else c3[1], mods + [x for x in c3[3] if x not in mods]
                        ns = 'minecraft' if van else None
                        if not ns:
                            cand = [x for x in jarns[p] if (x, ls) in tex or 'effect.%s.%s' % (x, ls) in lang.get(x, {})]
                            ns = cand[0] if len(cand) == 1 else next((x for x in cand if x in strs), cand[0] if cand else next(iter(jarinfo[p]['ids']), None))
                        if ns and (ns, ls) not in regs: regs[(ns, ls)] = {'cat': cat, 'color': col, 'mods': mods, 'jar': p}
                        ls = None; handle = None; start = n + 1
    blobs = {}
    def literal(p, name):
        if p not in blobs:
            z = zipfile.ZipFile(p); blobs[p] = b'\0'.join(z.read(n) for n in z.namelist() if n.endswith('.class'))
        return name.encode() in blobs[p]
    # merge with lang and textures
    gear = set()   # effects a weapon or armour piece applies, read from its bytecode (gear_fx.py): the effect object exists even when no registration of its name was followed
    try: gear = {f['effect'] for v in json.load(open(os.path.join(OUT, 'gear_fx.json'), encoding='utf-8')).values() for f in v.get('fx', []) if 'effect' in f}
    except Exception: pass
    rows = []; icons = {}; unconf = []
    try: game = {e['id']: e for e in json.load(open(os.path.join(OUT, 'game_registry.json'), encoding='utf-8'))['effects']}
    except Exception: game = None
    keys = set(regs) | {tuple(i.split(':', 1)) for i in gear if ':' in i} | {(ns, kk.split('.', 2)[2]) for ns, d in lang.items() for kk in d if kk.count('.') == 2 and kk.startswith('effect.')} | set(tex)
    if game: keys |= {tuple(i.split(':', 1)) for i in game}   # the game's registry decides which effects exist: game ids the scan missed are added, scan-only names the game lacks are dropped below
    for ns, name in sorted(keys):
        r = regs.get((ns, name)); L = lang.get(ns, {}); g = game.get('%s:%s' % (ns, name)) if game else None
        if not g and not r and '%s:%s' % (ns, name) not in gear:   # no MobEffect built next to this name: still an effect when it has an icon, a name and the name is written in the jar's code (registered by a pattern the scan does not follow); otherwise leftover assets or another kind of thing
            if not ((ns, name) in tex and 'effect.%s.%s' % (ns, name) in L and literal(tex[(ns, name)][0], name)): unconf.append('%s:%s' % (ns, name)); continue
        jar = r['jar'] if r else (tex[(ns, name)][0] if (ns, name) in tex else nsjar.get(ns))
        info = jarinfo.get(jar, {'ids': [], 'lic': '', 'disp': {}})
        title = L.get('effect.%s.%s' % (ns, name))
        desc = next((v for kk, v in sorted(L.items()) if kk.startswith('effect.%s.%s.' % (ns, name)) and v and not v.startswith('effect.')), None)
        mod = info['disp'].get(ns) or next(iter(info['disp'].values()), None) or ns
        if ns == 'minecraft': mod = 'Minecraft'
        ico = (ns, name) in tex
        lic = info['lic']; allow = ns == 'minecraft' or (ns not in NO_ICON and bool(lic) and not BAD_LIC.search(lic) and bool(OK_LIC.search(lic)))
        row = {'id': '%s:%s' % (ns, name), 'ns': ns, 'name': title, 'mod': mod, 'reg': bool(r) or bool(g), 'src': ('game' if g else 'reg' if r else 'gear' if '%s:%s' % (ns, name) in gear else 'name-in-code') + ('+lang' if title else '') + ('+tex' if ico else ''),
               'cat': (g['cat'] if g else r['cat'] if r else None), 'color': (g['color'] if g else r['color'] if r else None), 'mods': ([{'attr': m['attr'], 'amount': m['amount'], 'op': m['op']} for m in g['mods']] if g else r['mods'] if r else []), 'desc': desc, 'lic': lic, 'icon': bool(ico and allow)}
        if game and not g: unconf.append(row['id']); continue
        rows.append(row)
        if row['icon']: icons[row['id']] = base64.b64encode(tex[(ns, name)][1]).decode()
    used = sorted({m['attr'] for r in rows for m in r['mods'] if m['attr']})
    json.dump({'effects': rows, 'unconfirmed': unconf, 'attrs': {a: alang.get(a) for a in used}}, open(os.path.join(OUT, 'effects.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0, separators=(',', ':'), sort_keys=True)
    json.dump(icons, open(os.path.join(OUT, 'effect_icons.json'), 'w'), separators=(',', ':'), sort_keys=True)
    c = collections.Counter(r['src'] for r in rows)
    print('effects', len(rows), 'unconfirmed (lang or icon only)', len(unconf), dict(c), 'icons', len(icons), 'with category', sum(1 for r in rows if r['cat']), 'with modifiers', sum(1 for r in rows if r['mods']))


if __name__ == '__main__': main(*sys.argv[1:4])
