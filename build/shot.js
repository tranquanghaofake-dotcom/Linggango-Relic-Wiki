// Screenshots of wiki routes from the built site, to look at a change before committing (cloud sessions have no screen).
// Usage: node build/shot.js '#home' '#gear' '#g12' [--width 1440] [--out /tmp/wiki-shots]   (run from the repo root, after a build)
// Prints one PNG path per route; exits 1 if a script error happened while drawing them.
const path = require('path'), fs = require('fs');
const { chromium } = (() => { try { return require('playwright'); } catch { // global install, no NODE_PATH needed
  return require(path.join(require('child_process').execSync('npm root -g').toString().trim(), 'playwright')); } })();
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : d; };
const out = opt('--out', '/tmp/wiki-shots'), width = +opt('--width', 1440);
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve('index.html'), { waitUntil: 'load' });
  await p.waitForTimeout(1500);
  for (const h of args.length ? args : ['#home']) {
    await p.evaluate(h => { location.hash = h; if (typeof render === 'function') render(); }, h);
    await p.waitForTimeout(800);
    const f = path.join(out, (h.replace(/[^\w-]+/g, '_').replace(/^_+/, '') || 'home') + `_${width}.png`);
    await p.screenshot({ path: f });
    console.log(f);
  }
  await b.close();
  if (errs.length) { console.log('script errors:', errs.slice(0, 5)); process.exit(1); }
})();
