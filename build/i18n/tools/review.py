#!/usr/bin/env python3
"""Hand the translations to a native speaker as a spreadsheet and take the corrections back (docs/I18N.md, "Reviewing as a native speaker").

  python3 build/i18n/tools/review.py export ru [--domain ui,vocab] [--all] [--out ru.csv]
  python3 build/i18n/tools/review.py import ru ru.csv [--dry] [--force]

export   one row per entry that is not yet `human` (with --all, also the game's own words, `official`): id, domain, state, english, translation, ok, comment.
         The order is the order a reader meets them: ui, vocab, gear, relic, st, cfg, fx, src, guide, boss, names; short English first.
         A plural entry gives one row per form (id `<hash>#one`); its english column is the singular or the plural sentence.
import   the reviewer edits the `translation` column and writes anything (x, ok, 1) in `ok` for a row that is right as it stands.
         A changed translation is checked like merge.py checks it (the same digits, {placeholders} and tags as the English; a row that fails is listed and skipped unless --force)
         and becomes `human`; an unchanged row with `ok` becomes `human`; a row with only a comment is listed and left as it is.
After an import: bash build/patches/apply_all.sh, node build/i18n/tools/inv.js, python3 build/i18n/tools/qa.py --strict.
"""
import sys, os, re, csv, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tmlib

ORDER = ['ui', 'vocab', 'gear', 'relic', 'st', 'cfg', 'fx', 'src', 'guide', 'boss', 'names']
num = lambda t: sorted(re.findall(r'\d+', re.sub(r'(?<=\d)[.,  ](?=\d{3}\b)', '', re.sub(r'(?<=\d)[.,](?=\d)', '', t))))
ph = lambda x: sorted(re.findall(r'\{\w+\}', x)); tg = lambda x: sorted(set(re.findall(r'</?[A-Za-z]\w*|href="[^"]*"', x)))

def rows(tm, domains, with_official):
    out = []
    for h, e in tm.items():
        d = e.get('d', 'vocab')
        if domains and d not in domains: continue
        if e['s'] == 'human' or (e['s'] == 'official' and not with_official): continue
        if isinstance(e['t'], dict):
            one, other = (e['en'].split('\u0001') + [e['en']])[:2]
            for form, t in e['t'].items(): out.append((d, h + '#' + form, e['s'], one if form == 'one' else other, t))
        else: out.append((d, h, e['s'], e['en'], e['t']))
    out.sort(key=lambda r: (ORDER.index(r[0]) if r[0] in ORDER else 99, len(r[3]), r[3]))
    return out

def cmd_export(a):
    lang = a.lang; tm = tmlib.load_tm(lang); rs = rows(tm, set(a.domain.split(',')) if a.domain else None, a.all)
    path = a.out or lang + '.csv'
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f); w.writerow(['id', 'domain', 'state', 'english', 'translation', 'ok', 'comment'])
        for d, h, s, en, t in rs: w.writerow([h, d, s, en, t, '', ''])
    print(len(rs), 'rows ->', path)

def cmd_import(a):
    lang = a.lang; tm = tmlib.load_tm(lang); changed = ok = 0; bad = []; talk = []
    for ln, r in enumerate(csv.DictReader(open(a.file, encoding='utf-8-sig', newline='')), 2):
        key = (r.get('id') or '').strip(); h, _, form = key.partition('#'); e = tm.get(h)
        if not e: bad.append((ln, 'unknown id', key)); continue
        t = r.get('translation') or ''; mark = (r.get('ok') or '').strip(); note = (r.get('comment') or '').strip()
        cur = e['t'][form] if form and isinstance(e['t'], dict) else e['t']
        if not isinstance(cur, str): bad.append((ln, 'plural entry needs its #form id', key)); continue
        en = (e['en'].split('\u0001') + [e['en']])[1 if form and form != 'one' else 0] if isinstance(e['t'], dict) else e['en']
        if t.strip() != cur.strip():
            if not t.strip(): bad.append((ln, 'empty translation', en[:60])); continue
            why = [n for n, f in (('digits', num), ('placeholders', ph), ('tags', tg)) if f(t) != f(en)] if not isinstance(e['t'], dict) else []
            if why and not a.force: bad.append((ln, 'differs from the English in ' + ', '.join(why), t[:70])); continue
            if isinstance(e['t'], dict): e['t'][form] = t.strip()
            else: e['t'] = t.strip()
            e['s'] = 'human'; changed += 1
        elif mark:
            e['s'] = 'human'; ok += 1
        elif note: talk.append((ln, en[:60], note[:80]))
    print(changed, 'changed,', ok, 'confirmed as they were,', len(bad), 'skipped,', len(talk), 'comments only')
    for b in bad[:40]: print('  skipped', b)
    for t in talk[:40]: print('  comment', t)
    if a.dry: print('(dry: nothing written)'); return
    tmlib.write_tm(lang, tm)

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    e = sub.add_parser('export'); e.add_argument('lang'); e.add_argument('--domain'); e.add_argument('--all', action='store_true'); e.add_argument('--out')
    i = sub.add_parser('import'); i.add_argument('lang'); i.add_argument('file'); i.add_argument('--dry', action='store_true'); i.add_argument('--force', action='store_true')
    a = ap.parse_args(); (cmd_export if a.cmd == 'export' else cmd_import)(a)

if __name__ == '__main__': main()
