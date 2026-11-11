// Changes: the bar of kinds and days, and the days that fold (docs/plans/2026-11-11-the-climb.md §10). Runs in the page
// (check.js: `bad` in scope). Every group of a day is one of the tagged kinds, so the filter misses nothing; a kind's chip
// counts that kind's entries; choosing a kind shows that kind alone and puts the days without it aside, and "All kinds"
// brings everything back; the newest day starts open and the oldest folded; a date folds and unfolds its day with one
// click each, also on a second visit (a listener left on <main> by the first visit would toggle twice); a day's chip opens it.
{ const wait = ms => new Promise(r => setTimeout(r, ms)), go = async h => { location.hash = h; await wait(60); render(); await wait(120); };
  await go('#changes'); await go('#bosses'); await go('#changes');
  const m = document.getElementById('main'), days = () => [...m.querySelectorAll('section.s[id^="c-"]')], open = d => !d.classList.contains('shut'), seen = e => e.offsetParent !== null;
  if (!m.querySelector('.chbar') || days().length < 3) bad.push(`changes: no bar, or only ${days().length} days`);
  else { const d0 = days()[0], dl = days()[days().length - 1];
    if (m.querySelector('section.s[id^="c-"]>h3:not(.ck)')) bad.push('changes: a group that is not Added, Changed or Fixed: ' + m.querySelector('section.s[id^="c-"]>h3:not(.ck)').textContent);
    if (!open(d0) || open(dl)) bad.push(`changes: the newest day is ${open(d0) ? 'open' : 'folded'} and the oldest ${open(dl) ? 'open' : 'folded'}`);
    d0.querySelector('.chtog').click(); const a = open(d0); d0.querySelector('.chtog').click();
    if (a || !open(d0) || d0.querySelector('.chtog').getAttribute('aria-expanded') !== 'true') bad.push('changes: a date does not fold and unfold its day with one click each');
    const kinds = [...m.querySelectorAll('.chbar .chip[data-ck]')].map(c => c.dataset.ck).filter(Boolean);
    if (!kinds.length) bad.push('changes: no kind chips');
    for (const k of kinds) { const c = m.querySelector(`.chbar .chip[data-ck="${k}"]`), n = m.querySelectorAll(`section.s>ul[data-k="${k}"]>li`).length;
      if (!n || +c.querySelector('.n').textContent !== n) bad.push(`changes: the ${k} chip says ${c.querySelector('.n').textContent} for ${n} entries`);
      c.click(); const vis = [...m.querySelectorAll('section.s[id^="c-"] [data-k]')].filter(seen);
      if (!vis.length || vis.some(e => e.dataset.k !== k)) bad.push(`changes: with ${k} chosen, ${vis.filter(e => e.dataset.k !== k).length} other groups still show (${vis.length} shown)`);
      if (days().some(d => !d.hidden !== d.dataset.kinds.split(' ').includes(k))) bad.push(`changes: with ${k} chosen, a day without it stays or a day with it is put aside`); }
    m.querySelector('.chbar .chip[data-ck=""]').click();
    if (m.dataset.ck || days().some(d => d.hidden) || [...d0.querySelectorAll('[data-k]')].some(e => !seen(e))) bad.push('changes: "All kinds" does not bring every day and group back');
    dl.querySelector('.chtog').click(); if (open(dl)) dl.querySelector('.chtog').click();   // fold the oldest again, then its chip must open it
    m.querySelector(`.chbar .chip[data-day="${dl.id}"]`).click(); if (!open(dl)) bad.push("changes: a day's chip does not open that day"); } }
