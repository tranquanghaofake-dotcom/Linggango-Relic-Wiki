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
  // the header does not grow a tab per section: the six main tabs stay (Spells joins them when that page lands, in its own change)
  const tabs = [...document.querySelectorAll('nav.nav a')].map(a => a.getAttribute('href'));
  if (tabs.filter(h => h.startsWith('#mechanics')).length !== 1) bad.push(`mechanics: the header has ${tabs.filter(h => h.startsWith('#mechanics')).length} Mechanics tabs`);
  // a page draws only its own section: the ritual table and the effects table never share a page
  await go('#mechanics/effects'); if (m().querySelector('#rtb')) bad.push('mechanics /effects draws the ritual table');
  await go('#mechanics/goety'); if (!m().querySelector('#rtb tr')) bad.push('mechanics /goety: the ritual table is empty');
  await go('#mechanics/effects'); if (!m().querySelector('#eff-bleeding')) bad.push('mechanics /effects: no Bleeding row (item pages link to it)');
  await go('#mechanics/stats'); for (const id of ['m-st-hit', 'm-st-armor', 'm-st-summon']) if (!document.getElementById(id)) bad.push('mechanics /stats: no #' + id);
  await go('#mechanics/stats'); for (const a of m().querySelectorAll('.mtabs [data-go]')) if (!document.getElementById(a.dataset.go)) bad.push('mechanics /stats: tab to a missing #' + a.dataset.go);
  await go('#mechanics'); }
