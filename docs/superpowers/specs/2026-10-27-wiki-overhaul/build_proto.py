"""Static prototype of the overhaul design (one texel = 2 CSS px everywhere; showcase ×6). Assets: ROOMT (vanilla, Linggango Textures
with permission), the asset library (Goety MIT flames, fxgen), Monocraft (OFL). Output: proto.html (self-contained)."""
import json,base64,io,sys,os
from PIL import Image
S=sys.argv[1]; LIB='/home/user/ws/assets/lib'
R=json.load(open(S+'/roomt.json')); P=json.load(open(S+'/proto_items.json'))
b64=lambda p:base64.b64encode(open(p,'rb').read()).decode()
def strip(paths):
    ims=[Image.open(p).convert('RGBA') for p in paths]; w=max(i.width for i in ims); h=max(i.height for i in ims)
    s=Image.new('RGBA',(w*len(ims),h))
    for k,i in enumerate(ims): s.alpha_composite(i,(k*w+(w-i.width)//2,h-i.height))
    b=io.BytesIO(); s.save(b,'PNG'); return base64.b64encode(b.getvalue()).decode(),w,h,len(ims)
fire=strip([f'{LIB}/goety/assets/goety/textures/particle/big_fire_{i}.png' for i in range(1,9)])
spark=b64(f'{LIB}/lgw-fxgen/gold/sparkle.png'); slash=b64(f'{LIB}/lgw-fxgen/blood/slash.png')
deep=b64(f'{LIB}/minecraft-26.3/assets/minecraft/textures/block/deepslate_tiles.png')
mono=b64('Monocraft.otf'); monob=b64('Monocraft-Bold.otf')
it=P['it']; more=P['more']
RC={0:'#ffffff',1:'#ffff55',2:'#55ffff',3:'#ff55ff',4:'#ffaa00',5:'#ff5555'}
RN={0:'Common',1:'Uncommon',2:'Rare',3:'Epic',4:'Legendary',5:'Mythic'}
def slot(ic,big=False): return f'<span class="slot"><img src="data:image/png;base64,{ic}" alt=""></span>'
cards=''.join(f'<a class="card" href="#"><span class="slot"><img src="data:image/png;base64,{m["ic"]}" alt=""></span><span><b style="color:{RC.get(m["r"],"#fff")}">{m["n"]}</b><small>{m["m"]}</small></span></a>' for m in more[:6] if m['ic'])
css=f'''
@font-face{{font-family:Monocraft;src:url(data:font/otf;base64,{mono})}}
@font-face{{font-family:Monocraft;font-weight:700;src:url(data:font/otf;base64,{monob})}}
:root{{--t:2px; /* one texel */
 --n0:#0b0a0e;--n1:#121117;--n2:#1a1921;--n3:#24222c;--n4:#2f2c39;--n5:#3d3a49;--n6:#5a566b;--n7:#8d89a0;--n8:#c9c5d6;--n9:#f1efe8;
 --gold:#ffaa00;--yellow:#ffff55;--green:#55ff55;--aqua:#55ffff;--red:#ff5555;--purple:#ff55ff;
 --disp:Monocraft,ui-monospace,monospace;--body:"Be Vietnam Pro",system-ui,sans-serif;
 --bevel:inset var(--t) var(--t) 0 var(--n5),inset calc(-1*var(--t)) calc(-1*var(--t)) 0 var(--n0)}}
*{{box-sizing:border-box}}img{{image-rendering:pixelated}}
body{{margin:0;background:var(--n1) url(data:image/png;base64,{deep}) 0 0/32px 32px;background-blend-mode:multiply;color:var(--n9);font:16px/1.6 var(--body)}}
body::before{{content:"";position:fixed;inset:0;background:rgba(11,10,14,.82);z-index:-1}}
h1,h2,h3,.disp{{font-family:var(--disp);font-weight:700;margin:0;letter-spacing:0}}
/* shell */
.top{{position:sticky;top:0;z-index:5;display:flex;align-items:center;gap:16px;height:64px;padding:0 24px;background:var(--n2);box-shadow:0 var(--t) 0 var(--n0),0 calc(2*var(--t)) 0 var(--n4)}}
.logo{{font:700 20px var(--disp);color:var(--n9);text-decoration:none}}.logo small{{display:block;font:12px var(--disp);color:var(--gold)}}
.nav{{display:flex;gap:8px;margin-left:8px}}
.btn{{display:inline-flex;align-items:center;height:40px;padding:0 14px;color:#e0e0e0;font:16px var(--disp);text-decoration:none;text-shadow:var(--t) var(--t) 0 #3f3f3f;
 border:6px solid;border-image:url(data:image/png;base64,{R['btn']}) 3 fill/6px/0 repeat;image-rendering:pixelated}}
.btn:hover{{border-image-source:url(data:image/png;base64,{R['btn_hover']});color:#ffffa0}}
.btn.on{{color:var(--green)}}
.search{{flex:1;max-width:440px;margin-left:auto;height:40px;background:var(--n0);color:var(--n9);font:16px var(--body);padding:0 12px;border:0;box-shadow:inset 0 0 0 var(--t) var(--n6)}}
/* page grid: contents | article | infobox */
.page{{display:grid;grid-template-columns:200px minmax(0,1fr) 320px;gap:24px;max-width:1360px;margin:24px auto;padding:0 24px}}
.crumb{{grid-column:1/-1;font:14px var(--disp);color:var(--n7)}}.crumb a{{color:var(--yellow);text-decoration:none}}
.toc{{position:sticky;top:88px;align-self:start;font:14px var(--disp)}}.toc b{{display:block;color:var(--n7);margin:0 0 8px}}
.toc a{{display:block;padding:6px 10px;color:var(--n8);text-decoration:none;box-shadow:inset var(--t) 0 0 var(--n4)}}.toc a.on{{color:var(--yellow);box-shadow:inset var(--t) 0 0 var(--yellow)}}
.head{{display:flex;gap:16px;align-items:center;margin:0 0 8px}}
.head h1{{font-size:32px;line-height:40px;color:{RC[it['r']]};text-shadow:var(--t) var(--t) 0 #3f1515}}
.lead{{font-size:18px;color:var(--n8);margin:0 0 12px;max-width:68ch}}
.chips{{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 24px}}
.chip{{font:14px var(--disp);padding:4px 10px;background:var(--n3);box-shadow:var(--bevel);color:var(--n8)}}.chip i{{color:var(--c);font-style:normal}}
.panel{{background:var(--n3);box-shadow:0 0 0 var(--t) var(--n0),var(--bevel);padding:20px 24px;margin:0 0 24px}}
.panel h2{{font-size:20px;line-height:24px;margin:0 0 16px;display:flex;gap:10px;align-items:center}}
.slot{{display:inline-grid;place-items:center;width:40px;height:40px;flex:none;background:var(--n1);box-shadow:inset var(--t) var(--t) 0 var(--n0),inset calc(-1*var(--t)) calc(-1*var(--t)) 0 var(--n5)}}
.slot img{{width:32px;height:32px}}
.steps{{counter-reset:s;list-style:none;padding:0;margin:0}}.steps li{{counter-increment:s;display:flex;gap:12px;padding:10px 0;box-shadow:0 var(--t) 0 var(--n2)}}
.steps li::before{{content:counter(s);font:700 16px var(--disp);color:var(--gold);width:24px}}
.stats li{{list-style:none;padding:6px 0;color:var(--aqua)}}.stats{{padding:0;margin:0}}.stats li::before{{content:"+ ";color:var(--n7)}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.card{{display:flex;gap:12px;align-items:center;padding:8px;background:var(--n2);box-shadow:var(--bevel);text-decoration:none;color:var(--n8)}}
.card:hover{{background:var(--n4)}}.card b{{display:block;font:700 15px var(--body)}}.card small{{color:var(--n7)}}
/* infobox */
.info{{align-self:start;position:sticky;top:88px;background:var(--n3);box-shadow:0 0 0 var(--t) var(--n0),var(--bevel);padding:16px}}
.art{{position:relative;display:grid;place-items:center;height:216px;background:var(--n1);box-shadow:inset var(--t) var(--t) 0 var(--n0),inset calc(-1*var(--t)) calc(-1*var(--t)) 0 var(--n5);overflow:hidden}}
.frame{{position:relative;width:144px;height:168px;background:url(data:image/png;base64,{R['lg_frame_gold']}) 0 0/144px 168px}}
.frame img{{position:absolute;left:24px;top:42px;width:96px;height:96px}}
.spark{{position:absolute;width:16px;height:16px;background:url(data:image/png;base64,{spark}) 0 0/64px 16px;animation:sp .6s steps(4) infinite}}
@keyframes sp{{to{{background-position:-64px 0}}}}
.info h3{{font-size:16px;margin:16px 0 8px;color:var(--n7)}}
.row{{display:flex;justify-content:space-between;padding:6px 0;box-shadow:0 var(--t) 0 var(--n2);font-size:15px}}.row span{{color:var(--n7)}}
/* spec board */
.spec{{max-width:1360px;margin:48px auto;padding:0 24px}}
.sw{{display:grid;grid-template-columns:repeat(10,1fr);gap:8px}}.sw div{{height:48px;box-shadow:0 0 0 var(--t) var(--n0);font:12px var(--disp);display:flex;align-items:flex-end;padding:4px;color:#fff;text-shadow:1px 1px 0 #000}}
.fonts{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}.fonts div{{background:var(--n2);padding:12px;box-shadow:var(--bevel)}}
.fx{{display:flex;gap:32px;align-items:end}}.fx figure{{margin:0;text-align:center;font:12px var(--disp);color:var(--n7)}}
.fire{{width:{fire[1]*2}px;height:{fire[2]*2}px;background:url(data:image/png;base64,{fire[0]}) 0 0/{fire[1]*2*fire[3]}px {fire[2]*2}px;animation:fi .8s steps({fire[3]}) infinite}}
@keyframes fi{{to{{background-position:-{fire[1]*2*fire[3]}px 0}}}}
.slash{{width:64px;height:64px;background:url(data:image/png;base64,{slash}) 0 0/512px 64px;animation:sl .5s steps(8) infinite}}@keyframes sl{{to{{background-position:-512px 0}}}}
'''
ic=P['ic']
html=f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Overhaul prototype</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Silkscreen&family=Pixelify+Sans:wght@500;700&family=Be+Vietnam+Pro:wght@400;600;700&display=swap"><style>{css}</style>
<header class="top"><a class="logo" href="#">Linggango<small>Unofficial Wiki</small></a>
<nav class="nav"><a class="btn on" href="#">The Path</a><a class="btn" href="#">Equipment</a><a class="btn" href="#">Bosses</a><a class="btn" href="#">Build planner</a><a class="btn" href="#">Mechanics</a></nav>
<input class="search" placeholder="Search curios, gear, bosses…  /"></header>
<main class="page">
<div class="crumb"><a href="#">Home</a> › <a href="#">The Path</a> › <a href="#">Act IX</a> › Hostility Curse</div>
<aside class="toc"><b>On this page</b><a class="on" href="#">How to get it</a><a href="#">Stats</a><a href="#">Related</a></aside>
<article>
<div class="head">{slot(ic)}<h1>{it['n']}</h1></div>
<p class="lead">{it['fx']}</p>
<div class="chips"><span class="chip" style="--c:{RC[it['r']]}"><i>■</i> {RN[it['r']]}</span><span class="chip">{it['m']}</span><span class="chip">Hostility Curse</span><span class="chip">Act IX</span><span class="chip">Craft</span></div>
<section class="panel"><h2>How to get it</h2><ol class="steps"><li>Craft at a Crafting Table from Miracle Ingot, Netherite Ingot, Eternium Ingot, Halo of Ascension, Killer Aura, Ragnarok and Dementor.</li><li>Hardest ingredient: Halo of Ascension, upgraded from Apostle's Broken Halo (Goety Revelation).</li></ol></section>
<section class="panel"><h2>Stats</h2><ul class="stats"><li>Extra level: 100</li><li>Obtain Abrahadabra</li><li>The Finale</li></ul></section>
<section class="panel"><h2>More Hostility Curse curios</h2><div class="cards">{cards}</div></section>
</article>
<aside class="info"><div class="art"><div class="frame"><img src="data:image/png;base64,{ic}" alt=""></div><i class="spark" style="left:40px;top:40px"></i><i class="spark" style="right:44px;bottom:36px;animation-delay:.3s"></i></div>
<h3>Abrahadabra</h3>
<div class="row"><span>Rarity</span><b style="color:{RC[it['r']]}">{RN[it['r']]}</b></div><div class="row"><span>Slot</span><b>Hostility Curse</b></div><div class="row"><span>Act</span><b>Act IX</b></div><div class="row"><span>Role</span><b>Tank</b></div><div class="row"><span>Mod</span><b>L2 Hostility</b></div></aside>
</main>
<section class="spec"><div class="panel"><h2>Design tokens (one texel = 2 px)</h2>
<div class="sw">{''.join(f'<div style="background:var(--n{i})">n{i}</div>' for i in range(10))}</div><br>
<div class="sw">{''.join(f'<div style="background:{c}">{n}</div>' for n,c in [('common','#ffffff'),('uncommon','#ffff55'),('rare','#55ffff'),('epic','#ff55ff'),('legend.','#ffaa00'),('mythic','#ff5555'),('xp','#55ff55'),('gold','#ffaa00'),('link','#ffff55'),('boss','#ec3fd0')])}</div><br>
<h2>Display font candidates</h2><div class="fonts"><div><div style="font:700 32px Monocraft">The Path 0123</div><small>Monocraft (OFL) — Minecraft-like, grid-exact at 16/32</small></div><div><div style="font:32px Silkscreen">The Path 0123</div><small>Silkscreen (OFL)</small></div><div><div style="font:700 32px 'Pixelify Sans'">The Path 0123</div><small>Pixelify Sans (current)</small></div></div><br>
<h2>Effects from the library at ×2</h2><div class="fx"><figure><div class="fire"></div>Goety big fire (MIT)</figure><figure><div class="slash"></div>fxgen slash, blood</figure><figure><div style="position:relative;width:32px;height:32px"><i class="spark" style="left:8px;top:8px"></i></div>fxgen sparkle, gold</figure>
<figure>{slot(ic)}<br>slot 40 / icon 32</figure><figure><a class="btn" href="#">Button</a><br>vanilla widgets ×2</figure></div></div></section>'''
open('proto.html','w').write(html); print(len(html)//1024,'KB')
