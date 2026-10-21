import json,re,collections,sys
W=sys.argv[1]; u=json.load(open(W+'/equip_unobtainable.json')); C=W+'/pack/src/overrides/config/'
flags={}
for f in (C+'simplyswords_main/loot.json5',C+'simplymore/loot.json5'):
    for k,v in re.findall(r'"enable([A-Za-z]+)":\s*(true|false)',open(f).read()): flags[k.lower()]=v
for x in u:
    ns,p=x['id'].split(':')
    if x['why']!=['no recipe and no loot']: x['verdict']='UNOBTAINABLE/hidden: '+'; '.join(x['why'])
    elif ns in('simplyswords','simplymore'):
        fl=[v for k,v in flags.items() if p.replace('_','').startswith(k)]
        x['verdict']=('UNOBTAINABLE: disabled in %s loot config'%ns) if 'false' in fl else 'obtainable: %s unique loot injection (code, config-enabled); wiki shows no source'%ns
    elif any('treasurebag' in s for s in x['other_sources']): x['verdict']='obtainable: Armageddon boss treasure bag; wiki shows no source'
    elif any('loot_modifiers' in s for s in x['other_sources']): x['verdict']='obtainable: global loot modifier; wiki shows no source'
    elif ns=='too_many_bows': x['verdict']='likely obtainable: too_many_bows config-driven loot injection; wiki shows no source'
    elif x['other_sources']: x['verdict']='unclear: id mentioned in '+', '.join(x['other_sources'][:3])
    else: x['verdict']='NO SOURCE FOUND in recipes/loot/bags/configs (code-only drop or unobtainable) - verify in game'
json.dump(u,open(W+'/equip_unobtainable.json','w'),indent=1)
print(collections.Counter(x['verdict'].split(':')[0] for x in u))
