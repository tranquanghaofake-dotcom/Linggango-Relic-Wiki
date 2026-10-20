/* ---------- gear: weapons and armor per Act and playstyle, with tier lists ---------- */
/* GE: weapons and armor pieces, GS: armor sets (built by build/gear/gear_data.py from the pack files) */
const GROLE={ME:"Melee",RA:"Ranged",MA:"Mage",SU:"Summon",TA:"Tank"};
const GKIND={melee:"Melee weapon",ranged:"Ranged weapon",magic:"Staff / magic weapon",armor:"Armor"};
/* tier = share of the list ranked above: top 6% S, next 14% A, 20% B, 25% C, rest D (ties share a tier) */
const GTIER=[["S",.06,"#ff5f6d"],["A",.2,"#ffb347"],["B",.4,"#ffe066"],["C",.65,"#7bd88f"],["D",1.01,"#7aa7ff"]];
const GSLOT={HELMET:"Head",CHESTPLATE:"Chest",LEGGINGS:"Legs",BOOTS:"Feet"};
const GATTR={attack_damage:"Attack Damage",attack_speed:"Attack Speed",armor:"Armor",armor_toughness:"Armor Toughness",max_health:"Max Health",
 knockback_resistance:"Knockback Resistance",movement_speed:"Speed",luck:"Luck",critical_strike_chance:"Crit Chance",critical_strike_damage:"Crit Damage",
 crit_chance:"Crit Chance",crit_damage:"Crit Damage",lifesteal:"Lifesteal",life_steal:"Life Steal",entity_reach:"Reach",damage_taken:"Damage Taken",
 spell_power:"Spell Power",max_mana:"Max Mana",cooldown_reduction:"Cooldown Reduction",cast_time_reduction:"Cast Time Reduction",summon_damage:"Summon Damage",
 arrow_damage:"Arrow Damage",draw_speed:"Draw Speed",healing_received:"Healing Received",dodge_chance:"Dodge Chance",mining_speed:"Mining Speed",
 experience_gained:"XP Gained",armor_shred:"Armor Shred",mana_regen:"Mana Regen",spell_resist:"Spell Resist",natural_regeneration_increase:"Natural Regen"};
const gAttr=k=>GATTR[k]||k.replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase());
const gRound=v=>Math.round(v*100)/100;
/* "+12% Spell Power" / "+2 Attack Damage", the way the game words AttributeModifier operations */
const gMod=(k,add,mul)=>{const p=[];const pct=/chance|damage_taken|lifesteal|life_steal|crit_damage|critical_strike_damage|healing|dodge|reduction|shred/.test(k)&&Math.abs(add)<=2;
 if(add)p.push((add>0?"+":"")+(pct?gRound(add*100)+"%":gRound(add))+" "+gAttr(k));
 if(mul)p.push((mul>0?"+":"")+gRound(mul*100)+"% "+gAttr(k));return p};
const GBY={};GE.forEach((g,i)=>{g.ix=i;GBY[g.id]=g});GS.forEach((s,i)=>{s.ix=i;s.ps=s.p.map(id=>GBY[id]).filter(Boolean)});
const gIcon=g=>g.ps?(g.ps.find(p=>p.sl==="CHESTPLATE")||g.ps[0]):g;
const gImg=g=>img(gIcon(g).id);
const oiA=a=>ORDER.indexOf(a);
/* weapons whose base damage lives in code we could not read: estimated from same-gate weapons */
const GEST={};
{const by={};GE.filter(g=>g.k==="melee"&&g.sc.ME!=null).forEach(g=>(by[g.ga]=by[g.ga]||[]).push(g.sc.ME));
 for(const k in by){const v=by[k].sort((a,b)=>a-b);GEST[k]=v[Math.floor(v.length*.6)]}
 const all=Object.values(by).flat().sort((a,b)=>a-b),med=all[Math.floor(all.length/2)]||1;
 GE.forEach(g=>{if(g.k==="melee"&&g.sc.ME==null){g.sc.ME=GEST[g.ga]||med;g.est=1}
  /* ranged / magic: the pack's gate ladder is the power ladder, so later gates rank higher */
  if(g.k==="ranged"||g.k==="magic"){g.est=1;for(const r in g.sc)g.sc[r]=g.sc[r]*(1+.3*oiA(g.ga||0))}})}
GS.forEach(s=>{if(!s.kn)s.est=1});
/* pool for Act a, role r: everything unlocked at or before a */
function gPool(a,r,w){const ia=oiA(+a);
 const xs=(w==="a"?GS:GE.filter(g=>g.k!=="armor")).filter(g=>g.sc[r]!=null&&oiA(g.a)<=ia);
 return xs.sort((p,q)=>q.sc[r]-p.sc[r])}
const GTC=new Map();
function gTiers(a,r,w){const key=a+r+w;if(GTC.has(key))return GTC.get(key);const xs=gPool(a,r,w);let out=[];
 if(xs.length){const n=xs.length,b=GTIER.map(()=>[]);let prev=null,pt=0;
  xs.forEach((g,i)=>{let t=GTIER.findIndex(([,f])=>i<Math.max(1,Math.round(f*n)));if(t<0)t=GTIER.length-1;if(prev!=null&&g.sc[r]===prev)t=pt;b[t].push(g);prev=g.sc[r];pt=t});
  out=GTIER.map(([t],i)=>[t,b[i]])}
 GTC.set(key,out);return out}
function gTierOf(g,a,r,w){for(const [t,xs] of gTiers(a,r,w))if(xs.includes(g))return t;return null}
const gHref=g=>g.ps?"#gs"+g.ix:"#g"+g.ix;
const gTile=(g,a)=>`<a class="gtl${g.est?" est":""}" href="${gHref(g)}" data-t="${g.ps?"s":"g"}${g.ix}">${gImg(g)}${g.a===+a?'<i class="gnew">NEW</i>':""}${g.ps?`<i class="gpc">${g.ps.length}</i>`:""}<span>${esc(g.n)}</span></a>`;
const GSTATE={a:0,r:"ME",w:"w",q:""};let GALL=false;
document.addEventListener("click",e=>{if(e.target.closest("[data-gall]")){GALL=true;const y=scrollY;gearPage(location.hash);scrollTo(0,y)}});
let GLASTH="";
try{Object.assign(GSTATE,JSON.parse(localStorage.getItem("lgw-gear")||"{}"))}catch(e){}
function gearPage(h){
 const m=h.match(/^#gear(?:\/([\d.]+))?(?:\/(\w\w))?(?:\/([wa]))?/);if(m){if(m[1]!=null)GSTATE.a=+m[1];if(m[2])GSTATE.r=m[2];if(m[3])GSTATE.w=m[3]}
 if(!ORDER.includes(+GSTATE.a))GSTATE.a=0;if(GSTATE.w==="w"&&GSTATE.r==="TA")GSTATE.r="ME";
 try{localStorage.setItem("lgw-gear",JSON.stringify(GSTATE))}catch(e){}
 const {a,r,w}=GSTATE;document.title=`Gear tier list · ${actL(a)} · Linggango Wiki`;
 const roles=Object.keys(GROLE).filter(k=>w==="a"||k!=="TA");
 const tiers=gTiers(a,r,w),pool=tiers.reduce((n,x)=>n+x[1].length,0);
 const go=(A,R,W)=>`#gear/${A}/${R}/${W}`;
 const q=GSTATE.q.trim().toLowerCase();
 el("main").innerHTML=`${crumb("Gear")}<div class="gear">
 <div class="ghead" style="--tc:${ACT[a][2]};${tex(a)}"><span class="gem">${emblem(a,"lg")}</span><div><h1>Gear tier list</h1>
 <p class="lede">The best weapons and armor sets for each playstyle at <b>${esc(actL(a))}</b>: everything you can use once ${a==0?"you start":esc(UNL[a]||"")+" is beaten"}, ranked against the best you have at that point.</p></div></div>
 <nav class="gacts" aria-label="Act">${ORDER.filter(x=>x!=-1).map(x=>`<a href="${go(x,r,w)}" style="--tc:${ACT[x][2]}"${x===+a?' aria-current="page"':""} title="${esc(actF(x))}"><span class="gx">${emblem(x,"xs")}</span><b>${esc(ACT[x][0])}</b></a>`).join("")}</nav>
 <div class="gbar"><div class="gseg" role="tablist" aria-label="Weapons or armor">${[["w","⚔ Weapons"],["a","🛡 Armor sets"]].map(([k,t])=>`<a role="tab" href="${go(a,w===k?r:(k==="w"&&r==="TA"?"ME":r),k)}"${k===w?' aria-selected="true"':""}>${t}</a>`).join("")}</div>
 <div class="gseg roles" role="tablist" aria-label="Playstyle">${roles.map(k=>`<a role="tab" href="${go(a,k,w)}" style="--rc:${ROLE_C[k]||"#8a8f99"}"${k===r?' aria-selected="true"':""}>${GROLE[k]}</a>`).join("")}</div>
 <input id="gq" type="search" placeholder="Find a weapon or set…" value="${esc(GSTATE.q)}" aria-label="Find gear"></div>
 ${q?gSearch(q,a):`<div class="gtl-list">${tiers.length?tiers.map(([t,xs],i)=>`<section class="grow" style="--gc:${GTIER[i][2]}"><h2 class="glet">${t}</h2><div class="gtiles">${xs.length?(GALL?xs:xs.slice(0,48)).map(g=>gTile(g,a)).join("")+(!GALL&&xs.length>48?`<button class="gmore" data-gall>Show ${xs.length-48} more</button>`:""):'<span class="gnone">—</span>'}</div></section>`).join(""):`<p class="note">No ${w==="a"?"armor":"weapons"} for ${GROLE[r]} unlocked by ${esc(actL(a))} yet.</p>`}</div>`}
 <div class="gfoot"><p><b>${pool}</b> ${w==="a"?"sets":"weapons"} usable at ${esc(actL(a))}. <i class="gnew">NEW</i> unlocks at this Act. Faded tiles are <b>estimated</b>: their numbers are computed in code the wiki could not read, so they are ranked by their Keeper gate.</p>
 <details class="ghow"><summary>How the tiers are worked out</summary><ul>
 <li><b>Act</b>: the Keeper gate from Linggango's own progression tags (<code>forge:iron_tools</code> … <code>forge:helionite_armor</code>): gear tagged Diamond is locked until Eldorath falls, and so on. Gear with no tag sits at the Act of its hardest ingredient or drop (Nether materials need Act V, a Nether Star the Wither, End loot the Ender Dragon).</li>
 <li><b>Melee</b>: damage per second = (base damage + pack bonus) × attack speed, × crit (chance × (50% + crit damage)), × lifesteal and reach. Base damage and speed are read from each mod's code and config; the pack's extra modifiers (<i>attributesetter</i>) are added on top, as the game does.</li>
 <li><b>Ranged, Mage, Summon weapons</b>: their bonuses (arrow damage, spell power, mana, cooldowns, summon damage) plus their gate. Bow and gun damage is set in each mod's code at shot time, so these are estimates.</li>
 <li><b>Armor sets</b>: the four pieces added together. Tank = armor + 0.8 × toughness + ½ × max health + knockback resistance and damage-taken reduction. Melee / Ranged / Mage / Summon also count that role's bonuses.</li>
 <li>Tiers rank each item against the rest of the same list: the top 6% are S, the next 14% A, then 20% B, 25% C and the rest D, so every Act has a short S row however strong its best item is. Enchantments, reforges (Tiered) and set bonuses written in code are not counted.</li></ul></details></div></div>`;
 const gq=el("gq");gq.oninput=()=>{GSTATE.q=gq.value;try{localStorage.setItem("lgw-gear",JSON.stringify(GSTATE))}catch(e){};const p=gq.selectionStart;gearPage(location.hash);const n=el("gq");n.focus();n.setSelectionRange(p,p)};
 seedBg("gear"+a,[]);decorate();
}
function gSearch(q,a){const xs=[...GE.filter(g=>g.k!=="armor"),...GS].filter(g=>g.n.toLowerCase().includes(q)||g.id.includes(q)).slice(0,80);
 return `<div class="gtiles gsr">${xs.length?xs.map(g=>gTile(g,a)).join(""):'<p class="note">Nothing matches.</p>'}</div>`}
/* main role of an item: the one it scores in, preferring the role named by its kind */
const gMain=g=>{const k=Object.keys(g.sc);return g.ps?(k.filter(x=>x!=="TA").sort((p,q)=>(g.off[q]||0)-(g.off[p]||0))[0]||"TA"):(k[0]||"ME")};
function gStats(g){const rows=[];
 if(g.k==="armor"){if(g.arm!=null)rows.push(["gui_armor","Armor",gRound(g.arm),"code"]);if(g.tough)rows.push(["fx_resistance","Armor Toughness",gRound(g.tough),"code"]);if(g.kbr)rows.push(["","Knockback Resistance",gRound(g.kbr*10)/1,"code"])}
 else{if(g.dmg!=null)rows.push(["fx_strength","Attack Damage",gRound(g.dmg),"code"]);if(g.spd!=null)rows.push(["fx_haste","Attack Speed",gRound(g.spd),"code"])}
 return rows}
function gBonus(g){return Object.entries(g.at).filter(([k])=>!(g.k!=="armor"&&g.dmg!=null&&false)).flatMap(([k,[a,m]])=>gMod(k,a,m))}
function gSrcText(g){const o=[];
 g.rc.forEach(r=>{const ing=[...new Set(r.i)].filter(x=>x!==r.t&&!/^(minecraft:crafting_|goety:(craft|ritual)$|ars_nouveau:enchanting_apparatus$)/.test(x)).slice(0,9);o.push(`<div class="grc"><span class="grt">${esc(gStation(r.t))}</span>${ing.map(x=>{const n=r.i.filter(y=>y===x).length,c=n>1?`<b class="gn">${n}×</b>`:"";return x.startsWith("#")?`<span class="gin tag" title="${esc(x)}">${c}any ${esc(x.split(":")[1].split("/").pop().replace(/_/g," "))}</span>`:`<a class="gin" ${GBY[x]?`href="#g${GBY[x].ix}" data-t="g${GBY[x].ix}"`:BYID[x]?`href="#i${BYID[x].ix}" data-t="${BYID[x].ix}"`:""}>${img(x)}${c}<span>${esc(BYID[x]?BYID[x].n:NM[x]||nmI(x))}</span></a>`}).join("")}</div>`)});
 g.lt.forEach(t=>o.push(`<div class="glt">${esc(gLoot(t))}</div>`));
 return o.join("")||'<p class="note">No recipe or loot table found in the pack data (it may come from a boss drop written in code, a trade or a quest reward).</p>'}
const gStation=t=>{t=String(t);const m={"minecraft:crafting_shaped":"Crafting Table","minecraft:crafting_shapeless":"Crafting Table (shapeless)","minecraft:smithing_transform":"Smithing Table","minecraft:smithing":"Smithing Table","kubejs:shaped":"Crafting Table (pack recipe)","kubejs:shapeless":"Crafting Table (pack recipe, shapeless)","adamsarsplus:a_armor_upgrade":"Armor upgrade (Adam's Ars Plus)","ars_elemental:armor_upgrade":"Armor upgrade (Ars Elemental)","ars_nouveau:enchanting_apparatus":"Enchanting Apparatus (Ars Nouveau)","goety:ritual":"Goety ritual","justdirethings:tier_upgrade":"Tier upgrade (Just Dire Things)","l2archery:bow_craft":"Bow crafting (L2 Archery)","celestisynth:starlit_factory":"Starlit Factory (Celestisynth)","saintsdragons:draconic_crucible":"Draconic Crucible (Saint's Dragons)","cataclysm:weapon_fusion":"Weapon Fusion (Cataclysm)","biomancy:bio_forging":"Bio-Forge (Biomancy)","mekanism:mek_data":"Crafting Table (Mekanism, keeps data)","bloodmagic:soulforge":"Hellfire Forge (Blood Magic)","bloodmagic:array":"Alchemy Array (Blood Magic)","simplymore:unique_upgrade":"Unique upgrade (Simply More)","hexerei:mixingcauldron":"Mixing Cauldron (Hexerei)","create:mechanical_crafting":"Mechanical Crafter (Create)","kubejs:recipes.create.mechanical_crafting":"Mechanical Crafter (Create, pack recipe)","farmersdelight:cutting":"Cutting Board (Farmer's Delight)"};
 return m[t]||t.replace(/^kubejs:/,"Pack recipe: ").split(":").pop().replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase())};
const gLoot=t=>{const [ns,p]=t.split(":");const parts=p.split("/");const kind=parts[0];const what=parts.slice(1).join(" ").replace(/_/g," ");
 return (kind==="entities"?"Dropped by "+what:kind==="chests"?"Found in chests: "+what:kind==="gameplay"?"Gameplay loot: "+what:"Loot table: "+p.replace(/[_/]/g," "))+" ("+ns+")"};
function gTimeline(g){const r=gMain(g),w=g.ps?"a":"w";const acts=ORDER.filter(x=>x!=-1&&oiA(x)>=oiA(g.a));
 return `<div class="gtime">${acts.map(x=>{const t=gTierOf(g,x,r,w);const i=GTIER.findIndex(z=>z[0]===t);return `<a href="#gear/${x}/${r}/${w}" style="--tc:${ACT[x][2]};--gc:${i>=0?GTIER[i][2]:"#555"}" title="${esc(actL(x))}: ${t||"below D"} for ${GROLE[r]}"><b>${t||"–"}</b><small>${esc(ACT[x][0])}</small></a>`}).join("")}</div>`}
function gearItemPage(g){document.title=g.n+" · Linggango Wiki";seedBg("g"+g.ix,[]);
 const r=gMain(g),rows=gStats(g),bon=gBonus(g),set=g.k==="armor"?GS.find(s=>s.p.includes(g.id)):null;
 el("main").innerHTML=`${crumb('<a href="#gear">Gear</a>',esc(g.n))}<article class="gpage" style="--tc:${ACT[g.a][2]};${tex(g.a)}">
 <header class="gph"><span class="gbig">${img(g.id)}</span><div><h1>${esc(g.n)}</h1><p class="gsub">${esc(GKIND[g.k])}${g.sl?" · "+GSLOT[g.sl]:""} · <a href="#mod/${enc(MODN(g.ns))}">${esc(MODN(g.ns))}</a> · <code>${esc(g.id)}</code></p>
 <p class="gact"><span class="gx">${emblem(g.a,"xs")}</span>${esc(actL(g.a))}${g.ga?` · 🔒 locked until ${esc(GATEN[g.ga])} falls (Linggango progression tag)`:""}</p></div></header>
 <div class="gcols"><section class="gbox"><h2>Stats</h2>${rows.length?`<table class="gst">${rows.map(([ic,n,v,s])=>`<tr><td>${ic?`<i class="ai" style="--ai:var(--v-${ic})"></i>`:""}${n}</td><td class="num">${v}</td><td><span class="tg ${s}">${s==="code"?"Read from the mod":"Pack"}</span></td></tr>`).join("")}${g.sc.ME!=null&&!g.est?`<tr class="dps"><td>Damage per second</td><td class="num">${gRound(g.sc.ME)}</td><td><span class="tg auto">Wiki estimate</span></td></tr>`:""}</table>`:`<p class="note">Base ${g.k==="armor"?"armor":"damage"} is computed in this mod's code at run time; the wiki could not read it, so this item is ranked by its gate.</p>`}
 ${bon.length?`<h3>Bonuses</h3><ul class="gbon">${bon.map(x=>`<li>${fmt(x)}</li>`).join("")}</ul><p class="note">From the mod's own modifiers and the Linggango <i>attributesetter</i> rebalance, added on top of the base stats.</p>`:""}</section>
 <section class="gbox"><h2>Tier by Act</h2>${set?`<p class="note">The ${esc(set.n)} set as ${GROLE[gMain(set)]} armor, compared with every set usable at each Act.</p>${gTimeline(set)}`:`<p class="note">${GROLE[r]} weapons, compared with everything usable at each Act.</p>${gTimeline(g)}`}
 ${set?`<h3>Set</h3><a class="gsetl" href="#gs${set.ix}" data-t="s${set.ix}">${gImg(set)}<span>${esc(set.n)} · ${set.ps.length} piece${set.ps.length>1?"s":""}</span></a>`:""}</section></div>
 <section class="gbox"><h2>How to get</h2>${gSrcText(g)}</section></article>`;decorate()}
function gearSetPage(s){document.title=s.n+" set · Linggango Wiki";seedBg("gs"+s.ix,[]);const r=gMain(s);
 el("main").innerHTML=`${crumb('<a href="#gear/'+GSTATE.a+'/TA/a">Gear</a>',esc(s.n))}<article class="gpage" style="--tc:${ACT[s.a][2]};${tex(s.a)}">
 <header class="gph"><span class="gbig">${gImg(s)}</span><div><h1>${esc(s.n)} set</h1><p class="gsub">${s.ps.length} piece${s.ps.length>1?"s":""} · <a href="#mod/${enc(MODN(s.k.split(":")[0]))}">${esc(MODN(s.k.split(":")[0]))}</a></p>
 <p class="gact"><span class="gx">${emblem(s.a,"xs")}</span>${esc(actL(s.a))}</p></div></header>
 <div class="gcols"><section class="gbox"><h2>Full set</h2><table class="gst">${s.kn?`<tr><td><i class="ai" style="--ai:var(--v-gui_armor)"></i>Armor</td><td class="num">${gRound(s.arm)}</td></tr><tr><td><i class="ai" style="--ai:var(--v-fx_resistance)"></i>Toughness</td><td class="num">${gRound(s.tough)}</td></tr>`:`<tr><td colspan="2" class="note">Base armor is computed in code the wiki could not read.</td></tr>`}${s.hp?`<tr><td><i class="ai" style="--ai:var(--v-gui_heart)"></i>Max Health</td><td class="num">${s.hp>0?"+":""}${gRound(s.hp)}</td></tr>`:""}${s.kbr?`<tr><td>Knockback Resistance</td><td class="num">${gRound(s.kbr)}</td></tr>`:""}${s.dtk?`<tr><td>Damage taken</td><td class="num">${s.dtk>0?"−":"+"}${gRound(Math.abs(s.dtk)*100)}%</td></tr>`:""}</table>
 <h3>Pieces</h3><div class="gpcs">${s.ps.map(p=>`<a href="#g${p.ix}" data-t="g${p.ix}">${img(p.id)}<span>${esc(p.n)}</span><small>${p.arm!=null?gRound(p.arm)+" armor":""}${gBonus(p).length?" · "+gBonus(p).slice(0,2).join(", "):""}</small></a>`).join("")}</div></section>
 <section class="gbox"><h2>Tier by Act</h2><p class="note">As a ${GROLE[r]} set.</p>${gTimeline(s)}<p class="note">${Object.keys(s.sc).map(k=>GROLE[k]).join(", ")} lists include this set.</p></section></div></article>`;decorate()}
const GATEN={2:"Iron Colossus",3:"the Goblin Lord",4:"Arion",5:"Eldorath",6:"Zoranth the Forgotten",7:"the Elvenite Paladin",8:"Vaedric",10:"Sanghor",11:"Zoranth Newborn"};
const MODN=ns=>(MODS.find(([m,xs])=>xs.some(d=>d.id.startsWith(ns+":")))||[GNS[ns]||ns.replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase())])[0];
/* tooltip for gear tiles: same frame as the relic tooltip */
function gearTip(n){const k=n.dataset.t,isSet=k[0]==="s",g=isSet?GS[+k.slice(1)]:GE[+k.slice(1)];if(!g)return;tipFor=n;
 const P=GTIER.map(x=>x[2]),c=ACT[g.a][2];tip.className="to gtip"+(tip.classList.contains("on")?" on":"");delete tip.dataset.mf;
 tip.style.setProperty("--c1",c);tip.style.setProperty("--c2",c+"aa");tip.style.setProperty("--c3","#1a1420");
 const rows=isSet?(g.kn?[`${gRound(g.arm)} Armor`,`${gRound(g.tough)} Armor Toughness`]:[]).concat(g.hp?[`+${gRound(g.hp)} Max Health`]:[]):gStats(g).map(([,n,v])=>`${v} ${n}`);
 const bon=isSet?Object.entries(g.off).map(([r,v])=>`+${gRound(v*100)}% ${GROLE[r]} bonuses`):gBonus(g).slice(0,6);
 tip.innerHTML=`<div class="tbox"><div class="tfr"></div><div class="thd"><span class="tslot"><span class="aimg">${gImg(g)}</span></span><div class="tht"><div class="tnm">${esc(g.n)}${isSet?" set":""}</div><div class="tsub">${isSet?g.ps.length+(g.ps.length>1?" pieces":" piece"):esc(GKIND[g.k])+(g.sl?" · "+GSLOT[g.sl]:"")}</div></div></div>
 <div class="tbd">${rows.length?`<ul class="tst">${rows.map(x=>`<li>${fmt(x)}</li>`).join("")}</ul>`:""}${bon.length?`<ul class="tst">${bon.map(x=>`<li>${fmt(x)}</li>`).join("")}</ul>`:""}${g.est?'<p class="tsrc">≈ ranked by its Keeper gate (base stats not readable)</p>':""}${g.ga?`<p class="tlock">🔒 Locked until ${esc(GATEN[g.ga])} falls</p>`:""}<p class="twhere">${esc(actL(g.a))}</p></div>
 <div class="tft"><span class="tmod">${esc(MODN((g.id||g.k).split(":")[0]))}</span><span class="trt">${Object.keys(g.sc).map(r=>GROLE[r]).join(" · ")}</span></div></div>`;
 if(lastAct)lastAct.classList.remove("act");lastAct=null;const first=!tip.classList.contains("on");place(n);tip.classList.add("on");if(first)tip.classList.add("in")}
/* best gear of an Act, for the Act pages and the hub */
function gearBest(a){const cell=(r,w)=>{const t=gTiers(a,r,w);const s=t.length?t[0][1]:[];const nw=s.filter(g=>g.a===+a);const pick=(nw.length?nw:s).slice(0,3);
  return pick.length?`<div class="gbc"><a class="gbr" href="#gear/${a}/${r}/${w}" style="--rc:${ROLE_C[r]||"#8a8f99"}">${GROLE[r]}</a><div class="gbt">${pick.map(g=>gTile(g,a)).join("")}</div></div>`:""};
 const W=["ME","RA","MA","SU"].map(r=>cell(r,"w")).join(""),A=["TA","ME","RA","MA","SU"].map(r=>cell(r,"a")).join("");
 return `<section class="gbest"><div class="hsec"><div><h2>Best gear at ${esc(actL(a))}</h2><p>S-tier weapons and armor sets for each playstyle once this Act opens. New unlocks first.</p></div><a href="#gear/${a}/ME/w">Full tier list →</a></div>
 <div class="gbg"><div><h3>⚔ Weapons</h3>${W||'<p class="note">No new weapons.</p>'}</div><div><h3>🛡 Armor sets</h3>${A||'<p class="note">No armor yet.</p>'}</div></div></section>`}
/* ---------- hooks into the wiki's router, tooltip and pages ---------- */
{const R0=render;render=function(){const h=decodeURIComponent(location.hash);if(h!==GLASTH){GALL=false;GLASTH=h}
  document.body.classList.toggle("gearv",h.startsWith("#gear")||/^#gs?\d+$/.test(h));
  if(h.startsWith("#gear")||/^#gs?\d+$/.test(h)){save();refreshSide();document.body.classList.remove("hub");const mn=el("main");mn.classList.remove("enter");void mn.offsetWidth;mn.classList.add("enter");
   if(h.startsWith("#gear"))gearPage(h);else if(h.startsWith("#gs")&&GS[+h.slice(3)])gearSetPage(GS[+h.slice(3)]);else if(GE[+h.slice(2)])gearItemPage(GE[+h.slice(2)]);else gearPage("#gear");scrollTo(0,0);return}
  R0()};
 const T0=showTip;showTip=function(n){const k=n.dataset.t;if(k&&/^[gs]\d/.test(k))gearTip(n);else T0(n)};
 const H0=hubList;hubList=function(kind,key){H0(kind,key);if(kind==="act"){const a=+key,x=el("main").querySelector(".lhero");if(a!=-1&&x)x.insertAdjacentHTML("afterend",gearBest(a));decorate()}};
 const HH=hubHome;hubHome=function(){HH();const p=el("main").querySelector(".pillars");
  if(p){const ic=GE.find(g=>g.k==="melee"&&g.a===12&&IC[g.id])||GE.find(g=>IC[g.id]);p.insertAdjacentHTML("beforeend",`<a class="pil" href="#gear"><span class="ic">${ic?img(ic.id):""}</span><span><h3>Gear tier list</h3><p>Weapons and armor sets for Melee, Ranged, Mage, Summon and Tank, Act by Act.</p></span></a>`)}
  const acts=el("main").querySelector(".acts");if(acts){acts.closest("div")&&acts.insertAdjacentHTML("afterend",`<div class="hsec"><div><h2>Gear tier list</h2><p>${GE.filter(g=>g.k!=="armor").length} weapons and ${GS.length} armor sets from the pack, ranked for each playstyle at every Act.</p></div><a href="#gear">Open →</a></div><div class="gstrip">${ORDER.filter(a=>a!=-1).map(a=>{const t=gTiers(a,"ME","w"),g=t.length&&t[0][1][0];return `<a href="#gear/${a}/ME/w" style="--tc:${ACT[a][2]}" title="${esc(actL(a))}"${g?` data-t="g${g.ix}"`:""}>${g?gImg(g):""}<b>${esc(ACT[a][0])}</b></a>`}).join("")}</div>`)}};
}
render();decorate();
