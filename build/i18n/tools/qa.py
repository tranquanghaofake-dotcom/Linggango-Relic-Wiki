#!/usr/bin/env python3
"""Deterministic checks of the translation text itself (no tokens, no network): python3 build/i18n/tools/qa.py [--lang ru] [--domain fx] [--rule typography] [--all] [--strict] [--json out.json]

What the build and the invariants cannot see: wrong typography per language, English left in a translation, a term that the glossary fixes, a symbol dropped, a length that does not fit.
Each finding is one line `lang domain rule: English => translation`; by default 6 examples per rule and language are printed, --all prints everything, --strict exits 1 if any finding of a hard rule is left.
Rules (hard = must be 0 before a commit):
  typography   hard  es: a number followed by % with no space; vi, ru, pt: a space before %; ru/pt/es: a decimal dot where the language writes a comma; vi: a decimal comma; doubled spaces; straight "quotes" in ru/es
  ending       hard  the English ends with . ! ? : … and the translation does not (or the other way round)
  symbols      hard  ★ ❤ 💥 🪡 ⚙ · → ~ ^ and the like: the count differs from the English
  brackets     hard  ( ) [ ] « » counts differ from the English
  script       hard  a word that mixes Latin and Cyrillic letters (a glitch), vi not in NFC
  plurals      hard  a plural entry misses a form the language's rule uses
  glossary     hard  a term of glossary.json "terms" is in the English and its translation is not in the text; a "forbidden" variant is
  english      soft  an English word written lowercase in the English text is still in a ru/vi translation (left untranslated)
  same         soft  the translation is the English (4 words or more, not a glossary name)
  length       soft  the translation is more than 3 times or less than a third as long as the English (20 characters or more)
  start        soft  the English starts with a capital letter and the translation with a lowercase one
"""
import sys, os, re, json, argparse, unicodedata, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tmlib

HERE = tmlib.HERE
LANGS = ['vi', 'ru', 'pt', 'es']
HARD = {'typography', 'ending', 'symbols', 'brackets', 'script', 'plurals', 'glossary'}
PLURAL_FORMS = {'vi': {'other'}, 'ru': {'one', 'few', 'many', 'other'}, 'pt': {'one', 'many', 'other'}, 'es': {'one', 'many', 'other'}}
SYM = '★❤💥🪡⚙·→~^×•▲▼↑↓…'
BRK = '()[]«»'
WORD = re.compile(r"[A-Za-z][A-Za-z'’\-]+")

def forms_of(e):
    t = e['t']; return [t] if isinstance(t, str) else list(t.values())

def load_glossary():
    g = json.load(open(os.path.join(HERE, 'glossary.json'), encoding='utf-8')); keep = json.load(open(os.path.join(HERE, 'keep.json'), encoding='utf-8'))
    names = set(g.get('doNotTranslate', [])) | set(keep.get('all', [])); per = {l: set(keep.get(l, [])) for l in LANGS}
    return g, names, per

def lower_words(tm_all):
    """English words that are written lowercase somewhere in the English text: common words, not names."""
    c = collections.Counter()
    for tm in tm_all.values():
        for e in tm.values():
            for w in re.findall(r"(?<![A-Za-z])[a-z][a-z'’\-]{3,}", e['en']): c[w] += 1
    return {w for w, n in c.items() if n >= 3}

def check(lang, e, g, names, kept, common):
    out = []; en = e['en']; src = en.split('\u0001')[0]; srcs = en.split('\u0001')
    t = e['t']; tx = forms_of(e); plural = isinstance(t, dict)
    for i, f in enumerate(tx):
        s = srcs[-1] if plural and i else src
        plain = re.sub(r'<[^>]*>', '', f); plain_en = re.sub(r'<[^>]*>', '', s)
        # typography
        if lang == 'es' and re.search(r'\d%', plain) and not re.search(r'%%|%\d\$|%[sd]', plain): out.append(('typography', 'es: number glued to %'))
        if lang in ('vi', 'ru', 'pt') and re.search(r'\d [%]', plain) and not re.search(r'\d [%]', plain_en): out.append(('typography', lang + ': space before %'))
        if lang in ('ru', 'pt', 'es'):   # a decimal dot where the language writes a comma: after ×, + or -, in brackets, before % or x (a version "1.19" or a thousands dot "10.000" is not flagged)
            m = re.search(r'(?:[×+\-−(~]\s?|\bx)\d+\.\d{1,2}(?!\d|\.\d)|(?<!\d)\d+\.\d{1,2}(?=\s?%|x\b| ?s\b)', plain)
            if m: out.append(('typography', lang + ': decimal dot ' + m.group(0)))
        if lang == 'vi' and re.search(r'\d,\d', plain) and not re.search(r'\d,\d{3}\b', plain): out.append(('typography', 'vi: decimal comma'))
        if '  ' in f.strip(): out.append(('typography', 'double space'))
        if lang in ('ru', 'es') and re.search(r'"[^"]*[A-Za-zА-Яа-я][^"]*"', plain) and '"' not in plain_en: out.append(('typography', lang + ': straight quotes'))
        # ending
        q = ' "\'»«“”‘’)'
        a, b = plain_en.rstrip(q)[-1:], plain.rstrip(q)[-1:]
        if len(plain_en) > 12 and a in '.!?:…' and b not in '.!?:…': out.append(('ending', 'English ends with %r, translation with %r' % (a, b)))
        elif len(plain_en) > 25 and b == '.' and a not in '.!?:…' and not a.isdigit(): out.append(('ending', 'translation ends with a full stop, the English with %r' % a))
        # symbols and brackets
        for ch in SYM:
            if ch in '×…': continue   # "3× faster" is said "3 veces más rápido" / "в 3 раза быстрее"; "..." and "…" are the same
            #
            if plain_en.count(ch) != plain.count(ch) and not (ch in '…' and ('...' in plain)) and not (ch == '·' and False): out.append(('symbols', 'count of ' + ch + ' %d vs %d' % (plain_en.count(ch), plain.count(ch)))); break
        for ch, pair in (('(', ')'), ('[', ']')):
            if plain.count(ch) != plain.count(pair) or plain.count(ch) < plain_en.count(ch): out.append(('brackets', 'a bracket %s%s is dropped or unbalanced' % (ch, pair))); break   # the translation may add (Stun) after a word
        # script and normalisation
        for w in re.findall(r'\w+', re.sub(r'<[^>]*>', ' ', f)):
            if re.search(r'[A-Za-z]', w) and re.search(r'[А-Яа-яЁё]', w): out.append(('script', 'mixed Latin and Cyrillic: ' + w)); break
        if lang == 'vi' and unicodedata.normalize('NFC', f) != f: out.append(('script', 'vi not NFC'))
        # english leftovers
        if lang in ('ru', 'vi') and not plural:
            ws = [w for w in re.findall(r"[^\W\d_]+", plain) if w.isascii() and w.islower() and len(w) >= 4 and w in common]
            if ws: out.append(('english', 'lowercase English word: ' + ws[0]))
        # same
        if f == s and len(s.split()) >= 4 and s not in names and s not in kept and not plural: out.append(('same', 'translation equals the English'))
        # length
        if len(s) >= 20 and not plural and (len(f) > 3 * len(s) or len(f) * 3 < len(s)): out.append(('length', 'length %d vs %d' % (len(f), len(s))))
        # start
        if re.match(r'[A-Z]', plain_en) and re.match(r'[a-zа-яё]', plain) and not plural: out.append(('start', 'lowercase start'))
    if plural:
        miss = PLURAL_FORMS[lang] - set(t)
        if miss: out.append(('plurals', 'missing forms: ' + ','.join(sorted(miss))))
    # glossary
    for term, per in g.get('terms', {}).items():
        want = per.get(lang)
        if not want: continue
        key = re.sub(r' \(.*\)$', '', term)
        if any(x in src for x in per.get('ignore', [])): continue   # a name that contains the word (Boss Soul, Terra Curio)
        if per.get('loose'): continue   # the word means different things by context (the Wither mob and the Wither effect): not checked
        if per.get('whole') and src.strip() != key: continue   # only where the English is exactly this word (Power as the wiki's tier label, not "Spell Power")
        if re.search(r'(?<![A-Za-z])' + re.escape(key) + r'(?![a-z])', src) and src != key:
            stem = want.lower()[:max(4, len(want) - 2)]
            if stem not in ' '.join(tx).lower() and want.lower() != key.lower() and not per.get('loose'): out.append(('glossary', 'term %s should be %s' % (key, want)))
        for bad in per.get('forbidden', {}).get(lang, []) if isinstance(per.get('forbidden'), dict) else []:
            if bad.lower() in ' '.join(tx).lower(): out.append(('glossary', 'forbidden %r for %s' % (bad, key)))
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--lang'); ap.add_argument('--domain'); ap.add_argument('--rule'); ap.add_argument('--all', action='store_true'); ap.add_argument('--strict', action='store_true'); ap.add_argument('--json')
    a = ap.parse_args(); g, names, per = load_glossary(); langs = [a.lang] if a.lang else LANGS
    tm_all = {l: tmlib.load_tm(l) for l in LANGS}; common = lower_words(tm_all); res = []; counts = collections.Counter(); shown = collections.Counter()
    for lang in langs:
        for k, e in tm_all[lang].items():
            if a.domain and e['d'] != a.domain: continue
            for rule, msg in check(lang, e, g, names, per[lang], common):
                if a.rule and rule != a.rule: continue
                counts[(lang, rule)] += 1; res.append({'lang': lang, 'domain': e['d'], 'rule': rule, 'msg': msg, 'en': e['en'].replace('\u0001', ' | '), 't': e['t'] if isinstance(e['t'], str) else json.dumps(e['t'], ensure_ascii=False)})
                if a.all or shown[(lang, rule)] < 6:
                    shown[(lang, rule)] += 1; print('%s %-6s %-10s %s: %s => %s' % (lang, e['d'], rule, msg, e['en'][:90].replace('\u0001', ' | '), (e['t'] if isinstance(e['t'], str) else json.dumps(e['t'], ensure_ascii=False))[:90]))
    print('\nfindings per language and rule:'); hard = 0
    for (lang, rule), n in sorted(counts.items()):
        print('  %s %-10s %5d%s' % (lang, rule, n, '' if rule not in HARD else '  (hard)')); hard += n if rule in HARD else 0
    print('hard findings:', hard)
    if a.json: json.dump(res, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False)
    return 1 if (a.strict and hard) else 0

if __name__ == '__main__': sys.exit(main())
