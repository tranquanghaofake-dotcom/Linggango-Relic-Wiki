/* ---------- gear: weapons and armor per Act and playstyle, with tier lists ---------- */
/* GE: weapons and armor pieces, GS: armor sets (built by build/gear/gear_data.py from the pack files) */
const GROLE={ME:"Melee",RA:"Ranged",MA:"Mage",SU:"Summon"};
const GKIND={melee:"Melee weapon",ranged:"Ranged weapon",magic:"Staff / magic weapon",summon:"Summon weapon",armor:"Armor"};
/* tier = score as a share of the best score at that Act: S ≥85%, A ≥70%, B ≥55%, C ≥40%, else D */
const GTIER_R=[.85,.7,.55,.4,0];
/* gear under a quarter of the best at an Act is left off its list (still found by search and on its own page) */
const GFLOOR=.25;
const GTIER=[["S",.06,"#d0564c"],["A",.2,"#d98a3d"],["B",.4,"#cdb45a"],["C",.65,"#6fa86a"],["D",1.01,"#6f8fc4"]];
const GSLOT={HELMET:"Head",CHESTPLATE:"Chest",LEGGINGS:"Legs",BOOTS:"Feet"};
const GATTR={attack_damage:"Attack Damage",attack_speed:"Attack Speed",armor:"Armor",armor_toughness:"Armor Toughness",max_health:"Max Health",
 knockback_resistance:"Knockback Resistance",movement_speed:"Speed",luck:"Luck",critical_strike_chance:"Critical Chance",critical_strike_damage:"Critical Damage",
 crit_chance:"Crit Chance",crit_damage:"Crit Damage",lifesteal:"Lifesteal",life_steal:"Life Steal",entity_reach:"Reach",damage_taken:"Damage Taken",
 spell_power:"Spell Power",max_mana:"Max Mana",cooldown_reduction:"Cooldown Reduction",cast_time_reduction:"Cast Time Reduction",summon_damage:"Summon Damage",
 arrow_damage:"Arrow Damage",draw_speed:"Draw Speed",healing_received:"Healing Received",dodge_chance:"Dodge Chance",mining_speed:"Mining Speed",
 experience_gained:"XP Gained",armor_shred:"Armor Shred",mana_regen:"Mana Regen",spell_resist:"Spell Resist",natural_regeneration_increase:"Natural Regen"};
const gAttr=k=>GATTR[k]||k.replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase());
const gRound=v=>Math.round(v*100)/100;
/* "+12% Spell Power" / "+2 Attack Damage", the way the game words AttributeModifier operations */
/* Brutality's critical_strike_* attributes show their raw value in game ("+0.01 Critical Chance"), so they are not turned into percents */
const gMod=(k,add,mul)=>{const p=[];const pct=/chance|damage_taken|lifesteal|life_steal|crit_damage|healing|dodge|reduction|shred/.test(k)&&!/^critical_strike/.test(k)&&Math.abs(add)<=2;
 if(add)p.push((add>0?"+":"")+(pct?gRound(add*100)+"%":/^critical_strike/.test(k)?+add.toFixed(2):gRound(add))+" "+gAttr(k));
 if(mul)p.push((mul>0?"+":"")+gRound(mul*100)+"% "+gAttr(k));return p};
const GBY={};GE.forEach((g,i)=>{g.ix=i;GBY[g.id]=g});GS.forEach((s,i)=>{s.ix=i;s.ps=s.p.map(id=>GBY[id]).filter(Boolean)});
const gIcon=g=>g.ps?(g.ps.find(p=>p.sl==="CHESTPLATE")||g.ps[0]):g;
const gImg=g=>img(gIcon(g).id);
/* ORDER holds the wiki's Acts only; data from the pack can carry Warden / Wither steps (6.1, 6.2): they count as the last Act below them */
const oiA=a=>{const i=ORDER.indexOf(a);return i>=0?i:ORDER.reduce((n,x,k)=>x<=a?k:n,0)};
/* ---------- how the lists are scored ----------
   One idea for every list: what you deal x what you can take, using the game's own rules where the pack has them.
   - Better Combat (allow_fast_attacks, on by default) clears the target's hurt cooldown on every hit: melee DPS = hit x attack speed, no 2-hits/s cap.
   - Apothic Attributes replaces vanilla armor: damage taken x a/(a+armor), a = 10 for hits under 20, 10+(hit-20)/2 above.
     Armor toughness no longer reduces damage; it only weakens the attacker's armor shred and pierce (by 2% per point, at most 60%). */
/* progression ladder: one step per Act; Warden / Wither / Dragon are three thirds of a step */
const GLAD={0:0,2:1,3:2,4:3,5:4,6:5,6.1:5.33,6.2:5.67,6.3:6,7:7,8:8,9:9,10:10,11:11,12:12};
const gLad=a=>GLAD[a]!=null?GLAD[a]:oiA(a);
/* the hit armor is judged against at each Act: the attack damage (entitybalance.json) of the Keeper that ends it.
   Arion's own value is not in the file (12 sits between Goblin Lord and Eldorath); Act VIII is the Discord's four forms (20-68, about 50) */
const GHIT={0:10,2:11,3:12,4:14,5:20,6:30,6.3:30,7:38,8:50,9:42,10:46,11:50,12:50};
/* health from everything else you wear (curios, relics, levels) grows with the Act: armor +HP is judged on top of 20 + 4 per step */
const gBaseHP=a=>20+4*gLad(a);
/* survival counts fully for melee, less for roles that fight at range and let minions or distance soak hits */
const GSURV={ME:1,RA:.7,SU:.6,MA:.6};
const gS=(at,rx,p)=>{let t=0;for(const k in at)if(rx.test(k))t+=at[k][p];return t};
const gS2=(at,rx)=>gS(at,rx,0)+gS(at,rx,1);
const GCC=/^(crit_chance|crit_rate|critical_strike_chance)$/,GCD=/^(crit_damage|critical_strike_damage)$/;
/* effects read from the item's code (gear_fx.json): only those with a number the game itself uses are scored.
   On hit, on the target: poison does 1 damage every 25>>(level-1) ticks, wither every 40>>(level-1), fire 1 a second, instant
   damage 6x2^(level-1) at once; kept up as long as chance x attacks a second x duration reaches 1.
   On the wearer or holder: Strength +3 attack damage a level, Resistance -20% damage taken a level, Health Boost and Absorption
   +4 health a level. Effects a mod adds (bleeding, soul burn...) are listed on the page but not scored: their numbers live in code. */
const GDOT={"minecraft:poison":L=>20/(25>>Math.min(4,L-1)),"minecraft:wither":L=>20/(40>>Math.min(5,L-1))};
const gFxOn=(g,when,who)=>(g.fx||[]).filter(r=>!r.maybe&&(when.includes(r.when))&&r.who===who);
function gFxDot(g,spd){let dps=0,burst=0;
 for(const r of gFxOn(g,["hit"],"target")){const c=r.chance||1,up=Math.min(1,c*spd*Math.max(.05,(r.ticks||r.fire*20||20)/20));
  if(r.fire)dps+=1*Math.min(1,c*spd*r.fire);else if(GDOT[r.effect])dps+=GDOT[r.effect](r.level||1)*up;else if(r.effect==="minecraft:instant_damage")burst+=6*Math.pow(2,(r.level||1)-1)*c}
 return dps+burst*spd}
/* the same effects as attributes {attr:[add, mul]}, so the playstyle and survival formulas below take them like any bonus */
function gFxAt(g){const o={},add=(k,i,v)=>{(o[k]=o[k]||[0,0])[i]+=v};
 for(const r of gFxOn(g,["worn","carried"],"self")){const L=r.level||1;
  if(r.effect==="minecraft:strength")add("attack_damage",0,3*L);if(r.effect==="minecraft:resistance")add("resistance",1,.2*L);
  if(r.effect==="minecraft:health_boost"||r.effect==="minecraft:absorption")add("max_health",0,4*L)}
 return o}
const gAt=g=>{const f=gFxAt(g);if(!Object.keys(f).length)return g.at||{};const o={...(g.at||{})};for(const k in f)o[k]=[(o[k]||[0,0])[0]+f[k][0],(o[k]||[0,0])[1]+f[k][1]];return o};
/* melee: damage per second = (base + bonus) x speed, x crit (chance capped at 100%: +50% plus crit damage), x lifesteal and reach,
   + damage over time from what a hit puts on the target */
function gMelee(g){const at=gAt(g),a=k=>at[k]||[0,0];
 const hit=(g.dmg+a("attack_damage")[0])*(1+a("attack_damage")[1]),spd=Math.max(.25,(g.spd||1.6)+a("attack_speed")[0])*(1+a("attack_speed")[1]);
 const cc=Math.min(1,gS2(at,GCC)),cd=gS2(at,GCD);
 return hit*spd*(1+cc*(.5+cd))*(1+.5*gS(at,/^life_?steal$/,0))*(1+.05*a("entity_reach")[0])+gFxDot(g,spd)}
const GME=GE.filter(g=>g.k==="melee"&&g.dmg!=null);
/* the melee frontier at an Act: the ten best real (not estimated) weapons usable there; their mean DPS and mean hit */
const GFR={};
function gFront(a){const k=oiA(a);if(GFR[k])return GFR[k];
 const xs=GME.filter(g=>oiA(g.a)<=k).map(g=>[gMelee(g),(g.dmg+(g.at.attack_damage||[0])[0])*(1+(g.at.attack_damage||[0,0])[1])]).sort((p,q)=>q[0]-p[0]).slice(0,10);
 return GFR[k]={dps:xs.reduce((s,x)=>s+x[0],0)/xs.length,hit:xs.reduce((s,x)=>s+x[1],0)/xs.length}}
/* how much stronger the pack's weapons get per Act, fitted on the melee frontier (log-linear least squares over every Act): about +20% */
const GSTEP=(()=>{const p=ORDER.filter(x=>x>=0).map(a=>[gLad(a),Math.log(gFront(a).dps)]),n=p.length,
 sx=p.reduce((s,q)=>s+q[0],0),sy=p.reduce((s,q)=>s+q[1],0),sxx=p.reduce((s,q)=>s+q[0]*q[0],0),sxy=p.reduce((s,q)=>s+q[0]*q[1],0);
 return Math.min(1.3,Math.max(1.05,Math.exp((n*sxy-sx*sy)/(n*sxx-sx*sx))))})();
/* what a set of attributes {attr: [add, mul]} multiplies a role's output by (1 = nothing) */
const GOFF={
 /* flat attack damage counts against the frontier's hit at that Act: +2 is a lot at Act 0 and little at Act XII */
 ME:(at,a)=>(1+gS(at,/^attack_damage$/,0)/gFront(a).hit)*(1+gS(at,/^attack_damage$/,1))*(1+gS(at,/^attack_speed$/,1))
  *(1+Math.min(1,gS2(at,GCC))*(.5+gS2(at,GCD)))*(1+.5*gS(at,/^life_?steal$/,0)),
 /* Apothic arrow_damage / draw_speed are percent attributes (base 1); gun_damage is +1 on a shot of about 12 */
 RA:at=>(1+gS2(at,/^(arrow_damage|projectile_damage|bow_damage)$/)+gS(at,/^gun_damage$/,0)/12)*(1+gS2(at,/draw_speed$/))
  *(1+Math.min(1,gS2(at,/^(crit_chance|crit_rate|bow_crit_chance)$/))*(.5+gS2(at,/^crit_damage$/))),
 /* two spell systems, and a mage casts with one: the better of
    Iron's: spell power + the best single school (a mage builds around one), x cast rate from cooldowns, x mana (saturating: +300 = +25%), x regen;
    Ars Nouveau: flat spell damage against the Act's typical hit (like melee flat damage), x Ars mana */
 MA:(at,a)=>{let sch=0;for(const k in at)if(/_spell_power$/.test(k)&&k!=="spell_power")sch=Math.max(sch,at[k][1]);
  const mana=m=>1+.5*m/(m+300),m=gS(at,/^max_mana$/,0);
  const iron=(1+gS2(at,/^(spell_power|spell_potency)$/)+sch)/(1-Math.min(.6,gS(at,/^cooldown_reduction$/,1)))
   *(1+.5*gS(at,/^cast_time_reduction$/,1)+gS(at,/^casting_speed$/,0))*mana(m)*(1+.3*Math.min(1,gS(at,/^mana_regen$/,1)));
  const ars=(1+gS(at,/spell_damage$/,0)/gFront(a).hit)*mana(gS(at,/^ars_nouveau\.perk\.max_mana$/,0));
  return Math.max(iron,ars)},
 /* summon damage (percent), each extra minion slot +25% */
 SU:at=>(1+gS(at,/summon|minion_damage|servant|sentry/,1)+.05*gS(at,/summon_damage|servant|sentry/,0))*(1+.25*gS(at,/^minion_slots$/,0))};
const gOff=(g,r,a)=>GOFF[r](gAt(g),a);
/* effective health against the Act's hit: (base HP + max health) x (a + armor)/a, x damage taken, dodge and knockback resistance.
   Armor is shred by an assumed 10% (L2 Hostility traits, armor-piercing weapons), which toughness weakens */
function gEHP(f,a){const D=GHIT[a]!=null?GHIT[a]:50,A=D<20?10:10+(D-20)/2,at=f.at||{};
 const arm=Math.max(0,f.arm)*(1-.1*(1-Math.min(.6,.02*Math.max(0,f.tough))));
 const dr=Math.min(.8,Math.max(0,f.dtk+gS(at,/^resistance$/,1))),dg=Math.min(.5,gS(at,/^dodge_chance$/,0));
 return Math.max(1,gBaseHP(a)+f.hp)*(A+arm)/A/(1-dr)/(1-dg)*(1+.1*Math.min(1,f.kbr))}
/* how hard an item is to get, 0..1: boss and mob drops 1, crafted from many parts up to 1, chest or unknown loot lower */
const GNOISE=/^(minecraft:crafting_|goety:(craft|ritual)$|ars_nouveau:enchanting_apparatus$)/;
function gSrc(g){const lt=g.lt||[],rc=g.rc||[];
 if(lt.some(t=>/:entities\//.test(t)))return 1;
 if(rc.length){const n=new Set((rc[0].i||[]).filter(x=>x!==rc[0].t&&!GNOISE.test(x))).size;return Math.min(1,Math.max(0,(n-1)/8))}
 return lt.length?.5:.3}
/* Ranged, Mage, Summon weapons: their shot or spell damage lives in code, so they sit on the fitted power curve at their unlock rung,
   + up to 10% for how hard they are to get, x their readable bonuses for the role */
function gEstScore(g,r){const rung=gLad(oiA(g.a)>oiA(g.ga||0)?g.a:g.ga);return Math.pow(GSTEP,rung)*(1+.1*gSrc(g))*gOff(g,r,g.a)}
const gR3=v=>Math.round(v*1000)/1000;
/* roles a weapon is listed for: its kind first; a staff that also buffs minions is listed for Summon too,
   and any weapon whose melee damage is readable (staves, spears, gunblades) is a Melee candidate at its real DPS */
const gKindRoles=g=>{const k=g.k==="melee"?["ME"]:g.k==="ranged"?["RA"]:g.k==="summon"?["SU"]:["MA"].concat(gOff(g,"SU",g.a)>1.001?["SU"]:[]);
 return g.dmg!=null&&!k.includes("ME")?k.concat("ME"):k};
GE.forEach(g=>{g.sc={};if(g.k!=="armor")gKindRoles(g).forEach(r=>g.sc[r]=null);if(g.dmg!=null&&g.sc.ME!==undefined)g.sc.ME=gR3(gMelee(g))});
/* melee weapons whose base damage lives in code we could not read: estimated from same-gate weapons */
const GEST={};
{const by={};GME.forEach(g=>(by[g.ga]=by[g.ga]||[]).push(g.sc.ME));
 for(const k in by){const v=by[k].sort((a,b)=>a-b);GEST[k]=v[Math.floor(v.length*.6)]}
 const all=Object.values(by).flat().sort((a,b)=>a-b),med=all[Math.floor(all.length/2)]||1;
 GE.forEach(g=>{if(g.k==="melee"&&g.sc.ME==null){g.sc.ME=GEST[g.ga]||med;g.est=1}
  if(g.k==="ranged"||g.k==="magic"||g.k==="summon"){g.est=1;for(const r in g.sc)if(r!=="ME")g.sc[r]=gRound(gEstScore(g,r)*100)}})}
/* armor sets: score = output multiplier for the role x effective health ^ the role's weight, so a set has to earn its place in a list
   by what it adds (spell power, crit, summon damage) or by how much longer it keeps you alive; a plain set is the fallback everywhere.
   Sets whose base armor is computed in code get the median armor, toughness and health of known sets of their Act (robes x0.7, others x0.8) */
const GROBE=/robe|crown|hat|hood|cowl|mask/;
{const kn=GS.filter(s=>s.kn&&s.arm>0),med={};
 const medAt=a=>{const k=oiA(a);if(!med[k]){let v=kn.filter(s=>oiA(s.a)<=k&&oiA(s.a)>=k-1);if(!v.length)v=kn;
  const m=f=>v.map(s=>s[f]).sort((x,y)=>x-y)[v.length>>1];med[k]={arm:m("arm"),tough:m("tough"),hp:m("hp")}}return med[k]};
 GS.forEach(s=>{if(s.kn&&s.arm>0){s.f=s;return}
  const m=medAt(s.a),x=s.p.some(id=>GROBE.test(id.split(":")[1]))?.7:.8;s.est=1;
  s.f={arm:m.arm*x,tough:m.tough*x,hp:Math.max(s.hp,m.hp*x),kbr:s.kbr||0,dtk:s.dtk||0,at:s.at}})
 /* worn effects of the pieces count in the survival formula: Resistance as damage taken, Health Boost and Absorption as health */
 GS.forEach(s=>{if(!s.fx)return;const f=gFxAt(s);if(!Object.keys(f).length)return;s.f={...s.f,at:gAt(s),hp:(s.f.hp||0)+((f.max_health||[0])[0])}})}
const GSC=new Map();
function gSetScore(s,r,a){const key=s.ix+r+a;let v=GSC.get(key);
 if(v==null){v=gRound(gOff(s,r,a)*Math.pow(gEHP(s.f,a),GSURV[r]));GSC.set(key,v)}return v}
GS.forEach(s=>{s.sc={};for(const r of ["ME","RA","MA","SU"])s.sc[r]=gSetScore(s,r,s.a)});
/* an item's score for a role at an Act: weapons have one score; a set's depends on the Act (the hit it faces, the HP and hit it adds to) */
const gScore=(g,r,a)=>g.ps?gSetScore(g,r,a):g.sc[r];
/* hidden from the lists (search still finds them): items the pack disables, creative-only items
   (Iron's Gold Crown: +10000 mana, +100% spell power, 75% cooldown, a creative/supporter item) */
const GCREATIVE=new Set(["irons_spellbooks:gold_crown"]);
const gHidden=g=>(g.ob&&g.ob[0]==="!")||/creative only/i.test(g.n)||(g.ps?g.p:[g.id]).some(id=>GCREATIVE.has(id));
/* pool for Act a, role r: everything unlocked at or before a */
function gPool(a,r,w){const ia=oiA(+a);
 const xs=(w==="a"?GS:GE.filter(g=>g.k!=="armor")).filter(g=>g.sc[r]!=null&&oiA(g.a)<=ia&&!gHidden(g));
 return xs.map(g=>[g,gScore(g,r,+a)]).sort((p,q)=>q[1]-p[1])}
const GTC=new Map();
function gTiers(a,r,w){const key=a+r+w;if(GTC.has(key))return GTC.get(key);const xs=gPool(a,r,w);let out=[];
 if(xs.length){const b=GTIER.map(()=>[]);
  // tier = how close an item is to the best one usable at this Act, so old gear slides down as better gear opens
  const top=xs[0][1]||1;xs.forEach(([g,v])=>{const q=v/top;if(q<GFLOOR)return;let t=GTIER_R.findIndex(f=>q>=f);if(t<0)t=GTIER.length-1;b[t].push(g)});
  out=GTIER.map(([t],i)=>[t,b[i]]);out.top=top}
 GTC.set(key,out);return out}
function gTierOf(g,a,r,w){for(const [t,xs] of gTiers(a,r,w))if(xs.includes(g))return t;return null}
const gHref=g=>g.ps?"#gs"+g.ix:"#g"+g.ix;
/* a tile is faded when its score in this list is an estimate (a staff's Melee DPS is read, its Mage score is not) */
const gTile=(g,a,r)=>`<a class="gtl${g.est&&!(r==="ME"&&g.dmg!=null)?" est":""}${!g.ps&&g.k!=="armor"?" wpn":""}" href="${gHref(g)}" data-t="${g.ps?"s":"g"}${g.ix}">${gImg(g)}${g.a===+a&&+a!==ORDER[0]?'<i class="gnew">NEW</i>':""}${g.ps?`<i class="gpc">${g.ps.length}</i>`:""}<span>${esc(g.n).replace(/ \((Lv|Tier|Mk) /g," ($1&nbsp;")}</span></a>`;
const GSTATE={a:0,r:"ME",w:"w",q:""};let GALL=false;
document.addEventListener("click",e=>{if(e.target.closest("[data-gall]")){GALL=true;const y=scrollY;gearPage(location.hash);scrollTo(0,y)}});
let GLASTH="";
try{Object.assign(GSTATE,JSON.parse(localStorage.getItem("lgw-gear")||"{}"))}catch(e){}
GSTATE.q="";
function gearPage(h){
 const m=h.match(/^#gear(?:\/([\d.]+))?(?:\/(\w\w))?(?:\/([wa]))?/);if(m){if(m[1]!=null)GSTATE.a=+m[1];if(m[2])GSTATE.r=m[2];if(m[3])GSTATE.w=m[3]}
 if(!ORDER.includes(+GSTATE.a))GSTATE.a=0;if(!GROLE[GSTATE.r])GSTATE.r="ME";   // old links and saved state can still say TA (Tank, retired)
 try{localStorage.setItem("lgw-gear",JSON.stringify(GSTATE))}catch(e){}
 const {a,r,w}=GSTATE;document.title=`Equipment tier list · ${actL(a)} · Linggango Wiki`;
 const roles=Object.keys(GROLE);
 const tiers=gTiers(a,r,w),pool=tiers.reduce((n,x)=>n+x[1].length,0);
 const go=(A,R,W)=>`#gear/${A}/${R}/${W}`;
 const q=GSTATE.q.trim().toLowerCase();
 el("main").innerHTML=`${crumb("Equipment")}<div class="gear">
 ${room("forge",tiers.flatMap(([t,xs])=>xs.map(g=>({h:gHref(g),i:gImg(g),t:(g.ps?"s":"g")+g.ix,n:g.n,l:esc(t)}))).slice(0,10),{head:`<span class="gem">${emblem(a,"lg")}</span><div><h1>Equipment tier list</h1>
 <p class="lede">The best weapons and armor sets for each playstyle at <b>${esc(actL(a))}</b>: everything you can use once ${a==0?"you start":esc(UNL[a]||"")+" is beaten"}, ranked against the best you have at that point.</p></div>`,min:5,cols:5,label:"Best at this Act"})}
 <nav class="gacts" aria-label="Act">${ORDER.filter(x=>x!=-1).map(x=>`<a href="${go(x,r,w)}" style="--tc:${ACT[x][2]}"${x===+a?' aria-current="page"':""} title="${esc(actF(x))}"><span class="gx">${emblem(x,"xs")}</span><b>${esc(ACT[x][0])}</b></a>`).join("")}</nav>
 <div class="gbar"><div class="gseg" role="tablist" aria-label="Weapons or armor">${[["w",ui("sword")+" Weapons"],["a",ui("chest")+" Armor sets"]].map(([k,t])=>`<a role="tab" href="${go(a,r,k)}"${k===w?' aria-selected="true"':""}>${t}</a>`).join("")}</div>
 <div class="gseg roles" role="tablist" aria-label="Playstyle">${roles.map(k=>`<a role="tab" href="${go(a,k,w)}" style="--rc:${ROLE_C[k]||"#8a8f99"}"${k===r?' aria-selected="true"':""}>${GROLE[k]}</a>`).join("")}</div>
 <input id="gq" type="search" autocomplete="off" name="gearq" placeholder="Find a weapon or set…" value="${esc(GSTATE.q)}" aria-label="Find gear"></div>
 ${q?gSearch(q,a):`<div class="gtl-list">${tiers.length?tiers.map(([t,xs],i)=>`<section class="grow" style="--gc:${GTIER[i][2]}"><h2 class="glet">${t}</h2><div class="gtiles">${xs.length?(GALL?xs:xs.slice(0,48)).map(g=>gTile(g,a,r)).join("")+(!GALL&&xs.length>48?`<button class="gmore" data-gall>Show ${xs.length-48} more</button>`:""):'<span class="gnone">—</span>'}</div></section>`).join(""):`<p class="note">No ${w==="a"?"armor":"weapons"} for ${GROLE[r]} unlocked by ${esc(actL(a))} yet.</p>`}</div>`}
 <div class="gfoot"><p><b>${pool}</b> ${w==="a"?"sets":"weapons"} usable at ${esc(actL(a))}.${+a!==ORDER[0]?' <i class="gnew">NEW</i> unlocks at this Act.':""} Faded tiles are <b>estimated</b>: their damage is computed in code the wiki could not read, so they are ranked by when and how you get them (see below).</p>
 <details class="ghow"><summary>How the tiers are worked out</summary><ul>
 <li><b>Act</b>: the Keeper gate from Linggango's own progression tags (<code>forge:iron_tools</code> … <code>forge:helionite_armor</code>): gear tagged Diamond is locked until Eldorath falls, and so on. Gear with no tag sits at the Act of its hardest ingredient or drop (Nether materials need Act V, a Nether Star the Wither, End loot the Ender Dragon).</li>
 <li><b>Melee</b>: damage per second = (base damage + pack bonus) × attack speed, × crit (chance × (50% + crit damage)), × lifesteal and reach. Base damage and speed are read from each mod's code and config; the pack's extra modifiers (<i>attributesetter</i>) are added on top, as the game does. Better Combat clears the target's hurt cooldown on every hit, so fast weapons are not capped at two hits a second. Staves, spears and gunblades whose melee damage is readable are ranked here too.</li>
 <li><b>Ranged, Mage, Summon weapons</b>: bow, gun and spell damage is set in each mod's code at shot time, so it cannot be read. They sit on the pack's power curve at the Act they unlock: the ten best melee weapons get about ${Math.round((GSTEP-1)*100)}% stronger per Act (fitted over all Acts), so an item one Act behind the frontier is at ${Math.round(100/GSTEP)}%, three behind at ${Math.round(100/GSTEP**3)}%. Then up to +10% for how hard it is to get (a boss drop or a many-part recipe over a one-ingredient craft), times its readable bonuses for the role (below).</li>
 <li><b>Armor sets</b>: score = output bonus × effective health<sup>k</sup>, the damage you deal times how long you last. Effective health uses Apothic Attributes' armor rule (damage × a/(a + armor), a = 10 for hits under 20, 10 + (hit − 20)/2 above) against the attack damage of the Keeper that ends the Act (10 at Act 0, 30 at Act VI, 50 at Act XII), on top of 20 + 4 HP per Act from your other gear, × damage-taken reduction and dodge. Toughness only blunts armor shred in this pack, so it counts little. k = 1 for Melee, 0.7 Ranged, 0.6 Mage and Summon (fighting at range, you take fewer hits). Output bonus: Melee attack damage (flat bonus against the Act's typical weapon hit), attack speed, crit, lifesteal; Ranged arrow damage, draw speed, crit; Mage: the better of Iron's (spell power + the best single school, × cast rate from cooldown reduction, × mana: +300 mana = +25%) and Ars Nouveau (flat spell damage against the Act's typical hit, × mana); Summon summon damage and +25% per extra minion slot. A plain set is the fallback in every list; a set built for the role beats it. Sets whose armor is computed in code get the median of their Act.</li>
 <li>Tiers compare each item with the best one usable at that Act: S is within 85% of it, A within 70%, B within 55%, C within 40%, the rest D; under 25% it is left off the list (search still finds it). When stronger gear opens, older gear slides down, and the Tier by Act strip says when an item is outclassed. Enchantments, reforges (Tiered) and set bonuses written in code are not counted.</li></ul></details></div></div>`;
 const gq=el("gq");gq.oninput=()=>{GSTATE.q=gq.value;try{localStorage.setItem("lgw-gear",JSON.stringify(GSTATE))}catch(e){};const p=gq.selectionStart;gearPage(location.hash);const n=el("gq");n.focus();n.setSelectionRange(p,p)};
 seedBg("gear"+a,[]);decorate();
}
function gSearch(q,a){const xs=[...GE.filter(g=>g.k!=="armor"),...GS].filter(g=>g.n.toLowerCase().includes(q)||(g.id||g.k||"").includes(q)||(g.lv||[]).some(x=>x.includes(q))).slice(0,80);
 return `<div class="gtiles gsr">${xs.length?xs.map(g=>gTile(g,a)).join(""):'<p class="note">Nothing matches.</p>'}</div>`}
/* main role of an item: the one it scores in, preferring the role named by its kind */
/* main role of an item: a weapon's kind; a set's is, among the roles it has a bonus for (all roles if none), the one where it ranks highest at its own Act */
const gMain=g=>{const k=Object.keys(g.sc);if(!g.ps)return k[0]||"ME";const own=gRoles(g);let b="ME",bq=-1;
 for(const r of own.length?own:k){const q=gSetScore(g,r,g.a)/(gTiers(g.a,r,"a").top||1);if(q>bq){bq=q;b=r}}return b};
/* roles an item is worth listing for: a set with no bonus for a role is only a fallback there, so it is not advertised */
const gRoles=g=>g.ps?Object.keys(GROLE).filter(r=>gOff(g,r,g.a)>1.02):Object.keys(g.sc);
/* the tooltip's base lines already include flat (+N) armor/damage modifiers from the mod and the pack's rebalance,
   so they are folded in here and left out of the bonus list: Topaz Leggings read 5 armor, 1 toughness, as in game */
const GFOLD={armor:["arm","armor"],weapon:["dmg","spd"]};
const gAdd=(g,k)=>(g.at[k]||[0,0])[0];
function gStats(g){const rows=[];
 if(g.k==="armor"){if(g.arm!=null)rows.push(["gui_armor","Armor",gRound(g.arm+gAdd(g,"armor")),"code"]);const t=(g.tough||0)+gAdd(g,"armor_toughness");if(t)rows.push(["fx_resistance","Armor Toughness",gRound(t),"code"]);const kb=(g.kbr||0)+gAdd(g,"knockback_resistance");if(kb)rows.push(["","Knockback Resistance",gRound(kb*10),"code"])}
 else{if(g.dmg!=null)rows.push(["fx_strength","Attack Damage",gRound(g.dmg+gAdd(g,"attack_damage")),"code"]);if(g.spd!=null)rows.push(["fx_haste","Attack Speed",gRound(g.spd+gAdd(g,"attack_speed")),"code"])}
 return rows}
function gBonus(g){const fold=g.k==="armor"?(g.arm!=null?["armor","armor_toughness","knockback_resistance"]:[]):[g.dmg!=null?"attack_damage":"",g.spd!=null?"attack_speed":""];
 return Object.entries(g.at).flatMap(([k,[a,m]])=>gMod(k,fold.includes(k)?0:a,m))}
/* How to get, as pictures (like a curio page): each recipe as its station with the ingredient slots and the result,
   each loot table as a card (the mob's face, a chest). The pack exports gear recipes as ingredient lists, not grids. */
function gSrcText(g){const o=[],out=g.ps?gIcon(g).id:g.id;
 const slot=(x,n)=>{const t=GBY[x]||BYID[x],nm=x.startsWith("#")?"any "+x.split(":")[1].split("/").pop().replace(/_/g," "):BYID[x]?BYID[x].n:NM[x]||nmI(x),
  h=GBY[x]?`#g${GBY[x].ix}`:BYID[x]?`#i${BYID[x].ix}`:"";
  return `<${h?`a href="${h}"`:"div"} class="mcs"${GBY[x]?` data-t="g${GBY[x].ix}"`:BYID[x]?` data-t="${BYID[x].ix}"`:""} title="${esc(nm)}">${x.startsWith("#")?(typeof TAGID!=="undefined"&&IC[TAGID[x]]?img(TAGID[x]):`<span class="ph">${esc(nm)}</span>`)+`<span class="tagm">#</span>`:IC[x]?img(x):`<span class="ph">${esc(nm)}</span>`}${n>1?`<span class="cnt">${n}</span>`:""}</${h?"a":"div"}>`};
 g.rc.forEach(r=>{const ing=[...new Set(r.i)].filter(x=>x!==r.t&&!GNOISE.test(x)).slice(0,9),st=gStation(r.t);
  o.push(`<div class="mcwin k-row"><div class="mct"><span class="mcst">${stIcon(st)}</span>${esc(st)}</div><div class="mcrow"><div class="mcg mrow">${ing.map(x=>slot(x,r.i.filter(y=>y===x).length)).join("")}</div><i class="mca" aria-hidden="true"></i><div class="mcs big">${img(out)}</div></div></div>`)});
 const cards=g.lt.map(t=>{const [ns,p]=t.split(":"),parts=p.split("/"),what=parts.slice(1).join(" ").replace(/_/g," "),Nm=what.replace(/\b\w/g,c=>c.toUpperCase()),
   fk="mf_"+what.toLowerCase().replace(/ /g,"_"),pic=k=>`<i class="lrt" style="--lrt:var(--rt-${k})"></i>`;
  return parts[0]==="entities"?`<div class="lcard"><span class="lpic">${pic(ROOMT[fk]?fk:"spawner")}</span><span class="ltx"><b>${esc(Nm)}</b><small>Mob drop · ${esc(ns)}</small></span></div>`
   :parts[0]==="chests"?`<div class="lcard"><span class="lpic">${pic("ftb_chest")}</span><span class="ltx"><b>${esc(Nm)}</b><small>Chest loot · ${esc(ns)}</small></span></div>`
   :`<div class="lcard"><span class="lpic">${pic("ftb_chest")}</span><span class="ltx"><b>${esc(gLoot(t))}</b></span></div>`});
 if(cards.length)o.push(`<div class="lcards">${cards.join("")}</div>`);
 return o.join("")||(g.ob?"":'<p class="note">No recipe or loot table found in the pack data (it may come from a boss drop written in code, a trade or a quest reward).</p>')}
/* element and damage type of a weapon, read from its kind, its class and its name (the pack has no field for it) */
const GDT=[["Slash",/sword|katana|blade|scythe|dagger|sabre|saber|cutlass|claymore|machete|sickle|glaive/i,"ui_sword"],["Pierce",/spear|trident|rapier|lance|bident|pike|javelin|halberd|estoc/i,"dt_pierce"],
 ["Blunt",/hammer|mace|axe|club|maul|flail|cudgel|gauntlet|fist|knuckle|morningstar/i,"dt_blunt"]];
const GEL=[["Fire",/fire|flame|blaze|inferno|lava|magma|ember|infernal|burn|hellfire|ignis|pyre|scorch/i],["Ice",/frost|ice|frozen|glacial|snow|cryo|winter|blizzard/i],
 ["Lightning",/thunder|lightning|storm|volt|tesla|spark|zeus/i],["Ender / Eldritch",/void|ender|\bend\b|eldritch|abyss/i],["Dark",/shadow|dark|wither|soul|cursed|night|umbral|necro/i],
 ["Holy",/holy|divine|radiant|celestial|angel|sun|solar|light\b|sacred|paladin/i],["Blood",/blood|sangu|vampir|hemo|crimson/i],["Poison / Nature",/poison|venom|toxic|nature|thorn|vine|verdant|plague/i],["Water",/water|ocean|tide|aqua|sea|coral|hydro/i]];
function gKinds(g){if(g.k==="armor")return "";const nm=g.n+" "+g.id,cl=(g.cls||[]).join(" ");
 const dt=g.k==="ranged"?[["Projectile",0,"ui_bow"]]:g.k==="magic"?[["Magic",0,"dt_magic"]]:g.k==="summon"?[["Summon",0,"ui_bone"]]:GDT.filter(x=>x[1].test(nm+" "+cl)).slice(0,1);
 const el=GEL.filter(x=>x[1].test(nm)).slice(0,2).map(x=>x[0]);if(!dt.length&&!el.length)return "";
 return `<div class="kinds">${el.length?`<span class="klab">Element</span>${el.map(e=>kchip("el_"+(ELEM[e]||"fire"),e.replace(" / ","/"),"el")).join("")}`:""}${dt.length?`<span class="klab">Damage</span>${dt.map(x=>kchip(x[2],x[0],"dt")).join("")}`:""}<span class="kest" title="The pack has no field for these: the wiki reads them from the weapon's kind and name">estimate</span></div>`}
const gStation=t=>{t=String(t);const m={"minecraft:crafting_shaped":"Crafting Table","minecraft:crafting_shapeless":"Crafting Table (shapeless)","minecraft:smithing_transform":"Smithing Table","minecraft:smithing":"Smithing Table","kubejs:shaped":"Crafting Table (pack recipe)","kubejs:shapeless":"Crafting Table (pack recipe, shapeless)","adamsarsplus:a_armor_upgrade":"Armor upgrade (Adam's Ars Plus)","ars_elemental:armor_upgrade":"Armor upgrade (Ars Elemental)","ars_nouveau:enchanting_apparatus":"Enchanting Apparatus (Ars Nouveau)","goety:ritual":"Goety ritual","justdirethings:tier_upgrade":"Tier upgrade (Just Dire Things)","l2archery:bow_craft":"Bow crafting (L2 Archery)","celestisynth:starlit_factory":"Starlit Factory (Celestisynth)","saintsdragons:draconic_crucible":"Draconic Crucible (Saint's Dragons)","cataclysm:weapon_fusion":"Weapon Fusion (Cataclysm)","biomancy:bio_forging":"Bio-Forge (Biomancy)","mekanism:mek_data":"Crafting Table (Mekanism, keeps data)","bloodmagic:soulforge":"Hellfire Forge (Blood Magic)","bloodmagic:array":"Alchemy Array (Blood Magic)","simplymore:unique_upgrade":"Unique upgrade (Simply More)","hexerei:mixingcauldron":"Mixing Cauldron (Hexerei)","create:mechanical_crafting":"Mechanical Crafter (Create)","kubejs:recipes.create.mechanical_crafting":"Mechanical Crafter (Create, pack recipe)","farmersdelight:cutting":"Cutting Board (Farmer's Delight)"};
 return m[t]||t.replace(/^kubejs:/,"Pack recipe: ").split(":").pop().replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase())};
const gLoot=t=>{const [ns,p]=t.split(":");const parts=p.split("/");const kind=parts[0];const what=parts.slice(1).join(" ").replace(/_/g," ");
 return (kind==="entities"?"Dropped by "+what:kind==="chests"?"Found in chests: "+what:kind==="gameplay"?"Gameplay loot: "+what:"Loot table: "+p.replace(/[_/]/g," "))+" ("+ns+")"};
function gTimeline(g){const r=gMain(g),w=g.ps?"a":"w";let acts=ORDER.filter(x=>x!=-1&&oiA(x)>=oiA(g.a)),out=null;
 {const ts=acts.map(x=>gTierOf(g,x,r,w)),k=ts.findIndex((t,i)=>i>0&&(!t||t==="D"));if(k>0){out=acts[k];acts=acts.slice(0,k)}}
 const tail=out!=null?`<span class="gout" title="From ${esc(actL(out))} on it is D tier or below: replace it.">Outclassed from ${esc(ACT[out][0])}</span>`:"";
 const mg=g.mg?`<p class="note">Needs ${ilink(g.mg[1])}, which the pack only opens at ${esc(actL(g.mg[0]))}, so it is listed from there.</p>`:"";
 return mg+`<div class="gtime">${acts.map(x=>{const t=gTierOf(g,x,r,w);const i=GTIER.findIndex(z=>z[0]===t);return `<a href="#gear/${x}/${r}/${w}" style="--tc:${ACT[x][2]};--gc:${i>=0?GTIER[i][2]:"#555"}" title="${esc(actL(x))}: ${t||"below D"} for ${GROLE[r]}"><b>${t||"–"}</b><small>${esc(ACT[x][0])}</small></a>`}).join("")}${tail}</div>`}
function gVerdict(g){const r=gMain(g),w=g.ps?"a":"w",acts=ORDER.filter(x=>x!=-1&&oiA(x)>=oiA(g.a)),ts=acts.map(x=>gTierOf(g,x,r,w));
 const rank=t=>t?GTIER.findIndex(z=>z[0]===t):9,best=Math.min(...ts.map(rank));if(best>=9)return "";
 const on=acts.filter((x,i)=>rank(ts[i])===best),k=ts.findIndex((t,i)=>i>0&&(!t||t==="D")),bt=GTIER[best];
 const span=on.length>1?`Acts ${esc(ACT[on[0]][0])}–${esc(ACT[on[on.length-1]][0])}`:`Act ${esc(ACT[on[0]][0])}`;
 return `<p class="gverd" style="--gc:${bt[2]}"><b>${bt[0]}</b><span><strong>${best<=1?"Worth using":best<=2?"Usable":"Weak"}</strong> as ${GROLE[r]} gear: ${bt[0]} tier at ${span}.${k>0?` Replace it by Act ${esc(ACT[acts[k]][0])}.`:""}</span></p>`}
/* gear pages use the shared article layout (app.js): sections, infobox, "On this page", navbox */
const gStatTable=(g,rows)=>rows.length?`${gKinds(g)}<table class="gst">${rows.map(([ic,n,v])=>`<tr><td>${ic?`<i class="ai" style="--ai:var(--v-${ic})"></i>`:""}${n}</td><td class="num">${v}</td></tr>`).join("")}${g.sc.ME!=null&&g.dmg!=null?`<tr class="dps"><td>Damage per second <span class="kest">estimate</span></td><td class="num">${gRound(g.sc.ME)}</td></tr>`:""}</table>`:`<p class="note">Base ${g.k==="armor"?"armor":"damage"} is computed in this mod's code at run time; the wiki could not read it, so this item is ranked by its gate.</p>`;
/* the best tier of a playstyle at an Act, for the navbox */
const gTop=(a,r,w,not)=>{const t=gTiers(a,r,w)[0];return t?t[1].filter(x=>x!==not).slice(0,10).map(x=>[gHref(x),esc(x.n)]):[]};
const gArtBox=(g,set)=>`<div class="ip-art${!g.ps&&g.k!=="armor"?" wpn":""}"><div class="ip-stage" style="${tex(g.a)}">${envFx(g.a)}<div class="ip-icon${set&&typeof ARMR!=="undefined"&&ARMR[set.k]?"":" framed"}">${set&&typeof ARMR!=="undefined"&&ARMR[set.k]?`<img class="garm" alt="${esc(set.n)} worn" src="${ARMR[set.k]}">`:`<span class="gbig">${img(g.ps?gIcon(g).id:g.id)}</span>`}</div></div></div>`;
function gearItemPage(g){document.title=g.n+" · Linggango Wiki";seedBg("g"+g.ix,[]);
 const r=gMain(g),rows=gStats(g),bon=gBonus(g),set=g.k==="armor"?GS.find(s=>s.p.includes(g.id)):null,w=set?"a":"w",mod=MODN(g.ns);
 el("main").innerHTML=article({cls:"r0 gearart",style:`--tc:${ACT[g.a][2]};${tex(g.a)}`,crumb:crumb('<a href="#gear">Equipment</a>',esc(g.n)),title:esc(g.n),
  lead:`${esc(GKIND[g.k])}${g.sl?` for the ${esc(GSLOT[g.sl].toLowerCase())}`:""} from ${esc(mod)}, usable from ${esc(actL(g.a))}${g.ga?` once ${esc(GATEN[g.ga])} falls`:""}.`,
  head:gVerdict(set||g),
  secs:[["get","How to get",`${g.ob?`<p class="gob${g.ob[0]==="!"?" bad":g.ob[0]==="?"?" unk":""}">${esc(g.ob.replace(/^[!?]/,""))}</p>`:""}${gSrcText(g)}`],
   ["stats","Stats",gStatTable(g,rows)+(bon.length?`<h3>Bonuses</h3><ul class="gbon attr">${bon.map(x=>`<li>${statLine(x)}</li>`).join("")}</ul><p class="note">From the mod's own modifiers, the Linggango <i>attributesetter</i> rebalance and the pack's runtime tweaks (linggango_tweaks: per-mod damage buffs and the tier damage floor), added on top of the base stats.</p>`:"")],
   (h=>h&&["fx","Effects",h])(gFxHtml(g)),
   ["tier","Tier by Act",set?`<p class="note">The ${esc(set.n)} set as ${GROLE[gMain(set)]} armor, compared with every set usable at each Act.</p>${gTimeline(set)}<h3>Set</h3><a class="gsetl" href="#gs${set.ix}" data-t="s${set.ix}">${gImg(set)}<span>${esc(set.n)} · ${set.ps.length} piece${set.ps.length>1?"s":""}</span></a>`:`<p class="note">${GROLE[r]} weapons, compared with everything usable at each Act.</p>${gTimeline(g)}`],
   typeof GUIDE!=="undefined"&&GUIDE[g.id]&&["guide","From the guide book",guideHtml(GUIDE[g.id])],
   g.lv&&g.lv.length&&["forms","Other levels and forms",`<p class="note">This page shows the strongest version. The same weapon also exists as: ${g.lv.map(x=>`<code>${esc(x)}</code>`).join(", ")}.</p>`]],
  art:gArtBox(g,set),
  box:{head:`<span class="ip-slot">${img(g.id)}</span><div><b>${esc(g.n)}</b><span>${esc(mod)}</span></div>`,
   rows:[["Type",esc(GKIND[g.k])],g.sl&&["Slot",esc(GSLOT[g.sl])],["Mod",`<a href="#mod/${enc(mod)}">${esc(mod)}</a>`],["Act",`<a href="#gear/${g.a}/${r}/${w}">${esc(actL(g.a))}</a>`],g.ga&&["Locked until",esc(GATEN[g.ga]),"Linggango progression tag"],["Playstyle",esc(GROLE[set?gMain(set):r])],set&&["Set",`<a href="#gs${set.ix}" data-t="s${set.ix}">${esc(set.n)}</a>`]],
   foot:idBox(g.id)},
  nav:wikiNav({act:g.a},[set&&["Set pieces",set.ps.map(p=>["#g"+p.ix,esc(p.n),p===g])],[`Best ${esc(GROLE[set?gMain(set):r])} ${set?"sets":"weapons"} at ${esc(actL(g.a))}`,gTop(g.a,set?gMain(set):r,w,set||g)]])});
 wireArticle();decorate()}
/* "Effects" section: what the item does on hit, worn, held or used (read from its code), then its own tooltip lines */
const GWHEN={hit:"On hit",worn:"While worn",carried:"While held or carried",use:"On use",release:"When you release the shot"};
const gRom=n=>["","I","II","III","IV","V","VI","VII","VIII","IX","X"][n]||String(n);
function gFxLine(r){const who=r.who==="target"?"the target":"you",ch=r.chance&&r.chance<1?` (${Math.round(r.chance*100)}% chance)`:"";
 if(r.fire)return `Sets ${who} on fire for ${r.fire} s${ch}`;if(r.heal)return `Heals you ${gRound(r.heal)} health${ch}`;
 const t=r.ticks>0?` for ${gRound(r.ticks/20)} s`:"";return `${esc(r.name||r.effect)} ${gRom(r.level||1)} on ${who}${t}${ch}${r.maybe?" (one of these, by the armor's material)":""}`}
function gFxHtml(g){const fx=g.fx||[],tip=g.tip||[];if(!fx.length&&!tip.length)return "";
 const by={};fx.forEach(r=>(by[r.when]=by[r.when]||[]).push(r));
 const scored=gFxOn(g,["hit"],"target").some(r=>r.fire||GDOT[r.effect]||r.effect==="minecraft:instant_damage")||Object.keys(gFxAt(g)).length;
 return `${Object.keys(by).length?`<table class="gst gfx">${Object.entries(by).map(([w,rs])=>`<tr><td>${GWHEN[w]||esc(w)}</td><td>${rs.map(gFxLine).join("<br>")}</td></tr>`).join("")}</table>
<p class="note">Read from the item's code${g.fx&&g.fx.some(r=>r.src)?" (each piece's own effect while worn)":""}. ${scored?"Poison, wither, fire, instant damage, Strength, Resistance and Health Boost are counted in its score. ":""}Effects a mod adds are listed, not scored, and set bonuses written elsewhere in a mod may be missing.</p>`:""}${tip.length?`<h3>From its tooltip</h3><ul class="gbon">${tip.map(x=>`<li>${esc(x)}</li>`).join("")}</ul>`:""}`}
function gearSetPage(s){document.title=s.n+" set · Linggango Wiki";seedBg("gs"+s.ix,[]);const r=gMain(s),mod=MODN(s.k.split(":")[0]);
 el("main").innerHTML=article({cls:"r0 gearart",style:`--tc:${ACT[s.a][2]};${tex(s.a)}`,crumb:crumb('<a href="#gear/'+GSTATE.a+'/'+r+'/a">Equipment</a>',esc(s.n)),title:esc(s.n)+" set",
  lead:`${s.ps.length}-piece armor set from ${esc(mod)}, usable from ${esc(actL(s.a))}.`,head:gVerdict(s),
  secs:[["set","Full set",`<table class="gst">${s.kn?`<tr><td><i class="ai" style="--ai:var(--v-gui_armor)"></i>Armor</td><td class="num">${gRound(s.arm)}</td></tr><tr><td><i class="ai" style="--ai:var(--v-fx_resistance)"></i>Toughness</td><td class="num">${gRound(s.tough)}</td></tr>`:`<tr><td colspan="2" class="note">Base armor is computed in code the wiki could not read.</td></tr>`}${s.hp?`<tr><td><i class="ai" style="--ai:var(--v-gui_heart)"></i>Max Health</td><td class="num">${s.hp>0?"+":""}${gRound(s.hp)}</td></tr>`:""}${s.kbr?`<tr><td>Knockback Resistance</td><td class="num">${gRound(s.kbr)}</td></tr>`:""}${s.dtk?`<tr><td>Damage taken</td><td class="num">${s.dtk>0?"−":"+"}${gRound(Math.abs(s.dtk)*100)}%</td></tr>`:""}</table>`],
   (h=>h&&["fx","Effects",h])(gFxHtml({fx:s.fx,tip:[]})),
   ["pieces","Pieces",`<div class="gpcs">${s.ps.map(p=>`<a href="#g${p.ix}" data-t="g${p.ix}">${img(p.id)}<span>${esc(p.n)}</span><small>${p.arm!=null?gRound(p.arm)+" armor":""}${gBonus(p).length?" · "+gBonus(p).slice(0,2).join(", "):""}</small></a>`).join("")}</div>`],
   ["tier","Tier by Act",`<p class="note">As a ${GROLE[r]} set.</p>${gTimeline(s)}<p class="note">${gRoles(s).length?`Its bonuses raise ${gRoles(s).map(k=>GROLE[k]).join(", ")} output; `:"It has no playstyle bonus, so it is ranked on how long it keeps you alive; "}every set is also in each other playstyle's list, scored on its defense and whatever bonus it has for that playstyle.</p>`]],
  art:gArtBox(s,s),
  box:{head:`<span class="ip-slot">${gImg(s)}</span><div><b>${esc(s.n)} set</b><span>${esc(mod)}</span></div>`,
   rows:[["Pieces",String(s.ps.length)],["Mod",`<a href="#mod/${enc(mod)}">${esc(mod)}</a>`],["Act",`<a href="#gear/${s.a}/${r}/a">${esc(actL(s.a))}</a>`],s.kn&&["Armor",String(gRound(s.arm))],s.kn&&["Toughness",String(gRound(s.tough))],s.hp&&["Max Health",(s.hp>0?"+":"")+gRound(s.hp)],["Playstyle",esc(GROLE[r])]]},
  nav:wikiNav({act:s.a},[["Pieces",s.ps.map(p=>["#g"+p.ix,esc(p.n)])],[`Best ${esc(GROLE[r])} sets at ${esc(actL(s.a))}`,gTop(s.a,r,"a",s)]])});
 wireArticle();decorate()}
const GATEN={2:"Iron Colossus",3:"the Goblin Lord",4:"Arion",5:"Eldorath",6:"Zoranth the Forgotten",7:"the Elvenite Paladin",8:"Vaedric",10:"Sanghor",11:"Zoranth Newborn"};
const MODN=ns=>(MODS.find(([m,xs])=>xs.some(d=>d.id.startsWith(ns+":")))||[GNS[ns]||ns.replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase())])[0];
/* tooltip for gear tiles: same frame as the relic tooltip */
function gearTip(n){const k=n.dataset.t,isSet=k[0]==="s",g=isSet?GS[+k.slice(1)]:GE[+k.slice(1)];if(!g)return;tipFor=n;
 const P=GTIER.map(x=>x[2]),c=ACT[g.a][2];tip.className="to gtip"+(tip.classList.contains("on")?" on":"");delete tip.dataset.mf;
 tip.style.setProperty("--c1",c);tip.style.setProperty("--c2",c+"aa");tip.style.setProperty("--c3","#1a1420");
 const rows=isSet?(g.kn?[`${gRound(g.arm)} Armor`,`${gRound(g.tough)} Armor Toughness`]:[]).concat(g.hp?[`+${gRound(g.hp)} Max Health`]:[]):gStats(g).map(([,n,v])=>`${v} ${n}`);
 const bon=isSet?Object.keys(GROLE).map(r=>[r,gOff(g,r,g.a)-1]).filter(x=>x[1]>.005).map(([r,v])=>`+${Math.round(v*100)}% ${GROLE[r]} output`):gBonus(g).slice(0,6);
 tip.innerHTML=`<div class="tbox"><div class="tfr"></div><div class="thd"><span class="tslot"><span class="aimg">${gImg(g)}</span></span><div class="tht"><div class="tnm">${esc(g.n)}${isSet?" set":""}</div><div class="tsub">${isSet?g.ps.length+(g.ps.length>1?" pieces":" piece"):esc(GKIND[g.k])+(g.sl?" · "+GSLOT[g.sl]:"")}</div></div></div>
 <div class="tbd">${rows.length?`<ul class="tst">${rows.map(x=>`<li>${fmt(x)}</li>`).join("")}</ul>`:""}${bon.length?`<ul class="tst">${bon.map(x=>`<li>${fmt(x)}</li>`).join("")}</ul>`:""}${g.est?'<p class="tsrc">≈ ranked by when you get it (base stats not readable)</p>':""}${g.ga?`<p class="tlock">${ui("lock")} Locked until ${esc(GATEN[g.ga])} falls</p>`:""}<p class="twhere">${esc(actL(g.a))}</p></div>
 <div class="tft"><span class="tmod">${esc(MODN((g.id||g.k).split(":")[0]))}</span><span class="trt">${gRoles(g).map(r=>GROLE[r]).join(" · ")}</span></div></div>`;
 if(lastAct)lastAct.classList.remove("act");lastAct=null;const first=!tip.classList.contains("on");place(n);tip.classList.add("on");if(first)tip.classList.add("in")}
/* ---------- hooks into the wiki's router, tooltip and pages (app.js EXT) ---------- */
EXT.route.push(h=>{if(h!==GLASTH){GALL=false;GLASTH=h}
  const mine=h.startsWith("#gear")||/^#gs?\d+$/.test(h);document.body.classList.toggle("gearv",mine);
  if(!mine)return false;
  save();refreshSide();document.body.classList.remove("hub");const mn=el("main");mn.classList.remove("enter");void mn.offsetWidth;mn.classList.add("enter");
  if(h.startsWith("#gear"))gearPage(h);else if(h.startsWith("#gs")&&GS[+h.slice(3)])gearSetPage(GS[+h.slice(3)]);else if(GE[+h.slice(2)])gearItemPage(GE[+h.slice(2)]);else gearPage("#gear");scrollTo(0,0);return true});
EXT.tip.push(n=>{const k=n.dataset.t;if(k&&/^[gs]\d/.test(k)){gearTip(n);return true}return false});
