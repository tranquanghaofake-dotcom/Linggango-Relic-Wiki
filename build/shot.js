// Screenshots of wiki routes from the built site, to look at a change before committing (cloud sessions have no screen).
// Usage: node build/shot.js '#home' '#gear' '#g12' [--width 1440] [--out /tmp/wiki-shots] [--diff DIR [--tol 2]]   (run from the repo root, after a build)
// Prints one PNG path per route; exits 1 if a script error happened while drawing them.
// --diff DIR compares each shot with the file of the same name in DIR (shots of an earlier build: check out the old
// commit, build, shoot into DIR) and writes <name>.diff.png (changed pixels red over a dimmed copy) with the share of
// pixels that changed; motion is turned off (prefers-reduced-motion, which stops every effect) so only real changes count,
// and a pixel counts as changed only past --tol (default 2) on some channel: Chromium's text compositing wobbles by 1.
const path = require('path'), fs = require('fs');
const { chromium } = (() => { try { return require('playwright'); } catch { // global install, no NODE_PATH needed
  return require(path.join(require('child_process').execSync('npm root -g').toString().trim(), 'playwright')); } })();
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : d; };
const out = opt('--out', '/tmp/wiki-shots'), width = +opt('--width', 1440), base = opt('--diff', null), tol = +opt('--tol', 2);
const b64 = f => 'data:image/png;base64,' + fs.readFileSync(f).toString('base64');
async function diff(page, a, b, f) {   // in the browser: no image library needed
  const r = await page.evaluate(async ([A, B, T]) => {
    const load = s => new Promise((ok, no) => { const i = new Image(); i.onload = () => ok(i); i.onerror = no; i.src = s; });
    const [x, y] = await Promise.all([load(A), load(B)]);
    const w = Math.max(x.width, y.width), h = Math.max(x.height, y.height);
    const px = i => { const c = new OffscreenCanvas(w, h).getContext('2d'); c.drawImage(i, 0, 0); return c.getImageData(0, 0, w, h).data; };
    const X = px(x), Y = px(y), o = new ImageData(w, h); let d = 0;
    for (let i = 0; i < X.length; i += 4) {
      if (Math.max(Math.abs(X[i] - Y[i]), Math.abs(X[i + 1] - Y[i + 1]), Math.abs(X[i + 2] - Y[i + 2]), Math.abs(X[i + 3] - Y[i + 3])) > T) { d++; o.data[i] = 255; o.data[i + 3] = 255; }
      else { const g = (X[i] + X[i + 1] + X[i + 2]) / 9; o.data[i] = o.data[i + 1] = o.data[i + 2] = g; o.data[i + 3] = 255; }
    }
    const c = new OffscreenCanvas(w, h); c.getContext('2d').putImageData(o, 0, 0);
    const blob = await c.convertToBlob();
    const url = await new Promise(ok => { const fr = new FileReader(); fr.onload = () => ok(fr.result); fr.readAsDataURL(blob); });
    return { d, n: w * h, png: url.split(',')[1] };
  }, [b64(a), b64(b), tol]);
  fs.writeFileSync(f, Buffer.from(r.png, 'base64'));
  return r;
}
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width, height: 900 } });
  if (base) await p.emulateMedia({ reducedMotion: 'reduce' });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve('index.html'), { waitUntil: 'load' });
  await p.waitForTimeout(1500);
  let changed = 0;
  for (const h of args.length ? args : ['#home']) {
    await p.evaluate(h => { location.hash = h; if (typeof render === 'function') render(); }, h);
    await p.waitForTimeout(800);
    const f = path.join(out, (h.replace(/[^\w-]+/g, '_').replace(/^_+/, '') || 'home') + `_${width}.png`);
    await p.screenshot({ path: f });
    console.log(f);
    if (!base) continue;
    const g = path.join(base, path.basename(f));
    if (!fs.existsSync(g)) { console.log('  no baseline', g); continue; }
    const q = await b.newPage(), r = await diff(q, f, g, f.replace(/\.png$/, '.diff.png')); await q.close();
    if (r.d) changed++;
    console.log(`  ${r.d ? (100 * r.d / r.n).toFixed(3) + '% of pixels changed → ' + f.replace(/\.png$/, '.diff.png') : 'same pixels as the baseline'}`);
  }
  await b.close();
  if (base) console.log(`${changed} of ${args.length || 1} routes changed`);
  if (errs.length) { console.log('script errors:', errs.slice(0, 5)); process.exit(1); }
})();
