// Two measurements of the wiki in Chromium.
//
// 1. Load time:  NODE_PATH=$(npm root -g) node build/perf.js --load [--runs 5] [--profile laptop|laptop2|slow|phone] [--root dir]
//    Serves index.html and static/ over http on localhost with gzip level 6 and cache-control max-age=600 (what GitHub Pages sends),
//    loads the home page cold under a network and CPU profile, five times by default, and prints the median of each number plus the
//    largest-contentful-paint element. Profiles: laptop (50 Mbps, 20 ms, CPU 1x), laptop2 (the same, CPU 2x, an office laptop),
//    slow (10 Mbps, 40 ms), phone (1.6 Mbps, 150 ms, CPU 4x, 390 px: kept only so it does not get worse; 3 runs). The container draws
//    in software, so compare runs of the same machine with each other; they are not promises to a reader. Google Fonts are blocked
//    (the container cannot reach them), so the numbers do not include them.
// 2. Frame times: the rest of this header.
// Usage: NODE_PATH=$(npm root -g) node build/perf.js dist/Linggango_Relic_Wiki.html [outdir]
// Measures rAF frame intervals while the page scrolls, hovers tiles and switches views,
// and long tasks (>50 ms) after first paint. Chromium is unthrottled (vsync off) so the
// numbers show how much headroom each frame has against the 8.33 ms budget of 120 Hz.
const { chromium } = require('playwright');
const path = require('path');

const FILE = path.resolve(process.argv[2] || 'dist/Linggango_Relic_Wiki.html');
const OUT = process.argv[3] || null;

const pct = (xs, p) => { const s = [...xs].sort((a, b) => a - b); return s[Math.min(s.length - 1, Math.floor(p / 100 * s.length))] || 0; };
const sum = xs => ({ frames: xs.length, p50: +pct(xs, 50).toFixed(2), p95: +pct(xs, 95).toFixed(2), p99: +pct(xs, 99).toFixed(2), max: +Math.max(0, ...xs).toFixed(2), over8: xs.filter(x => x > 8.34).length });

const median = xs => { const s = [...xs].sort((a, b) => a - b); return s[Math.floor(s.length / 2)]; };
async function loadMode() {
  const http = require('http'), fs = require('fs'), zlib = require('zlib');
  const arg = (n, d) => { const i = process.argv.indexOf('--' + n); return i > 0 ? process.argv[i + 1] : d; };
  const ROOT = path.resolve(arg('root', path.join(__dirname, '..'))), RUNS = +arg('runs', 5), ONLY = arg('profile', '');
  const PROFILES = { laptop: [50, 20, 1, 1440, 900], laptop2: [50, 20, 2, 1440, 900], slow: [10, 40, 1, 1440, 900], phone: [1.6, 150, 4, 390, 800] };
  const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.png': 'image/png', '.webp': 'image/webp', '.txt': 'text/plain' };
  const server = http.createServer((q, r) => {
    let u = decodeURIComponent(q.url.split('?')[0]); if (u === '/') u = '/index.html';
    const f = path.join(ROOT, u); if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.statusCode = 404; return r.end(); }
    const ext = path.extname(f), h = { 'content-type': TYPES[ext] || 'application/octet-stream', 'cache-control': 'max-age=600' }, body = fs.readFileSync(f);
    if (/\.(html|js|css)$/.test(ext)) { h['content-encoding'] = 'gzip'; r.writeHead(200, h); r.end(zlib.gzipSync(body, { level: 6 })); } else { r.writeHead(200, h); r.end(body); }
  }).listen(0);
  const port = server.address().port, b = await chromium.launch(), out = {};
  for (const [name, [mbps, rtt, cpu, vw, vh]] of Object.entries(PROFILES)) {
    if (ONLY && ONLY !== name) continue;
    const runs = name === 'phone' ? Math.min(3, RUNS) : RUNS, rows = [], lcpEl = [];
    for (let i = 0; i < runs; i++) {
      const ctx = await b.newContext({ viewport: { width: vw, height: vh }, colorScheme: 'dark' }), p = await ctx.newPage(), cdp = await ctx.newCDPSession(p);
      await cdp.send('Network.enable'); await cdp.send('Network.emulateNetworkConditions', { offline: false, downloadThroughput: mbps * 125000, uploadThroughput: mbps * 62500, latency: rtt });
      await cdp.send('Emulation.setCPUThrottlingRate', { rate: cpu }); await cdp.send('Performance.enable');
      await p.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
      await p.addInitScript(() => {
        window.__lt = []; window.__lcp = [0, ''];
        try { new PerformanceObserver(l => l.getEntries().forEach(e => __lt.push(e.duration))).observe({ type: 'longtask', buffered: true }); } catch (e) {}
        try { new PerformanceObserver(l => l.getEntries().forEach(e => { const el = e.element; __lcp = [Math.round(e.startTime), el ? el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.className && el.className.baseVal === undefined ? '.' + String(el.className).trim().split(/\s+/).join('.') : '') : e.url.slice(0, 40)]; })).observe({ type: 'largest-contentful-paint', buffered: true }); } catch (e) {}
      });
      await p.goto(`http://localhost:${port}/`, { waitUntil: 'load', timeout: 300000 }); await p.waitForTimeout(1500);
      const m = Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.map(x => [x.name, x.value]));
      const r = await p.evaluate(() => { const n = performance.getEntriesByType('navigation')[0], paint = Object.fromEntries(performance.getEntriesByType('paint').map(e => [e.name, e.startTime]));
        const kb = performance.getEntriesByType('resource').reduce((a, e) => a + e.transferSize, 0) / 1024;
        return { fcp: paint['first-contentful-paint'], lcp: __lcp[0], lcpEl: __lcp[1], dcl: n.domContentLoadedEventEnd, load: n.loadEventEnd, kb, long: __lt.length, maxLong: Math.max(0, ...__lt), tbt: __lt.reduce((a, d) => a + Math.max(0, d - 50), 0) }; });
      rows.push({ ...r, script: m.ScriptDuration * 1000, style: m.RecalcStyleDuration * 1000, layout: m.LayoutDuration * 1000, task: m.TaskDuration * 1000, heap: m.JSHeapUsedSize / 1048576 });
      lcpEl.push(r.lcpEl); await ctx.close();
    }
    const med = k => Math.round(median(rows.map(x => x[k])));
    out[name] = { runs, fcp: med('fcp'), lcp: med('lcp'), dcl: med('dcl'), load: med('load'), kb: med('kb'), longTasks: med('long'), maxLongMs: med('maxLong'), tbt: med('tbt'), scriptMs: med('script'), styleMs: med('style'), layoutMs: med('layout'), taskMs: med('task'), heapMB: med('heap'), lcpElement: [...new Set(lcpEl)].join(' | '), lcpSpread: [Math.min(...rows.map(x => x.lcp)), Math.max(...rows.map(x => x.lcp))].map(Math.round) };
    console.log(name, JSON.stringify(out[name]));
  }
  await b.close(); server.close();
  return out;
}

if (process.argv.includes('--load')) { loadMode().then(() => process.exit(0)); return; }
(async () => {
  const b = await chromium.launch({ args: ['--disable-gpu-vsync', '--disable-frame-rate-limit', '--enable-gpu-rasterization', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1, colorScheme: 'dark' });
  const errors = [];
  p.on('pageerror', e => errors.push(e.message));
  p.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await p.addInitScript(() => {
    window.__lt = [];
    try { new PerformanceObserver(l => l.getEntries().forEach(e => window.__lt.push(e.duration))).observe({ type: 'longtask', buffered: true }); } catch (e) {}
    window.__rec = (ms) => new Promise(res => { const xs = []; let last = performance.now(); const t0 = last; const f = (t) => { xs.push(t - last); last = t; if (t - t0 < ms) requestAnimationFrame(f); else res(xs.slice(2)); }; requestAnimationFrame(f); });
  });
  const t0 = Date.now();
  await p.goto('file://' + FILE, { waitUntil: 'load' });
  const loadMs = Date.now() - t0;
  await p.waitForTimeout(1500);
  const res = { loadMs };
  const measure = async (name, action, ms = 3000) => {
    const rec = p.evaluate(m => window.__rec(m), ms);
    await action();
    res[name] = sum(await rec);
    if (OUT) await p.screenshot({ path: `${OUT}/perf-${name}.png` });
  };
  await measure('hub-idle', async () => {});
  await measure('hub-scroll', async () => { for (let i = 0; i < 25; i++) { await p.mouse.wheel(0, 120); await p.waitForTimeout(90); } });
  await p.evaluate(() => { location.hash = '#home'; });
  await p.waitForTimeout(1200);
  const lt0 = await p.evaluate(() => window.__lt.length);
  await measure('path-scroll', async () => { for (let i = 0; i < 30; i++) { await p.mouse.wheel(0, 160); await p.waitForTimeout(80); } });
  await measure('path-hover', async () => {
    const tiles = await p.$$('[data-t]');
    for (let i = 0; i < Math.min(40, tiles.length); i += 2) { try { await tiles[i].hover({ timeout: 500 }); } catch (e) {} await p.waitForTimeout(60); }
  });
  const ix = await p.evaluate(() => (typeof D !== 'undefined' ? D.findIndex(d => d.r >= 5) : 0));
  await measure('item-page', async () => { await p.evaluate(i => { location.hash = '#i' + i; }, ix); await p.waitForTimeout(800); for (let i = 0; i < 10; i++) { await p.mouse.wheel(0, 120); await p.waitForTimeout(90); } });
  res.longTasksAfterLoad = (await p.evaluate(() => window.__lt)).slice(lt0).map(x => Math.round(x));
  res.errors = errors;
  console.log(JSON.stringify(res, null, 1));
  await b.close();
})();
