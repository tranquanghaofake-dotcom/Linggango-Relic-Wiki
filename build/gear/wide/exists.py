import sys, zipfile, glob, re
G = sys.argv[1]; ids = sys.argv[2:]
jars = sorted(glob.glob(G + '/pack/mods/*.jar')) + sorted(glob.glob(G + '/nested/*.jar'))
for i in ids:
    ns, nm = i.split(':')
    hits = []
    for j in jars:
        try: z = zipfile.ZipFile(j)
        except Exception: continue
        for n in z.namelist():
            if n.endswith('.class'):
                continue
            if (nm in n.split('/')[-1]) and (ns in n):
                hits.append((j.split('/')[-1][:30], n))
        # class constant strings
        for n in z.namelist():
            if n.endswith('.class'):
                b = z.read(n)
                if nm.encode() in b: hits.append((j.split('/')[-1][:30], 'CLASS ' + n))
    print('==', i, len(hits))
    for h in hits[:12]: print('   ', h)
