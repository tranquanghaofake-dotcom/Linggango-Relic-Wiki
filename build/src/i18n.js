/* Languages (docs/plans/2026-11-08-multilingual.md). English is the source and stays in the HTML and the JS; a language pack only overrides it,
   so a missing pack or key shows English and an English reader pays for nothing. Packs are build/i18n/ui.json split per language by build.py:
   I18N.<code> = {key: text}; the site fetches one on demand (<html data-lang-<code>=url>), the offline file has all of them inline.
     t("key","English",{n:3})                      one string; {n} is filled from the third argument
     tn("key",n,{one:"{n} item",other:"{n} items"})  a counted string: the pack holds the same object with the language's CLDR forms
     data-lg="key" (text)  data-lgh="key" (html)  data-lga="attr=key;attr=key"   static text in template.html
   Keys are written out in full (build.py reads them to check the table), never built from parts. */
const LANGS=[["en","English"],["vi","Tiếng Việt"],["ru","Русский"],["pt","Português"],["es","Español"]];
const LANG_CODES=LANGS.map(x=>x[0]);
let LANG="en",PRULES=null;
window.I18N=window.I18N||{};
const lsGet=k=>{try{return localStorage.getItem(k)}catch(e){return null}};
const lsSet=(k,v)=>{try{localStorage.setItem(k,v)}catch(e){}};
/* the reader's choice: ?lang=xx, else the one they picked last time, else English (no guessing from the browser while the
   translations are unreviewed: docs/plans/2026-11-08-multilingual.md, Phase 5) */
const wantLang=()=>{const q=new URLSearchParams(location.search).get("lang");if(LANG_CODES.includes(q))return q;const s=lsGet("lgw-lang");return LANG_CODES.includes(s)?s:"en"};
const fill=(s,p)=>p?s.replace(/\{(\w+)\}/g,(m,k)=>k in p?p[k]:m):s;
const pack=()=>LANG==="en"?null:I18N[LANG]||null;
const t=(k,en,p)=>{const P=pack();return fill(P&&P[k]||en,p)};
const nL=n=>LANG==="en"?n.toLocaleString():n.toLocaleString(LANG==="vi"?"en-US":LANG==="es"?"es-ES":LANG==="pt"?"pt-BR":"ru-RU");   // number with the language's grouping (vi keeps the dot decimal, so it groups with commas); English leaves the browser to decide, as before
const tn=(k,n,en,p)=>{const P=pack(),f=P&&P[k]||en;PRULES=PRULES||new Intl.PluralRules(LANG);return fill(f[PRULES.select(n)]||f.other,{n:nL(n),...p})};
/* Sentences written in the code (not in template.html): the English text is the key, so nothing is named by hand and the English stays readable where it is used.
     T("Opens when {boss} falls.",{boss:esc(name)})        one sentence; the caller escapes what it passes in
     TN(n,"{n} curio","{n} curios")                       a counted one: the pack holds the language's CLDR forms (one, few, many, other); {n} is n as written
   The pack's `tr` maps hsh(English) to the text (a string, or an object of plural forms); a sentence without one shows its English. build/i18n/tm/<lang>.json
   is where the translations live; build.py checks them (the same hash in Python), and build/i18n/trlog.js crawls the site to list every sentence a page asks for. */
const hsh=s=>{let a=0xdeadbeef,b=0x41c6ce57;for(let i=0;i<s.length;i++){const c=s.charCodeAt(i);a=Math.imul(a^c,2654435761);b=Math.imul(b^c,1597334677)}
 a=Math.imul(a^(a>>>16),2246822507)^Math.imul(b^(b>>>13),3266489909);b=Math.imul(b^(b>>>16),2246822507)^Math.imul(a^(a>>>13),3266489909);return(4294967296*(2097151&b)+(a>>>0)).toString(36)};
const trOf=en=>{const P=pack();if(window.__TRLOG)window.__TRLOG.add(en);return P&&P.tr&&P.tr[hsh(en)]};
const T=(en,p)=>fill(trOf(en)||en,p);
/* a string that comes from the data (an item name, an effect text): looked up in the pack's `tr` like a sentence, but not logged by trlog.js and not a placeholder template */
/* N("…") marks a sentence inside a constant table (a tooltip, a label): it returns the string unchanged so the build can find it; print it with T(x) */
const N=s=>s;
const TD=en=>{const P=pack();return P&&P.tr&&P.tr[hsh(en)]||en};
const TN=(n,one,other,p)=>{const f=trOf(one+"\u0001"+other);let s;if(f&&typeof f==="object"){PRULES=PRULES||new Intl.PluralRules(LANG);s=f[PRULES.select(n)]||f.other}else s=n===1?one:other;return fill(s,{n,...p})};
/* a pack arrives as a script (site) or is already there (offline file, or loaded before); either way the promise resolves, with English if it failed */
const langPack=c=>new Promise(ok=>{if(c==="en"||I18N[c])return ok();const u=document.documentElement.getAttribute("data-lang-"+c);if(!u)return ok();
 const s=document.createElement("script");s.src=u;s.onload=s.onerror=()=>ok();document.head.appendChild(s)});
/* static text: the first pass keeps each element's English (so English comes back), then every pass writes the pack's text or that English */
function shell(){const P=pack();
 for(const n of document.querySelectorAll("[data-lg],[data-lgh],[data-lga]")){
  if(!n._en){n._en={t:n.textContent,h:n.innerHTML,a:{}};for(const pr of(n.dataset.lga||"").split(";").filter(Boolean)){const a=pr.split("=")[0];n._en.a[a]=n.getAttribute(a)}}
  if(!P&&!n._on)continue;n._on=!!P;
  if(n.dataset.lg)n.textContent=P&&P[n.dataset.lg]||n._en.t;
  if(n.dataset.lgh)n.innerHTML=P&&P[n.dataset.lgh]||n._en.h;
  for(const pr of(n.dataset.lga||"").split(";").filter(Boolean)){const[a,k]=pr.split("=");n.setAttribute(a,P&&P[k]||n._en.a[a])}}}
/* the language is taken here once its pack is in; render() / decorate() (app.js) then redraw whatever JS wrote */
function useLang(c){LANG=c;PRULES=null;document.documentElement.lang=c;shell();if(typeof relabelSide==="function")relabelSide();
 const s=document.getElementById("lang");if(s)s.value=c}
function setLang(c){return langPack(c).then(()=>{if(c!=="en"&&!I18N[c])return;lsSet("lgw-lang",c);
 const u=new URL(location.href);if(c==="en")u.searchParams.delete("lang");else u.searchParams.set("lang",c);history.replaceState(null,"",u);
 useLang(c);render();decorate()})}
const I18N_READY=wantLang()==="en"?null:langPack(wantLang());
/* called once by app.js before the first render: the menu, then the chosen language if its pack arrived */
function langBoot(){const s=document.getElementById("lang");
 if(s&&!s.options.length){for(const[c,n]of LANGS){const o=document.createElement("option");o.value=c;o.textContent=c.toUpperCase()+"\u2003\u2003\u2003\u2003"+n;s.appendChild(o)}s.onchange=()=>setLang(s.value)}
 const w=wantLang();useLang(w==="en"||I18N[w]?w:"en")}
