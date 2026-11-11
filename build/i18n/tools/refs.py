#!/usr/bin/env python3
"""Names inside sentences (docs/I18N.md, "Names inside sentences").

A translation names an item or a term between ⟦ ⟧ and the build writes the name of that language: "Lleva la ⟦Frozen Blade⟧". The name lives once, in names.json;
rename it there and every sentence follows. ⟦English|gen⟧ asks for a case form (ru): forms/<lang>.json = {"English": {"gen": "…"}}; a form that is missing leaves the English name.

  python3 build/i18n/tools/refs.py scan  [lang] [--show N]       English names still written out in translations (not yet references)
  python3 build/i18n/tools/refs.py apply <lang> [--dry]           wrap them (vi, pt, es: the name replaces the English; look at pt/es articles, the list says where one stands before the name)
  python3 build/i18n/tools/refs.py patch <lang> file.json         {english sentence: new text with references}: for a hand edit of the sentences the list pointed at (ru cases)
  python3 build/i18n/tools/refs.py forms <lang> file.json         add case forms {"English": {"gen": "…"}} to forms/<lang>.json
  python3 build/i18n/tools/refs.py gender <lang> [--dry]         pt, es: the article before a reference takes the gender and number of the name that stands there (a list of the changes is printed)
  python3 build/i18n/tools/refs.py check [--strict]               every reference points at a name that exists; every case asked for has its form

Which English counts as a name: entries of the names domain and the Title Case entries of the boss domain (two words or more), the game's own names, and the terms in refs.json.
"""
import sys, os, re, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tmlib

LANGS = ['vi', 'ru', 'pt', 'es']
TITLE = re.compile(r"^[A-Z][\w'’\-]*( (?:[A-Z0-9][\w'’\-]*|of|the|and|in|a|an|to|for|with|on|de|la|le))+$")
ARTICLES = {'pt': {'o', 'a', 'os', 'as', 'um', 'uma', 'do', 'da', 'dos', 'das', 'no', 'na', 'nos', 'nas', 'ao', 'à', 'aos', 'às', 'pelo', 'pela', 'num', 'numa', 'dum', 'duma'},
            'es': {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'del', 'al'}}

def _refs():
    p = os.path.join(tmlib.HERE, 'refs.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
def extra_terms(): return _refs().get('terms', [])
def protected(): return set(_refs().get('protect', []))

SMALL = {'of', 'the', 'and', 'in', 'a', 'an', 'to', 'for', 'with', 'on'}
def is_bag(en):
    """A boss's own drop: "Iron Colossus Treasure Bag", "Sanghor, Lord of the Blood Relic" (not a sentence that ends with one)."""
    if not en.endswith((' Treasure Bag', ' Relic')): return False
    ws = [w.strip(',') for w in en.split()]
    return all(w[:1].isupper() or w in SMALL for w in ws) and ';' not in en

def item_names():
    """The English names of things a sentence can mention: curios and gear (data.js, gear_data.js), every item a recipe names (NM in data.js), the game's own item, block and mob names.
    Armor-set names (the "Cursed Paladin" of "Cursed Paladin set") are not here: they are prefixes ("Dark Metal" is also the start of "Dark Metal Ingot") and are written out as they are."""
    out = set(); src = os.path.join(tmlib.SRC, 'data.js')
    for f in ('data.js', 'gear_data.js'):
        p = os.path.join(tmlib.SRC, f)
        if os.path.exists(p):
            for m in re.finditer(r'\{"id":"([^"]+)","n":"((?:[^"\\]|\\.)*)"', open(p, encoding='utf-8').read()): out.add(json.loads('"' + m.group(2) + '"'))
    if os.path.exists(src):
        t = open(src, encoding='utf-8').read(); i = t.find('NM={')
        if i >= 0: out |= set(json.JSONDecoder().raw_decode(t[i + 3:])[0].values())
    v = os.path.join(tmlib.HERE, 'official', 'vanilla_terms.json')
    if os.path.exists(v): out |= set(json.load(open(v, encoding='utf-8')))
    return out

def candidates(lang, tm):
    """{English: translation} of what a sentence may name."""
    out = {}; items = item_names()
    for e in tm.values():
        if not isinstance(e['t'], str) or e['t'] == e['en'] or '\u0001' in e['en']: continue
        if e['d'] == 'names' and len(e['en'].split()) >= 2 and e['en'] in items or e['d'] == 'boss' and (TITLE.match(e['en']) or is_bag(e['en'])): out[e['en']] = e['t']
    for en, t in tmlib.official_names_by_english(lang).items():
        if len(en.split()) >= 2 and t != en: out.setdefault(en, t)
    mine = {e['en']: e['t'] for e in tm.values() if isinstance(e['t'], str)}
    for en in extra_terms():
        if en in mine and mine[en] != en: out[en] = mine[en]
    return out

def finder(names):
    if not names: return None
    alt = '|'.join(re.escape(n) for n in sorted(set(names) | protected(), key=len, reverse=True))
    return re.compile(r"(?<![\w'’\-])(" + alt + r")(?![\w'’\-])")

def occurrences(text, rx):
    """(start, end, name) outside ⟦ ⟧."""
    out, pos, keep = [], 0, protected()
    for m in tmlib.REF.finditer(text):
        out += [(pos + x.start(), pos + x.end(), x.group(1)) for x in rx.finditer(text[pos:m.start()])]; pos = m.end()
    out += [(pos + x.start(), pos + x.end(), x.group(1)) for x in rx.finditer(text[pos:])]
    return [o for o in out if o[2] not in keep]

def forms_of(t): return [(k, v) for k, v in t.items()] if isinstance(t, dict) else [(None, t)]

def scan(lang, tm):
    names = candidates(lang, tm); rx = finder(names); rows = []
    if not rx: return rows
    for k, e in tm.items():
        if e['d'] == 'names' or e['t'] == e['en'] or e['en'] in names: continue
        for form, t in forms_of(e['t']):
            oc = occurrences(t, rx)
            if oc: rows.append((k, e, form, t, oc))
    return rows

def prev_word(t, i):
    m = re.search(r"([\w'’À-ÿ]+)\W*$", t[:i]); return m.group(1).lower() if m else ''

def cmd_scan(a):
    for lang in ([a.lang] if a.lang else LANGS):
        tm = tmlib.load_tm(lang); rows = scan(lang, tm); occ = sum(len(r[4]) for r in rows); cnt = {}
        for r in rows:
            for _, _, n in r[4]: cnt[n] = cnt.get(n, 0) + 1
        art = sum(1 for r in rows for s, _, _ in r[4] if prev_word(r[3], s) in ARTICLES.get(lang, ()))
        print('%s: %d strings, %d occurrences of %d names%s' % (lang, len(rows), occ, len(cnt), '' if lang not in ARTICLES else '; %d stand right after an article or preposition (check gender)' % art))
        if a.show:
            for k, e, form, t, oc in rows[:a.show]:
                s, _, n = oc[0]; print('   %s ... %s' % (n, t[max(0, s - 30):s + len(n) + 25].replace('\n', ' ')))

def cmd_apply(a):
    lang = a.lang; tm = tmlib.load_tm(lang); rows = scan(lang, tm); n = 0; flagged = []
    for k, e, form, t, oc in rows:
        new = t
        for s, en, name in reversed(oc):
            new = new[:s] + '⟦' + name + '⟧' + new[en:]; n += 1
            if prev_word(t, s) in ARTICLES.get(lang, ()): flagged.append((e['en'][:60], prev_word(t, s) + ' ⟦' + name + '⟧'))
        if form: e['t'][form] = new
        else: e['t'] = new
    print(lang, len(rows), 'strings,', n, 'references' + (' (dry)' if a.dry else ''))
    for f in flagged[:200]: print('  article?', f)
    if not a.dry: tmlib.write_tm(lang, tm)


# --- articles in front of a reference (pt, es): the article must agree with the name that will stand there ---
PT_M = {'focus', 'coração', 'pó', 'anel', 'colar', 'cachecol', 'capacete', 'peitoral', 'bracelete', 'pingente', 'tomo', 'mapa', 'dia', 'sistema', 'cinto', 'cutelo', 'cajado', 'elmo', 'chapéu', 'selo', 'sinete', 'símbolo', 'núcleo', 'saco', 'barril'}
PT_F = {'neve', 'foice', 'chave', 'corrente', 'noite', 'fenda', 'ponte', 'fonte', 'carne', 'pele', 'lente', 'torre', 'ordem', 'imagem', 'virtude', 'verdade', 'tarde', 'glacê', 'mão', 'luz', 'cruz', 'paz', 'voz', 'vez', 'lança', 'ferradura', 'tábua', 'caveira', 'aljava', 'bengala', 'bússola', 'geladeira', 'torradeira', 'betoneira', 'meia'}
ES_M = {'caché', 'focus', 'foco', 'mapa', 'día', 'sistema', 'problema', 'tema', 'planeta', 'cofre', 'estandarte', 'brazalete', 'colgante', 'guante', 'casco', 'yelmo', 'peto', 'collar', 'anillo', 'amuleto', 'bastón', 'tomo', 'sello', 'polvo', 'corazón', 'imán', 'carcaj', 'pico', 'martillo'}
ES_F = {'llave', 'noche', 'corriente', 'gente', 'fuente', 'muerte', 'sangre', 'nieve', 'leche', 'clave', 'torre', 'cumbre', 'fiebre', 'mano', 'flor', 'luz', 'cruz', 'voz', 'vez', 'piel', 'sal', 'ley', 'red', 'nevera', 'hoja', 'capa', 'ropa', 'daga', 'lanza', 'espada', 'bota', 'túnica', 'corona'}
ES_EL_F = {'ala', 'alma', 'arma', 'hacha', 'hada', 'águila', 'área', 'aura', 'agua', 'asa', 'arpa', 'ancla', 'hambre', 'ave', 'ascua'}   # feminine, but "el" / "un" in the singular
LEAD_ADJ = {'grande', 'gran', 'pequeno', 'pequeña', 'pequeño', 'primeiro', 'primer', 'último', 'último', 'último', 'velho', 'viejo', 'antigo', 'novo', 'nuevo'}

def head_word(name):
    ws = re.findall(r"[A-Za-zÀ-ÿ'’]+", name)
    for w in ws:
        if w.lower() not in LEAD_ADJ: return w.lower()
    return ws[0].lower() if ws else ''

def gender_of(lang, name):
    """'m', 'f', 'mp', 'fp' or None (unknown) for the translated name: from its head noun."""
    w = head_word(name)
    if not w or name == '': return None
    M, F = (PT_M, PT_F) if lang == 'pt' else (ES_M, ES_F)
    first = name.split(' ')[0]
    own = {'pt': {'O': 'm', 'A': 'f', 'Os': 'mp', 'As': 'fp'}, 'es': {'El': 'm', 'La': 'f', 'Los': 'mp', 'Las': 'fp'}}[lang]
    if first in own and len(name.split(' ')) > 1: return own[first]   # a name that starts with its own article ("O Olho Onividente") says its gender
    if w in M: return 'm'
    if w in F or w in ES_EL_F: return 'f'
    pl = w.endswith('s') and len(w) > 3 and not w.endswith(('ás', 'ês', 'ís'))
    b = w[:-1] if pl else w
    if lang == 'es' and w in ('pantalones', 'guantes', 'brazaletes', 'tobilleras', 'botas', 'escarpines', 'zapatos', 'cuernos', 'colmillos', 'aros', 'dados', 'granos', 'nombres'): pl, b = True, w[:-1]
    if b in M or (b + 'o') in M: g = 'm'
    elif b in F: g = 'f'
    elif b.endswith(('ção', 'ción', 'sión', 'são', 'dade', 'dad', 'tad', 'tud', 'gem', 'umbre', 'ez')): g = 'f'
    elif b.endswith('a'): g = 'f'
    elif b.endswith('o'): g = 'm'
    elif b.endswith(('or', 'al', 'el', 'il', 'ar', 'ão', 'e', 'én', 'ón', 'ín', 'iz', 'ol', 'ul', 'ut', 't', 'm', 'l', 'r', 'n', 'z', 'x', 'k', 'd')): g = 'm'
    else: return None
    return g + ('p' if pl else '')

FORMS = {
 'pt': {'def': {'m': 'o', 'f': 'a', 'mp': 'os', 'fp': 'as'}, 'ind': {'m': 'um', 'f': 'uma', 'mp': 'uns', 'fp': 'umas'}, 'de': {'m': 'do', 'f': 'da', 'mp': 'dos', 'fp': 'das'},
        'em': {'m': 'no', 'f': 'na', 'mp': 'nos', 'fp': 'nas'}, 'a': {'m': 'ao', 'f': 'à', 'mp': 'aos', 'fp': 'às'}, 'por': {'m': 'pelo', 'f': 'pela', 'mp': 'pelos', 'fp': 'pelas'}},
 'es': {'def': {'m': 'el', 'f': 'la', 'mp': 'los', 'fp': 'las'}, 'ind': {'m': 'un', 'f': 'una', 'mp': 'unos', 'fp': 'unas'}, 'de': {'m': 'del', 'f': 'de la', 'mp': 'de los', 'fp': 'de las'},
        'a': {'m': 'al', 'f': 'a la', 'mp': 'a los', 'fp': 'a las'}}}

def article_table(lang):
    inv = {}
    for kind, d in FORMS[lang].items():
        for g, w in d.items(): inv.setdefault(w, []).append((kind, g))
    return inv

def fix_articles(lang, text, lookup):
    """(new text, [changes]): the article or contraction right before a reference takes the gender and number of the name that will stand there."""
    inv = article_table(lang); changes = []
    alt = '|'.join(sorted((re.escape(w) for w in inv), key=len, reverse=True))
    rx = re.compile(r"(?<![\w'’])(" + alt + r")(\s+)(\u27e6([^\u27e7|]+?)(?:\|\w+)?\u27e7)", re.I)
    def sub(m):
        art, sp, tok, name = m.group(1), m.group(2), m.group(3), m.group(4)
        low = art.lower(); kinds = inv.get(low)
        if not kinds: return m.group(0)
        tr = lookup(name)
        if not isinstance(tr, str) or tr == name: return m.group(0)
        g = gender_of(lang, tr)
        if not g: changes.append(('?', art + ' ' + name + ' => ' + tr)); return m.group(0)
        kind, cur = kinds[0]
        if lang == 'es' and g == 'f' and head_word(tr) in ES_EL_F and kind in ('def', 'ind', 'de', 'a') and not tr.split(' ')[0] in ('La', 'Las'):
            g = 'm' if kind != 'de' else 'm'   # el agua, un hacha, del ala
        if g == cur: return m.group(0)
        new = FORMS[lang][kind][g]
        if art[:1].isupper(): new = new[:1].upper() + new[1:]
        changes.append((art + ' → ' + new, tr)); return new + sp + tok
    return rx.sub(sub, text), changes

def cmd_gender(a):
    lang = a.lang; tm = tmlib.load_tm(lang); look = tmlib.name_lookup(lang, tm); allc = []
    for e in tm.values():
        for form, t in forms_of(e['t']):
            new, ch = fix_articles(lang, t, look)
            if ch: allc += [(e['en'][:40],) + c for c in ch]
            if new != t:
                if form: e['t'][form] = new
                else: e['t'] = new
    unk = [c for c in allc if c[1] == '?']; fixed = [c for c in allc if c[1] != '?']
    print(lang, len(fixed), 'articles changed;', len(unk), 'names of unknown gender')
    for c in fixed[:400]: print('  ', c[1], '|', c[2])
    for c in unk[:80]: print('  ?', c[2])
    if not a.dry: tmlib.write_tm(lang, tm)

def cmd_patch(a):
    lang = a.lang; tm = tmlib.load_tm(lang); by = {e['en']: e for e in tm.values()}; patch = json.load(open(a.file, encoding='utf-8')); n = 0
    for en, new in patch.items():
        if en not in by: print('  unknown English:', en[:70]); continue
        e = by[en]
        if not isinstance(e['t'], str): print('  plural entry, edit by hand:', en[:70]); continue
        if '⟦' in new and tmlib.REF.sub(lambda m: m.group(1), new).count('{') != en.count('{'): print('  placeholders differ:', en[:70]); continue
        e['t'] = new; n += 1
    print(n, 'sentences patched')
    if not a.dry: tmlib.write_tm(lang, tm)

def cmd_forms(a):
    p = os.path.join(tmlib.HERE, 'forms', a.lang + '.json'); os.makedirs(os.path.dirname(p), exist_ok=True)
    cur = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
    for en, fs in json.load(open(a.file, encoding='utf-8')).items(): cur.setdefault(en, {}).update(fs)
    body = ',\n'.join(json.dumps(k, ensure_ascii=False) + ': ' + json.dumps(cur[k], ensure_ascii=False) for k in sorted(cur))
    open(p, 'w', encoding='utf-8').write('{\n' + body + '\n}\n'); print(len(cur), 'names with forms in', p)

def cmd_check(a):
    bad = 0
    for lang in LANGS:
        tm = tmlib.load_tm(lang); look = tmlib.name_lookup(lang, tm); forms = tmlib.load_forms(lang); n = 0; miss = {}
        for e in tm.values():
            for _, t in forms_of(e['t']):
                for en, case in tmlib.REF.findall(t):
                    n += 1
                    if case: ok = bool(forms.get(en, {}).get(case))
                    else: ok = bool(look(en))
                    if not ok: miss.setdefault(en + ('|' + case if case else ''), []).append(e['en'][:50])
        print('%s: %d references; %d with no name or no case form%s' % (lang, n, len(miss), '' if not miss else ': ' + '; '.join(sorted(miss)[:8]) + (' …' if len(miss) > 8 else '')))
        bad += len(miss)
    return 1 if (a.strict and bad) else 0

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('scan'); s.add_argument('lang', nargs='?'); s.add_argument('--show', type=int, default=0)
    p = sub.add_parser('apply'); p.add_argument('lang'); p.add_argument('--dry', action='store_true')
    q = sub.add_parser('patch'); q.add_argument('lang'); q.add_argument('file'); q.add_argument('--dry', action='store_true')
    f = sub.add_parser('forms'); f.add_argument('lang'); f.add_argument('file')
    c = sub.add_parser('check'); c.add_argument('--strict', action='store_true')
    g = sub.add_parser('gender'); g.add_argument('lang'); g.add_argument('--dry', action='store_true')
    a = ap.parse_args(); return {'scan': cmd_scan, 'apply': cmd_apply, 'patch': cmd_patch, 'forms': cmd_forms, 'check': cmd_check, 'gender': cmd_gender}[a.cmd](a) or 0

if __name__ == '__main__': sys.exit(main())
