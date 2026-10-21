import json,glob,re,sys,collections
W=sys.argv[1]
s=open('/home/user/Linggango-Relic-Wiki/build/src/gear_data.js').read()
d=json.JSONDecoder();GE,_=d.raw_decode(s,s.index('[',s.index('const GE=')))
G={e['id']:e for e in GE}
AS=collections.defaultdict(list); ASF={}
for f in sorted(glob.glob(W+'/pack/src/overrides/kubejs/data/linggango/attributesetter/item/*.json')):
    for k,v in json.load(open(f)).items(): AS[k].extend(v); ASF.setdefault(k,[]).append(f.split('/')[-1])
out=[]; checked=collections.Counter()
key=lambda a:a.split(':')[-1].replace('generic.','')
# 1. pack attributesetter vs wiki src
for i,e in G.items():
    wiki=collections.Counter(); act=collections.Counter()
    for src,k,v,op in e.get('src',[]):
        if src=='pack': wiki[(k,op[:4])]+=v
    for x in AS.get(i,[]):
        act[(key(x['attribute']),x.get('operation','ADDITION')[:4])]+=x['value']
    if not wiki and not act: continue
    checked['attributesetter']+=1
    for k in set(wiki)|set(act):
        if abs(wiki[k]-act[k])>1e-3:
            out.append({'id':i,'field':'pack %s (%s)'%k,'wiki':round(wiki[k],4),'actual':round(act[k],4),'source':'attributesetter '+','.join(ASF.get(i,['(none)']))})
# AS entries for ids not in GE (gear rebalanced by pack but absent from wiki)
asmiss=[k for k in AS if k not in G and not k.startswith('#')]
# 2. Simply Swords formula from config
cfg=open(W+'/pack/src/overrides/config/simplyswords_main/weapon_attributes.json5').read()
C={k:float(v) for k,v in re.findall(r'"(\w+)":\s*(-?[\d.]+)',cfg)}
TB={'iron':2,'gold':0,'diamond':3,'netherite':4,'runic':4}
for i,e in G.items():
    ns,p=i.split(':')
    if ns!='simplyswords': continue
    m=re.match(r'(iron|gold|diamond|netherite|runic)_(\w+)$',p)
    if m and m.group(2)+'_attackSpeed' in C:
        t,w=m.groups()
        dmg=1+TB[t]+int(C[t+'_damageModifier']+C[w+'_positiveDamageModifier']-C[w+'_negativeDamageModifier'])
        spd=round(4+C[w+'_attackSpeed'],2)
    else:
        k=p.replace('_','').replace('claymore','').replace('relic','')
        ks=[x for x in C if x.endswith('_damageModifier') and x[:-15].lower()==p.replace('_','')]
        if not ks: continue
        dmg=1+5+int(C[ks[0]]); spd=None
    checked['simplyswords config']+=1
    if e.get('dmg')!=dmg: out.append({'id':i,'field':'dmg','wiki':e.get('dmg'),'actual':dmg,'source':'simplyswords_main/weapon_attributes.json5 (1 + tier bonus + int(modifiers))'})
    if spd is not None and e.get('spd') is not None and abs(e['spd']-spd)>0.01: out.append({'id':i,'field':'spd','wiki':e.get('spd'),'actual':spd,'source':'simplyswords config attackSpeed'})
# 3. entries dropped by the extractor sanity check (stat unknown on wiki)
bad=[i for i,e in G.items() if e.get('bad')]
for i in bad:
    e=G[i]
    out.append({'id':i,'field':'dmg/spd' if e['k']!='armor' else 'arm','wiki':None,'actual':'unknown (extractor value rejected as implausible)','source':'gear_data bad=1'})
json.dump(out,open(W+'/equip_mismatch.json','w'),indent=1)
json.dump(sorted(asmiss),open(W+'/eqa/as_not_in_wiki.json','w'),indent=1)
print(checked,len(out),collections.Counter(o['source'].split()[0] for o in out),'AS ids not in GE',len(asmiss))
