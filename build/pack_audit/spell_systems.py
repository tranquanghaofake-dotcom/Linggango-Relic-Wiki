#!/usr/bin/env python3
"""The pack's other spell systems, from the game export and the jars -> build/patches/spells_<system>.json (plan: docs/plans/2026-11-15-spell-systems.md).
Usage: python3 -I spell_systems.py MODS_DIR
  MODS_DIR  the server pack's mods/ (383 jars of 6.6.6hf)
The list and the numbers are the running game's (patches/game_registry.json, written by kubejs/server_scripts/lgw_registry.js in the full server, so
after the pack's config): Goety, every item whose class has getSpell() and whose id ends in _focus, with the spell's soul cost, cast ticks, cooldown
ticks and spell type. Names, descriptions and icons are the jars' (lang item.<ns>.<name> and .info, textures/item/<name>.png).
Nothing is guessed: what neither source has stays null."""
import sys, os, re, json, zipfile, glob, base64, collections
H = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(H, '..', 'patches')
CODES = re.compile(r'§.')


def jar_index(mods_dir):
    """lang (every en_us key), item textures and mod display names over every jar"""
    lang, tex, modname = {}, {}, {}; models = {}; files = {}
    for p in sorted(glob.glob(os.path.join(mods_dir, '*.jar'))):
        z = zipfile.ZipFile(p)
        try:
            toml = z.read('META-INF/mods.toml').decode('utf-8', 'replace')
            for mid, dn in re.findall(r'modId\s*=\s*"([^"]+)"[\s\S]*?displayName\s*=\s*"([^"]+)"', toml): modname.setdefault(mid, dn)
        except KeyError: pass
        for n in z.namelist():
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
    return lang, tex, modname


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


def main(mods_dir):
    game = json.load(open(os.path.join(OUT, 'game_registry.json'), encoding='utf-8'))
    lang, tex, modname = jar_index(mods_dir)
    goety(game, lang, tex, modname)


if __name__ == '__main__': main(sys.argv[1])
