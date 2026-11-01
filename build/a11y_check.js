// Checks that need more than the page's data (Chromium, no network): a fresh load per route, a second viewport or a touch screen,
// saved storage injected before the scripts run, real key presses and taps, paint and layout-shift timing, contrast and the
// accessibility tree. Run by check.sh after style_check.js (about 90 s).
// Usage: NODE_PATH=$(npm root -g) node build/a11y_check.js [dist/Linggango_Relic_Wiki.html]
// Each block names the audit finding (2026-10-31) it guards; fails (exit 1) on any of them or a script error.
const { chromium } = require('playwright'), path = require('path');
(async () => {
  const b = await chromium.launch(), URL = 'file://' + path.resolve(process.argv[2] || 'dist/Linggango_Relic_Wiki.html'), bad = [], errs = [], T0 = Date.now();
  const drawn = p => p.waitForFunction(() => { const m = document.getElementById('main'); return m && !m.querySelector('.boot') && m.innerText.length > 40; }, null, { timeout: 20000 }).catch(() => {});
  // a fresh context and page on route h; init: functions run before the page's scripts
  const open = async (h = '', opt = {}, ...init) => { const c = await b.newContext({ viewport: { width: 1440, height: 900 }, ...opt });
    for (const [f, a] of init) await c.addInitScript(f, a);
    const p = await c.newPage(); p.on('pageerror', e => errs.push((h || '#') + ': ' + e.message)); await p.goto(URL + h, { waitUntil: 'load' }); await drawn(p); return [c, p]; };
  const nav = async (p, h, ms = 400) => { await p.evaluate(h => { location.hash = h }, h); await p.waitForTimeout(ms); };
  const step = (n, t) => console.log(`  ${n}: ${((Date.now() - t) / 1000).toFixed(1)} s`);
  let t = Date.now();

  // a11y-perf-10: the Google Fonts hosts never hold the first paint (it waited 3.3-3.7 s on them)
  { const [c] = await Promise.all([b.newContext({ viewport: { width: 1440, height: 900 } })]);
    await c.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//, async r => { await new Promise(x => setTimeout(x, 3000)); await r.abort().catch(() => {}); });
    await c.addInitScript(() => { window.__fcp = null; new PerformanceObserver(l => { for (const e of l.getEntries()) if (e.name === 'first-contentful-paint') window.__fcp = e.startTime; }).observe({ type: 'paint', buffered: true }); });
    const p = await c.newPage(); await p.goto(URL + '#', { waitUntil: 'commit' });
    await p.waitForFunction(() => window.__fcp !== null, null, { timeout: 10000 }).catch(() => {});
    const fcp = await p.evaluate(() => window.__fcp);
    if (!(fcp < 1500)) bad.push(`fonts host delayed 3 s: first contentful paint ${fcp === null ? 'never' : Math.round(fcp) + ' ms'} (limit 1500 ms)`);
    await c.close(); }
  step('first paint', t); t = Date.now();

  // a11y-perf-01: the body classes the boot script in template.html sets before the first paint are the ones render() leaves, so the
  // shell does not jump when <main> is filled; and the first draw's layout shift stays under 0.1 (it was 0.2-0.9)
  { const KEEP = ['hub', 'noside', 'qbg', 'gearv'], CLS = new Set(['#', '#home', '#gear', '#build', '#act/5']), f = s => KEEP.filter(k => (s || '').split(/\s+/).includes(k)).join(' ');
    for (const h of ['#', '#home', '#gear', '#gs50', '#build', '#bosses', '#boss/nyxaris', '#side/Frostmaw', '#mechanics', '#act/5', '#i0']) {   // one route per body-class rule
      const [c, p] = await open(h, {}, [() => document.addEventListener('DOMContentLoaded', () => { window.__boot = document.body.className; })],
        [() => { window.__cls = 0; new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({ type: 'layout-shift', buffered: true }); }]);
      if (CLS.has(h)) await p.waitForTimeout(1500);
      const { boot, now, cls } = await p.evaluate(() => ({ boot: window.__boot, now: document.body.className, cls: window.__cls }));
      if (f(boot) !== f(now)) bad.push(`boot classes ${h}: before the first draw "${f(boot)}", after "${f(now)}"`);
      if (CLS.has(h) && cls > 0.1) bad.push(`layout shift ${h}: ${cls.toFixed(3)} (limit 0.1)`);
      await c.close(); } }
  step('boot classes and layout shift', t); t = Date.now();

  // one page at 1440 px for the keyboard, focus and contrast checks
  const [C, P] = await open('#gear/5/ME/w');
  // app-logic-08 / a11y-perf-04: switching a playstyle on Equipment keeps the scroll and the focus; #gear from Curios opens at the top
  { await P.evaluate(() => scrollTo(0, document.querySelector('.gbar').getBoundingClientRect().top + scrollY - 100)); const y0 = await P.evaluate(() => scrollY);
    await P.click('.gseg.roles a[href="#gear/5/MA/w"]'); await P.waitForTimeout(400);
    const [y1, href] = await P.evaluate(() => [scrollY, document.activeElement.getAttribute('href')]);
    if (Math.abs(y1 - y0) > 1) bad.push(`gear switch scrolled ${y0} -> ${y1}`); if (href !== '#gear/5/MA/w') bad.push('gear switch focus on ' + href);
    await nav(P, '#home', 300); await P.evaluate(() => { scrollTo(0, 900); location.hash = '#gear'; }); await P.waitForTimeout(400);
    if (await P.evaluate(() => scrollY) !== 0) bad.push('#gear from #home not at the top'); }
  // css (a11y-perf): text on the stone buttons and tabs, the chips' counts and the quick-search group labels reach 4.5:1
  { const CON = ([sel, back]) => {
      const lum = c => { const [r, g, b] = c.match(/[\d.]+/g).slice(0, 3).map(v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }); return .2126 * r + .7152 * g + .0722 * b; };
      const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
      const bg = e => { for (; e; e = e.parentElement) { const c = getComputedStyle(e).backgroundColor; if (!/rgba\(.*, 0\)|transparent/.test(c)) return c; } return 'rgb(255, 255, 255)'; };
      const xs = [...document.querySelectorAll(sel)].filter(e => e.getClientRects().length && e.textContent.trim()); if (!xs.length) return `contrast: no ${sel} text to test on ${location.hash}`;
      for (const e of xs.slice(0, 5)) { const k = ratio(getComputedStyle(e).color, back || bg(e)); if (k < 4.5) return `contrast ${sel} ${k.toFixed(2)}:1 on ${location.hash}`; } return ''; };
    const STONE = 'rgb(111, 111, 111)';   // the stone button texture's mean colour
    for (const [h, sel, back] of [['#boss/arion', '.pnx a small', STONE], ['#', '.pbtn a.mcb', STONE], ['#mechanics', '.mtabs a', STONE], ['#home', '.chip .n'], ['#', '#qs .qg em']]) {
      await nav(P, h, 500); if (sel.startsWith('#qs')) { await P.click('#q'); await P.keyboard.type('ring'); await P.waitForTimeout(400); }
      const m = await P.evaluate(CON, [sel, back]); if (m) bad.push(m);
      if (sel.startsWith('#qs')) { await P.fill('#q', ''); await P.keyboard.press('Escape'); } } }
  // css (a11y-perf): keyboard focus on The Path's first Act tile is visible (the focused and the blurred tile differ by 15+ pixels)
  { await nav(P, '', 600); await P.evaluate(() => scrollTo(0, 0)); await P.focus('.skip');   // Tab from the top of the page
    let ok = false; for (let i = 0; i < 60 && !ok; i++) { await P.keyboard.press('Tab'); ok = await P.evaluate(() => document.activeElement.id === 'pn-0'); }
    if (!ok) bad.push('Tab never reaches #pn-0 (focus ends on ' + await P.evaluate(() => document.activeElement.outerHTML.slice(0, 80)) + ')'); else {
      await P.waitForTimeout(300); const box = await P.evaluate(() => { const r = document.activeElement.getBoundingClientRect(); return { x: Math.max(0, r.x - 6), y: Math.max(0, r.y - 6), width: r.width + 12, height: r.height + 12 }; });
      const a = await P.screenshot({ clip: box }); await P.evaluate(() => document.activeElement.blur()); await P.waitForTimeout(300); const z = await P.screenshot({ clip: box });
      const n = await P.evaluate(async ([a, z]) => { const px = async s => { const i = new Image(); i.src = 'data:image/png;base64,' + s; await i.decode(); const c = new OffscreenCanvas(i.width, i.height).getContext('2d'); c.drawImage(i, 0, 0); return c.getImageData(0, 0, i.width, i.height).data; };
        const [x, y] = [await px(a), await px(z)]; let n = 0; for (let j = 0; j < x.length; j += 4) if (Math.abs(x[j] - y[j]) + Math.abs(x[j + 1] - y[j + 1]) + Math.abs(x[j + 2] - y[j + 2]) > 30) n++; return n; }, [a.toString('base64'), z.toString('base64')]);
      if (n < 15) bad.push(`focus on #pn-0 is invisible: ${n} pixels change`); } }
  // a11y-perf-04: keyboard focus survives the planner's redraws
  { await nav(P, '#build', 800);
    for (const s of ['[data-preset]', '#bclr', '[data-preset]', '.bslots [data-rm]']) {   // the last: a preset can overfill a slot, so no + appears if (!await P.$(s)) { bad.push('#build: no ' + s); continue; }
      await P.focus(s); await P.keyboard.press('Enter'); await P.waitForTimeout(150);
      if (!await P.evaluate(() => document.activeElement !== document.body && document.getElementById('main').contains(document.activeElement))) bad.push('#build: Enter on ' + s + ' drops focus to body'); } }
  // Mechanics stays light (under 5,000 nodes, no task over 200 ms) and its ritual filter finds what the data has (a11y-perf)
  { await P.evaluate(() => { window.__lt = []; new PerformanceObserver(l => l.getEntries().forEach(e => window.__lt.push(e.duration))).observe({ type: 'longtask' }); });
    for (const h of ['#mechanics', '#mechanics/stats']) { await nav(P, h, 1200);
      const r = await P.evaluate(() => { const r = { n: document.querySelectorAll("#main *").length, lt: Math.max(0, ...window.__lt) }; window.__lt = []; return r; });
      if (r.n >= 5000) bad.push(`${h}: #main has ${r.n} nodes (limit 5000)`); if (r.lt > 200) bad.push(`${h}: long task ${Math.round(r.lt)} ms`); }
    await nav(P, '#mechanics', 800); await P.fill('#rq', 'soul'); await P.waitForTimeout(300);
    for (let i = 0; i < 50 && await P.$('#rmore button'); i++) { await P.click('#rmore button'); await P.waitForTimeout(100); }
    const m = await P.evaluate(() => [document.querySelectorAll('#rtb tr').length, GOETY.rituals.filter(r => (r.out + ' ' + r.act + ' ' + r.ings.join(' ')).toLowerCase().includes('soul')).length]);
    if (m[0] !== m[1]) bad.push(`ritual filter 'soul': ${m[0]} rows, data has ${m[1]}`);
    // every control on Mechanics has an accessible name (Chromium's own tree)
    await P.fill('#rq', ''); const cdp = await C.newCDPSession(P), { nodes } = await cdp.send('Accessibility.getFullAXTree');
    for (const n of nodes) if (!n.ignored && ['combobox', 'textbox', 'searchbox', 'button', 'listbox'].includes(n.role?.value) && !n.name?.value?.trim()) bad.push('#mechanics: unnamed ' + n.role.value); }
  await C.close();
  step('keyboard, focus, contrast, Mechanics', t); t = Date.now();

  // app-logic-04/05/12, a11y-perf-06: counts that link to Curios are the counts Curios shows, saved filters included; Enter in the header
  // box applies it; '/' types inside a box and focuses the search box elsewhere
  { const [c, q] = await open('#bosses');
    await q.evaluate(() => { Object.assign(st, { c: [], g: [], x: [], m: '', s: '', a: '', q: '', nw: false, r: ['5'] }); el('q').value = ''; });
    await q.click('#q'); await q.keyboard.type('ring'); await q.waitForTimeout(400);
    bad.push(...await q.evaluate(() => { const t = document.querySelector('#qs .qall b')?.textContent || '', n = +(t.match(/\d+/) || [])[0], s = st.q; st.q = 'ring'; const want = D.filter(d => pass(d)).length; st.q = s;
      return n === want ? [] : [`quick search row '${t}' but Curios shows ${want}`]; }));
    await q.keyboard.press('Escape');
    await nav(q, '#i' + await q.evaluate(() => D.find(d => d.sl[0] === 'Ring').ix), 1200);
    const lbl = await q.evaluate(() => document.querySelector('.sib h2 a')?.textContent || ''); await q.click('.sib h2 a'); await q.waitForTimeout(1200);
    bad.push(...await q.evaluate(lbl => { const n = +(lbl.match(/\d+/) || [])[0], got = D.filter(d => pass(d)).length, fn = document.querySelector('.fn')?.textContent || '';
      return n === got && fn.startsWith(String(got)) ? [] : [`curio page '${lbl}' lands on ${got} (${fn})`]; }, lbl));
    await q.evaluate(() => { st.r = []; st.q = ''; location.hash = '#bosses'; }); await q.waitForTimeout(1000);
    await q.fill('#q', ''); await q.click('#q'); await q.keyboard.type('ring'); await q.waitForTimeout(300); await q.keyboard.press('Escape'); await q.keyboard.press('Enter'); await q.waitForTimeout(1200);
    bad.push(...await q.evaluate(() => { const fn = document.querySelector('.fn')?.textContent || '', n = D.filter(d => pass(d)).length;
      return st.q === 'ring' && location.hash === '#home' && fn.startsWith(n + ' of') ? [] : [`header Enter: st.q '${st.q}', ${location.hash}, '${fn}' (want ring, #home, ${n})`]; }));
    await q.fill('#fq', ''); await q.click('#fq'); await q.keyboard.type('a/b'); await q.waitForTimeout(400);
    bad.push(...await q.evaluate(() => el('fq').value === 'a/b' && document.activeElement.id === 'fq' ? [] : [`typing a/b in #fq gave '${el('fq').value}', focus #${document.activeElement.id}`]));
    await q.evaluate(() => document.activeElement.blur()); await q.keyboard.press('/');
    bad.push(...await q.evaluate(() => document.activeElement.id === 'q' ? [] : [`'/' on the page focuses #${document.activeElement.id}, not #q`]));
    await c.close(); }
  // app-logic-03: 'I'm here' redraws Continue and closes the Acts opened by hand
  { const [c, p] = await open('#', {}, [() => { if (!sessionStorage.s) { sessionStorage.s = 1; localStorage.setItem('lgw2', '{"op":[9,2]}'); localStorage.setItem('lgw-here', '9'); } }]);
    await p.evaluate(() => { const t = [...document.querySelectorAll('.pn')].find(x => x.textContent.trim() === 'XI'); t && t.click(); }); await p.waitForTimeout(300);
    if (!await p.$('.phere[data-here="11"]')) bad.push("no I'm here button for Act XI"); else {
      await p.click('.phere[data-here="11"]'); const tb = await p.textContent('.tbtns');
      if (!/Continue: Act XI/.test(tb)) bad.push('I\'m here: .tbtns not redrawn: ' + tb.trim().slice(0, 60));
      await p.click('.tbtns a.wide'); await p.waitForTimeout(800); const op = await p.evaluate(() => ORDER.filter(a => tierOpen(a)));
      if (op.join() !== '11') bad.push('Continue Act XI opens ' + op.join()); }
    await c.close(); }
  // app-logic-14: a bad saved value falls back key by key (no error, a title, The Path still opens an Act)
  for (const [k, v] of [['lgw2', '{"c":"ME"}'], ['lgw2', '{"op":5}'], ['lgw2', '{"r":"5"}'], ['lgw2', '{"a":"zz"}'], ['lgw2', '{"q":5}'], ['lgw-recent', '{}'], ['lgw-here', '6.1']]) {
    const n = errs.length, [c, p] = await open('#', {}, [([k, v]) => localStorage.setItem(k, v), [k, v]]);
    const r = await p.evaluate(() => ({ h1: !!document.querySelector('#main h1'), open: ORDER.filter(a => tierOpen(a)).length }));
    await nav(p, '#home', 300); if (k === 'lgw-recent') await nav(p, '#i5', 300);
    if (errs.length > n || !r.h1 || !r.open || !await p.$('#main h1')) bad.push(`storage ${k}=${v}: errors ${errs.slice(n).join('; ')} h1 ${r.h1} open ${r.open}`);
    await c.close(); }
  // gear-logic-combat-13: a share link with items it cannot place says so; a preset's own link does not
  { const [c, p] = await open('#home'); const dfp = await p.evaluate(() => DFP);
    for (const tail of ['b10n', 'zzz|b2']) { await p.goto(URL + '#build/12/' + dfp + '/' + tail); await p.reload(); await drawn(p); await p.waitForTimeout(300);
      if (!await p.evaluate(() => [...document.querySelectorAll('.bpane .note')].some(x => /could not be placed/.test(x.textContent)))) bad.push('#build/…/' + tail + ': dropped-items note missing'); }
    await p.goto(URL + '#build'); await p.reload(); await drawn(p); await p.click('[data-preset]'); const h = await p.evaluate(() => location.hash);
    await p.goto(URL + '#home'); await p.goto(URL + h); await p.reload(); await drawn(p); await p.waitForTimeout(300);
    if (await p.evaluate(() => [...document.querySelectorAll('.bpane .note')].some(x => /could not be placed|different wiki version/.test(x.textContent)))) bad.push('preset share link shows a dropped/stale note');
    await c.close(); }
  step('search keys, saved state, share links', t); t = Date.now();

  // phone-04: the room heads are painted, wide enough and inside their room at 375, 768, 1024 and 1440 px
  { const [c, p] = await open('#home');
    for (const vw of [375, 768, 1024, 1440]) { await p.setViewportSize({ width: vw, height: 900 });
      for (const r of ['#home', '#gear', '#build', '#bosses', '#mechanics']) { await nav(p, r, 300);
        await p.waitForFunction(() => [...document.querySelectorAll('.room3.rhd')].filter(e => e.offsetParent).every(e => e.dataset.p), null, { timeout: 10000 }).catch(() => {});
        const m = await p.evaluate(() => [...document.querySelectorAll('.room3.rhd')].filter(e => e.offsetParent).map(el => { const h = el.querySelector('.rhead'), R = el.getBoundingClientRect(), H = h.getBoundingClientRect(), w = parseFloat(h.style.width);
          return { painted: !!el.dataset.p, ok: w >= 240 || w >= el.clientWidth - 40, w: h.style.width, cw: el.clientWidth, over: Math.round(H.bottom - (R.bottom - parseFloat(getComputedStyle(el).borderBottomWidth))) }; }));
        if (!m.length) bad.push(`${r} at ${vw}px: no visible .room3.rhd`);
        for (const x of m) { if (!x.painted) bad.push(`${r} at ${vw}px: room not painted`); else { if (!x.ok) bad.push(`${r} at ${vw}px: room head width '${x.w}' (room ${x.cw}px)`); if (x.over > 0) bad.push(`${r} at ${vw}px: room head ${x.over}px below the room`); } } } }
    await c.close(); }
  // phone-05: the planner's picker and inspector come into view on narrow screens
  for (const w of [375, 800]) { const [c, p] = await open('#build', { viewport: { width: w, height: 740 }, hasTouch: true, isMobile: w === 375 });
    const io = s => p.evaluate(s => { const r = document.querySelector(s)?.getBoundingClientRect(); return !!r && r.bottom > 0 && r.top < innerHeight; }, s);
    await p.tap('[data-pick=Head]'); await p.waitForTimeout(200); if (!await io('.bpick')) bad.push(`#build ${w}px: .bpick off screen after tapping +`);
    await p.tap('[data-preset]'); await p.tap('.bslots [data-insp]'); await p.waitForTimeout(200); if (!await io('.binsp')) bad.push(`#build ${w}px: .binsp off screen after inspecting`);
    await c.close(); }
  // phone-19: on a touch screen (the tooltip is off under hover:none) no visible lede, note or paragraph says to hover
  { const [c, p] = await open('#home', { viewport: { width: 375, height: 800 }, hasTouch: true, isMobile: true });
    for (const h of ['#home', '#build', '#mechanics', '#mechanics/stats']) { await nav(p, h, 400);
      for (const x of await p.evaluate(() => [...document.querySelectorAll('#main .lede,#main .note,#main p')].filter(e => e.offsetParent && /\bhover\b/i.test(e.innerText)).map(e => e.innerText.slice(0, 60)))) bad.push(`hover on touch ${h}: ${x}`); }
    await c.close(); }
  // css (a11y-perf): with reduced motion asked for, nothing animates for ever
  { const [c, p] = await open('#', { reducedMotion: 'reduce' });
    for (const h of ['#', '#gear', '#bosses']) { await nav(p, h, 1500);
      for (const x of await p.evaluate(() => document.getAnimations().filter(a => a.playState === 'running' && a.effect?.getComputedTiming().iterations === Infinity).map(a => (a.animationName || a.constructor.name) + ' on ' + (a.effect.target?.className || a.effect.target?.tagName)))) bad.push(`reduced motion ${h}: ${x} runs for ever`); }
    await c.close(); }
  step('viewports, touch, reduced motion', t);

  await b.close();
  console.log(`a11y and timing checks: ${bad.length} broken ${bad.slice(0, 8).join(' | ')}`);
  console.log(`script errors: ${errs.length} ${errs.slice(0, 3).join(' | ')}  (${((Date.now() - T0) / 1000).toFixed(0)} s)`);
  process.exit(bad.length || errs.length ? 1 : 0);
})();
