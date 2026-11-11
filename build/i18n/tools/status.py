#!/usr/bin/env python3
"""Where the translations stand: python3 build/i18n/tools/status.py <dir with domains.json and todo.json>   (bash build/i18n/tools/status.sh makes both)

Per language and domain: entries in tm/<lang>/<domain>.json by state (llm = machine, official = the game's own text, human = a person checked it), the strings still without a translation
(todo.json), and orphans: entries of fx, st, boss, guide, gear and relic whose English no longer appears on the site (the pack changed; safe to drop after a look)."""
import sys, json, os, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tmlib
D = sys.argv[1]; dom = {k: set(v) for k, v in json.load(open(os.path.join(D, 'domains.json'), encoding='utf-8')).items()}; todo = json.load(open(os.path.join(D, 'todo.json'), encoding='utf-8'))
CHECKED = ['fx', 'st', 'boss', 'guide', 'gear', 'relic']; tot = collections.Counter()
for lang in ['vi', 'ru', 'pt', 'es']:
    tm = tmlib.load_tm(lang); by = collections.defaultdict(list)
    for e in tm.values(): by[e['d']].append(e)
    print('== %s: %d entries' % (lang, len(tm)))
    print('   %-7s %6s  %-26s %7s %7s' % ('domain', 'entries', 'states', 'todo', 'orphans'))
    for d in sorted(set(by) | set(todo.get(lang, {}))):
        es = by.get(d, []); st = collections.Counter(e.get('s', 'llm') for e in es); orph = sum(1 for e in es if d in CHECKED and e['en'] not in dom.get(d, ())) if d in dom else '-'
        rv = sum(1 for e in es if e.get('r') == 'needs-review')
        print('   %-7s %6d  %-26s %7s %7s%s' % (d, len(es), ' '.join('%s %d' % kv for kv in sorted(st.items())), len(todo.get(lang, {}).get(d, [])) if lang in todo else '-', orph, '  (%d needs-review)' % rv if rv else ''))
