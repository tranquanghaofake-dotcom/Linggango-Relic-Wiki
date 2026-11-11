#!/usr/bin/env python3
"""The mods' own words in the four languages, as {English phrase: {vi, ru, pt, es}} (official/mod_terms.json), for the phrases that the wiki's own text uses.

  python3 build/i18n/tools/mod_terms.py <harvest cache dir> <domains.json>       (the cache: python3 build/i18n/harvest.py fetch <manifest> <cache dir>; domains.json: node build/i18n/tools/domains.js)

Every mod of the pack ships `assets/<mod>/lang/en_us.json` and, for some languages, ru_ru, pt_br, es_mx/es_es, vi_vn. A phrase of at most 5 words that is the English value of a key and is used in the wiki's text
(any 1-5 word run of the translation memory's English and of the data domains) gets the translation of that key. When several mods or keys translate it differently the most frequent wins.
Use it as a hint when translating a label or name (todo/merge batches), and as a reference for terms.py. It is not applied automatically: a word with several meanings ("Damage") has a translation per mod."""
import json,glob,re,collections,sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import tmlib
C=sys.argv[1].rstrip('/')+'/'
LF={'vi':['vi_vn'],'ru':['ru_ru'],'pt':['pt_br'],'es':['es_mx','es_es']}
# corpus phrases: names and TM English (all langs share), plus domains.json
corp=set()
for l in ['ru']:
    for e in tmlib.load_tm(l).values():
        corp.add(e['en'].split('\u0001')[0])
dom=json.load(open(sys.argv[2]))
for d,v in dom.items(): corp.update(v)
words=lambda s: re.findall(r"[A-Za-z0-9'’\-]+",s)
phr=set()
for s in corp:
    w=words(s)
    for n in range(1,6):
        for i in range(len(w)-n+1): phr.add(' '.join(w[i:i+n]))
print('corpus strings',len(corp),'phrases',len(phr))
cnt=collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
nmods=0
for en_path in glob.glob(C+'*/assets/*/lang/en_us.json'):
    d=os.path.dirname(en_path)
    try: en=json.load(open(en_path,encoding='utf-8'))
    except Exception: continue
    nmods+=1
    tr={}
    for lg,fs in LF.items():
        for f in fs:
            p=os.path.join(d,f+'.json')
            if os.path.exists(p):
                try: tr.setdefault(lg,{}).update({k:v for k,v in json.load(open(p,encoding='utf-8')).items() if k not in tr.get(lg,{})})
                except Exception: pass
    for k,v in en.items():
        if not isinstance(v,str) or len(v)>60 or v not in phr: continue
        for lg in LF:
            t=tr.get(lg,{}).get(k)
            if isinstance(t,str) and t.strip() and t!=v: cnt[v][lg][t]+=1
print('mods',nmods,'English phrases with an official translation in some mod:',len(cnt))
for lg in LF: print(lg,sum(1 for v in cnt.values() if lg in v))
out={v:{lg:c.most_common(1)[0][0] for lg,c in per.items()} for v,per in cnt.items()}
json.dump({k:out[k] for k in sorted(out)},open(os.path.join(tmlib.HERE,'official','mod_terms.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0,sort_keys=True)
conf=[(v,per) for v,per in cnt.items() if any(len(c)>1 for c in per.values())]
print('with conflicting translations across mods',len(conf))
