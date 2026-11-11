// The climb: the home page's hero is The Path as a staircase (docs/plans/2026-11-11-the-climb.md). Runs in the page (check.js:
// `bad` and `acts` in scope). One step per Act of The Path, in order; a step's text is the Act's label alone (the Keeper's name
// is drawn from data-k, so tools and tests that read a step still read "XI"); the Keeper on a step is the one to beat at that
// Act (NEXTB) and the last Act carries its emblem; an Act's chest holds its strongest curios first; "I'm here" marks that step
// and the ones before it.
{ location.hash = '#'; render();
  const path = ORDER.filter(a => a >= 0 && D.some(d => d.t === a)), pn = () => [...document.querySelectorAll('#pmap .pn')];
  if (pn().length !== path.length) bad.push(`climb: ${pn().length} steps for ${path.length} Acts`);
  if (!document.querySelector('#main h1')) bad.push('climb: the home page has no h1');
  pn().forEach((b, i) => { const a = path[i], k = NEXTB[a], im = b.querySelector('img.pk');
    if (b.textContent.trim() !== ACT[a][0]) bad.push(`climb: step ${i} reads "${b.textContent.trim()}", not "${ACT[a][0]}"`);
    if (!/url\(/.test(getComputedStyle(b).backgroundImage)) bad.push(`climb: step ${ACT[a][0]} has no block texture`);
    if (k) { if (!b.dataset.k) bad.push(`climb: step ${ACT[a][0]} does not name its Keeper`);
      if (BPORT[k] ? !im || !im.src.endsWith(BPORT[k]) : !!im) bad.push(`climb: step ${ACT[a][0]} does not show ${k}`); }
    else if (im || b.dataset.k || !b.querySelector('.emb')) bad.push(`climb: step ${ACT[a][0]} has no Keeper to beat, so it shows the Act's emblem`); });
  const i = Math.min(2, path.length - 1), a = path[i]; pn()[i].click();
  const sl = [...document.querySelectorAll(`#pp-${i} .chest .sslot`)], top = byRank(D.filter(d => d.t === a));
  if (!sl.length || sl.length > CHESTN || sl.length !== Math.min(CHESTN, top.length)) bad.push(`climb: the chest of ${ACT[a][0]} has ${sl.length} slots for ${top.length} curios`);
  sl.forEach((s, j) => { if (s.getAttribute('href') !== '#i' + top[j].ix) bad.push(`climb: chest slot ${j} of ${ACT[a][0]} is not the curio ranked ${j + 1}`); });
  try { localStorage.setItem(PHKEY, a); render();
    const cls = pn().map(b => b.classList.contains('here') ? 'h' : b.classList.contains('done') ? 'd' : '-').join('');
    if (cls !== 'd'.repeat(i) + 'h' + '-'.repeat(path.length - i - 1)) bad.push(`climb: "I'm here" at ${ACT[a][0]} marks the steps ${cls}`);
    if (pn()[i].getAttribute('aria-selected') !== 'true') bad.push(`climb: the reader's own step is not the open one`);
  } finally { try { localStorage.removeItem(PHKEY); } catch (e) {} render(); } }
