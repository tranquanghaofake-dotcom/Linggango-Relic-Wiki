"""Shared helpers of the asset library scripts: file kind, image facts and automatic scores, catalog columns."""
import re,io,json,os,csv
from PIL import Image
FXW=re.compile(r'(fx|effect|spell|magic|vfx|slash|beam|aura|ring|circle|rune|glyph|spark|flame|soul|lightning|shock|wave|blast|explos|portal|orb|trail|swirl|glow|halo)',re.I)
def kind(p):
    l=p.lower()
    if l.endswith('.json'): return 'particle_def'
    t=l.split('/textures/',1)[1]
    for k,pre in (('particle','particle'),('mob_effect','mob_effect'),('gui','gui'),('gui','ui'),('item','item'),('block','block'),('environment','environment'),('misc','misc')):
        if t.startswith(pre): return k
    if t.startswith('entity'): return 'entity_fx' if FXW.search(t) else 'entity'
    if t.startswith(('models/armor','armor')): return 'armor'
    return 'other_fx' if FXW.search(t) else 'other'
def img_info(b,meta):
    im=Image.open(io.BytesIO(b)); w,h=im.size; im=im.convert('RGBA'); a=im.getchannel('A')
    hist=a.histogram(); px=w*h; semi=sum(hist[1:255])/px if px else 0
    cols=len(im.getcolors(1<<20) or [])
    frames=1; ft=''
    if meta is not None:
        frames=h//w if w and h%w==0 else 1
        try:
            an=json.loads(meta).get('animation',{}); ft=an.get('frametime',1)
            if 'frames' in an: frames=len(an['frames'])
            if an.get('height') and an.get('width'): frames=h//an['height']
        except Exception: pass
    fw,fh=(w,h//frames) if frames>1 else (w,h)
    grid=3 if fw%8==0 and fh%8==0 and max(fw,fh)<=64 else 2 if fw%8==0 and fh%8==0 and max(fw,fh)<=256 else 1
    if semi>0.15: grid=max(0,grid-1)
    return dict(w=w,h=h,frame_w=fw,frame_h=fh,frames=frames,frametime=ft,colors=cols,semi_alpha=round(semi,3),score_grid=grid,
                score_anim=3 if frames>=4 else 2 if frames>1 else '')
KEYS=['id','tier','confidence','kind','namespace','source','version','src_path','out_path','author','license','derivative_ok','sharealike','noncommercial',
      'w','h','frame_w','frame_h','frames','frametime','colors','semi_alpha','sha256','score_grid','score_light','score_read','score_anim','score_rel','score_lic',
      'use_on_wiki','status','duplicate_of','note']

def append(assets,rows):
    p=os.path.join(assets,'catalog.csv'); first=not os.path.exists(p)
    with open(p,'a',newline='') as f:
        w=csv.DictWriter(f,fieldnames=KEYS,extrasaction='ignore')
        if first: w.writeheader()
        w.writerows(rows)
