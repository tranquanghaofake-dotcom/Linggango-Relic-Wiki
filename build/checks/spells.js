// Spells: every spell the jars register (pack_audit/spells.py -> patches/spells.json) is on #spells, the seventh tab (2026-11-14); since 2026-11-17 one
// library for the four systems (app.js spellsPage, docs/plans/2026-11-17-spell-library.md).
// Runs in the page (check.js: `bad` and `patchJSON` in scope): the data, its cross-links to Effects, the icons, the library's search, filters, links and the header tab.
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
    // every clip belongs to a spell of some tab: checked below with the other systems (Goety, Ars, Brutality clips are not Iron's spells)
    const ic = window.SPLI || {}; for (const k of Object.keys(ic)) if (!ids.has(k)) bad.push('spells: icon for unknown ' + k);
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
  // Spells > Goety (2026-11-15): every focus the game export lists (an item with getSpell() whose id ends in _focus) and nothing else; the numbers are the export's
  { const G = window.GSPL || [], E = ((await patchJSON('game_registry.json')).goety || []).filter(g => g.id.endsWith('_focus')), Ei = new Map(E.map(g => [g.id, g]));
    if (!G.length) bad.push('spells: window.GSPL is empty (Goety focuses)');
    if (new Set(G.map(g => g.i)).size !== G.length) bad.push('spells: a Goety focus twice');
    for (const g of E) if (!G.some(x => x.i === g.id)) bad.push('spells: the game has the focus ' + g.id + ', the Goety tab lacks it');
    for (const x of G) { const e = Ei.get(x.i); if (!e) { bad.push('spells: ' + x.i + ' is on the Goety tab but not a focus in the export'); continue; }
      if (x.c !== e.cost || x.t !== e.cast || x.cd !== e.cooldown || x.y !== (e.type || 'NONE').toLowerCase()) bad.push('spells: ' + x.i + ' numbers differ from the export');
      if (!(x.y in GCOL)) bad.push('spells: Goety type "' + x.y + '" has no colour (GCOL in app.js)'); }
    for (const id of window.SPCLIP || []) if (![window.SPL, G, window.ASPL, window.BSPL].some(L => (L || []).some(s => s.i === id))) bad.push('spells: a clip for ' + id + ', in no system'); }
  // Spells > Ars Nouveau (2026-11-15): every glyph of the export's GlyphRegistry and nothing else; mana cost and on/off are the export's, the kind follows the
  // glyph's type index; the tier is the pack's config (spell_systems.py), so here: 1 to 3, and one tier for each SpellTier object the export printed
  { const A = window.ASPL || [], E = (await patchJSON('game_registry.json')).ars || [], Ei = new Map(E.map(g => [g.id, g])), KIND = {1: 'form', 5: 'augment', 8: 'effect', 10: 'effect', 15: 'filter'}, tierOf = new Map();
    if (!A.length) bad.push('spells: window.ASPL is empty (Ars glyphs)');
    if (new Set(A.map(g => g.i)).size !== A.length) bad.push('spells: an Ars glyph twice');
    for (const g of E) if (!A.some(x => x.i === g.id)) bad.push('spells: the game has the glyph ' + g.id + ', the Ars tab lacks it');
    for (const x of A) { const e = Ei.get(x.i); if (!e) { bad.push('spells: ' + x.i + ' is on the Ars tab but not a glyph in the export'); continue; }
      if (x.c !== e.cost || !!x.x !== (e.enabled === false) || x.k !== KIND[e.type]) bad.push('spells: ' + x.i + ' cost, on/off or kind differ from the export');
      if (!(x.k in ACOL)) bad.push('spells: Ars kind "' + x.k + '" has no colour (ACOL in app.js)');
      if (!(x.g || '').trim()) bad.push('spells: ' + x.i + ' has a blank description (Iceburst\'s export text is one space: spell_systems.py falls back to the lang file)');
      if (![1, 2, 3].includes(x.r)) bad.push('spells: ' + x.i + ' has tier ' + x.r);
      if (tierOf.has(e.tier) && tierOf.get(e.tier) !== x.r) bad.push('spells: ' + x.i + ' tier ' + x.r + ', another glyph of the same SpellTier has ' + tierOf.get(e.tier));
      tierOf.set(e.tier, x.r); }
  }
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
  }
  // the library (2026-11-17): one list of every spell the pack leaves on, the system chips and the filter chips count what they show, a spell's link opens it,
  // and every spell the pack leaves on has a clip or says why it has none (build/clips/noclip.json, window.SPWHY)
  { const SP = window.SPL || [], G = window.GSPL || [], A = window.ASPL || [], B = window.BSPL || [], why = window.SPWHY || {}, clips = new Set(window.SPCLIP || []);
    const on = { irons: SP.filter(s => !s.x), goety: G, ars: A.filter(s => !s.x), brutality: B }, all = Object.values(on).flat(), total = all.length, offN = SP.length + A.length - on.irons.length - on.ars.length;
    for (const id of Object.keys(why)) { if (!all.some(s => s.i === id)) bad.push('spells: noclip.json gives a reason for ' + id + ', not a spell the pack leaves on'); if (clips.has(id)) bad.push('spells: ' + id + ' has a clip and a no-clip reason'); }
    if (clips.size) for (const s of all) if (!clips.has(s.i) && !why[s.i]) bad.push('spells: ' + s.i + ' has neither a clip nor a reason in build/clips/noclip.json');
    const rows = () => document.querySelectorAll('#spl .sr').length, cnt = () => document.getElementById('sn')?.textContent, h2 = () => document.querySelector('#sdp h3')?.textContent.trim();
    const go = async h => { location.hash = h; await wait(80); render(); await wait(300); }, chip = (f, v) => document.querySelector(`#sfxb [data-f="${f}"][data-v="${CSS.escape(v)}"]`);
    const press = async b => { b.click(); await wait(30); }, input = async (v) => { const q = document.getElementById('sq'); q.value = v; q.dispatchEvent(new Event('input', { bubbles: true })); await wait(30); };
    await go('#spells');
    if (rows() !== Math.min(60, total)) bad.push('spells: the first draw has ' + rows() + ' rows, want 60');
    if (cnt() !== total + ' of ' + total) bad.push('spells: the count line says ' + cnt() + ', want ' + total + ' of ' + total);
    if (document.querySelectorAll('#main *').length >= 5000) bad.push('spells: #main has ' + document.querySelectorAll('#main *').length + ' nodes on the first draw (limit 5000)');
    if (/undefined|NaN|\[object|\{\w+\}/.test(document.getElementById('main').innerText)) bad.push('spells: undefined, NaN, [object] or a {placeholder} on the page');
    if (innerWidth > 760 && !h2()) bad.push('spells: a wide page opens with an empty detail panel');
    // the system chips: each says how many spells it shows, and shows them
    const sysb = [...document.querySelectorAll('#ssys [data-sy]')];
    if (sysb.map(b => b.dataset.sy).join() !== ',irons,goety,ars,brutality') bad.push('spells: the system chips are ' + sysb.map(b => b.dataset.sy).join());
    for (const [k, X] of Object.entries(on)) { const b = document.querySelector(`#ssys [data-sy="${k}"]`); if (!b) continue;
      if (b.querySelector('i')?.textContent !== String(X.length)) bad.push(`spells: the ${k} chip says ${b.querySelector('i')?.textContent}, the data has ${X.length}`);
      await press(b); if (cnt() !== X.length + ' of ' + total) bad.push(`spells: the ${k} chip shows ${cnt()}`);
      if (document.querySelector(`#ssys [data-sy="${k}"]`)?.getAttribute('aria-pressed') !== 'true') bad.push(`spells: the ${k} chip is not marked pressed`);
      if (location.hash !== '#spells/' + k) bad.push(`spells: the ${k} chip leaves the address at ${location.hash}`); }
    await press(document.querySelector('#ssys [data-sy=""]'));
    // a filter chip shows as many spells as its number says (every chip of Clip and How it is cast, and a few others)
    const sample = [...document.querySelectorAll('#sfxb [data-f="st"],#sfxb [data-f="ck"],#sfxb [data-f="tier"]')].map(b => [b.dataset.f, b.dataset.v]).concat([['gk', 'irons/fire'], ['rar', 'legendary']]);
    for (const [f, v] of sample) { const b = chip(f, v); if (!b) { bad.push(`spells: no ${f} chip "${v}"`); continue; } const n = +b.querySelector('.n').textContent;
      await press(b); if (cnt() !== n + ' of ' + total) bad.push(`spells: the ${f} chip "${v}" says ${n}, shows ${cnt()}`); await press(chip(f, v)); }
    if (cnt() !== total + ' of ' + total) bad.push('spells: pressing a chip twice does not clear it (' + cnt() + ')');
    { const b = chip('st', 'off'); if (!b || +b.querySelector('.n').textContent !== offN) bad.push(`spells: the Turned off chip says ${b && b.querySelector('.n').textContent}, the data has ${offN}`); }
    if (clips.size) { const b = chip('st', 'clip'); if (!b || +b.querySelector('.n').textContent !== all.filter(s => clips.has(s.i)).length) bad.push('spells: the Has a clip chip says ' + (b && b.querySelector('.n').textContent)); }
    { const b = chip('gk', 'irons/fire'); if (b && +b.querySelector('.n').textContent !== on.irons.filter(s => s.s === 'fire').length) bad.push('spells: the Fire chip says ' + b.querySelector('.n').textContent); }
    { const b = chip('tier', '3'); if (b && +b.querySelector('.n').textContent !== on.ars.filter(s => s.r === 3).length) bad.push('spells: the Ars Tier 3 chip says ' + b.querySelector('.n').textContent); }
    // search: nonsense finds nothing and says so, a name finds its spell, Clear filters brings everything back
    await input('zzzzqq'); if (rows() !== 0 || !document.querySelector('#spl .empty')) bad.push('spells: a nonsense search shows ' + rows() + ' rows');
    if (document.getElementById('sclr').hidden) bad.push('spells: Clear filters is hidden while a search is on');
    await input('fireball'); if (![...document.querySelectorAll('#spl .sr')].some(a => a.getAttribute('href') === '#spells/' + encodeURIComponent('irons_spellbooks:fireball'))) bad.push('spells: a search for fireball misses Fireball');
    document.getElementById('sclr').click(); await wait(30); if (cnt() !== total + ' of ' + total || document.getElementById('sq').value) bad.push('spells: Clear filters leaves ' + cnt());
    for (let i = 0; i < 20 && document.querySelector('#smore button'); i++) { document.querySelector('#smore button').click(); await wait(10); }
    if (rows() !== total) bad.push('spells: Show more ends at ' + rows() + ' of ' + total);
    if (!document.documentElement.dataset.clips && document.querySelector('#main video')) bad.push('spells: a <video> on the offline page, which has no clips');
    // picking a row shows that spell without redrawing the page, and the address becomes its link
    { const room = document.querySelector('#main .room3'), a = [...document.querySelectorAll('#spl .sr')].find(x => x.getAttribute('href').includes('goety'));
      a.click(); await wait(60); const id = decodeURIComponent(a.getAttribute('href').slice(8));
      if (location.hash !== '#spells/' + encodeURIComponent(id) && decodeURIComponent(location.hash) !== '#spells/' + id) bad.push('spells: picking a row leaves the address at ' + location.hash);
      if (document.querySelector('#main .room3') !== room) bad.push('spells: picking a row redrew the page');
      if (a.getAttribute('aria-current') !== 'true') bad.push('spells: the picked row is not marked');
      if (h2() !== a.querySelector('b').textContent.trim()) bad.push(`spells: picked "${a.querySelector('b').textContent.trim()}", the panel shows "${h2()}"`); }
    // links: a spell (as the Effects page links it), a system, any other text fills the search; a spell without a clip says why; one per system draws cleanly
    await go('#spells/irons_spellbooks%3Afireball');
    if (h2() !== 'Fireball' || document.querySelector('#spl .sr[aria-current]')?.getAttribute('href') !== '#spells/' + encodeURIComponent('irons_spellbooks:fireball')) bad.push('spells: #spells/irons_spellbooks:fireball opens ' + h2());
    await go('#spells/goety'); if (document.querySelector('#ssys [aria-pressed="true"]')?.dataset.sy !== 'goety' || cnt() !== G.length + ' of ' + total) bad.push('spells: #spells/goety shows ' + cnt());
    await go('#spells/frost'); if (document.getElementById('sq').value !== 'frost' || rows() === 0) bad.push('spells: #spells/frost does not search for frost');
    for (const id of Object.keys(why).slice(0, 3)) { await go('#spells/' + encodeURIComponent(id));
      if (document.querySelector('#sdp .snc p')?.textContent !== why[id]) bad.push('spells: ' + id + ' does not say why it has no clip'); }
    { const o = SP.find(s => s.x); if (o) { await go('#spells/' + encodeURIComponent(o.i)); if (!/Turned off/.test(document.querySelector('#sdp .snc')?.textContent || '')) bad.push('spells: the turned-off ' + o.i + ' does not say so'); } }
    for (const X of [SP, G, A, B]) { const s = X.find(x => !x.x); await go('#spells/' + encodeURIComponent(s.i));
      if (/undefined|NaN|\[object|\{\w+\}/.test(document.getElementById('sdp').innerText)) bad.push('spells: undefined, NaN, [object] or a {placeholder} in the panel of ' + s.i); } }
  location.hash = '#home'; await wait(80); render(); }
