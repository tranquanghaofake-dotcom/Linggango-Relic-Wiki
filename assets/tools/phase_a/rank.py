import json,sys
P=sys.argv[1]; d=json.load(open(P+'/scan.json'))
def fx(r):
    c=r.get('counts',{})
    return 3*c.get('particle',0)+2*c.get('entity_fx',0)+2*c.get('other_fx',0)+c.get('mob_effect',0)+0.5*c.get('gui',0)+r.get('anim',0)
for r in d.values(): r['fx']=fx(r)
json.dump(d,open(P+'/scan.json','w'),indent=0)
bad=lambda r: r['lic'] in('ARR','CC-ND','none','custom') or 'ARR' in r['lic'] or 'custom' in r['lic'] or r['asset_exc']
rows=sorted(d.values(),key=lambda r:-r['fx'])
def show(r):
    c=r.get('counts',{})
    print(f"{r['fx']:6.0f} {r['lic'][:22]:22} {r['title'][:38]:38} p{c.get('particle',0)} efx{c.get('entity_fx',0)} ofx{c.get('other_fx',0)} me{c.get('mob_effect',0)} gui{c.get('gui',0)} an{r.get('anim',0)} {'EXC' if r['asset_exc'] else ''} {(r.get('mr') or {}).get('source') or r.get('toml_url') or ''}")
print('== permissive-ish'); [show(r) for r in [r for r in rows if not bad(r)][:70]]
