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
  const vi = await q.evaluate(() => ({ lang: document.documentElement.lang, nav: document.querySelector('[data-lg="nav.gear"]').textContent, want: window.I18N.vi && I18N.vi['nav.gear'] }));
  const r = await b.newPage({ viewport: { width: 1400, height: 900 } }), rerr = [];
  r.on('pageerror', e => rerr.push(e.message)); await r.route(/lang-vi\./, x => x.abort());
  await r.goto(url + '?lang=vi', { waitUntil: 'load' }); await r.waitForTimeout(2500);
  const nopack = await r.evaluate(() => ({ lang: document.documentElement.lang, app: typeof render === 'function', text: (document.getElementById('main')?.innerText || '').length }));
  await b.close();
  const langOk = vi.lang === 'vi' && !!vi.want && vi.nav === vi.want && nopack.lang === 'en' && nopack.app && nopack.text > 40 && !rerr.length;
  console.log(`site: ${st.scripts} scripts, app ${st.app ? 'started' : 'NOT started'}, ${st.gear} gear items, ` +
    `home page ${st.text} chars, ${failed.length} missing files, ${errs.length} script errors; ` +
    `language pack ${langOk ? 'loads, and a missing pack leaves English' : 'FAILED ' + JSON.stringify({ vi, nopack, rerr })}`);
  [...failed, ...errs].slice(0, 10).forEach(x => console.log('  ' + x));
  process.exit(!errs.length && !failed.length && st.app && st.gear > 0 && st.text > 40 && langOk ? 0 : 1);
})();
