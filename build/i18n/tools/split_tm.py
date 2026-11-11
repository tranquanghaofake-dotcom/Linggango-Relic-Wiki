#!/usr/bin/env python3
"""One-time migration (kept as a record, harmless to run again): tm/<lang>.json -> tm/<lang>/<domain>.json.

A domain is the part of the wiki a sentence belongs to, so a reviewer can take one file (docs/I18N.md). Which domain is decided from the built site:
  node build/i18n/tools/domains.js /tmp/domains.json     (after apply_all.sh)
  python3 build/i18n/tools/split_tm.py /tmp/domains.json [--dry]
First match wins: ui (sentences the code writes with T()), then fx, st, src, boss, guide, relic, gear, names; the rest is `vocab` (words and clause shapes the engines compose: source-line templates, attribute names, ...).
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tmlib
ORDER = ['ui', 'fx', 'st', 'src', 'boss', 'guide', 'relic', 'gear', 'names']

def main():
    dom = {k: set(v) for k, v in json.load(open(sys.argv[1], encoding='utf-8')).items()}
    ui = tmlib.scan_msgids(); lp = os.path.join(tmlib.HERE, 'tr_log.json')
    if os.path.exists(lp): ui |= set(json.load(open(lp, encoding='utf-8')))
    dom['ui'] = ui; counts = {}
    for lang in ['vi', 'ru', 'pt', 'es']:
        old = os.path.join(tmlib.HERE, 'tm', lang + '.json')
        if not os.path.exists(old): print(lang, 'already split'); continue
        tm = json.load(open(old, encoding='utf-8')); out = {}
        for k, e in tm.items():
            d = next((x for x in ORDER if e['en'] in dom.get(x, ())), 'vocab'); e = dict(e); e['d'] = d; out[k] = e; counts.setdefault(lang, {}).setdefault(d, 0); counts[lang][d] += 1
        print(lang, counts[lang])
        if '--dry' in sys.argv: continue
        os.remove(old); tmlib.write_tm(lang, out)
main()
