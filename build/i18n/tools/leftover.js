// node build/i18n/tools/leftover.js <index.html> <lang> [routes...]: text nodes still written in English on pages shown in <lang>; prints each distinct text with the routes it appears on (names and data texts show up too: look for chrome)
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const [, , html, lang, ...routes] = process.argv; const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  await p.goto('file://' + path.resolve(html) + '?lang=' + lang, { waitUntil: 'load' }); await p.waitForTimeout(1500);
  const seen = new Map();
  for (const r of routes) {
    await p.evaluate(h => { location.hash = h }, r); await p.waitForTimeout(350);
    const ts = await p.evaluate(() => { const out = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) { const t = n.nodeValue.replace(/\s+/g, ' ').trim(); const pe = n.parentElement; if (!t || !pe || /^(SCRIPT|STYLE|NOSCRIPT)$/.test(pe.tagName)) continue; if (pe.closest('[hidden],#tip')) continue; if (/[A-Za-z]{3,}[ -][A-Za-z]{2,}/.test(t) && !/[А-Яа-яЁё]/.test(t)) out.push(t); }
      for (const e of document.querySelectorAll('[title],[aria-label],[placeholder]')) for (const a of ['title', 'aria-label', 'placeholder']) { const t = (e.getAttribute(a) || '').trim(); if (t && /[A-Za-z]{3,}[ -][A-Za-z]{2,}/.test(t) && !/[А-Яа-яЁё]/.test(t)) out.push('[' + a + '] ' + t); } return out });
    for (const t of ts) { const k = t.slice(0, 160); if (!seen.has(k)) seen.set(k, new Set()); seen.get(k).add(r); }
  }
  for (const [t, rs] of [...seen].sort((a, b) => b[1].size - a[1].size || a[0].length - b[0].length)) console.log(rs.size + ' | ' + t + ' | ' + [...rs].slice(0, 2).join(' '));
  await b.close();
})();
