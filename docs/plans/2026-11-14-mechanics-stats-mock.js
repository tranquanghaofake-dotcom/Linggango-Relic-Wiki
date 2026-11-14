// Mock-up of Mechanics > Stats "One hit, step by step", direction 2 (2026-11-14): not wired into the wiki yet; waits for the owner's approval.
// It injects CSS, HTML and JS into #m-stats of the built offline page and shoots three screenshots:
//   bash build/patches/apply_all.sh && node docs/plans/2026-11-14-mechanics-stats-mock.js <out dir>   (h2_a.png, h2_b.png, h2_phone.png)
// Rules checked against the pack: soft cap = knee x sqrt(m / knee), knee 3.0 (linggango_tweaks AccessoryLimitsMath.softened and
// config/linggango_tweaks-accessory_limits.toml); floor 13% of the incoming hit and hit cap 1/2 max health (linggango_tweaks-common.toml [damage_floor]);
// lifesteal cap 10% of the attacker's max health a tick ([lifesteal_cap]); armor A/(A+armor) and Resistance levels as on the Stats page.
const { chromium } = require('playwright'), path = require('path');
const CSS = `
.h2x{--side-a:#3c7d1e;--side-b:#2a5ea8;--gold:#ffd84a;--ink:#e9e6dc;--mute:#a9a597}
.h2x .lead{max-width:72ch;margin:0 0 14px;color:var(--ink)}
.h2x .board{background:#14131a;box-shadow:0 0 0 2px #000,inset 2px 2px 0 #34333f,inset -2px -2px 0 #09080c;padding:16px 16px 10px}
.h2x .sides{display:grid;grid-template-columns:5fr 3fr 1fr;gap:8px;margin-bottom:8px;font:700 12px monospace;letter-spacing:.06em;text-transform:uppercase}
.h2x .sides div{padding:4px 8px;color:#fff;box-shadow:0 0 0 2px #000}
.h2x .sides .a{background:var(--side-a)}.h2x .sides .b{background:var(--side-b)}.h2x .sides .c{background:#6b3b8f}
.h2x .track{display:grid;grid-template-columns:repeat(9,1fr);gap:8px;position:relative}.h2x .col{display:flex;flex-direction:column;align-items:center;min-width:0}
.h2x .track:before{content:"";position:absolute;left:4%;right:4%;top:34px;height:6px;background:repeating-linear-gradient(90deg,#7a5a2c 0 10px,#5c4220 10px 14px);box-shadow:0 0 0 2px #000;z-index:0}
.h2x .st{position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;gap:6px;cursor:pointer;background:none;border:0;color:var(--ink);padding:0}
.h2x .slot{width:64px;height:64px;display:grid;place-items:center;background:#8b8b8b;box-shadow:inset 3px 3px 0 #373737,inset -3px -3px 0 #fff;position:relative}
.h2x .slot i{transform:scale(1.5)}
.h2x .st .no{position:absolute;left:-6px;top:-6px;width:22px;height:22px;display:grid;place-items:center;background:#000;color:var(--gold);font:700 12px monospace;box-shadow:0 0 0 2px #555}
.h2x .st b{font-size:13px;text-align:center;line-height:1.2}
.h2x .st.on .slot{background:#c6c6c6;outline:3px solid var(--gold);outline-offset:2px}
.h2x .st.byp .slot:after{content:"may miss";position:absolute;bottom:-2px;right:-26px;font:700 9px monospace;color:#fff;background:#a32b1c;padding:1px 3px;box-shadow:0 0 0 1px #000}

.h2x .dmg{display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:150px;width:100%;margin-top:14px;padding-top:6px;border-top:2px dashed #34333f}
.h2x .dmg span{font:700 13px monospace;color:var(--gold);margin-bottom:4px}
.h2x .dmg i{display:block;width:60%;min-height:2px;background:linear-gradient(#e0533d,#8e2414);box-shadow:0 0 0 2px #000,inset 2px 2px 0 rgba(255,255,255,.25);height:calc(var(--p)*100px)}
.h2x .dmg.heal i{background:linear-gradient(#e86fa0,#9b2a5e)}.h2x .dmg.cut i{background:linear-gradient(#7e8aa0,#3b4254)}
.h2x .dmg small{font-size:10px;color:var(--mute);margin-top:4px;text-align:center;min-height:24px}
.h2x .lower{display:grid;grid-template-columns:1.25fr 1fr;gap:14px;margin-top:14px}
.h2x .panel{background:#1b1a22;box-shadow:0 0 0 2px #000,inset 2px 2px 0 #3a3946,inset -2px -2px 0 #0d0c12;padding:14px 16px}
.h2x .panel h4{margin:0 0 8px;font:700 16px var(--head,inherit);color:#fff;display:flex;gap:10px;align-items:center}
.h2x .panel p{margin:0 0 10px;color:var(--ink);max-width:62ch}
.h2x .math{font:13px monospace;background:#0d0c12;box-shadow:inset 0 0 0 2px #000;padding:8px 10px;color:#bfe3a8;margin:8px 0}
.h2x .chips{display:flex;flex-wrap:wrap;gap:4px}.h2x .chips a{font-size:11px;padding:2px 6px;background:#0d0c12;box-shadow:0 0 0 1px #4a4955;color:#e9e6dc;text-decoration:none}
.h2x .ctl{display:grid;grid-template-columns:auto 1fr auto;gap:8px 10px;align-items:center;font-size:13px;color:var(--ink)}
.h2x .ctl output{font:700 13px monospace;color:var(--gold);min-width:5ch;text-align:right}
.h2x .ctl input[type=range]{width:100%}.h2x .tog{display:flex;gap:8px;align-items:center;font-size:13px;margin-top:8px;color:var(--ink)}
.h2x .hres{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 10px;margin-top:12px;padding-top:10px;border-top:2px solid #2c2b35}
.h2x .hres b{font:700 30px var(--head,inherit);color:var(--gold)}.h2x .hres span{color:var(--mute);font-size:13px;flex:1;min-width:14ch}
.h2x .hest{font-size:11px;color:var(--mute);margin-top:6px}
@media (max-width:640px){.h2x .board{padding:10px}.h2x .sides{display:none}.h2x .track{grid-template-columns:1fr;gap:6px}.h2x .track:before{display:none}
.h2x .col{display:grid;grid-template-columns:auto 1fr;align-items:center;gap:10px;padding:4px 6px 4px 10px;box-shadow:inset 4px 0 0 var(--g)}
.h2x .col[data-gl]:before{content:attr(data-gl);grid-column:1/-1;font:700 11px monospace;text-transform:uppercase;letter-spacing:.06em;color:#fff;background:var(--g);margin:6px -6px 2px -10px;padding:3px 8px}
.h2x .st{flex-direction:row;gap:10px;justify-content:flex-start;width:150px}.h2x .st .slot{width:44px;height:44px;flex:none}.h2x .st .slot i{transform:none}.h2x .st .slot img{width:28px!important;height:28px!important}.h2x .st b{text-align:left}
.h2x .st.byp .slot:after{display:none}
.h2x .dmg{height:auto;margin:0;padding:0;border:0;display:grid;grid-template-columns:auto 1fr;grid-template-rows:auto auto;align-items:center;justify-items:start;gap:0 8px}
.h2x .dmg span{grid-row:1/3;margin:0;min-width:4ch;text-align:right}.h2x .dmg i{height:12px;width:calc(var(--p)*100%)}.h2x .dmg small{min-height:0;margin:2px 0 0;text-align:left}
.h2x .lower{grid-template-columns:1fr}.h2x .ctl{grid-template-columns:1fr auto}.h2x .ctl label{grid-column:1/-1;margin-bottom:-6px}}
`;
const HTML = `<h2>Stats explained</h2><h3>One hit, step by step</h3>
<p class="lead">A hit travels through nine steps. The first five happen on your side, the next three on the target. Move the sliders and watch the damage shrink step by step; click a step to read what happens there.</p>
<div class="board"><div class="sides"><div class="a">Your side: build the hit</div><div class="b">The target's side: cut it down</div><div class="c">After</div></div>
<div class="track" id="trk"></div></div>
<div class="lower"><div class="panel" id="det"></div><div class="panel"><h4>Try a hit</h4><div class="ctl">
<label for="cb">Weapon hit</label><input id="cb" type="range" min="1" max="100" value="12"><output id="ob"></output>
<label for="cm">Step 4 multiplier (Apothic crit, Exposed…)</label><input id="cm" type="range" min="10" max="100" value="15"><output id="om"></output>
<label for="ca">Target armor</label><input id="ca" type="range" min="0" max="100" value="20"><output id="oa"></output>
<label for="cr">Resistance level</label><input id="cr" type="range" min="0" max="10" value="0"><output id="or"></output>
<label for="ch">Target max health</label><input id="ch" type="range" min="20" max="200" step="2" value="40"><output id="oh"></output></div>
<label class="tog"><input id="cp" type="checkbox" checked> The target is a player (13% floor, ½ max health cap)</label>
<div class="hres"><b id="out">0</b><span id="outs"></span></div><p class="hest">Rules from the pack itself: soft cap knee 3.0, damage floor 13%, hit cap ½ max health, lifesteal cap 10% (Linggango Tweaks config). Crits, dodges and Protection are left out of this example.</p></div></div>`;
const JS = `(()=>{const R=[0,.20,.24,.29,.33,.38,.42,.47,.51,.56,.60];
const S=[['Swing','ri_diamond_sword','Weapon damage, scaled by how charged the attack is.',['Attack Damage','Sword Damage','Food buffs']],
['Melee crit','minecraft:strength','Decided once per swing, melee only.',['Crit Chance','Crit Damage']],
['Dodge','minecraft:invisibility','The target may avoid the hit completely: then nothing below happens.',['Dodge Chance','Roll','Parry']],
['Bonus stage','minecraft:haste','Every bonus multiplier on the hit, before armor. They multiply each other.',['Apothic Crit','Exposed','Perfect Hit','Summon Damage']],
['Soft cap','minecraft:slowness','How much step 4 grew the hit is measured. Up to ×3 it stays; past ×3 the growth only counts as 3 × √(growth ÷ 3): ×10 lands as ×5.5, ×1000 as ×55.',['Everything in step 4']],
['Armor','ri_iron_chestplate','The target keeps A / (A + armor) of the hit: A is 10 for hits under 20, 10 + (hit − 20) / 2 above. Big hits go through armor better.',['Armor','Armor Penetration','Armor Shred','Lethality']],
['Resistance','minecraft:resistance','The Resistance effect, rescaled by the pack (I 20% … V 38% … X 60%), then Protection.',['Resistance','Protection']],
['Floor & cap','sb_heart','Players only: at least 13% of the hit lands, and one hit never takes more than half of max health.',['Max Health']],
['Healing','minecraft:regeneration','Lifesteal stats heal the attacker; all of them together give back at most 10% of the attacker’s own max health a tick.',['Lifesteal','Omnivamp','Overheal']]];
const ic=k=>k.indexOf(':')>0?(window.EFXI&&EFXI[k]?'<img alt="" style="width:36px;height:36px;image-rendering:pixelated" src="data:image/png;base64,'+EFXI[k]+'">':''):'<i class="ui ui2" style="--ui:var(--rt-'+k+')" aria-hidden="true"></i>';let cur=5;const $=id=>document.getElementById(id);
const G=i=>i<5?['#3c7d1e','Your side: build the hit',0]:i<8?['#2a5ea8','The target’s side: cut it down',5]:['#6b3b8f','After',8];
$('trk').innerHTML=S.map((s,i)=>{const g=G(i);return '<div class="col" style="--g:'+g[0]+'"'+(g[2]===i?' data-gl="'+g[1]+'"':'')+'><button class="st'+(i===2?' byp':'')+'" data-i="'+i+'"><span class="slot"><span class="no">'+(i+1)+'</span>'+ic(s[1])+'</span><b>'+s[0]+'</b></button><div class="dmg" id="d'+i+'"></div></div>'}).join('');
function calc(){const b=+$('cb').value,m=$('cm').value/10,a=+$('ca').value,r=+$('cr').value,h=+$('ch').value,pl=$('cp').checked;
 const s4=b*m,cm=m<=3?m:Math.sqrt(3*m),s5=b*cm,A=s5<20?10:10+(s5-20)/2,s6=s5*A/(A+a),s7=s6*(1-R[r]),s8=pl?Math.min(Math.max(s7,.13*s5),h/2):s7;
 $('ob').value=b;$('om').value='×'+m.toFixed(1);$('oa').value=a;$('or').value=r?['','I','II','III','IV','V','VI','VII','VIII','IX','X'][r]:'none';$('oh').value=h;
 const v=[b,b,b,s4,s5,s6,s7,s8,null],lab=['base','','no dodge',m===1?'':'×'+m.toFixed(1),m>3?'capped ×'+cm.toFixed(2):'under ×3',Math.round(100*A/(A+a))+'% kept',r?'−'+Math.round(R[r]*100)+'%':'no effect',pl?(s8>s7?'floor 13%':s8<s7?'½ HP cap':'no change'):'not a player','≤10% of your max HP a tick'];
 const mx=Math.max(...v.filter(x=>x!=null),1);v.forEach((x,i)=>{const d=$('d'+i);d.className='dmg'+(x==null?' heal':i>=5&&i<=7?' cut':'');d.innerHTML=x==null?'<span>♥</span><small>'+lab[i]+'</small>':'<span>'+(Math.round(x*10)/10)+'</span><i style="--p:'+Math.max(.02,x/mx)+'"></i><small>'+lab[i]+'</small>'});
 $('out').textContent=(Math.round(s8*10)/10);$('outs').textContent='damage lands from a '+b+' hit ('+Math.round(100*s8/Math.max(b,1))+'% of the weapon hit)';
 const st=S[cur],ex=[ 'base hit = '+b,'not rolled in this example: a crit multiplies the swing here','if dodged: 0 damage, the chain stops','bonus: '+b+' × '+m.toFixed(1)+' = '+(Math.round(s4*10)/10),m>3?'3 × √('+m.toFixed(1)+' ÷ 3) = ×'+cm.toFixed(2)+' → '+(Math.round(s5*10)/10):'×'+m.toFixed(1)+' is under ×3: unchanged','A = '+(Math.round(A*10)/10)+' → '+(Math.round(s5*10)/10)+' × '+(Math.round(A*10)/10)+' / ('+(Math.round(A*10)/10)+' + '+a+') = '+(Math.round(s6*10)/10),r?'× (1 − '+R[r]+') = '+(Math.round(s7*10)/10):'no Resistance: unchanged',pl?'min(max('+(Math.round(s7*10)/10)+', 13% of '+(Math.round(s5*10)/10)+'), '+h/2+') = '+(Math.round(s8*10)/10):'not a player: unchanged','heal ≤ 10% of your own max health per tick, however much lifesteal you stack'][cur];
 $('det').innerHTML='<h4><span class="slot" style="width:40px;height:40px">'+ic(st[1])+'</span>'+(cur+1)+'. '+st[0]+'</h4><p>'+st[2]+'</p><div class="math">'+ex+'</div><div class="chips">'+st[3].map(c=>'<a href="#">'+c+'</a>').join('')+'</div>';
 document.querySelectorAll('.h2x .st').forEach(e=>e.classList.toggle('on',+e.dataset.i===cur))}
document.querySelectorAll('.h2x .st').forEach(e=>e.onclick=()=>{cur=+e.dataset.i;calc()});['cb','cm','ca','cr','ch','cp'].forEach(id=>$(id).oninput=calc);calc();window.__set=(o)=>{for(const k in o){if(k==='cur')cur=o[k];else if(k==='cp')$('cp').checked=o[k];else $(k).value=o[k]}calc()}})()`;
(async () => { const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.resolve('dist/Linggango_Relic_Wiki.html'), { waitUntil: 'load' }); await p.waitForTimeout(2000);
  await p.evaluate(() => { location.hash = '#mechanics/stats' }); await p.waitForTimeout(1500);
  const info = await p.evaluate(([css, html, js]) => { const sec = document.getElementById('m-stats'); sec.classList.add('h2x');
    const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st); sec.innerHTML = html; (0, eval)(js); sec.scrollIntoView(); scrollBy(0, -12);
    return typeof ui === 'function' ? ui('minecraft:strength', 1).slice(0, 80) : 'no ui()'; }, [CSS, HTML, JS]);
  console.log('icon sample:', info);
  await p.waitForTimeout(500); await p.screenshot({ path: process.argv[2] + '/h2_a.png' });
  await p.evaluate(() => window.__set({ cb: 30, cm: 100, ca: 60, cr: 5, ch: 40, cp: true, cur: 4 })); await p.waitForTimeout(300); await p.screenshot({ path: process.argv[2] + '/h2_b.png' });
  await p.setViewportSize({ width: 390, height: 1400 }); await p.waitForTimeout(800); await p.evaluate(() => { document.getElementById('m-stats').scrollIntoView() }); await p.screenshot({ path: process.argv[2] + '/h2_phone.png' });
  await b.close(); })();
