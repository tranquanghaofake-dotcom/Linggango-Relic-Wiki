// Style guardrails for the built wiki (Chromium, no network). Run by check.sh after check.js.
// Fails (exit 1) when a visible element on the main routes and a sample of detail pages:
//   - has rounded corners (the look is pixel GUI: square corners only);
//   - draws pixel art (a source of 64 px or less) at a scale that is not a whole number, nor 1/n of the source;
//   - uses an emoji as an icon (any emoji-presentation character, or a pictograph inside a button, chip, badge, heading or label).
// Prints, without failing, edges drawn within 40 px inside another edge (frame inside a frame), to look at by eye.
const { chromium } = require('playwright'), path = require('path');
(async () => {
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1440, height: 900 } }), errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve(process.argv[2] || 'dist/Linggango_Relic_Wiki.html'), { waitUntil: 'load' });
  await p.waitForTimeout(2500);
  const sample = await p.evaluate(() => ['#i' + D[0].ix, '#i' + D[Math.floor(D.length / 2)].ix, '#g0', '#gs0', '#boss/' + KEEPERS()[3], '#side/' + encodeURIComponent(Object.keys(SIDEB)[0])]);
  const routes = ['#', '#home', '#gear', '#bosses', '#build', '#mechanics', ...sample];
  const fails = [], warn = [];
  for (const r of routes) {
    await p.evaluate(h => { location.hash = h }, r); await p.waitForTimeout(1800);
    const res = await p.evaluate(async () => {
      const out = { round: {}, scale: {}, emoji: {}, nest: {} }, nat = {};
      const name = e => e.tagName.toLowerCase() + (e.classList.length ? '.' + [...e.classList].slice(0, 2).join('.') : '');
      const path2 = e => (e.parentElement ? name(e.parentElement) + '>' : '') + name(e);
      const add = (o, k) => { o[k] = (o[k] || 0) + 1 };
      const load = u => nat[u] || (nat[u] = new Promise(ok => { const i = new Image(); i.onload = () => ok([i.naturalWidth, i.naturalHeight]); i.onerror = () => ok(null); i.src = u }));
      const okScale = s => s > 0 && (Math.abs(s - Math.round(s)) < 0.02 && Math.round(s) >= 1 || Math.abs(1 / s - Math.round(1 / s)) < 0.02);
      const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < 2700 };
      const els = [...document.querySelectorAll('body *')].filter(vis);
      const edge = e => { const c = getComputedStyle(e); return (parseFloat(c.borderTopWidth) > 0 && c.borderTopStyle !== 'none') || c.boxShadow !== 'none' || c.borderImageSource !== 'none' };
      for (const e of els) {
        const c = getComputedStyle(e);
        for (const ps of [null, '::before', '::after']) { const q = ps ? getComputedStyle(e, ps) : c; if (ps && q.content === 'none') continue; if (parseFloat(q.borderTopLeftRadius) > 0 || parseFloat(q.borderBottomRightRadius) > 0) add(out.round, path2(e) + (ps || '')) }
        if (e.tagName === 'IMG' && e.naturalWidth && e.naturalWidth <= 64 && /pixelated|crisp/.test(c.imageRendering)) {
          const w = e.getBoundingClientRect().width - parseFloat(c.paddingLeft) - parseFloat(c.paddingRight) - parseFloat(c.borderLeftWidth) - parseFloat(c.borderRightWidth);
          if (!okScale(w / e.naturalWidth) && e.naturalWidth % 8 === 0) add(out.scale, path2(e) + ' x' + (w / e.naturalWidth).toFixed(2));
        }
        const m = c.backgroundImage.match(/url\("?(data:image\/png[^")]+)"?\)/);
        if (m && /pixelated|crisp/.test(c.imageRendering)) {
          const n = await load(m[1]); if (n && n[0] <= 64 && n[0] % 8 === 0) {
            const bs = c.backgroundSize.split(',')[0].trim().split(' ')[0], rw = e.getBoundingClientRect().width;
            const w = bs === 'auto' ? n[0] : bs.endsWith('px') ? parseFloat(bs) : bs.endsWith('%') ? rw * parseFloat(bs) / 100 : null;
            if (w !== null && !okScale(w / n[0])) add(out.scale, path2(e) + ' bg x' + (w / n[0]).toFixed(2));
          }
        }
        if (edge(e) && e.getBoundingClientRect().width > 40) { let n = e.parentElement, d = 0; const r = e.getBoundingClientRect();
          while (n && n !== document.body && d < 5) { const q = n.getBoundingClientRect(); if (edge(n) && r.left - q.left <= 40 && q.right - r.right <= 40 && r.top - q.top <= 40 && q.bottom - r.bottom <= 40) { add(out.nest, path2(e) + ' in ' + name(n)); break } n = n.parentElement; d++ } }
      }
      const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      for (let t; (t = tw.nextNode());) { const el = t.parentElement; if (!el || !vis(el) || el.closest('script,style,code')) continue; const s = t.textContent;
        if (/\p{Emoji_Presentation}/u.test(s) || (/\p{Extended_Pictographic}/u.test(s) && el.closest('button,.chip,.badge,h1,h2,h3,th,label,.mcb,.pill,small'))) add(out.emoji, path2(el) + ' "' + s.trim().slice(0, 20) + '"') }
      return out;
    });
    for (const k of ['round', 'scale', 'emoji']) for (const [s, n] of Object.entries(res[k])) fails.push(`${r} ${k}: ${s} (${n})`);
    for (const [s, n] of Object.entries(res.nest)) warn.push(`${r} ${s} (${n})`);
  }
  console.log('style: ' + (fails.length ? fails.length + ' problems' : 'square corners, whole-number pixel scales, sprite icons') + (warn.length ? '; frames inside frames to look at: ' + warn.length : ''));
  fails.slice(0, 40).forEach(x => console.log('  FAIL ' + x)); warn.slice(0, 15).forEach(x => console.log('  look ' + x));
  if (errs.length) console.log('  script errors: ' + errs.slice(0, 3).join(' | '));
  await b.close(); process.exit(fails.length || errs.length ? 1 : 0);
})();
