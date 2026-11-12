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
    // the body's width is known and inside the frame (the page keeps bodies over their own step); the Ender Dragon perches (its feet are its lowest pixel, behind the others)
    if (!(f.bw > 0 && f.bw <= f.w)) bad.push(`climb: the figure of ${k} has no body width`);
    // the strip is pixel art drawn at whole texels (an even number of strip pixels to a skin texel, so the half-size page shows whole pixels) and shown unsmoothed;
    // the perched dragon (wings) is sized by its width, not by whole texels; the end boss's picture is a nearest-texel render shown at a whole number of pixels a texel
    const ir = getComputedStyle(im).imageRendering, art = NEXTB[a] && !f.perch;
    if (art && !(Number.isInteger(f.tx) && f.tx >= 2 && f.tx % 2 === 0)) bad.push(`climb: the strip of ${k} is not drawn at whole texels (tx ${f.tx})`);
    if (art && ir !== 'auto') bad.push(`climb: the figure of ${k} is shown ${ir}, not smoothly downscaled (nearest-neighbour at 0.31 to 0.47 makes its texels uneven)`);
    if (!NEXTB[a] && ir !== 'auto') bad.push(`climb: the end boss ${k} is shown ${ir}, not smoothly downscaled`);
    if (!!f.perch !== b.querySelector('.pfr').classList.contains('perch')) bad.push(`climb: ${k} ${f.perch ? 'should perch and does not' : 'perches and should not'}`); }
  // side by side, at rest: every figure's body stands over the middle of its step (the strips are framed on the body, not on a
  // sword or a wing), and no two bodies overlap (the perched dragon is behind the others); the ground is the frame's bottom
  { const at = pn().map((b, i) => { const a = path[i], k = NEXTB[a] || (ENDB[a] || [])[0], f = BFIG[k], r = b.querySelector('.pfr'), pr = r.getBoundingClientRect(), br = b.getBoundingClientRect(), fit = +getComputedStyle(r).getPropertyValue('--fit') || 1;
      const pk = r.querySelector('.pk:not(.wk)').getBoundingClientRect();   // the figure as drawn (its scale included), not the box it is scaled from: the end steps once pushed theirs 15 px aside
      return { k, perch: !!f.perch, c: pr.left + pr.width / 2, off: pk.left + pk.width / 2 - (br.left + br.width / 2), bw: pr.width * f.bw / f.w * fit }; });
    at.forEach((x, i) => { if (Math.abs(x.off) > 6) bad.push(`climb: the body of ${x.k} is ${x.off.toFixed(0)}px off the middle of its step`);
      const y = at[i + 1]; if (y && !x.perch && !y.perch && y.c - x.c < (x.bw + y.bw) / 2 - 2) bad.push(`climb: the bodies of ${x.k} and ${y.k} overlap by ${((x.bw + y.bw) / 2 - (y.c - x.c)).toFixed(0)}px`); }); }
  // at rest the staircase is small, with sky between its steps (--rest in style.game.css; the pointed step grows to full size, which needs a pointer to test): on a wide
  // screen no step fills more than 80% of its cell, and no figure is drawn at more than three quarters of its full size
  { const tr = document.querySelector('#pmap .ptrack');
    if (getComputedStyle(tr).display === 'grid') { const cell = tr.clientWidth / pn().length;
      pn().forEach((b, i) => { if (b.offsetWidth > cell * .8) bad.push(`climb: step ${i} fills ${(b.offsetWidth / cell * 100).toFixed(0)}% of its cell: no sky between the steps`);
        const sc = parseFloat(getComputedStyle(b.querySelector('.pk')).scale); if (sc > .75) bad.push(`climb: the figure on step ${i} is drawn at ${sc.toFixed(2)} of its size at rest, not small`); }); } }
  // a column is built (app.js colFx): courses of stone, a frieze in the Act's colour, the sun's grade and three points of light, all pictures that loaded; nothing dark or faded laid over it,
  // and it has the same one-texel outline as the Keeper on top
  pn().forEach((b, i) => { const bk = b.querySelector('.bk'), fr = b.querySelector('.fr'), gr = b.querySelector('.gr'), gl = b.querySelectorAll('.gl b');
    if (!bk || !fr || !gr || gl.length !== 3) { bad.push(`climb: column ${i} is missing a piece (courses ${!!bk}, frieze ${!!fr}, grade ${!!gr}, ${gl.length} lights)`); return; }
    if (!/svg/.test(getComputedStyle(bk).backgroundImage) || !/svg/.test(getComputedStyle(fr).backgroundImage)) bad.push(`climb: column ${i} has no courses or no frieze picture`);
    const cs = getComputedStyle(b); if (!/22, 11, 42/.test(cs.boxShadow)) bad.push(`climb: column ${i} has no outline`);
    if (/gradient/.test(cs.backgroundImage) && /rgba\(0, 0, 0, 0?\.[5-9]/.test(cs.backgroundImage)) bad.push(`climb: column ${i} has a dark shade over its stone`);
    if (getComputedStyle(b.querySelector('.gl b')).animationIterationCount !== 'infinite' && !matchMedia('(prefers-reduced-motion:reduce)').matches) bad.push(`climb: the lights of column ${i} do not twinkle`); });
  // the sky is painted (app.js skyPaint): both canvases have a picture, the sky's top is not the land and the land's foot is opaque rock, the clouds are sprites, and the old CSS hills and cloud shapes are gone
  { await new Promise(r => requestAnimationFrame(() => setTimeout(r, 250)));   // skyPaint runs in the frame after the page is drawn
    const cl = document.querySelector('#pmap .climb'), a0 = cl.querySelector('.dart0'), a1 = cl.querySelector('.dart1');
    if (!a0 || !a1 || !a0.width || !a1.width || a0.width !== a1.width || a0.height !== a1.height) bad.push('climb: the sky canvases are missing, empty or of different sizes');
    else { const px = (c, x, y) => c.getContext('2d').getImageData(x, y, 1, 1).data[3];
      if (px(a0, a0.width >> 1, 2) < 250) bad.push('climb: the top of the sky is not painted');
      if (px(a1, a1.width >> 1, a1.height - 2) < 250) bad.push('climb: the foot of the land is not painted');
      if (px(a1, a1.width >> 1, 2) > 0) bad.push('climb: the land fills the whole scene'); }
    if (cl.querySelector('.dr1, .dr2')) bad.push('climb: the CSS hills are still there beside the painted land');
    if (!/url\(/.test(getComputedStyle(cl.querySelector('.dcl')).backgroundImage)) bad.push('climb: a cloud has no sprite'); }
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
// the second round of the hero (docs/plans/2026-11-11-the-climb.md section 22): the loops are smooth (idle 24 frames at most 130 ms a frame, walk 16), the step layers cost no blend
// (thirteen blend groups across the sky were the lag when a step was pointed at; the stair light slides by translate, not by background-position), the text of the hero
// stands on one left edge and is legible, and the shelves are display cases of whole rows
{ location.hash = '#'; await new Promise(r => setTimeout(r, 80)); render(); await new Promise(r => setTimeout(r, 120));
  const px = [...document.querySelectorAll('#pmap .pn')];
  for (const a of ORDER.filter(a => a >= 0 && NEXTB[a])) { const k = NEXTB[a], f = BFIG[k], w = (window.BWALK || {})[k];
    if (f.n < 24 || f.ms / f.n > 130) bad.push(`climb: the idle loop of ${k} is ${f.n} frames in ${f.ms} ms (needs 24 frames, at most 130 ms a frame)`);
    if (w && w.n < 16) bad.push(`climb: the walk loop of ${k} is ${w.n} frames (needs 16)`); }
  px.forEach((b, i) => { const gr = getComputedStyle(b.querySelector('.gr')), fa = getComputedStyle(b.querySelector('.fr'), '::after'), sw = getComputedStyle(b.querySelector('.sw'), '::before');
    if (gr.mixBlendMode !== 'normal' || fa.mixBlendMode !== 'normal') bad.push(`climb: column ${i} blends its layers (grade ${gr.mixBlendMode}, frieze light ${fa.mixBlendMode}): that made pointing at a step lag`);
    if (gr.backgroundAttachment.includes('fixed')) bad.push(`climb: the grade of column ${i} is a fixed background (repainted on every scroll)`);
    if (sw.animationName !== 'stairLight' || sw.translate === 'none' || getComputedStyle(b.querySelector('.sw')).animationName !== 'none') bad.push(`climb: the stair light of column ${i} is not a sliding layer (animation ${sw.animationName}, translate ${sw.translate})`); });
  const cl = document.querySelector('#pmap .climb'), L = e => Math.round(cl.querySelector(e).getBoundingClientRect().left), lum = c => { const m = c.match(/\d+/g).map(Number); return Math.min(m[0], m[1], m[2]) };
  if (innerWidth > 1100) { const ls = ['.tcs', 'h1.lg', '.pcap', '.hsearch'].map(L); if (Math.max(...ls) - Math.min(...ls) > 1) bad.push(`climb: the hero's text is not on one left edge (${ls.join(', ')})`);
    const hs = cl.querySelector('.tact').getBoundingClientRect(), top = Math.min(...px.map(b => b.getBoundingClientRect().top - 330));
    if (hs.bottom > cl.getBoundingClientRect().top + cl.clientHeight * .58) bad.push(`climb: the hero's text runs down to ${Math.round(hs.bottom)} px, into the sun and the staircase`); }
  if (lum(getComputedStyle(cl.querySelector('.pcap .gs')).color) < 200) bad.push(`climb: the caption of The Path is ${getComputedStyle(cl.querySelector('.pcap .gs')).color}, too dim on its plate`);
  if (!cl.querySelectorAll('.tcs .tcorner').length || cl.querySelectorAll('.tcs .tcorner').length !== 4) bad.push('climb: the line of facts about the pack is not four chips');
  // the shelves of the rack: a title bar in the case's colour, a count that is the real count, a link to all of it, a tray of slots in whole rows
  const sh = [...document.querySelectorAll('.rack .shelf')], want = { 0: D.filter(isMust).length, 1: D.filter(d => d.r === 5).length, 2: D.filter(d => d.nw).length };
  if (sh.length < 3) bad.push(`climb: the rack has ${sh.length} shelves`);
  sh.forEach((e, i) => { const slots = [...e.querySelectorAll('.srow .sslot')], vis = slots.filter(x => getComputedStyle(x).display !== 'none'), cols = getComputedStyle(e.querySelector('.srow')).gridTemplateColumns.split(' ').length;
    if (!e.querySelector('.shh .gt') || !getComputedStyle(e.querySelector('.shh .gt'), '::before').display.includes('block')) bad.push(`climb: shelf ${i} has no title bar`);
    if (!e.querySelector('.shall[data-f]')) bad.push(`climb: shelf ${i} has no link to all of it`);
    const n = +(e.querySelector('.shn') || { textContent: '' }).textContent.match(/\d+/); if (n !== want[i]) bad.push(`climb: shelf ${i} counts ${n}, the pack has ${want[i]}`);
    if (!vis.length || vis.length % cols || cols < 4) bad.push(`climb: shelf ${i} shows ${vis.length} slots in ${cols} columns: not whole rows`);
    if (e.querySelector('.sslot small')) bad.push(`climb: shelf ${i} labels its slots (the Act is in the tooltip, not on the slot)`);
    const ic = vis.find(x => !x.classList.contains('e')), im = ic && ic.querySelector('img, .aimg'), q = im && im.getBoundingClientRect().width / ic.getBoundingClientRect().width;
    if (im && !(q > .45 && q < .66)) bad.push(`climb: shelf ${i} draws its icon ${Math.round(im.getBoundingClientRect().width)} px in a ${Math.round(ic.getBoundingClientRect().width)} px slot (${q.toFixed(2)}: it should be a little over half)`);
    if (vis.length < Math.min(cols, 8)) bad.push(`climb: shelf ${i} shows ${vis.length} slots of ${cols} columns`); }); }
// the wave (app.js pathMapWire): the step under the pointer grows to full size, its neighbours shrink, the nearer the more, and everything settles back when the pointer leaves;
// the pointer parallax is written on the sky, never on the whole hero (every node under a written custom property works out its style again: 10 ms a move)
{ location.hash = '#'; await new Promise(r => setTimeout(r, 80)); render(); await new Promise(r => setTimeout(r, 200));
  const map = document.getElementById('pmap'), cl = map.querySelector('.climb'), tabs = [...map.querySelectorAll('.pn')], tr = map.querySelector('.ptrack'), sk = cl.querySelector('.dsky'),
    rest = parseFloat(getComputedStyle(cl).getPropertyValue('--rest')), sleep = ms => new Promise(r => setTimeout(r, ms)),
    ratio = () => tabs.map(t => t.getBoundingClientRect().width / (tr.clientWidth / tabs.length)), T = tr.getBoundingClientRect(), w = T.width / tabs.length,
    move = (k, dx = 0) => sk.dispatchEvent(new PointerEvent('pointermove', { bubbles: true, clientX: T.left + w * (k + .5) + dx, clientY: T.bottom - 40 }));
  if (innerWidth > 1100 && matchMedia('(hover:hover) and (pointer:fine)').matches && !matchMedia('(prefers-reduced-motion:reduce)').matches) {
    if (!map.classList.contains('wave')) bad.push('climb: the wave is not on at a desktop width');
    else { const k = 6, h0 = tabs.map(t => t.getBoundingClientRect().height); move(k); await sleep(900); const r = ratio();
      if (r[k] < .97) bad.push(`climb: the step under the pointer is ${r[k].toFixed(2)} of its cell, not full size`);
      if (!(r[k - 1] < rest - .05 && r[k + 1] < rest - .05)) bad.push(`climb: the neighbours of the pointed step are ${r[k - 1].toFixed(2)} and ${r[k + 1].toFixed(2)}, not smaller than rest (${rest})`);
      if (!(r[k - 1] < r[k - 2] && r[k - 2] <= r[k - 3] + .001 && r[k + 1] < r[k + 2] && r[k + 2] <= r[k + 3] + .001)) bad.push(`climb: the wave does not fade with distance (${r.map(x => x.toFixed(2)).join(' ')})`);
      if (Math.abs(r[0] - rest) > .01 || Math.abs(r[12] - rest) > .01) bad.push('climb: the far steps move with the pointer');
      if (tabs.filter(t => t.classList.contains('hov')).length !== 1 || !tabs[k].classList.contains('hov')) bad.push('climb: the pointed step is not the one marked .hov');
      if (cl.style.getPropertyValue('--mx') !== '' || sk.style.getPropertyValue('--mx') === '') bad.push('climb: the pointer parallax is not written on the sky alone');
      const hr = tabs.map((t, i) => t.getBoundingClientRect().height / h0[i]);
      if (!(hr[k] > 1.4 && hr[k - 1] < .95 && hr[k + 1] < .95)) bad.push(`climb: the heights do not follow the wave (pointed ${hr[k].toFixed(2)}, neighbours ${hr[k - 1].toFixed(2)} and ${hr[k + 1].toFixed(2)} of rest)`);
      move(k, w * .5); await sleep(900); const b = ratio();
      if (!(b[k] > rest + .05 && b[k] < .97 && b[k + 1] > rest + .05 && b[k + 1] < .97)) bad.push(`climb: between two steps both should be part grown (${b[k].toFixed(2)}, ${b[k + 1].toFixed(2)})`);
      sk.dispatchEvent(new PointerEvent('pointerleave')); cl.dispatchEvent(new PointerEvent('pointerleave')); await sleep(900); const z = ratio();
      if (z.some(x => Math.abs(x - rest) > .01) || tabs.some(t => t.classList.contains('hov'))) bad.push(`climb: the steps do not settle back to rest when the pointer leaves (${z.map(x => x.toFixed(2)).join(' ')})`); } } }
