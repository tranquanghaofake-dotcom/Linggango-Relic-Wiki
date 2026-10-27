"""Download the newest primary file of each selected Modrinth project into <work>/mr/<slug>/, record version + source url.
Projects built on another company's IP are skipped (their art is not the mod author's to license).
Usage: python3 -I mr_fetch.py <selected json> <work dir>"""
import json,sys,os,re,urllib.request,concurrent.futures as cf,time
SEL,W=sys.argv[1:3]; d=json.load(open(SEL)); os.makedirs(W+'/mr',exist_ok=True)
H={'User-Agent':'lgw-asset-library (github.com/tranquanghaofake-dotcom/Linggango-Relic-Wiki)'}
IP=re.compile(r'pok[eé]mon|cobblemon|pixelmon|terraria|calamity|zelda|genshin|hollow ?knight|undertale|mario|sonic|star ?wars|marvel|naruto|one ?piece|touhou|elden|dark ?souls|fnaf|five nights|minecraft dungeons|dungeons[- ]weaponry|legends|wallpaper|anime|warhammer|lord of the rings|lotr|doom|halo|fortnite|roblox|digimon|yugioh|ben 10|dragon ball|bleach|jujutsu|demon slayer|attack on titan|chainsaw',re.I)
def get(u,t=120):
    err=None
    for i in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=t).read()
        except Exception as e: err=e; time.sleep(2**i)
    raise err
def job(kv):
    pid,v=kv
    if IP.search(v['slug']+' '+v['title']+' '+v['description']): return pid,{'skip':'third-party IP'}
    try:
        p=json.loads(get(f'https://api.modrinth.com/v2/project/{pid}'))
        vs=json.loads(get(f'https://api.modrinth.com/v2/project/{pid}/version'))
        if not vs: return pid,{'skip':'no versions'}
        pick=next((x for x in vs if '1.20.1' in x['game_versions']),vs[0])
        f=next((x for x in pick['files'] if x['primary']),pick['files'][0])
        if f['size']>80e6: return pid,{'skip':'file over 80 MB'}
        od=f"{W}/mr/{v['slug']}"; os.makedirs(od,exist_ok=True); out=f"{od}/{f['filename']}"
        if not os.path.exists(out): open(out,'wb').write(get(f['url'],300))
        return pid,{'slug':v['slug'],'title':p['title'],'type':p['project_type'],'license':p['license']['id'],'license_url':p['license'].get('url'),
                    'source':p.get('source_url'),'team':v['author'],'downloads':p['downloads'],'version':pick['version_number'],'version_id':pick['id'],
                    'game_versions':pick['game_versions'][-3:],'file':f['filename'],'sha1':f['hashes']['sha1'],'url':f'https://modrinth.com/{p["project_type"]}/{v["slug"]}'}
    except Exception as e: return pid,{'skip':'error '+str(e)[:80]}
with cf.ThreadPoolExecutor(8) as ex: res=dict(ex.map(job,d.items()))
json.dump(res,open(W+'/mr_fetched.json','w'),indent=0)
import collections; print(collections.Counter(v.get('skip','ok')[:20] for v in res.values()))
