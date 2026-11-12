/* pixel icons for the UI (lock, star, check, attack types, armor slots, sources): sprites from uiicons.js / scenes.js, never emoji.
   ui(k) is 16 px for running text; ui(k,1) is the 16 px sprite at x2 for icon boxes. */
const UIK={star:"rt-ui_star",lock:"rt-lg_lock",check:"rt-lg_check",q:"rt-ftb_info",spy:"rt-spyglass",sword:"rt-ui_sword",bow:"rt-ui_bow",aoe:"rt-ui_fire_charge",
 summon:"rt-ui_bone",move:"rt-ui_feather",buff:"rt-ui_glowstone",helmet:"rt-ui_helmet",chest:"rt-ui_chestplate",legs:"rt-ui_leggings",boots:"rt-ui_boots"};
/* a curio's effect line in the reader's language (the English stays in the data: scores, search and the effect hints read it) */
const fxT=d=>TD(d.fx);
function ui(k,big){return `<i class="ui${big?" ui2":""}" style="--ui:var(--${UIK[k]})" aria-hidden="true"></i>`}
/* show any script error on the page itself, so a screenshot tells us what broke */
{const box=()=>{let b=document.getElementById("jserr");if(!b){b=document.createElement("div");b.id="jserr";b.onclick=()=>b.remove();document.body.appendChild(b)}return b};
 const show=m=>{try{const b=box();b.textContent="Wiki error (click to hide): "+m}catch(e){}};
 // "ResizeObserver loop completed with undelivered notifications" is the browser saying a resize callback changed the layout again in the same frame (a room painted after
 // a longer translated text wrapped); the next frame delivers it and nothing is lost, so it is not shown as a wiki error
 addEventListener("error",e=>{if(/^ResizeObserver loop/.test(e.message))return;show(`${e.message} @ ${String(e.filename||"").split("/").pop()}:${e.lineno}`)});
 addEventListener("unhandledrejection",e=>show(String(e.reason&&e.reason.stack||e.reason).slice(0,300)))}
/* pixel art at whole device pixels: 16px textures drawn at an integer multiple of the screen's pixels (Windows 125%/150% scaling) */
{const fit=()=>{const r=devicePixelRatio||1,k=n=>Math.max(1,Math.round(n*r/16))*16/r;document.documentElement.style.setProperty("--ip",k(32)+"px");document.documentElement.style.setProperty("--ip2",k(48)+"px")};
 fit();addEventListener("resize",fit)}
/* ---------- build planner, boss guides, pack mechanics, recipe trees ---------- */
// Player curio slots: merged curios/slots data from the base pack jars (Scroll, Spellstone, Focus are registered in code: assumed 1)
var SLOT_BASE={Head:1,Necklace:2,Back:1,Body:1,Belt:1,Hands:2,Ring:2,Bracelet:2,Glove:2,Anklet:2,Feet:2,Charm:6,Accessory:6,Heart:1,Spellbook:1,Scroll:1,Spellstone:1,Talent:2,Focus:1,"Hostility Curse":1,Curio:1,Elytra:1,"Binding Key":1,Magnetizer:1,Bundle:1};
var SLOT_KEYS=Object.keys(SLOT_BASE); // share-link slot code = base-36 position here: append only
var STAT_ALIAS={"Knockback Res":"Knockback Resistance","Knockback resistance":"Knockback Resistance","Increased reach":"Reach","Increased block reach":"Block Reach","Step Height Addition":"Step Height"};
var BS={p:12,s:{},c:[]},BPICK=null,BINSP=null,BSTALE=false,BLOST=0;
// home boons: permanent consumables from linggango_tweaks; icons are the mod's own PNGs
const HOME_BOONS=[
 {id:"linggango_tweaks:hearty_feast",n:"Hearty Feast",st:"+2 max health"},
 {id:"linggango_tweaks:anglers_pearl",n:"Angler's Pearl",st:"+3% move speed, +10% swim speed"},
 {id:"linggango_tweaks:amber_core",n:"Amber Core",st:"+6% mining speed, +0.2 block reach"},
 {id:"linggango_tweaks:hunters_essence",n:"Hunter's Essence",st:"+1% damage for every class"},
 {id:"linggango_tweaks:arcane_crystal",n:"Arcane Crystal",st:"+10 max mana, +1% spell power"}];
Object.assign(IC,{"linggango_tweaks:hearty_feast":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABVUlEQVR4nGNgoBf46u/x/+/0qf9h7A1KimA2EymG/NixGax59+WbDCd//QSLMZJiAMxWkOb2J89I0gsHlTJSYENggJEBDRQ4qqIoQAYT9t/GUM+CrtnfUYlBw0YWzF8+4xRDZIYZXP71559gw5eeeQQ3iAmbZr4NixhetGxmOPDjA8PKw5fA8mwrVzL0dLkxGCsJMDgoCsFdyYTuJJBmNg0OhmVS3AypnmwM4bZ6DHcb1jNcv87G8HnmBhQXoXjhwoO3DBbPhBlee0YyCLL8YrD8dpPh5NWvDDyvHzNoNASCXQACv/CFweYzz8C0L9s5BsuAOAYj1d9g/sFVVxgYGLXB7BPNB1EMYETmgPxmoyHGoCMvAOZbeKozXD10l+Hm408Mj15/h7v0wP13jFhdwMDAwHD/9TeGLz/+gtlXHp4E00duvEJXht0FMFfgVM3AgGL74AAAZuqBC6mZJfoAAAAASUVORK5CYII=","linggango_tweaks:anglers_pearl":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABzUlEQVR4nGNgoBAwYhO0jKj+j038+IpWDPUs6AJO8W3/rW0NGeQVJBnMtBXBYqu3HmN4/PgNwzOz2P8PTy1GMYQR3WZjUyOGAE9zhtycNrCYpKwMw/PHT8A0CNy9fp0B2RAWdBdMKgxk0HbJAbMVVVUYfvz4wSAgJsjw/edXBk52bgxvsSDbHhXpBdYM0iDILwwWl1OQBdOvXrxmuH/7DoOOuSXD7x8//j+7tBrsCiYGPEBJTZ6Bh4+L4eu3HwzcfLxgMS4OVga8YaCursFw8+YNBiFRaYZSrcdg8an3lMA0NxcHw/7tu1DCgAndVpCNMrIKDD1+TAx26a0MfCJCDNlK9xiePH7AQBTwzp32/8KWGf///fsHxu9eXPt/YHrl/70TS/7Lm8VixA8mdC8Y6SsyMHHyMVzZvwIs9ujMITDNzAbxu6ZT1n+sBlhGVP9vrstkeP/xG8PrK+cY/n3/xHBp2yywnICsPMPfX78ZJk5uZNAxNmSQ0gv9jzUdzJy/ncHURI3hLIMvw6ObbxgCWY6Dxdf/sWRgYBBlONs/Fxw+yAAlFkAmG1haMhibajLYW+miKOybuApMXzh+nAGWBjAMgBmCPXghAFkzVQAAHGSfhgW9wd8AAAAASUVORK5CYII=","linggango_tweaks:amber_core":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABf0lEQVR4nGNgoBAw4pIIcTT6j8xfs/8cVrUsuDQnZjvB+ecPXWNgYDD6j80QFmyaC+r8GVbN2A3m77/wHEyHu6tjNYQRXXNQkCHDtYtPGbT0pcFiIPb3Hz/AbEkpfoYTpx+jeIcFXbOcjhyYz7dzH5hmfcLEsI+BFcwOkuJnsDCVBTHhLmFC98KjK4/A9I+fjAxq2UoM5gZMDO4MvxksdSTAtoPAzWcfMcPg5rOPDM8ev2G4dectg+2rZwzyPlIM8q7ZDAwMUxl4xJ4w7N31mMHADhQOeALxxOnHDEKCXAyvmVgYBI88Zbgo1skgIMnD8OL8b4ZXjEwMLy+/wDCAEZmjq678X12Kn+HZ+28MOkoiDH6/noLFb2jpgQ030JVgWLnzJsPlm3cxAxEEeDkhgSUlyMXw7v03hk2CkJh4B3UZSDNMDVYDPn//zbDmwjlGkEtAfHXkAHv2EWwzTA4GmFCMgwJkJ1pqS2KIEQ1AtlkZaKDYiA6wugAZgLxFUwAAX6aQiziBywcAAAAASUVORK5CYII=","linggango_tweaks:hunters_essence":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAA1UlEQVR4nGNgGGjAiEuiO8niP4x988UXhjnbrmBVy4TPdHMlMbDmNx++kue80hD9/wFWinCXkOSF2OKJ/3l5ecDs40dOMpzfM4t0L7Tl+jCIiYngdSUTA4WAiYEWwDut4/+ukzf+f3j78v+f0OD/DdM2/jfxL/1PkguceqoZeFetYTh08QXD9+YmnJYx4ZKoPvKA4f++fQxLP34hPwzuP8CvGacBL1++ZXDn5WCY8+QNgwgTC0OrjQLD368fsRqAMyGBAu0E2z0w2+KXEsOZjd041VIEAIeSSz/apQ37AAAAAElFTkSuQmCC","linggango_tweaks:arcane_crystal":"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABOklEQVR4nGNgoCWwVqz5D8Jka16a/vb/opS3/+X4o3AawohLc5ZbIcP1B/cYvv/8DhbbcGEew90PCzDUM6ELOKr0/HdU8wezG6MZGNQV1cFsdREbBmwuYUEXYGVkB2tkYLiHIq4rp8lw5d0OBoIusNN2hLP/RsqgyOlJOGO4ggnd74rikiiaOZhZGIzUtRlYWdkYeNkkGAh6AQRWHFViiIB64f4LNjD97ONbMM3KCOHj9AII3H/5nKF9HScDDNx4gggPbnZBBpwGPP54A0w/f/0c7hKYZil+YQZlcdQwwTAAZjsI3Hhyh4Hx9x8GZhZGFI1CvKIMOA149G4NPKF8/PqJYfnxnQwKwtJweU0FJRTNGAaAwIKjLRiKQEBPV46hZUkjw4E7VSipEWtSVhGNwJr277xegVU9RQAAnn9fmuI9iZ8AAAAASUVORK5CYII="});
const togBtn=(h,on,dtk)=>`<button class="btog${on?" on":""}" data-${dtk}="${esc(h.id)}" aria-pressed="${on}" title="${esc(TD(h.n))}: ${esc(h.st)}" aria-label="${esc(TD(h.n))}">${img(h.icon||h.id)}</button>`;
function consRow(){return `<div class="bslot bcons${BS.c.length?" has":""}"><div class="bsh"><b>${T("Consumables")}</b><span>${T("permanent · not in totals")}</span></div><div class="bsb">${HOME_BOONS.map(h=>togBtn(h,BS.c.includes(h.id),"cons")).join("")}</div></div>`}

function slotAdds(d){
 if(d._sa)return d._sa;const o={};
 const put=(n,s)=>{s=s.toLowerCase().replace(/s$/,"");const k=Object.keys(SLOT_BASE).find(x=>x.toLowerCase()===s);if(k&&+n>0)o[k]=Math.max(o[k]||0,+n)};
 for(const t of [...d.st,d.fx]){let m;
  for(const r of [/grants (\d+) (\w+) slots?/gi,/\+(\d+)(?:[–-]\d+)? (\w+) slots?/gi,/\+(\d+) slot (\w+)/gi])while((m=r.exec(t)))put(m[1],m[2]);
  const r=/bonus (\w+) slots: (\d+)/gi;while((m=r.exec(t)))put(m[2],m[1])}
 return d._sa=o}
function statsOf(d){
 if(d._stp)return d._stp;const out=[];
 for(const x of d.st){const m=x.trim().match(/^([+-])\s*(\d+(?:\.\d+)?)\s*(%?)\s+(?:to\s+)?([A-Z][A-Za-z' ]{2,40}?)\s*(?:\(.*\))?\.?$/);
  // conditional lines ("Damage dealt to enemies on fire", "Attack Damage per stored soul") are effects, not totals
  if(!m||/slots?$/i.test(m[4])||/\b(to|against|for each|per|when|while)\b/i.test(m[4]))continue;let k=STAT_ALIAS[m[4]]||m[4],v=(m[1]==="-"?-1:1)*+m[2];
  if(/^Hearts?$/.test(k)){k="Max Health";v*=2}
  out.push({k:k+(m[3]?" %":""),v})}
 return d._stp=out}
// the generic Curio slot takes any accessory; items tagged only "Curio" still fit nowhere else
function bFits(d,k){return d.sl.includes(k)||(k==="Curio"&&d.sl.length>0)}
function bAvail(d){return ORDER.indexOf(d.t)<=ORDER.indexOf(BS.p)}
// a copy past the first adds its stats/slots only when the scan says the bonus is slot-tied
function bStk(id){const k=SK.i[id];return !!k&&(k.s==="y"||k.w.includes("s"))}
function bCounted(){const seen=new Set();return Object.values(BS.s).flat().filter(id=>seen.has(id)?bStk(id):seen.add(id))}
// per-copy relic state key: the second Leather Belt is "<id>#2"
const rlId=k=>k.split("#")[0],bKey=(n,id)=>(n[id]=(n[id]||0)+1)>1?id+"#"+n[id]:id;
function bKeys(){const n={};return Object.values(BS.s).flat().map(id=>bKey(n,id))}
function bCaps(){const c={...SLOT_BASE};bKeys().filter(k=>k===rlId(k)||bStk(rlId(k))).forEach(k=>{const id=rlId(k),a=RL[id]?rlSlots(k):slotAdds(BYID[id]);for(const s in a)c[s]+=a[s]});return c}
function bParse(h){
 const [,p,f,b]=decodeURIComponent(h).split("/"),v=f!==undefined&&!f.includes("="),c=v?b:f;BSTALE=v&&f!==DFP;BLOST=0;BS={p:p!==undefined&&p!==""&&ACT[p]&&ORDER.includes(+p)?+p:ORDER[ORDER.length-1],s:{},c:[]};
 const n={};(c||"").split("|").filter(Boolean).forEach(part=>{if(part[0]==="*"){const xs=part.slice(1).split(",").filter(Boolean);BS.c=xs.map(x=>HOME_BOONS[parseInt(x,36)]?.id).filter(Boolean);BLOST+=xs.length-BS.c.length;return}const [k,ids]=part.includes("=")?part.split("="):[SLOT_KEYS[parseInt(part[0],36)],part.slice(1)],xs=(ids||"").split(",").filter(Boolean);
  // an unknown slot code, an index past the list or a curio that does not fit its slot is dropped, and counted for the note
  if(!(k in SLOT_BASE)){BLOST+=xs.length||1;return}BS.s[k]=xs.map(x=>bLv(x,n)).filter(i=>BYID[i]&&bFits(BYID[i],k));BLOST+=xs.length-BS.s[k].length})}
// "index_" + level, ability points, then per-stat stars, all base 36 ("-" any roll); older "id~level~a.b.c~stars" still reads
function bLv(x,n){
 if(x.includes("_")&&!x.includes(":")){const [t,d]=x.split("_"),id=(D[parseInt(t,36)]||{}).id||"",r=RL[id];
  if(r){const ch=[...d],na=r.ab.length;RLV[bKey(n,id)]=rlFit(r,Math.max(0,Math.min(r.mx,parseInt(ch[0],36)||0)),ch.slice(1,1+na).map(c=>parseInt(c,36)),ch.slice(1+na).map(c=>c==="-"?-1:parseInt(c,36)))}
  return id}
 let [id,l,a,q]=x.split("~");if(!id.includes(":"))id=(D[parseInt(id,36)]||{}).id||"";const r=RL[id];if(r&&l!==undefined){RLV[bKey(n,id)]=rlFit(r,Math.max(0,Math.min(r.mx,+l||0)),(a||"").split(".").map(Number),[...(q||"")].map(c=>c==="-"?-1:parseInt(c,11)))}return id}
function bHash(){const n={};return "#build/"+BS.p+"/"+DFP+"/"+Object.entries(BS.s).filter(([,v])=>v.length).map(([k,v])=>SLOT_KEYS.indexOf(k).toString(36)+v.map(id=>{const t=BYID[id].ix.toString(36);if(!RL[id])return t;const s=rlState(bKey(n,id));return t+"_"+[s.l,...s.a,...(s.q.some(v=>v>=0)?s.q:[])].map(v=>v<0?"-":v.toString(36)).join("")}).join(",")).join("|")+(BS.c.length?"|*"+BS.c.map(id=>HOME_BOONS.findIndex(h=>h.id===id).toString(36)).join(","):"")}
// a redraw of #main keeps the keyboard position: the same control (by id, data-* key or link) gets focus back, or pref() picks one
function focusKey(){const a=document.activeElement,m=el("main");if(!a||a===document.body||!m||!m.contains(a)||!a.matches(":focus-visible"))return null;
 const sc=a.closest(".bslots,.bpick,.binsp,.bpane,.bbar"),pre=sc?"."+sc.classList[0]+" ":"";
 if(a.id)return ["#"+CSS.escape(a.id)];
 for(const k of ["data-pick","data-rm","data-add","data-preset","data-insp","data-cons","data-evo","data-pgi","data-tab"])if(a.hasAttribute(k)){const q=`[${k}="${CSS.escape(a.getAttribute(k))}"]`;return [pre+q,q]}
 return a.matches("a[href]")?[`a[href="${CSS.escape(a.getAttribute("href"))}"]`]:null}
function keepFocus(fn,pref){const k=focusKey();fn();if(!k)return;const m=el("main"),t=(pref&&pref(m))||k.map(q=>m.querySelector(q)).find(Boolean);if(t&&document.activeElement!==t)t.focus({preventScroll:true})}
function bSave(pref){history.replaceState(null,"",bHash());keepFocus(buildPage,pref)}
function bPreset(role){
 BS.s={};const pool=D.filter(d=>bAvail(d)&&!d.inv);
 const score=d=>(isMust(d)?1e6:0)+(d.ro.includes(role)?1e3:0)+d.r*10+(+d.sc||0);
 const order=pool.sort((a,b)=>score(b)-score(a)),used=new Set();
 for(const pass of [0,1]){const caps=bCaps();
  for(const d of order){if(used.has(d.id))continue;const adds=slotAdds(d),n=Object.keys(adds).length;
   if(pass===0&&!n)continue;if(pass===1&&!d.ro.includes(role)&&!isMust(d))continue;
   const k=d.sl.find(s=>s in caps&&caps[s]>(BS.s[s]||[]).length);if(!k)continue;
   (BS.s[k]=BS.s[k]||[]).push(d.id);used.add(d.id);for(const x in adds)caps[x]+=adds[x]}}
 bSave()}
function bOpts(k,q){
 const eq=new Set(Object.values(BS.s).flat());q=(q||"").toLowerCase();
 return D.filter(d=>bFits(d,k)&&bAvail(d)&&!(eq.has(d.id)&&SK.i[d.id]?.s==="u")&&(!q||d.n.toLowerCase().includes(q)||d.fx.toLowerCase().includes(q)||d.m.toLowerCase().includes(q)))
  .sort((a,b)=>(isMust(b)-isMust(a))||(b.r-a.r)||((+b.sc||0)-(+a.sc||0))).slice(0,150)}
function bWorn(id){return Object.values(BS.s).flat().filter(x=>x===id).length}
// fade the list's top/bottom edge while there is more to scroll that way
function bFade(){const o=el("bopts");if(!o)return;o.classList.toggle("mt",o.scrollTop>2);o.classList.toggle("mb",o.scrollTop+o.clientHeight<o.scrollHeight-2)}
function bPickHtml(){
 if(!BPICK)return"";const xs=bOpts(BPICK,el("bq")?el("bq").value:"");
 return xs.map(d=>`<div class="bopt r${d.r}${BINSP===d.id?" sel":""}"><button class="bopi" data-insp="${esc(d.id)}" data-t="${d.ix}" title="${T("Show recipe and details")}">${img(d.id)}<span><b>${esc(TD(d.n))}</b><small>${esc(actL(d.t))} · ${isMust(d)?ui("star")+"Must-Have":RN[d.r]} · ${esc(d.m)}${bWorn(d.id)?` · <b>${T("worn ×{n}",{n:bWorn(d.id)})}</b>`:""}</small>${SK.i[d.id]?`<small>${skTag(d.id)}</small>`:""}<small class="bofx">${esc(fxT(d))}</small></span></button><button class="chip" data-add="${esc(BPICK)}|${esc(d.id)}" aria-label="${esc(T("Add {name}",{name:TD(d.n)}))}">${T("Add")}</button></div>`).join("")||`<p class="note">${el("bq")&&el("bq").value?T("Nothing for this slot on this act matches the search."):T("Nothing for this slot on this act.")}</p>`}
function bInspHtml(){
 const d=BINSP&&BYID[BINSP];if(!d)return"";const k0=Object.keys(BS.s).find(k=>BS.s[k].includes(d.id)),caps=bCaps();
 const adds=k0&&SK.i[d.id]?.s==="u"?"":Object.keys(SLOT_BASE).filter(k=>bFits(d,k)).map(k=>`<button class="chip" data-add="${esc(k)}|${esc(d.id)}"${(BS.s[k]||[]).length>=caps[k]?` title="${esc(T("{slot} is full",{slot:T(k)}))}"`:""}>${T("Add to {slot}",{slot:esc(T(k))})}</button>`).join("");
 const tree=rtreeHtml(d,true),how=d.gr?"":(d.src||[]).slice(0,3).map(s=>`<li>${fmt(s)}</li>`).join("");
 return `<div class="binsp"><div class="bph"><b class="bih">${img(d.id)}<span>${esc(TD(d.n))}<small>${esc(d.sl.map(x=>T(x)).join(", "))} · ${esc(actL(d.t))} · ${esc(d.m)}</small></span></b><button class="ghost" data-insp="">${T("Close")}</button></div>
<p class="bifx">${fmt(fxT(d))}</p>${SK.i[d.id]?`<p class="bisk">${skTag(d.id)} <a href="#i${d.ix}">${T("why?")}</a></p>`:""}${d.gr?tipRecipe(d).replace(/,18px\)/,",30px)"):""}${tree?`<h3>${T("Recipe tree")}</h3><ul class="rtree">${tree}</ul><p class="note">${T("Click an ingredient to open its recipe here.")}</p>`:how?`<h3>${T("How to get it")}</h3><ul class="bihow">${how}</ul>`:""}
<p class="biact">${k0?`<button class="chip" data-rm="${esc(k0)}|${esc(d.id)}">${T("Remove from {slot}",{slot:esc(T(k0))})}</button>`:""}${bAvail(d)?adds:k0?"":`<span class="note">${T("Past your selected Act.")}</span>`} <a href="#i${d.ix}">${T("Open full page →")}</a></p></div>`}
// side box: one page at a time (stats, each relic copy, effects), switched by arrows, tabs or ←/→
var BPANE="stats";
function bPaneHtml(pages){let c=pages.findIndex(p=>p[0]===BPANE);if(c<0)c=0;BPANE=pages[c][0];const n=pages.length;
 return `<div class="bpane" tabindex="-1"><div class="bpnav"><button class="chip bpar" data-pgs="-1" aria-label="${T("Previous panel")}"${n>1?"":" disabled"}>‹</button><div class="bpt" aria-live="polite"><small></small><b></b></div><button class="chip bpar" data-pgs="1" aria-label="${T("Next panel")}"${n>1?"":" disabled"}>›</button></div>
${n>1?`<div class="bptabs">${pages.map((p,i)=>`<button class="chip" data-pgi="${i}" title="${esc(p[2])}" aria-label="${esc(p[2])}">${p[4]?img(p[4]):esc(p[2])}</button>`).join("")}</div>`:""}
${pages.map((p,i)=>`<section class="bpgx" data-k="${esc(p[0])}" data-h="${esc(p[1])}" data-title="${esc(p[2])}"${i===c?"":" hidden"}>${p[3]}</section>`).join("")}</div>`}
function bPaneGo(i){const box=el("main").querySelector(".bpane"),g=[...box.querySelectorAll(".bpgx")],n=g.length;i=(i+n)%n;
 g.forEach((x,j)=>x.hidden=j!==i);box.querySelectorAll("[data-pgi]").forEach((b,j)=>b.setAttribute("aria-pressed",j===i));
 BPANE=g[i].dataset.k;box.querySelector(".bpt small").textContent=`${g[i].dataset.h} · ${i+1} / ${n}`;box.querySelector(".bpt b").textContent=g[i].dataset.title;
 const sd=box.closest(".bside");if(sd&&sd.scrollTop>box.offsetTop)sd.scrollTop=box.offsetTop}
function bPaneWire(){const box=el("main").querySelector(".bpane"),cur=()=>[...box.querySelectorAll(".bpgx")].findIndex(x=>!x.hidden);
 box.addEventListener("click",e=>{const s=e.target.closest("[data-pgs]"),t=e.target.closest("[data-pgi]");if(s)bPaneGo(cur()+ +s.dataset.pgs);else if(t)bPaneGo(+t.dataset.pgi)});
 box.addEventListener("keydown",e=>{if((e.key==="ArrowLeft"||e.key==="ArrowRight")&&!e.target.closest("input,select,textarea")){e.preventDefault();bPaneGo(cur()+(e.key==="ArrowLeft"?-1:1))}});
 bPaneGo(cur())}
// the planner stacks into one column at 860px (v5.css): the picker and the inspector open below the slots there
const NARROW=()=>matchMedia("(max-width:860px)").matches;
function buildPage(h){
 if(h!==undefined){bParse(h);BPICK=null;BINSP=null}
 document.title=T("Build planner")+" · Linggango Wiki";
 const caps=bCaps(),eq=Object.values(BS.s).flat(),tot={},lf=skLadder(eq),uq=[...new Set(eq)];
 bCounted().forEach(id=>statsOf(BYID[id]).forEach(s=>tot[s.k]=Math.round(((tot[s.k]||0)+s.v*(lf[id]??1))*100)/100));
 const late=eq.filter(id=>!bAvail(BYID[id])).length;
 const row=k=>{const have=BS.s[k]||[],cap=caps[k],n=Math.max(cap,have.length);let b="";
  for(let i=0;i<n;i++){const id=have[i],xt=i>=SLOT_BASE[k]&&i<cap?" xtra":"";if(id){const d=BYID[id];b+=`<span class="bx on${xt}${bAvail(d)?"":" late"}${i>=cap?" over":""}${BINSP===id?" sel":""}"><button class="bxi" data-insp="${esc(id)}" data-t="${d.ix}" title="${T("Show recipe and details")}">${img(id)}<span>${esc(TD(d.n))}</span></button><button class="bxr" data-rm="${esc(k)}|${esc(id)}" aria-label="${esc(T("Remove {name}",{name:TD(d.n)}))}" title="${T("Remove")}">×</button></span>`}
   else b+=`<button class="bx${xt}${BPICK===k?" sel":""}" data-pick="${esc(k)}" aria-label="${esc(T("Add {slot} curio",{slot:T(k)}))}"${xt?` title="${T("Bonus slot from an equipped curio")}"`:""}>+</button>`}
  const si=slotIcon(k);return `<div class="bslot${have.length?" has":""}"><div class="bsh">${si?`<img class="bsi" alt="" src="${si}">`:""}<b>${esc(T(k))}</b><span class="${have.length>cap?"bad":""}">${have.length}/${cap}</span>${caps[k]>SLOT_BASE[k]?`<em>+${caps[k]-SLOT_BASE[k]}</em>`:""}</div><div class="bsb">${b}</div></div>`};
 const stats=Object.entries(tot).filter(([,v])=>v).sort((a,b)=>a[0].localeCompare(b[0]));
 const pages=[["stats",T("Build"),T("Stat totals"),`${stats.length?`<table>${stats.map(([k,v])=>`<tr><td>${esc(k.replace(/ %$/," (%)"))}</td><td class="num ${v<0?"neg":""}">${v>0?"+":""}${v}${/ %$/.test(k)?"%":""}</td></tr>`).join("")}</table>`:`<p class="note">${eq.length?T("No flat or percentage bonuses to sum."):T("Add curios to see totals.")}</p>`}
${BSTALE?`<p class="note">${T("This link was made on a different wiki version, so some items may not match.")}</p>`:""}${BLOST?`<p class="note">${TN(BLOST,"{n} item in this link could not be placed.","{n} items in this link could not be placed.")}</p>`:""}<p class="note">${Object.values(lf).some(v=>v<1)?T("Flat bonuses (+N) and percentage bonuses (+N%) are summed on separate lines; a second copy counts only if its bonus stacks, and ladder-reduced curios count at their reduced share. Conditional effects and ×multipliers are not summed: see the Effects tab."):T("Flat bonuses (+N) and percentage bonuses (+N%) are summed on separate lines; a second copy counts only if its bonus stacks. Conditional effects and ×multipliers are not summed: see the Effects tab.")}</p>`]];
 bKeys().filter(k=>RL[rlId(k)]).forEach(k=>{const id=rlId(k),c=k.split("#")[1]||(bWorn(id)>1?1:0);pages.push(["rl:"+k,T("Relic levels"),TD(BYID[id].n)+(c?" #"+c:""),rlPanel(k,true)+`<p class="note">${T("Slots a relic adds count its lowest roll.")}</p>`,id])});
 if(eq.length)pages.push(["fx",T("Build"),T("Effects"),`<ul>${uq.map(id=>{const d=BYID[id],n=bWorn(id);const k=Object.keys(BS.s).find(k=>BS.s[k].includes(id)),nx=(evo().to[id]||[]).filter(t=>bFits(BYID[t],k));return `<li><a href="#i${d.ix}" data-t="${d.ix}">${esc(TD(d.n))}</a>${n>1?` ×${n}${SK.i[id]?" "+skTag(id):""}`:""}: ${esc(fxT(d))}${lf[id]<1?` <span class="sk sk-${lf[id]?"l":"n"}" title="${esc(T("Outranked by a better {set} curio in this build",{set:SK.i[id].l[0]}))}">${lf[id]?esc(T("{set} ladder: {pct} strength",{set:SK.i[id].l[0],pct:pct(lf[id])})):esc(T("{set} ladder: switched off",{set:SK.i[id].l[0]}))}</span>`:""}${nx.map(t=>` <button class="chip" data-evo="${esc(k)}|${esc(id)}|${esc(t)}">${T("Evolve → {name}",{name:esc(TD(BYID[t].n))})}</button>`).join("")}</li>`}).join("")}</ul>`]);
 el("main").innerHTML=`${crumb(T("Build planner"))}${room("armory",uq.map(id=>rCurio(BYID[id])),{head:`<h1>${T("Build planner")}</h1>
<p class="lede">${T("Pick the furthest Act you've reached, then fill your curio slots. Slot counts are the base pack's player slots; curios that add slots raise them, and the Curio slot takes any accessory.")} ${NOHOVER?T("Tap any curio to see its recipe tree, and use × to take it off."):T("Hover any curio for its tooltip; click it to see its recipe tree, and use × to take it off.")}</p>`,min:8,cols:8,label:T("Your build")})}
<div class="bbar"><label>${T("Progress")} <select id="bp">${ORDER.map(a=>`<option value="${a}"${a===BS.p?" selected":""}>${esc(actL(a))}${a?" · "+esc(T(ACT[a][1])):""}</option>`).join("")}</select></label>
<span class="bpre">${T("Starter build:")} ${Object.entries(ROLE).map(([k,v])=>`<button class="chip" data-preset="${k}">${T(v)}</button>`).join("")}</span>
<span class="bact"><button class="chip" id="bcopy">${T("Copy link")}</button><button class="chip" id="bclr">${T("Clear")}</button></span></div>
${late?`<p class="bwarn">${TN(late,"{n} curio is past your selected Act (marked red).","{n} curios are past your selected Act (marked red).")}</p>`:""}
<div class="bgrid"><div class="bslots">${Object.keys(SLOT_BASE).map(row).join("")}${consRow()}</div>
<aside class="bside">${bInspHtml()}${BPICK?`<div class="bpick"><div class="bph"><b>${T("Add to {slot}",{slot:esc(T(BPICK))})}</b><button class="ghost" id="bpx">${T("Close")}</button></div><input id="bq" type="search" placeholder="${T("Search name, effect or mod…")}" name="buildq" spellcheck="false" aria-label="${T("Search curios for this slot")}" autocomplete="off"><div id="bopts" class="bopts">${bPickHtml()}</div></div>`:""}
${bPaneHtml(pages)}</aside></div>`;
 el("bp").onchange=e=>{BS.p=+e.target.value;bSave()};
 el("bclr").onclick=()=>{BS.s={};BS.c=[];BPICK=null;bSave()};
 el("bcopy").onclick=()=>{const u=location.href;(navigator.clipboard?navigator.clipboard.writeText(u):Promise.reject()).then(()=>{el("bcopy").textContent=T("Link copied")},()=>prompt(T("Copy this link:"),u))};
 if(el("bq")){el("bq").oninput=()=>{el("bopts").innerHTML=bPickHtml();bFade()};el("bopts").onscroll=bFade;bFade();el("bpx").onclick=()=>{const k=BPICK;keepFocus(()=>{BPICK=null;buildPage()},m=>m.querySelector(`[data-pick="${CSS.escape(k)}"]`))};el("bq").focus({preventScroll:true})}
 el("main").querySelector(".bgrid").onclick=e=>{
  const p=e.target.closest("[data-pick]"),rm=e.target.closest("[data-rm]"),ad=e.target.closest("[data-add]"),ev=e.target.closest("[data-evo]"),ins=e.target.closest("[data-insp]"),cn=e.target.closest("[data-cons]");
  if(cn){const i=cn.dataset.cons;BS.c=BS.c.includes(i)?BS.c.filter(x=>x!==i):[...BS.c,i];hideTip();bSave()}
  else if(ins){const was=BINSP;BINSP=ins.dataset.insp||null;hideTip();keepFocus(buildPage,BINSP?null:m=>was&&m.querySelector(`[data-insp="${CSS.escape(was)}"]`));const b=el("main").querySelector(".binsp");if(b&&NARROW())b.scrollIntoView({block:"start"})}
  else if(ev){const [k,id,to]=ev.dataset.evo.split("|");BS.s[k][BS.s[k].indexOf(id)]=to;hideTip();bSave(m=>m.querySelector(`.bslots [data-insp="${CSS.escape(to)}"]`))}
  else if(p){BPICK=p.dataset.pick;buildPage();const b=el("main").querySelector(".bpick");if(b&&NARROW())b.scrollIntoView({block:"start"})}
  else if(rm){const [k,id]=rm.dataset.rm.split("|");const a=BS.s[k]||[],i=a.lastIndexOf(id);if(i>=0)a.splice(i,1);hideTip();bSave(m=>m.querySelector(`.bslots [data-pick="${CSS.escape(k)}"]`)||m.querySelector(`.bslots [data-rm^="${CSS.escape(k+"|")}"]`))}
  else if(ad){const [k,id]=ad.dataset.add.split("|");(BS.s[k]=BS.s[k]||[]).push(id);const shut=BS.s[k].length>=bCaps()[k];if(shut)BPICK=null;hideTip();
   bSave(shut?m=>[...m.querySelectorAll(`.bslots [data-rm="${CSS.escape(k+"|"+id)}"]`)].pop()||m.querySelector(`.bslots [data-pick="${CSS.escape(k)}"]`):null)}};
 bPaneWire();
 el("main").querySelector(".bpre").onclick=e=>{const b=e.target.closest("[data-preset]");if(b){BPICK=null;bPreset(b.dataset.preset)}};
}

// ACTS row (old guide table) for each Keeper
var BOSS_ACT={iron_colossus:1,goblin_lord:2,arion:3,eldorath:4,zoranth_forgotten:5,elvenite_paladin:6,vaedric:7,discord:8,sanghor:9,zoranth_newborn:10,nyxaris:11};
function pathText(s){return String(s)}
function bossPath(k){const a=ORDER.find(a=>PB[a]===k);return a!==undefined?a:SIDEV[k]}
function bossName(k){return (bst(k)&&bst(k).name)||(VBI[k==="ender_dragon"?"dragon":k]||{}).n||nmI("x:"+k)}
const bossNameT=k=>TD(bossName(k));
const ilink=(id,n)=>{const d=BYID[id];return d?`<a href="#i${d.ix}" data-t="${d.ix}">${esc(TD(n||d.n))}</a>`:esc(TD(n||NM[id]||nmI(id)))};
const islot=(id,big)=>`<span class="slot${big?" big":" sm"}" title="${esc(TD(NM[id]||nmI(id)))}">${img(id)}</span>`;
// vanilla summons, written out step by step (no item recipe to show)
const VSUM={
 warden:{item:"minecraft:sculk_shrieker",name:"Sculk Shrieker",steps:[N("Go to an Ancient City in the Deep Dark (deep below y 0 in the Deep Dark biome)."),N("Set off a natural Sculk Shrieker three times: walk or sprint near Sculk Sensors, or step on the shrieker. Each shriek raises your warning level and gives Darkness."),N("The fourth shriek makes the Warden dig out of the ground next to the shrieker. Sneaking and wool keep the warning level down if you are not ready.")],extra:N("The pack gives the Warden 700 health and 20 armor. If every player who hurt it dies in that dimension it gets back 50% of its health. It drops a Sculk Catalyst."),grid:null},
 wither:{item:"minecraft:wither_skeleton_skull",name:"Wither Skeleton Skull",steps:[N("Collect 3 Wither Skeleton Skulls: Wither Skeletons in Nether Fortresses drop them (2.5%, Looting raises it)."),N("Place 4 Soul Sand or Soul Soil in a T: one block, three across on top of it."),N("Put the 3 skulls on the top row. The last skull spawns the Wither; it explodes after it charges, so build it away from your base or underground in a sealed room.")],extra:N("Pack values: 500 health, 20 armor, 32 damage. Below half health its armor blocks arrows. It always drops a Nether Star (Demon Heart, Made in Heaven, Curse of Envy). Its health comes back to 50% if everyone who hurt it dies there."),grid:[["minecraft:wither_skeleton_skull","minecraft:wither_skeleton_skull","minecraft:wither_skeleton_skull"],["minecraft:soul_sand","minecraft:soul_sand","minecraft:soul_sand"],[null,"minecraft:soul_sand",null]]},
 ender_dragon:{item:"minecraft:ender_eye",name:"Eye of Ender",steps:[N("Craft Eyes of Ender (Ender Pearl + Blaze Powder) and throw them to find a Stronghold."),N("Fill all 12 frames of the End Portal with eyes and jump in."),N("Destroy the End Crystals on the obsidian pillars first (some sit in iron cages), then fight the Dragon on the central island.")],extra:N("Killing it turns on Hardmode for the world: Hardmode scales other mobs ×2.1 in health and damage; the Armageddon bosses, Wither and Ender Dragon (forge:armageddon_bosses tag) and the Warden (blacklist) are exempt, and since 6.6.6 every player who has killed it carries 30 extra Hostility levels. The End then fills with monsters and Erasure storms, and the Night of Chaos, Krampus Night and Black Sabbath invasions unlock. Its treasure bag gives the Khyros's Goldened Tears for Titan's Insigna, the Elvenite Paladin's summon item. First kill: 12,000 XP and the Dragon Egg."),grid:null}};
const UNL_TIER={2:"Iron",3:"Gold",4:"Emerald",5:"Diamond",6:"Netherite",7:"Elvenite",8:"Voiderite",9:"Cataclysm",10:"Blood",11:"Sun",12:"Shadow"};
function unlockText(k,a){
 if(VBOSS[a])return T(k==="ender_dragon"?N("No Keeper tier. It turns on Hardmode and its treasure bag is the only source of Khyros's Goldened Tears."):N("No Keeper tier: nothing is locked behind it. The wiki places it here because of the gear you need to beat it."));
 const t=UNL_TIER[a],n=D.filter(d=>d.gk===a).length,ch=(CHAP.find(c=>c[0]===a)||[0,""])[1];
 return T("Beating it opens the {tier} tier. Items in the {tier} tier ({lower} tools, armor and the machines, magic and curios the pack locks there; {n} curios on this wiki) can then be crafted, placed, used and worn.",{tier:t,lower:t.toLowerCase(),n})+(ch?" "+T("Mods with the most items locked here: {mods}.",{mods:esc(ch)}):"")}
const TAGI={"minecraft:small_flowers":"minecraft:poppy","minecraft:flowers":"minecraft:poppy"};
// 6.6.6: the summon recipe's soul slot takes the Boss Soul of one of these side bosses, or a Mystical Agriculture ingot
const soulFrom=o=>{const nm=e=>{const f=typeof SIDEB!=="undefined"&&Object.entries(SIDEB).find(([,b])=>b.entity===e||(Array.isArray(b.entity)&&b.entity.includes(e)));return f?f[0]:e.split(":")[1].replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase())};
 return T("Boss Soul of {bosses}",{bosses:o.bosses.map(nm).map(x=>TD(x)).join(", ")})+(o.or&&o.or.length?"; "+T("or {items} instead",{items:o.or.map(i=>NM[i]||nmI(i)).join(", ")}):"")};
function sumGrid(g){return `<div class="sgrid">${g.map(r=>r.map(c=>c?islot(c.startsWith("#")?(TAGI[c.slice(1)]||c.slice(1)):c):`<span class="slot sm"></span>`).join("")).join("")}</div>`}
/* the item's own text opens with "Allow you to spawn X!", which the lead above already says: it is dropped (the translation ends its first sentence with "!" too) */
const sumInfo=t=>{const o=TD(t);return /^Allow you to spawn/.test(t)?o.replace(LANG==="en"?/^Allow you to spawn[^!]*!\s*/:/^[^!]*!\s*/,""):o};
function summonHtml(k){
 const v=VSUM[k];
 if(v)return `<section class="s sumg"><h2>${T("How to summon it")}</h2><div class="sumhead">${islot(v.item,1)}<div><b>${esc(TD(v.name))}</b><ol class="how">${v.steps.map(x=>`<li>${esc(T(x))}</li>`).join("")}</ol></div></div>${v.grid?`<h3>${T("Build it like this")}</h3><div class="sumcraft">${sumGrid(v.grid)}<span class="arr">→</span>${islot("minecraft:wither_skeleton_skull",1)}<small>${esc(TD("Wither"))}</small></div>`:""}<p class="note">${esc(T(v.extra))}</p></section>`;
 const u=typeof SUM!=="undefined"&&SUM[k];if(!u)return "";
 const where=/in the Nether/i.test(u.use)?"in the Nether":/in the End/i.test(u.use)?"in the End":"anywhere";
 return `<section class="s sumg"><h2>${T("How to summon it")}</h2><div class="sumhead">${islot(u.item,1)}<div><b>${ilink(u.item,u.name)}</b><p>${T(where==="in the Nether"?N("Hold it and right-click <b>in the Nether</b> to summon the boss next to you. One item is used up per summon."):where==="in the End"?N("Hold it and right-click <b>in the End</b> to summon the boss next to you. One item is used up per summon."):N("Hold it and right-click <b>anywhere</b> to summon the boss next to you. One item is used up per summon."))}</p>${u.info?`<p class="note">${esc(sumInfo(u.info))}</p>`:""}</div></div>
${u.recipe?`<h3>${/^the\s/i.test(u.name)?T("Crafting {name}",{name:esc(u.name)}):T("Crafting the {name}",{name:esc(u.name)})}</h3><div class="sumcraft">${sumGrid(u.recipe)}<span class="arr">→</span>${islot(u.item,1)}<small>${u.recipe_src==="pack KubeJS"?T("Linggango's own recipe (replaces the mod's)"):esc(TD("Crafting Table"))}</small></div>
<table class="sumings"><tr><th>${T("Ingredient")}</th><th>${T("Where to get it")}</th></tr>${u.ings.map(x=>`<tr><td>${islot(x.id.startsWith("#")?(TAGI[x.id.slice(1)]||x.id.slice(1)):x.id)} ${x.id.startsWith("#")?esc(TD(x.n)):ilink(x.id,x.n)}</td><td>${x.id==="linggango_tweaks:boss_soul"&&u.soul?esc(soulFrom(u.soul)):esc(x.from?TD(x.from):T("common material"))}</td></tr>`).join("")}</table>${u.routes&&u.routes.length?`<h3>${T("Other ways to make it")}</h3><p>${T("Instead of the Crafting Table, any one of these machines makes it (the Act quest in the quest book says which).")}</p><table class="sumings"><tr><th>${T("Machine")}</th><th>${T("Ingredients")}</th></tr>${u.routes.map(r=>`<tr><td>${esc(TD(r.label))}</td><td>${r.ings.map(x=>`<span class="nch">${islot(x.id.startsWith("#")?(TAGI[x.id.slice(1)]||x.id.slice(1)):x.id)}${x.c>1?`<b>${x.c}×</b>`:""}${esc(TD(x.n))}</span>`).join(" ")}</td></tr>`).join("")}</table>`:""}`+(u.infinite&&u.infinite.recipe?`<h3>${T("Reusable version: {name}",{name:esc(u.infinite.name)})}</h3><p>${T("Unbreakable, so it summons the boss again and again (handy for farming its drops once the first-kill damage cap is gone).")}</p><div class="sumcraft">${sumGrid(u.infinite.recipe)}<span class="arr">→</span>${islot(u.infinite.item,1)}<small>${esc(TD("Crafting Table"))}</small></div>`:""):`<p>${T("{name} has no recipe: {info}",{name:esc(u.name),info:esc(TD(u.info))})}</p>`}</section>`}
function bossList(){
 document.title=T("Bosses")+" · Linggango Wiki";
 const ks=ORDER.map(a=>PB[a]).filter(Boolean);ks.splice(ks.indexOf("zoranth_forgotten")+1,0,"warden","wither");
 el("main").innerHTML=`${crumb(T("Bosses"))}${room("crypt",ks.map(k=>{const v=VSUM[k],u=typeof SUM!=="undefined"&&SUM[k],it=v?v.item:u&&u.item;return it?{h:"#boss/"+k,i:img(it),n:T("{boss}: summoned with {item}",{boss:bossNameT(k),item:TD(v?v.name:u.name)}),l:esc(ACT[bossPath(k)][0])}:null}).filter(Boolean),{head:`<h1>${T("Bosses")}</h1><p class="lede">${T("The Keepers in fight order: beating each one opens the next Act. Below them, the optional side bosses by Act. Open any boss for how to summon it, its attacks and its drops.")}</p>`,cols:7,label:T("Summon items in fight order")})}
<h2 class="gt bsec">${T("Keepers and vanilla bosses")}</h2><div class="blist">${ks.map(k=>{const a=bossPath(k),v=VSUM[k],u=typeof SUM!=="undefined"&&SUM[k],it=v?v.item:u&&u.item,itn=v?v.name:u&&u.name;return `<a class="bcardl" href="#boss/${k}" style="--tc:${ACT[a][2]};${btex(a,k)}">${envFx(a,k)}${cardFig(k)||emblem(a,"sm")}<span><b>${esc(bossNameT(k))}</b><small>${SIDEV[k]!=null?T("Side boss · {act}",{act:esc(actL(a))}):T("Opens {act}",{act:esc(actL(a))})}</small>${it?`<small class="bsum">${img(it)} ${esc(TD(itn))}</small>`:""}</span></a>`}).join("")}</div>${sideList()}${wikiNav()}`}
/* optional bosses, by the Act you can take them on; each opens its own page */
function sideList(){if(typeof SIDEB==="undefined")return "";const rows=(typeof BOSSR!=="undefined"?BOSSR:[]).filter(r=>SIDEB[r[0]]&&!/Keeper/.test(r[0]));
 const acts=ORDER.filter(a=>rows.some(r=>r[1]===a));if(!acts.length)return "";
 return `<h2 class="gt bsec">${T("Side bosses")}</h2><p class="gs">${T("Optional fights, by the Act your gear can take them. Many drop curios and materials you need later.")}</p>
 ${acts.map(a=>`<div class="sbact" style="--tc:${ACT[a][2]}"><h3>${emblem(a,"xs")} ${esc(actL(a))}</h3><div class="sbgrid">${rows.filter(r=>r[1]===a).map(r=>{const sp=sidePic(r[0]);
  const k=sideKey(r[0]),ki=k?(IC[k.id]?img(k.id):`<img alt="" src="${BIMG[k.id]}">`):`<i class="lrt" style="--lrt:var(--rt-spawner)"></i>`;
  return `<a class="sbc${sp?" pic":""}" href="#side/${enc(r[0])}">${sp?`<img class="sbbg" alt="" src="${sp}">`:""}<span class="sbk">${ki}</span><span class="sbt"><b>${esc(TD(r[0]))}</b>${SIDEB[r[0]]&&SIDEB[r[0]].gname?`<i class="sbg">${esc(SIDEB[r[0]].gname)}</i>`:""}<small>${k?T("Drops {name}",{name:esc(TD(k.n))}):esc(SIDEB[r[0]].mod||T("Side boss"))}</small></span></a>`}).join("")}</div></div>`).join("")}`}
/* the drop a side boss is fought for: a curio first, then a modded item, then anything with a picture */
const sideKey=n=>{const ds=((SIDEB[n]||{}).drops||[]).filter(x=>x.id&&(IC[x.id]||(typeof BIMG!=="undefined"&&BIMG[x.id])));return ds.find(x=>BYID[x.id])||ds.find(x=>!/^minecraft:/.test(x.id))||ds[0]||null};
const ATG={melee:ui("sword",1),proj:ui("bow",1),aoe:ui("aoe",1),summon:ui("summon",1),move:ui("move",1),buff:ui("buff",1)};
const atype=d=>/summon|spawns? (a|an|\d|two|three|four|five|six|minions?)|calls? /i.test(d)?"summon":/throws|shoots|fires|projectile|bolt|orb|beam|laser|arrow/i.test(d)?"proj":/ground|area|around it|within \d+ blocks|ring|circle|shockwave|explo/i.test(d)?"aoe":/teleport|dash|charge|leap|jumps|flies/i.test(d)?"move":/heals?|regenerat|gains? resistance|buffs? itself/i.test(d)?"buff":"melee";
function bossInfoHtml(k){const b=typeof BINFO!=="undefined"&&BINFO[k];if(!b)return "";
 const di=id=>BIMG[id]?`<img alt="" src="${BIMG[id]}">`:(IC[id]?img(id):"");
 const drops=b.drops.length?`<section class="s"><h2>${T("Drops")}</h2><div class="bdrops">${b.drops.map(d=>`<div class="bdrop${d.via==="treasure bag"?" bag":""}"><span class="slot">${di(d.id)}</span><b>${BYID[d.id]?ilink(d.id,d.n):esc(TD(d.n))}</b><span class="bch">${esc(TD(d.chance))}</span>${d.count&&d.count!=="1"?`<small>×${esc(TD(d.count))}</small>`:""}${d.note?`<small class="bnt">${esc(TD(d.note))}</small>`:""}</div>`).join("")}</div><p class="note">${T("Gold frame: dropped straight on death. Plain: inside the Treasure Bag (right-click it).")}</p></section>`:"";
 const ph=b.ph.filter(p=>p.at.length),multi=ph.length>1;
 const atk=ph.length?`<section class="s"><h2>${T("Attacks")}</h2>${ph.map((p,i)=>`${multi?`<h3>${p.title?esc(TD(p.title)):esc(p.e.replace(/_/g," ").replace(/\b(\w)/g,c=>c.toUpperCase()))}</h3>`:""}<div class="batks">${p.at.map(a=>{const im=a.img?BIMG["g:"+a.img]:a.ic?BIMG[a.ic]:null;return `<div class="batk">${im?`<img class="bai" alt="" src="${im}">`:`<span class="bai bai0 ${atype(a.d)}">${ATG[atype(a.d)]}</span>`}<div><b>${esc(TD(a.n))}</b>${a.ph?`<small class="bph">${esc(TD(a.ph))}</small>`:""}<p>${esc(TD(a.d))}</p></div></div>`}).join("")}</div>`).join("")}</section>`:"";
 return atk+drops}
// Stats of a boss as a table, one row per phase or body: Keepers from BST (pack overrides, HP bonus, Hardmode), side bosses
// from SSTAT (the mod jars). hm: the fight comes after the Ender Dragon, so Hardmode's ×2.1 health and damage is the number shown.
const HMX=2.1,fnum=v=>v==null?"—":String(Math.round(v*10)/10),mobN=e=>e.split(":")[1].replace(/_boss$|_p_?2$/,"").replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase());
const hmAfter=a=>ORDER.indexOf(a)>=ORDER.indexOf(bossPath("ender_dragon"));
function statTable(rows,hm,note){if(!rows.length)return "";const has=k=>rows.some(r=>r[k]!=null),cols=[["hp",N("Health")],["armor",N("Armor")],["tough",N("Toughness")],["dmg",N("Attack")],["cap",N("Most damage per hit")]].filter(c=>has(c[0]));
 const cell=(r,k)=>{const v=r[k],o=r.o&&r.o[k];return `<td><b>${fnum(v)}</b>${r.x&&r.x[k]?`<small>${esc(r.x[k])}</small>`:""}${o!=null&&o!==v?`<small>${fnum(o)} ${hm?T("before Hardmode"):T("in Hardmode")}</small>`:""}</td>`};
 return `<div class="tw bst"><table><tr>${rows.length>1?"<th></th>":""}${cols.map(c=>`<th>${T(c[1])}</th>`).join("")}${has("hits")?`<th>${T("Hits to win")}</th>`:""}</tr>${rows.map(r=>`<tr>${rows.length>1?`<td>${esc(TD(r.n))}</td>`:""}${cols.map(c=>cell(r,c[0])).join("")}${has("hits")?`<td><b>${r.hits??"—"}</b></td>`:""}</tr>`).join("")}</table></div>${note}`}
function keeperStats(k){if(typeof BST==="undefined")return "";const ks=k==="discord"?["bringer_of_doom","famine","chaos","discord"]:[k],bs=ks.map(x=>BST[x]).filter(Boolean);if(!bs.length)return "";
 const hm=bs.some(b=>b.phases.some(p=>p.hardmode&&b.effective.hp===p.hardmode.hp)),rows=[];
 for(const b of bs)b.phases.forEach((p,i)=>{const e=hm&&p.hardmode?p.hardmode:p.pre_hardmode||p.base,o=hm?p.pre_hardmode:p.hardmode;rows.push({n:b.phases.length>1?`${b.name.split(",")[0]} · ${T("phase {n}",{n:i+1})}`:b.name.split(",")[0],...e,o})});
 const rules=[...new Set(bs.flatMap(b=>b.rules||[]))].filter(x=>!/^Assumption/.test(x));
 return statTable(rows,hm,`<ul class="how bstr">${rules.map(x=>`<li>${esc(TD(x))}</li>`).join("")}</ul>`)}
function sideStats(n,a){const ss=typeof SSTAT!=="undefined"&&SSTAT[n];if(!ss)return "";const hm=hmAfter(a);let hpX=0,dmX=0;
 const rows=ss.map(s=>{const dm=s.dmg?s.dmg*(s.dmg_mult??1):s.dmg,r={n:mobN(s.entity),armor:s.armor,tough:s.tough,hits:s.hits,hp:s.hp,dmg:dm,cap:s.cap,o:{},x:{}};
  const sc=(k,v)=>{hm?(r[k]=v*HMX,r.o[k]=v):r.o[k]=v*HMX};
  // the pack's boss souls (Linggango Tweaks) pin health and armor; Hardmode multiplies attack only for Monster-class mobs
  if(s.hp!=null&&!s.pinned){sc("hp",s.hp);hpX=1}if(dm&&s.monster!==false){sc("dmg",dm);dmX=1}
  if(s.dmg&&s.dmg_mult!=null&&s.dmg_mult!==1)r.x.dmg=T("{a} × {b} vs players",{a:fnum(s.dmg),b:fnum(s.dmg_mult)});return r});
 const src=[...new Set(ss.map(s=>s.src))],what=[hpX&&"health",dmX&&"attack"].filter(Boolean).join(" and ");
 return statTable(rows,hm,`<p class="note">${[ss.some(s=>s.pinned)?T("The pack pins this boss's health and armor (Linggango Tweaks boss souls), so Hardmode does not change them."):"",what?(hm?T(hpX&&dmX?N("Fought after the Ender Dragon, so the numbers include Hardmode (×2.1 health and attack)."):hpX?N("Fought after the Ender Dragon, so the numbers include Hardmode (×2.1 health)."):N("Fought after the Ender Dragon, so the numbers include Hardmode (×2.1 attack).")):T(hpX&&dmX?N("In Hardmode (after the Ender Dragon) health and attack are ×2.1."):hpX?N("In Hardmode (after the Ender Dragon) health is ×2.1."):N("In Hardmode (after the Ender Dragon) attack is ×2.1."))):"",rows.some(r=>r.x.dmg)?T("Attack against players: the attack attribute × the pack's damage multiplier."):"",src.some(x=>/pack config|pack override/.test(x))?T("Includes the pack's own settings ({list}).",{list:esc([...new Set(src.join("; ").match(/pack config [^ ]+|entitybalance\.json/g)||[])].map(x=>x.replace("pack config ","")).join(", "))}):"",rows.some(r=>r.cap!=null)?T("Most damage per hit: one hit never takes more than this off the boss."):"",T("Base values read from the mod's code.")].filter(Boolean).join(" ")}</p>`)}
const BE=k=>typeof BST!=="undefined"&&BST[k]&&BST[k].effective||null;
const keeperHp=k=>{const b=typeof BST!=="undefined"&&BST[k];return b&&b.effective&&b.effective.hp?fnum(b.effective.hp)+(b.phases.length>1?" "+T("per phase"):""):""};
const sideHp=(n,a)=>{const s=typeof SSTAT!=="undefined"&&SSTAT[n];return s&&s.length===1&&s[0].hp!=null?fnum(s[0].hp*(hmAfter(a)&&!s[0].pinned?HMX:1)):""};
function sidePage(n){const b=typeof SIDEB!=="undefined"&&SIDEB[n],r=(typeof BOSSR!=="undefined"?BOSSR:[]).find(x=>x[0]===n);if(!b){location.replace("#bosses");return}
 document.title=TD(n)+" · Linggango Wiki";const a=r?r[1]:0,pi=typeof PIMG!=="undefined"?PIMG.side[n]:null,sl=typeof BGRAPH!=="undefined"&&BGRAPH.soul&&BGRAPH.soul[n];
 const di=id=>IC[id]?img(id):(typeof BIMG!=="undefined"&&BIMG[id]?`<img alt="" src="${BIMG[id]}">`:"");
 const same=(typeof BOSSR!=="undefined"?BOSSR:[]).filter(x=>x[1]===a&&SIDEB[x[0]]).map(x=>["#side/"+enc(x[0]),esc(TD(x[0])),x[0]===n]);
 const src=`${b.src_note?`<p class="note">${T("Source: {x}",{x:esc(TD(b.src_note))})}</p>`:""}${b.sources&&b.sources.length?`<p class="note">${T("Sources: {list}",{list:b.sources.map(u=>/^https?:/.test(u)?`<a href="${esc(u)}" target="_blank" rel="noopener">${esc(u.replace(/^https?:\/\/(www\.)?/,"").split("/")[0])}</a>`:`<span>${esc(TD(u))}</span>`).join(" · ")})}</p>`:""}`;
 el("main").innerHTML=article({cls:"r0 bossart",style:`--tc:${ACT[a][2]};--rc:${ACT[a][2]}`,crumb:crumb(`<a href="#bosses">${T("Bosses")}</a>`,esc(TD(n))),title:esc(TD(n)),
  lead:(b.gname?T("In the game: <b>{name}</b>.",{name:esc(b.gname)})+" ":"")+(b.mod?T("An optional side boss from {mod}. Fight it with {link} gear.",{mod:esc(b.mod),link:`<a href="#act/${a}">${esc(actL(a))}</a>`}):T("An optional side boss. Fight it with {link} gear.",{link:`<a href="#act/${a}">${esc(actL(a))}</a>`})),
  secs:[["find",T("Where to find it"),`<p class="sbfind">${esc(TD(b.find||""))}</p>${sl?`<p class="sbsoul">${img("linggango_tweaks:boss_soul")}<span>${T("<b>Boss Soul</b> · drops its soul, which can go into the {item}, the summon for {boss}.",{item:esc(sl[0]),boss:esc(sl[1])})}</span></p>`:""}${pi?`<figure class="sbfig"><img class="sbarena" alt="${T("Where it is fought")}" src="${pi}"></figure>`:""}`],
   (h=>h&&["stats",T("Stats"),h])(sideStats(n,a)),
   b.attacks&&b.attacks.length&&["atk",T("Attacks"),`<div class="batks">${b.attacks.map(x=>`<div class="batk"><span class="bai bai0 ${atype(x.desc)}">${ATG[atype(x.desc)]}</span><div><b>${esc(TD(x.name))}</b><p>${esc(TD(x.desc))}</p></div></div>`).join("")}</div>`],
   b.drops&&b.drops.length&&["drops",T("Drops"),`<div class="bdrops">${b.drops.map(x=>`<div class="bdrop bag"><span class="slot">${di(x.id)}</span><b>${BYID[x.id]?ilink(x.id,x.n):esc(TD(x.n))}</b><span class="bch">${esc(TD(x.chance||"—"))}</span>${x.count&&x.count!=="1"?`<small>×${esc(TD(x.count))}</small>`:""}</div>`).join("")}</div>${b.drops_note?`<p class="note">${esc(TD(b.drops_note))}</p>`:""}<p class="note">${b.drops_src?T("Chances are estimated from the loot table rolls (the mod's own table; the pack may override it)."):T("Chances are estimated from the loot table rolls.")}${b.drops.some(x=>!x.chance)?" "+T("A dash: the item is not in the loot table (the mod drops it in code or the quest book gives it)."):""}</p>`]],
  after:src,
  art:`<div class="ip-art"><div class="ip-stage" style="${tex(a)}">${envFx(a)}${b.img?`<div class="stage"><img alt="" src="${b.img}"></div>`:`<div class="ip-icon">${emblem(a,"lg")}</div>`}</div></div>`,
  box:{head:`<span class="ip-slot">${emblem(a,"xs")}</span><div><b>${esc(TD(n))}</b><span>${T("Side boss")}</span></div>`,
   rows:[[T("Type"),T("Optional side boss")],b.mod&&[T("Mod"),esc(b.mod)],[T("Fight in"),`<a href="#act/${a}">${esc(actL(a))}</a>`],sideHp(n,a)&&[T("Health"),sideHp(n,a)],sl&&[T("Boss Soul"),T("for {item}",{item:esc(sl[0])})],b.drops&&b.drops.length&&[T("Drops"),String(b.drops.length)]],
   foot:b.entity?idBox(b.entity):""},
  nav:wikiNav({act:a},[[T("Side bosses in {act}",{act:esc(actL(a))}),same]])});
 wireArticle()}
function bossPage(k){
 const a=bossPath(k);if(a===undefined){bossList();return}
 const nm=bossName(k),nmT=bossNameT(k),i=ORDER.indexOf(a),row=ACTS[BOSS_ACT[k]],side=SIDEV[k]!=null,vb=VBI[k==="ender_dragon"?"dragon":k],keeper=!side&&BOSS_ACT[k]!=null,kind=side?N("Optional side boss"):keeper?N("Keeper"):N("Required boss");
 // previous / next follow the Bosses list (KEEPERS(): Zoranth the Forgotten, Warden, Wither, Ender Dragon, ...); a side boss's own Act is a, a Keeper's fights are the Act before the one it opens
 const KS=KEEPERS(),ki=KS.indexOf(k),prevK=ki>0?KS[ki-1]:ki<0?PB[ORDER.slice(0,i).reverse().find(x=>PB[x])]:undefined,nextK=ki>=0?KS[ki+1]:PB[ORDER.slice(i+1).find(x=>PB[x])];
 const at=side?a:ORDER[i-1],sides=(typeof BOSSR!=="undefined"?BOSSR:[]).filter(r=>r[1]===at&&r[0]!==nm&&!/Keeper/.test(r[0])&&!/^(Ender Dragon)\b/.test(r[0]));
 // the pack's own note for this Keeper ("Act V Keeper; 20 dmg / 50 armor"), matched by Keeper order, read only when it has that shape
 const kn=BOSS_ACT[k]!=null&&typeof BOSSR!=="undefined"?(BOSSR.filter(r=>/\(Keeper\)/.test(r[0]))[BOSS_ACT[k]-1]||[])[3]||"":"",ks=String(kn).match(/Keeper;\s*(\d+)\s*(?:dmg|damage)(?:\s*\/\s*(\d+)\s*armor)?/);
 const v=VSUM[k],u=typeof SUM!=="undefined"&&SUM[k],sit=v?v.item:u&&u.item,sitn=v?v.name:u&&u.name;
 const xs=D.filter(d=>d.t===a),must=xs.filter(isMust),gated=D.filter(d=>d.gk===a).length;
 const opens=!side&&ACT[a]?["opens",T("What it opens"),`<p>${row&&row[3]&&row[3]!=="—"?T("Defeating {boss} opens {act}, and items behind the {gate} progression gate can be used.",{boss:esc(nmT),act:`<b>${esc(actL(a))}</b>`,gate:`<b>${esc(row[3].replace(/\s*\((Act|end)[^)]*\)\s*$/i,""))}</b>`}):T("Defeating {boss} opens {act}.",{boss:esc(nmT),act:`<b>${esc(actL(a))}</b>`})}</p>
<ul class="how"><li>${TN(xs.length,"{n} curio is first available in {act}{must}.","{n} curios are first available in {act}{must}.",{n:`<b>${xs.length}</b>`,act:esc(actL(a)),must:must.length?", "+T("{m} of them Must-Have: {list}",{m:must.length,list:must.slice(0,6).map(d=>ilink(d.id)).join(", ")}):""})}</li>${gated?`<li>${TN(gated,"{n} curio can only be worn once it is dead (Keeper-gated).","{n} curios can only be worn once it is dead (Keeper-gated).",{n:`<b>${gated}</b>`})}</li>`:""}</ul>
<p class="pbtn"><a class="mcb" href="#act/${a}">${TN(xs.length,"See {n} curio","See {n} curios")}</a><a class="mcb" href="#gear/${a}/ME/w">${T("Gear at {act}",{act:esc(actL(a))})}</a></p>`]:null;
 document.title=`${nmT} · Linggango Wiki`;
 const stage=typeof BFIG!=="undefined"&&BFIG[k]?`<div class="stage">${figHtml(k,figFit(k,300,256))}</div>`:BPORT[k]?`<div class="stage"><img alt="" src="data:image/png;base64,${BPORT[k]}"></div>`:`<div class="ip-icon">${emblem(a,"lg")}</div>`;
 el("main").innerHTML=article({cls:"r0 bossart",data:` data-boss-kind="${esc(k)}"`,style:`--tc:${ACT[a][2]};--rc:${ACT[a][2]}`,crumb:crumb(`<a href="#bosses">${T("Bosses")}</a>`,esc(nmT)),title:esc(nmT),
  lead:side?T("Optional side fight in {act}: it drops its own curios.",{act:`<a href="#act/${a}">${esc(actL(a))}</a>`}):(keeper?(ORDER[i-1]!=null?T("The Keeper at the end of {act}.",{act:esc(actL(ORDER[i-1]))}):T("The Keeper at the end of the start.")):T("A fight the pack requires."))+" "+T("Defeat it to open {act}.",{act:`<a href="#act/${a}">${esc(actL(a))}</a>`}),
  secs:[...secsOf(summonHtml(k),"sum"),(h=>h&&["stats",T("Stats"),h])(keeperStats(k)),...secsOf(bossInfoHtml(k),"inf"),opens,
   row&&row[5]&&row[5]!=="—"&&["know",T("Good to know"),`<p>${esc(TD(pathText(row[5])))}</p>`],
   sides.length&&["side",T("Side bosses at this point"),`<div class="tw"><table><tr><th>${T("Boss")}</th><th>${T("Where / notes")}</th><th>${T("Useful drops")}</th></tr>${sides.map(r=>`<tr><td><b>${typeof SIDEB!=="undefined"&&SIDEB[r[0]]?`<a href="#side/${enc(r[0])}">${esc(TD(r[0]))}</a>`:esc(TD(r[0]))}</b></td><td>${esc(TD(pathText(r[3]).replace(/[^;]*\d+\s*(dmg|damage|armor)[^;]*;?\s*/gi,"").trim())||"—")}</td><td>${r[4].slice(0,5).map(id=>ilink(id)).join(", ")||"—"}</td></tr>`).join("")}</table></div>`]],
  after:`<nav class="pnx">${prevK?`<a href="#boss/${prevK}"><small>${T("← Previous boss")}</small>${esc(bossNameT(prevK))}</a>`:"<span></span>"}${nextK?`<a href="#boss/${nextK}"><small>${T("Next boss →")}</small>${esc(bossNameT(nextK))}</a>`:""}</nav>`,
  art:`<div class="ip-art"><div class="ip-stage" style="${btex(a,k)}">${stage}${envFx(a,k)}</div></div>`,
  box:{head:`<span class="ip-slot">${emblem(a,"xs")}</span><div><b>${esc(nmT)}</b><span>${T(kind)}</span></div><i class="bossbar" aria-hidden="true"><i></i></i>`,
   rows:[[T("Type"),T(kind)],side?[T("Fight in"),`<a href="#act/${a}">${esc(actL(a))}</a>`]:[T("Opens"),`<a href="#act/${a}">${esc(actL(a))}</a>`],
    sit&&[T("Summoned with"),ilink(sit,sitn)],row&&[T("Weak to"),esc(TD(row[2]))],...(BE(k)?[BE(k).dmg!=null&&[T("Attack"),fnum(BE(k).dmg)],BE(k).armor!=null&&[T("Armor"),fnum(BE(k).armor)]]:[ks&&[T("Damage"),ks[1],T("Linggango pack setting")],ks&&ks[2]&&[T("Armor"),ks[2],T("Linggango pack setting")]]),
    keeperHp(k)?[T("Health"),keeperHp(k)]:vb&&vb.hp&&[T("Health"),String(vb.hp)],row&&row[4]&&row[4]!=="—"&&[T("Looting Charm"),esc(row[4])]],
   foot:vb&&vb.line?`<p class="note">${esc(TD(vb.line))}</p>`:""},
  nav:wikiNav({boss:k,act:a})});
 wireArticle()}

const nic=n=>{const id=typeof NAMEID!=="undefined"&&NAMEID[n];return id&&IC[id]?`<img class="nic" alt="" src="${icu(id)}">`:""};
const nchip=(x,re=/^(\d+)× /)=>{const m=x.match(re),n=m?x.slice(m[0].length):x;return `<span class="nch">${nic(n)}${m?`<b>${m[1]}×</b>`:""}${esc(/^any /.test(n)?T("any {tag}",{tag:TD(n.slice(4))}):TD(n))}</span>`};
const EFF_LOOK="(?<!Fire |Knockback |Grave |Attack |Movement |Mining |Armor |Damage |Swim |Sprint |Eldritch |Ender )";
const effRe=n=>new RegExp(EFF_LOOK+"\\b"+n+"\\b");
const EFFECTS=[
 {n:"Well Fed",k:"Food",d:"Attack, spell, summon and arrow damage and movement speed +5%, a little mining speed. A meal scoring 12 or more (cooked chicken is 13). Lasts 10 minutes.",note:"Any meal scoring 12 or more"},
 {n:"Plenty Satisfied",k:"Food",d:"The same bonuses at +10%. A meal scoring 24 or more. Lasts 15 minutes.",note:"Any meal scoring 24 or more"},
 {n:"Exquisitely Stuffed",k:"Food",d:"The same bonuses at +15%. A meal scoring 30 or more: every bowl and plate from a cooking pot. Lasts 20 minutes.",note:"Any meal scoring 30 or more"},
 {n:"Exposed",k:"Linggango",d:""},
 {n:"Familiar Face",k:"Linggango",d:""},
 {n:"Winded",k:"Linggango",d:"You hit the ground hard. Give yourself a second to get back up."},
 {n:"Erosion",k:"Linggango",d:"The End is rubbing you out. Each level takes 8% of your max health until you find cover."},
 {n:"Bleeding",k:"Linggango",d:"Loses a bit of health every half second, twice as much while moving."},
 {n:"Scorched",k:"Linggango",d:"Takes 15% more fire damage."},
 {n:"Frostbite",k:"Linggango",d:"40% slower and takes 15% more damage."},
 {n:"Stunned",k:"Linggango",d:"Can't move or attack."},
 {n:"Judged",k:"Linggango",d:"Glows and can't heal."},
 {n:"Dread",k:"Linggango",d:"Deals 30% less damage. When it ends, a quarter of the damage taken during it hits again."},
 {n:"Rooted",k:"Linggango",d:"Can't move, can still attack."},
 {n:"Rot",k:"Linggango",d:"Loses 1% of max health every second."},
 {n:"Unravelled",k:"Linggango",d:"Takes 20% more elemental and magic damage."},
 {n:"Chaos Spent",k:"Linggango",d:"Your Chaos Surge is recharging. Until this ends, a killing blow kills you."},
 {n:"Paradox Charge",k:"Linggango",d:"Damage your armour blocked, waiting to be unleashed by your next melee hit. When this runs out it bursts inside you for half."},
 ...["Speed","Slowness","Haste","Mining Fatigue","Strength","Jump Boost","Nausea","Regeneration","Resistance","Fire Resistance","Water Breathing","Invisibility","Blindness","Night Vision","Hunger","Weakness","Poison","Wither","Absorption","Saturation","Glowing","Levitation","Slow Falling","Darkness","Health Boost"].map(n=>({n,k:"Vanilla",d:""}))
].map(e=>({...e,re:effRe(e.n)}));
// effect names in an item's text link to the Effects list
function effHint(h){for(const e of EFFECTS){const m=h.match(e.re);if(!m)continue;const pre=h.slice(0,m.index);if(/<[^>]*$/.test(pre)||pre.lastIndexOf('<a class="sth"')>pre.lastIndexOf("</a>"))continue;h=pre+`<a class="sth" href="#mechanics/effects" title="${esc(TD(e.n))}">${m[0]}</a>`+h.slice(m.index+m[0].length)}return h}
function mechPage(){
 document.title=T("Mechanics")+" · Linggango Wiki";
 needPics();const G=GOETY,A=AE2,TY=Object.entries(G.types),cnt=G.counts;
 const tName=t=>(G.types[t]||{name:t}).name.replace(/ Rituals?$/,"");
 const act=a=>a?esc(actL(a)):"—";
 const kindL={craft:"Craft",enchant:"Enchant",summon:"Summon",summon_tamed:"Summon",summon_tamed_no_variant:"Summon",convert:"Convert",convert_tamed:"Convert",convert_complete_tamed:"Convert",locate:"Locate",teleport:"Teleport"};
 const gate=Object.entries(G.base_gate).filter(([,v])=>v).map(([k,v])=>`${esc(k)} (${act(v)})`).join(", ");
 const rowH=r=>`<tr data-ty="${esc(r.type||"")}" data-k="${esc(kindL[r.kind]||r.kind)}"><td>${r.out_id&&IC[r.out_id]?islot(r.out_id)+" ":""}<b>${r.out_id&&BYID[r.out_id]?ilink(r.out_id,r.out):esc(r.out)}</b>${r.xp?` <small>· ${T("{n} XP levels",{n:r.xp})}</small>`:""}</td><td>${esc(TD(tName(r.type)))}</td><td>${r.act_id&&IC[r.act_id]?`<img class="nic" alt="" loading="lazy" src="${icu(r.act_id)}">`:""}${esc(r.act)}</td><td class="nchs">${r.ings.map(x=>nchip(x)).join("")}</td><td class="num">${r.soul??"—"}</td><td>${[r.research?T("Research: {x}",{x:esc(G.research[r.research]||r.research)}):"",r.sacrifice?T("Sacrifice: {x}",{x:esc(r.sacrifice)}):"",r.gate?T("Locked until {act}",{act:act(r.gate)}):""].filter(Boolean).join("<br>")||"—"}</td></tr>`;
 // 711 rituals: drawn from the data, 60 at a time (a full table is ~40k nodes); the filter redraws instead of hiding rows
 const RMAX=60,rOk=(r,v,ty,k)=>(!ty||(r.type||"")===ty)&&(!k||(kindL[r.kind]||r.kind)===k)&&(!v||(r.out+" "+r.act+" "+r.ings.join(" ")).toLowerCase().includes(v));
 const cells=A.cells.map(c=>`<tr><td><b>${c.t}</b></td><td class="num">${nL(c.bytes)}</td><td class="num">${c.bpt}</td><td class="num">${nL((c.bytes-c.bpt)*A.per_byte_item)}</td><td class="num">${nL((c.bytes-63*c.bpt)*A.per_byte_item)}</td><td class="num">${nL((c.bytes-c.bpt)*A.per_byte_fluid_mb/1000)} B</td><td class="num">${c.drain}</td></tr>`).join("");
 const gates=Object.entries(A.gates).sort((a,b)=>a[0]-b[0]).map(([a,xs])=>`<tr><td><b>${act(+a)}</b><br><small>${T("after {boss}",{boss:esc(TD(GK[a]||""))})}</small></td><td class="nchs">${xs.slice(0,12).map(x=>nchip(x)).join("")}${xs.length>12?`<details class="nmore"><summary>${T("{n} more",{n:xs.length-12})}</summary><div class="nchs">${xs.slice(12).map(x=>nchip(x)).join("")}</div></details>`:""}</td></tr>`).join("");
 const made=[...new Map(G.rituals.filter(r=>r.out_id&&BYID[r.out_id]).map(r=>[r.out_id,BYID[r.out_id]])).values()].slice(0,8);
 const EFX_ROWS=EFFECTS.map(e=>({...e,items:D.filter(d=>e.re.test(d.fx))})).filter(e=>e.items.length||e.k!=="Vanilla").map(e=>`<tr id="eff-${esc(e.n.toLowerCase().replace(/ /g,"-"))}"><td><b>${esc(TD(e.n))}</b><br><small>${esc(T(e.k))}</small></td><td>${e.d?esc(TD(e.d)):"—"}</td><td class="nchs">${e.note?esc(TD(e.note)):e.items.map(d=>ilink(d.id,d.n)).join(" ")||"—"}</td></tr>`).join("");
 el("main").innerHTML=`${crumb(T("Mechanics"))}${room("ritual",made.map(d=>rCurio(d)),{head:`<h1>${T("Mechanics")}</h1><p class="lede">${T("How the pack's bigger systems work: Goety's dark rituals, AE2 storage and how the combat stats work, with Linggango's own changes.")}</p>`,cols:4,label:T("Curios made by rituals")})}

<nav class="mtabs"><a href="#mechanics" data-go="m-goety">${T("Goety rituals")}</a><a href="#mechanics" data-go="m-ae2">${T("AE2 storage")}</a><a href="#mechanics" data-go="m-effects">${T("Effects")}</a><a href="#mechanics" data-go="m-stats">${T("Stats")}</a></nav>
<section class="s" id="m-goety"><h2>${T("Goety: Dark Rituals")}</h2>
<div class="flow">
<div class="fst">${islot("goety:totem_of_souls",1)}<b>${T("1. Fill a totem")}</b><span>${T("Kill mobs with a Totem of Roots / Souls in your hotbar")}</span></div><i class="far">→</i>
<div class="fst">${islot("goety:cursed_cage",1)}${islot("goety:dark_altar",1)}<b>${T("2. Cage + Altar")}</b><span>${T("Totem in the Cursed Cage, Dark Altar on top")}</span></div><i class="far">→</i>
<div class="fst">${islot("goety:pedestal",1)}<b>${T("3. Pedestals")}</b><span>${T("Ingredients on Pedestals within {a} blocks, plus the blocks the ritual type needs",{a:G.range})}</span></div><i class="far">→</i>
<div class="fst">${islot("goety:dark_wand",1)}<b>${T("4. Activate")}</b><span>${T("Right-click the altar with the activation item")}</span></div>
</div>
<div class="kchips"><span><i class="lk" aria-hidden="true"></i>${T("Ritual blocks open at {act}",{act:`<b>${act(3)}</b>`})}</span><span><i class="ki" style="--ki:var(--rt-writable_book)" aria-hidden="true"></i>${T("Some rituals need a <b>research scroll</b>")}</span><span><i class="ki" style="--ki:var(--v-i_netherite_sword)" aria-hidden="true"></i>${T("Some need a <b>sacrifice</b> in range")}</span><span><i class="ki" style="--ki:var(--rt-ftb_alert)" aria-hidden="true"></i>${T("Wrong or extra items = ritual fails")}</span><span><i class="ki" style="--ki:var(--rt-ftb_shape_gear)" aria-hidden="true"></i>${T("6.6.6: the <b>Sabbath Engine</b> multiblock runs about 200 altar rituals for you on soul sand instead of souls (not the ones that need a research scroll)")}</span></div>
<h3>${T("Ritual types")}</h3>
<div class="rtypes">${TY.map(([k,t])=>`<div class="rtype">${t.img?`<img src="data:image/webp;base64,${t.img}" alt="${esc(T("{name} example layout",{name:TD(t.name)}))}" loading="lazy">`:""}<b>${esc(TD(t.name))}</b><small>${TN(cnt[k]||0,"{n} ritual","{n} rituals")}</small><div class="nchs">${t.req.map(x=>nchip(x,/^(\d+) /)).join("")}</div></div>`).join("")}</div>
<h3>${T("Every ritual in the pack ({a})",{a:G.rituals.length})}</h3>
<p class="note">${T("From Goety {a}, plus the pack's own datapack recipes; rituals the pack removes are left out. Soul = Soul Energy drained over the ritual.",{a:"and its addons (Goety Revelation, Goety Delight, Goety Cataclysm, Goety Hostility, Goety Awaken)"})}</p>
<div class="rflt"><input id="rq" type="search" aria-label="${T("Find a ritual, item or ingredient")}" placeholder="${T("Find a ritual, item or ingredient…")}"><select id="rt" aria-label="${T("Ritual type")}"><option value="">${T("All types")}</option>${TY.map(([k,t])=>`<option value="${esc(k)}">${esc(TD(t.name))}</option>`).join("")}</select><select id="rk" aria-label="${T("Ritual kind")}"><option value="">${T("All kinds")}</option>${[N("Craft"),N("Enchant"),N("Summon"),N("Convert"),N("Locate"),N("Teleport")].map(k=>`<option value="${k}">${T(k)}</option>`).join("")}</select><span id="rn"></span></div>
<div class="tw rtw"><table class="rtab"><thead><tr><th>${T("Result")}</th><th>${T("Type")}</th><th>${T("Activation item")}</th><th>${T("Ingredients (on pedestals)")}</th><th>${T("Soul")}</th><th>${T("Also needs")}</th></tr></thead><tbody id="rtb">${G.rituals.slice(0,RMAX).map(rowH).join("")}</tbody></table></div><div id="rmore"></div>
</section>
<section class="s" id="m-ae2"><h2>${T("AE2 storage")}</h2>
<p>${T("Applied Energistics 2 (15.4.11) with AE2 Things, AE2 Wireless Terminals and Insert/Export Card, plus the add-ons MEGA Cells (2.4.6), ExtendedAE (1.4.21) and Applied Flux (1.3.7). In Linggango its later parts open with the Keepers:")}</p>
<div class="tw"><table><tr><th>${T("Opens at")}</th><th>${T("AE2 parts that unlock")}</th></tr>${gates}</table></div>
<p class="note">${T("Since 6.6.6 (boss locks loosened) the ME Controller, Drive, Chest, 1k–16k cells, crafting and wireless terminals are open from the start; of AE2's own parts only 64k cells, the ME DISK line, spatial and quantum parts wait for {a}, and 256k for {b}. The add-ons are gated too: most ExtendedAE and Applied Flux parts at {a}, MEGA Cells from its 1M cells at {c} up to 64M and 256M at {d} (its Cell Dock at {e}).",{a:act(6),b:act(7),c:act(8),d:act(11),e:act(4)})}</p>
${typeof ROOMT!=="undefined"&&ROOMT.ae2_item_storage_cell_1k?slotRow([["1k",0],["4k",0],["16k",0],["64k",6],["256k",7]].map(([c,a])=>({h:"#mechanics",i:`<img alt="" src="data:image/png;base64,${ROOMT["ae2_item_storage_cell_"+c]}">`,n:a?T("{c} ME Storage Cell: from {act}",{c,act:actL(a)}):T("{c} ME Storage Cell: open from the start",{c}),l:c+(a?" · "+esc(ACT[a][0]):"")})),T("ME storage cells")):""}
<h3>${T("Getting started")}</h3>
<div class="flow">
<div class="fst">${islot("ae2:certus_quartz_crystal",1)}<b>${T("Certus Quartz")}</b><span>${T("Grow it, or Nether Quartz + Light Blue Dye")}</span></div>
<div class="fst">${islot("ae2:inscriber",1)}<b>${T("Presses")}</b><span>${T("Found in meteorites")}</span></div>
<div class="fst">${islot("ae2:energy_acceptor",1)}<b>${T("Power")}</b><span>1 FE = ${A.fe_ratio} AE</span></div>
<div class="fst">${islot("ae2:drive",1)}<b>${T("Drive")}</b><span>${T("Without a Controller: max 8 channels total")}</span></div>
<div class="fst">${islot("ae2:controller",1)}<b>${T("Controller")}</b><span>${T("Cable 8 · dense 32 · each face 32 channels")}</span></div>
</div>
<h3>${T("How much a cell holds")}</h3>
<p>${T("A cell has a byte budget. Every <b>item type</b> stored costs a fixed number of bytes before any items go in, then each byte holds {a} items (or {b} mB of fluid). Item cells take up to {c} types, fluid cells {d}. So one type fills a cell best; many types eat the budget.",{a:A.per_byte_item,b:nL(A.per_byte_fluid_mb),c:A.types_item,d:A.types_fluid})}</p>
<div class="tw"><table><tr><th>${T("Cell")}</th><th>${T("Bytes")}</th><th>${T("Bytes per type")}</th><th>${T("Items, 1 type")}</th><th>${T("Items, 63 types")}</th><th>${T("Fluid, 1 type")}</th><th>${T("Idle drain (AE/t)")}</th></tr>${cells}</table></div>
<h3>${T("ME DISK Drives (AE2 Things)")}</h3>
<p>${T("A DISK drive counts items one by one with <b>no type limit and no per-type cost</b>: a {a} DISK holds {b} items of any mix, a 256k DISK {c}. Items only, no fluids. The contents are saved with the world under the drive's ID, so a full drive stays light to carry. Use them for messy mixed storage, normal cells for bulk single items.",{a:A.disk.tiers[0],b:nL(A.disk.per_k),c:nL(256*A.disk.per_k)})}</p>
<p class="note">${T("Linggango makes them expensive: each DISK drive needs 2 Quartz Glass, 3 Quantum Entangled Singularities, 2 Netherite Ingots, a Nether Star and the matching AE2 storage component (pack recipe; the DISK Housing swaps the component for an empty slot), and they open at {a} (256k at {b}).",{a:act(6),b:act(7)})}</p>
<h3>${T("Wireless and curios")}</h3>
<p>${T("The wireless range is {a} blocks around a Wireless Access Point before boosters. These terminals can be worn in the Curio slot, so you can use them without holding them: {b}. The plain Wireless Terminal can't.",{a:A.wireless_range,b:A.curio.map(esc).join(", ")})}</p>
</section>
<section class="s" id="m-effects"><h2>${T("Effects")}</h2>
<p>${T("Status effects in the pack, what each one does, and the items whose own text names it. Food buffs are not an item: eating a meal that scores high enough gives them, as set in <code>linggango_tweaks-common.toml</code>.")}</p>
<div class="tw"><table><tr><th>${T("Effect")}</th><th>${T("What it does")}</th><th>${T("Given by")}</th></tr>${EFX_ROWS}</table></div></section>
<section class="s" id="m-stats"><h2>${T("Stats explained")}</h2>
<p>${T("About a dozen mods in the pack add combat stats, often with the same name and a different rule. This section follows one hit from your swing to the target's health bar and says at which step each stat counts. It is read from the code of the V6.6.6hf jars and the pack's own config files (the stat caps in <code>attributefix.json</code>, the Linggango Tweaks combat rules). Two warnings up front: several stats on the wiki do nothing in this pack, and some caps are much lower than the mods' own tooltips say.")}</p>
<nav class="mtabs" aria-label="${T("Stats explained")}"><a href="#mechanics" data-go="m-st-hit">${T("One hit")}</a><a href="#mechanics" data-go="m-st-armor">${T("Armor")}</a><a href="#mechanics" data-go="m-st-crit">${T("Crits")}</a><a href="#mechanics" data-go="m-st-dodge">${T("Dodge")}</a><a href="#mechanics" data-go="m-st-def">${T("Taking damage")}</a><a href="#mechanics" data-go="m-st-heal">${T("Healing")}</a><a href="#mechanics" data-go="m-st-roll">${T("Roll and parry")}</a><a href="#mechanics" data-go="m-st-type">${T("Damage types")}</a><a href="#mechanics" data-go="m-st-combo">${T("Status and combos")}</a><a href="#mechanics" data-go="m-st-magic">${T("Magic")}</a><a href="#mechanics" data-go="m-st-summon">${T("Summons")}</a></nav>

<h3 id="m-st-hit">${T("One hit, step by step")}</h3>
<p>${T("Every hit goes through these steps in order. A stat only changes the steps it belongs to, so the same \"+10%\" can be worth very different amounts.")}</p>
<div class="tw"><table><tr><th>${T("Step")}</th><th>${T("What happens")}</th><th>${T("Stats that count here")}</th></tr>
<tr><td>${T("<b>1. Swing</b>")}</td><td>${T("Weapon damage, scaled by how charged the attack is (vanilla attack cooldown).")}</td><td>${T("Attack Damage, Brutality's weapon and damage-type stats (Sword Damage, Slash Damage…), Food buffs")}</td></tr>
<tr><td>${T("<b>2. Melee crit</b>")}</td><td>${T("Decided once per swing. Melee only.")}</td><td>${T("Brutality Critical Strike Chance / Damage, plus small add-ons (see Crits)")}</td></tr>
<tr><td>${T("<b>3. Dodge</b>")}</td><td>${T("The target gets its chances to avoid the hit completely.")}</td><td>${T("Dodge Chance (three different ones), roll and parry")}</td></tr>
<tr><td>${T("<b>4. Bonus stage</b>")}</td><td>${T("Multipliers on the hit before armor. Order between mods does not matter here: they multiply.")}</td><td>${T("Apothic Critical Chance / Damage, damage affinity, Exposed, Perfect Hit, roll counters, Damage Taken, Summon Damage")}</td></tr>
<tr><td>${T("<b>5. Hit soft cap</b>")}</td><td>${T("How much step 4 grew your hit is measured. Up to ×3 it stays; past ×3 only the square root of the extra counts (×10 lands as ×5.5). Your summons' hits are exempt.")}</td><td>${T("Everything in step 4")}</td></tr>
<tr><td>${T("<b>6. Armor</b>")}</td><td>${T("The target's armor takes its share (formula below).")}</td><td>${T("Armor, Armor Penetration, Armor Shred, Armor Pierce, Lethality")}</td></tr>
<tr><td>${T("<b>7. Resistance, Protection</b>")}</td><td>${T("The Resistance effect, then Protection enchantments.")}</td><td>${T("Resistance levels, Protection, Protection Pierce / Shred")}</td></tr>
<tr><td>${T("<b>8. Floor and cap</b>")}</td><td>${T("Players only, and only for hits from something: at least 13% of the hit always lands, and no single hit takes more than half your max health.")}</td><td>${T("Max Health (moves the cap)")}</td></tr>
<tr><td>${T("<b>9. Healing from the hit</b>")}</td><td>${T("Lifesteal-type stats heal the attacker. All of it together is capped at 10% of max health per tick.")}</td><td>${T("Lifesteal, Omnivamp, Life Steal, Overheal, Healing Received")}</td></tr>
</table></div>
<p class="note">${T("Bosses on the Nightmare Altar roster also have an intake ceiling: they lose at most 1/30 of their max health per second (40–50 s for Sanghor, Zoranth Newborn and Nyxaris), banked up to 3 s, until you have beaten them once. Past that point more damage buys nothing.")}</p>

<h3 id="m-st-armor">${T("Armor: how much gets through")}</h3>
<p>${T("Apothic Attributes replaces vanilla armor. A hit keeps <b>A / (A + armor)</b> of its damage, where A is 10 for hits under 20 and 10 + (hit − 20) / 2 above. Armor has no cap, and big hits go through it more easily.")}</p>
<div class="tw"><table><tr><th>${T("Target armor")}</th><th>${T("10 damage hit")}</th><th>${T("50 damage hit")}</th><th>${T("200 damage hit")}</th></tr>
<tr><td>10</td><td>${T("50% lands")}</td><td>71%</td><td>91%</td></tr>
<tr><td>20</td><td>33%</td><td>56%</td><td>83%</td></tr>
<tr><td>50</td><td>17%</td><td>33%</td><td>67%</td></tr>
<tr><td>100</td><td>9%</td><td>20%</td><td>50%</td></tr>
<tr><td>200</td><td>5%</td><td>11%</td><td>33%</td></tr>
<tr><td>400</td><td>2%</td><td>6%</td><td>20%</td></tr>
</table></div>
<p>${T("<b>Armor Toughness</b> does not reduce damage in this formula. Its only job is to blunt Armor Shred and Armor Pierce used against you: 2% per point, up to 60% at 30 toughness. Mobs rarely have either, so for a player toughness is almost dead weight.")}</p>
<h4>${T("Getting through armor")}</h4>
<p>${T("On your hits, the stats below are worked out in this order: Armor Penetration, then Shred, then Pierce, then Lethality. A small pack mod (Lethality Guard) takes over the armor step whenever the attacker has any of these four, so they all work together and armor never goes below zero.")}</p>
<div class="tw"><table><tr><th>${T("Stat on the wiki")}</th><th>${T("Mod")}</th><th>${T("Kind")}</th><th>${T("What it does")}</th></tr>
<tr><td><b>Armor Penetration</b></td><td>${T("Brutality")}</td><td>${T("Percent")}</td><td>${T("Ignores that share of the target's armor: +50% means the target counts with half its armor. Capped at 95% by the pack.")}</td></tr>
<tr><td><b>Armor Shred</b></td><td>${T("Apothic")}</td><td>${T("Percent")}</td><td>${T("Removes another share of what is left, weakened by the target's toughness.")}</td></tr>
<tr><td><b>Armor Pierce</b></td><td>${T("Apothic")}</td><td>${T("Flat")}</td><td>${T("Subtracts armor points, also weakened by toughness. TerraCurio's \"armor pass\" items give this stat.")}</td></tr>
<tr><td><b>Lethality</b></td><td>${T("Brutality")}</td><td>${T("Flat")}</td><td>${T("Subtracts armor points last. <b>Each point past zero armor becomes +10% damage</b> (Lethality Guard), so it is strongest against lightly armored or unarmored targets.")}</td></tr>
<tr><td>${T("Armor pierce")}</td><td>${T("Iron's Lib")}</td><td>${T("Flat")}</td><td>${T("<b>Does nothing on your hits</b>: it hooks a part of the armor code that Brutality skips for every player hit. Mobs with it still use it on you.")}</td></tr>
<tr><td>${T("Needle armor penetration")}</td><td>${T("Goety Revelation")}</td><td>${T("Recovery")}</td><td>${T("Gives back a share of what armor took. Same problem as Iron's: skipped on player hits.")}</td></tr>
<tr><td>${T("Enchantment piercing")}</td><td>${T("Goety Revelation")}</td><td>${T("Recovery")}</td><td>${T("Gives back a share of what Protection enchantments took (damage = after + (before − after) × value). The Protection step is not skipped on player hits, so this one can work.")}</td></tr>
<tr><td>${T("Protection Pierce / Shred")}</td><td>${T("Apothic")}</td><td>${T("Flat / Percent")}</td><td>${T("The same as Armor Pierce / Shred, for the target's Protection points.")}</td></tr>
</table></div>
<div class="tw"><table><tr><th>${T("Example")}</th><th>${T("Nothing")}</th><th>${T("+50% Armor Penetration")}</th><th>${T("10 Lethality")}</th><th>${T("Both")}</th></tr>
<tr><td>${T("50 damage into a Keeper with 100 armor")}</td><td>10.0</td><td>16.7</td><td>10.9</td><td>19.2</td></tr>
<tr><td>${T("10 damage into a mob with 4 armor")}</td><td>7.1</td><td>8.3</td><td>16.0</td><td>18.0</td></tr>
</table></div>
<p class="note">${T("Penetration is the stat against heavy armor, Lethality against light armor. Against the 4-armor mob, 10 Lethality leaves 6 points past zero, worth +60%.")}</p>

<h3 id="m-st-crit">${T("Crits")}</h3>
<p>${T("There are two crit systems on top of each other, and they multiply: a melee crit decided at the swing, then the Apothic crit, which rolls on every hit you own.")}</p>
<h4>${T("The melee crit (Brutality decides)")}</h4>
<p>${T("Brutality's <b>Critical Strike Chance</b> is the gate for every melee crit. Your swing crits when it is charged over 90% and this roll succeeds. Jumping does not matter, and a jump without a successful roll is <b>not</b> a crit any more. The base chance is 0%, so with no crit gear, jump crits are gone. A crit deals <b>Critical Strike Damage</b>: base ×1.4, capped at ×3 by the pack. Most armor in the pack carries a little of it (+0.06 to +0.15 a piece).")}</p>
<div class="tw"><table><tr><th>${T("Stat on the wiki")}</th><th>${T("Mod")}</th><th>${T("What it does to melee crits")}</th></tr>
<tr><td><b>Critical Strike Chance</b></td><td>${T("Brutality")}</td><td>${T("The roll above. Base 0%.")}</td></tr>
<tr><td><b>Critical Strike Damage</b></td><td>${T("Brutality")}</td><td>${T("Sets the crit multiplier. Base ×1.4, cap ×3. Fuzzy Dice: a second roll doubles it.")}</td></tr>
<tr><td>${T("Crit damage")}</td><td>${T("Iron's Lib")}</td><td>${T("Adds to the multiplier (+0.15 turns ×1.4 into ×1.55). It runs at the same step as Brutality, so if it goes first, Brutality overwrites it. Not reliable.")}</td></tr>
<tr><td>${T("Weapon crit rate / damage")}</td><td>${T("L2 (l2damagetracker)")}</td><td>${T("Brutality's gate cancels or overwrites it on melee. It still works on fully drawn arrows (×1.5 at base crit damage).")}</td></tr>
<tr><td>${T("Chaos / Vex / Allay's Wing")}</td><td>${T("Armageddon (Linggango Fixes)")}</td><td>${T("+0.35 / +0.25 / +0.18 added to every melee crit's multiplier, after everything else.")}</td></tr>
<tr><td>${T("Perfect Hit")}</td><td>${T("Linggango")}</td><td>${T("Not a crit stat: any hit while falling has 5% to deal ×1.5 more (and huge knockback), at most once every 30 s.")}</td></tr>
</table></div>
<h4>${T("The Apothic crit (every hit)")}</h4>
<p>${T("<b>Critical Chance</b> and <b>Critical Damage</b> from Apothic Attributes roll again at the bonus stage, on every hit where you are the attacker: melee, arrows and spells. Base 5% for ×1.5, and every mob has the same base 5% against you. TerraCurio's \"critical chance\" items (Destroyer Emblem, Celestial Stone…) give this stat. Above 100% it can crit more than once: each extra crit has the chance that is left over and multiplies by the crit damage ×0.85.")}</p>
<p class="note">${T("Example: a 20 damage swing that wins both rolls: ×1.4 (Brutality) = 28, then ×1.5 (Apothic) = 42. Only the Apothic part counts toward the ×3 soft cap.")}</p>
<div class="tw"><table><tr><th>${T("Other crits")}</th><th>${T("Mod")}</th><th>${T("Where it applies")}</th></tr>
<tr><td><b>Spell crit chance / damage</b></td><td>${T("GTBCS")}</td><td>${T("Iron's Spells damage only. Base 0% chance and ×1.0 damage, so you need both stats for it to do anything.")}</td></tr>
<tr><td><b>Bow crit chance</b></td><td>${T("Too Many Bows")}</td><td>${T("Arrows from that mod's bows only, with each bow's own multiplier.")}</td></tr>
<tr><td>${T("Reforge crit")}</td><td>${T("Linggango (Reforging Table)")}</td><td>${T("×1.5 on swings that are not jumps, and a chance at double base damage on arrows. On melee it is cancelled when Brutality's roll fails, unless it happens to run later. The order is not fixed.")}</td></tr>
</table></div>

<h3 id="m-st-dodge">${T("Dodge")}</h3>
<p>${T("Three mods have a Dodge Chance and each rolls separately. A hit has to get past all of them, so they combine as 1 − (1 − a)(1 − b): 50% and 40% avoid 70% of hits.")}</p>
<div class="tw"><table><tr><th>${T("Stat on the wiki")}</th><th>${T("Mod")}</th><th>${T("Cap in the pack")}</th><th>${T("What it does")}</th></tr>
<tr><td>${T("<b>Dodge Chance</b> (anklets…)")}</td><td>${T("Brutality")}</td><td><b>50%</b></td><td>${T("Any hit. After a dodge it rests for half a second. Players only.")}</td></tr>
<tr><td>${T("<b>Dodge Chance</b> (Master Ninja Gear…)")}</td><td>${T("Apothic")}</td><td><b>40%</b></td><td>${T("Only melee from within reach, and projectiles. Hits in the same tick share one roll. TerraCurio's dodge items give this stat.")}</td></tr>
<tr><td>${T("Dodge chance")}</td><td>${T("Iron's Lib")}</td><td>${T("none")}</td><td>${T("Any hit; a dodge also gives 1 s of invulnerability.")}</td></tr>
</table></div>
<p class="note">${T("The mods' tooltips say up to 95% (Brutality) and 100% (Apothic); the pack's attributefix config lowers them to 50% and 40%. Stacking past the cap does nothing. A dodge cancels the hit outright, so the 13% damage floor does not apply to it.")}</p>

<h3 id="m-st-def">${T("Taking damage")}</h3>
<div class="tw"><table><tr><th>${T("Stat or rule")}</th><th>${T("Mod")}</th><th>${T("What it does")}</th></tr>
<tr><td><b>Damage Taken</b></td><td>${T("Brutality")}</td><td>${T("Multiplies the damage you take, at the bonus stage. Many armor pieces have −5%: a full set at −5% each takes ×0.8. Because it works before the floor is measured, it can push a hit below 13%.")}</td></tr>
<tr><td><b>Armor</b></td><td>${T("vanilla, Apothic formula")}</td><td>${T("See the table above. Never below the 13% floor on hits from something.")}</td></tr>
<tr><td>${T("<b>Resistance</b> (effect)")}</td><td>${T("Linggango Fixes")}</td><td>${T("Rescaled: I 20%, II 24%, III 29%, IV 33%, V 38%, VI 42%, VII 47%, VIII 51%, IX 56%, X 60%, then only +0.04% a level. Vanilla Resistance V would make you immune; here it is 38%.")}</td></tr>
<tr><td>${T("<b>Protection</b> (enchantments)")}</td><td>${T("Apothic formula")}</td><td>${T("2.5% per Protection point, up to 85% at 34 points.")}</td></tr>
<tr><td>${T("<b>Magic resist</b> (all, or one school)")}</td><td>${T("Iron's Spells")}</td><td>${T("Spell damage taken × (2 − resist). Past +50% it softens: +100% resist blocks 75%, never 100%.")}</td></tr>
<tr><td>${T("Damage floor")}</td><td>${T("Linggango")}</td><td>${T("At least 13% of a hit always lands after armor, Resistance, Protection and absorption. Reductions at the bonus stage (Damage Taken, some accessories) count before the floor is set.")}</td></tr>
<tr><td>${T("Hit cap")}</td><td>${T("Linggango")}</td><td>${T("No single hit from something takes more than half your max health. Falls, lava and drowning are not floored or capped.")}</td></tr>
<tr><td><b>Knockback Resistance</b></td><td>${T("vanilla")}</td><td>${T("Share of knockback ignored, capped at 100%.")}</td></tr>
</table></div>

<h3 id="m-st-heal">${T("Healing from damage")}</h3>
<div class="tw"><table><tr><th>${T("Stat on the wiki")}</th><th>${T("Mod")}</th><th>${T("Which hits")}</th><th>${T("Heals")}</th></tr>
<tr><td><b>Lifesteal</b></td><td>${T("Brutality")}</td><td>${T("Your melee swings only")}</td><td>${T("That share of the swing's damage, before armor")}</td></tr>
<tr><td><b>Omnivamp</b></td><td>${T("Brutality")}</td><td>${T("Every hit you own: melee, arrows, spells (not your summons)")}</td><td>${T("That share of the damage at the bonus stage, before armor")}</td></tr>
<tr><td><b>Life Steal</b></td><td>${T("Apothic")}</td><td>${T("Physical hits you land in person (melee; not arrows or spells)")}</td><td>${T("That share of the damage before armor, at most the target's remaining health")}</td></tr>
<tr><td><b>Overheal</b></td><td>${T("Apothic")}</td><td>${T("Same as Life Steal")}</td><td>${T("Absorption hearts instead of health, up to half your max health")}</td></tr>
<tr><td><b>Healing Received</b></td><td>${T("Apothic, Iron's Lib")}</td><td>${T("Every heal")}</td><td>${T("Multiplies it (two separate stats, both apply)")}</td></tr>
</table></div>
<p class="note">${T("Cap: in a tick where you dealt damage, all healing from hits together is at most 10% of your max health. Regeneration, food and potions are not capped.")}</p>

<h3 id="m-st-roll">${T("Roll and parry")}</h3>
<p>${T("Linggango's dodge roll (one press dashes, a second press rolls) and its parry have their own stats. During a roll's invulnerable ticks every hit is dodged.")}</p>
<div class="tw"><table><tr><th>${T("Stat on the wiki")}</th><th>${T("Base")}</th><th>${T("What it does")}</th></tr>
<tr><td><b>Roll Count</b></td><td>1</td><td>${T("Roll charges. Only whole numbers count: +0.5 does nothing until the total reaches 2.")}</td></tr>
<tr><td><b>Roll Recharge</b></td><td>20</td><td>${T("A charge comes back in 3.2 s after a roll and 1.3 s after a dash, × 20 / Roll Recharge. +10% (22) is 9% faster.")}</td></tr>
<tr><td><b>Roll Distance</b></td><td>${T("3 blocks")}</td><td>${T("How far a roll goes; a dash goes 70% of it.")}</td></tr>
<tr><td><b>Roll Top Speed</b></td><td>0.8</td><td>${T("Caps the speed you can build by chaining rolls and jumps.")}</td></tr>
<tr><td><b>Dodge Window</b></td><td>0</td><td>${T("Extra invulnerable ticks on rolls, dashes and air steps, rounded to the nearest tick (+0.5 is a whole tick), at most +4. A roll starts with 4 ticks, a dash with 3.")}</td></tr>
<tr><td><b>Dodge Damage</b></td><td>×1</td><td>${T("Multiplies the damage of the counter after a dodge, Bash and Flash.")}</td></tr>
<tr><td><b>Parry Window</b></td><td>${T("3 ticks")}</td><td>${T("Adds ticks to the parry window.")}</td></tr>
<tr><td><b>Parry Recovery</b></td><td>×1</td><td>${T("Divides the lockout after a missed parry.")}</td></tr>
<tr><td><b>Stun Duration</b></td><td>×1</td><td>${T("Multiplies how long parries, counters and Bash leave a mob stunned or Exposed. Exposed mobs take +20% damage from you.")}</td></tr>
<tr><td>${T("Technique Recharge / Range")}</td><td>×1</td><td>${T("Bash and Thunderclap: shorter cooldown, longer reach.")}</td></tr>
</table></div>
<p class="note">${T("A counter is the first hit within 1.5 s on the mob you just dodged: ×1.5, ×2 or ×2.5 by Mirror Step rank, times Dodge Damage, and it Exposes the mob.")}</p>

<h3 id="m-st-type">${T("Damage types and bonus damage")}</h3>
<div class="tw"><table><tr><th>${T("Stat on the wiki")}</th><th>${T("Mod")}</th><th>${T("What it does")}</th></tr>
<tr><td><b>Sword / Axe / Hammer / Scythe / Spear Damage</b> and <b>Slash / Pierce / Blunt Damage</b></td><td>${T("Brutality")}</td><td>${T("Added to your melee swing by the weapon you hold. Swords and axes take Slash, Brutality hammers Blunt, scythes Slash, spears and tridents Pierce, pickaxes and hoes Pierce, shovels Blunt. Flat values first, then percents. It goes by the item's class, not by the wiki's Damage chips.")}</td></tr>
<tr><td>${T("Damage affinity")}</td><td>${T("Linggango")}</td><td>${T("A mob weak to your damage type (the Damage chips on curio pages) takes ×1.25, or ×1.5 when the type is boosted (rain for lightning, unarmored targets for slash, airborne targets for pierce…). A resistance is ×0.75 or ×0.5. Elemental types also fill a status meter on the target, see Status and combos below.")}</td></tr>
<tr><td><b>Arrow Damage</b></td><td>${T("Apothic, Iron's Lib")}</td><td>${T("Multiplies arrow damage (Apothic when the arrow is shot, Iron's when it hits). TerraCurio's ranged damage items give the Apothic one.")}</td></tr>
<tr><td><b>Fire / Cold Damage</b></td><td>${T("Apothic")}</td><td>${T("An extra hit of that much on swings charged 55% or more; Fire also sets the target alight, Cold slows it.")}</td></tr>
<tr><td><b>Magic Damage</b></td><td>${T("TerraCurio")}</td><td>${T("Multiplies damage of the magic and indirect magic types.")}</td></tr>
<tr><td>${T("Food buffs")}</td><td>${T("Linggango")}</td><td>${T("Well Fed, Plenty Satisfied, Exquisitely Stuffed: +5 / 10 / 15% attack, spell, summon and arrow damage and movement speed.")}</td></tr>
</table></div>

<h3 id="m-st-combo">${T("Status and combos")}</h3>
<p class="lede">${T("Each hit fills a meter for its damage type on the target. When the meter is full it goes off into a status. Two elements that both reach half a meter on the same mob react as a combo.")}</p>
<div class="tw"><table><tr><th>${T("Element")}</th><th>${T("Boosted in or on")}</th><th>${T("Status when the meter goes off")}</th></tr>
<tr><td><b>Fire</b></td><td>${T("Hot places and the Nether")}</td><td>${T("<b>Scorched</b>: takes 15% more fire damage")}</td></tr>
<tr><td><b>Frost</b></td><td>${T("The cold, and frozen targets")}</td><td>${T("<b>Frostbite</b>: 40% slower and takes 15% more damage")}</td></tr>
<tr><td><b>Lightning</b></td><td>${T("Rain, and wet targets")}</td><td>${T("<b>Stunned</b>: can't move or attack")}</td></tr>
<tr><td><b>Holy</b></td><td>${T("Daylight")}</td><td>${T("<b>Judged</b>: glows and can't heal")}</td></tr>
<tr><td><b>Dark</b></td><td>${T("The dark")}</td><td>${T("<b>Dread</b>: deals 30% less damage. When it ends, a quarter of the damage taken during it hits again")}</td></tr>
<tr><td><b>Blood</b></td><td>${T("Wounded targets")}</td><td>${T("<b>Bleeding</b>: loses health every half second, twice as much while moving")}</td></tr>
<tr><td><b>Nature</b></td><td>${T("Poisoned targets")}</td><td>${T("<b>Rooted</b> (can't move, can still attack) and <b>Rot</b> (loses 1% of max health every second)")}</td></tr>
<tr><td><b>Arcane</b></td><td>${T("The End, and under a full moon")}</td><td>${T("<b>Unravelled</b>: takes 20% more elemental and magic damage")}</td></tr>
</table></div>
<p class="note">${T("Slash, pierce and blunt do not have a status of their own. The pack's config comment says they fill a meter too, but no effect name for them is in the pack's text, so none is listed here.")}</p>
<ul>
<li>${T("A normal elemental weapon fills its meter in about five hits.")}</li>
<li>${T("Slow weapons fill it faster per hit. A hit on a weakness fills it faster. A resistance never fills it.")}</li>
<li>${T("After a meter goes off, the next one takes longer, so one weapon can't keep a mob stunned.")}</li>
<li>${T("Bosses fill at half speed, take smaller bursts, and are never stunned or rooted.")}</li>
</ul>
<h4>${T("Combos")}</h4>
<div class="tw"><table><tr><th>${T("Pair")}</th><th>${T("Combo")}</th><th>${T("What it does")}</th></tr>
<tr><td>${T("Fire + Frost")}</td><td><b>Shatter</b></td><td>${T("An ice burst that hits the mob for a share of its max health. Bosses take half.")}</td></tr>
<tr><td>${T("Fire + Lightning")}</td><td><b>Detonation</b></td><td>${T("An explosion that hurts the mob and the mobs close to it.")}</td></tr>
<tr><td>${T("Frost + Lightning")}</td><td><b>Superconduct</b></td><td>${T("Applies Exposed and stuns the mob.")}</td></tr>
<tr><td>${T("Holy + Dark")}</td><td><b>Eclipse</b></td><td>${T("The mob ignores its resistances for a while.")}</td></tr>
<tr><td>${T("Blood + Nature")}</td><td><b>Fester</b></td><td>${T("Bleeding on the mob, and Rot on the mobs around it.")}</td></tr>
<tr><td>${T("Fire + Nature")}</td><td><b>Wildfire</b></td><td>${T("Scorched on the mobs around it.")}</td></tr>
<tr><td>${T("Frost + Blood")}</td><td><b>Crimson Ice</b></td><td>${T("A stun after a short delay.")}</td></tr>
<tr><td>${T("Lightning + Holy")}</td><td><b>Smite</b></td><td>${T("Judged on the mob.")}</td></tr>
<tr><td>${T("Dark + Blood")}</td><td><b>Bloodletting</b></td><td>${T("A heavy hit with blood particles.")}</td></tr>
<tr><td>${T("Frost + Nature")}</td><td><b>Frostbloom</b></td><td>${T("Rooted and Frostbite on the mobs around it.")}</td></tr>
<tr><td>${T("Lightning + Blood")}</td><td><b>Arterial Surge</b></td><td>${T("Bleeding on the mobs around it.")}</td></tr>
<tr><td>${T("Holy + Fire")}</td><td><b>Sunfire</b></td><td>${T("Hits the mobs around it, harder against undead.")}</td></tr>
<tr><td>${T("Arcane")}</td><td><b>Resonance</b></td><td>${T("A burst. With Iron's Spellbooks installed you also get 25 mana.")}</td></tr>
</table></div>
<h4>${T("When Arcane hits max")}</h4>
<p>${T("The Arcane meter goes off into <b>Unravelled</b>: the mob takes 20% more elemental and magic damage. Resonance is the Arcane combo: its burst gives you 25 mana, the mana from Iron's Spellbooks. The pack's own in-game text describes it as \"Arcane blows up around it and gives you mana back\".")}</p>

<h3 id="m-st-magic">${T("Magic (Iron's Spells)")}</h3>
<div class="tw"><table><tr><th>${T("Stat on the wiki")}</th><th>${T("What it does")}</th></tr>
<tr><td>${T("<b>Spell Power</b> and <b>School Power</b> (Fire, Ice, Ender…)")}</td><td>${T("Spell damage = the spell's base × Spell Power × that school's power. They multiply each other.")}</td></tr>
<tr><td><b>Cooldown Reduction</b></td><td>${T("Cooldown × (2 − value), softened past +50%: +25% → ×0.75, +50% → ×0.5, +100% → ×0.25, +200% → ×0.125. Imbued weapons also have half the cooldown (pack config).")}</td></tr>
<tr><td><b>Cast Time Reduction</b></td><td>${T("The same formula on cast time.")}</td></tr>
<tr><td><b>Max Mana</b>, <b>Mana Regen</b></td><td>${T("Every half second you get back 1% of max mana × Mana Regen: 100 mana refills in 50 s at base.")}</td></tr>
<tr><td><b>Casting Movement Speed</b></td><td>${T("How fast you can move while casting.")}</td></tr>
</table></div>

<h3 id="m-st-summon">${T("Summons")}</h3>
<div class="tw"><table><tr><th>${T("Stat on the wiki")}</th><th>${T("Mod")}</th><th>${T("What it does")}</th></tr>
<tr><td><b>Minion Damage</b></td><td>${T("Summonity")}</td><td>${T("Multiplies your minions' damage. Halved while you hold neither a summoning item nor a whip.")}</td></tr>
<tr><td><b>Summon Damage</b></td><td>${T("Iron's Spells")}</td><td>${T("Multiplies the damage of Iron's summons, and of Summonity minions too.")}</td></tr>
<tr><td>${T("Linggango's summon bridge")}</td><td>${T("Linggango")}</td><td>${T("Iron's and Goety summons you own also get your Minion Damage (no half-damage penalty), capped at ×2.")}</td></tr>
<tr><td><b>Minion Slots</b></td><td>${T("Summonity")}</td><td>${T("How many minions you can have (base 2). Each slot above 2 also adds one to every Goety summon limit.")}</td></tr>
<tr><td><b>Minion Range</b>, <b>Minion Attack Speed</b>, <b>Minion Movement Speed</b></td><td>${T("Summonity")}</td><td>${T("How far minions roam from you (base 20 blocks), how fast they attack and move.")}</td></tr>
<tr><td><b>Whip Damage / Range / Attack Speed</b></td><td>${T("Summonity")}</td><td>${T("Your whip's own hit, reach and speed.")}</td></tr>
</table></div>
<p class="note">${T("Your summons' hits skip the ×3 soft cap, and your crit and lifesteal stats do not apply to them. When a mob hurts you, idle Summonity minions turn on it.")}</p>
<p class="note">${T("Read from the V6.6.6hf jars (Brutality 0.8.5, Apothic Attributes 1.3.7, Lethality Guard 1.0.0, Iron's Lib 1.1.0, Iron's Spells 3.15.6, TerraCurio 0.1.13, Summonity 0.1.7, L2 Damage Tracker 0.3.8, Linggango Tweaks 7.47, Linggango Fixes 2.16) and the pack's config. Not yet measured in game. Where two mods act at the same step with no fixed order, the text says so. Stat names on curio pages have a dotted underline: {a}.",{a:NOHOVER?T("tap one to come back here"):T("hover one for the short version, or click it to come back here")})}</p>
</section>${wikiNav()}`;
 const q=el("rq"),t=el("rt"),kk=el("rk");let lim=RMAX;
 const f=more=>{if(more!==true)lim=RMAX;const v=q.value.trim().toLowerCase(),hit=G.rituals.filter(r=>rOk(r,v,t.value,kk.value));
  el("rtb").innerHTML=hit.slice(0,lim).map(rowH).join("");el("rn").textContent=T("{a} of {b}",{a:hit.length,b:G.rituals.length});
  el("rmore").innerHTML=hit.length>lim?`<button class="gmore" type="button">${T("Show {n} more",{n:Math.min(RMAX*5,hit.length-lim)})}</button>`:"";
  const b=el("rmore").firstChild;if(b)b.onclick=()=>{lim+=RMAX*5;f(true)}};
 [q,t,kk].forEach(x=>x.addEventListener("input",f));f();
 el("main").querySelectorAll(".mtabs [data-go]").forEach(a=>a.onclick=e=>{e.preventDefault();el(a.dataset.go).scrollIntoView({behavior:"smooth"})});
 {const sec=decodeURIComponent(location.hash).split("/")[1];if(sec)setTimeout(()=>{const n=el("m-"+sec);if(n)n.scrollIntoView()})}
}

const rIngr=x=>{const c={};x.gr.c.forEach(e=>{if(e&&e[0])c[e[0]]=(c[e[0]]||0)+1});return Object.entries(c)};
// "" unless some ingredient has its own recipe
function rtreeHtml(d,insp){
 if(!d.gr||!rIngr(d).some(([i])=>BYID[i]&&BYID[i].gr))return"";
 const seen=new Set();
 const node=(id,n,depth)=>{const x=BYID[id],sub=x&&x.gr&&depth<6&&!seen.has(id)?(seen.add(id),rIngr(x)):[];
  return `<li><span class="rn">${img(id)}${n>1?`<i>${n}×</i>`:""}${x?(insp?`<button class="lnk" data-insp="${esc(x.id)}" data-t="${x.ix}">${esc(TD(x.n))}</button>`:`<a href="#i${x.ix}" data-t="${x.ix}">${esc(TD(x.n))}</a>`)+`<small>${esc(actL(x.t))}</small>`:`<span>${esc(nmI(id.replace(/^#/,"")))}</span>`}</span>${sub.length?`<ul>${sub.map(([i,c])=>node(i,c,depth+1)).join("")}</ul>`:""}</li>`};
 return node(d.id,1,0)}
function recipeTree(d){
 const host=el("s-recipe"),tr=host&&rtreeHtml(d);if(!tr)return;
 host.insertAdjacentHTML("afterend",`<section class="s ip-sec" id="s-tree"><h2>${T("Recipe tree")}</h2><ul class="rtree">${tr}</ul><p class="note">${T("Curio ingredients open into their own recipes. Counts are per craft.")}</p></section>`)}

/* ---------- relic levels: per-level stats from the pack's Relics configs (RL, tools/relic_levels.py) ---------- */
var RLV={},RLMAX=Math.max(...Object.values(RL).map(r=>r.mx));
// 1 point per relic level (IRelicItem.addLevel), spent round-robin on unlocked abilities (lowest level first)
function rlAuto(r,l){const a=r.ab.map(()=>0);let p=0;
 for(let lv=1;lv<=l;lv++){p++;for(;;){let b=-1;r.ab.forEach((x,i)=>{if(x.rq<=lv&&a[i]<x.mx&&x.pt<=p&&(b<0||a[i]<a[b]))b=i});if(b<0)break;p-=r.ab[b].pt;a[b]++}}
 return a}
// keep a manual spend valid for level l: drop locked or over-max points, then refund from the last ability until it fits
function rlFit(r,l,a,q){const s={l,a:r.ab.map((x,i)=>x.rq>l?0:Math.max(0,Math.min(x.mx,a?a[i]|0:0))),q:rlStats(r).map((t,i)=>q&&q[i]>=0&&q[i]<=10?rlSnap(t,q[i]|0):-1)};
 for(let i=s.a.length-1;i>=0&&rlFree(r,s)<0;)s.a[i]?s.a[i]--:i--;return s}
function rlState(id){const r=RL[rlId(id)];return RLV[id]||(RLV[id]=rlFit(r,Math.min(st.rl,r.mx),null,rlStats(r).map(()=>st.rq)))}
function rlStats(r){return r.ab.flatMap(x=>x.st)}
function rlFree(r,s){return s.l-r.ab.reduce((n,x,i)=>n+s.a[i]*x.pt,0)}
const jround=v=>Math.floor(v+.5);
// IRelicItem.getAbilityValue: upgrade op, clamp to the config thresholds, round to 5 places
function rlVal(t,x,z){let v=t.op==="A"?x+t.m*z:t.op==="MB"?x+x*t.m*z:x*Math.pow(t.m+1,z);
 if(t.t[0]!=null)v=Math.max(v,t.t[0]);if(t.t[1]!=null)v=Math.min(v,t.t[1]);return jround(v*1e5)/1e5}
// the relic's own formatValue, as a stack program pulled from its bytecode; prints like Java's String.valueOf
function rlFmt(p,v){const [r,int]=rlNum(p,v);return int||!Number.isInteger(r)?String(r):r+".0"}
function rlNum(p,v){const k=[];let int=0;
 for(const o of p){if(typeof o==="number")k.push(o);else if(o==="v")k.push(v);else if(o==="I")int=1;else if(o==="D")int=0;
  else if(o==="R"){const n=k.pop(),f=Math.pow(10,n);k.push(jround(k.pop()*f)/f)}else if(o==="r")k.push(jround(k.pop()));else if(o==="i")k.push(Math.trunc(k.pop()));else if(o==="n")k.push(-k.pop());
  else{const b=k.pop(),a=k.pop();k.push(o==="+"?a+b:o==="-"?a-b:o==="*"?a*b:a/b)}}
 return [k.pop(),int]}
// star quality 0..10 (half stars), IRelicItem.getStatByQuality / getStatQuality / getAbilityQuality / getRelicQuality
function rlBase(t,q){return t.lo===t.hi?t.lo:jround((t.lo+(t.hi-t.lo)/10*q)*1e5)/1e5}
function rlSQ(t,b){const f=v=>rlNum(t.p,v)[0],lo=f(t.lo),hi=f(t.hi);return lo===hi?10:Math.max(0,Math.min(10,jround((f(b)-lo)/((hi-lo)/10))))}
// stars a stat can really show (formatted values are coarse, e.g. whole slots): quality -> first quality step that reaches it
function rlQMap(t){if(!t._q){t._q=new Map();for(let q=0;q<=10;q++){const g=rlSQ(t,rlBase(t,q));if(!t._q.has(g))t._q.set(g,q)}}return t._q}
function rlSnap(t,v){let b=-1;for(const g of rlQMap(t).keys())if(b<0||Math.abs(g-v)<Math.abs(b-v)||(Math.abs(g-v)===Math.abs(b-v)&&g<b))b=g;return b}
function rlBQ(t,v){return rlBase(t,rlQMap(t).get(rlSnap(t,v)))}
function rlRelicQ(r,q){if(q.some(v=>v<0))return -1;let o=0,n=r.ab.length,s=0;
 r.ab.forEach(x=>{const qs=x.st.map((t,j)=>rlSnap(t,q[o+j]));o+=x.st.length;if(x.nq)n--;else s+=qs.length?Math.trunc(qs.reduce((p,c)=>p+c,0)/qs.length):0});
 return n>0?Math.max(0,Math.min(10,Math.trunc(s/n))):0}
function rlStars(q){return `<span class="rst" title="${T("{n} of 5 stars",{n:q/2})}">${[0,1,2,3,4].map(i=>`<i class="${q>=2*i+2?"f":q>=2*i+1?"h":""}">★</i>`).join("")}</span>`}
const RLQO=(q,t)=>`${q===-2?`<option value="-2" selected>${T("mixed")}</option>`:""}<option value="-1"${q===-1?" selected":""}>${T("any roll")}</option>${(t?[...rlQMap(t).keys()].sort((a,b)=>a-b):[...Array(11).keys()]).map(v=>`<option value="${v}"${v===q?" selected":""}>${v/2} ★</option>`).join("")}`;
function rlStat(t,z,q){const a=(q>=0?[rlVal(t,rlBQ(t,q),z)]:[rlVal(t,t.lo,z),rlVal(t,t.hi,z)].sort((p,c)=>p-c)).map(v=>rlFmt(t.p,v));if(!a[1])a[1]=a[0];
 return TD(t.f).replace("%1$s",dec(a[0]===a[1]?a[0]:a[0]+" ~ "+a[1])).replace(/%%/g,"%").replace(/\.$/,"")}   // the format ("%1$s seconds.") is the mod's own text: said through TD, the number with the language's decimal sign
function rlXp(r,l){let t=0;for(let i=0;i<l;i++)t+=r.xp[0]+r.xp[1]*i;return t}
// tooltip: no spend is assumed, so each ability shows its base and the most this level could buy for it alone
function rlTip(d){const r=RL[d.id],l=Math.min(st.rl,r.mx),q=st.rq;
 return `<div class="trl"><b>${T("Relic level {l} / {max}",{l,max:r.mx})}</b> <small>${TN(l,"{n} point to spend","{n} points to spend")}${q>=0?" · "+T("every stat rolled near {n} ★",{n:q/2}):""}</small>${r.ab.map(x=>{if(x.rq>l)return `<p class="trlk">${ui("lock")} ${T("{name}: unlocks at level {lv}",{name:esc(TD(x.n)),lv:x.rq})}</p>`;
  const z=Math.min(x.mx,Math.floor(l/x.pt));return `<p><b>${esc(TD(x.n))}</b>${x.st.length?` <small>${z?T("up to {z}/{max}",{z,max:x.mx}):`0/${x.mx}`}</small>${x.st.map(t=>` · ${esc(TD(t.n))} ${esc(rlStat(t,0,q))}${z?` → ${esc(rlStat(t,z,q))}`:""}`).join("")}`:` <small>${T("passive")}</small>`}</p>`}).join("")}</div>`}
function rlBody(id,compact){const r=RL[rlId(id)],s=rlState(id),free=rlFree(r,s),rq=rlRelicQ(r,s.q);let o=0;
 return `<p class="rls"><b>${T("Level {l} / {max}",{l:s.l,max:r.mx})}</b> · <span class="${free?"rlf":""}">${TN(free,"{n} point free","{n} points free")}</span> <button class="ghost" data-rlx="auto">${T("Auto-spend")}</button>${s.a.some(Boolean)?` <button class="ghost" data-rlx="reset">${T("Reset")}</button>`:""}</p>
 ${s.q.length?`<p class="rlq"><label>${T("Roll quality")} <select data-rlq="all" aria-label="${T("Set every stat's stars")}">${RLQO(s.q.every(v=>v===s.q[0])?s.q[0]:-2)}</select></label> ${rq>=0?T("Relic {stars} {rating}",{stars:rlStars(rq),rating:`<small>${rq/2} / 5</small>`}):`<small>${T("pick stars to see the relic's rating")}</small>`}</p>`:""}
 ${r.ab.map((x,i)=>{const lock=x.rq>s.l;return `<div class="rla${lock?" lk":""}"><div class="rlah"><b>${esc(TD(x.n))}</b>${lock?`<span>${ui("lock")} ${T("unlocks at relic level {lv}",{lv:x.rq})}</span>`:!x.mx?`<span>${T("passive, no upgrades")}</span>`:`<span>${T("level {a} / {max}",{a:s.a[i],max:x.mx})}${x.pt>1?" · "+T("{n} points each",{n:x.pt}):""}</span><button class="chip" data-rlx="-${i}"${s.a[i]?"":" disabled"} aria-label="${esc(T("Lower {name}",{name:TD(x.n)}))}">−</button><button class="chip" data-rlx="+${i}"${s.a[i]<x.mx&&free>=x.pt?"":" disabled"} aria-label="${esc(T("Raise {name}",{name:TD(x.n)}))}">+</button>`}</div>${x.st.length?`<ul>${x.st.map(t=>{const j=o++;return `<li>${esc(TD(t.n))}: <b>${esc(rlStat(t,lock?0:s.a[i],s.q[j]))}</b>${t.lo===t.hi?"":` <select class="rlqs" data-rlq="${j}" aria-label="${esc(T("{name} stars",{name:TD(t.n)}))}">${RLQO(s.q[j],t)}</select>`}</li>`}).join("")}</ul>`:""}</div>`}).join("")}
 ${compact?"":`<p class="note">${T("Each relic level gives 1 point; spend them with + and −, or let Auto-spend spread them evenly. Values follow this pack's config and the mod's own rounding: a new relic rolls a random base inside the range (its stars: 0 ★ is the worst roll, 5 ★ the best; the relic's rating averages its abilities), upgrades scale it, and some stats have a hard cap.")} ${T("Reaching level {l} takes {xp} relic XP.",{l:s.l,xp:nL(rlXp(r,s.l))})}</p>`}`}
function rlPanel(id,compact){const r=RL[rlId(id)],s=rlState(id);
 return `<div class="rlp${compact?" sm":""}" data-rl="${esc(id)}"><label class="rlh">${T("Relic level")} <input type="range" min="0" max="${r.mx}" value="${s.l}" data-rlv aria-label="${T("Relic level")}"></label><div class="rlb">${rlBody(id,compact)}</div></div>`}
function rlDraw(p){p.querySelector(".rlb").innerHTML=rlBody(p.dataset.rl,p.classList.contains("sm"))}
document.addEventListener("input",e=>{const v=e.target.closest("[data-rlv]");if(!v)return;const p=v.closest("[data-rl]"),id=p.dataset.rl;RLV[id]=rlFit(RL[rlId(id)],+v.value,rlState(id).a,rlState(id).q);rlDraw(p)});
document.addEventListener("change",e=>{const g=e.target.closest("[data-rlq]");if(g){const p=g.closest("[data-rl]"),s=rlState(p.dataset.rl),v=+g.value;if(g.dataset.rlq==="all"){if(v>-2)s.q=rlStats(RL[rlId(p.dataset.rl)]).map(t=>v<0?-1:rlSnap(t,v))}else s.q[+g.dataset.rlq]=v;location.hash.startsWith("#build")?bSave():rlDraw(p);return}
 if(e.target.closest("[data-rlv]")&&location.hash.startsWith("#build"))bSave()});
document.addEventListener("click",e=>{const b=e.target.closest("[data-rlx]");if(!b)return;const p=b.closest("[data-rl]"),id=p.dataset.rl,r=RL[rlId(id)],s=rlState(id),x=b.dataset.rlx;
 if(x==="auto")s.a=rlAuto(r,s.l);else if(x==="reset")s.a=s.a.map(()=>0);else s.a[+x.slice(1)]+=x[0]==="+"?1:-1;
 location.hash.startsWith("#build")?bSave():rlDraw(p)});
// slots a levelled relic adds: the mod applies Math.round to the value; chosen roll, else the lowest (e.g. Leather Belt "Charms")
function rlSlots(id){const r=RL[rlId(id)],s=rlState(id),o={};
 let n=0;r.ab.forEach((x,i)=>{const o0=n;n+=x.st.length;if(x.rq<=s.l)x.st.forEach((t,j)=>{const k=/slots?/i.test(t.f)&&Object.keys(SLOT_BASE).find(k=>k.toLowerCase()===t.n.toLowerCase().replace(/s$/,""));if(k)o[k]=(o[k]||0)+jround(s.q[o0+j]>=0?rlVal(t,rlBQ(t,s.q[o0+j]),s.a[i]):Math.min(rlVal(t,t.lo,s.a[i]),rlVal(t,t.hi,s.a[i])))})});return o}

/* ---------- duplicates: what a second copy does, read from the mods' bytecode (tools/stacking.py) ---------- */
const SKL={y:N("Stacks"),p:N("Partly stacks"),n:N("Doesn't stack"),u:N("One per player")};
const SKW={u:N("The game won't let you equip a second copy."),s:N("Its stat bonus is tied to the slot it sits in, so each copy adds it again."),c:N("Its effect counts how many copies you wear."),
 f:N("Its stat bonus uses one fixed ID, so a second copy just replaces the first."),o:N("Its effect only checks whether one is worn.")};
const pct=v=>Math.round(v*100)+"%";
function skTag(id){const k=SK.i[id];return k?(k.s?`<span class="sk sk-${k.s}">${T(SKL[k.s])}</span>`:"")+(k.l?`<span class="sk sk-l">${esc(T("{set} ladder #{n}",{set:k.l[0],n:k.l[1]}))}</span>`:""):""}
function skLadderText(l){return T("{set} set, place {n}. Linggango lets only the best {set} curio you wear work in full; the next best keeps {f1} of its effect (upsides and costs alike), the third {f2}, and any more switch off.",{set:esc(l[0]),n:l[1],f1:pct(SK.f[0]),f2:pct(SK.f[1])})+(l[2]?" "+T("This one switches off completely as soon as a better {set} curio is worn.",{set:esc(l[0])}):"")+" "+T("A copy of the same curio doesn't outrank it.")}
function skSec(d){const k=SK.i[d.id];if(!k)return"";
 const lad=k.l?D.filter(x=>SK.i[x.id]&&SK.i[x.id].l&&SK.i[x.id].l[0]===k.l[0]).sort((a,b)=>SK.i[a.id].l[1]-SK.i[b.id].l[1]):[];
 return `${k.s?`<p><b class="sk sk-${k.s}">${T(SKL[k.s])}</b> ${[...k.w].map(c=>T(SKW[c])).join(" ")}</p>`:""}${k.l?`<p><b class="sk sk-l">${T("{set} ladder",{set:esc(k.l[0])})}</b> ${skLadderText(k.l)}</p>
 <ol class="sklad">${lad.map(x=>`<li${x===d?' class="me"':""}>${img(x.id)}<a href="#i${x.ix}" data-t="${x.ix}">${esc(TD(x.n))}</a>${SK.i[x.id].l[2]?` <small>${T("switches off when outranked")}</small>`:""}</li>`).join("")}</ol>`:""}
 <p class="note">${T("Read from the mods' code by a script: it looks at how each curio's bonuses are keyed and how its effects check what you wear. Effects coded in unusual ways can be missed.")}</p>`}
// linggango_tweaks AccessoryStacking.factorFor: share of its effect each worn ladder curio keeps
function skLadder(ids){const out={};
 ids.forEach(id=>{const l=SK.i[id]&&SK.i[id].l;if(!l)return;let n=0;
  ids.map(j=>SK.i[j]&&SK.i[j].l).filter(m=>m&&m[0]===l[0]&&m[1]<l[1]).sort((a,b)=>a[1]-b[1]).forEach(m=>{if(!(m[2]&&n))n++});
  out[id]=!n?1:l[2]?0:n===1?SK.f[0]:n===2?SK.f[1]:0});
 return out}

/* ---------- evolutions: More Relics "evolves from", Somake Spells spellbook tiers ---------- */
var EVO=null;
function evo(){if(EVO)return EVO;EVO={from:{},to:{}};const byN={};D.forEach(d=>byN[d.n.toLowerCase()]=d);
 D.forEach(d=>{let p=null;for(const s of d.src){const m=s.match(/evolves from ([^.]+)\./i);if(m)p=byN[m[1].trim().toLowerCase()]}
  if(!p&&d.m==="Somake Spells"){const m=d.n.match(/^(.*) (II|III)$/);if(m)p=byN[(m[2]==="II"?m[1]:m[1]+" II").toLowerCase()]}
  if(p&&p!==d){EVO.from[d.id]=p.id;(EVO.to[p.id]=EVO.to[p.id]||[]).push(d.id)}});return EVO}
function evoChain(id){const E=evo();let r=id;while(E.from[r])r=E.from[r];const out=[];const walk=x=>{out.push(x);(E.to[x]||[]).forEach(walk)};walk(r);return out}
function evoSec(d){const c=evoChain(d.id);if(c.length<2)return "";
 return `<ol class="evo">${c.map((id,i)=>{const x=BYID[id];return `${i?`<li class="evh">↓ <span>${fmt(x.src[0]||"")}</span></li>`:""}<li class="evs${id===d.id?" cur":""}">${img(id)}${id===d.id?`<b>${esc(TD(x.n))}</b>`:`<a href="#i${x.ix}" data-t="${x.ix}">${esc(TD(x.n))}</a>`}<small>${esc(actL(x.t))}</small></li>`}).join("")}</ol>`}

/* ---------- field search: free words plus mod:x slot:y stat:z … ---------- */
var SOFT=false,IDXSIG="",FQT=0,FQS=null,FHINT=false,FKEY="mod",QP={raw:null};
var QK={mod:"m",slot:"s",stat:"st",stats:"st",effect:"fx",fx:"fx",source:"src",src:"src",drop:"src",path:"p",act:"p",acts:"p",rarity:"r",role:"ro",type:"g",tag:"x",name:"n"};
var QOR={m:1,s:1,p:1,r:1,ro:1,g:1,x:1};
var QFIELDS=[["mod","Mod"],["slot","Slot"],["stat","Stat"],["effect","Effect"],["source","Source"],["path","Act"],["rarity","Power"],["role","Role"],["type","Craft or loot"],["tag","Element or mechanic"],["name","Name"]];
var QNAME={m:"Mod",s:"Slot",st:"Stat",fx:"Effect",src:"Source",p:"Act",r:"Power",ro:"Role",g:"Type",x:"Tag",n:"Name"};
/* lower case; in the translated languages also without accents (vi "ao choang" finds "Áo Choàng"): each non-ASCII letter becomes one letter, so positions in the text stay the same */
const fold=s=>{s=String(s).toLowerCase();return LANG==="en"?s:s.replace(/[^\x00-\x7f]/g,c=>c.normalize("NFD").replace(/[\u0300-\u036f]/g,"").replace(/đ/g,"d"))};
function qNorm(s){return fold(String(s||"").replace(/[–—]/g,"-"))}
const QTOK=/-?[a-z]+:"[^"]*"?|-?"[^"]*"?|\S+/gi;
function parseQ(q){const o={raw:q,t:[],k:{}};
 (q.match(QTOK)||[]).forEach(w=>{const raw=w;let neg=false;if(w[0]==="-"&&w.length>1){neg=true;w=w.slice(1)}
  const m=w.match(/^([a-z]+):(.*)$/i),k=m&&QK[m[1].toLowerCase()],v=qNorm((k?m[2]:w).replace(/"/g,"")).trim();if(!v)return;
  const e={v,neg,raw,k:k||""};k?(o.k[k]=o.k[k]||[]).push(e):o.t.push(e)});return o}
function qParsed(){if(QP.raw!==st.q)QP=parseQ(st.q);return QP}
function qTokens(){const P=qParsed();return [...P.t,...Object.values(P.k).flat()]}
const qName=k=>({m:T("Mod"),s:T("Slot"),st:T("Stat"),fx:T("Effect"),src:T("Source"),p:T("Act"),r:T("Power"),ro:T("Role"),g:T("Type"),x:T("Tag"),n:T("Name")})[k];
const qfLab=k=>({mod:T("Mod"),slot:T("Slot"),stat:T("Stat"),effect:T("Effect"),source:T("Source"),path:T("Act"),rarity:T("Power"),role:T("Role"),type:T("Craft or loot"),tag:T("Element or mechanic"),name:T("Name")})[k];
function qLabel(e){return (e.neg?T("not")+" ":"")+(e.k?qName(e.k)+": ":"“")+e.v+(e.k?"":"”")}
// remove exactly the clicked token: split the query the way parseQ does, so "ring" is not cut out of "slot:ring" or "swordsman"
const slotQ=v=>`slot:${/\s/.test(v)?`"${v}"`:v}`;
function qDrop(raw){const ws=st.q.match(QTOK)||[],i=ws.indexOf(raw);if(i>=0)ws.splice(i,1);return ws.join(" ")}
function qf(d){if(d._q)return d._q;const F=mf(d.m),tn=TD(d.n)!==d.n?" | "+TD(d.n):"";
 return d._q={n:qNorm(d.n+tn),m:qNorm(d.m+"|"+(F?F[2]:"")),s:qNorm(d.sl.join("|")),st:qNorm(d.st.join(" | ")),fx:qNorm(d.fx),src:qNorm(srcText(d)),
  p:qNorm(ACT[d.t][0]),pl:qNorm(actL(d.t)),r:qNorm(RN[d.r]+(isMust(d)?"|"+RN[d.br]:"")),ro:qNorm(d.ro.map(k=>ROLE[k]+(T(ROLE[k])!==ROLE[k]?"|"+T(ROLE[k]):"")).join("|")),g:qNorm(d.g),
  x:qNorm(d.mt.map(t=>t.slice(2)).join("|")),all:qNorm(d.n+tn+" "+d.fx+(fxT(d)!==d.fx?" "+fxT(d):"")+" "+srcText(d)+" "+d.m+" "+d.id+" "+d.st.join(" "))}}
function qHit(d,f,k,v){
 if(k==="p")return v===f.p||v===String(d.t)||v===f.pl||"act "+v===f.pl||"path "+v===f.pl||(f.p==="0-i"&&(v==="0"||v==="i"))||(v.length>2&&!/^[ivx]+$/.test(v)&&f.pl.includes(v));
 if(k==="r"||k==="ro"||k==="g")return f[k].split("|").some(x=>x.startsWith(v));
 return qHas(f[k],v)}
function qHas(s,v){if(!/^[a-z0-9]/.test(v))return s.includes(v);for(let i=s.indexOf(v);i>=0;i=s.indexOf(v,i+1))if(!i||!/[a-z0-9]/.test(s[i-1]))return true;return false}
function qMatch(d){if(!st.q)return true;const P=qParsed(),f=qf(d);
 for(const e of P.t)if(qHas(f.all,e.v)===e.neg)return false;
 for(const k in P.k){const es=P.k[k],pos=es.filter(e=>!e.neg);
  if(es.some(e=>e.neg&&qHit(d,f,k,e.v)))return false;
  if(pos.length&&!(QOR[k]?pos.some(e=>qHit(d,f,k,e.v)):pos.every(e=>qHit(d,f,k,e.v))))return false}
 return true}
function fOn(){return !!(st.c.length||st.r.length||st.x.length||st.g.length||st.nw||st.m||st.s||st.a!==""||st.q)}
function fSug(k){const u=new Set(),add=x=>x&&u.add(x);
 if(k==="mod")MODS.forEach(([m])=>add(m));else if(k==="slot")SLOTS.forEach(([s])=>add(s));else if(k==="path")ORDER.forEach(a=>add(ACT[a][0]));
 else if(k==="rarity")RN.forEach(add);else if(k==="role")Object.values(ROLE).forEach(add);else if(k==="type"){add("Craft");add("Loot")}
 else if(k==="tag")D.forEach(d=>d.mt.forEach(t=>add(t.slice(2))));else if(k==="stat")D.forEach(d=>statsOf(d).forEach(s=>add(s.k)));
 return [...u].sort((a,b)=>String(a).localeCompare(String(b)))}
function fbar(n,total){
 return `<div class="fbar" role="search"><div class="fbr"><input id="fq" type="search" autocomplete="off" spellcheck="false" name="pathq" placeholder="${T("Search, or filter: mod:terramity slot:ring stat:damage…")}" aria-label="${T("Search and filter curios")}" value="${esc(st.q)}"><span class="fn">${n===total?TN(total,"{n} curio","{n} curios"):T("{n} of {total}",{n,total})}</span></div>
<div class="fbr fadd"><select id="fk" aria-label="${T("Filter field")}">${QFIELDS.map(([k])=>`<option value="${k}"${k===FKEY?" selected":""}>${qfLab(k)}</option>`).join("")}</select><input id="fv" list="fvl" autocomplete="off" name="filterv" placeholder="${T("e.g. Terramity…")}" aria-label="${T("Filter value")}"><datalist id="fvl"></datalist><button class="chip" id="fgo">${T("Add filter")}</button><button class="ghost" id="fhelp" aria-expanded="${FHINT}">${T("How it works")}</button></div>
<p class="fhint" id="fhint"${FHINT?"":" hidden"}>${T(`Words search names, effects, stats and sources. Add <b>field:value</b> to narrow it down, e.g. <code>mod:terramity slot:ring stat:damage</code>. The same field twice means either one (<code>slot:ring slot:charm</code>); different fields must all match. Put <b>-</b> in front to exclude (<code>-mod:brutality</code>) and quotes around spaces (<code>stat:"attack speed"</code>). Fields: mod, slot, stat, effect, source, act, rarity, role, type, tag, name. Sidebar filters stack with these.`)}</p>
<details class="fadv"${st.rl?" open":""}><summary>${T("Relic levels in tooltips")}</summary><div class="fbr frl"><label for="frl">${T("Relic level")}</label><input id="frl" type="range" min="0" max="${RLMAX}" value="${Math.min(st.rl,RLMAX)}"><b id="frlv">${st.rl>=RLMAX?T("Max"):st.rl}</b><label class="frq">${T("Stars")} <select id="frq">${RLQO(st.rq)}</select></label><span class="fn">${T("{n} Relics and More Relics curios; each stops at its own max",{n:Object.keys(RL).length})}</span></div></details>
${activeBar()}</div>`}
function fbind(){const q=el("fq");if(!q)return;
 const rl=el("frl");rl.oninput=()=>{st.rl=+rl.value;el("frlv").textContent=st.rl>=RLMAX?T("Max"):st.rl;TIPC.clear();save()};
 el("frq").onchange=e=>{st.rq=+e.target.value;TIPC.clear();save()};
 q.oninput=()=>{clearTimeout(FQT);FQT=setTimeout(()=>{st.q=q.value.trim();el("q").value=st.q;FQS=[q.selectionStart,q.selectionEnd];refresh()},220)};
 const k=el("fk"),v=el("fv"),sug=()=>{el("fvl").innerHTML=fSug(k.value).map(x=>`<option value="${esc(x)}">`).join("")};
 k.onchange=()=>{FKEY=k.value;sug();v.focus()};sug();
 const add=()=>{const val=v.value.trim().replace(/"/g,"");if(!val)return;st.q=(st.q+" "+k.value+":"+(/\s/.test(val)?`"${val}"`:val)).trim();el("q").value=st.q;refresh()};
 el("fgo").onclick=add;v.onkeydown=e=>{if(e.key==="Enter"){e.preventDefault();add()}};
 el("fhelp").onclick=()=>{FHINT=!FHINT;el("fhint").hidden=!FHINT;el("fhelp").setAttribute("aria-expanded",FHINT)};
 if(FQS){q.focus({preventScroll:true});q.setSelectionRange(FQS[0],FQS[1]);FQS=null}}


"use strict";
/* ---------- constants ---------- */
const ACT={"-1":["L2","L2 Artifacts: drops from L2 Hostility mobs by level","#a98bd0","L2 Artifacts"],0:["0–I","Sticks and Stones: before Iron Colossus","#9fb3a6"],2:["II","after Iron Colossus","#c7ccd1"],3:["III","after the Goblin Lord","#d9bd5e"],4:["IV","after Arion","#62b882"],5:["V","after Eldorath: the Nether opens","#df8a62"],6:["VI","after Zoranth the Forgotten","#9b8bd9"],6.1:["Warden","after the Warden","#3fa79c","Warden Act"],6.2:["Wither","after the Wither","#a7a3b8","Wither Act"],6.3:["Dragon","after the Ender Dragon: Hardmode ×2.1","#ab7fd0","Ender Dragon Act"],7:["VII","after the Elvenite Paladin","#76c4a8"],8:["VIII","after Vaedric","#a67fcc"],9:["IX","after The Discord, the Calamitous Keeper","#e8875f"],10:["X","after Sanghor","#cf5c56"],11:["XI","after Zoranth Newborn","#e0a352"],12:["XII","after Nyxaris, the Shadow Keeper","#8c80d4"]};
const ORDER=[0,2,3,4,5,6,6.3,7,8,9,10,11,12];
const VBOSS={6.3:"dragon"};
/* the Warden and the Wither are optional: their curios and gear sit in Act VI, and they show as side bosses there */
const SIDEV={warden:6,wither:6};
{const f=v=>v===6.1||v===6.2?6:v;D.forEach(d=>{if(d.t===6.1||d.t===6.2)d.vb=d.t===6.1?"warden":"wither";d.t=f(d.t);d.a=f(d.a);if(d.gk)d.gk=f(d.gk)});
 if(typeof GE!=="undefined")GE.forEach(g=>{g.a=f(g.a);g.ga=f(g.ga);if(g.mg)g.mg[0]=f(g.mg[0])});if(typeof GS!=="undefined")GS.forEach(g=>{g.a=f(g.a)})}
const UNL={0:"",2:"Iron Colossus",3:"the Goblin Lord",4:"Arion",5:"Eldorath",6:"Zoranth the Forgotten",6.1:"the Warden",6.2:"the Wither",6.3:"the Ender Dragon",7:"the Elvenite Paladin",8:"Vaedric",9:"The Discord",10:"Sanghor",11:"Zoranth Newborn",12:"Nyxaris","-1":""};
const GK={2:"Iron Colossus",3:"Goblin Lord",4:"Arion",5:"Eldorath",6:"Zoranth the Forgotten",7:"Elvenite Paladin",8:"Vaedric",9:"The Discord",10:"Sanghor",11:"Zoranth Newborn",12:"Nyxaris"};
const ROLE={ME:"Melee",RA:"Ranged",MA:"Mage",SU:"Summon",MO:"Movement",HE:"Health",TA:"Tank",UT:"Utility"};
const ROLE_C={ME:"#d9534f",RA:"#e0a030",MA:"#4f7fe0",SU:"#2fb5a8",MO:"#47b05a",HE:"#e05a8a",TA:"#8a8f99",UT:"#9a6ad0"};
const RN=["Common","Uncommon","Rare","Epic","Legendary","Mythic","Must-Have ★"];
const RNS=[0,1,2,3,4,5,6].reverse();
const RC=["#a9a7ad","#c9b45a","#5fb3a7","#9a7bcf","#d07f3c","#ec6b5f","#e3b440"];
const TAGN={relic:"Relic formula",pack:"Pack setting",tooltip:"In-game tooltip",code:"Mod default",auto:"Read from the mod"};
const TAGT={relic:"Relics-mod formula with the pack config applied",pack:"Value set in the Linggango pack config",tooltip:"Text shown on the item in game",code:"Default value inside the mod",auto:"Read automatically from the mod: check it against the in-game tooltip"};
const MFAM=[["calam",/^(Wizard Terra|Curios of Calamity)/,"CALAMITY"],["terra",/^Terramity/,"TERRAMITY"],["brut",/^Brutality/,"BRUTALITY"],["leth",/^Lethality/,"LETHALITY"],["summ",/^Summonity/,"SUMMONITY"],["enigma",/^Enigmatic/,"Enigmatic"],["armag",/^Armageddon/,"ARMAGEDDON"],["celest",/^Celestial/,"CELESTIAL"],["goety",/^(Goety|Covenant)/,"Goety"],["blood",/^(Blood Magic|Animus)/,"Blood Magic"],["l2",/^(L2|Fallen Traits)/,"L2 HOSTILITY"],["spell",/^(Iron's|T\.O Magic|Somake|Ars |Ars$|Adam's|Caster|GTBC|Nature's Aura|Mahou)/,"ARCANE"],["tech",/^(Powah|Thermal|AE2|Sophisticated|Mekanism|Create|Applied)/,"TECH"],["relic",/./,"Relic"]];
const mf=m=>MFAM.find(f=>f[1].test(m||""));
const MINFO={"Terramity": ["Aurukel", "https://www.curseforge.com/minecraft/mc-mods/terramity", "A Terraria-inspired Forge mod adding bosses, weapons, structures and a large set of curios, with a Patchouli guidebook as an in-game wiki.", "The backbone of the pack: most Keepers and gate tiers (Elvenite, Voiderite, Helionite…) come from here. Terramity pickaxes carry mining power 5–7."], "Brutality": ["gooMC", "https://www.curseforge.com/minecraft/mc-mods/brutality-a-terramity-addon", "A Terramity addon with weapons and curios drawn from Terraria and League of Legends, a magic system built on Terramity materials, and a Throwing class.", "Brutality charms stack stats (attack speed, crit, armor penetration). Anklets add Brutality's own Dodge Chance, so on-dodge effects fire right away."], "Terra Curio": ["Westernat233", "https://www.curseforge.com/minecraft/mc-mods/terra-curio", "Terraria accessories recreated in Minecraft.", "Mob drops need a direct player kill; Looting does not help. 158 items: 80 craftable (67 at the Workshop)."], "Armageddon": ["choupicul", "https://www.curseforge.com/minecraft/mc-mods/armageddon", "An RPG adventure mod adding bosses, ores, weapons and a Hardmode.", "Home of the Elvenite Paladin, Eldorath and Hardmode (×2.1 mob health and damage after the Ender Dragon)."], "Goety": ["Polarice3", "https://www.curseforge.com/minecraft/mc-mods/goety", "A dark-arts mod: necromancy, rituals and spells powered by souls. Highly configurable.", "Goety rituals are the route to the Potion of Transformation; the Luck brew raises the Luck effect level."], "Sanctified Legacy": ["llenzzz", "https://www.curseforge.com/minecraft/mc-mods/sanctified-legacy", "An Iron's Spells addon (its jar and mod id are still covenant_of_the_seven), built around seven rings, each with its own mana system.", "Brightest Scroll is a plain item; worn in a Scroll slot it does nothing."], "More Artifacts": ["gobies", "https://www.curseforge.com/minecraft/mc-mods/more-artifacts", "More curios, heavily inspired by Terraria.", "KubeJS removes the recipes for Ankh Shield, Ankh Charm and Obsidian Shield; only the Terra Curio versions can be crafted."], "Enigmatic Legacy": ["Aizistral", "https://www.curseforge.com/minecraft/mc-mods/enigmatic-legacy", "A broad mod with weapons, Etherium armor, potions and its own curio types such as Scrolls and Spellstones; Spellstones are dungeon-only finds.", "The Spellstones chapter of the quest book holds exactly 13."], "Unique Accessories": ["Genzyuro", "https://www.curseforge.com/minecraft/mc-mods/unique-accessories", "Unusual accessories dropped by mobs or found in structure chests.", ""], "L2 Hostility": ["lcy0x1", "https://www.curseforge.com/minecraft/mc-mods/l2hostility", "Makes mobs stronger by giving them special traits.", "A Looting Charm must be worn in a curio slot to unlock trait drops. Linggango Tweaks adds trait hunting: Hostile Remnant → Core → Trait Lure."], "Artifacts": ["ochotonida", "https://www.curseforge.com/minecraft/mc-mods/artifacts", "Uncraftable treasures found in vanilla structure chests, through archaeology, or rarely worn by mobs.", ""], "Iron's Spells": ["Iron431", "https://www.curseforge.com/minecraft/mc-mods/irons-spells-n-spellbooks", "A classic RPG magic mod: spellbooks, scrolls, hostile wizards and structures.", ""], "T.O Magic 'n Extras": ["GameTechBC", "https://www.curseforge.com/minecraft/mc-mods/to-tweaks-irons-spells", "An Iron's Spells addon adding spells, bosses, evolving weapons and a Talent curio slot, integrated with Cataclysm and Alex's Caves.", ""]};
const minfo=m=>MINFO[m]||MINFO[Object.keys(MINFO).find(k=>m.startsWith(k+" ")||m===k)]||null;

/* ---------- helpers ---------- */
const el=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const enc=encodeURIComponent;
const RM=matchMedia("(prefers-reduced-motion:reduce)").matches;
/* touch screens: the same query as v5.css's (hover:none) rule that hides #tip, so the copy never says "hover" where no tooltip opens */
const NOHOVER=matchMedia("(hover:none)").matches;
const ICU={};
/* an icon as a data: URL. Decoding the base64 into a Blob in script cost ~0.5 s on the Curios page; the browser decodes data: URLs itself, off the main script */
const icu=id=>{let u=ICU[id];if(!u&&IC[id])u=ICU[id]="data:image/png;base64,"+IC[id];return u};
let GEK=null;
const phGlyph=id=>{if(!GEK&&typeof GE!=="undefined"){GEK={};GE.forEach(g=>GEK[g.id]=g)}const g=GEK&&GEK[id];if(!g)return null;return g.k==="armor"?({HELMET:ui("helmet",1),CHESTPLATE:ui("chest",1),LEGGINGS:ui("legs",1),BOOTS:ui("boots",1)}[g.sl]||ui("chest",1)):ui("sword",1)};
const img=(id,cls)=>{if(/^forge:(partial_)?nbt$|textures\//.test(id))return "";if(IC[id])return `<img alt="" decoding="async" src="${icu(id)}"${cls?` class="${cls}"`:""}>`;const gl=phGlyph(id);return gl?`<span class="ph gph" title="No flat icon: this item only has a 3D model in its mod">${gl}</span>`:`<span class="ph" data-id="${esc(id)}">${esc((NM[id]||id.split(":")[1]||"?").slice(0,2))}</span>`};
const nmI=id=>NM[id]||id.split(":")[1].replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase());
const ACTN={"-1":"L2 Artifacts",0:"Iron Colossus",2:"The Goblin Lord",3:"Arion",4:"Eldorath",5:"Zoranth the Forgotten",6:"The Ender Dragon",6.3:"The Elvenite Paladin",7:"Vaedric",8:"The Discord",9:"Sanghor",10:"Zoranth Newborn",11:"Nyxaris"};
const actL=a=>ACT[a][3]?T(ACT[a][3]):T("Act {n}",{n:ACT[a][0]});
const actF=a=>ACTN[a]&&a!=-1?T("{act} · next: {boss}",{act:actL(a),boss:T(ACTN[a])}):actL(a);
const count=xs=>xs.reduce((s,d)=>s+d.k,0);
const byRank=xs=>[...xs].sort((a,b)=>b.r-a.r||b.sc-a.sc);
const CT='<i class="ct" title="Ingredient: used to craft another curio" aria-label="Crafting ingredient"></i>';
if(UI.ctable)document.documentElement.style.setProperty("--ctimg",`url(${URL.createObjectURL(new Blob([Uint8Array.from(atob(UI.ctable),c=>c.charCodeAt(0))],{type:"image/png"}))})`);

/* ---------- art: attribute icons, boss emblems, 3D heads ---------- */
{const st=document.createElement("style");st.textContent=":root{"+Object.keys(VA).map(k=>`--v-${k}:url(data:image/png;base64,${VA[k]})`).join(";")+(typeof ROOMT!=="undefined"?";"+Object.keys(ROOMT).map(k=>`--rt-${k}:url(data:image/png;base64,${ROOMT[k]})`).join(";"):"")+"}";document.head.appendChild(st)}
const AIR=[[/armor toughness|\btoughness\b/i,"fx_resistance"],[/🦺|\barmou?r\b/i,"gui_armor"],[/💥|\bcrit(?:ical)?(?: hit)? (?:chance|rate)\b/i,"p_critical_hit"],[/🧨|\bcrit(?:ical)? damage\b|\bcrits?\b/i,"p_enchanted_hit"],
 [/attack speed/i,"fx_haste"],[/\b(?:attack|melee|bonus|extra|magic|ranged|arrow|spell) damage\b|\bdamage dealt\b|\bstrength\b/i,"fx_strength"],[/❤|\bmax(?:imum)? health\b|\bhealth\b|\bhearts?\b/i,"gui_heart"],
 [/\bdamage taken\b|\bdamage reduction\b|\bresistance\b|\bknockback\b/i,"fx_resistance"],[/\b(?:movement|move|walk) speed\b|\bspeed\b/i,"fx_speed"],[/[+−-]\d[\d.]*%? luck\b|\bluck (?:stat|bonus|attribute)\b|\bfortune\b|\blooting\b/i,"fx_luck"],
 [/\bdodge\b|\bevasion\b/i,"fx_invisibility"],[/\blife ?steal\b|\bheal(?:s|ing)?\b|\bregenerat\w*/i,"fx_regeneration"],[/💧|\bmana\b|\bspell power\b|\bspells?\b/i,"fx_conduit_power"],
 [/\bmining\b|\bharvest\b/i,"fx_haste"],[/\bfire\b|\bburn\w*|\bflames?\b/i,"fx_fire_resistance"],[/\bpoison\w*/i,"fx_poison"],[/\bwither\w*/i,"fx_wither"],[/\bslow(?:ness|s|ed)?\b/i,"fx_slowness"],
 [/\bweakness\b/i,"fx_weakness"],[/\bjump\w*/i,"fx_jump_boost"],[/\babsorption\b/i,"fx_absorption"],[/\bnight vision\b/i,"fx_night_vision"],[/\binvisib\w*/i,"fx_invisibility"],
 [/\bswim\w*|\bunderwater\b|\bwater\b/i,"fx_dolphins_grace"],[/\bfall damage\b|\bslow falling\b|\blevitat\w*/i,"fx_slow_falling"],[/\bhunger\b|\bfood\b|\bsaturation\b/i,"gui_food"],
 [/\bdarkness\b|\bblind\w*/i,"fx_darkness"],[/\bglow\w*/i,"fx_glowing"],[/🏹|\barrows?\b|\branged\b|\bprojectiles?\b/i,"i_bow"],[/☠|\blethality\b|\bexecute\w*/i,"fx_instant_damage"]];
const EMO=/^[☀-➿\uD83C-\uDBFF]/;
// one pass: each AIR pattern, in order, claims its first match that no earlier pattern has claimed, so a phrase gets one icon
// ("Attack Speed" is haste, not haste plus a speed icon before "Speed"); the icons go in after, in text order
const AIRG=AIR.map(([re,k])=>[new RegExp(re.source,re.flags+"g"),k]);
// the mods' lang templates are stored verbatim: the game fills %s/%1$s/%d and [] (a key name) in code, '+' joins negative numbers, Tiers.X.m_…_() is the tier's level
const gameTx=t=>String(t).replace(/%%/g,"%").replace(/%(\d+\$)?[sd]\b/g,"…").replace(/\[\]/g,"[key]").replace(/\+-(?=\d)/g,"-").replace(/\bTiers\.([A-Z]+)\.m_\d+_\(\)/g,(m,t)=>t.charAt(0)+t.slice(1).toLowerCase()+" tier level");
// config values read from the pack's files: JSON id lists in words, an empty list as 'none'
const cfgTx=v=>{v=gameTx(v).trim();if(/^\[.*\]$/.test(v)){try{const a=JSON.parse(v);if(Array.isArray(a))return a.length?a.map(x=>typeof x==="string"&&/^[a-z0-9_.-]+: ?[a-z0-9_/.-]+$/.test(x)?nmI(x.replace(": ",":")):String(x)).join(", "):"none"}catch(e){}}
 return v};
function fmt(t){const h=esc(gameTx(t)).replace(/️/g,""),hit=[];
 for(const [re,k] of AIRG){re.lastIndex=0;let m;
  while((m=re.exec(h))){if(!m[0]){re.lastIndex++;continue}const a=m.index,b=a+m[0].length;if(!hit.some(([x,y])=>a<y&&b>x)){hit.push([a,b,k,m[0]]);break}}}
 hit.sort((x,y)=>x[0]-y[0]);let o="",q=0;
 for(const [a,b,k,m] of hit){o+=h.slice(q,a)+`<i class="ai" style="--ai:var(--v-${k})" aria-hidden="true"></i>${EMO.test(m)?"":m}`;q=b}return o+h.slice(q)}
const VBI={warden:{n:"Warden",hp:700,url:"https://minecraft.wiki/w/Warden",line:"Melee 18.5 / 35 / 52.5 (Easy / Normal / Hard: vanilla 30 plus the pack's +5); the ranged Sonic Boom ignores armor and shields.",sum:"Calls up from a Sculk Shrieker in the Deep Dark after repeated warnings. Drops a Sculk Catalyst.",pack:"Linggango's Hardmode ×2.1 does not apply to the Warden."},
 wither:{n:"Wither",hp:500,url:"https://minecraft.wiki/w/Wither",line:"Linggango stats: 32 damage, 20 armor. Below half health its armor makes it immune to arrows.",sum:"Build a T of 4 Soul Sand or Soul Soil and put 3 Wither Skeleton Skulls on top. Always drops a Nether Star.",pack:"Its Nether Star feeds Curse of Envy, which opens every L2 trait-item recipe."},
 dragon:{n:"Ender Dragon",get hp(){return typeof BST!=="undefined"&&BST.ender_dragon&&BST.ender_dragon.effective&&BST.ender_dragon.effective.hp||200},url:"https://minecraft.wiki/w/Ender_Dragon",line:"Heals from End Crystals on the obsidian pillars; first kill gives 12,000 XP and the Dragon Egg.",sum:"Its death opens the End Gateways to the outer islands: End Cities, Shulkers, Elytra.",pack:"Required before the Elvenite Paladin. Killing it switches on Hardmode: ×2.1 health and damage for other mobs; the Armageddon bosses, Wither, the Dragon itself and the Warden are exempt."}};
const CUBE='<span class="cube"><i class="f"></i><i class="t"></i><i class="l"></i><i class="r"></i><i class="b"></i></span>';
const head3d=(k,c="")=>`<span class="h3d h-${k} ${c}" aria-hidden="true"><span class="rig">${CUBE.replace('class="cube"','class="cube mn"')}${k==="wither"?CUBE.replace('class="cube"','class="cube sm sl"')+CUBE.replace('class="cube"','class="cube sm sr"'):""}</span></span>`;
const idOf=n=>(D.find(d=>d.n===n)||{}).id;
const EMB={"-1":"l2hostility:charm_of_looting_1",0:"minecraft:stick",2:"armageddon_mod:colossal_iron_ingot",3:"armageddon_mod:gilded_plate",4:"armageddon_mod:arion_heart",5:idOf("Ancient Builder's Charm"),6:"armageddon_mod:zoranths_hand",7:"armageddon_mod:elvenite_bell",8:"armageddon_mod:endermen_totem",9:"armageddon_mod:calamitous_core",10:idOf("Hemorrhage Charm")||"armageddon_mod:bloody_ingot",11:"armageddon_mod:helionite_ingot",6.1:"armageddon_mod:warden_treasure_bag",6.2:"armageddon_mod:wither_spine",6.3:"armageddon_mod:dragons_fang",12:"armageddon_mod:nyxaris_the_veil_of_oblivion_treasure_bag"};
{const l2=D.find(d=>d.t===-1&&IC[d.id]);if(l2)EMB["-1"]=l2.id}
const PB={2:"iron_colossus",3:"goblin_lord",4:"arion",5:"eldorath",6:"zoranth_forgotten",6.1:"warden",6.2:"wither",6.3:"ender_dragon",7:"elvenite_paladin",8:"vaedric",9:"discord",10:"sanghor",11:"zoranth_newborn",12:"nyxaris"};
const NEXTB={0:"iron_colossus",2:"goblin_lord",3:"arion",4:"eldorath",5:"zoranth_forgotten",6:"ender_dragon",6.3:"elvenite_paladin",7:"vaedric",8:"discord",9:"sanghor",10:"zoranth_newborn",11:"nyxaris"};
const bst=k=>(typeof BST!=="undefined"&&BST[k])||null;
const emblem=(a,c="")=>{const e=EMB[a],bi=typeof BIMG!=="undefined"&&BIMG[e];return `<span class="emb ${c}" style="--tc:${ACT[a][2]}">${e&&IC[e]?img(e):bi?`<img alt="" src="${bi}">`:`<span class="ph">${esc(ACT[a][0])}</span>`}</span>`};
const PTEX={"-1":"b_crying_obsidian",0:"b_dirt",2:"b_stone",3:"b_gilded_blackstone",4:"b_deepslate",5:"b_netherrack",6:"b_blackstone",6.1:"b_sculk",6.2:"b_soul_sand",6.3:"b_end_stone",7:"b_obsidian",8:"b_purpur_block",9:"b_crying_obsidian",10:"b_soul_soil",11:"b_reinforced_deepslate_top",12:"b_bedrock"};
const tex=a=>`--tex:var(--v-${PTEX[a]||"b_stone"})`;
/* the air of each Act's world, from the same block as its wall: falling petals on the surface, drips in caves, embers and ash in the Nether, souls by soul
   sand, sculk souls in the deep dark, portal motes in the End, glitter on gilded blackstone (CSS: .envfx[data-env=…]) */
const PENV={b_dirt:"meadow",b_stone:"cave",b_deepslate:"cave",b_gilded_blackstone:"gold",b_netherrack:"nether",b_blackstone:"nether",b_sculk:"sculk",b_soul_sand:"soul",b_soul_soil:"soul",
 b_end_stone:"end",b_obsidian:"end",b_purpur_block:"end",b_crying_obsidian:"end",b_reinforced_deepslate_top:"sculk",b_bedrock:"nether"};
// a boss brings its own air where its arena is plainer than the Act's block
const BENV={warden:"sculk",wither:"soul",ender_dragon:"end"},BTEX={warden:"b_sculk",wither:"b_soul_sand",ender_dragon:"b_end_stone"};
const btex=(a,k)=>BTEX[k]?`--tex:var(--v-${BTEX[k]})`:tex(a);
/* a column of The Path is built, not painted: courses of stone (.bk), a frieze in the Act's colour (.fr), the sun's grade over it (.gr), and three points of light in the stone that
   catch now and then (.gl, the colour of the Act; where they sit is the step's own, drawn from its number) */
const colFx=i=>{const h=n=>{const x=Math.sin(i*127.1+n*311.7)*43758.5453;return x-Math.floor(x)};
 return `<i class="bk"></i><i class="gr"></i><i class="fr"></i><span class="gl" aria-hidden="true">${[0,1,2].map(n=>`<b style="left:${(14+h(n)*66).toFixed(0)}%;top:${(16+n*26+h(n+5)*14).toFixed(0)}%;--d:${(11+h(n+9)*9).toFixed(1)}s;--w:-${(h(n+13)*20).toFixed(1)}s"></b>`).join("")}</span>`};
const envFx=(a,k)=>{const e=BENV[k]||PENV[PTEX[a]];return e?`<span class="envfx" data-env="${e}" aria-hidden="true">${[0,1,2,3,4,5,6,7].map(k=>`<i style="--k:${k}"></i>`).join("")}</span>`:""};
const SPR=["p_glint","p_sga_a","p_sga_e","p_sga_k","p_sga_r","p_sga_x","p_sga_z","p_glitter_0","p_glitter_3","p_spark_3"];
const MFSP={terra:"p_glitter_3",brut:"p_critical_hit",leth:"p_critical_hit",summ:"p_glitter_0",enigma:"p_sga_k",armag:"p_flame",celest:"p_glint",goety:"p_soul_5",l2:"p_sga_x",spell:"p_sga_e",blood:"p_drip_hang",tech:"p_spark_3",calam:"p_soul_fire_flame",relic:"p_glitter_6"};
const isMust=d=>d.r===6;
const rLabel=d=>isMust(d)?`${RN[6]} <span class="base">· ${T("power {tier}",{tier:RN[d.br]})}</span>`:RN[d.r];
const srcText=d=>Array.isArray(d.src)?d.src.join(" "):d.src;
/* floating relics behind the page, re-seeded per view */
const bgfx=document.createElement("div");bgfx.id="bgfx";bgfx.setAttribute("aria-hidden","true");document.body.prepend(bgfx);
let bgKey="";
/* the page background: a deepslate cave wall with tuff and cobbled patches and small ore veins, painted once at 16 px per block
   and shown at x4 behind everything (#cave). Seeded, toroidal, so it repeats without a seam. Textures: uiicons.js (bg_*).
   The precious ores twinkle (.og, shown on the home page): the wall's own gold, redstone, lapis, diamond and emerald
   blocks plus GLOWN more at seeded cells near the two edges, where no panel covers them. A block is as dark as the wall;
   every so often (each block on its own clock) three of its gem pixels (the pixels that differ from plain deepslate)
   catch the light for a moment, then three others. */
{const T=typeof ROOMT!=="undefined"?ROOMT:{},need=["bg_deepslate","bg_cobbled_deepslate","bg_tuff"];
 if(need.every(k=>T[k])){const W=32,Hh=20,cv=document.createElement("canvas");cv.width=W*16;cv.height=Hh*16;const g=cv.getContext("2d");
  let sd=7;const rnd=()=>(sd=(sd*16807)%2147483647)/2147483647;
  const blobs=[...Array(9)].map(()=>[rnd()*W,rnd()*Hh,1.5+rnd()*2.5,rnd()<.5?"bg_tuff":"bg_cobbled_deepslate"]);
  const ores=["bg_deepslate_coal_ore","bg_deepslate_iron_ore","bg_deepslate_copper_ore","bg_deepslate_coal_ore","bg_deepslate_gold_ore","bg_deepslate_redstone_ore","bg_deepslate_lapis_ore","bg_deepslate_iron_ore","bg_deepslate_diamond_ore","bg_deepslate_emerald_ore"];
  const map=[...Array(Hh)].map((_,y)=>[...Array(W)].map((_,x)=>{for(const[bx,by,r,k]of blobs){const dx=Math.min(Math.abs(x-bx),W-Math.abs(x-bx)),dy=Math.min(Math.abs(y-by),Hh-Math.abs(y-by));if(dx*dx+dy*dy<r*r)return k}return "bg_deepslate"}));
  for(let i=0;i<14;i++){const k=ores[Math.floor(rnd()*ores.length)];let x=Math.floor(rnd()*W),y=Math.floor(rnd()*Hh);for(let n=1+Math.floor(rnd()*3);n--;){map[y][x]=k;x=(x+(rnd()<.5?1:0))%W;y=(y+(rnd()<.5?1:0))%Hh}}
  const GEM=["gold","redstone","lapis","diamond","emerald"].map(k=>"bg_deepslate_"+k+"_ore").filter(k=>T[k]),GLOWN=18;
  const ims={};let left=0;const draw=()=>{for(let y=0;y<Hh;y++)for(let x=0;x<W;x++)g.drawImage(ims[map[y][x]],x*16,y*16);
   const c=document.createElement("div"),R=document.documentElement.style;c.id="cave";c.setAttribute("aria-hidden","true");R.setProperty("--cave",`url(${cv.toDataURL()})`);
   // gem pixels of each precious ore: what differs from plain deepslate
   const px=im=>{const q=document.createElement("canvas");q.width=q.height=16;const x=q.getContext("2d",{willReadFrequently:true});x.drawImage(im,0,0);return [q,x,x.getImageData(0,0,16,16)]},[, ,base]=px(ims.bg_deepslate);
   GEM.forEach((k,i)=>{const [q,x,d]=px(ims[k]),gem=[];let cr=0,cg=0,cb=0;
    for(let j=0;j<d.data.length;j+=4)if(Math.abs(d.data[j]-base.data[j])+Math.abs(d.data[j+1]-base.data[j+1])+Math.abs(d.data[j+2]-base.data[j+2])>=90){gem.push(j);cr+=d.data[j];cg+=d.data[j+1];cb+=d.data[j+2]}
    R.setProperty("--ore"+i,`url(data:image/png;base64,${T[k]})`);R.setProperty("--gc"+i,`rgb(${cr/gem.length|0},${cg/gem.length|0},${cb/gem.length|0})`);
    // two sets of three gems, each lightened towards white
    for(const v of "ab"){const o=x.createImageData(16,16);for(let n=0;n<3&&gem.length;n++){const j=gem[Math.floor(rnd()*gem.length)];for(let c=0;c<3;c++)o.data[j+c]=d.data[j+c]+(255-d.data[j+c])*.6;o.data[j+3]=255}
     x.putImageData(o,0,0);R.setProperty("--sp"+v+i,`url(${q.toDataURL()})`)}});
   const cell=(x,y,i,right)=>`<i class="og" style="${right?"right":"left"}:${x*64}px;top:${y*64}px;--t:var(--ore${i});--ka:var(--spa${i});--kb:var(--spb${i});--gc:var(--gc${i});--dur:${(14+rnd()*16).toFixed(1)}s;--d:-${(rnd()*30).toFixed(1)}s"></i>`,og=[];
   for(let y=0;y<Hh;y++)for(let x=0;x<W;x++){const i=GEM.indexOf(map[y][x]);if(i>=0)og.push(cell(x,y,i),cell(x+W,y,i))}
   for(let n=0;n<GLOWN;n++)og.push(cell(Math.floor(rnd()*5),Math.floor(rnd()*Hh),Math.floor(rnd()*GEM.length),n%2));
   c.innerHTML=og.join("");document.body.prepend(c)};
  const keys=[...new Set(map.flat().concat(GEM,"bg_deepslate"))];left=keys.length;keys.forEach(k=>{const im=new Image();im.onload=()=>{if(!--left)draw()};im.src="data:image/png;base64,"+T[k];ims[k]=im})}}
function seedBg(key,pool){return;bgKey=key;pool=pool.filter(d=>IC[d.id]);if(!pool.length)pool=D.filter(d=>d.r>=4&&IC[d.id]);
 const W=["i_netherite_sword","i_diamond_sword","i_trident","i_bow","i_totem_of_undying","i_nether_star","i_echo_shard","i_heart_of_the_sea"];
 const N=innerWidth<760?0:14,R=Math.ceil(N/2)||1,gx=i=>i%2?1.5+(i*3)%5:92+(i*2)%5,gy=(i,o=0)=>((Math.floor(i/2)+.5+o)/R*94+3+((i*17)%5-2)).toFixed(1);let h="";
 for(let i=0;i<N;i++){const z=i%3,y=gy(i),dur=16+(i*13)%15,dl=-((i*2.7)%16).toFixed(1),dx=((i%2?1:-1)*(10+i*3%22));
  const src=i%5===4?`data:image/png;base64,${VA[W[i%W.length]]}`:icu(pool[(i*7+3)%pool.length].id);
  h+=`<span class="fl z${z}" style="left:${gx(i)}%;top:${y}%;--dur:${dur}s;--dl:${dl}s;--dx:${dx}px"><img alt="" src="${src}"></span>`}
 for(let i=0;i<(innerWidth<760?0:12);i++)h+=`<span class="sp" style="left:${gx(i+1)}%;top:${gy(i,.5)}%;--sp:var(--v-${SPR[i%SPR.length]});--dur:${5+i%6}s;--dl:-${(i*1.3%6).toFixed(1)}s"></span>`;
 bgfx.innerHTML=h}

/* ---------- data prep ---------- */
/* power tiers measured in game (patches/curio_tiers.json, from gear.js's curio scores): a curio Equipment -> Curios tiers takes
   that tier at its own Act (S Mythic .. D Uncommon); the others keep the tier read from their text (d.pe: an estimate) */
if(typeof CTIER!=="undefined")D.forEach(d=>{const t=CTIER[d.id];if(t&&d.r!==6){d.r=t[0];d.pr0=t[1]}else if(d.r!==6)d.pe=1});
D.sort((a,b)=>b.r-a.r||b.sc-a.sc||a.n.localeCompare(b.n));
const BYID={};D.forEach((d,i)=>{d.ix=i;d.c=d.ro[0];BYID[d.id]=d});
// list fingerprint: share links store item indices, so a link made before the item list changed is flagged
const DFP=(()=>{let h=0;D.forEach(d=>{for(const c of d.id)h=(h*31+c.charCodeAt(0))%1000003});return h.toString(36)})();
/* d.rq: the curio's own text says it needs the Ring of the Seven Curses or Virtues */
const RQRING={Curses:"enigmaticlegacy:cursed_ring",Virtues:"covenant_of_the_seven:virtue_ring"},RQRX=/requires (?:the )?(?:Ring of )?(?:the )?Seven (?:Curses|Virtues)|Seven (?:Curses|Virtues) bearers only|\(Seven (?:Curses|Virtues)(?: path)?\)|Break the Ring of (?:the )?Seven Curses/i;
D.forEach(d=>{if(d.id===RQRING.Curses||d.id===RQRING.Virtues)return;const m=RQRX.exec([d.fx,...d.st,...d.src].join(" | "));if(m)d.rq=/curses/i.test(m[0])?"Curses":"Virtues"});
const rqName=d=>"Ring of the Seven "+d.rq;
const rqb=(d,cls="")=>d.rq?`<i class="rqring${cls}" title="${T("Requires the {ring}",{ring:rqName(d)})}" aria-label="${T("Requires the {ring}",{ring:rqName(d)})}">${img(RQRING[d.rq])}</i>`:"";
const TOTAL=count(D);
const usedBy=id=>D.filter(d=>d.gr&&d.gr.c.some(c=>c&&c[0]===id));
const SLOTS=(()=>{const c={};D.forEach(d=>d.sl.forEach(s=>(c[s]=c[s]||[]).push(d)));return Object.entries(c).sort((a,b)=>b[1].length-a[1].length)})();
const BIGSLOTS=SLOTS.filter(s=>s[1].length>=7);
const MODS=(()=>{const c={};D.forEach(d=>(c[d.m]=c[d.m]||[]).push(d));return Object.entries(c).sort((a,b)=>a[0].localeCompare(b[0]))})();

/* ---------- filter state ---------- */
const st={c:[],g:[],r:[],x:[],m:"",s:"",a:"",q:"",nw:false,sort:"a",dir:1,cl:[],op:null,rl:0,rq:-1};
// a saved key is kept only when its shape matches the default (an edited or foreign value falls back per key)
try{const o=JSON.parse(localStorage.getItem("lgw2")||"{}");if(o&&typeof o==="object")for(const k in st){if(!(k in o))continue;const v=o[k],d=st[k];
 if(k==="op"?v===null||Array.isArray(v)&&v.every(x=>typeof x==="number"):Array.isArray(d)?Array.isArray(v)&&v.every(x=>typeof x==="string"):typeof v===typeof d)st[k]=v}
 st.c=st.c.filter(k=>k in ROLE);st.r=st.r.filter(x=>/^[0-6]$/.test(x));if(st.a!==""&&!ORDER.includes(+st.a))st.a=""}catch(e){}st.cl=[];
const save=()=>{try{localStorage.setItem("lgw2",JSON.stringify(st))}catch(e){}};
function pass(d,skip){
 return (skip==="x"||st.x.every(k=>d.mt.includes(k)))&&(skip==="r"||!st.r.length||st.r.includes(String(d.r)))
  &&(skip==="c"||!st.c.length||isMust(d)||st.c.some(k=>d.ro.includes(k)))&&(skip==="g"||!st.g.length||st.g.includes(d.g))
  &&(!st.nw||d.nw)&&(!st.m||d.m===st.m)&&(!st.s||d.sl.includes(st.s))&&(st.a===""||d.a<=+st.a)
  &&qMatch(d);
}

/* ---------- sidebar ---------- */
const chipEls={c:[],r:[],g:[],x:[]};
function chips(id,map,key){const box=el(id);for(const k in map){const b=document.createElement("button");b.className="chip"+(key==="r"?" r"+k:"");b.dataset.k=k;b._en=map[k];b.innerHTML=esc(map[k])+'<span class="n"></span>';
 b.onclick=()=>{const a=st[key],i=a.indexOf(k);i<0?a.push(k):a.splice(i,1);refresh()};box.appendChild(b);chipEls[key].push(b)}}
/* sidebar tags, read from each curio's effect text: spell schools (not elemental damage or immunities) and secondary stats the Role filter doesn't cover */
{const SCH=/\b(Aqua|Lightning|Eldritch|Ender|Fire|Holy|Nature|Blood|Evocation|Ice|Geo|Annihilation) (?:spell|magic)/gi;
 const MECH=[["Lifesteal",/lifesteal|life steal|of (?:the )?damage (?:dealt )?as health/i],["Armor pierce",/armor pierc|armor penetrat|lethality|ignores?[^.;]*armor/i],["Crit",/\bcrit/i],["Dodge",/dodge/i],["Attack speed",/attack speed/i],["Cooldown",/cooldown/i],["Mana",/\bmana\b/i],["Minions",/minion|summon damage|whip/i],["Reach",/reach/i],["Thorns / reflect",/thorns|reflect/i],["Damage reduction",/damage taken|less damage|damage resistance/i],["Knockback resist",/knockback resistance/i],["Bleed",/bleed|hemorrhage/i],["Rage",/\brage\b/i],["Luck / loot",/\bluck\b|looting|drop chance/i],["Mining",/mining speed|fortune/i]];
 D.forEach(d=>{const keep=d.mt.filter(t=>(t.startsWith("l:")||t.startsWith("s:"))&&t!=="l:Luck"),t=new Set(keep.map(x=>x.startsWith("s:")?"l:Brutality seasoning":x)),fx=d.fx||"";
  for(const m of fx.matchAll(SCH))t.add("e:"+m[1][0].toUpperCase()+m[1].slice(1).toLowerCase());
  for(const [n,re] of MECH)if(re.test(fx))t.add("l:"+n);d.mt=[...t]})}
{const all={};D.forEach(d=>d.mt.forEach(t=>all[t]=(all[t]||0)+1));
 const grp=p=>Object.fromEntries(Object.keys(all).filter(t=>t.startsWith(p)).sort((a,b)=>all[b]-all[a]).map(t=>[t,t.slice(2)]));
 chips("fe",grp("e:"),"x");chips("fl",grp("l:"),"x");chips("fsp",grp("s:"),"x");st.x=st.x.filter(k=>all[k])}
chips("fr",Object.fromEntries(RN.map((n,i)=>[i,n])),"r");chips("fc",ROLE,"c");chips("fg",{Craft:"Craft",Loot:"Loot"},"g");
const nb=document.createElement("button");nb.className="chip";nb.textContent="New in 6.6.6";nb.onclick=()=>{st.nw=!st.nw;refresh()};el("fg").appendChild(nb);
function opts(id,vals){const s=el(id);vals.forEach(([v,t])=>s.add(new Option(t,v)))}
opts("fm",MODS.map(([m])=>[m,m]));
opts("fs",SLOTS.map(([s])=>s).sort().map(s=>[s,s]));
opts("fa",ORDER.filter(a=>a>=0).map(a=>[a,"Up to "+actL(a)]));
for(const k of ["m","s","a"]){const s=el("f"+k);s.value=st[k];s.onchange=()=>{st[k]=s.value;refresh()}}
el("q").value=st.q;
el("q").oninput=e=>{clearTimeout(FQT);FQT=setTimeout(()=>{st.q=e.target.value.trim();const f=el("fq");if(f)f.value=st.q;location.hash.startsWith("#i")?refreshSide():refresh()},220)};
// Enter applies what the box says (the typed text may not have reached st.q yet, or was typed off Curios) and opens Curios
el("q").onkeydown=e=>{if(e.key==="Enter"){clearTimeout(FQT);st.q=e.target.value.trim();const f=el("fq");if(f)f.value=st.q;location.hash==="#home"?refresh():location.hash="#home"}};
function resetFilters(){Object.assign(st,{c:[],g:[],r:[],x:[],m:"",s:"",a:"",q:"",nw:false});["fm","fs","fa","q"].forEach(i=>el(i).value="");refresh()}
el("reset").onclick=resetFilters;
el("fold").onclick=()=>{const s=el("side");s.classList.toggle("closed");el("fold").setAttribute("aria-expanded",!s.classList.contains("closed"))};
if(matchMedia("(max-width:760px)").matches)el("side").classList.add("closed");

function refreshSide(){
 for(const key in chipEls)chipEls[key].forEach(b=>{const k=b.dataset.k;b.setAttribute("aria-pressed",st[key].includes(k));
  b.querySelector(".n").textContent=count(D.filter(d=>(key==="c"?(d.ro.includes(k)||isMust(d)):key==="x"?d.mt.includes(k):String(d[key])===k)&&pass(d,key)))});
 nb.setAttribute("aria-pressed",st.nw);
 const xs=D.filter(d=>pass(d));el("cnt").textContent=T("{n} / {total} curios",{n:count(xs),total:TOTAL});
 const cur=location.hash.startsWith("#i")?+location.hash.slice(2):-9;
 const sig=xs.map(d=>d.ix).join();if(sig!==IDXSIG){IDXSIG=sig;el("idx").innerHTML=[...xs].sort((a,b)=>nameCmp(a.n,b.n)).slice(0,600).map(d=>`<li><a href="#i${d.ix}" data-t="${d.ix}">${img(d.id)}<span>${esc(TD(d.n))}</span><span class="act">${ACT[d.t][0]}</span></a></li>`).join("")
  +(xs.length>600?`<li class="meta">${T("… {n} more, narrow the filters to see them",{n:xs.length-600})}</li>`:"")}
 el("idx").querySelectorAll("[aria-current]").forEach(a=>a.removeAttribute("aria-current"));const ca=el("idx").querySelector(`a[href="#i${cur}"]`);if(ca)ca.setAttribute("aria-current","page");
 return xs}

/* the sidebar is built once, in English, when the page loads; a language change (i18n.js useLang) only relabels it: the filter keys stay English, so saved filters and links keep working */
function relabelSide(){
 {const n=document.getElementById("strans"),m=typeof pack==="function"&&pack()&&pack().meta;   // how much of this language was checked by a person (the build counts the states in the translation memory)
  if(n){if(LANG==="en"||!m)n.hidden=true;else{n.hidden=false;n.innerHTML=T(`Translation: {official}% is the game's own wording, {human}% was checked by a native speaker, {llm}% is machine translation still waiting for one. <a href="https://github.com/tranquanghaofake-dotcom/Linggango-Relic-Wiki/issues" target="_blank" rel="noopener">Report a mistake</a>`,m)}}}
 {const t=document.getElementById("totop"),q=document.getElementById("qs");if(t)t.setAttribute("aria-label",T("Back to top"));if(q)q.setAttribute("aria-label",T("Search results"))}
 for(const key in chipEls)chipEls[key].forEach(b=>{b.firstChild.nodeValue=T(b._en)});
 nb.textContent=T("New in 6.6.6");
 for(const o of el("fs").options)if(o.value)o.textContent=T(o.value);
 for(const o of el("fa").options)if(o.value!=="")o.textContent=T("Up to {act}",{act:actL(+o.value)});
 IDXSIG="";TIPC.clear();D.forEach(d=>{d._q=null});if(typeof QSRESET==="function")QSRESET()}

/* ---------- shared bits ---------- */
/* Curios slot icons: the empty-slot silhouette each mod registers for that slot */
const SLA={"living armour":"living_armour_socket","binding key":"bindingkey","wings":"terra_wings","focus":"an_focus","spellstone":"scroll","bundle":"curio"};
const SLU={};
const slotKey=n=>{const k=n.toLowerCase();return SLA[k]||k.replace(/ /g,"_")};
const slotIcon=(n,t)=>{const k=slotKey(n),b=(UI[t?"cslotT":"cslot"]||{})[k],c=t?k+"~":k;if(!b)return "";if(!SLU[c])SLU[c]=URL.createObjectURL(new Blob([Uint8Array.from(atob(b),c=>c.charCodeAt(0))],{type:"image/png"}));return SLU[c]};
/* slot badge in the tile corner (slot_badges.py): one drawn sign per slot family */
const SBK={Charm:"charm",Accessory:"curio",Curio:"curio",Anklet:"anklet",Blasphemy:"skull",Scroll:"scroll",Ring:"ring",Head:"head",Hands:"hands",Glove:"hands",Focus:"orb",Spellbook:"book",Back:"back",Spellstone:"orb",Heart:"heart",Necklace:"necklace",Belt:"belt","Living Armour":"living","Hostility Curse":"skull",Elytra:"elytra","Binding Key":"key",Feet:"feet",Body:"body",Bracelet:"bracelet",Talent:"talent",Magnetizer:"magnet",Bundle:"bundle",Sacrament:"chalice"};
const sbadge=(s,cls="")=>`<i class="sbdg${cls}" style="--sb:var(--rt-sb_${SBK[s]||"curio"})" title="${esc(T("{slot} slot",{slot:T(s)}))}" aria-hidden="true"></i>`;
const slk=d=>sbadge(d.sl[0]||"Curio");
const tile=(d,i=99)=>`<a style="--i:${i}" class="t c${d.c} r${d.r}${d.g==="Loot"?" L":""}${d.inv?" inv":""}" data-mf="${mf(d.m)[0]}" href="#i${d.ix}" data-t="${d.ix}" aria-label="${esc(TD(d.n))}">${AN[d.id]?`<span class="aimg" data-an="${esc(d.id)}">${img(d.id)}</span>`:img(d.id)}${d.k>1?`<span class="kv">${d.k}</span>`:""}${glint(d)}${isMust(d)?`<span class="star" aria-label="${T("Must-Have")}">★</span>`:""}${rqb(d)}${slk(d)}</a>`;
const gcard=(d,i)=>`<a class="gc r${d.r}" style="--i:${Math.min(i,40)}" href="#i${d.ix}" data-t="${d.ix}"><span class="pic">${img(d.id)}</span><b>${esc(TD(d.n))}</b><small>${esc(d.sl.map(x=>T(x)).join(", "))} · ${esc(d.m)}</small><span class="gm"><span class="rk">${isMust(d)?ui("star")+"Must-Have":RN[d.r]}</span><span class="ak">${esc(actL(d.t))}</span></span></a>`;
const rbar=xs=>`<span class="bar5">${RNS.map(i=>{const n=xs.filter(d=>d.r===i).length;return n?`<i style="flex:${n};background:${RC[i]}"></i>`:""}).join("")}</span>`;
const cards=xs=>`<div class="cards">${xs.map(x=>`<a class="card" href="#i${x.ix}" data-t="${x.ix}">${img(x.id)}<span>${esc(TD(x.n))}</span></a>`).join("")}</div>`;
const crumb=(...p)=>`<div class="crumb"><a href="#">${T("Home")}</a> / ${p.join(" / ")}</div>`;
/* ---------- article: the one layout every detail page uses (curio, gear piece, armor set, Keeper, side boss) ----------
   The convention of game wikis (Minecraft Wiki, Terraria and Calamity on wiki.gg): title and a one-line lead, sections in a
   fixed order, an infobox with the picture and the key facts plus "On this page" on the right, a navbox at the foot, and the
   pack version the page was checked against. A new kind of page only fills this object:
     cls      extra classes on .ip (a curio passes its rarity "r3"; other pages "r0")   style  CSS variables (--tc, --tex…)
     crumb    breadcrumb html          title / pre  heading text and anything before it (the Must-Have star)
     lead     one sentence that says what it is     meta  chips under the lead (html, each in a <span>)   head  extra header html
     secs     [[id, heading, html], …]; falsy entries are skipped, ids become #s-<id> and the table of contents
     art      the picture box (html of a .ip-art)   box  {head, rows:[[term, value, tooltip?]], foot}   after  html under the sections
     nav      navbox html (navbox() / wikiNav())
   wireArticle() runs after the html is in the page (copy button, the table of contents following the scroll). */
const PACKV="V6.6.6hf";
const nameCmp=(a,b)=>LANG==="en"?a.localeCompare(b):TD(a).localeCompare(TD(b),LANG);   // A–Z by the name the reader sees
const enAlt=n=>LANG!=="en"&&TD(n)!==n?`<p class="ip-alt" lang="en">${esc(n)}</p>`:"",enTip=n=>LANG!=="en"&&TD(n)!==n?`<div class="tnen" lang="en">${esc(n)}</div>`:"";
function article(o){const secs=(o.secs||[]).filter(Boolean),here=location.hash||"#",b=o.box||{};
 return `<div class="ip art ${o.cls||"r0"}"${o.style?` style="${o.style}"`:""}${o.data||""}>
 <header class="ip-hero"><span class="motes" aria-hidden="true">${"<i></i>".repeat(9)}</span><div class="ip-htext">${o.crumb||""}<h1 class="ip-title">${o.pre||""}${o.title}</h1>${o.alt||""}${o.lead?`<p class="ip-lead">${o.lead}</p>`:""}${o.meta?`<p class="ip-meta">${o.meta}</p>`:""}${o.head||""}</div></header>
 <div class="ip-body"><div class="ip-main">${secs.map(x=>`<section class="s ip-sec${x[3]?" "+x[3]:""}" id="s-${x[0]}"><h2>${x[1]}</h2>${x[2]}</section>`).join("")}${o.after||""}</div>
 <aside class="ip-side">${o.art||""}${b.rows||b.head?`<div class="ip-info">${b.head?`<div class="ip-ih">${b.head}</div>`:""}<dl>${(b.rows||[]).filter(Boolean).map(([t,v,tt])=>`<dt${tt?` title="${esc(tt)}"`:""}>${t}</dt><dd>${v}</dd>`).join("")}</dl>${b.foot||""}</div>`:""}
 ${secs.length>1?`<nav class="ip-toc" aria-label="${T("On this page")}"><b>${T("On this page")}</b><ol>${secs.map(x=>`<li><a href="${here}" data-go="s-${x[0]}">${x[1].replace(/<[^>]+>/g,"")}</a></li>`).join("")}</ol><a href="${here}" class="ip-top" data-top="1">${T("↑ Back to top")}</a></nav>`:""}</aside></div>
 ${o.nav||""}<p class="art-ver">${T("Checked against Linggango {v}. Numbers come from the pack's own files; estimates say so.",{v:PACKV})}</p></div>`}
function wireArticle(){const m=el("main");
 const cb=m.querySelector("#ipcopy"),id=m.querySelector("#ipid");if(cb&&id)cb.onclick=()=>{const v=id.textContent,ok=()=>{cb.classList.add("ok");cb.textContent=T("Copied");setTimeout(()=>{cb.classList.remove("ok");cb.textContent=T("Copy")},1400)};const old=()=>{const r=document.createRange();r.selectNodeContents(id);const se=getSelection();se.removeAllRanges();se.addRange(r);try{document.execCommand("copy")?ok():(cb.textContent=T("Press Ctrl+C"))}catch(e){cb.textContent=T("Press Ctrl+C")}};try{navigator.clipboard.writeText(v).then(ok,old)}catch(e){old()}};
 try{const links=[...m.querySelectorAll(".ip-toc [data-go]")];if(!links.length)return;const io=new IntersectionObserver(es=>es.forEach(en=>{if(en.isIntersecting)links.forEach(a=>a.classList.toggle("on",a.dataset.go===en.target.id))}),{rootMargin:"-30% 0px -60% 0px"});m.querySelectorAll(".ip-sec").forEach(x=>io.observe(x))}catch(e){}}
/* turn html made of <section class="s …"><h2>Title</h2>…</section> blocks into article sections [id, title, html, class] */
function secsOf(html,pre){const t=document.createElement("template");t.innerHTML=html;
 return [...t.content.children].filter(x=>x.tagName==="SECTION").map((x,i)=>{const h=x.querySelector(":scope>h2");const title=h?h.innerHTML:"";if(h)h.remove();
  return [(pre||"x")+i+"-"+title.replace(/<[^>]+>/g,"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,""),title,x.innerHTML,[...x.classList].filter(c=>c!=="s").join(" ")]})}
const idBox=id=>`<div class="ip-id"><code id="ipid">${esc(id)}</code><button type="button" id="ipcopy">${T("Copy")}</button></div>`;
/* navbox: the block of related links at the foot of a page. groups = [[label, [[href, text, current?], …]], …]; empty groups drop out */
function navbox(title,groups){groups=(groups||[]).filter(g=>g&&g[1]&&g[1].length);if(!groups.length)return "";
 return `<details class="navbox" open><summary>${title}</summary><dl>${groups.map(([l,xs])=>`<dt>${l}</dt><dd>${xs.map(([h,t,on])=>on?`<b aria-current="page">${t}</b>`:`<a href="${h}">${t}</a>`).join('<i aria-hidden="true"> · </i>')}</dd>`).join("")}</dl></details>`}
/* rooms: rooms.js. A row of inventory slots holding a list of items (links with tooltips), with a small label under each */
const slotRow=(xs,label,pad=0)=>`<nav class="srow" aria-label="${esc(label)}">${xs.map((x,k)=>`<a class="sslot${x.c||""}" style="--k:${k}" href="${x.h}"${x.t!=null?` data-t="${x.t}"`:` title="${esc(TD(x.n))}"`} aria-label="${esc(TD(x.n))}">${x.i}${x.l?`<small>${x.l}</small>`:""}</a>`).join("")}${"<span class=\"sslot e\" aria-hidden=\"true\"></span>".repeat(Math.max(0,pad-xs.length))}</nav>`;
const rCurio=(d,l,g)=>({h:"#i"+d.ix,i:img(d.id)+glint(d),t:d.ix,n:d.n,l,g});
const KEEPERS=()=>{const ks=ORDER.map(a=>PB[a]).filter(Boolean);const i=ks.indexOf("zoranth_forgotten");if(i>=0)ks.splice(i+1,0,"warden","wither");return ks};
/* update log, newest first */
function changesPage(){
 document.title=T("Changes")+" · Linggango Wiki";
 el("main").innerHTML=`${crumb(T("Changes"))}${room("vault",[],{head:`<h1>${T("Changes")}</h1><p class="lede">${T("What's new on the wiki, newest first.")}</p>`})}
<section class="s" id="c-2026-10-31"><h2>${T("October 31, 2026")}</h2>
<h3 class="ck chg">${T("Changed")}</h3><ul>
<li>${T("<b>Boss pictures</b> are drawn from each mod's own model with the game's light, for the Keepers and the side bosses. Crone, Ice Hermit and Mutant Enderman have a picture for the first time, and none is taken from another wiki.")}</li>
<li>${T("<b>Drop chances and gear effects</b> are re-read from the pack's official server files. For example, the Crone drops glowstone dust 37% of the time, not 55%.")}</li>
<li>${T("<b>Obsidian armor</b> (Composite Material) moved from Act V to Act VI: the pack's own recipe upgrades a netherite piece.")}</li>
<li>${T("<b>Icons</b> come from the mods' own and vanilla textures, tinted the way the game tints them. None are drawn from All Rights Reserved resource packs.")}</li>
</ul>
<h3 class="ck fix">${T("Fixed")}</h3><ul>
<li>${T("A pass over search, filters, The Path, the build planner, Mechanics and the boss pages. For example, quick search calls the Ender Dragon a required boss, not a Keeper; \"What can I get now?\" says it lists the curios that open at your Act; on phones the pages say tap, not hover.")}</li>
</ul></section>
<section class="s" id="c-2026-10-30"><h2>${T("October 30, 2026")}</h2>
<h3 class="ck chg">${T("Changed")}</h3><ul>
<li>${T("<b>Build planner</b> keeps only the permanent Consumables row. The Food buffs and Potions rows are gone.")}</li>
<li>${T("<b>Stacks</b> label fix: Summonity curios that can't be worn twice (Minion Metronome, Lead Bell, Ring of Summoning and others, plus the whistles) now show One per player instead of Stacks.")}</li>
<li>${T("<b>Act pages</b> no longer run idle animations on curio tiles. They animate on hover.")}</li>
</ul></section>
<section class="s" id="c-2026-10-29"><h2>${T("October 29, 2026")}</h2>
<h3 class="ck add">${T("Added")}</h3><ul>
<li>${T("<b>Consumables</b> in the build planner: the five home boons (Hearty Feast, Angler's Pearl, Amber Core, Hunter's Essence, Arcane Crystal). They are toggled on and off, kept out of the stat totals, and saved in the link.")}</li>
<li>${T("<b>Status and combos</b> in Stats explained: what each element's meter does when it fills, the 13 element combos, and what happens when Arcane hits max.")}</li>
<li>${T("<b><a href=\"#mechanics/effects\">Effects</a></b> on the Mechanics page: food buffs, Linggango's effects and the vanilla effects in the pack, each with the items whose text names it. Effect names on item pages link there.")}</li>
</ul>
<h3 class="ck chg">${T("Changed")}</h3><ul>
<li>${T("<b>Build planner share links</b> are shorter: slots use one-character codes and relic data is packed in base 36. Older links still open.")}</li>
<li>${T("<b>Path curios</b> only animate while the tile is hovered; the idle bobbing, shine and star motion is off.")}</li>
<li>${T("<b><a href=\"#mechanics/stats\">Stats explained</a></b> rewritten from the mods' code and the pack's config. It now follows one hit step by step and covers armor, crits, dodge, taking damage, healing, roll and parry, damage types, magic and summons. What changed from the first version:")}<ul>
<li>${T("<b>Melee crits:</b> Brutality's Critical Strike Chance is the roll every melee crit needs. Jumping is not required, and with 0% chance jump crits are gone. TerraCurio's \"critical chance\" is the Apothic crit (base 5%, every hit), not a separate roll.")}</li>
<li>${T("<b>Dodge caps</b> in this pack are 50% (Brutality) and 40% (Apothic), not 95% and 100%.")}</li>
<li>${T("<b>Lethality</b> past zero armor turns into +10% damage per point.")}</li>
<li>${T("<b>Slash, Pierce and Blunt Damage</b> do work: Brutality adds them by the weapon you hold.")}</li>
<li>${T("<b>Does nothing on your hits:</b> Iron's Lib armor pierce and Goety Revelation's armor penetration.")}</li>
<li>${T("<b>Armor Toughness</b> does not reduce damage here; it only weakens armor shred and pierce used against you.")}</li>
<li>${T("The pack's own rules are in: 13% damage floor, a hit never over half your max health, ×3 soft cap on bonus damage, 10% max health a tick from lifesteal, Resistance levels (V is 38%, not immunity).")}</li></ul></li>
<li>${T("<b>Stat tooltips</b> on curio pages match the new text, and a few more stats have one (Damage Taken, Armor Shred, roll stats, Cooldown Reduction).")}</li></ul>
<h3 class="ck fix">${T("Fixed")}</h3><ul>
<li>${T("Warden melee damage now shows the pack's +5: 18.5 / 35 / 52.5.")}</li></ul>
</section>
<section class="s" id="c-2026-10-28"><h2>${T("October 28, 2026")}</h2>
<h3 class="ck add">${T("New")}</h3><ul>
<li>${T("<b>Equipment › Curios:</b> 1,318 curios measured in game; 357 are tiered on the same scale as weapons and sets.")}</li>
<li>${T("<b>Gear measured in game:</b> 1,038 weapons and 328 armor sets (hits, on-hit effects, worn effects, set bonuses, damage taken).")}</li>
<li>${T("<b>Ranking:</b> tiers are set against the fifth best item, and survival scores use the pack's damage floor and hit cap.")}</li>
<li>${T("<b>Stats explained</b> (Mechanics › Stats), first version. Rewritten on October 29.")}</li>
<li>${T("<b>Stat tooltips on curio pages:</b> stat names have a dotted underline. Hover one for a short explanation, or click it to open the full guide.")}</li>
<li>${T("<b>Changes:</b> this page.")}</li></ul>
<h3 class="ck fix">${T("Fixed")}</h3><ul>
<li>${T("Warden health is now 700 and Wither health is now 500.")}</li>
<li>${T("Keeper armor in the Path rows: Goblin Lord 12 (Act II), Arion 20 on foot and 15 on its Ravager (Act III), Eldorath 18 (Act IV).")}</li></ul>
</section>${wikiNav()}`;
 /* the bar: show one kind of change (Added, Changed, Fixed) or jump to a day. A day folds at its date; the two newest start open,
    and a folded day's date carries its counts. The page's own text is untouched: the groups are tagged, not moved. A new kind
    of group needs its class here and in KN (and a translated name). */
 const days=[...el("main").querySelectorAll('section.s[id^="c-"]')],KN={add:T("Added"),chg:T("Changed"),fix:T("Fixed")},cnt={};
 days.forEach((d,i)=>{const h=d.querySelector("h2"),own={};let k=null;
  [...d.children].forEach(c=>{if(c.tagName==="H3"&&c.classList.contains("ck"))k=["add","chg","fix"].find(x=>c.classList.contains(x));if(c!==h&&k){c.dataset.k=k;if(c.tagName==="UL"){const n=c.querySelectorAll(":scope>li").length;own[k]=(own[k]||0)+n;cnt[k]=(cnt[k]||0)+n}}});
  h.innerHTML=`<button type="button" class="chtog" aria-expanded="${i<2}">${h.innerHTML}</button><span class="chn">${Object.keys(own).map(k=>`<i class="ck ${k}" title="${esc(KN[k])}">${own[k]}</i>`).join("")}</span>`;
  d.classList.toggle("shut",i>=2);d.dataset.kinds=Object.keys(own).join(" ")});
 const open=(d,on)=>{d.classList.toggle("shut",!on);d.querySelector(".chtog").setAttribute("aria-expanded",on)};
 el("main").querySelector(".room3").insertAdjacentHTML("afterend",`<div class="chbar"><div class="chips" role="group" aria-label="${T("All kinds")}"><button type="button" class="chip" data-ck="" aria-pressed="true">${T("All kinds")}</button>${Object.keys(cnt).map(k=>`<button type="button" class="chip ck ${k}" data-ck="${k}" aria-pressed="false">${KN[k]} <span class="n">${cnt[k]}</span></button>`).join("")}</div>
 <div class="chips" role="group" aria-label="${T("Changes")}">${days.map(d=>`<button type="button" class="chip" data-day="${d.id}">${d.querySelector(".chtog").textContent}</button>`).join("")}</div></div>`);
 // listeners go on what this draw made (<main> itself outlives the page and would collect one more each visit)
 days.forEach(d=>d.querySelector(".chtog").onclick=e=>open(d,e.currentTarget.getAttribute("aria-expanded")!=="true"));
 el("main").querySelector(".chbar").addEventListener("click",e=>{const c=e.target.closest(".chip");if(!c)return;
  if(c.dataset.day){const d=el(c.dataset.day);open(d,true);d.scrollIntoView({behavior:RM?"auto":"smooth",block:"start"});return}
  const k=c.dataset.ck;c.parentNode.querySelectorAll(".chip").forEach(b=>b.setAttribute("aria-pressed",b===c));
  if(k)el("main").dataset.ck=k;else delete el("main").dataset.ck;
  // one kind: every day that has it opens and shows that kind only; a day without it steps aside
  days.forEach((d,i)=>{const has=!k||d.dataset.kinds.split(" ").includes(k);d.hidden=!has;d.querySelectorAll("[data-k]").forEach(x=>x.classList.toggle("on",x.dataset.k===k));if(k&&has)open(d,true)})});
}

/* the wiki-wide groups every detail page ends with; extra = this page's own groups, put first */
function wikiNav(cur,extra){cur=cur||{};const a=cur.act!=null&&ACT[cur.act]&&ORDER.includes(cur.act)?cur.act:null;
 return navbox("Linggango Wiki",[...(extra||[]),
  [T("Bosses"),KEEPERS().map(k=>["#boss/"+k,esc(bossName(k)),k===cur.boss])],
  [T("The Path"),ORDER.filter(x=>x>=0).map(x=>["#act/"+x,esc(actL(x)),x===a])],
  [a!=null?T("Equipment at {act}",{act:esc(actL(a))}):T("Equipment"),[["ME",T("Melee")],["RA",T("Ranged")],["MA",T("Mage")],["SU",T("Summon")]].map(([r,t])=>[`#gear/${a!=null?a:ORDER[0]}/${r}/w`,t]).concat([[`#gear/${a!=null?a:ORDER[0]}/ME/a`,T("Armor sets")]])],
  [T("Tools"),[["#build",T("Build planner")],["#bosses",T("Bosses")],["#mechanics",T("Mechanics")],["#changes",T("Changes")]]]])}
function activeBar(){const P=[];
 st.c.forEach(k=>P.push(["c",k,ROLE[k]]));st.r.forEach(k=>P.push(["r",k,RN[k]]));st.x.forEach(k=>P.push(["x",k,k.slice(2)]));st.g.forEach(k=>P.push(["g",k,k]));
 if(st.nw)P.push(["nw","",T("New in 6.6.6")]);if(st.m)P.push(["m","",st.m]);if(st.s)P.push(["s","",T("Slot {s}",{s:T(st.s)})]);if(st.a!=="")P.push(["a","",T("Up to {act}",{act:actL(st.a)})]);if(st.q)qTokens().forEach(e=>P.push(["qt",e.raw,qLabel(e)]));
 return P.length?`<div class="act-bar" role="group" aria-label="${T("Active filters")}">${P.map(([k,v,t])=>`<button class="pill" data-k="${k}" data-v="${esc(v)}" aria-label="${esc(T("Remove filter {t}",{t}))}">${esc(t)}<b aria-hidden="true">×</b></button>`).join("")}<button class="ghost" id="clr2">${T("Clear all")}</button></div>`:""}

/* ---------- views ---------- */
/* The Path on the home page: a track of Act frames on an XP bar, and one panel per Act (side bosses, next Keeper, best weapon).
   "I'm here" marks your run in this browser; the bar fills to it and the Acts after it fade. */
const PHKEY="lgw-here";
const pHere=()=>{try{const v=localStorage.getItem(PHKEY);return v===null?null:+v}catch(e){return null}};
/* the saved Act when it is on The Path, else null (a stale or edited value must not close every Act) */
const hereOn=()=>{const h=pHere();return h!==null&&ACT[h]&&ORDER.includes(h)?h:null};
/* Title screen: one button carries the reader's run ("I'm here"), the rest of the wiki is in the top bar */
const hereBtns=()=>{const h=hereOn(),ok=h!==null;
 return ok?`<a class="mcb wide" href="#home">${T("Continue: {act}",{act:esc(actL(h))})}</a><a class="mcb" href="#gear/${h}/ME/w">${T("Gear at {act}",{act:esc(actL(h))})}</a><a class="mcb" href="#build">${T("Build planner")}</a>`
  :`<a class="mcb wide" href="#home">${T("Browse curios")}</a><a class="mcb" href="#gear">${T("Equipment")}</a><a class="mcb" href="#build">${T("Build planner")}</a>`};
function pSide(a){const pi=typeof PIMG!=="undefined"?PIMG:{side:{},act:{}};
 let sb=(typeof BOSSR!=="undefined"?BOSSR:[]).filter(r=>r[1]===a&&!/Keeper/.test(r[0])&&!/^(Ender Dragon)\b/.test(r[0]));if(a===6&&!sb.some(r=>r[0]==="Warden"))sb=[["Warden",6,"","Ancient City: shriek three Sculk Shriekers to call it",[]],...sb];
 return sb.length?[...sb].sort((x,y)=>(!!pi.side[y[0]]||!!(typeof SIDEB!=="undefined"&&SIDEB[y[0]]&&SIDEB[y[0]].img))-(!!pi.side[x[0]]||!!(typeof SIDEB!=="undefined"&&SIDEB[x[0]]&&SIDEB[x[0]].img))).map(r=>{const sb2=typeof SIDEB!=="undefined"&&SIDEB[r[0]],rim=sb2&&sb2.img,im=pi.side[r[0]]||(rim&&((pi.scene&&pi.scene[r[0]])||(pi.biome&&pi.biome[r[0]]))),vk=r[0]==="Warden"?"warden":r[0]==="Wither"?"wither":null,hr=vk?` href="#boss/${vk}"`:sb2?` href="#side/${enc(r[0])}"`:"";return rim||im?`<a class="pbc${rim?" rnd":""}"${hr} title="${esc(pathText(r[3]||""))}">${im||(pi.scene&&pi.scene[r[0]])?`<img class="bg" alt="" loading="lazy" src="${im||pi.scene[r[0]]}">`:""}${rim?`<img class="fg" alt="" src="${rim}">`:""}<b>${esc(r[0])}</b></a>`:(()=>{const bg=(pi.scene&&pi.scene[r[0]])||(pi.biome&&pi.biome[r[0]]),it=[sb2&&sb2.summon].concat(r[4]||[],sb2&&sb2.drops?sb2.drops.map(x=>x.id):[]).find(x=>x&&IC[x]);return `<a class="pbc ibg"${hr} title="${esc(pathText(r[3]||""))}">${bg?`<img class="bg" alt="" loading="lazy" src="${bg}">`:""}${it?`<span class="fgi">${img(it)}</span>`:""}<b>${esc(r[0])}</b></a>`})()}).join(""):""}
function pPanel(a,i,eager){return `<div class="ppanel" id="pp-${i}" role="tabpanel" aria-labelledby="pn-${i}" style="--tc:${ACT[a][2]};${tex(a)}"${i?" hidden":""}>${eager?pPanelInner(a):""}</div>`}
function pPanelInner(a){const xs=D.filter(d=>d.t===a),m=xs.filter(isMust).length,nb=NEXTB[a],sides=pSide(a),ti=typeof PIMG!=="undefined"&&PIMG.act[String(a)];
 const nSide=(sides.match(/class="pbc/g)||[]).length,gt=typeof gTiers==="function"&&gTiers(a,"ME","w"),bw=gt&&gt.length&&gt[0][1][0];
 return `<div class="pph">${ti?`<img class="ptitle" alt="${esc(actL(a))}" src="${ti}"><h3 class="ptxt">${esc(actL(a))}</h3>`:`<h3>${esc(actL(a))}</h3>`}<p>${a?T("Opens when {boss} falls.",{boss:esc(T(UNL[a]))}):T("Where every run starts: no Keeper to beat yet.")}</p></div>
 <div class="ppg"><div class="ppl">
  <dl class="pstat"><div><dt>${T("Curios")}</dt><dd>${xs.length}</dd></div><div><dt>${T("Must-Have")}</dt><dd>${m}</dd></div><div><dt>${T("Side bosses")}</dt><dd>${nSide}</dd></div></dl>
  ${nb?`<a class="pnext" href="#boss/${nb}">${emblem(bossPath(nb)??a,"sm")}<span><small>${VBOSS[bossPath(nb)]?T("Boss to beat next"):T("Keeper to beat next")}</small><b>${esc(bossName(nb))}</b></span></a>`:`<p class="pnext end"><span><small>${T("Keeper to beat next")}</small><b>${T("None: this is the last Act")}</b></span></p>`}
  ${bw?`<a class="pnext" href="#g${bw.ix}" data-t="g${bw.ix}"><span class="slot sm">${gImg(bw)}</span><span><small>${T("Best melee weapon here")}</small><b>${esc(TD(bw.n))}</b></span></a>`:""}
  <div class="pbtn"><a class="mcb" href="#act/${a}">${TN(xs.length,"See {n} curio","See {n} curios")}</a><a class="mcb" href="#gear/${a}/ME/w">${T("See gear")}</a><button class="mcb phere" type="button" data-here="${a}" aria-pressed="false">${T("I'm here")}</button></div>
 </div><div class="pside">${envFx(a)}${sides||`<p class="pnone">${T("No side bosses at this Act. Gear up for the Keeper.")}</p>`}</div></div>
 ${xs.length?`<div class="chest"><p class="cht">${esc(actL(a))}: ${T("Curios")}</p>${slotRow(byRank(xs).slice(0,CHESTN).map(d=>({...rCurio(d,"",1),c:" r"+d.r})),actL(a)+": "+T("Curios"))}</div>`:""}`}
/* how many curios an Act's chest shows on the home page (two rows of a wide screen), and how many a shelf of the rack shows (one row) */
const CHESTN=36,SHELFN=30;
/* the dusk sky behind The Path: stars and two far ridges, the same on every load (a seeded generator, no data), and what
   moves in it: clouds that drift across, a few birds, gusts of wind (CSS; the sun's light too). The layers shift a little
   with the pointer (pathMapWire: --mx, --my). */
/* The Path's sky as pixel art, drawn once per size (PX css px to an art pixel): behind the sun, the sky (the page's gradient as dithered colour bands, a warm glow round the sun, stars);
   in front of it, the land (three ridges with a castle and pines, mist between them, three floating islands); and three cloud sprites (violet tops, undersides the sun still lights).
   Seeded, so every visit draws the same sky. Returns {back, front (ImageData), clouds: [data URLs]}. */
function skyArt(w,h,PX){
 const W=Math.ceil(w/PX),H=Math.ceil(h/PX);let q=11;const R=()=>(q=q*16807%2147483647)/2147483647;
 const hex=s=>[1,3,5].map(i=>parseInt(s.slice(i,i+2),16)),mix=(a,c,t)=>a.map((v,i)=>v+(c[i]-v)*t);
 const BAY=(x,y)=>([0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5][(y&3)*4+(x&3)]+.5)/16;
 const buf=(Hb=H)=>{const c=document.createElement("canvas");c.width=W;c.height=Hb;const x=c.getContext("2d"),im=x.createImageData(W,Hb),d=im.data;
  // put: a pixel over what is there (a < 1 blends)
  const put=(X,Y,c,a=1)=>{if(X<0||Y<0||X>=W||Y>=Hb)return;const i=(Y*W+X)*4,da=d[i+3]/255,oa=a+da*(1-a);if(a>=1||!da){d[i]=c[0];d[i+1]=c[1];d[i+2]=c[2];d[i+3]=a*255;return}
   for(let k=0;k<3;k++)d[i+k]=(c[k]*a+d[i+k]*da*(1-a))/oa;d[i+3]=oa*255};
  const rect=(X,Y,w,h,c,a)=>{for(let j=0;j<h;j++)for(let i=0;i<w;i++)put(X+i,Y+j,c,a)};
  return {c,x,im,put,rect}};
 // 1 the sky: the page's gradient in 24 dithered bands, a warm glow round the sun, the sun itself, stars, a moon, long streaks of high cloud
 const B=buf(),ST=[[0,"#141038"],[.24,"#2e1d62"],[.46,"#6d2f7c"],[.64,"#c8506d"],[.80,"#f58a54"],[.93,"#ffc66e"],[1,"#ffe3a0"]].map(([t,c])=>[t,hex(c)]);
 const at=t=>{for(let i=1;i<ST.length;i++)if(t<=ST[i][0]){const [t0,c0]=ST[i-1],[t1,c1]=ST[i];return mix(c0,c1,(t-t0)/(t1-t0))}return ST.at(-1)[1]};
 const Hh=Math.min(H,220),O=H-Hh,F=buf(Hh),noise=sc=>{const p=[...Array(48)].map(R);return x=>{const u=x/sc,i=Math.floor(u),t=u-i,s=t*t*(3-2*t);return p[i%48]*(1-s)+p[(i+1)%48]*s}};
 const ridge=(base,amp,sc,oct)=>{const ns=oct.map(o=>noise(sc/o));return x=>{let v=0,a=1,s=0;oct.forEach((o,i)=>{v+=ns[i](x)*a;s+=a;a*=.5});return base-amp*v/s}};
 const hz=Hh*.72,R0=ridge(hz-Hh*.14,Hh*.15,84,[1,2,5]),R1=ridge(hz-Hh*.08,Hh*.16,70,[1,2,4]),R2=ridge(hz+Hh*.02,Hh*.13,46,[1,2.5,5]),R3=ridge(hz+Hh*.14,Hh*.12,36,[1,2,4]);
 const N=24,bands=[...Array(N)].map((_,i)=>at(i/(N-1))),sunX=.175*W+15,sunY=O+Math.round(R0(sunX))-3;   // the sun sits just above the far range's crest: half of its disc shows
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){const t=y/H*(N-1),i=Math.min(N-2,Math.floor(t));let c=bands[i+(t-i>BAY(x,y)?1:0)];
  const d=Math.hypot((x-sunX)/1.8,y-sunY),g=Math.max(0,1-d/(H*.5)),l=Math.floor(g*g*5+BAY(x,y)-.25);if(l>0)c=mix(c,[255,196,110],Math.min(.46,l*.1));B.put(x,y,c)}
 // the sun: a disc of four bands of light, dithered into each other (its lower half is behind the far range); the rays (CSS .dsun::before) turn round its middle
 const SC=[[255,249,218],[255,234,156],[255,208,112],[255,176,88]];
 for(let y=Math.floor(sunY-24);y<=sunY+24;y++)for(let x=Math.floor(sunX-24);x<=sunX+24;x++){const d=Math.hypot(x-sunX,y-sunY);if(d>17.2){if(d<24&&(1-(d-17.2)/6.8)*.36>BAY(x,y)*.5)B.put(x,y,[255,206,140],.2);continue}B.put(x,y,SC[Math.max(0,Math.min(3,Math.floor(Math.pow(d/17.2,1.5)*4+(BAY(x,y)-.5)*.7)))])}
 for(let k=0;k<120;k++){const x=Math.floor(R()*W),y=Math.floor(Math.pow(R(),1.7)*H*.5),sc=[[255,244,230],[255,244,230],[198,214,255],[255,204,226]][Math.floor(R()*4)];if(Math.hypot((x-sunX)/1.8,y-sunY)<H*.3)continue;B.put(x,y,sc,.3+R()*.5);if(R()<.07){B.put(x-1,y,sc,.7);B.put(x+1,y,sc,.7);B.put(x,y-1,sc,.7);B.put(x,y+1,sc,.7)}}
 // the moon, opposite the sun: a crescent, its dark part just there, a halo of dither
 {const mx=Math.round(W*.78),my=Math.round(H*.1);
  for(let y=-11;y<=11;y++)for(let x=-11;x<=11;x++){const d=Math.hypot(x,y),e=Math.hypot(x-3,y+1.5);
   if(d<=6.2)B.put(mx+x,my+y,e>5.4?[238,238,254]:[120,104,176],e>5.4?1:.35);else if(d<11&&(1-(d-6.2)/4.8)*.5>BAY(mx+x,my+y)*.55)B.put(mx+x,my+y,[196,190,255],.16)}}
 // high cloud: thin streaks warmed from below, tapering at both ends
 for(let k=0;k<8;k++){const y=Math.floor(H*(.14+R()*.34)),x0=Math.floor(R()*W*.9),len=22+Math.floor(R()*44),base=at(y/H);
  for(let i=0;i<len;i++){const a=.5*Math.pow(Math.sin(Math.PI*i/len),1.3);if(a>BAY(x0+i,y)*.55)B.put(x0+i,y,mix(base,[255,176,128],.5),Math.min(.8,a+.2));if(i>4&&i<len-4&&R()<.7)B.put(x0+i+3,y+1,mix(base,[255,150,110],.4),a*.5)}}
 // cloud banks: heaps of discs with a flat underside and puffs on top. The shape comes first (a mask), then the light, in bands of depth from the top edge: a rim of pale pink-gold, a lilac upper body (the
 // sky's colour), a violet core, and the sun's orange along the underside (the sun is below the cloud), each band dithered into the next; the core is a little darker away from the sun
 const bank=(cx,cy,w,hg,seed)=>{let z=seed*7919;const rz=()=>(z=z*16807%2147483647)/2147483647,n=4+Math.floor(w/7),D=[],pf=t=>Math.pow(Math.sin(Math.PI*(.08+.84*t)),1.2);
  for(let i=0;i<n;i++){const t=(i+.5)/n,r=hg*(.32+.68*pf(t))*(.72+.45*rz());D.push([cx+(t-.5)*w+(rz()-.5)*4,cy-r*.28,r])}
  for(let i=0;i<Math.floor(n*.8);i++){const t=.1+.8*rz(),r=hg*(.26+.22*rz());D.push([cx+(t-.5)*w,cy-hg*(.5+.6*pf(t))+r*.3,r])}
  const x0=Math.floor(cx-w/2-hg),x1=Math.ceil(cx+w/2+hg),y0=Math.floor(cy-hg*1.8),base=Math.round(cy+hg*.3),gw=x1-x0+1,m=new Uint8Array(gw*(base-y0+1)),
   cov=(x,y)=>x>=x0&&x<=x1&&y>=y0&&y<=base&&m[(y-y0)*gw+x-x0];
  for(let y=y0;y<=base;y++)for(let x=x0;x<=x1;x++)for(const [dx,dy,r] of D){const u=(x-dx)/r,v=(y-dy)/(r*.85);if(u*u+v*v<1){m[(y-y0)*gw+x-x0]=1;break}}
  for(let y=y0;y<=base;y++)for(let x=x0;x<=x1;x++){if(!cov(x,y))continue;
   let up=0,lf=0;while(cov(x,y-up-1))up++;while(cov(x-lf-1,y))lf++;
   const dn=base-y,rim=Math.max((2.2-up)/2.2,(1.8-lf)/1.8*(up<hg*.8?1:0)),und=1-dn/(hg*.42),top=1-up/(hg*.62),sk=at(y/H),bay=BAY(x,y),away=Math.max(0,Math.min(1,(x-cx)/(w*.6)+.4)),wm=Math.max(0,1-Math.hypot((x-sunX)/1.8,y-sunY)/(H*.85)),wr=c=>mix(c,[255,166,132],wm*.55);
   B.put(x,y,rim>bay*.9?mix(sk,[255,222,176],.85):und>bay?wr(mix(sk,[246,146,128],.65)):top>bay?wr(mix(sk,[196,122,172],.6)):wr(mix(mix(sk,[100,54,134],.7),[58,28,94],away*.4)),.96)}};
 (W<200?[[.74,.64,.34,8,4],[.22,.70,.30,7,5]]:[[.41,.49,.18,19,1],[.57,.36,.12,14,2],[.11,.35,.13,15,3],[.88,.40,.13,17,4],[.66,.57,.10,10,5]]).forEach(([fx,fy,fw,fh,sd])=>bank(Math.round(W*fx),Math.round(H*fy),Math.round(W*fw),fh,sd));
 // 2 the land: the far range (hazy), a crag of dark rock on it with a castle, mist, the far ridge, the middle ridge, floating islands, the near ridge with pines
 const layer=(fn,col,haze,lit,deco)=>{for(let x=0;x<W;x++){const top=Math.round(fn(x));for(let y=top;y<Hh;y++){let c=mix(col,at((y+O)/H),haze);if(y-top<2&&fn(x+2)>fn(x-2)+.5)c=mix(c,lit,y===top?.5:.28);F.put(x,y,c)}}if(deco)deco()};
 const mist=(y0,hh,a)=>{for(let y=y0;y<y0+hh;y++)for(let x=0;x<W;x++)if((1-(y-y0)/hh)*a>BAY(x,y)*.9)F.put(x,y,[255,176,120],.3)};
 // (the crag's flat top stands 16 art px, 64, over the lowest point of the range's crest under it, so rock shows all round)
 // the crag: a flat top 52 wide, steep sides that run down into the range; the castle stands on the flat, wall to wall, with a gate, a keep, a tall tower and two more,
 // the sun's side (left) lit, a few windows lit
 const nar=W<200,cx0=Math.round(W*(nar?.66:.70)),hw=nar?15:26,top=Math.round(Math.min(R0(cx0),R0(cx0-hw),R0(cx0+hw)))-(nar?15:16),nz=noise(9),nz2=noise(5),
  crag=x=>{const ax=Math.abs(x-cx0);if(ax<=hw)return top+(nz2(x)-.5)*2+(ax>hw-4?(ax-hw+4)*.5:0);const o=ax-hw;return top+2+Math.floor(o/5)*3.5+(o%5)*.5+o*.34+(nz(x*1.7)-.5)*7},
  bx=cx0-hw-(nar?14:26),bt=top+(nar?10:18),butte=x=>{const dx=Math.abs(x-bx);return dx<=(nar?3:5)?bt+dx*dx*.14:bt+3+(dx-(nar?3:5))*2.6},
  rock=x=>Math.min(crag(x),butte(x)),cragFn=x=>{const c=rock(x);return c<R0(x)-1?c:Infinity};
 layer(ridge(hz-Hh*.1,Hh*.07,150,[1,3]),hex("#a05aa4"),.8,[255,206,156]);   // a pale, far range that shows only in the valleys of the next
 layer(cragFn,hex("#552a72"),.18,[255,184,124],()=>{
  for(let x=cx0-hw-70;x<=cx0+hw+60;x++){const c=Math.round(rock(x)),f=Math.round(R0(x));if(c>=f-1)continue;for(let y=c+1;y<f;y++){   // light from the left across the whole rock, strata that tilt, grain
   const sh=Math.max(0,Math.min(1,(x-(cx0-hw*.5))/(hw*2.4)));if(sh>0)F.put(x,y,[22,8,42],.46*sh);if(x<cx0)F.put(x,y,[255,190,130],Math.max(0,.2*(1-(x-(cx0-hw-10))/(hw+10))));
   if((y+(x>>2))%8===0&&(x+y)%5!==0)F.put(x,y,[28,12,48],.24);if(R()<.025)F.put(x,y,[255,190,130],.14)}}
  {let px=cx0-hw*.6,py=Math.round(R0(cx0-hw*.6))-1;while(py>top+1){px+=(py%4<2?1:-.5);py-=1;if(Math.round(px)<=cx0+3&&py%2===0)F.put(Math.round(px),py,[255,210,150],.55)}}   // a path up to the gate
  for(let k=0;k<(nar?3:7);k++){const x=cx0-hw-14+Math.floor(R()*(2*hw+28)),y=Math.round(rock(x));if(y<R0(x)-4&&Math.abs(x-cx0)>hw-2&&Math.abs(x-bx)>(nar?4:6)){const h=4+Math.floor(R()*4);for(let j=0;j<h;j++){const wj=Math.ceil((j+1)/2);F.rect(x-Math.floor(wj/2),y-h+j+1,wj,1,[26,10,44])}}}
  const cl=hex("#2d1450"),rf=hex("#240f3e"),lt=mix(cl,[255,190,130],.5),wn=[255,200,122],by=top,r=(x,y,w,h,c=cl,a=1)=>F.rect(cx0+x,by-y-h,w,h,c,a),
   roof=(xc,baseY,hw2,hg)=>{for(let j=0;j<hg;j++){const w=Math.max(1,Math.round(hw2*2*(1-j/hg)));F.rect(cx0+xc-Math.floor(w/2),by-baseY-j-1,w,1,rf)}};
  const ww=nar?13:23;r(-ww,0,2*ww,6);for(let x=-ww;x<ww;x+=4)r(x,6,2,2);                       // the wall and its merlons
  r(-5,0,10,12);r(-5,12,3,2);r(2,12,3,2);r(-1,0,2,6,[255,168,98]);        // the gatehouse and its lit gate
  r(-9,6,18,9);for(let x=-9;x<9;x+=4)r(x,15,2,2);                          // the keep
  r(-3,15,6,9);roof(0,24,5,6);r(0,30,1,6,rf);r(1,34,3,2,[255,118,108]);   // the tall tower, its roof and its flag
  if(!nar){r(-30,0,8,16);r(-31,16,10,2);roof(-26,18,6,7);                  // the tower on the left
   r(22,0,8,12);r(21,12,10,2);roof(26,14,6,6);                             // the tower on the right
   r(-30,0,1,16,lt,.85);r(22,0,1,12,lt,.7);[[-27,9],[-27,4],[25,6]].forEach(([x,y])=>r(x,y,1,2,wn))}
  r(-ww,0,1,6,lt,.85);r(-9,6,1,9,lt,.8);r(-3,15,1,9,lt,.8);
  [[0,19],[-6,10],[5,10]].forEach(([x,y])=>r(x,y,1,2,wn));r(-3,0,1,6,[255,168,98],.4)});
 layer(R0,hex("#8a4a98"),.6,[255,196,140]);   // the far range comes after the crag, so only the rock above its crest shows (a crag laid over it stood in it like a box)
 mist(Math.round(hz-Hh*.02),Math.round(Hh*.05),.55);
 layer(R1,hex("#7a3a86"),.5,[255,190,130]);
 mist(Math.round(hz+Hh*.04),Math.round(Hh*.05),.4);
 layer(R2,hex("#4a2368"),.2,[255,170,110],()=>{for(let k=0;k<22;k++){const x=Math.floor(R()*W),y=Math.round(R2(x)),h=3+Math.floor(R()*4);for(let j=0;j<h;j++){const wj=Math.ceil((j+1)/2);F.rect(x-Math.floor(wj/2),y-h+j,wj,1,hex("#3a1c5c"))}}});
 mist(Math.round(hz+Hh*.12),Math.round(Hh*.05),.36);
 const island=(cx,cy,w,hh,s)=>{const c=hex("#3a1a58"),top=hex("#5a3478"),lit=[255,184,120];
  for(let x=-w;x<=w;x++){const e=1-Math.pow(Math.abs(x)/w,1.6),yt=cy-Math.round(1+e*2),yb=cy+Math.round(hh*e*e*(.6+.4*Math.sin(x*.7+s)));
   for(let y=yt;y<=yb;y++){let col=y<=cy?top:mix(c,[20,8,36],(y-cy)/hh*.7);if(y===yt)col=mix(top,lit,x<w*.2?.55:.22);F.put(cx+x,y,col)}}
  const tx=cx-Math.round(w*.3),dk=hex("#2b1445");F.rect(tx,cy-3,1,3,dk);F.rect(tx-1,cy-6,3,3,dk);F.rect(tx,cy-8,1,2,dk);F.rect(cx+Math.round(w*.35),cy-3,1,2,[255,200,130]);
  const wx=cx+Math.round(w*.55);for(let y=cy;y<cy+hh*1.6;y++)F.put(wx,y,[255,210,170],.35)};
 if(nar){island(Math.round(W*.24),Math.round(Hh*.30),8,6,1);island(Math.round(W*.84),Math.round(Hh*.16),6,5,2.4);island(Math.round(W*.46),Math.round(Hh*.10),5,4,4)}
 else{island(Math.round(W*.52),Math.round(Hh*.40),10,8,1);island(Math.round(W*.89),Math.round(Hh*.34),8,7,2.4);island(Math.round(W*.33),Math.round(Hh*.50),6,5,4)}
 layer(R3,hex("#2c1648"),.05,[255,150,100],()=>{for(let k=0;k<26;k++){const x=Math.floor(R()*W);if(x>W*.2&&x<W*.3&&R()<.8)continue;const y=Math.round(R3(x)),h=4+Math.floor(R()*6);for(let j=0;j<h;j++){const wj=Math.ceil((j+1)/2);F.rect(x-Math.floor(wj/2),y-h+j,wj,1,hex("#1f0f36"))}}});
 // 3 clouds: 44 x 17 art pixels, a flat underside and a top made of puffs; violet on top, the sun's colour underneath, the left edge (the sun's side) lit
 const clouds=[3,7,12].map(s=>{const cw=44,ch=17,C=document.createElement("canvas");C.width=cw;C.height=ch;const x=C.getContext("2d");let z=s*977;const r=()=>(z=z*16807%2147483647)/2147483647;
  const base=ch-2,puffs=[...Array(6)].map((_,k)=>({cx:4+k*7+Math.round(r()*3),rx:4.5+r()*3.5,ry:(3+r()*5)*(.55+.9*Math.sin(Math.PI*(k+.5)/6))})),inC=(i,j)=>j<=base&&puffs.some(p=>((i-p.cx)/p.rx)**2+((j-base)/p.ry)**2<=1);
  for(let i=0;i<cw;i++){let top=-1;for(let j=0;j<=base;j++)if(inC(i,j)){top=j;break}if(top<0)continue;
   for(let j=top;j<=base;j++){const t=(j-top)/Math.max(1,base-top),lit=!inC(i-1,j)||!inC(i-2,j),c=mix([112,66,146],[255,172,124],Math.pow(t,1.3)),k=lit?mix(c,[255,214,170],.45):c;
    x.fillStyle=`rgba(${k.map(Math.round)},${.7-.12*(1-t)})`;x.fillRect(i,j,1,1)}}
  return C.toDataURL()});
 // the land stands on the foot of the scene, at most 220 art pixels (880) tall: on a phone, where the hero is a column of sky, it does not climb to the text
 const FD=new ImageData(W,H);FD.data.set(F.im.data,O*W*4);
 return {back:B.im,front:FD,clouds,sunb:Math.round((H-sunY)*PX-60)}}   // pixel data, not canvases: a canvas kept in the cache can come back empty (it did, after thousands of page draws in check.js)

/* the hero's sky and land painted into its two canvases, and the cloud sprites into --cl0..2; one painting per size is kept (a second visit paints nothing) */
const SKYC={};
function skyPaint(cl){const a=cl.querySelector(".dart0"),b=cl.querySelector(".dart1"),d=cl.querySelector(".dsky");if(!a||!b||!d)return;
 const w=cl.clientWidth+48,h=cl.clientHeight,k=w+"x"+h;if(!w||!h)return;let c=SKYC[k];if(!c){const ks=Object.keys(SKYC);if(ks.length>3)delete SKYC[ks[0]];c=SKYC[k]=skyArt(w,h,4)}
 for(const [cv,src] of [[a,c.back],[b,c.front]]){cv.width=src.width;cv.height=src.height;cv.getContext("2d").putImageData(src,0,0)}
 c.clouds.forEach((u,i)=>d.style.setProperty("--cl"+i,`url(${u})`));cl.style.setProperty("--sunb",c.sunb+"px")}
const SKY=(()=>{let q=7;const r=()=>(q=q*16807%2147483647)/2147483647;
 const stars=Array.from({length:90},()=>{const big=r()<.18;return `${(r()*100).toFixed(2)}vw ${r()*300|0}px 0 ${big?1:0}px rgba(255,255,255,${(.35+r()*.6).toFixed(2)})`}).join(",");
 /* the sky and the land are two canvases (skyPaint): the sky behind the sun and the clouds, the land in front of them */
 return `<div class="dsky" aria-hidden="true"><canvas class="dart0"></canvas><i class="dstars" style="box-shadow:${stars}"></i><i class="dsun"></i>${[[37,.8,230,0],[44,.55,300,.22],[40,.45,360,.47],[49,.7,260,.63],[35,.5,330,.85]].map(([y,z,d,o],k)=>`<i class="dcl" style="top:${y}%;scale:${z};--cd:${d}s;--cdl:-${(d*o).toFixed(0)}s;--cx:${(o*100).toFixed(0)}vw;background-image:var(--cl${k%3})"></i>`).join("")}<canvas class="dart1"></canvas>${[[22,64,0],[31,78,-23],[14,92,-47]].map(([y,d,l])=>`<i class="dbirds" style="top:${y}%;--bd:${d}s;--bdl:${l}s"><b></b><b></b><b></b></i>`).join("")}${[[38,0],[52,-4],[27,-8]].map(([y,l])=>`<i class="dwind" style="top:${y}%;--wl:${l}s"></i>`).join("")}</div>`})();
/* a boss's figure: the strip of its idle loop (BFIG) in a box one frame wide; z = shown px per strip px (the strip's own when
   left out); "" when the boss has no figure. cardFig: the picture on a boss's card in the Bosses list, fitted to a 112x116 box:
   its figure, else its portrait (the Warden and the Wither), else nothing (the caller puts the Act's emblem). */
const figHtml=(k,z,at="")=>{const f=typeof BFIG!=="undefined"&&BFIG[k];return f?`<span class="pk${f.n>1?"":" st"}"${at} style="--w:${f.w};--h:${f.h};--n:${f.n};--z:${z??f.z};--ms:${f.ms}"><img alt="" decoding="async" src="${f.src}"></span>`:""};
const figFit=(k,w,h)=>{const f=BFIG[k];return +Math.min(h/f.h,w/f.w).toFixed(3)};
const cardFig=k=>typeof BFIG!=="undefined"&&BFIG[k]?`<span class="bfig">${figHtml(k,figFit(k,128,112))}</span>`:typeof BPORT!=="undefined"&&BPORT[k]?`<span class="bfig"><img class="bst" alt="" decoding="async" src="data:image/png;base64,${BPORT[k]}"></span>`:"";
/* a Keeper's short name for its step: "Arion, Tyrant of the Emerald Wrath" => "Arion" */
const kShort=k=>bossNameT(k).split(",")[0].split(/ the /)[0].replace(/^The /,"");
/* the last Act has no Keeper to beat: its step shows the Act's end-game boss, a side boss ([figure key in BFIG, name in SIDEB]) */
const ENDB={12:["apollyon","Apollyon"]};
/* five sparks that rise from a figure while it is the open or the pointed one (x offset, drift, delay) */
const SPARKS=[[-46,-14,0],[-18,10,.5],[8,-8,1],[30,16,.25],[52,-10,.8]].map(([x,dx,d])=>`<i class="sp" style="--x:${x}px;--dx:${dx}px;--d:${d}s"></i>`).join("");
/* The Path on the home page is the hero: each Act is a step of its own block, with the Keeper to beat there standing on it
   (BFIG: a strip of its idle loop, framed on its feet and sized by its in-game height; build/pack_audit/boss_portraits.js --figs).
   A step is a tab; its panel opens under the sky. Every Keeper plays its idle loop; the open step's Keeper and the pointed one
   grow, and the pointed one walks (BWALK, a second strip that comes with the late pictures: pathMapWire puts it in). Each step
   carries its Act's air (envFx) and a light that runs up the stairs (.sw). */
function pathMap(path,lead){
 return `<div class="pmap" id="pmap"><section class="title-scr climb">${SKY}
 ${lead}
 <div class="pcap"><h2 class="gt">${T("The Path")}</h2><p class="gs">${T("Pick an Act to see what it opens and who guards it. Press “I'm here” on the Act you reached and the map follows your run.")}</p><p class="prun" id="prun" aria-live="polite"></p></div>
 <div class="ptrack" role="tablist" aria-label="${T("Acts of The Path")}" style="--n:${path.length}"><div class="pxp" aria-hidden="true"><i id="pxpf"></i></div>
 ${path.map((a,i)=>{const k=NEXTB[a],e=!k&&ENDB[a],f=typeof BFIG!=="undefined"&&BFIG[k||(e&&e[0])];
  return `<button type="button" role="tab" class="pn${VBOSS[a]?" ch":""}" id="pn-${i}" data-i="${i}" aria-controls="pp-${i}" aria-selected="${!i}" tabindex="${i?-1:0}" style="--tc:${ACT[a][2]};--i:${i};${tex(a)}" title="${esc(actF(a))}" data-k="${k?esc(kShort(k)):e?esc(TD(e[1])):""}" data-fk="${k||(e?e[0]:"")}">${colFx(i)}<i class="sw"></i>${envFx(a)}<span class="pfr${f&&f.perch?" perch":""}" data-h="${esc(T("You are here"))}">${f?`<i class="au"></i>${figHtml(k||e[0],null,` data-bw="${(f.bw/f.w).toFixed(3)}"`)}${SPARKS}`:emblem(a,"lg")}</span><b>${esc(ACT[a][0])}</b></button>`}).join("")}</div></section>
 ${path.map((a,i)=>pPanel(a,i,!i)).join("")}
 ${D.some(d=>d.t===-1)?`<p class="gs side">${T("Side Act: {link}, dropped by L2 Hostility mobs by level, outside the Keeper order.",{link:`<a href="#act/-1">${T("L2 Artifacts")}</a>`})}</p>`:""}</div>`}
function pathMapWire(path){const map=el("pmap");if(!map)return;const tabs=[...map.querySelectorAll(".pn")],pans=[...map.querySelectorAll(".ppanel")];let cur=0;
 const tr=map.querySelector(".ptrack"),ctr=i=>{if(tr.scrollWidth>tr.clientWidth+1)tr.scrollLeft=tabs[i].offsetLeft-(tr.clientWidth-tabs[i].offsetWidth)/2};
 // the sky fills the screen under the header, whatever the header's height (it wraps in some languages and on phones)
 const top=document.querySelector(".top"),toph=()=>document.documentElement.style.setProperty("--toph",top.offsetHeight+"px");
 // a Keeper that is not the open or the pointed one keeps its body over its own step (a sword or a wing tip may reach
 // past it): a broad one is drawn smaller. The dragon flies behind the others and is left as it is.
 /* a step's full width: the grid cell it sits in (at rest the step itself is narrower, with sky beside it), or the step on a phone */
 const cell=t=>getComputedStyle(t.parentNode).display==="grid"?t.parentNode.clientWidth/tabs.length:t.offsetWidth;
 const fit=()=>tabs.forEach(t=>{const k=t.querySelector(".pk:not(.wk)");if(k&&k.offsetWidth&&!k.parentNode.classList.contains("perch"))k.parentNode.style.setProperty("--fit",Math.min(1,1.25*cell(t)/(k.offsetWidth*(+k.dataset.bw||1))).toFixed(3))});
 let wv=null;
 const sky=()=>skyPaint(map.querySelector(".climb"));
 toph();fit();requestAnimationFrame(sky);if(window.ResizeObserver){let st=0;const ro=new ResizeObserver(()=>{if(!map.isConnected){ro.disconnect();return}toph();fit();wv&&wv.resize();clearTimeout(st);st=setTimeout(sky,120)});ro.observe(top);ro.observe(tr);ro.observe(map.querySelector(".climb"))}
 // the walk loop of the Keeper under the pointer (or the keyboard): put in the first time, once its picture is ready
 const walk=t=>{const w=t&&!t.dataset.wk&&window.BWALK&&BWALK[t.dataset.fk],f=w&&BFIG[t.dataset.fk];if(!w)return;t.dataset.wk=0;const im=new Image();im.alt="";im.src=w.src;
  im.decode().then(()=>{const k=document.createElement("span");k.className="pk wk";k.style.cssText=`--w:${w.w};--h:${w.h};--n:${w.n};--z:${f.z};--ms:${w.ms}`;k.appendChild(im);t.querySelector(".pfr").appendChild(k);t.dataset.wk=1}).catch(()=>{})};
 tr.addEventListener("pointerover",e=>walk(e.target.closest(".pn")));tr.addEventListener("focusin",e=>walk(e.target.closest(".pn")));
 const paint=()=>{const h=pHere(),hi=h===null?-1:path.indexOf(h);
  tabs.forEach((t,i)=>{t.classList.toggle("done",hi>=0&&i<hi);t.classList.toggle("here",i===hi);t.classList.toggle("ahead",hi>=0&&i>hi)});
  el("pxpf").style.transform=`scaleX(${hi<0?0:(hi+.5)/path.length})`;
  map.querySelectorAll(".phere").forEach(b=>{const on=+b.dataset.here===h;b.setAttribute("aria-pressed",on);b.innerHTML=on?ui("check")+" "+T("You are here"):T("I'm here")});
  el("prun").textContent=hi<0?"":T("Your run: {act} ({i} of {n} on The Path)",{act:actL(h),i:hi+1,n:path.length})};
 const sel=(i,focus)=>{if(i===cur){if(focus)tabs[i].focus();return}const was=cur,dir=i>was?"next":"prev";cur=i;if(!pans[i].firstElementChild){pans[i].innerHTML=pPanelInner(path[i]);paint()}const swap=()=>{tabs.forEach((t,k)=>{t.setAttribute("aria-selected",k===i);t.tabIndex=k===i?0:-1});pans.forEach((p,k)=>p.hidden=k!==i);decorate(pans[i]);ctr(i)};
  if(focus)tabs[i].focus();
  if(RM||!document.startViewTransition){swap();return}
  pans[was].style.viewTransitionName="ppanel";document.documentElement.dataset.pvt=dir;
  const t=document.startViewTransition(()=>{pans.forEach(p=>p.style.viewTransitionName="");swap();pans[i].style.viewTransitionName="ppanel"});
  // a transition cut short by the next click rejects ready/finished ("Transition was skipped"): not an error
  t.ready.catch(()=>{});t.finished.catch(()=>{}).finally(()=>{pans[i].style.viewTransitionName="";delete document.documentElement.dataset.pvt})};
 map.addEventListener("click",e=>{const t=e.target.closest(".pn");if(t){sel(+t.dataset.i);return}
  const b=e.target.closest(".phere");if(b){const a=+b.dataset.here;try{pHere()===a?localStorage.removeItem(PHKEY):localStorage.setItem(PHKEY,a)}catch(e){}
   // a new run position drops the Acts opened by hand, so Continue lands on that Act; the title buttons follow at once
   st.op=null;save();paint();const tb=document.querySelector(".tbtns");if(tb)tb.innerHTML=hereBtns()}});
 /* The pointer over the hero. The sky's layers shift a little with it (--mx and --my on the sky, not on the whole hero: a custom property written on the hero makes every node under
    it, the thirteen steps included, work out its style again on every move: 10 ms each time, measured). On a desktop with a mouse the steps are a wave too: the one under the pointer
    grows to full size and its neighbours shrink, the nearer the more, and the sizes follow the pointer on springs, a frame at a time, so a step never jumps from one size to another as
    the pointer goes along the stairs. A frame writes only what moves (a step's height and sides, its numeral, its Keeper's scale), never a custom property on a step; the CSS (#pmap.wave)
    hands those over, and the pointer's own :hover goes to .hov (the step whose cell the pointer is in: cells do not move, steps do) so that nothing flickers as they change size. */
 {const cl=map.querySelector(".climb"),sk=cl.querySelector(".dsky"),mq=matchMedia("(min-width:1101px) and (hover:hover) and (pointer:fine)"),n=tabs.length,
   REST=parseFloat(getComputedStyle(cl).getPropertyValue("--rest"))||.66,pf=tabs.map(t=>t.querySelector(".pfr")),nb=tabs.map(t=>t.querySelector(":scope>b")),
   X=new Float64Array(n).fill(REST),V=new Float64Array(n),L=new Float64Array(n),LV=new Float64Array(n),TX=new Float64Array(n),TL=new Float64Array(n),F=new Float64Array(n).fill(1),B=new Float64Array(n),
   wx=new Float64Array(n).fill(-1),wl=new Float64Array(n).fill(-1),
   G=d=>Math.exp(-((d/.55)**2)),NB=d=>Math.exp(-(((d-1)/.8)**2))*(1-Math.exp(-((d/.5)**2))),SHRINK=.12,K=380,C=32,LIFT=24,LIFT_OPEN=12;
  let on=false,hov=-1,mx=NaN,my=NaN,tg=null,fr=0,last=0;
  const sel0=()=>tabs.findIndex(t=>t.getAttribute("aria-selected")==="true"),wake=()=>{if(!fr)fr=requestAnimationFrame(tick)};
  // a step's full height and its Keeper's fit, read with the CSS in charge; every step then holds its resting size inline (the Keeper's fit is folded into --sc, the CSS's --fit is 1 in the wave)
  const measure=()=>{tabs.forEach((t,i)=>{t.style.height=t.style.marginInline="";nb[i].style.fontSize="";pf[i].style.removeProperty("--sc")});
   const s0=sel0();tabs.forEach((t,i)=>{B[i]=(t.getBoundingClientRect().height-(i===s0?LIFT_OPEN:0))/REST;const f=parseFloat(pf[i].style.getPropertyValue("--fit"));F[i]=f>0?f:1;wx[i]=wl[i]=-1;X[i]=REST;V[i]=LV[i]=0;L[i]=i===s0?LIFT_OPEN:0});
   tabs.forEach((t,i)=>pf[i].style.setProperty("--sc",(.94*REST*(i===s0?1:F[i])).toFixed(4)))};
  const setHov=k=>{if(hov>=0)tabs[hov].classList.remove("hov");hov=k;if(k>=0){tabs[k].classList.add("hov");walk(tabs[k])}tr.classList.toggle("hv",k>=0)};
  const enable=()=>{if(on)return;on=true;map.classList.add("wave");measure()},
   disable=()=>{if(!on)return;on=false;map.classList.remove("wave");setHov(-1);tabs.forEach((t,i)=>{t.style.height=t.style.marginInline="";nb[i].style.fontSize="";pf[i].style.removeProperty("--sc")})};
  function tick(t){fr=0;const R=cl.getBoundingClientRect(),T=tr.getBoundingClientRect(),w=T.width/n,s0=sel0();
   if(!RM&&mx===mx){sk.style.setProperty("--mx",((mx-R.left)/R.width*2-1).toFixed(3));sk.style.setProperty("--my",((my-R.top)/R.height*2-1).toFixed(3))}
   if(!on){last=0;return}
   // the step under the pointer, by its cell and the air above it (not over the text of the hero), and the wave round it
   let k=-1;if(mx===mx&&tg&&!tg.closest(".pcap,.tact,.tcs,.lg")){const c=Math.floor((mx-T.left)/w);if(c>=0&&c<n&&my>=T.bottom-(B[c]+LIFT+330)&&my<=T.bottom)k=c}
   if(k!==hov)setHov(k);
   const pos=k>=0?(mx-T.left)/w-.5:0,dt=last?Math.min(.05,(t-last)/1000):.016,sub=Math.max(1,Math.ceil(dt*120)),h=dt/sub;last=t;let moving=false;
   for(let i=0;i<n;i++){const d=k>=0?Math.abs(pos-i):9,g=k>=0?G(d):0;TX[i]=k>=0?REST+(1-REST)*g-SHRINK*NB(d):REST;TL[i]=k>=0?LIFT*g:(i===s0?LIFT_OPEN:0);
    for(let q=0;q<sub;q++){V[i]+=(K*(TX[i]-X[i])-C*V[i])*h;X[i]+=V[i]*h;LV[i]+=(K*(TL[i]-L[i])-C*LV[i])*h;L[i]+=LV[i]*h}
    if(Math.abs(X[i]-TX[i])>.0015||Math.abs(V[i])>.01||Math.abs(L[i]-TL[i])>.05||Math.abs(LV[i])>.5)moving=true;else{X[i]=TX[i];V[i]=0;L[i]=TL[i];LV[i]=0}}
   for(let i=0;i<n;i++){const r=X[i],l=L[i];if(Math.abs(r-wx[i])<.0003&&Math.abs(l-wl[i])<.03)continue;wx[i]=r;wl[i]=l;
    const b=i===s0?1:F[i],gn=Math.max(0,Math.min(1,(r-REST)/(1-REST)));
    tabs[i].style.height=(B[i]*r+l).toFixed(2)+"px";tabs[i].style.marginInline=((1-r)*50).toFixed(3)+"%";nb[i].style.fontSize=(34*(.55+.45*r)).toFixed(2)+"px";pf[i].style.setProperty("--sc",(.94*r*(b+(1-b)*gn)).toFixed(4))}
   if(moving)fr=requestAnimationFrame(tick);else last=0}
  cl.addEventListener("pointermove",e=>{mx=e.clientX;my=e.clientY;tg=e.target;wake()},{passive:true});
  cl.addEventListener("pointerleave",()=>{mx=my=NaN;tg=null;wake()});
  // a click in the air above a step opens that step (the steps themselves take no pointer in the wave)
  cl.addEventListener("click",e=>{if(!on||hov<0||e.target.closest("a,button,input,select,label,.pcap,.tact,.tcs,.lg,.pn"))return;tabs[hov].click()});
  // the open step changes (a click, the arrow keys): its lift follows
  if(window.MutationObserver)new MutationObserver(()=>{if(on)wake()}).observe(tr,{attributes:true,attributeFilter:["aria-selected"],subtree:true});
  const sync=()=>{if(!RM&&mq.matches&&REST<1)enable();else disable()};
  sync();if(mq.addEventListener)mq.addEventListener("change",sync);
  wv={resize(){if(on){const was=hov;measure();wake();hov=was}else sync()}}}
 map.querySelector(".ptrack").addEventListener("keydown",e=>{const k={ArrowRight:1,ArrowLeft:-1,Home:-99,End:99}[e.key];if(!k)return;e.preventDefault();sel(Math.max(0,Math.min(path.length-1,k===-99?0:k===99?path.length-1:cur+k)),true)});
 const h=pHere(),hi=h===null?-1:path.indexOf(h);paint();if(hi>0){pans[0].hidden=true;tabs[0].setAttribute("aria-selected","false");tabs[0].tabIndex=-1;if(!pans[hi].firstElementChild){pans[hi].innerHTML=pPanelInner(path[hi]);paint()}pans[hi].hidden=false;tabs[hi].setAttribute("aria-selected","true");tabs[hi].tabIndex=0;cur=hi}ctr(cur)}
/* a shelf of the home page's rack, a display case: its title with the count and one line, then a link to all of it (or the playstyle buttons), over one tray
   of slots (SHELFN of them; CSS shows whole rows of the room it has) */
const shelf=(title,sub,slots,label,{ac="#7aa7ff",n=null,all=""}={})=>`<div class="shelf" style="--ac:${ac}"><header class="shh"><h2 class="gt">${title}</h2>${n!=null?`<span class="shn">${TN(n,"{n} curio","{n} curios")}</span>`:""}<p class="gs">${sub}</p>${all}</header><div class="chest">${slotRow(slots,label,SHELFN)}</div></div>`;
/* a shelf shows one row of its slots (two on a phone): as many as fit at the cell size; the others stay hidden until the window is wider */
function shelfFit(){const rows=innerWidth<=760?2:1;document.querySelectorAll(".rack .srow").forEach(r=>{const n=getComputedStyle(r).gridTemplateColumns.split(" ").length*rows;[...r.children].forEach((x,i)=>{x.hidden=i>=n})})}
function hubHome(){
 document.title="Linggango Wiki";document.body.classList.add("hub");
 const path=ORDER.filter(a=>a>=0&&D.some(d=>d.t===a)),news=D.filter(d=>d.nw),rc=d=>({...rCurio(d,"",1),c:" r"+d.r});
 const lead=`<h1 class="lg"><span class="vh">Linggango Wiki: </span>The Keepers are watching!</h1>
 <div class="tact"><form class="hsearch" id="hs" role="search"><input id="hq" type="search" name="hubq" spellcheck="false" placeholder="${T("Search curios, gear, bosses…")}" aria-label="${T("Search curios")}" autocomplete="off"></form>
 <nav class="tbtns" aria-label="${T("Start")}">${hereBtns()}</nav></div>
 <p class="tcs"><span class="tcorner">Linggango ${PACKV}</span><span class="tcorner">${TN(TOTAL,"{n} curio","{n} curios")}</span><span class="tcorner">${TN(MODS.length,"{n} mod","{n} mods")}</span><span class="tcorner">${T("{n} Keeper-gated",{n:D.filter(d=>d.gk).length})}</span></p>`;
 el("main").innerHTML=`${pathMap(path,lead)}
 <section class="gui rack">
 ${(()=>{const must=D.filter(isMust).sort((x,y)=>ORDER.indexOf(x.t)-ORDER.indexOf(y.t)),myth=byRank(D.filter(d=>d.r===5)),all=f=>`<a class="shall" data-f="${f}" href="#home">${T("See them all →")}</a>`;
  return shelf(ui("star")+" "+T("Must-Have"),T("Looting Charms and every curio that adds curio slots. Get each one the moment its Act opens."),must.slice(0,SHELFN).map(rc),T("Must-Have curios"),{ac:RC[6],n:must.length,all:all("r6")})
  +shelf(T("Mythic"),T("The rarest curios in the pack."),myth.slice(0,SHELFN).map(rc),T("Mythic"),{ac:RC[5],n:myth.length,all:all("r5")})
  +(news.length?shelf(T("New in 6.6.6"),T("{n} curios the pack added in 6.6.6, from {mods}. {link}",{n:news.length,mods:(m=>Object.keys(m).sort((x,y)=>m[y]-m[x]).map(esc).join(", "))(news.reduce((m,d)=>(m[d.m]=(m[d.m]||0)+1,m),{})),link:""}),byRank(news).slice(0,SHELFN).map(rc),T("New in 6.6.6"),{ac:"#7ad65a",n:news.length,all:all("nw")}):"")})()}
 </section>
 <section class="gui"><h2 class="gt">${T("Curio slots")}</h2><p class="gs">${T("The pack's Curios menu, slot by slot.")}</p>
 <div class="slotlist">${BIGSLOTS.map(([s,xs])=>`<a href="#slot/${enc(s)}"><span class="slot sm">${(()=>{const u=slotIcon(s);return u?`<img alt="" src="${u}">`:byRank(xs).filter(d=>IC[d.id]).slice(0,1).map(d=>img(d.id)).join("")})()}</span><b>${esc(T(s))}</b><em>${xs.length}</em>${rbar(xs)}</a>`).join("")}</div></section>`;
 pathMapWire(path);shelfFit();{const rk=document.querySelector(".rack");if(rk&&window.ResizeObserver){let w0=0;const ro=new ResizeObserver(()=>{if(!rk.isConnected){ro.disconnect();return}if(rk.clientWidth!==w0){w0=rk.clientWidth;shelfFit()}});ro.observe(rk)}}document.querySelectorAll(".shall[data-f]").forEach(a=>a.onclick=()=>{const f=a.dataset.f;st.nw=f==="nw";st.r=f==="nw"?[]:[f.slice(1)];save()});el("hs").onsubmit=e=>{e.preventDefault();const v=el("hq").value.trim();if(!v)return;el("q").value=v;st.q=v.toLowerCase();location.hash="#home"};
}


function hubList(kind,key){
 let xs,title,lede="",bar="",cr,hero="";
 if(kind==="slot"){const rf=key.includes("?r=")?+key.split("?r=")[1]:null;key=key.split("?")[0];xs=key==="*"?D:D.filter(d=>d.sl.includes(key));if(rf!=null)xs=xs.filter(d=>d.r===rf);
  title=key==="*"?(rf!=null?`All ${RN[rf]} curios`:"All curios"):`${key} slot`;cr="Slot";if(key!=="*")lede=`Every curio worn in the ${key} slot, rarest first.${!SLOT_BASE[key]?` Players start with no ${key} slot: a curio or its own mod has to add one.`:""}`;
  bar=`<div class="brw-bar">${BIGSLOTS.map(([s])=>`<a href="#slot/${enc(s)}"${s===key?' aria-current="page"':""}>${esc(s)}</a>`).join("")}</div>`}
 else if(kind==="act"){const a=+key;
  // the Warden and Wither Acts were folded into Act VI (ORDER); an old link to them opens Act VI
  if(a===6.1||a===6.2){location.replace("#act/6");return}
  if(!/^-?\d+(\.\d+)?$/.test(key)||!ACT[a]||!(ORDER.includes(a)||a===-1)){document.title=T("Not found")+" · Linggango Wiki";el("main").innerHTML=`${crumb(T("Curios"))}<h1>${T("No Act called “{key}”",{key:esc(key)})}</h1><p class="lede">${T("That Act is not on The Path. See every Act on {path} or every curio on {home}.",{path:`<a href="#">${T("The Path")}</a>`,home:`<a href="#home">${T("Curios")}</a>`})}</p>`;return}
  xs=D.filter(d=>d.t===a);title=actL(a);cr=T("Curios");lede=`${(x=>x.charAt(0).toUpperCase()+x.slice(1))(T(ACT[a][1]))}.${a!=-1?ACTN[a]?" "+T("Next boss: {boss}.",{boss:T(ACTN[a])}):" "+T("This is the last Act."):""} ${T("Must-Have items first, then rarest first.")}`;const bk=PB[a],nb=NEXTB[a],ti=typeof PIMG!=="undefined"&&PIMG.act[String(a)];
  const bl=(k,l)=>k?`<a class="actb" href="#boss/${k}">${emblem(bossPath(k),"sm")}<span><small>${l}</small><b>${esc(bossName(k))}</b></span><i>${T("Guide →")}</i></a>`:"";
  hero=`<div class="actban" style="--tc:${ACT[a][2]}">${ti?`<img class="ptitle big" alt="" src="${ti}"><h3 class="ptxt">${esc(actL(a))}</h3>`:""}<div class="actbs">${bl(bk,T("Opened by beating"))}${bl(nb,T("Next boss"))}</div></div>`;
  bar=`<div class="brw-bar">${ORDER.filter(a=>D.some(d=>d.t===a)).map(b=>`<a href="#act/${b}"${b===a?' aria-current="page"':""}>${actL(b)}</a>`).join("")}</div>`}
 else if(kind==="mod"){modPage(key);return}
 else{document.title="Mods · Linggango Wiki";const ms=[...MODS].sort((a,b)=>b[1].length-a[1].length);el("main").innerHTML=`${crumb("Mods")}<h1 class="qb">Mods</h1><p class="lede">${MODS.length} mods with curios in the pack, biggest first. Each page lists its curios, slots and the Acts they unlock in.</p><div class="mgrid">${ms.map(([m,xs])=>{const F=mf(m),top=byRank(xs).filter(d=>IC[d.id]).slice(0,4);return `<a class="mcard" data-mf="${F[0]}" href="#mod/${enc(m)}"><span class="mbg"></span><span class="mic">${top.map(d=>img(d.id)).join("")}</span><b>${esc(m)}</b><small>${xs.length} curio${xs.length===1?"":"s"}${minfo(m)?" · official page":""}</small></a>`}).join("")}</div>`;return}
 const all=xs.length;xs=byRank(xs.filter(d=>pass(d)));document.title=title+" · Linggango Wiki";seedBg(kind+key,xs);
 let shown=60;
 const draw=()=>{el("gl").innerHTML=xs.slice(0,shown).map(gcard).join("");el("bc").innerHTML=xs.length?T("Showing <b>1–{a}</b> of <b>{b}</b> curios{hidden}",{a:Math.min(shown,xs.length),b:xs.length,hidden:all>xs.length?" · "+T("{n} hidden by filters",{n:all-xs.length}):""}):T("No curios here match these filters.");el("mr").hidden=shown>=xs.length};
 el("main").innerHTML=`${crumb(cr,esc(title))}${hero}<h1>${esc(title)}</h1>${lede?`<p class="lede">${esc(lede)}</p>`:""}${bar}${fbar(xs.length,all)}<div class="brw-ct" id="bc"></div><div class="gridc" id="gl"></div><button class="more" id="mr">${T("Show {n} more",{n:60})}</button>`;
 el("mr").onclick=()=>{shown+=60;draw()};draw();fbind();
}

function modPage(m){
 const xs=byRank(D.filter(d=>d.m===m));if(!xs.length){location.hash="#mods";return}
 document.title=TD(m)+" · Linggango Wiki";seedBg("mod"+m,xs);const F=mf(m),I=minfo(m),hero=xs.filter(d=>IC[d.id]).slice(0,7);
 const sl={};xs.forEach(d=>d.sl.forEach(s=>sl[s]=(sl[s]||0)+1));const sls=Object.entries(sl).sort((a,b)=>b[1]-a[1]);
 const acts=ORDER.map(a=>[a,xs.filter(d=>d.t===a)]).filter(x=>x[1].length),mx=Math.max(...acts.map(x=>x[1].length));
 const rc=RN.map((n,i)=>xs.filter(d=>d.r===i).length);
 const fx=xs.filter(d=>pass(d)),fa=ORDER.map(a=>[a,fx.filter(d=>d.t===a)]).filter(x=>x[1].length);
 const links=I?`<a class="mbtn" href="${I[1]}" target="_blank" rel="noopener">CurseForge ↗</a>`:`<a class="mbtn" href="https://www.curseforge.com/minecraft/search?search=${enc(m)}" target="_blank" rel="noopener">${T("Search on CurseForge ↗")}</a>`;
 el("main").innerHTML=`<div class="mp" data-mf="${F[0]}">${crumb(`<a href="#mods">${T("Mods")}</a>`,esc(m))}
 <section class="mhero"><span class="mbg"></span><span class="mwm" aria-hidden="true"></span>
  <div class="mht"><h1>${esc(m)}</h1>${I?`<p class="mby">${T("by {author}",{author:esc(I[0])})}</p><p>${esc(TD(I[2]))}</p>`:`<p>${TN(xs.length,"{n} curio from this mod is in Linggango.","{n} curios from this mod are in Linggango.")}</p>`}<div class="mlinks">${links}</div></div>
  <div class="mshow">${hero.map((d,i)=>`<a class="ms r${d.r}" style="--i:${i}" href="#i${d.ix}" data-t="${d.ix}">${img(d.id)}</a>`).join("")}</div></section>
 <div class="mstat">
  <div class="mbox"><h3>${T("Curios")}</h3><b class="big">${xs.length}</b><div class="rmix">${rc.map((n,i)=>n?`<i class="r${i}" style="flex:${n}" title="${RN[i]}: ${n}"></i>`:"").join("")}</div><small>${rc.map((n,i)=>n?`${RN[i]} ${n}`:"").filter(Boolean).join(" · ")}</small></div>
  <div class="mbox"><h3>${T("Slot")}</h3><div class="slb">${sls.slice(0,8).map(([s,n])=>`<a href="#slot/${enc(s)}"><span>${esc(T(s))}</span><i style="width:${n/sls[0][1]*100}%"></i><em>${n}</em></a>`).join("")}</div></div>
  <div class="mbox wide"><h3>${T("Unlocks by Act")}</h3><div class="abars">${acts.map(([a,ys])=>`<a href="#act/${a}" style="--tc:${ACT[a][2]}" title="${esc(actF(a))}: ${ys.length}"><i style="height:${Math.max(6,ys.length/mx*100)}%"></i><span>${ACT[a][0]}</span><em>${ys.length}</em></a>`).join("")}</div></div>
 </div>
 ${I&&I[3]?`<aside class="mnote"><b>${T("In Linggango")}</b><p>${esc(TD(I[3]))}</p></aside>`:""}
 ${fbar(fx.length,xs.length)}${fa.length?"":`<p class="note">${T("No curios from this mod match these filters.")}</p>`}
 ${fa.map(([a,ys])=>`<section class="mact" style="--tc:${ACT[a][2]}"><h2>${emblem(a,"xs")}<span>${actL(a)}</span>${esc(T(ACT[a][1]))}<small>${ys.length}</small></h2><div class="gridc">${ys.map(gcard).join("")}</div></section>`).join("")}</div>`;fbind()
}

/* The Path opens one Act by default (the reader's "I'm here" Act, else Act 0–I); a closed Act's tiles are only built when it opens.
   With filters on, every Act with matches is open unless closed by hand (st.cl). */
let pathXs=[];
const tierOpen=a=>fOn()?!st.cl.includes(a):(st.op||[hereOn()??ORDER[0]]).includes(a);
/* an Act shows its first 72 curios (best first) and a button for the rest: Act 0-I alone has over 600 */
const TMORE=72;
const tierTiles=(ys,all)=>ys.length?(all||ys.length<=TMORE+12?ys:ys.slice(0,TMORE)).map((d,i)=>tile(d,i)).join("")+(!all&&ys.length>TMORE+12?`<button type="button" class="mcb tmore" data-more="${ys[0].t}">${T("Show all {n} curios",{n:ys.length})}</button>`:""):`<span class="empty">${T("No items match the filters.")}</span>`;
document.addEventListener("click",e=>{const b=e.target.closest(".tmore");if(!b)return;const a=+b.dataset.more,t=b.closest(".tiles");t.innerHTML=tierTiles(pathXs.filter(d=>d.t===a),1);decorate(t.closest(".tier"))});
function home(xs,asTable){pathXs=xs;
 let h=`${crumb(T("Curios"))}${room("library",D.filter(isMust).sort((a,b)=>ORDER.indexOf(a.t)-ORDER.indexOf(b.t)).map(d=>rCurio(d,esc(ACT[d.t][0]),1)),{head:`<h1 class="qb">${T("Curios")}</h1>
 <p class="lede">${T("Every curio, grouped by the Act you can get it in. Open an Act below to see its curios; {how}.",{how:NOHOVER?T("tap one to open its page"):T("hover one for its tooltip")})}</p>`,cols:8,label:T("Must-Have curios")})}

 ${fbar(xs.length,D.length)}
<div class="legend lgl"><span title="${T("Frame colour: power tier, brighter = stronger at its Act (measured in game where the game test can see it)")}"><i class="lgr"></i>${T("Power")}</span><span title="${T("Curio slot it goes in")}">${sbadge("Ring"," lg")}${T("Slot")}</span><span title="${T("Variants merged into one tile")}"><b class="lgn">16</b>${T("Variants")}</span><span title="${T("Must-Have: get it first")}"><b class="lgs">★</b>${T("Must-Have")}</span><span title="${T("Needs the Seven Curses or Virtues ring")}">${rqb({rq:"Curses"}," lg")}${T("Curses ring")}</span></div>${xs.length?"":`<p class="note">${T("No curios match these filters. Remove one above or clear them all.")}</p>`}`;
 seedBg("path"+st.a,xs.filter(d=>d.r>=4));
 if(!asTable){
  for(const a of ORDER){if(st.a!==""&&a>+st.a)continue;const ys=xs.filter(d=>d.t===a);if((a===-1||fOn())&&!ys.length)continue;const cl=!tierOpen(a);
   h+=`<section class="tier${cl?" closed":""}${VBOSS[a]?" vb":""}" style="--tc:${ACT[a][2]};${tex(a)}" id="p${String(a).replace(".","_")}"><button class="tl" data-tier="${a}" aria-expanded="${!cl}"><span class="tlem">${emblem(a)}</span><span class="ta">${actL(a)}</span><small>${esc(T(ACT[a][1]))}</small>${a==-1?"":`<span class="tn">${ACTN[a]?T("next: {boss}",{boss:esc(T(ACTN[a]))}):T("the last Act")}</span>`}<span class="rs">${RNS.map(i=>{const n=ys.filter(d=>d.r===i).length;return n?`<i class="r${i}" style="flex:${n}" title="${RN[i]}: ${n}"></i>`:""}).join("")}</span><small>${TN(count(ys),"{n} item","{n} items")}</small></button><div class="tiles">${cl?"":tierTiles(ys)}</div></section>`}
 }else{
  const COLS=[["n",T("Curio")],["r",T("Power")],["c",T("Role")],["t",T("Tier")],["a",T("Usable from")],["g",T("Source")],["m",T("Mod")],["fx",T("Effect")]];
  const CO=Object.keys(ROLE);
  const ys=[...xs].sort((p,q)=>{const k=st.sort;const r=k==="a"?p.a-q.a:k==="t"?p.t-q.t:k==="r"?(p.r-q.r||p.sc-q.sc):k==="c"?CO.indexOf(p.c)-CO.indexOf(q.c):k==="n"||k==="fx"?nameCmp(String(p[k]),String(q[k])):String(p[k]).localeCompare(String(q[k]));return r*st.dir});
  h+=`<div class="tw"><table><thead><tr><th></th>${COLS.map(([k,t])=>`<th><button class="ghost" data-s="${k}">${t}${st.sort===k?(st.dir>0?" ▲":" ▼"):""}</button></th>`).join("")}</tr></thead><tbody>${ys.map(d=>`<tr><td data-t="${d.ix}">${img(d.id)}</td><td><a href="#i${d.ix}" data-t="${d.ix}">${esc(TD(d.n))}</a></td><td class="r${d.r}"><i class="rdot"></i>${RN[d.r]}</td><td>${d.ro.map(k=>T(ROLE[k])).join(", ")}</td><td class="num">${ACT[d.t][0]}</td><td class="num">${ACT[d.a][0]}</td><td>${T(d.g)}</td><td>${esc(d.m)}</td><td>${esc(fxT(d))}</td></tr>`).join("")}</tbody></table></div>`}
 el("main").innerHTML=h;decorate();fbind();
 el("main").querySelectorAll("th button").forEach(b=>b.onclick=()=>{const k=b.dataset.s;st.dir=st.sort===k?-st.dir:1;st.sort=k;render()});
}

function relicRows(line){
 // "Ability [active] (unlocks at relic lvN): Stat a ~ b (lv N: c ~ d); ... · note ⚙ pack tweak: x"
 let note="",pack="";const pi=line.indexOf(" ⚙ ");if(pi>=0){pack=line.slice(pi+3);line=line.slice(0,pi)}
 const ni=line.indexOf(" · ");if(ni>=0){note=line.slice(ni+3);line=line.slice(0,ni)}
 const ci=line.indexOf(": "),ab=ci>=0?line.slice(0,ci):line,rest=ci>=0?line.slice(ci+2):"";
 let rows=`<tr class="ab"><td colspan="3">${esc(ab)}${pack?` <span class="tg pack">${esc(pack)}</span>`:""}</td></tr>`;
 rest.split("; ").filter(Boolean).forEach(s=>{const m=s.match(/^(.+?) ([-+]?[x×]?\d[\s\S]*?)(?: \(lv (\d+): (.*)\))?$/);
  rows+=m?`<tr><td>${esc(m[1])}</td><td class="num">${esc(m[2])}</td><td class="num">${m[3]?`${esc(m[4])} <span class="meta">(lv ${m[3]})</span>`:"—"}</td></tr>`:`<tr><td colspan="3">${esc(s)}</td></tr>`});
 if(note)rows+=`<tr><td colspan="3" class="meta">${esc(note)}</td></tr>`;return rows}

/* ---------- How to get it, as pictures ----------
   A recipe shows its station: the crafting grid, the smithing row, or for a ritual (Goety's Dark Altar, Ars Nouveau's
   Enchanting Apparatus, Nature's Aura) the ingredients on pedestals in a ring around the altar. A drop shows who or what
   gives it: the mob's face (mob_faces.py; a spawner for modded mobs), the Keeper's emblem for a treasure bag, a chest
   with the structures, a suspicious block for brushing, the container item. Lines that say something else stay as text. */
let IDNM=null;const idName=id=>{if(!IDNM){IDNM={};if(typeof NAMEID!=="undefined")for(const k in NAMEID)IDNM[NAMEID[k]]??=k}return IDNM[id]};
const rcNm=c=>c[0]?TD(BYID[c[0]]?BYID[c[0]].n:NM[c[0]]||idName(c[0])||(c[0].includes(":")?nmI(c[0]):c[0])):T("Any {kind}",{kind:(c[1].split(":")[1]||c[1]).replace(/_/g," ")});
const STATION=[[/Dark Altar|Ritual Goety/,"goety:dark_altar","ring"],[/Enchanting Apparatus/,"","ring"],[/Ritual of the Forest|Natural Altar|Offering Table/,"","ring"],
 [/Blood Altar|Imbuement|Cursed Infuser|Mixing Cauldron/,"goety:cursed_infuser","ring"],[/Smithing/,"minecraft:smithing_table","row"],[/Tinkerer|Upgrade Forge|Alchemy Array/,"","row"],[/Crafting Table/,"","grid"]];
/* stations whose use the generic line gets wrong */
const STHOW={"Alchemy Array":N("draw the array with Arcane Ashes, drop the first item on it, then the second"),"Hellfire Forge":N("any slots; needs Demon Will in a Tartaric Gem in the forge")};
/* the station's own block: its name in the pack's lang files (name_icons.py) gives the item; the vanilla table stays vanilla */
const STN={"Ritual Goety":"Dark Altar","Ritual of the Forest":"Natural Altar","Crafting Table":"","Enchanting Apparatus":"Enchanting Apparatus"};
const stIcon=st=>{const base=st.replace(/\s*\(.*\)\s*$/,"").replace(/^an? /,""),inner=(st.match(/\(([^)]+)\)/)||[])[1];
 for(const n of [STN[base],inner,base]){const id=n&&(NAMEID[n]||(n==="Smithing Table"&&"minecraft:smithing_table"));if(id&&IC[id])return img(id)}
 return `<i class="sti" style="--sti:var(--rt-${/Smithing/.test(st)?"smithing_table_front":"crafting_table_front"})"></i>`};
function recipeGui(d){const g=d.gr,stn=g.st.replace(/\s*\(shapeless\)/i,""),kind=(STATION.find(x=>x[0].test(stn))||[,,"grid"])[2],grid=kind==="grid"&&g.l===0&&!/shapeless/i.test(g.st);
 const ing=[],seen={};g.c.forEach(c=>{if(!c)return;const k=c[0]+"|"+c[1];if(!seen[k]){seen[k]={c,n:0};ing.push(seen[k])}seen[k].n++});
 const slot=(c,cls="",k)=>{const sty=k!=null?` style="--k:${k}"`:"";if(!c)return `<div class="mcs${cls}"${sty}></div>`;const t=BYID[c[0]];
  return `<div class="mcs${cls}"${sty} data-k="${esc(c[0]+"|"+c[1])}"${t?` data-t="${t.ix}"`:""} title="${esc(rcNm(c))}${c[1]?" "+T("(any item tagged {tag})",{tag:esc(c[1].replace(/^#/,""))}):""}">${c[0]?img(c[0]):c[1]&&typeof TAGID!=="undefined"&&IC[TAGID["#"+c[1].replace(/^#/,"")]]?img(TAGID["#"+c[1].replace(/^#/,"")]):'<span class="ph">'+esc(rcNm(c))+'</span>'}${c[1]?'<span class="tagm" aria-label="${T("tag")}">#</span>':""}</div>`};
 const flat=ing.flatMap(e=>Array(e.n).fill(e.c));let inputs;
 if(kind==="ring"){const n=flat.length;inputs=`<div class="mring" style="--n:${n}">${flat.map((c,i)=>slot(c,"",i)).join("")}<span class="mcen" title="${esc(stn)}">${stIcon(stn)}</span></div>`}
 else if(kind==="row")inputs=`<div class="mcg mrow">${flat.map(c=>slot(c)).join("")}</div>`;
 else inputs=grid?`<div class="mcg" style="grid-template-columns:repeat(${g.w},var(--sz))">${g.c.map(c=>slot(c)).join("")}</div>`:`<div class="mcg free">${flat.map(c=>slot(c)).join("")}</div>`;
 const list=`<ol class="mcl">${ing.map(e=>{const t=BYID[e.c[0]];return `<li><span class="mcs sm">${e.c[0]?img(e.c[0]):""}</span><b>${e.n}×</b> ${t?`<a href="#i${t.ix}" data-t="${t.ix}">${esc(rcNm(e.c))}</a>`:esc(rcNm(e.c))}${e.c[1]&&e.c[0]?` <span class="tg">${T("any {tag}",{tag:esc(e.c[1].replace(/^#?[a-z0-9_.-]+:/,"").replace(/_/g," "))})}</span>`:""}</li>`}).join("")}</ol>`;
 const how=T(STHOW[stn.replace(/\s*\(.*\)\s*$/,"")]||(kind==="ring"?N("put the ingredients on the pedestals around it, then start the ritual"):kind==="row"?N("the ingredients go in left to right"):grid?N("shaped: the layout matters"):N("shapeless: any arrangement")));
 return `<div class="mcwin k-${kind}"><div class="mct"><span class="mcst">${stIcon(stn)}</span>${esc(TD(stn))}<span>${how}</span></div>
 <div class="mcrow">${inputs}<i class="mca" aria-hidden="true"></i>${slot([d.id,""]," big").replace(/<\/div>$/,`${g.n>1?`<span class="cnt">${g.n}</span>`:""}</div>`)}</div>
 <div class="mcli"><div class="mch">${T("Ingredients")}</div>${list}</div></div>`}
const SRCX={mob:/[Dd]ropped by ([^(;]+?)\s*\(([^)]*)\)/g,bag:/[Cc]omes from (?:the )?(.+?)'s treasure bag \(([^)]+)\)/g,brush:/Brush suspicious blocks at ([^(;]+?) \(([^)]+)\)/g,
 chest:/[Ff]ound in chests at ([^;]+?)(?:, up to ([\d.]+%) per chest)?\.?(?=;|$)/g,tomb:/[Ff]ound in ([A-Z][\w' ]+?) chests \(([^)]+)\)/g,van:/Vanilla chests \(([^)]*)\): ([^;]+?)\.?(?=;|$)/g,
 box:/(?:From an?|Can roll from an?) ([A-Z][\w' ]+?)(?: \(([^)]*)\))?(?= or|[.;]|$)/g,trade:/Bought from ([^.;]+)/g};
/* a modded mob that is one of the side bosses: its picture is the side boss's own (the pack's screenshot the wiki already shows) */
const SIDEAL={"archmage gundalf":"Gundalf, Circe, Merlin (Shadow Wizards)","echo of tyros, first flamebearer":"Tyros (fire boss)","the dead king":"Dead King","enraged dead king":"Dead King","leviathan":"The Leviathan"};
const sideByName=n=>{if(typeof SIDEB==="undefined")return null;const l=n.toLowerCase();if(SIDEAL[l])return SIDEAL[l];return Object.keys(SIDEB).find(k=>{const x=k.toLowerCase();return x===l||x.replace(/^the /,"")===l.replace(/^the /,"")})||null};
const sidePic=k=>{const pi=typeof PIMG!=="undefined"?PIMG:{};return (pi.side&&pi.side[k])||(SIDEB[k]&&SIDEB[k].img&&pi.scene&&pi.scene[k])||null};
const bossByName=n=>{n=n.replace(/^the /i,"").toLowerCase();return [...KEEPERS(),...Object.keys(SIDEV||{})].find(k=>{const b=bossName(k).toLowerCase();return b===n||b.startsWith(n)||b.replace(/^the /,"").startsWith(n)})};
function lootCards(d){const out=[],used=new Set();
 const card=(pic,title,sub,chance,href)=>`<${href?`a href="${href}"`:"div"} class="lcard"><span class="lpic">${pic}</span><span class="ltx"><b>${title}</b>${sub?`<small>${sub}</small>`:""}</span>${chance?`<span class="lch">${esc(chance)}</span>`:""}</${href?"a":"div"}>`;
 const rt=k=>`<i class="lrt" style="--lrt:var(--rt-${k})"></i>`;
 d.src.forEach((line,li)=>{let m,hit=0;const R=k=>{SRCX[k].lastIndex=0;const xs=[];while(m=SRCX[k].exec(line))xs.push(m);return xs};
  R("mob").forEach(m=>{hit=1;const n=m[1].trim(),bk=bossByName(n),fk="mf_"+n.replace(/s$/,"").toLowerCase().replace(/ /g,"_"),sk=sideByName(n),sp=sk&&sidePic(sk);
   out.push(bk?card(emblem(bossPath(bk)??0,"sm"),esc(bossName(bk)),T("Boss drop"),m[2],"#boss/"+bk)
    :sk?card(sp?`<img class="lsc" alt="" src="${sp}">`:rt("spawner"),esc(n),T("Side boss drop"),m[2],"#side/"+enc(sk))
    :card(typeof ROOMT!=="undefined"&&ROOMT[fk]?rt(fk):rt("spawner"),esc(n),T("Mob drop"),m[2]))});
  R("bag").forEach(m=>{hit=1;const bk=bossByName(m[1]),bag=bk&&BINFO[bk]&&(BINFO[bk].drops||[]).find(x=>/treasure_?bag/.test(x.id));
   out.push(card(bag&&IC[bag.id]?img(bag.id):bag&&BIMG[bag.id]?`<img alt="" src="${BIMG[bag.id]}">`:bk?emblem(bossPath(bk)??0,"sm"):rt("ftb_chest"),T("{boss}'s treasure bag",{boss:esc(bk?bossName(bk):m[1])}),T("Open the bag the Keeper drops"),m[2],bk?"#boss/"+bk:""))});
  R("brush").forEach(m=>{hit=1;out.push(card(rt("lt_sand"),esc(m[1]),T("Brush the suspicious blocks"),m[2]))});
  R("tomb").forEach(m=>{hit=1;out.push(card(rt("ftb_chest"),T("{place} chests",{place:esc(m[1])}),T("Chest loot"),m[2]))});
  R("chest").forEach(m=>{hit=1;out.push(card(rt("ftb_chest"),esc(m[1].replace(/ and (\d+) more places/,(x,n)=>" "+T("+{n} more",{n}))),T("Chest loot"),m[2]?T("up to {n}",{n:m[2]}):""))});
  R("van").forEach(m=>{hit=1;const c=m[2].match(/^(.+?) ([\d.]+%)$/);out.push(card(rt("ftb_chest"),esc(c?c[1]:m[2]),T("Vanilla chest loot"),c?c[2]:""))});
  R("box").forEach(m=>{const id=NAMEID[m[1]];if(!id&&!/Bag|Box|Chest|Crate/.test(m[1]))return;hit=1;out.push(card(id&&IC[id]?img(id):rt("lt_bundle"),esc(m[1]),m[2]?esc(m[2]):T("Open it for a random roll"),""))});
  R("trade").forEach(m=>{hit=1;out.push(card(rt("lt_emerald"),esc(m[1]),T("Trade"),""))});
  if(hit)used.add(li)});
 return {html:out.length?`<div class="lcards">${out.join("")}</div>`:"",used}}
/* no recipe in the pack files (curio_recipes.json): the ingredients the "Craft at … from A, B and C" line names, as a row with the station */
const TXRC=/^(?:Craft|Combine|Infuse|Forge|Upgrade|Imbue|Perform) (?:at|in|on) (?:an? |the )?(.+?)(?: from|:| with) (.+?)\.*$/;
let DROPN=null;const dropId=n=>{if(!DROPN){DROPN={};for(const k in BINFO)(BINFO[k].drops||[]).forEach(x=>{if(x.n)DROPN[x.n.toLowerCase()]=x.id})}return DROPN[n.toLowerCase()]};
function textRecipe(d){if(d.gr)return null;for(let i=0;i<d.src.length;i++){const m=d.src[i].match(TXRC);if(!m)continue;
  const names=m[2].replace(/\.+$/,"").split(/,\s*|\s+and\s+/).map(x=>x.trim()).filter(Boolean),ids=names.map(n=>NAMEID[n]||(D.find(x=>x.n===n)||{}).id||dropId(n));
  if(!ids.some(id=>id&&(IC[id]||BIMG[id])))continue;
  const slot=(id,n)=>{const t=BYID[id];return `<div class="mcs"${t?` data-t="${t.ix}"`:""} title="${esc(n)}">${id&&IC[id]?img(id):id&&BIMG[id]?`<img alt="" src="${BIMG[id]}">`:`<span class="ph">${esc(n)}</span>`}</div>`};
  return {i,html:`<div class="mcwin k-row"><div class="mct"><span class="mcst">${stIcon(m[1])}</span>${esc(TD(m[1].replace(/^a /,"")))}<span>${T("ingredients")}</span></div>
  <div class="mcrow"><div class="mcg mrow">${ids.map((id,j)=>slot(id,names[j])).join("")}</div><i class="mca" aria-hidden="true"></i><div class="mcs big">${img(d.id)}</div></div></div>`}}return null}
const howVisual=d=>(d.gr?recipeGui(d):(textRecipe(d)||{}).html||"")+lootCards(d).html;
/* Source lines in the reader's language. The patch scripts put a curio's source lines together from a few clause shapes joined with "; ".
   A shape is one sentence with {slots}: srcClause matches a clause against the shapes and says it in the reader's language; mob and item names go
   through TD, structure and place names stay as the mods print them, a percentage takes the language's decimal comma. A clause no shape fits goes to the
   translation memory whole (TD) and stays English if it is not there. English never goes through here: srcT hands the line back as it is. */
const dec=s=>LANG==="en"||LANG==="vi"?s:(s=s.replace(/(\d)\.(\d)/g,"$1,$2"),LANG==="es"?s.replace(/(\d)%/g,"$1 %"):s);
const plc=s=>{const m=s.match(/^(.*) and (\d+) more places?$/);if(m)return TN(+m[2],"{a} and {n} more place","{a} and {n} more places",{a:m[1]});
 const k=s.lastIndexOf(" and ");return k>0?T("{a} and {b}",{a:s.slice(0,k),b:s.slice(k+5)}):s};
const SRCSUF=[[/^dropped by (.+)$/,N("dropped by {b}"),m=>({b:TD(m[1])})],[/^mined from (.+)$/,N("mined from {b}"),m=>({b:TD(m[1])})],
 [/^found in the Nether$/,N("found in the Nether"),()=>({})],[/^found in the End$/,N("found in the End"),()=>({})],[/^trait mobs drop it while you wear Curse of (.+)$/,N("trait mobs drop it while you wear Curse of {b}"),m=>({b:m[1]})],
 [/^from (?:the )?(.+?)'s? treasure bag \(([\d.–]+%?)\)$/,N("from {b}'s treasure bag ({c})"),m=>({b:TD(m[1]),c:dec(m[2])})],[/^from (?:the )?(.+?)'s? treasure bag$/,N("from {b}'s treasure bag"),m=>({b:TD(m[1])})],
 [/^comes from the (.+?) on this wiki's Act ladder$/,N("comes from the {b} on this wiki's Act ladder"),m=>({b:TD(m[1])})],[/^made with an? (.+)$/,N("made with {b}"),m=>({b:TD(m[1])})],
 [/^locked behind the (\w+) gate until you defeat (?:the )?(.+)$/,N("locked behind the {g} gate until you defeat {b}"),m=>({g:m[1],b:TD(m[2])})],
 [/^throw (.+?) into (.+)$/,N("throw {a} into {b}"),m=>({a:TD(m[1]),b:TD(m[2])})],[/^found in (.+?) chests$/,N("found in {p} chests"),m=>({p:m[1]})],
 [/^upgraded from (.+?) \(Goety Revelation special mechanic\)$/,N("upgraded from {a} (Goety Revelation special mechanic)"),m=>({a:TD(m[1])})],
 [/^L(\d+) Hostility (.+?) trait drop$/,N("L{n} Hostility {t} trait drop"),m=>({n:m[1],t:m[2]})]];
const SRCSH=[[/^Found in chests at (.+?), up to ([\d.]+%) per chest$/,N("Found in chests at {p}, up to {c} per chest"),m=>({p:plc(m[1]),c:dec(m[2])})],
 [/^Found in chests at ([^()]+)$/,N("Found in chests at {p}"),m=>({p:plc(m[1])})],
 [/^Also: found in chests at (.+?), up to ([\d.]+%) per chest$/,N("Also: found in chests at {p}, up to {c} per chest"),m=>({p:plc(m[1]),c:dec(m[2])})],
 [/^Also: found in chests at ([^()]+)$/,N("Also: found in chests at {p}"),m=>({p:plc(m[1])})],
 [/^Also: found in (.+?) chests \(([\d.]+%) per chest\)$/,N("Also: found in {x} chests ({c} per chest)"),m=>({x:m[1],c:dec(m[2])})],
 [/^Found in (.+?) chests \(([\d.]+%) per chest\)$/,N("Found in {x} chests ({c} per chest)"),m=>({x:m[1],c:dec(m[2])})],
 [/^Dropped by ([^(:+]+?) \(([\d.–]+%)\)$/,N("Dropped by {m} ({c})"),m=>({m:TD(m[1]),c:dec(m[2])})],
 [/^Also: dropped by ([^(]+?) \(([\d.]+%)\)$/,N("Also: dropped by {m} ({c})"),m=>({m:TD(m[1]),c:dec(m[2])})],
 [/^Brush suspicious blocks at (.+?) \(([\d.]+%)\)$/,N("Brush suspicious blocks at {p} ({c})"),m=>({p:m[1],c:dec(m[2])})],
 [/^Also in vanilla chests \(Unique Accessories' own loot, chance from the pack config\): (.+)$/,N("Also in vanilla chests (Unique Accessories' own loot, chance from the pack config): {l}"),m=>({l:dec(m[1])})],
 [/^Vanilla chests \(Terra Curio adds it\): (.+)$/,N("Vanilla chests (Terra Curio adds it): {l}"),m=>({l:dec(m[1])})],
 [/^Since ([\d.]+) every chest and mob that gave (.+?) gives this instead: (.+)$/,N("Since {v} every chest and mob that gave {x} gives this instead: {r}"),m=>({v:m[1],x:TD(m[2]),r:srcClause(m[3])})],
 [/^Since ([\d.]+) the chests and mobs that gave (.+?) give this instead: (.+)$/,N("Since {v} the chests and mobs that gave {x} give this instead: {r}"),m=>({v:m[1],x:TD(m[2]),r:srcClause(m[3])})],
 [/^Comes from (?:the )?(.+?)'s? treasure bag \(([\d.]+%)\)$/,N("Comes from {b}'s treasure bag ({c})"),m=>({b:TD(m[1]),c:dec(m[2])})],
 [/^Comes from (?:the )?(.+?)'s? treasure bag$/,N("Comes from {b}'s treasure bag"),m=>({b:TD(m[1])})],
 [/^Draw an Alchemy Array \(Blood Magic\) with (.+?) and (.+)$/,N("Draw an Alchemy Array (Blood Magic) with {a} and {b}"),m=>({a:TD(m[1]),b:TD(m[2])})],
 [/^The mod's own page \(([\d.]+)\) says: evolves from (.+)$/,N("The mod's own page ({v}) says: evolves from {n}"),m=>({v:m[1],n:TD(m[2])})],
 [/^The mod's own page \(([\d.]+)\) says: (.+)$/,N("The mod's own page ({v}) says: {x}"),m=>({v:m[1],x:m[2].split(", ").map(w=>TD(w)).join(", ")})],
 [/^Also craftable from Act ([IVX]+)$/,N("Also craftable from {a}"),m=>({a:T("Act {n}",{n:m[1]})})]];
function srcSuf(s){let m;for(const [re,tpl,f] of SRCSUF)if(m=re.exec(s))return T(tpl,f(m));return TD(s)}
function srcClause(c){const h=TD(c);if(h!==c)return h;const e=c.replace(/\.$/,""),dot=e===c?"":".";const h2=TD(e);if(h2!==e)return h2+dot;let m;
 if(m=e.match(/^Hardest ingredient: (.+?)(?: — (.+))?$/))return (m[2]?T("Hardest ingredient: {a} — {s}",{a:TD(m[1]),s:srcSuf(m[2])}):T("Hardest ingredient: {a}",{a:TD(m[1])}))+dot;
 if(m=e.match(/^Dropped by \+(\d+) other sources?$/))return TN(+m[1],"Dropped by +{n} other source","Dropped by +{n} other sources")+dot;
 for(const [re,tpl,f] of SRCSH)if(m=re.exec(e))return T(tpl,f(m))+dot;
 return c}
const srcT=l=>{if(LANG==="en")return l;const w=TD(l);return w!==l?w:l.split(/;\s+/).map(srcClause).join("; ")};
const howText=d=>{const u=lootCards(d).used,tr=textRecipe(d);if(tr)u.add(tr.i);const xs=d.src.filter((x,i)=>!u.has(i)&&!(d.gr&&RCV.test(x))&&!/^Key requirement: locked behind/i.test(x));return xs.length?`<ol class="how">${xs.map(x=>`<li>${fmt(srcT(x))}</li>`).join("")}</ol>`:""};

/* ---------- Stats, readable ----------
   First what the curio is (element, damage types it touches), then the effect as the wiki sums it up, one line per
   clause, with numbers picked out (blue = bonus, red = cost, as in the game's tooltip). The in-game tooltip follows with
   its wrapped lines joined back into sentences, then the pack's config numbers as a small table. No source tags. */
const ELEM={"Fire":"fire","Ice":"ice","Water":"water","Lightning":"lightning","Dark":"dark","Holy":"holy","Blood":"blood","Ender / Eldritch":"ender","Poison / Nature":"nature"};
const DMGT=[[N("Slash"),/\bslash(ing)? damage|[+\-−]\s?[\d.]+%? slash\b/i,"ui_sword"],[N("Pierce"),/\bpierc(e|ing) damage|[+\-−]\s?[\d.]+%? pierce\b/i,"dt_pierce"],[N("Blunt"),/\bblunt damage|[+\-−]\s?[\d.]+%? blunt\b/i,"dt_blunt"],[N("Magic"),/\b(magic|spell)\b[^.;]*\b(damage|power)|\bspell (power|damage)/i,"dt_magic"],
 [N("Projectile"),/\b(projectile|arrow|ranged)\b[^.;]*damage|\bdamage[^.;]*\b(projectile|arrow)/i,"ui_bow"],[N("Melee"),/\b(melee|attack) damage|\bmelee\b/i,"ui_sword"],[N("Summon"),/\b(summon|minion)s?\b[^.;]*damage/i,"ui_bone"]];
const ELX=[["Fire",/\b(ignite|on fire|fire damage|burn|flame)/i],["Ice",/\b(freez|frost|ice damage)/i],["Lightning",/\b(lightning|thunder|shock)/i],["Holy",/\bholy\b/i]];
const kindOf=d=>{const txt=d.fx+" "+d.st.join(" "),el=(d.mt||[]).filter(k=>k.startsWith("e:")).map(k=>k.slice(2));ELX.forEach(([e,re])=>{if(!el.includes(e)&&re.test(d.fx))el.push(e)});return {el,dt:DMGT.filter(x=>x[1].test(txt))}};
const kchip=(k,label,cls)=>`<span class="kchip ${cls}"><i style="--kc:var(--rt-${k})"></i>${esc(label)}</span>`;
/* stat names on curio pages: short hover text, click goes to Mechanics › Stats */
const STATH=[[/\barmor penetration\b/i,N("Percent: the target counts with that much less armor (Brutality, cap 95%). Best vs heavy armor.")],[/\blethality\b/i,N("Flat armor removal, applied last; each point past zero armor is +10% damage. Best vs light armor.")],[/\barmor pierce\b/i,N("Flat armor removal (Apothic), weakened by the target's toughness.")],[/\barmor pass\b/i,N("Becomes Apothic Armor Pierce in this pack: flat armor removal.")],[/\benchantment piercing\b/i,N("Gives back part of the damage Protection enchantments removed (Goety Revelation).")],[/\barmor shred\b/i,N("Percent armor removal after penetration (Apothic), weakened by the target's toughness.")],[/\bdamage taken\b/i,N("Multiplies the damage you take: −5% means 5% less.")],
 [/\bcritical strike chance\b/i,N("Brutality: the roll every melee crit needs (base 0%). No jump needed; a failed roll cancels jump crits.")],[/\bcritical strike damage\b/i,N("Brutality melee crit multiplier: base ×1.4, capped at ×3.")],[/\bcritical chance\b/i,N("Apothic crit: its own roll on every hit you own (base 5%, ×1.5).")],[/\bspell crit\b/i,N("Iron's Spells damage only; needs both spell crit chance and spell crit damage.")],[/\bcrit damage\b/i,N("Adds to a crit's multiplier; which crit depends on the mod (see Mechanics › Stats).")],[/\bcrit chance\b/i,N("There are several crit chances; see Mechanics › Stats.")],
 [/\bdodge chance\b/i,N("Chance to avoid a hit completely. Capped at 50% (Brutality) or 40% (Apothic) in this pack.")],[/\bomnivamp\b/i,N("Heals a share of every hit you own: melee, arrows, spells (cap 10% max health a tick).")],[/\blife ?steal\b/i,N("Heals a share of the melee damage you deal (cap 10% max health a tick).")],[/\bminion damage\b/i,N("Multiplies minion damage (Summonity); halved without a summoning item or whip in hand.")],[/\bsummon damage\b/i,N("Multiplies summoned creatures' damage (Iron's Spells).")],
 [/\broll count\b/i,N("Roll charges; only whole numbers count.")],[/\broll recharge\b/i,N("Charges come back faster: cooldown × 20 / Roll Recharge.")],[/\bdodge window\b/i,N("Extra invulnerable ticks on rolls and dashes, rounded, at most +4.")],[/\bcooldown reduction\b/i,N("Spell cooldown × (2 − value), softened past +50%.")]];
function statHint(h){for(const [re,tip] of STATH){const m=h.match(re);if(!m)continue;const pre=h.slice(0,m.index);if(/<[^>]*$/.test(pre)||pre.lastIndexOf('<a class="sth"')>pre.lastIndexOf("</a>"))continue;h=pre+`<a class="sth" href="#mechanics/stats" title="${esc(T(tip))}">${m[0]}</a>`+h.slice(m.index+m[0].length)}return h}
/* a raw tooltip line of a curio (the game's or the mod's own text): a whole-line entry in the pack, else "+8% Max Health" with the attribute name translated (gAL), else as it is. English never goes through here. */
// "Name: value" lines of the tooltip (the pack's config, relic abilities): the label through TD part by part ("A — B", "A › B"), the value by shape (cfgV); a clause, unit or word without an entry stays English
const RLUc={},rlU=()=>RLUc[LANG]||(RLUc[LANG]=(()=>{const m=[],seen=new Set(),un=f=>f.replace("%1$s","").replace(/%%/g,"%").replace(/\.$/,"").replace(/^\s*\+\s*/,"").trim();   // "seconds" => "с": the units of the relic value formats, read from the formats rlStat already says through TD
 for(const id in RL)for(const a of RL[id].ab)for(const t of a.st){if(seen.has(t.f))continue;seen.add(t.f);const ue=un(t.f);if(!ue||/^[%xX]$/.test(ue))continue;const ut=un(TD(t.f));if(ut!==ue)m.push([ue,ut])}
 return m.sort((p,q)=>q[0].length-p[0].length)})());
const relUnits=v=>{for(const [e,t] of rlU())v=v.replace(new RegExp("(?<=[\\d?])"+(e[0]==="%"?"":" ")+e.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+"(?![A-Za-z])","g"),(t[0]==="%"?"":" ")+t);return v};
const relV=v=>{let tail="",ex="",pk="",m;   // "Cooldown 16 seconds ~ 12 seconds; Duration … (at relic level 0; grows as the relic levels up) · max level 5 (…) ⚙ pack tweak: …"; null = a shape this does not read
 if(m=v.match(/^([\s\S]*?) ⚙ pack tweak: ([\s\S]*)$/))v=m[1],pk=" ⚙ "+T("pack tweak:")+" "+dec(m[2]).replace(/max level/g,T("max level")).replace(/pts\/level/g,T("pts/level"));   // the code names in it stay as written
 if(m=v.match(/^([\s\S]*?) · max level (\d+) \(relic lv(\d+), (\d+) pts\/level, shared with other abilities\)$/))v=m[1],ex=" · "+T("max level {a} (relic lv{b}, {c} pts/level, shared with other abilities)",{a:m[2],b:m[3],c:m[4]});
 if(m=v.match(/^(.*) \(at relic level (\d+); grows as the relic levels up\)$/)){v=m[1];tail=" "+T("(at relic level {n}; grows as the relic levels up)",{n:m[2]})}
 if(/ [·⚙] /.test(v))return null;
 const o=v.split("; ").map(c=>{const k=c.match(/^(.+?) ([+\-−]?\d[\s\S]*)$/);return k&&TD(k[1])+" "+dec(relUnits(k[2])).replace(/\(lv (\d+):/g,(_,n)=>"("+T("lv {n}",{n})+":")});
 return o.includes(null)||o.includes(undefined)||o.some(x=>!x)?null:o.join("; ")+tail+ex+pk};
const cfgV=v=>{let m;
 if(/^[\d.,+\-−×x%~ ()\/?…]+$/.test(v))return dec(v);
 if(m=v.match(/^(.*) \(game-rule default\)$/))return cfgV(m[1])+" ("+T("game-rule default")+")";
 if(m=v.match(/^(.*) \(code default\)$/))return cfgV(m[1])+" ("+T("code default")+")";
 if(m=v.match(/^([\d.,?]+)s$/))return T("{n}s",{n:dec(m[1])});
 if(m=v.match(/^(\d+) seconds$/))return T("{n} seconds",{n:m[1]});
 if(m=v.match(/^([…?]) s$/))return T("{n} s",{n:m[1]});
 if(m=v.match(/^([…?]) m\/s$/))return T("{n} m/s",{n:m[1]});
 const r=relV(v);return r!=null?r:TD(v)};
const cfgS=t=>{let m,u,par="",suf="";   // one part of a label: "Name [active] (unlocks at relic lv7)", "Chest chance in Igloo Chest", "Drop chance from Warden"
 if(m=t.match(/^(.*?)( \([^)]*\))$/)){t=m[1];par=(u=m[2].match(/^ \(unlocks at relic lv(\d+)\)$/))?" "+T("(unlocks at relic lv{n})",{n:u[1]}):m[2]}
 if(m=t.match(/^(.*) \[active\]$/)){t=m[1];suf=" ["+T("active")+"]"}
 if(m=t.match(/^Chest chance in (.+)$/))return T("Chest chance in {x}",{x:TD(m[1])})+suf+par;   // the loot tables of the pack's config
 if(m=t.match(/^Drop chance from (.+)$/))return T("Drop chance from {x}",{x:TD(m[1])})+suf+par;
 return TD(t)+suf+par};
const cfgT=x=>{const i=x.indexOf(": ");if(i<1||i>90||!/[A-Za-z]{2}/.test(x.slice(0,i)))return x;
 return x.slice(0,i).split(/( — | › )/).map((t,j)=>j%2?t:cfgS(t)).join("")+": "+cfgV(x.slice(i+2))};
const stT=x=>{if(LANG==="en")return x;const w=TD(x);if(w!==x)return w;const g=gAL(x);return g!==x?g:cfgT(x)};
function statLine(t){const h=fmt(t).replace(/(^|[\s(])([+\-−]\s?\d[\d.,]*\s?%?|x\s?\d[\d.]*|×\s?\d[\d.]*|\d[\d.,]*\s?%)/g,(m,a,n)=>`${a}<b class="${/^[\-−]/.test(n)?"neg":"pos"}">${n}</b>`);return effHint(statHint(h))}
function joinTip(xs){const out=[];xs.forEach(x=>{x=String(x).trim();if(!x)return;const p=out[out.length-1];
 if(p&&!/[.!?:)]$/.test(p)&&/^[a-z(…]/.test(x))out[out.length-1]=p+" "+x;else out.push(x)});return out}
function statsHtml(d,other){const k=kindOf(d),nm=d.n.toLowerCase();
 const head=(k.el.length||k.dt.length)?`<div class="kinds">${k.el.length?`<span class="klab">${T("Element")}</span>${k.el.map(e=>kchip("el_"+(ELEM[e]||"fire"),T(e).replace(" / ","/"),"el")).join("")}`:""}${k.dt.length?`<span class="klab">${T("Damage")}</span>${k.dt.map(x=>kchip(x[2],T(x[0]),"dt")).join("")}`:""}</div>`:"";
 const sum=fxT(d).split(/;\s*/).filter(Boolean),tip=joinTip(other.filter(x=>x[0]!=="pack").map(x=>x[1])).filter(x=>x.toLowerCase()!==nm&&!/^obtain\b/i.test(x)&&!/^(hold shift|the finale$)/i.test(x)),
  cfg=other.filter(x=>x[0]==="pack").map(x=>String(x[1]).split(/:\s*/)).filter(x=>x.length>1);
 const HD=/^(passive effect|active ability|when worn|when equipped|set bonus|abilities?)\s*:?$/i;
 // the title's lead already says the wiki's one-line summary: Stats shows the game's own tooltip (or the summary split, if there is none)
 // the wiki's summary is complete and curated; the game's own tooltip (often wrapped, sometimes only lore) folds away below it
 const lines=sum;
 return `${head}<ul class="attr">${lines.map(x=>HD.test(x)?`<li class="fxh">${fmt(x)}</li>`:`<li>${statLine(x)}</li>`).join("")}</ul>
 ${tip.length?`<details class="tipx"><summary>${T("In-game tooltip")}</summary><ul>${tip.map(x=>HD.test(x)?`<li class="fxh">${fmt(stT(x))}</li>`:`<li>${statLine(stT(x))}</li>`).join("")}</ul></details>`:""}
 ${cfg.length?`<details class="tipx"><summary>${T("Config values ({n})",{n:cfg.length})}</summary><table class="cfg">${cfg.map(([a,...b])=>`<tr><td>${esc(a)}</td><td class="num">${esc(cfgTx(b.join(": ")))}</td></tr>`).join("")}</table></details>`:""}`}
const guideHtml=g=>(needPics(),"")+`<div class="gbk">${g.i?`<img alt="" src="${g.i}">`:""}<div><small>📖 ${esc(g.b)} · ${esc(g.e)}</small><p>${esc(gameTx(TD(g.t)))}</p></div></div>`;
function page(d){
 document.title=TD(d.n)+" · Linggango Wiki";seedBg("item"+d.m,D.filter(x=>x.m===d.m));
 const F=mf(d.m),slot=d.sl.map(x=>T(x)).join(", ")||"—",loot=d.g==="Loot",secs=[];
 /* when and how it opens, said once: the Act, the luck window, the Keeper gate, the ring it needs */
 const gate=d.gk?T("locked until {boss} falls (you can't craft, use or wear it before, even from a chest)",{boss:`<b>${TD(GK[d.gk])}</b>`}):"";
 const unlock=`<div class="unlock"><i class="ui" style="--ui:var(--rt-${d.gk||d.rq?"lg_lock":"lg_check"})" aria-hidden="true"></i><div><b>${esc(actL(d.t))}</b>${d.a===-1?" · "+T("drops from L2 Hostility mobs by their level"):d.a!==d.t?" · "+T("with luck from {act}",{act:esc(actL(d.a))}):" · "+esc(T(ACT[d.t][1]))}${gate?`<br><span>${gate}</span>`:""}${d.rq?`<br><span>${T("only for bearers of the {ring}",{ring:`<a href="#i${BYID[RQRING[d.rq]].ix}">${rqName(d)}</a>`})}</span>`:""}</div></div>`;
 const must=isMust(d)?`<div class="mh-banner"><span class="mhs">★</span><div><b>${T("Must-Have")}</b><p>${!/etching|charm_of_looting/.test(d.id)?T("It adds curio slots, so you can wear more curios at once: every other relic on this wiki gets better with it."):/etching/.test(d.id)?T("An Etching turns one of your Catastrophe Scroll curses into a blessing and is an ingredient for most Celestial Artifacts relics."):T("A Looting Charm unlocks L2 Hostility trait drops; without the right tier worn, trait mobs drop nothing extra.")} ${T("Get it as soon as {act} opens and keep it in every build. Base power rating: {tier}.",{act:esc(actL(d.t)),tier:`<b>${RN[d.br]}</b>`})}</p></div></div>`:"";
 const scarce=d.sca?`<div class="mh-banner sca"><span class="mhs">⛏</span><div><b>${T("Scarce Act 0 material")}</b><p>${T("Daemonium and Iridium need a high-tier pickaxe to mine, but Terramity structures can drop them in chests. That makes this craftable early with luck, so it is rated one rarity higher than other Act 0 curios.")}</p></div></div>`:"";
 secs.push(["get",loot?T("Where it drops"):T("How to get it"),`${must}${scarce}${unlock}${howVisual(d)}${howText(d)}`]);
 {const gu=typeof GUIDE!=="undefined"&&GUIDE[d.id];if(gu)secs.push(["guide",T("From the guide book"),guideHtml(gu)])}
 {const ev=evoSec(d);if(ev)secs.push(["evo",T("Evolution"),ev])}
 const rel=d.tg.map((t,j)=>[t,d.st[j],d.sr&&d.sr[j]]).filter(r=>typeof r[1]==="string"),relic=rel.filter(r=>r[0]==="relic"),other=rel.filter(r=>r[0]!=="relic");
 let sh="";
 if(RL[d.id])secs.push(["levels",T("Relic levels"),rlPanel(d.id)]);
 if(relic.length&&!RL[d.id])sh+=`<div class="tw"><table><thead><tr><th>${T("Stat")}</th><th>${T("On pickup (random)")}</th><th>${T("Max upgrade")}</th></tr></thead><tbody>${relic.map(r=>relicRows(r[1])).join("")}</tbody></table></div>`;
 sh=statsHtml(d,other)+sh;
 if(sh)secs.push(["stats",T("Stats"),sh]);
 if(typeof gCurioMs==="function"){const mh=gCurioMs(d);if(mh)secs.push(["ms",T("Measured in game"),mh])}
 if(d.uid.length)secs.push(["uses",T("Used to craft"),`<div class="cards">${d.uid.map(o=>{const t=BYID[o];return `<a class="card"${t?` href="#i${t.ix}" data-t="${t.ix}"`:""}>${img(o)}<span>${esc(NM[o]||o)}${t?"":` <span class="meta">${T("(not a curio)")}</span>`}</span></a>`}).join("")}</div>`]);
 const bar=(v,l)=>`<div class="sg" style="grid-template-columns:150px 1fr;margin:var(--s1) 0"><span>${l}</span><div class="bar"><i style="width:${Math.round(Math.min(5,Math.max(0,v))*20)}%;background:var(--rc);opacity:.55"></i><span>${(+v).toFixed(1)} / 5</span></div></div>`;
  const same=D.filter(x=>x!==d&&x.m===d.m&&x.t===d.t).slice(0,8);
 const ic=slotImg(d);
 // slot neighbours
 const s0=d.sl[0],sx=s0?byRank(D.filter(x=>x.sl.includes(s0))):[],si=sx.indexOf(d),pv=sx[si-1],nx=sx[si+1];
 const near=sx.filter(x=>x!==d).slice(Math.max(0,si-4),Math.max(0,si-4)+8);
 // the link lands on Curios filtered to slot:<s0> with the sidebar filters kept: count what it will show
 let seeAll="";if(s0){const q0=st.q;st.q=slotQ(s0);let n=0,all=0;D.forEach(x=>{if(qMatch(x)){all++;if(pass(x))n++}});st.q=q0;
  seeAll=n===all?T("see all {n} →",{n:all}):T("see {n} (your filters; {all} in all) →",{n,all})}
 const art=`<div class="ip-art"><span class="ip-badge">${RN[d.r]}</span><div class="ip-stage" style="${tex(d.t)}">${envFx(d.t)}<span class="orb" aria-hidden="true">${[0,1,2,3,4,5].map(i=>`<i style="--k:${i};--sp:var(--v-${MFSP[F[0]]||"p_glint"})"></i>`).join("")}</span><div class="ip-icon framed">${ic}${glint(d)}</div></div><span class="ip-mini">${ic}</span><span class="ip-path" title="${esc(actL(d.t))}">${emblem(d.t,"xs")}</span></div>`;
 const sib=s0&&near.length?`<section class="sib"><h2>${T("More {slot} curios",{slot:esc(T(s0))})} <a style="font-size:13px;font-weight:400" href="#slot/${enc(s0)}">${seeAll}</a></h2><div class="gridc">${near.map(gcard).join("")}</div><nav class="pnx">${pv?`<a href="#i${pv.ix}"><small>${T("← Previous in {slot}",{slot:esc(T(s0))})}</small>${esc(TD(pv.n))}</a>`:"<span></span>"}${nx?`<a href="#i${nx.ix}"><small>${T("Next in {slot} →",{slot:esc(T(s0))})}</small>${esc(TD(nx.n))}</a>`:""}</nav></section>`:"";
 el("main").innerHTML=article({cls:"r"+d.r,data:` data-mf="${F[0]}"`,style:`${tex(d.t)};--tc:${ACT[d.t][2]}`,
  crumb:`<div class="crumb ip-crumb"><a href="#">${T("Home")}</a> / <a href="#home">${T("Curios")}</a> / <a href="#act/${d.t}">${actL(d.t)}</a></div>`,
  pre:isMust(d)?'<span class="mstar">★</span>':"",title:esc(TD(d.n)),alt:enAlt(d.n),lead:fmt(fxT(d)),
  meta:`<span class="ip-fam">${esc(d.m)}</span><span>${rLabel(d)}</span><span>${esc(slot)}</span><span>${loot?T("Loot"):T("Craft")}</span>${d.nw?`<span>${T("new in 6.6.6")}</span>`:""}`,
  secs,after:sib,art,
  box:{head:`<span class="ip-slot">${ic}</span><div><b>${esc(TD(d.n))}</b><span>${esc(d.m)}</span></div>`,
   rows:[[T("Slot"),esc(slot)],[T("Power"),rLabel(d)+(d.pe?` <span class="kest">${T("estimate")}</span>`:""),d.pe?T("Read from its text: the game test cannot see what it does (a condition, an active ability, loot or utility)"):T("Measured in game: how much it adds to a typical build of its Act, next to the other curios of that Act")],[T("Act"),actL(d.t)],d.a!==d.t&&[T("With luck"),actL(d.a)],d.rq&&[T("Requires"),rqName(d)],[T("Role"),isMust(d)?T("Every build"):d.ro.map(k=>T(ROLE[k])).join(", ")],[`<span class="ign-dt">${T("Name colour")}</span>`,igName(d),T("Colour of the item's name in game; not the wiki rarity")],SK.i[d.id]&&[T("Duplicates"),skTag(d.id)]],
   foot:idBox(d.id)},
  nav:wikiNav({act:d.t},[[`${esc(d.m)} · ${esc(actL(d.t))}`,same.map(x=>["#i"+x.ix,esc(TD(x.n))])]])});
 wireArticle();
}

/* ---------- guide ---------- */
const CF={ok:[ui("check"),"Tested in game"],code:[ui("spy"),"Read from code/config"],q:[ui("q"),"Not yet confirmed"]};
const cf=k=>`<span class="badge" title="${CF[k][1]}">${CF[k][0]} ${CF[k][1]}</span>`;
const ACTS=[
["0","— (Sticks and Stones)","—","—","—","Pale Branch (Heart slot): stand still for 3 s for Resistance V and knockback immunity. Phantom Finger (+2 Ring) is craftable from the start.","code"],
["I","The Iron Colossus","Blunt / Lightning","Iron (Act II)","—","—","code"],
["II","The Goblin Lord","Fire / Slash","Gold (Act III)","—","Goblin Army invasions start appearing. Its treasure bag gives the Gilded Plate for the Unpolished Charm. 6.6.6 lowered its armor to 12 (from 30).","code"],
["III","Arion","Frost / Pierce","Emerald (Act IV)","Unpolished","Unpolished Charm = Gilded Plate + Emerald Totem (Arion's summon item), so it can be made before the fight. With it worn, Gravity-trait mobs (level ≥ 50) drop Dragon's Breath → True Enderian Scarf, Enderian Treads. Thrash Gloves. Beating Arion unlocks the Illager Crusade invasion (finale: the Vizier) and natural Goety mob spawns; Night of Chaos moved to after the Ender Dragon in 6.6.6. Arion has 20 armor on foot and 15 on its Ravager.","code"],
["IV","Eldorath","Blunt / Nature","Diamond (Act V)","—","Defeating it opens the Nether. Elvenite and Bloody ore in deepslate only need mining power 3. 6.6.6: armor 18 instead of 40.","code"],
["V","Zoranth the Forgotten","Frost / Holy (fought in the Nether)","Netherite (Act VI)","Magical","The Magical Charm needs Celestial Netherite from the Nether. Grave Gloves (Grave Dust from the Reaper). Magical trait drops for the Study Lectern: Hard Ice, Explosion Shard, Life Essence.","code"],
["VI","The Elvenite Paladin","Blunt / Dark (resists Holy)","Elvenite (Act VII)","Chaotic","The Ender Dragon comes first: its treasure bag gives the 4 Khyros's Goldened Tears for Titan's Insigna, the Paladin's summon item, and its death switches on Hardmode (×2.1 health and damage). The Chaotic Charm needs a Wanderer's Fallen Shard from the End. Demon Heart needs a Nether Star from the Wither; eat it before Heart of the Beloved (+1 Accessory). 6.6.6: the Paladin gets a second phase at half health, and all of Ad Astra opens after it.","code"],
["VII","Vaedric","Holy / Lightning","Voiderite (Act VIII)","—","Chaotic trait drops: Force Field, Captured Wind. 6.6.6: he brings at most 2 Void Tomes (later, slower, no copied traits) and freezes and glows with portal sparks at your feet right before he blinks to you.","code"],
["VIII","The Discord, the Calamitous Keeper","Bringer Holy/Pierce · Famine Fire/Holy · Chaos Frost/Pierce · Discord Arcane/Blunt","Cataclysm (Act IX)","—","The pack config makes The Discord the Calamitous Keeper; Bringer of Doom, Famine and Chaos are side fights. Sigil of Calamity summoning all of them at once: untested.","code"],
["IX","Sanghor","Fire / Holy","Blood (Act X)","—","Infinity Glove: +5 Ring, +1 Charm. Beating Sanghor moves the Keeper Ladder (the L2 Hostility levels every Keeper you beat adds to the mobs around you) from rung 7 to rung 8: +102 mob levels instead of +69. Hemalith Catalyst never drops from its treasure bag (a bug in the bag's loot code), so craft it from Bloody Ingot + Blaze Powder + Quartz. Whether Judged blocks orb healing: untested.","q"],
["X","Zoranth Newborn","Dark / Frost","Sun (Act XI)","—","Its treasure bag gives the Helionite Block for the Miraculous Charm.","q"],
["XI","Nyxaris","Holy / Lightning","Act XII (end game)","Miraculous","Miraculous trait drops: Resonant Feather, Sun Membrane, Void Eye. Helionite gate (damage floor 50). Its treasure bag gives the materials for the three Act XII curios: Shadow Fragment for The Eclypse, Shadowed Ingot for the Non-Euclidean Cube, which Heart of Creation is crafted from.","code"]];
const L2=[["Unpolished","Act III (needs the Goblin Lord's Gilded Plate)",22,"Fiery → 8 blaze rods (25%); Gravity ≥ 50 → 4 dragon's breath (10%/level)"],["Magical","Act V (needs Celestial Netherite from the Nether)",16,"Hard Ice, Explosion Shard, Life Essence"],["Chaotic","Ender Dragon Act (needs a Wanderer's Fallen Shard from the End)",8,"Force Field, Captured Wind"],["Miraculous","Act XI (needs Helionite from Zoranth Newborn)",9,"Resonant Feather, Sun Membrane, Void Eye"]];
const TF={Iron:6,Gold:8,Emerald:11,Diamond:14,Netherite:18,Elvenite:24,Voiderite:31,Bloody:40,Helionite:50};
const CHN=["","Unpolished","Magical","Chaotic","Miraculous"];
function gcalc(){const b=+el("gb").value||0,s=Math.min(+el("gs").value||0,20)*.5,sp=+el("gp").value||1.6,f=TF[el("gt").value];const fr=Math.min(f,(f+1)*1.8/sp-1),raw=b+s,out=Math.max(raw,fr);
 el("go").innerHTML=`Effective floor: <b>${fr.toFixed(2)}</b> · Base + Somber: <b>${raw.toFixed(2)}</b> → Damage used: <b>${out.toFixed(2)}</b>${raw<fr&&s>0?" <span class='badge loot'>Somber Stones are swallowed by the floor</span>":""}`}
const LURE={"adaptive":"Netherite Scrap","blindness":"Ink Sac","corrosion":"Copper Block","counter_strike":"Shield","cursed":"Soul Sand","dementor":"Hostility Essence + Echo Shard","dispell":"Hostility Essence + Lapis Block","drain":"Nether Wart","erosion":"Oxidized Copper","fiery":"Blaze Powder","freezing":"Blue Ice","gravity":"Anvil","grenade":"TNT","growth":"Bone Block","hexed":"Crying Obsidian","invisible":"Golden Carrot","killer_aura":"Hostility Essence + Wither Skeleton Skull","levitation":"Phantom Membrane","moonwalk":"Feather","nausea":"Pufferfish","poison":"Spider Eye","protection":"Scute","pulling":"Hostility Essence + Fishing Rod","ragnarok":"Hostility Essence + Nether Star","reflect":"Prismarine Crystals","regenerate":"Ghast Tear","repelling":"Hostility Essence + Piston","reprint":"Hostility Essence + Book and Quill","shulker":"Shulker Shell","slowness":"Cobweb","soul_burner":"Soul Campfire","speedy":"Sugar","split":"Slime Block","tank":"Iron Block","teleport":"Hostility Essence + Chorus Fruit","weakness":"Fermented Spider Eye","wither":"Wither Rose"};const L2D=[{"tr":["adaptive"],"item":"l2complements:cursed_droplet","n":1,"charm":2,"ch":0.0,"rb":0.15,"lv":[[1,5]],"ml":[]},{"tr":["arena"],"item":"l2hostility:chaos_ingot","n":1,"charm":4,"ch":0.5,"rb":0.0,"lv":[[1,5]],"ml":[]},{"tr":["blindness"],"item":"minecraft:ink_sac","n":8,"charm":1,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["corrosion"],"item":"l2complements:cursed_droplet","n":1,"charm":2,"ch":0.0,"rb":0.2,"lv":[[1,5]],"ml":[]},{"tr":["counter_strike"],"item":"l2complements:explosion_shard","n":1,"charm":2,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["cursed"],"item":"l2complements:cursed_droplet","n":1,"charm":2,"ch":0.0,"rb":0.05,"lv":[[2,5]],"ml":[]},{"tr":["cursed"],"item":"minecraft:potion","n":1,"charm":1,"ch":0.0,"rb":0.2,"lv":[[1,5]],"ml":[]},{"tr":["killer_aura","ragnarok"],"item":"l2hostility:chaos_ingot","n":1,"charm":4,"ch":1.0,"rb":0.0,"lv":[[1,5],[1,5]],"ml":[]},{"tr":["dementor"],"item":"l2complements:sun_membrane","n":1,"charm":4,"ch":0.2,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["dispell"],"item":"l2hostility:imagine_breaker","n":1,"charm":4,"ch":1.0,"rb":0.0,"lv":[[3,5]],"ml":[]},{"tr":["dispell"],"item":"l2complements:resonant_feather","n":1,"charm":4,"ch":0.2,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["drain"],"item":"l2hostility:witch_droplet","n":1,"charm":2,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["erosion"],"item":"l2complements:cursed_droplet","n":1,"charm":2,"ch":0.0,"rb":0.2,"lv":[[1,5]],"ml":[]},{"tr":["fiery"],"item":"minecraft:blaze_rod","n":8,"charm":1,"ch":0.25,"rb":0.0,"lv":[[1,5]],"ml":[]},{"tr":["freezing"],"item":"l2complements:hard_ice","n":2,"charm":2,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["gravity"],"item":"minecraft:dragon_breath","n":4,"charm":1,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["grenade"],"item":"minecraft:creeper_head","n":1,"charm":1,"ch":0.25,"rb":0.0,"lv":[[5,5]],"ml":[]},{"tr":["grenade"],"item":"minecraft:gunpowder","n":4,"charm":1,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["grenade"],"item":"l2complements:storm_core","n":1,"charm":3,"ch":0.0,"rb":0.1,"lv":[[3,5]],"ml":[]},{"tr":["growth"],"item":"minecraft:enchanted_golden_apple","n":1,"charm":1,"ch":0.0,"rb":0.02,"lv":[[1,5]],"ml":[]},{"tr":["invisible"],"item":"minecraft:phantom_membrane","n":4,"charm":1,"ch":0.25,"rb":0.0,"lv":[[1,5]],"ml":[]},{"tr":["killer_aura"],"item":"l2complements:heirophant_green","n":1,"charm":4,"ch":0.0,"rb":0.02,"lv":[[1,5]],"ml":[]},{"tr":["levitation"],"item":"l2complements:captured_shulker_bullet","n":1,"charm":2,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["master"],"item":"l2hostility:chaos_ingot","n":4,"charm":4,"ch":1.0,"rb":0.0,"lv":[[1,5]],"ml":[]},{"tr":["moonwalk"],"item":"minecraft:dragon_breath","n":4,"charm":1,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["nausea"],"item":"minecraft:pufferfish","n":4,"charm":1,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["poison"],"item":"minecraft:spider_eye","n":8,"charm":1,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["protection"],"item":"minecraft:scute","n":4,"charm":1,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["protection"],"item":"minecraft:shulker_shell","n":1,"charm":1,"ch":0.0,"rb":0.1,"lv":[[3,5]],"ml":[]},{"tr":["pulling"],"item":"l2complements:blackstone_core","n":1,"charm":3,"ch":0.0,"rb":0.05,"lv":[[1,5]],"ml":[]},{"tr":["ragnarok"],"item":"l2complements:eternium_nugget","n":4,"charm":4,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["reflect"],"item":"l2complements:explosion_shard","n":1,"charm":2,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["regenerate"],"item":"minecraft:ghast_tear","n":4,"charm":1,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["regenerate"],"item":"l2complements:life_essence","n":1,"charm":2,"ch":-0.1,"rb":0.1,"lv":[[2,5]],"ml":[]},{"tr":["regenerate"],"item":"l2complements:totemic_gold_nugget","n":4,"charm":3,"ch":0.0,"rb":0.1,"lv":[[3,5]],"ml":[]},{"tr":["repelling"],"item":"l2complements:force_field","n":1,"charm":3,"ch":0.2,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["reprint"],"item":"l2hostility:book_of_reprint","n":1,"charm":3,"ch":1.0,"rb":0.0,"lv":[[1,5]],"ml":[]},{"tr":["shulker"],"item":"l2complements:captured_shulker_bullet","n":1,"charm":2,"ch":0.0,"rb":0.2,"lv":[[1,5]],"ml":[]},{"tr":["slowness"],"item":"minecraft:cobweb","n":4,"charm":1,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["soul_burner"],"item":"l2complements:soul_flame","n":2,"charm":2,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["speedy"],"item":"l2complements:captured_wind","n":1,"charm":3,"ch":0.0,"rb":0.1,"lv":[[3,5]],"ml":[{"condition":"l2hostility:mob_level","maxLevel":0,"minLevel":100}]},{"tr":["speedy"],"item":"minecraft:rabbit_foot","n":2,"charm":1,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["speedy","tank"],"item":"l2complements:sculkium_nugget","n":4,"charm":3,"ch":0.0,"rb":0.1,"lv":[[3,5],[3,5]],"ml":[]},{"tr":["split"],"item":"l2complements:guardian_eye","n":1,"charm":2,"ch":0.0,"rb":0.05,"lv":[[1,5]],"ml":[]},{"tr":["tank"],"item":"minecraft:diamond","n":4,"charm":1,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["tank"],"item":"minecraft:netherite_scrap","n":1,"charm":1,"ch":0.0,"rb":0.1,"lv":[[3,5]],"ml":[]},{"tr":["tank","protection"],"item":"l2complements:shulkerate_ingot","n":2,"charm":2,"ch":0.0,"rb":0.1,"lv":[[3,5],[4,5]],"ml":[]},{"tr":["tank","protection"],"item":"l2complements:shulkerate_nugget","n":6,"charm":2,"ch":0.0,"rb":0.1,"lv":[[3,5],[1,3]],"ml":[]},{"tr":["teleport"],"item":"l2complements:void_eye","n":1,"charm":4,"ch":0.2,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["undying"],"item":"l2complements:life_essence","n":1,"charm":2,"ch":0.5,"rb":0.0,"lv":[[1,5]],"ml":[]},{"tr":["undying"],"item":"minecraft:totem_of_undying","n":1,"charm":1,"ch":1.0,"rb":0.0,"lv":[[1,5]],"ml":[]},{"tr":["weakness"],"item":"minecraft:fermented_spider_eye","n":8,"charm":1,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["wither"],"item":"minecraft:wither_rose","n":8,"charm":1,"ch":0.0,"rb":0.1,"lv":[[1,5]],"ml":[]},{"tr":["wither"],"item":"minecraft:wither_skeleton_skull","n":1,"charm":1,"ch":0.0,"rb":0.1,"lv":[[3,5]],"ml":[]}];const BOSSR=[["Iron Colossus (Keeper)",0,"✓","Act I Keeper; 10 damage",[]],["Swampjaw",2,"❓","Meet Your Fight, summoned with Fossil Bait in a swamp",["meetyourfight:mossy_tooth"]],["Draugr → Night Shade",2,"❓","the second phase counts as the kill",["soulsweapons:draugr"]],["Goblin Lord (Keeper)",2,"✓","Act II Keeper; 11 dmg / 12 armor",[]],["Bellringer",3,"❓","Haunted Bell",["meetyourfight:phantoplasm"]],["Frostbitten Golem",3,"❓","Legendary Monsters, spawns naturally",["legendary_monsters:frozen_rune"]],["Dune Sentinel",3,"❓","",["legendary_monsters:crystal_of_sandstorm"]],["Overgrown Colossus",3,"❓","",["legendary_monsters:nature_crystal"]],["Skeletosaurus",5,"❓","",["legendary_monsters:dinosaur_bone"]],["Yeti",3,"❓","",[]],["Arion (Keeper)",3,"✓","Act III Keeper; its summon item, the Emerald Totem, is also half of the Unpolished Charm",[]],["Frostmaw",4,"❓","",["mowziesmobs:ice_crystal"]],["Umvuthi",4,"❓","",["mowziesmobs:sol_visage"]],["Naga",4,"❓","",["mowziesmobs:naga_fang"]],["Dame Fortuna",4,"❓","Devil's Ante",["meetyourfight:fortunes_favor"]],["Dead King",4,"❓","Iron's Spells, in the Catacombs",["irons_spellbooks:arcane_essence","irons_spellbooks:blank_rune","irons_spellbooks:blood_staff","irons_spellbooks:necronomicon_spell_book","irons_spellbooks:scroll"]],["Cumulonimbus",4,"❓","",["legendary_monsters:air_rune","legendary_monsters:atmospheric_boots"]],["Ancient Guardian",4,"❓","",["legendary_monsters:anchor_handle"]],["Eldorath (Keeper)",4,"✓","Act IV Keeper; 14 dmg / 18 armor; opens the Nether",[]],["Netherite Monstrosity",5,"🔍","in the Nether, which opens after Eldorath",["cataclysm:infernal_forge","cataclysm:lava_power_cell","cataclysm:monstrous_horn"]],["Rosalyne",5,"❓","",["meetyourfight:violet_bloom"]],["Luxtructosaurus",5,"❓","Alex's Caves",["alexscaves:tectonic_shard"]],["Forsaken",5,"❓","",["alexscaves:pure_darkness"]],["Returning Knight",5,"❓","",["soulsweapons:arkenstone","soulsweapons:lord_soul_rose","soulsweapons:nightfall","soulsweapons:soul_ingot"]],["Vizier",5,"❓","Goety, a Dark Scroll used inside a woodland mansion",["goety:treasure_pouch"]],["Malkuth",5,"❓","",["fdbosses:fire_and_ice_core","fdbosses:malkuth_fist","fdbosses:malkuth_trophy"]],["Corpse Warlock",5,"❓","",[]],["Lich",5,"❓","",["bosses_of_mass_destruction:ancient_anima"]],["Underworld Knight",5,"🔍","in the Nether",[]],["Zoranth the Forgotten (Keeper)",5,"✓","Act V Keeper; 20 dmg / 50 armor",[]],["Super Sniffer",6,"✓","pack stats 27 dmg / 65 armor",["terramity:accursed_soul","terramity:cosmilite_upgrade_smithing_template","terramity:evil_king_armor_boots","terramity:evil_king_armor_chestplate","terramity:evil_king_armor_helmet","terramity:evil_king_armor_leggings","terramity:gaianite_cluster","terramity:giant_sniffers_hoof","terramity:guided_energy_blast","terramity:hermit_bean","terramity:iridescent_shard","terramity:music_sheet_of_the_legendary_super_sniffer","terramity:onyx","terramity:ruby","terramity:sapphire","terramity:super_sniffers_pelt","terramity:topaz","terramity:virentium_upgrade_smithing_template"]],["Gundalf, Circe, Merlin (Shadow Wizards)",6,"✓","80 armor; Chthonic Cathedral on the Nether roof",["terramity:antiprism","terramity:chthonic_shell_casing","terramity:fortunes_favor","terramity:gold_medal","terramity:gundalfs_hat_helmet","terramity:iridium_chunk","terramity:malediction_bracelets","terramity:music_sheet_of_the_shadow_wizards","terramity:occult_fabric","terramity:swag_glasses"]],["Forgotten Guardian",6,"✓","30 damage; the Undergarden opens after Eldorath",["undergarden:forgotten_nugget"]],["Wither",6,"✓","32 dmg / 20 armor; drops the Nether Star for Demon Heart, Made in Heaven",[]],["Ender Dragon",6,"🔍","required before the Elvenite Paladin; enables Hardmode ×2.1",[]],["Ender Guardian",6.3,"🔍","in the End",["cataclysm:gauntlet_of_guard"]],["Ancient Remnant",6,"❓","",["cataclysm:ancient_metal_block","cataclysm:remnant_skull","cataclysm:sandstorm_in_a_bottle"]],["Gauntlet",6,"🔍","in the Nether",[]],["Obsidilith",6.3,"🔍","in the End",[]],["Void Blossom",6,"❓","",["bosses_of_mass_destruction:crystal_fruit","bosses_of_mass_destruction:void_thorn"]],["Chesed",6,"❓","",["fdbosses:chesed_trophy","fdbosses:lightning_core","fdbosses:phase_sphere"]],["Moonknight",6,"❓","",["soulsweapons:essence_of_luminescence","soulsweapons:lord_soul_white","soulsweapons:moonlight_greatsword","soulsweapons:moonstone"]],["Accursed Lord",6,"❓","",["soulsweapons:darkin_blade","soulsweapons:lord_soul_red","soulsweapons:withered_demon_heart"]],["Tyros (fire boss)",6,"🔍","in the Nether",["irons_spellbooks:arcane_essence","irons_spellbooks:betrayer_signet","irons_spellbooks:cinder_essence","irons_spellbooks:decrepit_scythe","irons_spellbooks:divine_soulshard"]],["Infernal Dragon",6,"❓","",[]],["Redstone Monstrosity",6,"❓","",["minecraft:redstone_block","minecraft:cobblestone"]],["Elvenite Paladin (Keeper)",6,"✓","Act VI Keeper; 30 dmg / 100 armor; resists Holy",[]],["Gob, King of Gnomes",7,"✓","45 dmg / 70 armor",["terramity:belt_of_the_gnome_king","terramity:dimlite_upgrade_smithing_template","terramity:gobs_claymore","terramity:gobs_gilded_hat_helmet","terramity:iridescent_shard","terramity:lost_soul","terramity:music_sheet_of_the_gnome_king","terramity:onyx","terramity:ruby","terramity:sapphire","terramity:topaz","terramity:virentium_upgrade_smithing_template"]],["Trial Guardian",7,"✓","35 dmg / 85 armor; needs a Spire Key",["terramity:chthonic_cursemark","terramity:conductite_upgrade_smithing_template","terramity:dimlite_nugget","terramity:energized_core","terramity:giant_dungeon_slab","terramity:guardian_grimoire","terramity:guardians_hand","terramity:hellspec_upgrade_smithing_template","terramity:lost_soul","terramity:music_sheet_of_the_trial_guardian","terramity:perish_staff","terramity:spire_key","terramity:spiteful_soul","terramity:void_upgrade_smithing_template"]],["Ignis",7,"🔍","in the Nether",["cataclysm:ignitium_ingot"]],["The Harbinger",7,"❓","",["cataclysm:witherite_block"]],["The Leviathan",7,"❓","",["cataclysm:abyssal_egg","cataclysm:tidal_claws"]],["Geburah",7,"❓","",["fdbosses:divine_gear","fdbosses:geburah_trophy","fdbosses:justice_core","fdbosses:polished_justicestone"]],["Nameless Guardian",7,"❓","",[]],["Realm Warden",7,"❓","",["eeeabsmobs:ancient_drive_crystal","eeeabsmobs:boundary_brick","eeeabsmobs:guardian_cube","eeeabsmobs:relicron_upgrade_smithing_template"]],["Relic Annihilator",7,"❓","",["eeeabsmobs:ancient_drive_crystal","eeeabsmobs:boundary_brick","eeeabsmobs:chain_gear","eeeabsmobs:relicron_upgrade_smithing_template"]],["Day Stalker",7,"❓","",["soulsweapons:dawnbreaker","soulsweapons:lord_soul_day_stalker"]],["Night Prowler",7,"❓","",["soulsweapons:forlorn_scythe","soulsweapons:lord_soul_night_prowler","soulsweapons:soul_reaper"]],["The Obliterator",7,"❓","",["legendary_monsters:portal_shard"]],["Apostle",7,"❓","Goety, ritual in the Nether",["goety:treasure_pouch"]],["Vaedric (Keeper)",7,"✓","Act VII Keeper; 38 dmg / 120 armor",[]],["Ferrous Wroughtnaut",8,"✓","pack sets 40 damage, on par with Vaedric",["mowziesmobs:wrought_axe","mowziesmobs:wrought_helmet"]],["Maledictus",8,"❓","",["cataclysm:cursium_ingot"]],["Scylla",8,"❓","",["cataclysm:essence_of_the_storm","cataclysm:lacrima"]],["Immortal",8,"❓","",[]],["Chaos Monarch",8,"❓","",["soulsweapons:blood_vial_recipe_page","soulsweapons:chaos_crown","soulsweapons:chaos_robes","soulsweapons:lord_soul_void","soulsweapons:withered_wabbajack"]],["The Nightwarden",8,"❓","",["irons_spellbooks:arcane_essence","irons_spellbooks:blank_rune","irons_spellbooks:legendary_ink","irons_spellbooks:scroll","traveloptics:cradle_of_will","traveloptics:stellothorn","traveloptics:withered_excrucis"]],["The Calamities: Bringer, Famine, Chaos, Discord (Keeper)",8,"✓","Bringer 68 / 240 armor; Famine 60 / 320; Chaos 40 / 330; Discord 20 / 130",[]],["Virtue",9,"✓","85 damage",["terramity:angel_feather","terramity:archangel_halo","terramity:music_sheet_of_cleansing"]],["Ultra Sniffer",9,"✓","150 damage; beat Super Sniffer first",["terramity:antiprism","terramity:black_matter","terramity:conductite_upgrade_smithing_template","terramity:dragon_band","terramity:hellspec_upgrade_smithing_template","terramity:hermit_bean","terramity:iridium_chunk","terramity:kamehameha","terramity:music_sheet_of_the_omnipotent_ultra_sniffer","terramity:prismatic_jewel","terramity:spectral_soul","terramity:ultra_sniffer_fur","terramity:ultra_sniffers_pelt","terramity:void_upgrade_smithing_template"]],["Lord Pumpkinhead",9,"✓","60 damage, on par with Famine",[]],["Sanghor (Keeper)",9,"✓","Act IX Keeper; 42 dmg / 340 armor",[]],["Zoranth Newborn (Keeper)",10,"✓","Act X Keeper; 46 dmg / 400 armor; its treasure bag holds the Helionite for the Miraculous Charm",[]],["Nyxaris (Keeper)",11,"✓","Act XI Keeper; 50 dmg / 450 armor",[]]];
if(typeof BEXTRA!=="undefined"){const have=new Set(BOSSR.map(r=>r[0]));BEXTRA.forEach(([n,a,m,f,it,mod,ent,gn])=>{if(have.has(n))return;BOSSR.push([n,a,m,f,it]);
 if(typeof SIDEB!=="undefined"&&!SIDEB[n])SIDEB[n]={entity:ent,mod,gname:gn||undefined,find:f,drops:it.map(id=>({id,n:NM[id]||id.split(":")[1].replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase())})),summon:null}});
 {const DROP=new Set(["Yeti","Naga","Super Sniffer","Ultra Sniffer","Forgotten Guardian","Infernal Dragon","Gob, King of Gnomes","Nameless Guardian","Virtue"]);
 for(let i=BOSSR.length-1;i>=0;i--)if(DROP.has(BOSSR[i][0])){if(typeof SIDEB!=="undefined")delete SIDEB[BOSSR[i][0]];BOSSR.splice(i,1)}}
 // Act order follows the quest book (computed in build/patches/boss_order.py)
 if(typeof BACT!=="undefined")BOSSR.forEach(r=>{if(BACT[r[0]]!=null)r[1]=BACT[r[0]]});
 BOSSR.forEach(r=>{r[2]=({"✓":ui("check"),"🔍":ui("spy"),"❓":ui("q")})[r[2]]||r[2]});
 BOSSR.sort((x,y)=>x[1]-y[1]);const dr=BOSSR.find(r=>/^Draugr/.test(r[0]));if(dr)dr[1]=3}
// portraits of side bosses drawn with Java models, rendered from the mod jars (build/pack_audit/side_bosses/jmodel.py)
// drop chances from the mods' loot tables for bosses whose drop list came from the quest book (build/pack_audit/side_bosses/loot_chance.py)
if(typeof SDROP!=="undefined"&&typeof SIDEB!=="undefined")for(const n in SDROP){const b=SIDEB[n];if(!b)continue;const L=SDROP[n].drops,by=Object.fromEntries(L.map(x=>[x.id,x]));
 if(!(b.drops||[]).length)b.drops=L.filter(x=>x.id!=="goety:treasure_pouch").slice(0,6);else b.drops.forEach(x=>{const y=by[x.id];if(y&&!x.chance){x.chance=y.chance;x.count=y.count}});b.drops_src=SDROP[n].src}
if(typeof SIMG!=="undefined"&&typeof SIDEB!=="undefined")for(const n in SIMG)if(SIDEB[n]&&!SIDEB[n].img){SIDEB[n].img=SIMG[n];SIDEB[n].img_src="render"}
// 6.6.6: no quest chapter is locked any more ([progression_gates] chapters = []); the mods with the most items in each linggango_tweaks:gated/<tier> tag
const CHAP=[[2,"only 6 items: Ars Nouveau's shaper foci, Enigmatic Legacy's Golem Heart and Magnet Ring, Animus's Hellforged Bow, a Blood Magic teleposer focus"],[3,"Goety (121 items: most foci and ritual gear), Goety Awaken, Ars Nouveau, Blood Magic, Mahou Tsukai, Nature's Aura"],[4,"Goety, Goety Awaken, Ars Nouveau, Goety Cataclysm, Animus, Blood Magic, Hexerei, Mahou Tsukai"],[5,"Nature's Aura, Goety, Blood Magic, Enigmatic Legacy, Mahou Tsukai, Enigmatic Addons"],[6,"Mystical Agriculture, Mekanism (+ Generators), Industrial Foregoing, Applied Flux, ExtendedAE, AE2, Nature's Aura"],[7,"Mekanism, Ad Astra (all of it), Mystical Agriculture, Just Dire Things, Blood Magic, ExtendedAE"],[8,"Evolved Mekanism, Mystical Agriculture, Sanctified Legacy, MEGA Cells, Mekanism"],[9,"Evolved Mekanism, MEGA Cells, SomakeSpells, Mahou Tsukai"],[10,"Evolved Mekanism, MEGA Cells"],[11,"Evolved Mekanism, Mekanism, MEGA Cells"]];
const sec=(id,t,body)=>`<section class="s" id="${id}"><h2>${t}</h2>${body}</section>`;
const tbl=(head,rows)=>`<div class="tw"><table><tr>${head.map(h=>`<th>${h}</th>`).join("")}</tr>${rows}</table></div>`;
function guide(){
 document.title="Mid & end game guide · Linggango Wiki";
 const SEC=[["g1","Act axis"],["g2","L2 Hostility"],["g3","Goety"],["g4","Linggango Tweaks — hidden rules"],["g5","Tech & Magic"],["g6","Keeper unlocks"],["g7","L2 trait hunting"],["g8","Boss route"]];
 const traits=[...new Set(L2D.flatMap(x=>x.tr))].sort();
 const trRows=traits.map(t=>`<tr><td><b>${t.replace(/_/g," ")}</b></td><td>${LURE[t]?esc(LURE[t]):"<span class='note'>no lure</span>"}</td><td>${L2D.filter(x=>x.tr.includes(t)).map(x=>{const u=usedBy(x.item);return `${x.n}× ${esc(nmI(x.item))} <span class="tg">${CHN[x.charm]} · ${Math.round(x.ch*100)}%${x.rb?` +${Math.round(x.rb*100)}%/level`:""}</span>${x.ml.length?" <span class='tg'>mob level ≥100</span>":""}${u.length?`<br><span class="note">used by: ${u.slice(0,6).map(d=>`<a href="#i${d.ix}">${esc(TD(d.n))}</a>`).join(", ")}${u.length>6?` +${u.length-6}`:""}</span>`:""}`}).join("<br>")}</td></tr>`).join("");
 let last=null,bossRows="";
 for(const [n,a,c,note,lo] of BOSSR){if(a!==last){bossRows+=`<tr class="ab"><td colspan="3">${actL(a)}</td></tr>`;last=a}
  const L=lo.slice(0,6).map(id=>{const u=usedBy(id);return esc(nmI(id))+(u.length?` <span class="note">→ ${u.slice(0,3).map(d=>`<a href="#i${d.ix}">${esc(TD(d.n))}</a>`).join(", ")}${u.length>3?` +${u.length-3}`:""}</span>`:"")}).join("<br>");
  bossRows+=`<tr><td><b>${esc(n)}</b>${note?`<br><span class="note">${esc(note)}</span>`:""}</td><td class="num">${c}</td><td>${L||'<span class="note">—</span>'}</td></tr>`}
 el("main").innerHTML=`${crumb("Guide")}<h1>Mid &amp; end game guide</h1>
<p class="lede">Ties curios to the Act progression, L2 Hostility, Goety, Linggango Tweaks and the Tech/Magic mods. Each entry carries a confidence label.</p>
<div class="legend">${cf("ok")}${cf("code")}${cf("q")}</div>
<div class="toc"><b>CONTENTS</b><ol>${SEC.map(([id,t])=>`<li><a href="#guide" data-go="${id}">${t}</a></li>`).join("")}</ol></div>
${sec("g1","1. Act axis",`<p class="note">The Keeper defeated at the end of Act N opens the gate for Act N+1. Since 6.6.6 every questline is open from the start, so the quest book no longer hides any Act.</p>${tbl(["Act","Keeper","Weakness","Opens gate","Looting Charm","Curios / notes","Confidence"],ACTS.map(a=>`<tr><td class="num"><b>${a[0]}</b></td><td>${a[1]}</td><td>${a[2]}</td><td>${a[3]}</td><td>${a[4]}</td><td>${a[5]}</td><td>${CF[a[6]][0]}</td></tr>`).join(""))}`)}
${sec("g2","2. L2 Hostility — Looting Charms",`<p class="lede"><span class="badge new">IMPORTANT</span>A charm must be <b>worn in a curio slot</b> for its drops to appear (disableHostilityLootCurioRequirement = false). Trait-added drops are still cut by Lean Drops. Chance = chance + trait level × rankBonus, and each item in a stack rolls separately.</p>${tbl(["Charm","Unlocked","Drops","Worth farming"],L2.map(r=>`<tr><td><b>${r[0]}</b></td><td>${r[1]}</td><td class="num">${r[2]}</td><td>${r[3]}</td></tr>`).join(""))}<p class="note">The original L2 Complements methods still work: Hard Ice = kill Drowned with Powder Snow; Force Field = finish the Wither with an arrow. These materials feed the Study Lectern (parry/dodge milestones are cumulative and never consumed).</p>`)}
${sec("g3","3. Goety",tbl(["Item","Recipe / source","Notes"],`<tr><td><b>Scroll of Blessing</b></td><td>Darkest Scroll + Heart of the Earth + nautilus shell + sunflower + feather + ink sac + gold</td><td>+1 Luck stat; each Luck point gives +2% damage, +2.5% attack speed, +2% dodge (dodge capped at 15%). This dodge does not trigger Brutality anklets.</td></tr>
<tr><td><b>Potion of Transformation</b></td><td>Ritual sacrificing a villager; Unholy Blood, totem, end crystal, enchanted golden apple, echo shard</td><td>Used for Dimensional Will.</td></tr>
<tr><td><b>Luck brew</b></td><td>Goety brewing</td><td>Raises the Luck <i>effect level</i> (doesn't stack), unlike the Luck <i>stat</i> (stacks).</td></tr>`))}
${sec("g4","4. Linggango Tweaks — hidden rules",tbl(["Rule","Details"],`<tr><td>Damage taken floor</td><td>13% of every hit from an attacker always gets through, whatever your armor, resistance and curios add up to (no ceiling). Falls, drowning and starving are untouched. A dodge, parry or anything that cancels the hit outright still cancels all of it.</td></tr>
<tr><td>Per-hit cap</td><td>After armor, one hit from an attacker takes at most 50% of your max health, so nothing one-shots you from full health. Ring of Life (80%) adds almost nothing on top.</td></tr>
<tr><td>Boss intake</td><td>Every Nightmare Altar boss (and its second phase) loses at most 1/30 of its max health per second, so a fight lasts at least 30 s. It can bank 3 s of that budget, so one hit never takes more than 10%. Healing refunds the budget. Once you have beaten that boss your hits ignore the ceiling; bosses summoned at the Nightmare Altar always keep it. Since 6.6.6 Sanghor, Zoranth Newborn and Nyxaris get a longer shortest fight: 40, 45 and 50 s.</td></tr>
<tr><td>Boss health reset</td><td>If every player who hurt the Wither, Ender Dragon, Warden or an Elder Guardian dies in that dimension, it gets 50% of its health back.</td></tr>
<tr><td>Hardmode</td><td>Killing the Ender Dragon turns on Armageddon's Hardmode: ×2.1 mob health and ×2.1 damage (the mod's defaults are ×2.5 and ×2.0). Hardmode scales other mobs; the Armageddon bosses, Wither and Ender Dragon (forge:armageddon_bosses tag) and the Warden (blacklist) are exempt. Since 6.6.6 the world also pushes back: every player who has killed the Dragon carries 30 extra Hostility levels on top of the Keeper Ladder (about a third more mob health and damage).</td></tr>
<tr><td>Mob stages</td><td>Tougher mobs don't spawn naturally near you until you beat Arion (stage "mid") and the Ender Dragon (stage "hard"). Spawners, structures and summons are never held back.</td></tr>
<tr><td>Keeper Ladder</td><td>Each Keeper you beat adds L2 Hostility levels to every mob around you: 200 × (rung/10)³ over 10 rungs (Iron, Gold, Emerald, Diamond, Netherite, Elvenite, Voiderite, Blood, Sun, Shadow). Rung 1 adds 0, rung 5 adds 25, rung 8 adds 102, rung 10 adds 200; each level is +1% mob health and damage. The Cataclysm Keeper (The Discord) is not a rung, so Sanghor jumps you from rung 7 (69) to rung 8 (102).</td></tr>
<tr><td>Damage types</td><td>Weapons and spells deal a type (slash, pierce, blunt, fire, frost, lightning, holy, dark, blood, nature, arcane). Against a weakness ×1.25 (×1.5 when the type is boosted: rain for lightning, daylight for holy, airborne targets for pierce…); against a resistance ×0.75 (×0.5 boosted). Hits also fill a status meter per type (Hemorrhage, Frostbite, Rend…); bosses fill it at half speed.</td></tr>
<tr><td>Perfect Hit</td><td>A jump crit has a 5% chance to become a Perfect Hit: ×1.5 on top of the crit and ×4 knockback.</td></tr>
<tr><td>Invasions</td><td>Terraria-style invasions unlock as you beat bosses; each nightfall there is an 8% chance of a random one, at most once every 3 days. Unlocks in 6.6.6: Goblin Army after the Goblin Lord; Illager Crusade (finale: the Vizier) after Arion; Night of Chaos (finale: Lord Pumpkinhead), Krampus Night and Black Sabbath (finale: an Apostle) after the Ender Dragon; Erasure storms in the End after the Dragon; Blood Moon after Sanghor.</td></tr>
<tr><td>Accessory limits (6.6.6)</td><td>All accessory damage multipliers together may grow a hit up to ×3 as is; past that the extra only grows by its square root (×10 lands as ×5.5). Summons are exempt. Lifesteal of every kind heals at most 10% of your max health per tick. Accessories that set a hit to exactly zero still let the damage-floor share through; parries, dodges and totems still cancel.</td></tr>
<tr><td>Terramity stacking</td><td>Terramity curios are sorted into Power, Edge and Guard sets; only the best one you wear from a set works in full, the second keeps 50% and the third 25% (costs included), the rest switch off.</td></tr>
<tr><td>Optional difficulty modifiers</td><td>Difficulty Enhancement lets you switch on extra modifiers; none are on by default, and this wiki's drop and chest chances assume none. The ones that touch loot: <b>Lean Drops</b> (Medium) mobs drop 25% less; <b>No Cheese</b> (Expert) mobs killed without a real player (farms, traps, kill machines) drop no loot or XP, though Drygmy and Hostile Neural Networks still work; <b>Horrible Scavenger</b> (Master) every chest stack ×0.2, randomly rounded, so a single curio survives 20% of the time; progression items in the loot_protected tag are spared.</td></tr>
`)+`<h3 style="margin-top:var(--s4)">Weapon damage floor calculator</h3><div class="craft" style="gap:var(--s3)">
<label>Base damage <input id="gb" type="number" value="10" style="width:70px"></label><label>Somber Stones <input id="gs" type="number" value="0" min="0" max="20" style="width:60px"></label>
<label>Attack speed <input id="gp" type="number" step="0.1" value="1.6" style="width:60px"></label><label>Tier <select id="gt" style="width:auto">${Object.keys(TF).map(k=>`<option>${k}</option>`).join("")}</select></label>
<div id="go" class="st"></div></div><p class="note">Formula: effective floor = min(floor, (floor+1) × 1.8 / speed − 1). Somber Stones (+0.5 each, max +10) are added before comparing to the floor. Exceptions: Royal Guardian Sword 70, Amaterasu/Tsukuyomi 17.</p>`)}
${sec("g5","5. Tech &amp; Magic for curios",tbl(["Mod","What to know","Confidence"],[["Hostile Neural Networks","Legit drop farming that still works with the No Cheese and Lean Drops modifiers on."],["Kill machines (FakePlayer)","No real player kill: Terra Curio and L2 trait drops never fall, and with the No Cheese modifier on nothing drops."],["Mekanism / AE2","Powah is gone in 6.6.6: Mekanism Energy Cubes, the Quantum Entangloporter and the Chargepad do its job. AE2 wireless terminals fit the universal Curio slot (it also takes items from other slots)."],["AE2 Certus Quartz Pickaxe","Not gated, mining power 2."],["Blood Magic","Socketed Upgrade Tome +1 Living Armour Socket each, up to 5; holds sigils, Tartaric Gems, Training Bracelet."],["Ars Additions","+3 Charm (Charm base 6 = 3 + 3)."],["Enigmatic Legacy","The Curses branch unlocks many Curses-only items (Astral Fruit +1 Ring, Ichor Bottle +1 Charm, Enchanter's Pearl…). Amulet of Ascension = Enigmatic Amulet + Heart of the Cosmos."],["Enigmatic Dice","Ring of Agility: dodge = 1 − 0.99^(speed × 100), up to 30%."]].map(([a,b])=>`<tr><td>${a}</td><td>${b}</td><td>${ui("spy")}</td></tr>`).join("")))}
${sec("g6","6. Keeper unlocks (pack config)",`<p class="lede">Per <code>[progression_gates]</code> in <code>linggango_tweaks-common.toml</code>: items in the <code>linggango_tweaks:gated/&lt;tier&gt;</code> tag can't be taken out of a crafting station, placed, used or worn until you have the Keeper's advancement. ${D.filter(d=>d.gk).length} curios in this wiki are gated this way (${ui("lock")} badge). Since 6.6.6 these lists are much shorter: farms, storage and the first step of most tech and magic mods are open from the start, while gear, magic and endgame machines still need their Keeper. The Classic Locks option on the difficulty screen brings back the old, stricter list (<code>gated_classic</code>). No quest chapter is locked any more.</p>${tbl(["Opens at","Defeat Keeper","Mods with the most locked items","Gated curios"],CHAP.map(([a,t])=>`<tr><td class="num"><b>${actL(a)}</b></td><td>${GK[a]}</td><td>${esc(t)}</td><td class="num">${D.filter(d=>d.gk===a).length}</td></tr>`).join(""))}`)}
${sec("g7","7. L2 trait hunting (Linggango Tweaks)",`<p class="lede">Mobs with L2 traits drop <b>Hostile Remnants</b> (1 per 2 trait levels, rounded up). 9 Remnants = 1 <b>Hostile Core</b>. Core + the ingredient below = 2 <b>Trait Lures</b>; each Lure summons 3 mobs with that trait. Burning a Core (L2 Complements, 1/3 chance) gives Hostility Essence, needed for high-tier lures. Burning an L2 trait item gives 2 Cores.</p><p class="note">Mastery: each kill gives every trait points equal to its level; 30 / 120 / 400 points grant −5/10/15% damage taken from and +5/10/15% damage to mobs with that trait. Trait drops only appear when a player kills the mob while wearing a Looting Charm of the right tier in a curio slot: Unpolished (Act III), Magical (Act V), Chaotic (Ender Dragon Act), Miraculous (Act XI). Chance = chance + trait level × rankBonus.</p>${tbl(["Trait","Lure (Core + …)","Drops (charm needed · chance) and curios that use them"],trRows)}`)}
${sec("g8","8. Boss route and loot use",`<p class="lede">Suggested order slotting side bosses between the Keepers. ${ui("check")} = pack stats (<code>entitybalance.json</code>) compared to the Keepers; ${ui("spy")} = inferred from dimension or config; ${ui("q")} = estimated from the mod's base difficulty, untested in the pack. The last column lists the boss's own drops and the curios that use them.</p>${tbl(["Boss","Confidence","Loot worth keeping → curios"],bossRows)}
<h3 style="margin-top:var(--s4)">Using loot (Linggango Tweaks config rules)</h3><ul class="note" style="font-size:13px;line-height:1.6">
<li><b>First fight is capped:</b> a boss loses at most 1/30 of its health per second and 10% per hit (so the fight lasts at least 30 s) until you beat it once. After that your hits ignore the cap, so re-farming is fast.</li>
<li><b>Nightmare Altar:</b> re-summons a defeated boss. Each L2 trait item placed on the altar (up to 8) adds 25 Hostility levels and one more full loot roll. Altar bosses always keep the damage cap, so this is how to multiply rare drops up to ×9, like Dragon Band, Angel Feather, Gob's Gilded Hat.</li>
<li><b>Group fights:</b> every player within 64 blocks when the boss dies gets the kill, Keeper milestones included.</li>
<li><b>Multi-phase bosses:</b> Arion, Bringer of Doom, Sanghor, Morphegor and Draugr have a second phase; beating phase two counts as the kill.</li>
<li><b>Kill by hand:</b> Terra Curio drops and L2 trait drops only fall when a real player lands the kill. Kill machines (FakePlayer) lose them.</li>
<li><b>Suggested farm order:</b> get the Unpolished Charm in Act III and hunt Gravity/Moonwalk traits for dragon's breath; after Zoranth fight Super Sniffer and the Shadow Wizards (Antiprism opens Brutality's Unbridled Rage branch); after the Elvenite Paladin fight Gob and the Trial Guardian (the Smithing Template opens Brutality's math group); leave Virtue and Ultra Sniffer until after The Calamities.</li></ul>`)}`;
 ["gb","gs","gp","gt"].forEach(i=>el(i).addEventListener("input",gcalc));gcalc();
}

function outside(){
 document.title="Unobtainable · Linggango Wiki";
 el("main").innerHTML=`${crumb("Unobtainable")}<h1>Off the act</h1><p class="lede">${U.length} curios that exist in the pack or the added mods but can't be obtained through normal play.</p><div class="tw"><table><thead><tr><th></th><th>Curio</th><th>Mod</th><th>Reason</th></tr></thead><tbody>${U.map(u=>`<tr><td>${img(u.id)}</td><td>${esc(TD(u.n))}<br><span class="meta">${esc(u.id)}</span></td><td>${esc(u.m)}</td><td>${esc(u.why)}</td></tr>`).join("")}</tbody></table></div>`}

/* ---------- router ---------- */
const tierIO=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add("seen");tierIO.unobserve(e.target)}}),{rootMargin:"200px"});
// tile icons only animate while on screen: hundreds of off-screen bobbing icons cost a frame each
const tileIO=new IntersectionObserver(es=>es.forEach(e=>e.target.classList.toggle("vis",e.isIntersecting)),{rootMargin:"120px"});
const watchTiles=r=>r.querySelectorAll&&r.querySelectorAll("a.t:not([data-vo])").forEach(t=>{t.dataset.vo=1;tileIO.observe(t)});
new MutationObserver(ms=>ms.forEach(m=>m.addedNodes.forEach(n=>{if(n.nodeType!==1)return;if(n.matches("input[type=range]"))setRv(n);else n.querySelectorAll&&n.querySelectorAll("input[type=range]").forEach(setRv);if(n.matches("a.t:not([data-vo])")){n.dataset.vo=1;tileIO.observe(n)}else watchTiles(n)}))).observe(document.documentElement,{childList:true,subtree:true});
/* range sliders: --rv (0–100) drives the cyan fill drawn on the track */
const setRv=i=>i.style.setProperty("--rv",((+i.value-(+i.min||0))/((+i.max||100)-(+i.min||0))*100)||0);
document.addEventListener("input",e=>{if(e.target.type==="range")setRv(e.target)},true);
function decorate(r=document){
 (r.querySelectorAll?r:document).querySelectorAll('input[type=range]').forEach(setRv);
 watchTiles(r);
 r.querySelectorAll(".tier:not(.seen):not([data-io])").forEach(t=>{t.dataset.io=1;tierIO.observe(t)});
 const hero=r.querySelector(".hero:not([data-done])");
 if(hero){hero.dataset.done=1;if(UI.bg){hero.classList.add("real");hero.style.setProperty("--hbg",`url(data:image/jpeg;base64,${UI.bg})`)}const w=hero.querySelector("img.wm");if(w&&UI.logo)w.src="data:image/png;base64,"+UI.logo}
 r.querySelectorAll("[data-an]:not([data-done])").forEach(el=>{el.dataset.done=1;const a=AN[el.dataset.an];if(!a)return;el.style.setProperty("--n",a[1]);el.style.setProperty("--ms",(a[1]*a[2])+"ms");el.insertAdjacentHTML("beforeend",`<img class="strip" alt="" src="data:image/png;base64,${a[0]}">`);el.classList.add("anim")});
}
function renderBase(){
 save();const xs=refreshSide();const h=decodeURIComponent(location.hash);
 if(["#bang","#ngoai","#table","#unobtainable","#guide"].includes(h)){location.replace("#home");return}
 // the mod and slot pages are gone: their links open Curios filtered to that mod or slot (the Act pages remain: hubList("act"))
 {const mm=h.match(/^#(mod|slot)\/(.+)$/);if(h==="#mods"||h==="#slot/*"){location.replace("#home");return}
  if(mm){const v=mm[2];st.q=mm[1]==="mod"?`mod:${/\s/.test(v)?`"${v}"`:v}`:slotQ(v);el("q").value=st.q;location.replace("#home");return}}
 document.body.classList.toggle("hub",h===""||h==="#");
 // curio filters and index only make sense next to curio lists
 // progression pages wear the quest-book look (FTB Quests theme of the pack); item pages keep the inventory look
 // the quest-book background (Linggango FTB Quests Theme) behind every progression page
 document.body.classList.toggle("qbg",h==="#home"||/^#(act|boss|side)\//.test(h)||h==="#bosses");
 document.body.classList.toggle("qbook",h==="#bosses"||h.startsWith("#boss/")||h.startsWith("#side/"));
 document.body.classList.toggle("noside",/^#i\d/.test(h)||h.startsWith("#side/")||h==="#bosses"||h.startsWith("#boss/")||h==="#mechanics"||h.startsWith("#mechanics/")||h==="#changes"||h.startsWith("#build"));
 if(innerWidth<=760&&(h.startsWith("#i")||h==="#guide")){el("side").classList.add("closed");el("fold").setAttribute("aria-expanded","false")}
 const soft=SOFT;SOFT=false;const mn=el("main");if(!soft){mn.classList.remove("enter");void mn.offsetWidth;mn.classList.add("enter")}
 const m=h.match(/^#(slot|act|mod)\/(.+)$/);
 if(h===""||h==="#")hubHome();
 else if(h.startsWith("#build"))buildPage(h);
 else if(h==="#bosses")bossList();
 else if(h.startsWith("#boss/"))bossPage(h.slice(6));
 else if(h==="#mechanics"||h.startsWith("#mechanics/"))mechPage();
 else if(h==="#changes")changesPage();
 else if(h.startsWith("#side/"))sidePage(h.slice(6));
 else if(m)hubList(m[1],m[2]);
 else if(h==="#mods")hubList("mods");
 else if(/^#i\d+$/.test(h)&&D[+h.slice(2)]){page(D[+h.slice(2)]);recipeTree(D[+h.slice(2)])}
 else{document.title="Curios · Linggango Wiki";home(xs,false);
  // any other hash (an old bookmark, a curio id that no longer exists) draws Curios under a one-line notice
  if(!/^#(home)?$/.test(h)){const mn2=el("main"),p=document.createElement("p");p.className="note nf";p.textContent=`No page called “${h.slice(1)}”. Here is the Curios list.`;const c=mn2.querySelector(".crumb");c?c.after(p):mn2.prepend(p)}}
 if(!soft&&!h.startsWith("#home")&&!h.startsWith("#build")&&h!=="#table")scrollTo(0,0);
}
/* extension points: a feature file (gear.js) registers handlers here instead of reassigning these functions, so script load order stops mattering.
   route(h) runs first on every render, and a handler that returns true has drawn the page; tip(n) likewise for tooltips;
   (gear.js once also hooked the hub pages; the mod and slot pages are gone and the Act pages are drawn by hubList, so those hooks were dead and were removed.) */
const EXT={route:[],tip:[]};
function render(){if(!EXT.route.some(f=>f(decodeURIComponent(location.hash))))renderBase()}
function showTip(n){if(!EXT.tip.some(f=>f(n)))showTipBase(n)}
/* the site fetches the detail pages' pictures (wiki_pics.js: armour stands, guide pages, ritual layouts) once the first page
   is drawn; a page drawn before they came is drawn again when they arrive. The offline file has them inline (PICS=1). */
function loadPics(){const u=document.documentElement.dataset.pics;if(!u||window.PICS)return;const s=document.createElement("script");s.src=u;document.head.appendChild(s)}
function picsLoaded(){if(!window.PICS_MISS)return;window.PICS_MISS=0;const y=scrollY;render();decorate();scrollTo(0,y)}
const needPics=()=>{if(!window.PICS)window.PICS_MISS=1};
document.addEventListener("DOMContentLoaded",()=>{const go=()=>{langBoot();render();decorate();loadPics()};I18N_READY?I18N_READY.then(go):go()});
function refresh(){const h=decodeURIComponent(location.hash);if(h==="#home"||/^#(slot|act|mod)\//.test(h)){SOFT=true;render()}else location.hash="#home"}
/* page change: a cross-fade between sections (View Transitions, where the browser has them); switches inside one page
   (an Equipment Act, a Path filter) redraw in place so the controls you just pressed do not blink */
const pageOf=h=>(decodeURIComponent(h).match(/^#(gear|gs|g|build|bosses|boss|side|mechanics|home|act|slot|mod|i)/)||[,"hub"])[1];
let lastHash=location.hash;
/* the icon you click flies into the item page's big art (and back to its tile when you go back); Previous/Next slide sideways */
const ART="#main .ip-icon .aimg img,#main .gbig img",DETAIL=/^#(i|gs|g)\d+$/;
let navA=null;document.addEventListener("click",e=>{navA=e.target.closest("a[href^='#']")},true);
const onScreen=n=>{if(!n)return null;const r=n.getBoundingClientRect();return r.width&&r.bottom>0&&r.top<innerHeight?n:null};
addEventListener("hashchange",()=>{const from=lastHash,to=location.hash,a=pageOf(from),b=pageOf(to);lastHash=to;
 const go=()=>{hideTip();render();decorate()};
 if(RM||!document.startViewTransition||(a===b&&!/^(i|g|gs|boss|side)$/.test(a))){go();return}
 const pn=[...document.querySelectorAll(".pnx a")].find(x=>x.getAttribute("href")===to),R=document.documentElement;
 let src=null,dst=null;
 if(pn)R.dataset.vt=/Previous/.test(pn.textContent)?"prev":"next";
 else if(DETAIL.test(to)&&navA&&navA.getAttribute("href")===to)src=onScreen(navA.querySelector("img"));
 else if(DETAIL.test(from))src=onScreen(document.querySelector(ART));
 if(src)src.style.viewTransitionName="art";
 const t=document.startViewTransition(()=>{if(src)src.style.viewTransitionName="";go();
  if(src){dst=onScreen(DETAIL.test(to)?document.querySelector(ART):document.querySelector(`#main a[href="${CSS.escape(from)}"] img`));if(dst)dst.style.viewTransitionName="art"}});
 t.ready.catch(()=>{});t.finished.catch(()=>{}).finally(()=>{if(dst)dst.style.viewTransitionName="";delete R.dataset.vt});navA=null});

/* ---------- tooltip ---------- */
const tip=document.createElement("div");tip.id="tip";tip.setAttribute("role","tooltip");document.body.appendChild(tip);
let tipFor=null;const TIPC=new Map();
const TOP={COMMON:["#969696","#575757","#3C3C3C"],UNCOMMON:["#9CA028","#6A6D18","#4B4D0E"],RARE:["#335FA0","#193A6D","#0A1D38"],EPIC:["#A02283","#691356","#3C0730"],LEGENDARY:["#A0803C","#815F19","#372808"],CHAOS:["#9F373A","#81191B","#370809"],CUSTOM:["#E8B84A","#B5832A","#6B4A12"]};
const VRAR={Common:"COMMON",Uncommon:"UNCOMMON",Rare:"RARE",Epic:"EPIC"};
const pal=d=>isMust(d)?["#FFE14D","#FFB300","#5A3A00"]:d.ig?(TOP[VRAR[d.ig[0]]]||TOP.CUSTOM):TOP.COMMON;
const igName=d=>d.ig?`<span class="ign" style="${d.ig[1]==="rainbow"?"":"color:"+d.ig[1]}"${d.ig[1]==="rainbow"?' data-rb="1"':""}>${esc(d.ig[0])}</span>`:`<span class="ign">${T("Unverified")}</span>`;
/* the enchantment glint over Mythic and Must-Have items, cut to the item's shape (mask = its icon) */
const glint=d=>d.r>=5&&IC[d.id]?`<span class="glint" style="--gm:url(${icu(d.id)})" aria-hidden="true"></span>`:"";
const slotImg=(d,cls="")=>IC[d.id]?`<span class="aimg ${cls}"${AN[d.id]?` data-an="${esc(d.id)}"`:""}><img alt="" src="${icu(d.id)}"></span>`:`<span class="ph">${esc(d.n.slice(0,2))}</span>`;
/* tooltip recipe: mini crafting grid instead of the "Craft at ... from ..." line */
const RCV=/^(Craft|Combine|Infuse|Perform|Upgrade|Imbue|Forge)\b/;
const rcName=c=>c[0]?TD(BYID[c[0]]?BYID[c[0]].n:NM[c[0]]||c[0]):T("Any {kind}",{kind:(c[1].split(":")[1]||c[1]).replace(/_/g," ")});
const tipRecipe=d=>{const g=d.gr,shaped=g.l===0&&!/shapeless/i.test(g.st),cs=shaped?g.c:g.c.filter(Boolean);
 return `<div class="trcp"><div class="trg" style="grid-template-columns:repeat(${shaped?g.w:Math.min(cs.length,5)},18px)">${cs.map(c=>`<i class="trc"${c?` title="${esc(rcName(c))}"`:""}>${c?(c[0]?img(c[0]):"<b>#</b>"):""}</i>`).join("")}</div><i class="tra" aria-hidden="true">→</i><i class="trc out">${img(d.id)}${g.n>1?`<b>${g.n}</b>`:""}</i><span class="trs">${esc(g.st.replace(/\s*\(shapeless\)/i,""))}</span></div>`};
function showTipBase(n){const d=/^\d+$/.test(n.dataset.t)&&D[+n.dataset.t];if(!d){hideTip();return}tipFor=n;const F=mf(d.m),P=pal(d),nc=d.ig&&d.ig[1]!=="rainbow"?d.ig[1]:"#FFFFFF";
 tip.className="to r"+d.r+(tip.classList.contains("on")?" on":"");tip.dataset.mf=F[0];
 tip.style.setProperty("--c1",P[0]);tip.style.setProperty("--c2",P[1]);tip.style.setProperty("--c3",P[2]);
 const stats=d.st.map((x,j)=>[d.tg[j],x]).filter(([t,x])=>t!=="relic"&&x.length<110&&!/^(When worn|Passive Effect|Hold Shift)/i.test(x)).slice(0,5);
 let c=TIPC.get(d.ix);if(!c){const w=document.createElement("div");w.innerHTML=`<div class="tbox"><div class="tfr"></div>
 <div class="thd"><span class="tslot">${slotImg(d)}</span><div class="tht"><div class="tnm" style="color:${nc}"${d.ig&&d.ig[1]==="rainbow"?' data-rb="1"':""}>${isMust(d)?ui("star"):""}${esc(TD(d.n))}</div>${enTip(d.n)}<div class="tsub">${esc(d.sl.map(x=>T(x)).join(", "))} · ${d.g==="Loot"?T("Loot"):T("Craft")}</div></div></div>
 <div class="tbd"><p class="tfx">${fmt(fxT(d))}</p>${RL[d.id]?rlTip(d):""}${evo().from[d.id]?`<p class="tevo">${T("⟲ Evolves from {name}",{name:esc(TD(BYID[evo().from[d.id]].n))})}</p>`:""}${(evo().to[d.id]||[]).map(t=>`<p class="tevo">${T("⟳ Evolves into {name}",{name:esc(TD(BYID[t].n))})}</p>`).join("")}${SK.i[d.id]?`<p class="tsk">${skTag(d.id)}</p>`:""}${stats.length?`<ul class="tst">${stats.map(([t,x])=>`<li>${fmt(stT(x))}</li>`).join("")}</ul>`:""}${d.gk?`<p class="tlock">${ui("lock")} ${T("Locked until {boss} falls",{boss:TD(GK[d.gk])})}</p>`:""}${d.rq?`<p class="tlock trq">${ui("lock")} ${img(RQRING[d.rq])} ${T("Requires the {ring}",{ring:rqName(d)})}</p>`:""}${isMust(d)?`<p class="tmust">${ui("star")} ${T("Must-Have: get it as soon as {act} opens.",{act:esc(actL(d.t))})}</p>`:""}
 ${d.gr?tipRecipe(d):""}${(x=>x.length?`<p class="tsrc">${fmt(x.map(srcT).join(" "))}</p>`:"")((d.gr?d.src.filter(x=>!RCV.test(x)):d.src).slice(0,2))}<p class="twhere">${esc(actL(d.t))}${d.a!==d.t?" · "+T("with luck from {act}",{act:esc(actL(d.a))}):""}</p></div>
 <div class="tft"><span class="tmod">${esc(d.m)}</span><span class="trt">${RN[d.r]}${d.pe?' <i class="kest" title="'+T("Power tier read from its text")+'">'+T("estimate")+'</i>':""}</span></div></div>`;c=w.firstElementChild;TIPC.set(d.ix,c)}tip.replaceChildren(c);
 if(lastAct)lastAct.classList.remove("act");lastAct=n.classList.contains("t")?n:null;if(lastAct)lastAct.classList.add("act");
 const first=!tip.classList.contains("on");place(n);tip.classList.add("on");if(first)tip.classList.add("in");decorate(tip)}
function place(n){const r=n.getBoundingClientRect(),w=tip.offsetWidth,h=tip.offsetHeight,vw=innerWidth,vh=innerHeight;
 let x=r.right+10,y=r.top;if(x+w>vw-8)x=r.left-w-10;if(x<8)x=Math.min(vw-w-8,Math.max(8,r.left));
 if(x<r.right&&x+w>r.left){y=r.bottom+8;if(y+h>vh-8)y=r.top-h-8}
 y=Math.max(8,Math.min(y,vh-h-8));tip.classList.toggle("glide",tip.classList.contains("on"));tip.style.setProperty("--tx",x+"px");tip.style.setProperty("--ty",y+"px");tip.dataset.side=x<r.left?"l":"r"}
let lastAct=null;
function hideTip(){tipFor=null;tip.classList.remove("on","glide","in");if(lastAct){lastAct.classList.remove("act");lastAct=null}}
/* at most one tooltip update per frame, always for the tile under the pointer now */
let hovT=null,hovQ=0;
document.addEventListener("mouseover",e=>{hovT=e.target.closest("[data-t]");if(!hovQ)hovQ=requestAnimationFrame(()=>{hovQ=0;if(hovT&&hovT!==tipFor)showTip(hovT);else if(!hovT&&tipFor)hideTip()})},{passive:true});
document.addEventListener("focusin",e=>{const n=e.target.closest("[data-t]");n?showTip(n):hideTip()});
addEventListener("scroll",hideTip,{capture:true,passive:true});

/* ---------- global events ---------- */
document.addEventListener("click",e=>{
 const p=e.target.closest(".pill");if(p){const k=p.dataset.k,v=p.dataset.v;
  if(k==="qt"){st.q=qDrop(v);el("q").value=st.q}else if(Array.isArray(st[k]))st[k]=st[k].filter(x=>String(x)!==v);else if(k==="nw")st.nw=false;else{st[k]="";el(k==="q"?"q":"f"+k).value=""}refresh();return}
 if(e.target.id==="clr2"){resetFilters();return}
 const go=e.target.closest("[data-go]");if(go){e.preventDefault();el(go.dataset.go).scrollIntoView({behavior:RM?"auto":"smooth",block:"start"});return}
 if(e.target.closest("[data-top]")){e.preventDefault();scrollTo({top:0,behavior:RM?"auto":"smooth"});return}
 const tl=e.target.closest(".tl[data-tier]");if(tl){const a=+tl.dataset.tier,open=!tierOpen(a);
  if(fOn()){const i=st.cl.indexOf(a);open?st.cl.splice(i,1):st.cl.push(a)}else{const o=st.op||[hereOn()??ORDER[0]];st.op=open?[...o,a]:o.filter(x=>x!==a)}save();
  const s=tl.parentNode,t=s.querySelector(".tiles");if(open&&!t.childElementCount){t.innerHTML=tierTiles(pathXs.filter(d=>d.t===a));decorate(s)}
  s.classList.toggle("closed",!open);tl.setAttribute("aria-expanded",open)}
});
document.addEventListener("keydown",e=>{if(location.hash.startsWith("#i")&&!/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)&&(e.key==="ArrowLeft"||e.key==="ArrowRight")){const a=[...document.querySelectorAll(".pnx a")].find(x=>x.textContent.includes(e.key==="ArrowLeft"?"Previous":"Next"));if(a){location.hash=a.getAttribute("href")}}if(e.key==="Escape")hideTip();if(e.key==="/"&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&!e.isComposing&&!/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)&&!document.activeElement.isContentEditable){e.preventDefault();el("q").focus()}});
{const b=document.createElement("button");b.id="totop";b.setAttribute("aria-label",T("Back to top"));b.textContent="↑";b.onclick=()=>scrollTo({top:0,behavior:RM?"auto":"smooth"});document.body.appendChild(b);
 addEventListener("scroll",()=>b.classList.toggle("on",scrollY>600),{passive:true})}
{const s=document.createElement("style");s.textContent=Object.entries(ROLE_C).map(([k,v])=>`.t.c${k}{--cat:${v}}`).join("");document.head.appendChild(s)}
/* recipe: hovering a slot or an ingredient line lights up every cell of that ingredient */
document.addEventListener("mouseover",e=>{const k=e.target.closest(".mcwin [data-k]");document.querySelectorAll(".mcwin .on").forEach(x=>x.classList.remove("on"));if(!k)return;
 k.closest(".mcwin").querySelectorAll(`[data-k="${CSS.escape(k.dataset.k)}"]`).forEach(x=>x.classList.add("on"))},{passive:true});