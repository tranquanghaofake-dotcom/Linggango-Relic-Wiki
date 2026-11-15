// Spells: every spell the jars register (pack_audit/spells.py -> patches/spells.json) is on #spells, the seventh tab (2026-11-14).
// Runs in the page (check.js: `bad` and `patchJSON` in scope): the data, its cross-links to Effects, the icons, the filters and the header tab.
{ const wait = ms => new Promise(r => setTimeout(r, ms)), P = (await patchJSON('spells.json')).spells, X = window.SPL || [];
  if (!X.length) bad.push('spells: window.SPL is empty (wiki_pics.js)');
  else {
    if (X.length !== P.length) bad.push(`spells: the page has ${X.length} spells, patches/spells.json ${P.length}`);
    const ids = new Set(X.map(e => e.i)), eff = new Set((window.EFX || []).map(e => e.i));
    if (ids.size !== X.length) bad.push('spells: a spell id twice');
    // the list is the game's own registry (patches/game_registry.json, KubeJS lgw_registry.js): none missing, none the game lacks
    { const g = new Set((await patchJSON('game_registry.json')).spells.map(s => s.id).filter(i => i !== 'irons_spellbooks:none'));
      for (const id of g) if (!ids.has(id)) bad.push('spells: the game registers ' + id + ', the page lacks it');
      for (const id of ids) if (!g.has(id)) bad.push('spells: ' + id + ' is on the page but the game does not register it'); }
    if (ids.has('irons_spellbooks:none')) bad.push('spells: the empty NoneSpell is listed');
    for (const s of X) {
      if (!/^[a-z0-9_.-]+:[a-z0-9_./-]+$/.test(s.i)) bad.push('spells: odd id ' + s.i); if (!s.m) bad.push('spells: no mod on ' + s.i);
      if (s.L != null && !(s.L >= 1)) bad.push('spells: ' + s.i + ' max level ' + s.L); if (s.c != null && !(s.c >= 0)) bad.push('spells: ' + s.i + ' cooldown ' + s.c);
      if (s.k && !['INSTANT', 'LONG', 'CONTINUOUS'].includes(s.k)) bad.push('spells: ' + s.i + ' cast type ' + s.k);
      if (s.s && !(s.s in SCOL)) bad.push('spells: school "' + s.s + '" has no colour (SCOL in app.js)');
      for (const f of s.f || []) if (!eff.has(f)) bad.push(`spells: ${s.i} applies ${f}, which is not on the Effects page`); }
    // what the jar says about one well-known spell (Fireball, read by javap: DefaultConfig RARE, FIRE, level 5, 25 s; mana 60 + 15 a level; cast 40 ticks, LONG)
    const fb = X.find(s => s.i === 'irons_spellbooks:fireball');
    if (!fb || fb.s !== 'fire' || fb.r !== 'rare' || fb.L !== 5 || fb.c !== 25 || fb.ma !== 60 || fb.mp !== 15 || fb.t !== 40 || fb.k !== 'LONG') bad.push('spells: Fireball reads ' + JSON.stringify(fb));
    // the pack's per-spell config turns four spells off (config/irons_spellbooks_spell_config): the page says so
    const off = X.filter(s => s.x).length, offData = P.filter(s => s.enabled === false).length;
    if (off !== offData) bad.push(`spells: ${off} turned off on the page, ${offData} in the data`);
    for (const id of window.SPCLIP || []) if (!ids.has(id)) bad.push('spells: a clip for the unknown ' + id);
    const ic = window.SPLI || {}; for (const k of Object.keys(ic)) if (!ids.has(k)) bad.push('spells: icon for unknown ' + k);
    // the page
    location.hash = '#spells'; await wait(80); render(); await wait(300);
    const n = () => document.querySelectorAll('#spl .spc').length, cnt = () => document.getElementById('sn')?.textContent, inp = (e, v) => { e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); };
    if (n() !== 40) bad.push('spells: the first draw has ' + n() + ' cards, want 40');
    if (cnt() !== X.length + ' of ' + X.length) bad.push('spells: the count line says ' + cnt());
    const q = document.getElementById('sq'), ss = document.getElementById('ss'), sk = document.getElementById('sk'), sm = document.getElementById('sm');
    inp(ss, 'fire'); if (cnt() !== X.filter(s => s.s === 'fire').length + ' of ' + X.length) bad.push('spells: school Fire says ' + cnt()); inp(ss, '');
    inp(sk, 'CONTINUOUS'); if (cnt() !== X.filter(s => s.k === 'CONTINUOUS').length + ' of ' + X.length) bad.push('spells: Continuous says ' + cnt()); inp(sk, '');
    inp(sm, "Iron's Spells 'n Spellbooks"); if (cnt() !== X.filter(s => s.m === "Iron's Spells 'n Spellbooks").length + ' of ' + X.length) bad.push("spells: mod Iron's says " + cnt()); inp(sm, '');
    inp(q, 'zzzzqq'); if (n() !== 0) bad.push('spells: a nonsense filter shows ' + n() + ' cards'); inp(q, '');
    for (let i = 0; i < 20 && document.querySelector('#smore button'); i++) document.querySelector('#smore button').click();
    if (n() !== X.length) bad.push('spells: Show more ends at ' + n() + ' of ' + X.length);
    if (/undefined|NaN|\[object/.test(document.getElementById('main').innerText)) bad.push('spells: undefined, NaN or [object] on the page');
    if (!document.documentElement.dataset.clips && document.querySelector('#spl video')) bad.push('spells: a <video> on the offline page, which has no clips')
    // a link from an effect (or from outside) opens the page filtered: #spells/<id>
    location.hash = '#spells/irons_spellbooks%3Afireball'; await wait(80); render(); await wait(300);
    if (n() !== 1 || !/^\s*Fireball/.test(document.querySelector('#spl .spc h3')?.textContent || '')) bad.push('spells: #spells/irons_spellbooks:fireball shows ' + n() + ' cards');
    // the chips of an effect lead to the Effects page filtered to it, and that page lists the spell back
    const sp = X.find(s => (s.f || []).length); location.hash = '#mechanics/effects/' + encodeURIComponent(sp.f[0]); await wait(80); render(); await wait(300);
    if (![...document.querySelectorAll('#etb tr')].some(t => t.querySelector(`a[href="#spells/${encodeURIComponent(sp.i)}"]`))) bad.push(`spells: the Effects page for ${sp.f[0]} does not list ${sp.i}`);
    // the header: seven tabs, Spells marked on its page
    location.hash = '#spells'; await wait(120); render(); await wait(200);
    const tabs = [...document.querySelectorAll('nav.nav a')].map(a => a.getAttribute('href'));
    if (tabs.join() !== '#home,#gear,#build,#bosses,#mechanics,#spells,#changes') bad.push('spells: header tabs ' + tabs.join());
    if (document.querySelector('nav.nav a[aria-current]')?.getAttribute('href') !== '#spells') bad.push('spells: the header does not mark Spells');
    if (!document.title.startsWith(document.querySelector('nav.nav a[href="#spells"]').textContent.trim())) bad.push('spells: title ' + document.title);
    if (getComputedStyle(document.getElementById('side')).display !== 'none') bad.push('spells: the Filters column shows beside the Spells page');
  }
  // Spells > Goety (2026-11-15): every focus the game export lists (an item with getSpell() whose id ends in _focus) and nothing else; the numbers are the export's;
  // the sub-tabs switch the system and #spells/<text> stays Iron's with the search filled
  { const G = window.GSPL || [], E = ((await patchJSON('game_registry.json')).goety || []).filter(g => g.id.endsWith('_focus')), Ei = new Map(E.map(g => [g.id, g]));
    if (!G.length) bad.push('spells: window.GSPL is empty (Goety focuses)');
    if (new Set(G.map(g => g.i)).size !== G.length) bad.push('spells: a Goety focus twice');
    for (const g of E) if (!G.some(x => x.i === g.id)) bad.push('spells: the game has the focus ' + g.id + ', the Goety tab lacks it');
    for (const x of G) { const e = Ei.get(x.i); if (!e) { bad.push('spells: ' + x.i + ' is on the Goety tab but not a focus in the export'); continue; }
      if (x.c !== e.cost || x.t !== e.cast || x.cd !== e.cooldown || x.y !== (e.type || 'NONE').toLowerCase()) bad.push('spells: ' + x.i + ' numbers differ from the export');
      if (!(x.y in GCOL)) bad.push('spells: Goety type "' + x.y + '" has no colour (GCOL in app.js)'); }
    for (const id of window.SPCLIP || []) if (![window.SPL, G, window.ASPL, window.BSPL].some(L => (L || []).some(s => s.i === id))) bad.push('spells: a clip for ' + id + ', on no tab');
    location.hash = '#spells/goety'; await wait(80); render(); await wait(300);
    const cards = () => document.querySelectorAll('#gpl .spc').length;
    if (cards() !== Math.min(40, G.length)) bad.push('spells: the Goety tab first draws ' + cards() + ' cards');
    if (document.getElementById('gn')?.textContent !== G.length + ' of ' + G.length) bad.push('spells: the Goety count says ' + document.getElementById('gn')?.textContent);
    if (document.querySelector('nav.mtabs a[aria-current]')?.getAttribute('href') !== '#spells/goety') bad.push('spells: the Goety sub-tab is not marked');
    if (/undefined|NaN|\[object/.test(document.getElementById('main').innerText)) bad.push('spells: undefined, NaN or [object] on the Goety tab');
    location.hash = '#spells/irons_spellbooks:fireball'; await wait(80); render(); await wait(300);
    if (document.getElementById('sq')?.value !== 'irons_spellbooks:fireball' || document.querySelector('nav.mtabs a[aria-current]')?.getAttribute('href') !== '#spells') bad.push('spells: #spells/<id> no longer opens Iron\'s with the search filled'); }
  // Spells > Ars Nouveau (2026-11-15): every glyph of the export's GlyphRegistry and nothing else; mana cost and on/off are the export's, the kind follows the
  // glyph's type index; the tier is the pack's config (spell_systems.py), so here: 1 to 3, and one tier for each SpellTier object the export printed
  { const A = window.ASPL || [], E = (await patchJSON('game_registry.json')).ars || [], Ei = new Map(E.map(g => [g.id, g])), KIND = {1: 'form', 5: 'augment', 8: 'effect', 10: 'effect', 15: 'filter'}, tierOf = new Map();
    if (!A.length) bad.push('spells: window.ASPL is empty (Ars glyphs)');
    if (new Set(A.map(g => g.i)).size !== A.length) bad.push('spells: an Ars glyph twice');
    for (const g of E) if (!A.some(x => x.i === g.id)) bad.push('spells: the game has the glyph ' + g.id + ', the Ars tab lacks it');
    for (const x of A) { const e = Ei.get(x.i); if (!e) { bad.push('spells: ' + x.i + ' is on the Ars tab but not a glyph in the export'); continue; }
      if (x.c !== e.cost || !!x.x !== (e.enabled === false) || x.k !== KIND[e.type]) bad.push('spells: ' + x.i + ' cost, on/off or kind differ from the export');
      if (!(x.k in ACOL)) bad.push('spells: Ars kind "' + x.k + '" has no colour (ACOL in app.js)');
      if (![1, 2, 3].includes(x.r)) bad.push('spells: ' + x.i + ' has tier ' + x.r);
      if (tierOf.has(e.tier) && tierOf.get(e.tier) !== x.r) bad.push('spells: ' + x.i + ' tier ' + x.r + ', another glyph of the same SpellTier has ' + tierOf.get(e.tier));
      tierOf.set(e.tier, x.r); }
    location.hash = '#spells/ars'; await wait(80); render(); await wait(300);
    const cards = () => document.querySelectorAll('#apl .spc').length, count = () => document.getElementById('an')?.textContent;
    if (cards() !== Math.min(40, A.length)) bad.push('spells: the Ars tab first draws ' + cards() + ' cards');
    if (count() !== A.length + ' of ' + A.length) bad.push('spells: the Ars count says ' + count());
    if (document.querySelector('nav.mtabs a[aria-current]')?.getAttribute('href') !== '#spells/ars') bad.push('spells: the Ars sub-tab is not marked');
    if (/undefined|NaN|\[object/.test(document.getElementById('main').innerText)) bad.push('spells: undefined, NaN or [object] on the Ars tab');
    const ar = document.getElementById('ar'); if (ar) { ar.value = '3'; ar.dispatchEvent(new Event('input')); const n3 = A.filter(x => x.r === 3).length;
      if (count() !== n3 + ' of ' + A.length) bad.push('spells: the Ars tier filter (3) says ' + count() + ', expected ' + n3); } else bad.push('spells: no tier filter on the Ars tab'); }
  // Spells > Brutality (2026-11-15): every spell of the export's SpellRegistry and nothing else; base numbers and per-level additions are the export's;
  // the first category is how it is cast; every school has a colour
  { const B = window.BSPL || [], E = (await patchJSON('game_registry.json')).brutality || [], Ei = new Map(E.map(g => [g.id, g]));
    if (!B.length) bad.push('spells: window.BSPL is empty (Brutality spells)');
    if (new Set(B.map(g => g.i)).size !== B.length) bad.push('spells: a Brutality spell twice');
    for (const g of E) if (!B.some(x => x.i === g.id)) bad.push('spells: the game has the spell ' + g.id + ', the Brutality tab lacks it');
    for (const x of B) { const e = Ei.get(x.i); if (!e) { bad.push('spells: ' + x.i + ' is on the Brutality tab but not in the export'); continue; }
      const cats = (e.cats || '').replace(/[\[\]\s]/g, '').toLowerCase().split(',').filter(Boolean), z = v => v || 0;
      if (z(x.ma) !== z(e.mana) || z(x.mal) !== z(e.manaLv) || z(x.d) !== z(e.damage) || z(x.dl) !== z(e.damageLv) || z(x.cd) !== z(e.cooldown) || z(x.cdl) !== z(e.cooldownLv)
        || z(x.t) !== z(e.cast) || z(x.tl) !== z(e.castLv) || x.s !== e.school || x.k !== cats[0] || (x.tg || []).join() !== cats.slice(1).join()) bad.push('spells: ' + x.i + ' numbers or categories differ from the export');
      if (!(x.s in BCOL)) bad.push('spells: Brutality school "' + x.s + '" has no colour (BCOL in app.js)');
      if (!(x.k in BCAST) || (x.tg || []).some(t => !(t in BTAG))) bad.push('spells: ' + x.i + ' has a category with no label (BCAST, BTAG in app.js)'); }
    location.hash = '#spells/brutality'; await wait(80); render(); await wait(300);
    const cards = () => document.querySelectorAll('#bpl .spc').length, count = () => document.getElementById('bn')?.textContent;
    if (cards() !== Math.min(40, B.length)) bad.push('spells: the Brutality tab first draws ' + cards() + ' cards');
    if (count() !== B.length + ' of ' + B.length) bad.push('spells: the Brutality count says ' + count());
    if (document.querySelector('nav.mtabs a[aria-current]')?.getAttribute('href') !== '#spells/brutality') bad.push('spells: the Brutality sub-tab is not marked');
    if (/undefined|NaN|\[object/.test(document.getElementById('main').innerText)) bad.push('spells: undefined, NaN or [object] on the Brutality tab'); }
  location.hash = '#home'; await wait(80); render(); }
