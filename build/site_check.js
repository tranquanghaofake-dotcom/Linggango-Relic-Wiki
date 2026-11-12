// Smoke test of the deployable site: index.html + the content-hashed static/ files, i.e. what GitHub Pages serves.
// check.js walks every page of the offline single file; this makes sure the split build loads the same way:
// every script and stylesheet is found, nothing throws, and the app starts and draws the home page.
// Usage: node build/site_check.js [index.html]   (check.sh runs it)
const path = require('path');
const { chromium } = (() => { try { return require('playwright'); } catch { // global install, no NODE_PATH needed
  return require(path.join(require('child_process').execSync('npm root -g').toString().trim(), 'playwright')); } })();
(async () => {
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1400, height: 900 } });
  const errs = [], failed = [];
  p.on('pageerror', e => errs.push(e.message));
  p.on('requestfailed', r => failed.push(r.url() + ' (' + (r.failure()?.errorText || 'failed') + ')'));
  await p.goto('file://' + path.resolve(process.argv[2] || 'index.html'), { waitUntil: 'load' });
  await p.waitForTimeout(2500);
  const st = await p.evaluate(() => ({
    app: typeof render === 'function',
    gear: typeof GE !== 'undefined' ? GE.length : 0,
    scripts: document.querySelectorAll('script[src]').length,
    text: (document.getElementById('main')?.innerText || '').length,
  }));
  // languages: ?lang=vi fetches its pack and draws the shell in it; a pack that cannot be fetched leaves English and nothing breaks
  const url = 'file://' + path.resolve(process.argv[2] || 'index.html');
  const q = await b.newPage({ viewport: { width: 1400, height: 900 } });
  q.on('pageerror', e => errs.push('vi: ' + e.message)); q.on('requestfailed', r => failed.push(r.url() + ' (vi)'));
  await q.goto(url + '?lang=vi', { waitUntil: 'load' }); await q.waitForTimeout(2500);
  const vi = await q.evaluate(async () => ({ lang: document.documentElement.lang, nav: document.querySelector('[data-lg="nav.gear"]').textContent, want: window.I18N.vi && I18N.vi['nav.gear'],
    font: (await document.fonts.load('32px "VT323 vi"', 'Tiếng Việt')).some(f => f.status === 'loaded') }));
  const ru = await b.newPage({ viewport: { width: 1400, height: 900 } });   // the Cyrillic faces are separate files, fetched only for Cyrillic text
  ru.on('pageerror', e => errs.push('ru: ' + e.message)); ru.on('requestfailed', r => failed.push(r.url() + ' (ru)'));
  await ru.goto(url + '?lang=ru', { waitUntil: 'load' }); await ru.waitForTimeout(2000);
  const ruFont = await ru.evaluate(async () => (await document.fonts.load('32px Monocraft', 'Русский')).some(f => f.status === 'loaded' && /U\+400/i.test(f.unicodeRange)));
  // a fresh load straight onto the Equipment list in Russian: the room paints after the longer text wrapped; no wiki error may show (a ResizeObserver notice once did)
  const gp = await b.newPage({ viewport: { width: 1400, height: 900 } }); await gp.goto(url + '?lang=ru#gear/5/ME/w', { waitUntil: 'load' }); await gp.waitForTimeout(2500);
  const ruToast = await gp.evaluate(() => { const e = document.getElementById('jserr'); return e ? e.textContent.slice(0, 120) : ''; });
  const r = await b.newPage({ viewport: { width: 1400, height: 900 } }), rerr = [];
  r.on('pageerror', e => rerr.push(e.message)); await r.route(/lang-vi\./, x => x.abort());
  await r.goto(url + '?lang=vi', { waitUntil: 'load' }); await r.waitForTimeout(2500);
  const nopack = await r.evaluate(() => ({ lang: document.documentElement.lang, app: typeof render === 'function', text: (document.getElementById('main')?.innerText || '').length }));
  // the Act title and side-boss pictures (PIMG) come in the late wiki_pics.js, held back here for a second: a page opened straight onto an Act or a side boss is drawn again when they arrive and shows them,
  // and the hub fills its open Act panel in place, without drawing the hero again (a mark put on the hero before they arrive is still there after)
  const late = [];
  for (const [h, sel] of [['#act/3', '#main .ptitle'], ['#side/Frostmaw', '#main img.sbarena'], ['', '#pp-0 .ptitle']]) {
    const lp = await b.newPage({ viewport: { width: 1400, height: 900 } }); lp.on('pageerror', e => errs.push('late ' + h + ': ' + e.message));
    await lp.route(/wiki_pics\./, async x => { await new Promise(y => setTimeout(y, 1200)); x.continue(); });
    await lp.goto(url + h, { waitUntil: 'domcontentloaded' }); await lp.waitForTimeout(500);
    const before = await lp.evaluate(([sel]) => { const c = document.querySelector('.climb'); if (c) c.dataset.mark = '1'; return typeof PIMG === 'undefined' ? document.querySelectorAll(sel).length : -1; }, [sel]);
    await lp.waitForTimeout(3000);
    const after = await lp.evaluate(([sel]) => ({ n: document.querySelectorAll(sel).length, pimg: typeof PIMG !== 'undefined', mark: !!(document.querySelector('.climb') || {}).dataset?.mark, hub: !!document.querySelector('.climb') }), [sel]);
    if (!after.pimg || !after.n || (after.hub && !after.mark) || before < 0) late.push(`${h || 'hub'}: PIMG ${after.pimg ? 'arrived' : 'never arrived'}, ${before} matches before and ${after.n} after${after.hub && !after.mark ? ', the hero was drawn again' : ''}`);
    await lp.close();
  }
  await b.close();
  const langOk = vi.lang === 'vi' && !!vi.want && vi.nav === vi.want && vi.font && ruFont && nopack.lang === 'en' && nopack.app && nopack.text > 40 && !rerr.length && !ruToast;
  console.log(`site: ${st.scripts} scripts, app ${st.app ? 'started' : 'NOT started'}, ${st.gear} gear items, ` +
    `home page ${st.text} chars, ${failed.length} missing files, ${errs.length} script errors; ` +
    `language pack ${langOk ? 'loads with its fonts, and a missing pack leaves English' : 'FAILED ' + JSON.stringify({ vi, ruFont, nopack, rerr, ruToast })}; ` +
    `late pictures ${late.length ? 'FAILED ' + late.join(' | ') : 'redraw the Act page, the side-boss page and the hub panel in place'}`);
  [...failed, ...errs].slice(0, 10).forEach(x => console.log('  ' + x));
  process.exit(!errs.length && !failed.length && st.app && st.gear > 0 && st.text > 40 && langOk && !late.length ? 0 : 1);
})();
