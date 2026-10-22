"""Iron's Spellbooks armor materials (additional attributes per piece) from ExtendedArmorMaterials.<clinit> with javap.
Usage: iss_armor.py <dir with the unzipped io/redspace/... classes>  -> iss_mats.json (copied into patches/gear_stats.json by hand)."""
import subprocess,re,json,sys
out=subprocess.run(['javap','-c','-p',sys.argv[1]+'/io/redspace/ironsspellbooks/item/armor/ExtendedArmorMaterials.class'],capture_output=True,text=True).stdout
body=out[out.index('static {};'):]
mats={};cur=None;attr=None;pend=None
for line in body.splitlines():
    m=re.search(r'// String ([A-Z_]+)$',line)
    if m and re.search(r'ldc_w?\s',line) and 'new' not in line:
        # enum constant names are the first String after 'dup'
        pass
    if 'new           #2 ' in line: cur=None;first=True
    m=re.search(r'ldc_w?\s+#\d+\s+// String ([A-Z][A-Z_]+)$',line)
    if m and first: cur=m.group(1);mats[cur]=[];first=False;continue
    if cur is None: continue
    m=re.search(r'AttributeRegistry\.([A-Z_]+):',line)
    if m: attr=m.group(1).lower();continue
    m=re.search(r'Attributes\.(f_\d+_|[A-Z_]+):',line)
    if m: attr='vanilla:'+m.group(1);continue
    m=re.search(r'// double ([-\d.eE]+)d',line)
    if m: pend=float(m.group(1));continue
    if 'dconst_1' in line: pend=1.0;continue
    if 'dconst_0' in line: pend=0.0;continue
    m=re.search(r'Operation\.([A-Z_]+):',line)
    if m and attr is not None and pend is not None:
        mats[cur].append((attr,pend,m.group(1)));attr=None;pend=None
for k,v in mats.items(): print(k,v)
json.dump(mats,open('iss_mats.json','w'))
