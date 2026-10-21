import zipfile,glob,sys,os,io
W=sys.argv[1]
for j in sorted(glob.glob(W+'/pack/mods/*.jar')):
    try: z=zipfile.ZipFile(j)
    except Exception as e: print('BAD',j,e); continue
    nested=[n for n in z.namelist() if n.startswith('META-INF/jarjar/') and n.endswith('.jar')]
    for n in nested:
        try:
            zz=zipfile.ZipFile(io.BytesIO(z.read(n))); nl=zz.namelist()
            cls=sum(1 for x in nl if x.endswith('.class')); items=any('/lang/en_us.json' in x for x in nl)
            print(os.path.basename(j), n.split('/')[-1], cls, 'LANG' if items else '')
        except Exception as e: print('ERR',n,e)
