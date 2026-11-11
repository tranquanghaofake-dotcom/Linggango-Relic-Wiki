// Languages (docs/plans/2026-11-08-multilingual.md). Runs in the page (check.js: `bad` in scope; the offline file has every pack inline).
// Every language draws the shell in its own words with nothing half-filled, English comes back untouched, a missing key shows English,
// and counted strings pick the language's CLDR plural form (Russian has four, Vietnamese one).
{ const en0 = [...document.querySelectorAll('[data-lg],[data-lgh]')].map(n => n.innerHTML).join('|'), at0 = [...document.querySelectorAll('[data-lga]')].map(n => n.outerHTML).join('|');
  for (const c of LANG_CODES.filter(x => x !== 'en')) {
    if (!I18N[c]) { bad.push('i18n: no pack for ' + c); continue; }
    useLang(c);
    const els = [...document.querySelectorAll('[data-lg],[data-lgh]')];
    for (const n of els) { const k = n.dataset.lg || n.dataset.lgh;
      if (!n.textContent.trim()) bad.push('i18n ' + c + ': empty ' + k);
      if (/\{\w+\}/.test(n.textContent)) bad.push('i18n ' + c + ': placeholder left in ' + k); }
    if (document.documentElement.lang !== c) bad.push('i18n: <html lang> is ' + document.documentElement.lang + ' for ' + c);
    if (els.map(n => n.innerHTML).join('|') === en0) bad.push('i18n ' + c + ': the shell is still English');
    if ([...document.querySelectorAll('[data-lga]')].map(n => n.outerHTML).join('|') === at0) bad.push('i18n ' + c + ': attributes (placeholder, aria-label) still English');
    if (document.getElementById('lang').value !== c) bad.push('i18n: the menu does not show ' + c);
  }
  useLang('en');
  if ([...document.querySelectorAll('[data-lg],[data-lgh]')].map(n => n.innerHTML).join('|') !== en0 || [...document.querySelectorAll('[data-lga]')].map(n => n.outerHTML).join('|') !== at0) bad.push('i18n: English did not come back after the languages');
  if (t('no.such.key', 'x {n}', { n: 2 }) !== 'x 2') bad.push('i18n: t() does not fall back to the English text');
  const f = { one: '{n} a', few: '{n} b', many: '{n} c', other: '{n} d' };
  useLang('ru'); const ru = [1, 2, 5, 21, 22, 25].map(n => tn('no.such.key', n, f)).join(',');
  if (ru !== '1 a,2 b,5 c,21 a,22 b,25 c') bad.push('i18n: Russian plural forms ' + ru);
  useLang('vi'); if (tn('no.such.key', 2, f) !== '2 d') bad.push('i18n: Vietnamese counted string ' + tn('no.such.key', 2, f));
  useLang('en'); if (tn('no.such.key', 1, f) !== '1 a' || tn('no.such.key', 2, f) !== '2 d') bad.push('i18n: English plural forms'); }
// Fonts: Russian draws in Monocraft's own Cyrillic faces and Vietnamese in VT323 (pixel faces, not the system fallback), and the Vietnamese page asks for VT323.
// A width test against the browser's default font does not work (Chromium picks a system face per missing glyph), so this asks which faces the text loads.
{ const ru = 'Путь испытаний Ёё', vi = 'Chế tạo bằng ấ ệ ử ữ Đường đi';
  const cyr = (fs, wt) => fs.some(f => f.status === 'loaded' && f.weight === wt && /U\+400/i.test(f.unicodeRange));
  if (!cyr(await document.fonts.load('32px Monocraft', ru), '400')) bad.push('fonts: no loaded Monocraft face for Cyrillic (regular)');
  if (!cyr(await document.fonts.load('700 32px Monocraft', ru), '700')) bad.push('fonts: no loaded Monocraft face for Cyrillic (bold)');
  if (!(await document.fonts.load('32px "VT323 vi"', vi)).some(f => f.family.includes('VT323') && f.status === 'loaded')) bad.push('fonts: VT323 not loaded for Vietnamese text');
  useLang('vi'); const lt = getComputedStyle(document.querySelector('.logo .lt')).fontFamily, h1 = getComputedStyle(document.querySelector('.top')).getPropertyValue('--title');
  if (!lt.includes('VT323 vi') || !h1.includes('VT323 vi')) bad.push('fonts: the Vietnamese page does not use VT323 for labels and titles: ' + lt + ' | ' + h1);
  useLang('ru'); if (getComputedStyle(document.querySelector('.logo .lt')).fontFamily.includes('VT323')) bad.push('fonts: VT323 leaked into the Russian page');
  useLang('en'); if (getComputedStyle(document.querySelector('.logo .lt')).fontFamily.includes('VT323')) bad.push('fonts: VT323 leaked into the English page'); }
// Pages drawn so far in the language (the hub, an Act page, an Act that does not exist): nothing half-filled, and every sentence they ask for
// is translated or kept in English on purpose (the pack's `keep`: proper names, rarity names). A sentence missing from tm/<lang>/ shows up here.
{ const h0 = location.hash;
  for (const c of LANG_CODES.filter(x => x !== 'en')) { useLang(c); window.__TRLOG = new Set();
    const st0 = JSON.stringify(st); Object.assign(st, { c: ['ME'], r: ['4'], s: 'Ring', q: 'role:melee -mod:brutality' });   // the Curios page with filters on: the pills, the legend, the table of tiers
    // curio pages that reach every helper of the page body: a relic (its level panel too), the stacking rules, a ladder, a scarce material, a Must-Have, a Keeper gate, a ring gate, an evolution
    const cp = [x => RL[x.id], x => SK.i[x.id] && SK.i[x.id].s === 'n', x => SK.i[x.id] && SK.i[x.id].l, x => SK.i[x.id] && SK.i[x.id].l && SK.i[x.id].l[2], x => x.sca, isMust, x => x.gk, x => x.rq, x => evo().from[x.id], x => (evo().to[x.id] || []).length, x => x.g === 'Loot'].map(f => D.find(x => { try { return f(x); } catch (e) { return false; } })).filter(Boolean).map(x => '#i' + x.ix);
    // Equipment: the list in each tab, a search that finds and one that does not, weapon pages of each measured kind (swings, conditions, effects), a set page, a curio with a measured section
    const gp = [x => x.ms && x.ms.sw && !x.ms.st, x => x.ms && x.ms.st === 'cond', x => x.ms && x.ms.pct, x => x.ms && x.ms.st === 'grows', x => x.fx && x.fx.some(r => r.fire !== undefined), x => x.fx && x.fx.some(r => r.chance && r.chance < 1), x => x.fx && x.fx.some(r => r.unseen), x => x.ga, x => x.est, x => x.k === 'armor'].map(f => GE.find(x => { try { return f(x); } catch (e) { return false; } })).filter(Boolean).map(x => '#g' + x.ix);
    const gsp = [x => x.ms && x.ms.bonus, x => !x.kn, x => x.fx && x.fx.length].map(f => GS.find(x => { try { return f(x); } catch (e) { return false; } })).filter(Boolean).map(x => '#gs' + x.ix);
    const cm = D.filter(x => typeof CM !== 'undefined' && CM[x.id]).slice(0, 6).map(x => '#i' + x.ix);
    // Bosses: the list, a Keeper with phases, the three vanilla bosses, a side boss with attacks and drops; the Build planner is driven below
    const bp = ['#bosses', '#boss/iron_colossus', '#boss/discord', '#boss/warden', '#boss/wither', '#boss/ender_dragon', ...Object.keys(SIDEB || {}).filter(n => SIDEB[n].drops && SIDEB[n].drops.length && SIDEB[n].attacks && SIDEB[n].attacks.length).slice(0, 3).map(n => '#side/' + encodeURIComponent(n)), '#build', '#build/6', '#mechanics', '#changes', '#mods', '#mod/' + encodeURIComponent(D[0].m)];
    for (const h of ['#', '#act/2', '#act/99', '#home', '#i5', '#g12', '#gs3', ...cp, '#gear', '#gear/5/RA/a', '#gear/9/MA/c', '#gear/3/SU/w', '#gear/99', ...gp, ...gsp, ...cm, ...bp]) { location.hash = h; render();
      const rv = document.querySelector('[data-rlv]'); if (rv) { rv.value = Math.max(1, Math.floor(rv.max / 2)); rv.dispatchEvent(new Event('input', { bubbles: true })); }   // the relic panel after a move of the slider
      const t = document.getElementById('main').innerText; if (/\{\w+\}|\$\{|undefined|NaN|\[object/.test(t)) bad.push('i18n ' + c + ' ' + h + ': a placeholder or "undefined" shows on the page'); }
    // the tooltip's chrome: Keeper-gated, ring-gated, Must-Have, evolving, estimate, luck window
    for (const d of [D.find(x => x.gk), D.find(x => x.rq), D.find(isMust), D.find(x => evo().from[x.id]), D.find(x => (evo().to[x.id] || []).length), D.find(x => x.pe), D.find(x => x.a !== x.t)].filter(Boolean)) {
      const n = document.createElement('a'); n.dataset.t = String(d.ix); document.body.appendChild(n); TIPC.clear(); showTipBase(n); n.remove(); }
    // Mechanics: the ritual list with its filters in use
    location.hash = '#mechanics'; render(); await new Promise(r => setTimeout(r, 300));
    for (const [id, v] of [['rq', 'sword'], ['rq', 'zzzzqq'], ['rq', ''], ['rk', 'Summon']]) { const e = document.getElementById(id); if (!e) { bad.push('i18n ' + c + ': Mechanics has no #' + id); continue; } e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); await new Promise(r => setTimeout(r, 150));
      const t = document.getElementById('main').innerText; if (/\{\w+\}|\$\{|undefined|NaN|\[object/.test(t)) bad.push('i18n ' + c + ' Mechanics filter: a placeholder or "undefined" shows'); }
    // the Build planner: a starter build, the picker with and without a hit, the inspector, a second panel, a consumable
    location.hash = '#build/12'; render(); await new Promise(r => setTimeout(r, 300));   // the hashchange redraw lands after this render
    for (const f of [() => document.querySelector('[data-preset]').click(), () => document.querySelector('[data-pick]').click(), () => { const q = document.getElementById('bq'); q.value = 'sword'; q.dispatchEvent(new Event('input', { bubbles: true })); }, () => { const q = document.getElementById('bq'); q.value = 'zzzzzz'; q.dispatchEvent(new Event('input', { bubbles: true })); }, () => document.getElementById('bpx').click(), () => document.querySelector('.bxi[data-insp]').click(), () => document.querySelector('[data-pgs="1"]').click(), () => document.querySelector('[data-cons]').click()]) {
      try { f(); } catch (e) { bad.push('i18n ' + c + ': the Build planner step failed: ' + e.message); } await new Promise(r => setTimeout(r, 120));
      const t = document.getElementById('main').innerText; if (/\{\w+\}|\$\{|undefined|NaN|\[object/.test(t)) bad.push('i18n ' + c + ' Build planner: a placeholder or "undefined" shows'); }
    for (const k of [GE.findIndex(x => x.est) >= 0 ? 'g' + GE.findIndex(x => x.est) : 'g0', GE.findIndex(x => x.ga) >= 0 ? 'g' + GE.findIndex(x => x.ga) : 'g1', 's0', 's' + Math.floor(GS.length / 2)]) { const n = document.createElement('a'); n.dataset.t = k; document.body.appendChild(n); gearTip(n); n.remove(); }   // the tooltip of a weapon and of a set
    GSTATE.q = 'sword'; location.hash = '#gear/0/ME/w'; render(); GSTATE.q = 'zzzz'; render(); GSTATE.q = '';
    for (const h of ['#gear/5/ME/w', '#gear/0/MA/c']) { location.hash = h; render(); await new Promise(r => setTimeout(r, 500)); }   // a room painted after longer text wrapped once raised a ResizeObserver notice that showed as a wiki error
    const je = document.getElementById('jserr'); if (je) { bad.push('i18n ' + c + ': the page shows a wiki error: ' + je.textContent.slice(0, 120)); je.remove(); }
    hideTip();
    Object.assign(st, JSON.parse(st0));
    const keep = new Set(I18N[c].keep || []);
    for (const en of keep) if (I18N[c].tr[hsh(en)] !== undefined) bad.push('i18n ' + c + ': "' + en + '" is kept in English on purpose but the pack translates it (' + I18N[c].tr[hsh(en)] + ')');   // the game\'s own text must not slip past the keep list
    for (const en of window.__TRLOG) if (!trOf(en) && !keep.has(en)) bad.push('i18n ' + c + ': no translation for ' + JSON.stringify(en.replace('\u0001', ' | ')).slice(0, 80)); }
  window.__TRLOG = undefined; useLang('en'); location.hash = h0; render(); }
// The sidebar is built once in English and only relabelled: the filter keys stay English (saved filters and shared links keep working), the labels follow the
// language, and a query can name a role in the reader's own language.
{ const h0 = location.hash; useLang('ru'); const chip = document.querySelector('#fc button'), d = D.find(x => x.ro.includes('ME')), q0 = st.q;
  if (chip.dataset.k !== 'ME' || chip.firstChild.nodeValue !== T('Melee') || T('Melee') === 'Melee') bad.push('i18n ru: the Role chip is not relabelled (' + chip.firstChild.nodeValue + ' for key ' + chip.dataset.k + ')');
  st.q = 'role:ближний'; if (!qMatch(d)) bad.push('i18n ru: "role:ближний" does not find a melee curio'); st.q = 'role:melee'; if (!qMatch(d)) bad.push('i18n ru: "role:melee" stopped working'); st.q = q0;
  useLang('en'); if (document.querySelector('#fc button').firstChild.nodeValue !== 'Melee') bad.push('i18n: the Role chip did not come back to English'); location.hash = h0; render(); }

// Data text (Phase 3): a curio's effect line and its source lines (the "How to get it" list, the tooltip's last lines) are said in every language.
// fxT reads the pack's table; srcT matches the clause shapes of the patch scripts and falls back to a whole-line entry. A line that stays English means the
// patch scripts made a new line (or clause shape) nobody translated.
{ const h0 = location.hash, seen = new Set(), srcLines = new Set(), fxLines = new Set();
  for (const d of D) { fxLines.add(d.fx); for (const x of d.src) if (!(d.gr && RCV.test(x)) && !/^Key requirement: locked behind/i.test(x)) srcLines.add(x); for (const x of (d.gr ? d.src.filter(x => !RCV.test(x)) : d.src).slice(0, 2)) srcLines.add(x); }
  for (const c of ['vi', 'ru', 'pt', 'es']) { useLang(c); let nf = 0, ns = 0;
    for (const l of fxLines) if (l && I18N[c].tr[hsh(l)] === undefined && !(I18N[c].keep || []).includes(l)) { if (nf++ < 3) bad.push('i18n ' + c + ': the effect line is still English: ' + l.slice(0, 90)); }
    if (nf > 3) bad.push('i18n ' + c + ': ' + nf + ' effect lines in all are still English');
    for (const l of srcLines) if (srcT(l) === l) { if (ns++ < 3) bad.push('i18n ' + c + ': the source line is still English: ' + l.slice(0, 90)); }
    if (ns > 3) bad.push('i18n ' + c + ': ' + ns + ' source lines in all are still English'); }
  useLang('en'); if (D.some(d => srcT(d.src[0] || '') !== (d.src[0] || ''))) bad.push('i18n: srcT changes an English source line'); location.hash = h0; }
// Boss text (Phase 3): the attack lists, "where to find it" lines and the items' own summon texts have an entry in every pack (the wiki's data file stays English).
{ const L = new Set(); const add = s => { if (typeof s === 'string' && s.trim().split(/\s+/).length >= 3) L.add(s); };   // three words or more: a name or a place stays English
  for (const k in BINFO) for (const p of BINFO[k].ph || []) for (const a of p.at || []) { add(a.n); add(a.d); }
  for (const k in SIDEB) { const b = SIDEB[k]; add(b.find); add(b.drops_note); for (const a of b.attacks || []) { add(a.name); add(a.desc); } }
  for (const k in SUM) add(SUM[k].info);
  for (const c of ['vi', 'ru', 'pt', 'es']) { let n = 0; for (const l of L) if (I18N[c].tr[hsh(l)] === undefined && !(I18N[c].keep || []).includes(l)) { if (n++ < 3) bad.push('i18n ' + c + ': boss text without a translation: ' + l.slice(0, 90)); }
    if (n > 3) bad.push('i18n ' + c + ': ' + n + ' boss texts in all have no translation'); } }
// Equipment attribute names (Phase 3): the lines "+8% Attack Speed" of the tooltip and the Bonuses list keep their number and translate the attribute name (gAL); every name the gear tables produce has an entry,
// except the ones that stay English on purpose (a spell school's Spell Power, Luck, Omnivamp, Lethality).
{ const names = new Set(); for (const g of GE) { for (const x of gBonus(g)) { const m = x.match(/^([+\-−]?\d[\d.,]*)(%?) (.+)$/); if (m) names.add(m[3]); } for (const [, n] of gStats(g)) names.add(n); }
  for (const c of ['vi', 'ru', 'pt', 'es']) { let n = 0; for (const a of names) if (I18N[c].tr[hsh(a)] === undefined && !/ Spell Power$|^(Luck|Omnivamp|Lethality|Spell Power)$/.test(a)) { if (n++ < 3) bad.push('i18n ' + c + ': the attribute name has no translation: ' + a); }
    if (n > 3) bad.push('i18n ' + c + ': ' + n + ' attribute names in all have no translation'); }
  useLang('ru'); if (gAL('+8% Attack Speed') === '+8% Attack Speed' || gAL('+2.5% Life Steal') !== '+2,5% ' + TD('Life Steal')) bad.push('i18n ru: gAL does not translate the name or does not take the decimal comma: ' + gAL('+2.5% Life Steal')); useLang('en');
  if (gAL('+8% Attack Speed') !== '+8% Attack Speed') bad.push('i18n: gAL changes an English line'); }
// Guide book (Phase 3): the text of each "From the guide book" entry has an entry in every pack (the book and entry titles are names and stay English).
{ const L = new Set(); for (const k in GUIDE) if (GUIDE[k].t) L.add(GUIDE[k].t);
  for (const c of ['vi', 'ru', 'pt', 'es']) { let n = 0; for (const l of L) if (I18N[c].tr[hsh(l)] === undefined && l.trim().split(/\s+/).length >= 3) { if (n++ < 3) bad.push('i18n ' + c + ': a guide book text has no translation: ' + l.slice(0, 80)); }
    if (n > 3) bad.push('i18n ' + c + ': ' + n + ' guide book texts in all have no translation'); } }
// Curio tooltip lines (Phase 3): the raw stat lines of the in-game tooltip (d.st) are said in every language. A whole sentence has a pack entry (stT -> TD); a "+8% Name" line keeps its number and
// translates the name (gAL); a "Name: value" config line translates its label and its value (cfgT). Left English on purpose: titles (every word capitalised), tags, symbol-only lines, the names Spell Power / Cast / Luck / Lethality / Omnivamp / Tenacity.
{ const L = new Set(); for (const d of D) for (const x of d.st || []) if (typeof x === 'string') L.add(x);
  const skip = l => !/[a-z]{3}/.test(l) || /^[a-z ]+$/.test(l) || /_/.test(l) || /^([A-Z][\w'’\-!?]*|of|the|to|and|in|a|an|from|for|is|[IVX]+|\?+)( |$)/.test(l) && l.split(/\s+/).every(w => /^([A-Z][\w'’\-!?]*|of|the|to|and|in|a|an|from|for|is|[IVX]+|\?+)$/.test(w))
    || / Spell Power$| Cast( \d)?$|^[+\-−]?\d[\d.,]*x? ?%? ?(Luck|Lethality|Omnivamp|Tenacity|Brimwielder School Level|Robes Iron Resist|Effect Geomancy Break)$/.test(l);
  for (const c of ['vi', 'ru', 'pt', 'es']) { useLang(c); let n = 0;
    const keep = new Set(I18N[c].keep || []), cfg = l => /^[^:]{1,90}: /.test(l);
    for (const l of L) if (!skip(l) && !cfg(l) && stT(l) === l && I18N[c].tr[hsh(l)] === undefined) { if (n++ < 3) bad.push('i18n ' + c + ': a tooltip line is still English: ' + l.slice(0, 90)); }
    // a "Label: value" line: every part of the label ("A — B › C", without "[active]", "(…)", "Chest chance in …") has a pack entry; a part that is a short title or an acronym can stay
    for (const l of L) if (cfg(l) && !skip(l) && I18N[c].tr[hsh(l)] === undefined) { const lab = l.slice(0, l.indexOf(': '));
      for (const seg of lab.split(/ — | › /)) { const b = seg.replace(/ \([^)]*\)$/, '').replace(/ \[active\]$/, '').replace(/^(Chest chance in|Drop chance from) .*$/, ''); if (b && !/^[A-Z0-9 ]{1,4}$/.test(b) && !keep.has(b) && I18N[c].tr[hsh(b)] === undefined) { if (n++ < 3) bad.push('i18n ' + c + ': the label of a tooltip line has no translation: ' + b); break; } } }
    if (n > 3) bad.push('i18n ' + c + ': ' + n + ' tooltip lines in all are still English'); }
  useLang('ru'); if (stT('+2.5% Life Steal') !== '+2,5% ' + TD('Life Steal') || gAL('+1.5x Damage dealt') === '+1.5x Damage dealt' || !/^\+1,5x /.test(gAL('+1.5x Damage dealt')) || gAL('30 second cooldown') === '30 second cooldown') bad.push('i18n ru: stT/gAL do not translate a multiplier or cooldown line');
  useLang('en'); if (D.some(d => (d.st || []).some(x => typeof x === 'string' && stT(x) !== x))) bad.push('i18n: stT changes an English tooltip line'); }
// Numbers with a thousands group (the AE2 cell tables, relic XP): ru groups with a space and a decimal comma, pt with dots, vi like English (its decimals keep the dot); English leaves it to the browser as before.
{ useLang('ru'); const r = nL(1234567.5); useLang('pt'); const q = nL(1234.5); useLang('vi'); const v = nL(1234.5); useLang('en');
  if (!/^1\s234\s567,5$/.test(r) || q !== '1.234,5' || v !== '1,234.5' || nL(1234.5) !== (1234.5).toLocaleString()) bad.push('i18n: nL groups numbers wrongly: ' + [r, q, v].join(' | ')); }
// Relic panel (Phase 3): the stat names ("Maximum duration") and the formats of their values ("%1$s seconds.") have an entry in every pack; a percent sign in es is written with a space.
// Ability names (Fins, Gills, Leap...) and Charms / Stun / Frostbite are names and stay English.
{ const nm = new Set(), fm = new Set(); for (const id in RL) for (const a of RL[id].ab) for (const t of a.st) { nm.add(t.n); fm.add(t.f); }
  for (const c of ['vi', 'ru', 'pt', 'es']) { let n = 0; for (const x of nm) if (!/^(Charms|Stun|Frostbite)$/.test(x) && I18N[c].tr[hsh(x)] === undefined) { if (n++ < 3) bad.push('i18n ' + c + ': a relic stat name has no translation: ' + x); }
    for (const f of fm) if ((/[a-z]{3}/.test(f.replace('%1$s', '')) || (c === 'es' && /%%/.test(f))) && I18N[c].tr[hsh(f)] === undefined) { if (n++ < 3) bad.push('i18n ' + c + ': a relic value format has no translation: ' + f); }
    if (n > 3) bad.push('i18n ' + c + ': ' + n + ' relic stat names and formats in all have no translation'); }
  const t0 = RL[Object.keys(RL)[0]].ab[0].st[0]; useLang('ru'); const sr = rlStat(t0, 0, -1); useLang('en'); if (/seconds/.test(sr) || /\d\.\d/.test(sr)) bad.push('i18n ru: rlStat does not translate the format or the decimal sign: ' + sr);
  if (!/seconds/.test(rlStat(t0, 0, -1))) bad.push('i18n: rlStat does not say the English format in English: ' + rlStat(t0, 0, -1)); }
// Item names (Phase 3, C3): the names of curios and gear are said in every language (a name that is a proper noun, a coined metal or an acronym stays English on purpose, so a few per cent are left),
// and every translated name keeps its English name beside it: a small line under the page title (enAlt) and in the tooltip (enTip). English shows neither; a name left English shows neither.
{ const all = [...new Set([...D.map(d => d.n), ...GE.map(g => g.n)])];
  for (const c of ['vi', 'ru', 'pt', 'es']) { useLang(c); const k = all.filter(n => TD(n) !== n).length;
    if (k < all.length * 0.9) bad.push('i18n ' + c + ': only ' + k + ' of ' + all.length + ' item names are translated');
    const t = all.find(n => TD(n) !== n), u = all.find(n => TD(n) === n);
    if (!t || !new RegExp('^<p class="ip-alt" lang="en">').test(enAlt(t)) || !enAlt(t).includes(esc(t)) || !enTip(t).includes('class="tnen"')) bad.push('i18n ' + c + ': the English alias line is missing for a translated name');
    if (u && (enAlt(u) !== '' || enTip(u) !== '')) bad.push('i18n ' + c + ': the English alias line shows for a name that is not translated: ' + u); }
  useLang('en'); if (all.some(n => enAlt(n) !== '' || enTip(n) !== '')) bad.push('i18n: the English alias line shows in English'); }
