#!/usr/bin/env python3
"""The pack's other spell systems, from the game export and the jars -> build/patches/spells_<system>.json (plan: docs/plans/2026-11-15-spell-systems.md).
Usage: python3 -I spell_systems.py MODS_DIR
  MODS_DIR  the server pack's mods/ (383 jars of 6.6.6hf); its config/ is read beside it
The list and the numbers are the running game's (patches/game_registry.json, written by kubejs/server_scripts/lgw_registry.js in the full server, so
after the pack's config): Goety, every item whose class has getSpell() and whose id ends in _focus, with the spell's soul cost, cast ticks, cooldown
ticks and spell type. Names, descriptions and icons are the jars' (lang item.<ns>.<name> and .info, textures/item/<name>.png).
Ars Nouveau: every glyph of the game's GlyphRegistry (Ars Nouveau and its add-ons) with its mana cost and whether it is on; the tier is the pack's
config (config/<ns>/<glyph>.toml glyph_tier: the export printed the SpellTier object, and its three objects map one to one onto the configs' tiers,
checked here); the kind from the glyph's type index (1 form, 5 augment, 8 and 10 effect, 15 filter).
Brutality: every spell of its SpellRegistry with base mana, damage, cooldown and cast ticks and what one level adds to each (IBrutalitySpell.getActual*:
base + per level x level, before the caster's attributes and curios), its school and categories (the first is how it is cast: instant, channelling,
continuous); name and description lines from lang spell.brutality.<name>[.description.N], the icon from the spell's own getIcon() texture.
Nothing is guessed: what neither source has stays null."""
import sys, os, re, json, zipfile, glob, base64, collections
H = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(H, '..', 'patches')
CODES = re.compile(r'§.')


def jar_index(mods_dir):
    """lang (every en_us key), item textures and mod display names over every jar"""
    lang, tex, modname = {}, {}, {}; models = {}; files = {}; owner = {}
    for p in sorted(glob.glob(os.path.join(mods_dir, '*.jar'))):
        z = zipfile.ZipFile(p); first = None
        try:
            toml = z.read('META-INF/mods.toml').decode('utf-8', 'replace')
            for mid, dn in re.findall(r'modId\s*=\s*"([^"]+)"[\s\S]*?displayName\s*=\s*"([^"]+)"', toml): modname.setdefault(mid, dn); first = first or dn
        except KeyError: pass
        for n in z.namelist():
            m = re.match(r'assets/([a-z0-9_.-]+)/', n)
            if m and first: owner.setdefault(m.group(1), first)   # a namespace no mod is named after (Not Enough Glyphs registers arsomega: and toomanyglyphs: glyphs)
            m = re.fullmatch(r'assets/([a-z0-9_.-]+)/lang/en_us\.json', n)
            if m:
                try: d = json.loads(re.sub(r',(\s*[}\]])', r'\1', z.read(n).decode('utf-8-sig', 'replace')))
                except Exception: continue
                for k, v in d.items():
                    if isinstance(v, str): lang.setdefault(k, v)
            m = re.fullmatch(r'assets/([a-z0-9_.-]+)/textures/(.+)\.png', n)
            if m: files.setdefault((m.group(1), m.group(2)), (p, n))
            m = re.fullmatch(r'assets/([a-z0-9_.-]+)/models/item/([a-z0-9_]+)\.json', n)
            if m:
                try: models.setdefault((m.group(1), m.group(2)), json.loads(z.read(n).decode('utf-8-sig', 'replace')))
                except Exception: pass
    # an item's icon: its item model's layer0 texture (Goety keeps focus textures in item/focus/), else textures/item/<name>.png
    for (ns, name), mdl in models.items():
        l0 = (mdl.get('textures') or {}).get('layer0') if isinstance(mdl, dict) else None
        if l0:
            tns, tp = l0.split(':', 1) if ':' in l0 else ('minecraft', l0)
            if (tns, tp) in files: tex[(ns, name)] = files[(tns, tp)]
    for (ns, tp), v in files.items():
        mm = re.fullmatch(r'items?/([a-z0-9_]+)', tp)
        if mm: tex.setdefault((ns, mm.group(1)), v)
    for ns, dn in owner.items(): modname.setdefault(ns, dn)
    return lang, tex, modname, files


def goety(game, lang, tex, modname):
    rows, icons = [], {}
    for g in game.get('goety', []):
        if not g['id'].endswith('_focus'): continue   # goety:soul_healer and goetyawaken:starless_night carry a spell but are not focuses
        ns, name = g['id'].split(':', 1); t = (g.get('type') or 'NONE').lower()
        info = lang.get('item.%s.%s.info' % (ns, name)) or lang.get('item.%s.%s.desc' % (ns, name)) or lang.get('item.%s.%s.description' % (ns, name))
        rows.append({'id': g['id'], 'ns': ns, 'name': lang.get('item.%s.%s' % (ns, name)), 'guide': CODES.sub('', info) if info else None, 'mod': modname.get(ns) or ns,
                     'type': t, 'typeName': CODES.sub('', lang['spell.goety.' + t]) if 'spell.goety.' + t in lang else None,
                     'cost': g.get('cost'), 'cast': g.get('cast'), 'cooldown': g.get('cooldown'), 'kind': g.get('kind'), 'cls': g.get('cls')})
        if (ns, name) in tex: icons[g['id']] = base64.b64encode(zipfile.ZipFile(tex[(ns, name)][0]).read(tex[(ns, name)][1])).decode()
    rows.sort(key=lambda r: r['id'])
    json.dump({'spells': rows}, open(os.path.join(OUT, 'spells_goety.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    json.dump(icons, open(os.path.join(OUT, 'spell_icons_goety.json'), 'w'), separators=(',', ':'), sort_keys=True)
    print('goety focuses', len(rows), dict(collections.Counter(r['mod'] for r in rows)), 'no name', sum(1 for r in rows if not r['name']),
          'no description', sum(1 for r in rows if not r['guide']), 'no type name', sum(1 for r in rows if not r['typeName']), 'icons', len(icons))


ARS_KIND = {1: 'form', 5: 'augment', 8: 'effect', 10: 'effect', 15: 'filter'}


def ars(game, lang, tex, modname, cfg_dir):
    tier = {}
    for f in glob.glob(os.path.join(cfg_dir, '*', 'glyph_*.toml')) + glob.glob(os.path.join(cfg_dir, '*', '*.toml')):
        m = re.search(r'glyph_tier\s*=\s*(\d+)', open(f, encoding='utf-8', errors='replace').read())
        if m: tier.setdefault(os.path.basename(os.path.dirname(f)) + ':' + os.path.basename(f)[:-5], int(m.group(1)))
    rows, icons, by_obj = [], {}, collections.defaultdict(set)
    for g in game.get('ars', []):
        ns, name = g['id'].split(':', 1); t = tier.get(g['id']); by_obj[g.get('tier')].add(t)
        desc = g.get('desc') or lang.get('%s.glyph_desc.%s' % (ns, name))
        rows.append({'id': g['id'], 'ns': ns, 'name': g.get('name') or lang.get('item.%s.%s' % (ns, name)), 'guide': CODES.sub('', desc) if desc else None,
                     'mod': modname.get(ns) or ns, 'kind': ARS_KIND.get(g.get('type')), 'tier': t, 'cost': g.get('cost'), 'enabled': g.get('enabled'), 'cls': g.get('cls')})
        if (ns, name) in tex: icons[g['id']] = base64.b64encode(zipfile.ZipFile(tex[(ns, name)][0]).read(tex[(ns, name)][1])).decode()
    assert all(len(v) == 1 and None not in v for v in by_obj.values()), ('a SpellTier object with more than one config tier', dict(by_obj))
    rows.sort(key=lambda r: r['id'])
    json.dump({'spells': rows}, open(os.path.join(OUT, 'spells_ars.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    json.dump(icons, open(os.path.join(OUT, 'spell_icons_ars.json'), 'w'), separators=(',', ':'), sort_keys=True)
    print('ars glyphs', len(rows), dict(collections.Counter(r['mod'] for r in rows)), dict(collections.Counter(r['kind'] for r in rows)), 'tiers', dict(collections.Counter(r['tier'] for r in rows)),
          'no name', sum(1 for r in rows if not r['name']), 'no description', sum(1 for r in rows if not r['guide']), 'off', sum(1 for r in rows if r['enabled'] is False), 'icons', len(icons))


def brutality(game, lang, files, modname):
    rows, icons = [], {}
    for g in game.get('brutality', []):
        ns, name = g['id'].split(':', 1); cats = [c.strip().lower() for c in (g.get('cats') or '').strip('[]').split(',') if c.strip()]
        desc = [CODES.sub('', lang[k]).strip() for k in ['spell.%s.%s.description.%d' % (ns, name, n) for n in range(1, 10)] if k in lang]
        rows.append({'id': g['id'], 'ns': ns, 'name': lang.get('spell.%s.%s' % (ns, name)), 'guide': ' '.join(desc) or None, 'mod': modname.get(ns) or ns,
                     'school': g.get('school'), 'cast': cats[0] if cats else None, 'tags': cats[1:], 'cls': g.get('cls'),
                     **{k: g.get(k) for k in ('mana', 'manaLv', 'damage', 'damageLv', 'cooldown', 'cooldownLv', 'castLv')}, 'castTicks': g.get('cast')})
        icon = g.get('icon') or ''; m = re.fullmatch(r'([a-z0-9_.-]+):textures/(.+)\.png', icon)
        if m and (m.group(1), m.group(2)) in files: f = files[(m.group(1), m.group(2))]; icons[g['id']] = base64.b64encode(zipfile.ZipFile(f[0]).read(f[1])).decode()
    rows.sort(key=lambda r: r['id'])
    json.dump({'spells': rows}, open(os.path.join(OUT, 'spells_brutality.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    json.dump(icons, open(os.path.join(OUT, 'spell_icons_brutality.json'), 'w'), separators=(',', ':'), sort_keys=True)
    print('brutality spells', len(rows), dict(collections.Counter(r['school'] for r in rows)), dict(collections.Counter(r['cast'] for r in rows)),
          'no name', sum(1 for r in rows if not r['name']), 'no description', sum(1 for r in rows if not r['guide']), 'icons', len(icons))


def main(mods_dir):
    game = json.load(open(os.path.join(OUT, 'game_registry.json'), encoding='utf-8'))
    lang, tex, modname, files = jar_index(mods_dir)
    goety(game, lang, tex, modname)
    ars(game, lang, tex, modname, os.path.join(os.path.dirname(os.path.abspath(mods_dir)), 'config'))
    brutality(game, lang, files, modname)


if __name__ == '__main__': main(sys.argv[1])
