// Spacing audit: computed margin/padding/gap on every visible element of each route, rhythm between siblings,
// boxes touching or overlapping, text too close to its box edge. Usage: node space.js out.json [routes...]
const { chromium } = require('playwright'), path = require('path'), fs = require('fs');
const ROUTES = ['#', '#home', '#gear', '#build', '#bosses', '#mechanics', '#boss/goblin_lord', '#side/Ignis', '#i5', '#g10', '#gs3'];
(async () => {
  const out = process.argv[2], routes = process.argv.length > 3 ? process.argv.slice(3) : ROUTES;
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.emulateMedia({ reducedMotion: 'reduce' });
  await p.goto('file://' + path.resolve('../dist/Linggango_Relic_Wiki.html'), { waitUntil: 'load' }); await p.waitForTimeout(1500);
  const res = {};
  for (const r of routes) {
    await p.evaluate(h => { location.hash = h; }, r); await p.waitForTimeout(1500);
    await p.evaluate(async () => { document.querySelectorAll('.rv').forEach(e => e.classList.add('in')); for (let y = 0; y < document.body.scrollHeight; y += 800) { scrollTo(0, y); await new Promise(r => setTimeout(r, 30)); } scrollTo(0, 0); });
    await p.waitForTimeout(400);
    res[r] = await p.evaluate(() => {
      const SCALE = new Set([0, 2, 4, 8, 12, 16, 24, 32, 48, 64]);
      const key = e => e.tagName.toLowerCase() + (e.classList.length ? '.' + [...e.classList].filter(c => !/^(in|rv|seen2|zz|enter)$/.test(c)).slice(0, 2).join('.') : '') + (e.id ? '#' + e.id : '');
      const vis = e => { const r = e.getBoundingClientRect(), cs = getComputedStyle(e); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && cs.opacity !== '0'; };
      const els = [...document.querySelectorAll('header *, #main *, footer *')].filter(vis);
      const off = {}, props = ['margin-top', 'margin-bottom', 'margin-left', 'margin-right', 'padding-top', 'padding-bottom', 'padding-left', 'padding-right', 'row-gap', 'column-gap'];
      for (const e of els) { const cs = getComputedStyle(e); if (/^(svg|path|img|i|b|small|span|a|code|br|canvas|input)$/i.test(e.tagName) && !/flex|grid|block/.test(cs.display)) continue;
        for (const pr of props) { let v = cs.getPropertyValue(pr); if (v === 'normal' || v === 'auto') continue; v = parseFloat(v); if (!isFinite(v)) continue; v = Math.round(Math.abs(v) * 100) / 100;
          if (pr.endsWith('gap') && !/flex|grid/.test(cs.display)) continue;
          if (!SCALE.has(v)) { const k = key(e) + ' ' + pr + ':' + v; off[k] = (off[k] || 0) + 1; } } }
      // rhythm: vertical gaps between consecutive in-flow block children
      const rhythm = {}, touch = [];
      const boxed = e => { const cs = getComputedStyle(e); return parseFloat(cs.borderTopWidth) > 0 || (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent') || cs.backgroundImage !== 'none' || cs.boxShadow !== 'none'; };
      for (const par of [document.querySelector('header'), ...document.querySelectorAll('#main, #main *')].filter(x => x && vis(x))) {
        const cs = getComputedStyle(par); if (/flex|grid/.test(cs.display) && !/column/.test(cs.flexDirection) && cs.display.indexOf('grid') < 0) continue;
        const kids = [...par.children].filter(k => vis(k) && !/absolute|fixed/.test(getComputedStyle(k).position) && !/inline/.test(getComputedStyle(k).display));
        for (let i = 1; i < kids.length; i++) { const a = kids[i - 1].getBoundingClientRect(), c = kids[i].getBoundingClientRect();
          if (c.top < a.bottom - 1 && c.left >= a.right - 1) continue; // same row
          const g = Math.round(c.top - a.bottom); const k = key(par) + ' > ' + key(kids[i - 1]) + ' | ' + key(kids[i]);
          (rhythm[k] = rhythm[k] || []).push(g);
          if (g <= 0 && boxed(kids[i - 1]) && boxed(kids[i]) && Math.abs(c.left - a.left) < 4) touch.push(k + ' gap ' + g); } }
      // text too close to a boxed parent's edge
      const tight = {};
      for (const e of els) { if (!boxed(e)) continue; const r = e.getBoundingClientRect(); if (r.width < 40 || r.height < 18) continue;
        const tw = document.createTreeWalker(e, NodeFilter.SHOW_TEXT); let n, m = 99;
        while ((n = tw.nextNode())) { if (!n.textContent.trim()) continue; const pe = n.parentElement; if (pe !== e && boxed(pe) && e.contains(pe) && pe !== e) continue; const rg = document.createRange(); rg.selectNodeContents(n); for (const q of rg.getClientRects()) { if (!q.width) continue; m = Math.min(m, q.left - r.left, r.right - q.right, q.top - r.top, r.bottom - q.bottom); } }
        if (m < 6 && m > -50) { const k = key(e) + ' min ' + Math.round(m); tight[k] = (tight[k] || 0) + 1; } }
      const inc = Object.entries(rhythm).filter(([k, v]) => v.length > 1 && Math.max(...v) - Math.min(...v) > 2).map(([k, v]) => k + ' ' + JSON.stringify([...new Set(v)].slice(0, 8)));
      const gapsAll = Object.entries(rhythm).map(([k, v]) => [k, [...new Set(v)]]);
      return { off, inc, touch: [...new Set(touch)], tight, gaps: gapsAll };
    });
  }
  fs.writeFileSync(out, JSON.stringify(res, null, 1));
  for (const r in res) { const x = res[r]; console.log(r, 'offscale', Object.keys(x.off).length, 'inconsistent', x.inc.length, 'touching', x.touch.length, 'tight', Object.keys(x.tight).length); }
  await b.close();
})();
