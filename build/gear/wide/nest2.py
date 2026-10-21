import zipfile,glob,sys,io,re
G=sys.argv[1]
for j,inner in (('GoetyRevelation-2.3.1.jar','[Forge]RevelationFix-1.20.1-4.0.jar'),('thermal_foundation-1.20.1-11.0.6.70.jar','thermal_core-1.20.1-11.0.6.24.jar')):
    z=zipfile.ZipFile(G+'/pack/mods/'+j); zz=zipfile.ZipFile(io.BytesIO(z.read('META-INF/jarjar/'+inner)))
    t=zz.read('META-INF/mods.toml').decode('utf8','ignore'); print(inner, re.findall(r'modId\s*=\s*"([^"]+)"',t))
    print(' outer', re.findall(r'modId\s*=\s*"([^"]+)"',z.read('META-INF/mods.toml').decode('utf8','ignore')))
    print(' ', sorted({n.split('/')[1] for n in zz.namelist() if n.startswith('assets/')}))
