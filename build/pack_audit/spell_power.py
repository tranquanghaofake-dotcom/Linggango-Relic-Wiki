#!/usr/bin/env python3
"""What spell power changes in each Iron's spell (2026-11-17, docs/plans/2026-11-17-spell-library.md).
Usage: python3 -I spell_power.py SERVER_DIR   (SERVER_DIR: the full server after kubejs/server_scripts/lgw_spellpower.js ran in it; its mods/ give the lang)
Reads SERVER_DIR/kubejs/lgw_spellpower.json: each spell's tooltip lines (getUniqueInfo) at its lowest and highest level, and at the highest level with
the school's power doubled and with the general Spell Power doubled, as a FakePlayer with no gear sees them. Writes ../patches/spell_power.json:
for every spell, its school, levels and on/off as the running game has them (after the pack's config), the school's power attribute by its
English name and one row per tooltip line: its label, the value at the lowest and at the highest
level (base power: 100%), and whether the school's power (p), the general Spell Power (g) or the level (l) changes it. Only what the tooltip shows is
measured; a spell whose tooltip has no line that power changes may still use power elsewhere (the page says so). Also the enchantments each Goety
focus accepts (Spell.acceptedEnchantments), which is what makes a focus stronger in Goety."""
import os, re, sys, json, glob, zipfile
H = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(H, '..', 'patches', 'spell_power.json')
SPEC = re.compile(r'%(?:(\d+)\$)?([sd%])')
CODES = re.compile(r'\u00a7.')   # Minecraft's colour and style codes (\u00a77 grey...): not text


def lang_of(mods_dir):
    lang = {}
    for p in sorted(glob.glob(os.path.join(mods_dir, '*.jar'))):
        z = zipfile.ZipFile(p)
        for n in z.namelist():
            if re.fullmatch(r'assets/[a-z0-9_.-]+/lang/en_us\.json', n):
                try: d = json.loads(re.sub(r',(\s*[}\]])', r'\1', z.read(n).decode('utf-8-sig', 'replace')))
                except Exception: continue
                for k, v in d.items():
                    if isinstance(v, str): lang.setdefault(k, v)
    return lang


def fmt(tpl, args):
    """Minecraft's format: %s and %d take the next argument, %1$s a numbered one, %% is a percent sign"""
    it = iter(args)
    def rep(m):
        if m.group(2) == '%': return '%'
        if m.group(1): k = int(m.group(1)) - 1; return args[k] if k < len(args) else ''
        return next(it, '')
    return SPEC.sub(rep, tpl)


def text(c, lang):
    """a serialised component (lgw_spellpower.js LGWP.ser) as English"""
    if isinstance(c, str): return c
    args = [text(a, lang) for a in c.get('a') or []]
    s = fmt(lang[c['k']], args) if c.get('k') and c['k'] in lang else (c.get('lit') if c.get('lit') is not None else c.get('t') or '')
    return s + ''.join(text(x, lang) for x in c.get('s') or [])


def label_value(c, lang):
    """the line's label and its value: '%d Damage' gives ('Damage', '15'), '%d%% Damage' ('Damage', '30%'), 'Max Distance: %s blocks' ('Max Distance: … blocks',
    '12'); a line with no number or several is all label"""
    full = CODES.sub('', text(c, lang)).strip()
    if not c.get('k') or c['k'] not in lang or c.get('s'): return full, ''
    tpl = CODES.sub('', lang[c['k']]); specs = [m for m in SPEC.finditer(tpl) if m.group(2) != '%']
    if len(specs) != 1: return full, ''
    m = specs[0]; end = m.end() + (2 if tpl[m.end():m.end() + 2] == '%%' else 0)   # a percent sign right after the number belongs to the value
    pre, post = tpl[:m.start()], tpl[end:]
    lab = (pre.strip() + (' … ' if pre.strip() and post.strip(' :+') else ' ') + post.strip()).replace('%%', '%').strip(' :+')
    args = [text(a, lang) for a in c.get('a') or []]
    return lab, CODES.sub('', fmt(tpl[m.start():end], args)).strip()


def main(srv):
    d = json.load(open(os.path.join(srv, 'kubejs', 'lgw_spellpower.json'), encoding='utf-8'))
    lang = lang_of(os.path.join(srv, 'mods'))
    attr_name = lambda a: (lang.get('attribute.' + a.replace(':', '.')) or lang.get('attribute.name.' + a.replace(':', '.'), a)) if a else None
    out = {'general': attr_name(d.get('general')), 'spells': {}, 'errors': d.get('errors', [])}
    for r in d['spells']:
        lo, hi, p2, g2 = r.get('lo') or [], r.get('hi') or [], r.get('school2'), r.get('general2')
        rows = []
        for i, c in enumerate(hi):
            lab, vb = label_value(c, lang)
            same_key = lambda L: L is not None and i < len(L) and L[i].get('k') == c.get('k')
            va = label_value(lo[i], lang)[1] if same_key(lo) else None
            row = {'t': lab, 'a': va, 'b': vb}
            if same_key(p2) and text(p2[i], lang) != text(c, lang): row['p'] = 1
            if same_key(g2) and text(g2[i], lang) != text(c, lang): row['g'] = 1
            if va is not None and va != vb: row['l'] = 1
            if not re.search(r'\d', lab + vb) and not row.get('l') and not row.get('p'): continue   # "T.O Magic 'n Extras", the add-on's own footer
            rows.append(row)
        sch = r.get('school') or ''; ns, _, nm = sch.partition(':')
        out['spells'][r['id']] = {'attr': attr_name(r.get('schoolAttr')), 'lv': [r.get('min'), r.get('max')], 'rows': rows, 'school': sch, 'enabled': r.get('enabled'),
                                  'schoolName': lang.get('school.%s.%s' % (ns, nm)) or lang.get('school.irons_spellbooks.' + nm),
                                  'sp': [round(x, 3) for x in r.get('sp') or []], 'sp2': round(r['sp2'], 3) if r.get('sp2') is not None else None}
    # Goety: the enchantments each focus accepts, by their English names
    out['goety'] = {g['id']: [lang.get('enchantment.' + e.replace(':', '.'), e) for e in g.get('ench') or []] for g in d.get('goety') or []}
    json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False, sort_keys=True)
    n = len(out['spells']); np = sum(1 for v in out['spells'].values() if any(x.get('p') for x in v['rows']))
    print('spell_power: %d spells, %d with a tooltip line spell power changes, %d with no tooltip line at all, %d errors'
          % (n, np, sum(1 for v in out['spells'].values() if not v['rows']), len(out['errors'])))


if __name__ == '__main__': main(sys.argv[1])
