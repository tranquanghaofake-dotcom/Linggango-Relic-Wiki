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
  await b.close();
  console.log(`site: ${st.scripts} scripts, app ${st.app ? 'started' : 'NOT started'}, ${st.gear} gear items, ` +
    `home page ${st.text} chars, ${failed.length} missing files, ${errs.length} script errors`);
  [...failed, ...errs].slice(0, 10).forEach(x => console.log('  ' + x));
  process.exit(!errs.length && !failed.length && st.app && st.gear > 0 && st.text > 40 ? 0 : 1);
})();
