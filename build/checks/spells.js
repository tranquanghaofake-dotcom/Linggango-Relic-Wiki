// Spells: every spell the jars register (pack_audit/spells.py -> patches/spells.json) is on #spells, the seventh tab (2026-11-14).
// Runs in the page (check.js: `bad` and `patchJSON` in scope): the data, its cross-links to Effects, the icons, the filters and the header tab.
{ const wait = ms => new Promise(r => setTimeout(r, ms)), P = (await patchJSON('spells.json')).spells, X = window.SPL || [];
  if (!X.length) bad.push('spells: window.SPL is empty (wiki_pics.js)');
  else {
    if (X.length !== P.length) bad.push(`spells: the page has ${X.length} spells, patches/spells.json ${P.length}`);
    const ids = new Set(X.map(e => e.i)), eff = new Set((window.EFX || []).map(e => e.i));
    if (ids.size !== X.length) bad.push('spells: a spell id twice');
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
  location.hash = '#home'; await wait(80); render(); }
