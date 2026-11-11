// The climb: the home page's hero is The Path as a staircase (docs/plans/2026-11-11-the-climb.md). Runs in the page (check.js:
// `bad` and `acts` in scope). One step per Act of The Path, in order; a step's text is the Act's label alone (the Keeper's name
// is drawn from data-k, so tools and tests that read a step still read "XI"); the figure on a step is the Keeper to beat at
// that Act (NEXTB) and, on the last Act, the Act's end-game side boss (ENDB: it must be a side boss of that Act); every figure
// has a strip in BFIG whose picture is as wide as its frames say; an Act's chest holds its strongest curios first; "I'm here"
// marks that step and the ones before it; the wordmark is gone from the hero (one "Linggango" at the top, the header's);
// every step carries its Act's air and the stair light.
// (the page redraws once more when the address changes, so wait for that before reading: this file awaits between steps)
{ location.hash = '#'; await new Promise(r => setTimeout(r, 80)); render();
  const path = ORDER.filter(a => a >= 0 && D.some(d => d.t === a)), pn = () => [...document.querySelectorAll('#pmap .pn')];
  if (pn().length !== path.length) bad.push(`climb: ${pn().length} steps for ${path.length} Acts`);
  const h1 = document.querySelector('#main h1');
  if (!h1 || !/Linggango Wiki/.test(h1.textContent) || h1.querySelector('img')) bad.push('climb: the home page\'s h1 is not the text headline that names the wiki');
  for (const [a, [k, name]] of Object.entries(ENDB)) { if (NEXTB[a]) bad.push(`climb: Act ${a} has a Keeper and an end boss`);
    if (!SIDEB[name] || !BOSSR.some(r => r[0] === name && r[1] === +a)) bad.push(`climb: ${name} is not a side boss of Act ${a}`); }
  for (const [i, b] of pn().entries()) { const a = path[i], k = NEXTB[a] || (ENDB[a] || [])[0], f = k && BFIG[k], im = b.querySelector('.pk img');
    if (b.textContent.trim() !== ACT[a][0]) bad.push(`climb: step ${i} reads "${b.textContent.trim()}", not "${ACT[a][0]}"`);
    if (!/url\(/.test(getComputedStyle(b).backgroundImage)) bad.push(`climb: step ${ACT[a][0]} has no block texture`);
    if (!b.querySelector('.sw') || !b.querySelector('.envfx')) bad.push(`climb: step ${ACT[a][0]} has no air or no stair light`);
    if (!f || !im || im.getAttribute('src') !== f.src || !b.dataset.k) { bad.push(`climb: step ${ACT[a][0]} does not show and name ${k || 'a boss'}`); continue; }
    await im.decode().catch(() => {});
    if (im.naturalWidth !== f.w * f.n || im.naturalHeight !== f.h) bad.push(`climb: the strip of ${k} is ${im.naturalWidth}x${im.naturalHeight}, its record says ${f.n} frames of ${f.w}x${f.h}`);
    if (NEXTB[a] && (f.n < 2 || !f.ms)) bad.push(`climb: the Keeper ${k} has no idle loop`);
    // the body's width is known and inside the frame (the page keeps bodies over their own step); only a flying figure is lifted off its step
    if (!(f.bw > 0 && f.bw <= f.w)) bad.push(`climb: the figure of ${k} has no body width`);
    if (!!f.fly !== b.querySelector('.pfr').classList.contains('fly')) bad.push(`climb: ${k} ${f.fly ? 'should fly and does not' : 'flies and should not'}`); }
  // the walk loops (BWALK, with the late pictures): each belongs to a figure, shares its scale and its ground, and its picture is as wide as its frames say
  for (const [k, w] of Object.entries(window.BWALK || {})) { const f = BFIG[k], im = new Image(); im.src = w.src; await im.decode().catch(() => {});
    if (!f || f.n < 2) bad.push(`climb: a walk loop for ${k}, which has no animated figure`);
    else if (im.naturalWidth !== w.w * w.n || im.naturalHeight !== w.h || Math.abs(w.h - f.h) > f.h * .12) bad.push(`climb: the walk strip of ${k} is ${im.naturalWidth}x${im.naturalHeight} for ${w.n} frames of ${w.w}x${w.h} (idle ${f.h} tall)`); }
  const i = Math.min(2, path.length - 1), a = path[i]; pn()[i].click();
  const sl = [...document.querySelectorAll(`#pp-${i} .chest .sslot`)], top = byRank(D.filter(d => d.t === a));
  if (!sl.length || sl.length > CHESTN || sl.length !== Math.min(CHESTN, top.length)) bad.push(`climb: the chest of ${ACT[a][0]} has ${sl.length} slots for ${top.length} curios`);
  sl.forEach((s, j) => { if (s.getAttribute('href') !== '#i' + top[j].ix) bad.push(`climb: chest slot ${j} of ${ACT[a][0]} is not the curio ranked ${j + 1}`); });
  try { localStorage.setItem(PHKEY, a); render();
    const cls = pn().map(b => b.classList.contains('here') ? 'h' : b.classList.contains('done') ? 'd' : '-').join('');
    if (cls !== 'd'.repeat(i) + 'h' + '-'.repeat(path.length - i - 1)) bad.push(`climb: "I'm here" at ${ACT[a][0]} marks the steps ${cls}`);
    if (pn()[i].getAttribute('aria-selected') !== 'true') bad.push(`climb: the reader's own step is not the open one`);
  } finally { try { localStorage.removeItem(PHKEY); } catch (e) {} render(); } }
