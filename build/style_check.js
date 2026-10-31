// Style guardrails for the built wiki (Chromium, no network). Run by check.sh after check.js.
// Fails (exit 1) when a visible element on the main routes and a sample of detail pages:
//   - has rounded corners (the look is pixel GUI: square corners only);
//   - draws pixel art (a source of 64 px or less) at a scale that is not a whole number, nor 1/n of the source;
//   - uses an emoji as an icon (any emoji-presentation character, or a pictograph inside a button, chip, badge, heading or label).
//   - (static, in the sources) sets a margin, padding or gap to a px length off the spacing scale: steps are var(--s1..s8)
//     (4 8 12 16 24 32 48 64), literal 0 / 1 / 2 px for hairline nudges, negatives for border overlaps, over 64 px for layout sizes.
//   - at 375/414/768/1024/1180 px on one page of each kind and the main routes: scrolls sideways, keeps a detail page in two
//     columns or draws its infobox over the article, or breaks a phone layout (Curios Act, footer, Equipment, hub slot list).
// Prints, without failing, edges drawn within 40 px inside another edge (frame inside a frame), to look at by eye.
const { chromium } = require('playwright'), path = require('path'), fs = require('fs');
function spacingOffScale() {
  const H = __dirname, out = [];
  for (const f of ['style.game.css', 'src/v5.css', 'src/app.js', 'src/gear.js', 'src/ux.js', 'src/rooms.js', 'src/template.html']) {
    const t = fs.readFileSync(path.join(H, f), 'utf8');
    for (const m of t.matchAll(/(?<![\w-])((?:margin|padding)(?:-[a-z]+){0,2}|gap|row-gap|column-gap|grid-gap)\s*:\s*([^;}"`]*)/g)) {
      if (/calc\(|env\(/.test(m[2])) continue;
      for (const v of m[2].matchAll(/(?<![\w.-])(-)?(\d*\.?\d+)px\b/g)) { const n = +v[2]; if (!v[1] && n > 2 && n <= 64) out.push(`${f}: ${m[1]}:${m[2].trim().slice(0, 40)}`) }
    }
  }
  return out;
}
(async () => {
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1440, height: 900 } }), errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve(process.argv[2] || 'dist/Linggango_Relic_Wiki.html'), { waitUntil: 'load' });
  await p.waitForTimeout(2500);
  const sample = await p.evaluate(() => ['#i' + D[0].ix, '#i' + D[Math.floor(D.length / 2)].ix, '#g0', '#gs0', '#boss/' + KEEPERS()[3], '#side/' + encodeURIComponent(Object.keys(SIDEB)[0])]);
  const routes = ['#', '#home', '#gear', '#bosses', '#build', '#mechanics', ...sample];
  const fails = spacingOffScale().map(x => 'spacing ' + x), warn = [];
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
  // Narrow widths (phone 375/414, tablet 768, laptop 1024/1180): nothing scrolls sideways, detail pages are one column with
  // the infobox above the article, and the phone layouts of the Curios Acts, the footer, Equipment and the hub slot list hold.
  const narrow = [sample[0], sample[2], sample[3], sample[4], sample[5], '#home', '#gear', '#', '#changes'];
  for (const W of [375, 414, 768, 1024, 1180]) {
    await p.setViewportSize({ width: W, height: 900 });
    for (const r of narrow) {
      await p.evaluate(h => { location.hash = h }, r); await p.waitForTimeout(r === '#' || r === '#home' || r === '#gear' ? 1500 : 700);
      const res = await p.evaluate(([W, r]) => {
        const o = [], de = document.documentElement, vw = de.clientWidth, tracks = e => getComputedStyle(e).gridTemplateColumns.split(' ').length;
        const hit = (a, m) => a.width && a.left < m.right && a.right > m.left && a.top < m.bottom && a.bottom > m.top;
        const textPast = (box, right) => { const rg = document.createRange(), tw = document.createTreeWalker(box, NodeFilter.SHOW_TEXT); let n = 0;
          for (let t; (t = tw.nextNode());) { rg.selectNodeContents(t); for (const rc of rg.getClientRects()) if (rc.width && rc.right > right + 0.5) { n++; break } } return n };
        if (de.scrollWidth > vw) o.push(`page scrolls sideways (${de.scrollWidth} > ${vw})`);
        const ib = document.querySelector('.ip-body'), main = document.querySelector('.ip-main');
        if (ib && W <= 1180 && tracks(ib) > 1) o.push('.ip-body has ' + tracks(ib) + ' columns: ' + getComputedStyle(ib).gridTemplateColumns);
        if (ib && main) { const m = main.getBoundingClientRect(); if ([...document.querySelectorAll('.ip-side .ip-art,.ip-side .ip-info')].some(k => hit(k.getBoundingClientRect(), m))) o.push('infobox drawn over the article') }
        const f = document.querySelector('.sfoot');
        if (f && W <= 414) { if (tracks(f) > 2) o.push('footer has ' + tracks(f) + ' columns');
          const n = [...f.querySelectorAll(':scope>div')].reduce((s, d) => s + textPast(d, d.getBoundingClientRect().right), 0); if (n) o.push(n + ' footer text runs past their column') }
        if (r === '#home' && W <= 414) { const t = document.querySelector('.tier:not(.closed)');
          if (!t) o.push('no open Act on Curios'); else { const tl = t.querySelector('.tiles');
            if (tracks(t) > 1 && !(tl && tl.getBoundingClientRect().width >= 300)) o.push('open Act keeps its label column beside the tiles: ' + getComputedStyle(t).gridTemplateColumns);
            for (const m of t.querySelectorAll('.tmore')) if (m.getBoundingClientRect().right > window.innerWidth) o.push('"' + m.textContent.trim() + '" ends at ' + Math.round(m.getBoundingClientRect().right)) } }
        if (r === '#gear') { for (const s of document.querySelectorAll('.gseg')) if (s.scrollWidth > s.clientWidth + 1) o.push(`.gseg clips its buttons (${s.clientWidth}/${s.scrollWidth})`);
          const cut = W > 414 ? [] : [...document.querySelectorAll('.gld a.slot span')].filter(s => s.scrollWidth > s.clientWidth + 1 || s.scrollHeight > s.clientHeight + 1);
          if (cut.length) o.push(cut.length + ' loadout names cut, e.g. ' + cut[0].textContent.trim()) }
        if (r === '#') { let n = 0, first = '';
          for (const a of document.querySelectorAll('.slotlist>a')) { const ar = a.getBoundingClientRect().right;
            if ([...a.children].some(c => c.getBoundingClientRect().right > ar + 0.5) || textPast(a, ar)) { n++; first = first || a.textContent.trim().slice(0, 20) } }
          if (n) o.push(n + ' Curio slot cells overflow, e.g. ' + first) }
        return o;
      }, [W, r]);
      for (const x of res) fails.push(`${W}px ${r} narrow: ${x}`);
    }
  }
  console.log('style: ' + (fails.length ? fails.length + ' problems' : 'square corners, whole-number pixel scales, sprite icons, spacing on the scale, narrow widths hold') + (warn.length ? '; frames inside frames to look at: ' + warn.length : ''));
  fails.slice(0, 40).forEach(x => console.log('  FAIL ' + x)); warn.slice(0, 15).forEach(x => console.log('  look ' + x));
  if (errs.length) console.log('  script errors: ' + errs.slice(0, 3).join(' | '));
  await b.close(); process.exit(fails.length || errs.length ? 1 : 0);
})();
