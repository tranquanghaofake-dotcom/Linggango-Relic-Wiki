import json,re,glob,sys,os
W=sys.argv[1]
K=W+'/pack/src/overrides/kubejs/server_scripts'
rm=set()
for f in glob.glob(K+'/**/*.js',recursive=True):
    rm|=set(re.findall(r"\.remove\(\{\s*id:\s*['\"]([^'\"]+)['\"]",open(f).read()))
rm|=set(re.findall(r"'(mysticalagriculture:[a-z_]+)'",''))
rec=json.load(open(W+'/rec.json'))
s=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','src','data.js'),encoding='utf-8').read();D,_=json.JSONDecoder().raw_decode(s,re.search(r'\bD\s*=\s*\[',s).end()-1)
live=lambda i:[r for r in rec['recipes'].get(i,[]) if r['id'] not in rm]
json.dump(sorted(rm),open(W+'/removed_ids.json','w'))
print('removed ids',len(rm))
for d in D:
    rs=rec['recipes'].get(d['id'],[]); lv=live(d['id'])
    txt=' / '.join(d['src'])
    if d['g']=='Craft' and rs and not lv: print('CRAFT_BUT_ALL_REMOVED',d['id'],'|',txt[:140])
    if d['g']=='Loot' and lv and 'craftable' not in txt.lower(): print('LOOT_MISSING_CRAFT',d['id'],'|',[ (r['id'],r['t']) for r in lv][:2])
    if d['g']=='Loot' and rs and not lv and 'removed' not in txt.lower(): print('LOOT_RECIPE_REMOVED_NOTE?',d['id'],'|',txt[:120])
    if d['g']=='Loot' and 'craftable' in txt.lower() and rs and not lv: print('SAYS_CRAFTABLE_BUT_REMOVED',d['id'],'|',txt[:160])
