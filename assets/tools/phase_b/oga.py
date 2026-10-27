"""OpenGameArt CC0 effect sprites. fetch: download the files of the selected entries (oga_selected.json, filtered from
huggingface nyuuzyou/OpenGameArt-CC0 2D_Art metadata) into <W>/ext/oga/files/<entry>/; zips are unpacked (images only).
ingest: copy images into <assets>/lib/opengameart-cc0/<entry>/ with one catalog row each (author and page per entry).
Usage: python3 -I oga.py fetch <W> | python3 -I oga.py ingest <W> <assets>"""
import sys,os,re,json,zipfile,urllib.request,urllib.parse,concurrent.futures as cf,time,hashlib,shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
mode,W=sys.argv[1:3]; D=W+'/ext/oga'; sel=json.load(open(D+'/oga_selected.json'))
slug=lambda r: r['url'].rstrip('/').rsplit('/',1)[-1][:80]
IMG=re.compile(r'\.(png|gif)$',re.I)
if mode=='fetch':
    def get(u):
        for i in range(3):
            try: return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'lgw-asset-library'}),timeout=120).read()
            except Exception as e: err=e; time.sleep(2**i)
        raise err
    def job(r):
        od=f"{D}/files/{slug(r)}"; os.makedirs(od,exist_ok=True); n=0
        for f in r['files']:
            out=f"{od}/{f['name']}"
            if not os.path.exists(out):
                try: open(out,'wb').write(get(f['url']))
                except Exception: continue
            if out.lower().endswith('.zip'):
                try:
                    z=zipfile.ZipFile(out)
                    for i in z.infolist():
                        if IMG.search(i.filename) and i.file_size<20e6 and '..' not in i.filename and not i.filename.startswith('/'):
                            p=os.path.join(od,'_unz',re.sub(r'[^\w./ -]','_',i.filename)); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'wb').write(z.read(i))
                except Exception: pass
            n+=1
        return n
    with cf.ThreadPoolExecutor(6) as ex: print(sum(ex.map(job,sel)),'files')
else:
    from assetlib import kind,img_info,append
    A=sys.argv[3]; rows=[]
    for r in sel:
        od=f"{D}/files/{slug(r)}"
        if not os.path.isdir(od): continue
        for dp,_,fs in os.walk(od):
            for f in sorted(fs):
                if not IMG.search(f): continue
                full=os.path.join(dp,f); rel=os.path.relpath(full,od)
                from PIL import Image
                try:
                    with Image.open(full) as im0:
                        if min(im0.size)>192: continue   # large painted frames, not pixel art
                except Exception: continue
                out=os.path.join(A,'lib','opengameart-cc0',slug(r),rel); os.makedirs(os.path.dirname(out),exist_ok=True); shutil.copyfile(full,out)
                b=open(full,'rb').read()
                row=dict(id=f"opengameart-cc0:{slug(r)}/{rel}",tier='A',confidence='high',kind='effect_sheet',source='OpenGameArt: '+r['title'],
                         version=r['url'],src_path=rel,out_path=os.path.relpath(out,A),author=r['author'],license='CC0-1.0',derivative_ok=1,sharealike=0,
                         noncommercial=0,sha256=hashlib.sha256(b).hexdigest(),score_lic=3,status='new',note='tags: '+', '.join(r['tags'][:8]))
                try:
                    row.update(img_info(b,None))
                    from PIL import Image; import io
                    im=Image.open(io.BytesIO(b))
                    if getattr(im,'n_frames',1)>1: row['frames']=im.n_frames; row['score_anim']=3 if im.n_frames>=4 else 2
                except Exception: row['note']+='; unreadable'
                rows.append(row)
    append(A,rows); print(len(rows),'rows')
