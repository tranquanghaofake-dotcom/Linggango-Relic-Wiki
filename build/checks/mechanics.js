// Mechanics: one tab in the header, four pages inside (2026-11-14). `#mechanics` and `#mechanics/goety` draw Goety rituals; `/ae2`, `/effects`
// and `/stats` draw one section each, with the sub-bar under the room naming the open one. The old links (`#mechanics/effects` from item
// pages, `#mechanics/stats` from Changes) keep their meaning. Runs in the page (check.js: `bad` in scope).
{ const wait = ms => new Promise(r => setTimeout(r, ms)), go = async h => { location.hash = h; await wait(60); render(); await wait(250); }, m = () => document.getElementById('main');   // as rooms.js: the hashchange handler marks the header tab (decorate), render() then draws the page again
  const PAGES = [['#mechanics', 'goety'], ['#mechanics/goety', 'goety'], ['#mechanics/ae2', 'ae2'], ['#mechanics/effects', 'effects'], ['#mechanics/stats', 'stats'], ['#mechanics/nonsense', 'goety']];
  for (const [h, want] of PAGES) { await go(h);
    const secs = [...m().querySelectorAll('section.s[id^="m-"]')].map(s => s.id), bar = [...m().querySelectorAll(':scope>nav.mtabs>a')], cur = bar.filter(a => a.getAttribute('aria-current') === 'page');
    if (secs.length !== 1 || secs[0] !== 'm-' + want) bad.push(`mechanics ${h}: draws ${secs.join(',') || 'no section'}, want m-${want} alone`);
    if (bar.map(a => a.getAttribute('href')).join() !== '#mechanics/goety,#mechanics/ae2,#mechanics/effects,#mechanics/stats') bad.push(`mechanics ${h}: the sub-bar links are ${bar.map(a => a.getAttribute('href')).join()}`);
    if (cur.length !== 1 || cur[0].getAttribute('href') !== '#mechanics/' + want) bad.push(`mechanics ${h}: the open tab is ${cur.map(a => a.getAttribute('href')).join() || 'none'}`);
    if (!document.title.startsWith(document.querySelector('nav.nav a[href="#mechanics"]').textContent.trim())) bad.push(`mechanics ${h}: title ${document.title}`);
    if (document.querySelectorAll('nav.nav a[aria-current]').length !== 1 || document.querySelector('nav.nav a[aria-current]').getAttribute('href') !== '#mechanics') bad.push(`mechanics ${h}: the header marks ${[...document.querySelectorAll('nav.nav a[aria-current]')].map(a => a.getAttribute('href')).join() || 'no tab'}`);
    if (h !== '#mechanics/nonsense' && !m().querySelector('.crumb')?.textContent.includes(bar.find(a => a.getAttribute('href') === '#mechanics/' + want).textContent.trim())) bad.push(`mechanics ${h}: the breadcrumb does not name the page`); }
  // the header does not grow a tab per section: Mechanics stays one tab
  const tabs = [...document.querySelectorAll('nav.nav a')].map(a => a.getAttribute('href'));
  if (tabs.filter(h => h.startsWith('#mechanics')).length !== 1) bad.push(`mechanics: the header has ${tabs.filter(h => h.startsWith('#mechanics')).length} Mechanics tabs`);
  // a page draws only its own section: the ritual table and the effects table never share a page
  await go('#mechanics/effects'); if (m().querySelector('#rtb')) bad.push('mechanics /effects draws the ritual table');
  await go('#mechanics/goety'); if (!m().querySelector('#rtb tr')) bad.push('mechanics /goety: the ritual table is empty');
  await go('#mechanics/effects'); if (![...m().querySelectorAll('#etb tr')].some(t => /^\s*Bleeding/.test(t.cells[0].textContent))) bad.push('mechanics /effects: no Bleeding row (item pages link to it)');
  await go('#mechanics/stats'); for (const id of ['m-st-hit', 'm-st-armor', 'm-st-summon']) if (!document.getElementById(id)) bad.push('mechanics /stats: no #' + id);
  await go('#mechanics/stats'); for (const a of m().querySelectorAll('.mtabs [data-go]')) if (!document.getElementById(a.dataset.go)) bad.push('mechanics /stats: tab to a missing #' + a.dataset.go);
  await go('#mechanics'); }
// Stats > One hit (2026-11-14): the nine steps as a track and a calculator (app.js hitBoard / hitInit / hitCalc). The calculator's rules are the
// pack's (Linggango Tweaks config, Apothic armor, Linggango Fixes Resistance), so they must say what the page's own text says.
{ const wait = ms => new Promise(r => setTimeout(r, ms)), m = () => document.getElementById('main');
  location.hash = '#mechanics/stats'; await wait(60); render(); await wait(300);
  const near = (a, b, e = 1e-6) => Math.abs(a - b) <= e, txt = m().textContent;
  // the soft cap: "×10 lands as ×5.5" (the page) and "x1000 as x55" (the config's own comment); summary of the rule: knee x sqrt(m / knee)
  if (Math.round(hitCalc(1, 10, 0, 0, 20, false).cm * 10) / 10 !== 5.5) bad.push('one hit: ×10 does not land as ×5.5 (' + hitCalc(1, 10, 0, 0, 20, false).cm + ')');
  if (Math.round(hitCalc(1, 1000, 0, 0, 20, false).cm) !== 55) bad.push('one hit: ×1000 does not land as ×55');
  if (hitCalc(1, 2.5, 0, 0, 20, false).cm !== 2.5) bad.push('one hit: ×2.5 (under the ×3 knee) is changed');
  // Resistance levels: the calculator's table is the one the "Taking damage" table states (I 20% ... X 60%)
  const RN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'];
  for (let i = 1; i <= 10; i++) if (!new RegExp('\\b' + RN[i - 1] + ' ' + Math.round(HIT.res[i] * 100) + '%').test(txt)) bad.push('one hit: Resistance ' + RN[i - 1] + ' is ' + Math.round(HIT.res[i] * 100) + '% in the calculator, not in the page text');
  // armor: A / (A + armor) with A = 10 under 20 and 10 + (hit - 20) / 2 above: the page's table says a 50 hit on 50 armor keeps 33%
  { const c = hitCalc(50, 1, 50, 0, 20, false); if (Math.round(100 * c.s6 / 50) !== 33) bad.push('one hit: 50 damage on 50 armor keeps ' + Math.round(100 * c.s6 / 50) + '%, the table says 33%'); }
  // floor and cap (players only): 13% of the incoming hit, at most half of max health; not a player: neither
  { const big = hitCalc(30, 10, 60, 5, 40, true), low = hitCalc(100, 1, 5000, 10, 1000, true), mob = hitCalc(30, 10, 60, 5, 40, false);
    if (!near(big.s8, 20)) bad.push('one hit: 30 ×10 on armor 60, Resistance V, a 40 HP player lands ' + big.s8 + ', want the cap 20');
    if (!near(low.s8, 13)) bad.push('one hit: a 100 hit through 5000 armor lands ' + low.s8 + ' on a player, want the 13% floor (13)');
    if (!near(mob.s8, mob.s7)) bad.push('one hit: a mob gets the player floor or cap'); }
  if (!/13%/.test(HROWS[7][1]) || !/half your max health/.test(HROWS[7][1]) || !/10% of max health/.test(HROWS[8][1]) || HIT.floor !== .13 || HIT.cap !== .5) bad.push('one hit: the floor, cap or lifesteal rule in the text and in HIT disagree');
  // the board: nine steps, each opens its own rule; every slider position gives numbers
  const st = [...m().querySelectorAll('.hb-st')];
  if (st.length !== 9) bad.push('one hit: ' + st.length + ' steps, want 9');
  for (const [i, b] of st.entries()) { b.click(); await wait(10);
    if (!document.getElementById('hbdet').textContent.includes(T(HROWS[i][1]).replace(/<[^>]+>/g, '').slice(0, 30))) bad.push('one hit: step ' + (i + 1) + ' does not show its rule');
    if (b.getAttribute('aria-pressed') !== 'true') bad.push('one hit: step ' + (i + 1) + ' is not marked pressed'); }
  const set = (id, v) => { const e = document.getElementById(id); if (e.type === 'checkbox') e.checked = v; else e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); };
  for (const [b, mm, a, r, h, p] of [[1, 10, 0, 0, 20, true], [100, 100, 100, 10, 200, true], [100, 100, 0, 0, 20, false], [1, 100, 100, 10, 200, false]]) {
    set('hbb', b); set('hbm', mm); set('hba', a); set('hbr', r); set('hbh', h); set('hbp', p); await wait(10);
    const t = document.querySelector('.hitb').textContent;
    if (/NaN|Infinity|undefined|\{\w+\}/.test(t)) bad.push(`one hit: ${[b, mm, a, r, h, p]} prints NaN, Infinity, undefined or a placeholder`);
    if (document.getElementById('hbout').textContent !== nL(Math.round(hitCalc(b, mm / 10, a, r, h, p).s8 * 10) / 10)) bad.push(`one hit: ${[b, mm, a, r, h, p]} shows ${document.getElementById('hbout').textContent}`); }
  // the old table is still there for readers who want all nine steps at once
  if (m().querySelectorAll('.hb-tab tr').length !== 10) bad.push('one hit: the table view has ' + m().querySelectorAll('.hb-tab tr').length + ' rows, want 10');
  location.hash = '#mechanics'; await wait(60); render(); }
