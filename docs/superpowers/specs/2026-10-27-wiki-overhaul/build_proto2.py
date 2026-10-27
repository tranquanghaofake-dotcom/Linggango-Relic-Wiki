"""Prototype v2: built from Linggango's own inventory (taste-skill run): the pack's logo and splash, the Terraria-style text menu
(#E6E6E6 → #FFE14A), the run through the Keepers as the frame of every page, the vanilla tooltip, the boss bar, Linggango Textures'
metal frame, the FTB quest-book ground. One texel = 2 px."""
import json,base64,io,sys,random
from PIL import Image
S=sys.argv[1]; LIB='/home/user/ws/assets/lib'
R=json.load(open(S+'/roomt.json')); P=json.load(open(S+'/proto_items.json')); E=json.load(open('emb.json')); REC=json.load(open('recipe.json'))
b64=lambda p:base64.b64encode(open(p,'rb').read()).decode()
def strip(paths):
    ims=[Image.open(p).convert('RGBA') for p in paths]; w=max(i.width for i in ims); h=max(i.height for i in ims)
    s=Image.new('RGBA',(w*len(ims),h))
    for k,i in enumerate(ims): s.alpha_composite(i,(k*w+(w-i.width)//2,h-i.height))
    b=io.BytesIO(); s.save(b,'PNG'); return base64.b64encode(b.getvalue()).decode(),w,h,len(ims)
spark=b64(f'{LIB}/lgw-fxgen/gold/sparkle.png'); fire=strip([f'{LIB}/goety/assets/goety/textures/particle/big_fire_{i}.png' for i in range(1,9)])
mono=b64('Monocraft.otf'); monob=b64('Monocraft-Bold.otf'); logo=b64('logo_h.png')
it=P['it']; ic=P['ic']; more=P['more']
RC={0:'#ffffff',1:'#ffff55',2:'#55ffff',3:'#ff55ff',4:'#ffaa00',5:'#ff5555'}; RN={0:'Common',1:'Uncommon',2:'Rare',3:'Epic',4:'Legendary',5:'Mythic'}
LAB={'0':'0-I','2':'II','3':'III','4':'IV','5':'V','6':'VI','6.3':'Dragon','7':'VII','8':'VIII','9':'IX','10':'X','11':'XI','12':'XII'}
emb={x['a']:x for x in E['o']}
order=[str(a) if a!=6.3 else '6.3' for a in E['order']]
HERE='7'; PAGE='9'
nodes=[]
for i,a in enumerate(order):
    x=emb.get(a,{}); state='done' if order.index(a)<order.index(HERE) else 'here' if a==HERE else 'cur' if a==PAGE else 'ahead'
    icn=x.get('ic') or ''
    icn=icn if (not icn or icn.startswith('data:')) else 'data:image/png;base64,'+icn
    k=x.get('keeper') or ''
    hard='<span class="hm">Hardmode ×2.1</span>' if a=='6.3' else ''
    nodes.append(f'<li class="{state}" title="Act {LAB[a]} · Keeper: {k}">{hard}<span class="slot">{f"<img src={chr(34)}{icn}{chr(34)} alt={chr(34)}{chr(34)}>" if icn else ""}{"<i class=ck></i>" if state=="done" else ""}</span><b>{LAB[a]}</b>{"<em>I am here</em>" if state=="here" else "<em>this curio</em>" if state=="cur" else ""}</li>')
ing=''.join(f'<span class="slot" title="{r["n"]}">{f"<img src=data:image/png;base64,{r[chr(105)+chr(99)]} alt>" if r["ic"] else "<span class=q>?</span>"}</span>' for r in REC)
cards=''.join(f'<a class="slot big" href="#" data-tip="{m["n"]}"><img src="data:image/png;base64,{m["ic"]}" alt=""></a>' for m in more if m['ic'])
splash=random.Random(3).choice(['The Keepers are watching.','Red means don\'t parry.','Hardmode starts after the Dragon.','Treasure bags for everyone!','Reforge it one more time.'])
css=f'''
@font-face{{font-family:Monocraft;src:url(data:font/otf;base64,{mono})}}@font-face{{font-family:Monocraft;font-weight:700;src:url(data:font/otf;base64,{monob})}}
:root{{--t:2px;--disp:Monocraft,monospace;--body:"Be Vietnam Pro",system-ui,sans-serif;--menu:#e6e6e6;--hover:#ffe14a;--ink:#f1efe8;--mute:#a7a3b6;--ground:#0e0d13}}
*{{box-sizing:border-box}}img{{image-rendering:pixelated}}
body{{margin:0;color:var(--ink);font:16px/1.6 var(--body);background:var(--ground) url(data:image/png;base64,{R['ftb_squares']}) 0 0/512px 512px}}
h1,h2,h3,b,.disp{{font-family:var(--disp)}}
/* title-screen header */
.top{{display:flex;align-items:center;gap:28px;padding:10px 28px;background:linear-gradient(#000c,#0008);position:sticky;top:0;z-index:9}}
.brand{{position:relative}}.brand img{{display:block;width:240px;image-rendering:auto}}
.splash{{position:absolute;left:196px;top:2px;transform:rotate(-14deg);font:700 12px var(--disp);color:#ffff00;text-shadow:2px 2px 0 #3f3f00;white-space:nowrap;animation:sp .5s ease-in-out infinite alternate}}
@keyframes sp{{to{{transform:rotate(-14deg) scale(1.08)}}}}
.menu{{display:flex;gap:26px;margin-left:110px}}.menu a{{font:700 20px var(--disp);color:var(--menu);text-decoration:none;text-shadow:var(--t) var(--t) 0 #000}}.menu a:hover,.menu a.on{{color:var(--hover)}}
.search{{margin-left:auto;width:340px;height:40px;background:#000;border:var(--t) solid #a0a0a0;color:#fff;font:16px var(--body);padding:0 12px}}
/* the run: Keepers as the frame of every page */
.run{{background:#000a;box-shadow:0 var(--t) 0 #000,0 calc(2*var(--t)) 0 #2a2633;padding:10px 28px 6px}}
.run h4{{margin:0 0 4px;font:700 14px var(--disp);color:var(--mute)}}.run h4 a{{color:var(--hover)}}
.run ol{{display:flex;list-style:none;margin:14px 0 0;padding:0;gap:0;align-items:flex-start}}
.run li{{position:relative;flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;font:12px var(--disp);padding-bottom:16px}}
.run li::before{{content:"";position:absolute;top:20px;left:-50%;width:100%;height:6px;background:url(data:image/png;base64,{R['bar_purple_bg']}) 0 0/364px 10px;z-index:-1}}
.run li:first-child::before{{display:none}}.run li.done::before,.run li.here::before{{background-image:url(data:image/png;base64,{R['bar_pink']})}}
.run .slot{{width:40px;height:40px}}.run li.done .slot img{{opacity:.55}}.run li.ahead .slot img{{filter:grayscale(1) brightness(.6)}}
.run li b{{color:var(--mute)}}.run li.here b{{color:var(--hover)}}.run li.cur b{{color:#ff5555}}
.run em{{position:absolute;bottom:0;white-space:nowrap;font:700 11px var(--disp);font-style:normal;color:var(--hover)}}.run li.cur em{{color:#ff5555}}
.run .ck{{position:absolute;right:-4px;bottom:-4px;width:18px;height:16px;background:url(data:image/png;base64,{R['lg_check']}) 0 0/18px 16px}}
.hm{{position:absolute;top:-14px;font:700 10px var(--disp);color:#ff5555;white-space:nowrap}}
/* page */
.page{{display:grid;grid-template-columns:200px minmax(0,1fr) 340px;gap:24px;max-width:1380px;margin:20px auto;padding:0 28px}}
.crumb{{grid-column:1/-1;font:14px var(--disp);color:var(--mute)}}.crumb a{{color:var(--hover);text-decoration:none}}
.toc{{position:sticky;top:180px;align-self:start;font:14px var(--disp)}}.toc a{{display:block;padding:5px 0;color:var(--menu);text-decoration:none;text-shadow:var(--t) var(--t) 0 #000}}.toc a:hover,.toc a.on{{color:var(--hover)}}.toc a.on::before{{content:"› "}}
h1{{font-size:32px;line-height:40px;margin:0;color:{RC[it['r']]};text-shadow:var(--t) var(--t) 0 #3f1515}}
.lead{{font-size:18px;color:#d0cdd8;margin:6px 0 14px;max-width:66ch}}
.gate{{display:flex;align-items:center;gap:14px;margin:0 0 22px;padding:10px 14px;background:#000a;box-shadow:0 0 0 var(--t) #000,inset 0 0 0 var(--t) #3a1d3a}}
.gate .bar{{flex:1}}.gate .bar div{{height:10px;background:url(data:image/png;base64,{R['bar_pink_bg']}) 0 0/364px 10px}}.gate .bar div i{{display:block;height:10px;width:66%;background:url(data:image/png;base64,{R['bar_pink']}) 0 0/364px 10px}}
.gate b{{color:#ff55ff;font-size:14px}}.gate small{{display:block;color:var(--mute);font:13px var(--disp)}}
.panel{{border:10px solid;border-image:url(data:image/png;base64,{R['lg_panel']}) 5/10px/0 repeat;background:#1c1a22;background-clip:padding-box;padding:12px 16px 14px;margin:0 0 22px;color:#e8e6ef}}
.panel h2{{font-size:20px;margin:0 0 12px;color:#fff;text-shadow:var(--t) var(--t) 0 #000}}
/* vanilla container for recipes */
.mc{{display:inline-flex;align-items:center;gap:12px;padding:12px;background:#c6c6c6;box-shadow:inset var(--t) var(--t) 0 #fff,inset calc(-1*var(--t)) calc(-1*var(--t)) 0 #555,0 0 0 var(--t) #000;color:#404040;font:14px var(--disp)}}
.mc .slot{{background:#8b8b8b;box-shadow:inset var(--t) var(--t) 0 #373737,inset calc(-1*var(--t)) calc(-1*var(--t)) 0 #fff}}
.arrow{{font:700 24px var(--disp);color:#8b8b8b}}
.slot{{position:relative;display:inline-grid;place-items:center;width:36px;height:36px;background:#8b8b8b;box-shadow:inset var(--t) var(--t) 0 #373737,inset calc(-1*var(--t)) calc(-1*var(--t)) 0 #fff}}.slot img{{width:32px;height:32px}}
.slot.big{{width:40px;height:40px}}.q{{font:700 16px var(--disp);color:#555}}
.grid{{display:flex;flex-wrap:wrap;gap:0}}
ol.steps{{margin:0;padding-left:22px}}ol.steps li{{margin:4px 0}}
/* infobox = the item's own tooltip */
.tip{{align-self:start;position:sticky;top:180px;background:#100010f0;box-shadow:0 0 0 var(--t) #100010,inset 0 0 0 var(--t) #5000ff,inset 0 calc(-1*var(--t)) 0 calc(var(--t)) #28007f;padding:14px 16px;font-family:var(--disp)}}
.show{{position:relative;display:grid;place-items:center;height:200px;margin:-4px -6px 10px;background:#0006}}
.frame{{position:relative;width:144px;height:168px;background:url(data:image/png;base64,{R['lg_frame_gold']}) 0 0/144px 168px}}.frame img{{position:absolute;left:24px;top:42px;width:96px;height:96px}}
.spark{{position:absolute;width:16px;height:16px;background:url(data:image/png;base64,{spark}) 0 0/64px 16px;animation:sk .6s steps(4) infinite}}@keyframes sk{{to{{background-position:-64px 0}}}}
.tip .nm{{font:700 18px var(--disp);color:{RC[it['r']]};text-shadow:var(--t) var(--t) 0 #3f1515}}
.tl{{font:14px/1.5 var(--disp);color:#a8a8a8}}.tl.b{{color:#5555ff}}.tl.g{{color:#55ff55}}.tl.d{{color:#555}}.tl.y{{color:#ffff55}}
.tip hr{{border:0;height:var(--t);background:#28007f;margin:10px 0}}
'''
html=f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Prototype v2</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700&display=swap"><style>{css}</style>
<header class="top"><div class="brand"><img src="data:image/png;base64,{logo}" alt="Linggango"><span class="splash">{splash}</span></div>
<nav class="menu"><a class="on" href="#">The Path</a><a href="#">Equipment</a><a href="#">Bosses</a><a href="#">Builder</a><a href="#">Mechanics</a></nav>
<input class="search" placeholder="Search curios, gear, Keepers…  /"></header>
<section class="run"><h4>Your run · Act VII, after the Elvenite Paladin · <a href="#">change</a></h4><ol>{''.join(nodes)}</ol></section>
<main class="page"><div class="crumb"><a href="#">The Path</a> › <a href="#">Act IX</a> › Hostility Curse</div>
<nav class="toc"><a class="on" href="#">How to get it</a><a href="#">Stats</a><a href="#">Same slot</a></nav>
<article><h1>{it['n']}</h1><p class="lead">{it['fx']}.</p>
<div class="gate"><span class="slot"><img src="{emb['9']['ic'] if emb.get('9',{}).get('ic','').startswith('data:') else 'data:image/png;base64,'+emb['9']['ic']}" alt=""></span><div class="bar"><b>Keeper-gated: 2 Keepers away</b><small>Beat Vaedric, then The Discord, to open Act IX</small><div><i></i></div></div></div>
<section class="panel"><h2>How to get it</h2><div class="mc">{ing}<span class="arrow">→</span><span class="slot"><img src="data:image/png;base64,{ic}" alt=""></span><span>Crafting Table</span></div>
<ol class="steps"><li>Hardest ingredient: Halo of Ascension, upgraded from Apostle's Broken Halo (Goety Revelation).</li><li>Dementor has no icon in the pack export (shown as ?).</li></ol></section>
<section class="panel"><h2>Same slot: Hostility Curse</h2><div class="grid">{cards}</div></section>
<section class="panel"><h2>Effects in this style</h2><div style="display:flex;gap:28px;align-items:end"><div style="width:{fire[1]*2}px;height:{fire[2]*2}px;background:url(data:image/png;base64,{fire[0]}) 0 0/{fire[1]*2*fire[3]}px {fire[2]*2}px;animation:fi .8s steps({fire[3]}) infinite"></div><span class="tl">Goety fire for the Nether Acts</span></div><style>@keyframes fi{{to{{background-position:-{fire[1]*2*fire[3]}px 0}}}}</style></section>
</article>
<aside class="tip"><div class="show"><div class="frame"><img src="data:image/png;base64,{ic}" alt=""></div><i class="spark" style="left:46px;top:30px"></i><i class="spark" style="right:52px;bottom:26px;animation-delay:.3s"></i></div>
<div class="nm">{it['n']}</div><div class="tl b">L2 Hostility</div><hr>
<div class="tl d">When in Hostility Curse slot:</div><div class="tl b">+100 Extra level</div><div class="tl b">Obtain Abrahadabra</div><div class="tl b">The Finale</div><hr>
<div class="tl">Rarity <span style="color:{RC[it['r']]}">{RN[it['r']]}</span></div><div class="tl">Act <span class="tl y">IX</span> · Role Tank</div><div class="tl g">Craft</div></aside>
</main>'''
open('proto2.html','w').write(html); print(len(html)//1024,'KB')
