"""Contact sheets: per source, the effect-related art (particles, effect textures, particle sheets, mob_effect, gui, misc, environment)
as thumbnails on the dark GUI background, first frame of animations, integer scale only. Writes <assets>/sheets/<slug>-<n>.png and
<slug>-<n>.json (cell → catalog id), plus sheets/index.json.
Usage: python3 -I sheets.py <assets> [kinds comma list]"""
import sys,os,csv,json,collections
from PIL import Image
A=sys.argv[1]; KINDS=set((sys.argv[2] if len(sys.argv)>2 else 'particle,entity_fx,other_fx,effect_sheet,mob_effect,gui,misc,environment').split(','))
R=[r for r in csv.DictReader(open(os.path.join(A,'catalog.csv'))) if r['kind'] in KINDS and not r['duplicate_of'] and r['out_path'].lower().endswith(('.png','.gif'))]
by=collections.defaultdict(list)
for r in R: by[r['out_path'].split('/')[1]].append(r)
OUT=os.path.join(A,'sheets'); os.makedirs(OUT,exist_ok=True); idx={}
C,COLS,PER=56,20,400; ORDER={'particle':0,'effect_sheet':0,'entity_fx':1,'other_fx':1,'mob_effect':2,'misc':3,'environment':3,'gui':4}
for slug,rows in sorted(by.items()):
    rows.sort(key=lambda r:(ORDER.get(r['kind'],9),r['src_path']))
    for page in range(0,len(rows),PER):
        part=rows[page:page+PER]; n=len(part); sh=Image.new('RGBA',(C*COLS,C*((n+COLS-1)//COLS)),(30,30,34,255)); cells=[]
        for i,r in enumerate(part):
            try:
                im=Image.open(os.path.join(A,r['out_path'])); im.seek(0); im=im.convert('RGBA')
                fw=int(r['frame_w'] or im.width); fh=int(r['frame_h'] or im.height)
                if int(r['frames'] or 1)>1 and fh<im.height: im=im.crop((0,0,fw,fh))
                k=max(1,min((C-6)//max(im.size),8)) if max(im.size)<=C-6 else 0
                im=im.resize((im.width*k,im.height*k),Image.NEAREST) if k else im.resize((max(1,im.width*(C-6)//max(im.size)),max(1,im.height*(C-6)//max(im.size))),Image.NEAREST)
                x,y=(i%COLS)*C,(i//COLS)*C
                if (i//COLS+i%COLS)%2: sh.paste((36,36,41,255),(x,y,x+C,y+C))
                sh.alpha_composite(im,(x+(C-im.width)//2,y+(C-im.height)//2))
            except Exception: pass
            cells.append(r['id'])
        name=f"{slug}-{page//PER+1}"; sh.save(os.path.join(OUT,name+'.png'),optimize=True)
        json.dump({'cols':COLS,'cell':C,'ids':cells},open(os.path.join(OUT,name+'.json'),'w'))
        idx[name]={'source':part[0]['source'],'tier':part[0]['tier'],'count':n}
json.dump(idx,open(os.path.join(OUT,'index.json'),'w'),indent=0); print(len(idx),'sheets',len(R),'cells')
