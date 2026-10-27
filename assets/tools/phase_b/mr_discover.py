"""Find open-licence Modrinth mods / resource packs likely rich in effects, outside the pack.
Usage: python3 -I mr_discover.py <work dir with scan.json> <out json>"""
import json,sys,urllib.request,urllib.parse,time
P,OUT=sys.argv[1:3]; d=json.load(open(P+'/scan.json'))
inpack={(r.get('mr') or {}).get('slug') for r in d.values()}
H={'User-Agent':'lgw-asset-library (github.com/tranquanghaofake-dotcom/Linggango-Relic-Wiki)'}
LIC=['MIT','Apache-2.0','LGPL-3.0-only','LGPL-3.0-or-later','LGPL-2.1-only','LGPL-2.1-or-later','GPL-3.0-only','GPL-3.0-or-later','MPL-2.0',
     'CC0-1.0','CC-BY-4.0','CC-BY-3.0','CC-BY-SA-4.0','CC-BY-NC-4.0','CC-BY-NC-SA-4.0','CC-BY-NC-SA-3.0','Unlicense','BSD-3-Clause','BSD-2-Clause','Zlib','ISC']
Q=[('mod','particles'),('mod','particle effects'),('mod','visual effects'),('mod','vfx'),('mod','magic spells'),('mod','spell'),('mod','boss'),('mod','ambient'),
   ('mod','weapons'),('mod','dungeon'),('mod','enchant'),('mod','tooltip'),('mod',''),
   ('resourcepack','particles'),('resourcepack','effects'),('resourcepack','gui'),('resourcepack','ui'),('resourcepack','16x'),('resourcepack','magic'),('resourcepack','')]
seen={}
def search(pt,q,off):
    f=json.dumps([[f'project_type:{pt}'],[f'license:{l}' for l in LIC]])
    u='https://api.modrinth.com/v2/search?'+urllib.parse.urlencode({'query':q,'facets':f,'limit':100,'offset':off,'index':'downloads' if not q else 'relevance'})
    return json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=60).read())['hits']
for pt,q in Q:
    for off in (0,100):
        for h in search(pt,q,off):
            if h['slug'] in inpack: continue
            s=seen.setdefault(h['project_id'],{k:h[k] for k in('slug','title','project_type','license','downloads','follows','author','categories','description')})
            s.setdefault('queries',[]).append(q)
        time.sleep(0.3)
print(len(seen),'candidates')
json.dump(seen,open(OUT,'w'),indent=0)
