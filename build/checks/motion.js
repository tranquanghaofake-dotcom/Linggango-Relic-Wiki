// Motion (docs/plans/2026-11-11-the-climb.md section 23). What the site adds in the round of 2026-11-12 shares one set of timings and one curve (--mo-*), moves only transform and opacity,
// starts when it can be seen, and stops when it cannot: the home page opens line by line; the shelves arrive once per visit and deal their slots in one after the other; a slot lifts under
// the pointer; the hero's own loops pause while it is off screen; the cave wall's ores wait behind the hero; Equipment marks a switch (.swap) and the chosen button presses in.
// (the page redraws once more when the address changes, so this file awaits between steps)
{ const sleep = ms => new Promise(r => setTimeout(r, ms)), go = async h => { location.hash = h; await sleep(150); },
    RM = matchMedia('(prefers-reduced-motion:reduce)').matches, root = getComputedStyle(document.documentElement);
  for (const v of ['--mo-1', '--mo-2', '--mo-3', '--mo-ease']) if (!root.getPropertyValue(v).trim()) bad.push(`motion: ${v} is not defined on :root`);
  if (!RM) {
    await go('#home'); await go('#'); await sleep(500);
    const cl = document.querySelector('#pmap .climb'), names = ['.tcs', '.lg', '.pcap', '.tact'].map(s => getComputedStyle(cl.querySelector(s)).animationName);
    if (names.some(n => n !== 'heroIn')) bad.push(`motion: the hero does not open line by line (${names.join(', ')})`);
    const dl = ['.tcs', '.lg', '.pcap', '.tact'].map(s => parseFloat(getComputedStyle(cl.querySelector(s)).animationDelay)); if (dl.some((d, i) => i && d <= dl[i - 1])) bad.push(`motion: the hero's lines do not follow one another (${dl.join(', ')} s)`);
    const sh = [...document.querySelectorAll('.rack .shelf')];
    if (sh.length < 3 || sh.some(e => !e.classList.contains('rv'))) bad.push('motion: the shelves do not arrive as they come into view');
    const og = document.querySelector('#cave .og'); if (og && !document.body.classList.contains('scrolled') && getComputedStyle(og, '::before').animationPlayState === 'running') bad.push('motion: the ores behind the hero twinkle at the top of the page');
    document.querySelector('.rack').scrollIntoView(); await sleep(700);
    if (sh.some(e => !e.classList.contains('in') && e.getBoundingClientRect().top < innerHeight - 60)) bad.push('motion: a shelf in view has not arrived');
    const s0 = sh[0], sl = [...s0.querySelectorAll('.sslot:not(.e)')].slice(0, 6), ds = sl.map(x => parseFloat(getComputedStyle(x).animationDelay)), an = getComputedStyle(sl[0]).animationName;
    if (s0.classList.contains('in') && (an !== 'slotIn' || ds.some((d, i) => i && d <= ds[i - 1]))) bad.push(`motion: the slots of a shelf do not deal in one after the other (${an}, delays ${ds.join(', ')})`);
    render(); await sleep(150); if (document.querySelector('.rack .shelf.rv')) bad.push('motion: a page drawn again on the same address replays its arrival');
    scrollTo(0, 3500); await sleep(500); if (!document.querySelector('#pmap .climb').classList.contains('zz')) bad.push('motion: the hero keeps playing while it is off screen');
    scrollTo(0, 0); await sleep(500); if (document.querySelector('#pmap .climb').classList.contains('zz')) bad.push('motion: the hero stays paused after it comes back');
    const sl2 = getComputedStyle(document.querySelector('.rack .sslot:not(.e)')).transitionProperty; if (!/transform/.test(sl2)) bad.push(`motion: a slot does not lift under the pointer (transition ${sl2})`);
    // Equipment: a switch marks the page and the chosen button presses in; then it is over
    await go('#gear/12/ME/w'); await sleep(300); await go('#gear/12/RA/w'); await sleep(250);
    const g = document.querySelector('#main .gear'), sel = g && g.querySelector('.gseg a[aria-selected="true"]');
    if (!g || !g.classList.contains('swap') || !sel || getComputedStyle(sel).animationName !== 'selPop') bad.push(`motion: an Equipment switch does not press the chosen button in (${g && g.className}, ${sel && getComputedStyle(sel).animationName})`);
    await sleep(1100); if (document.querySelector('#main .gear.swap')) bad.push('motion: the Equipment switch mark stays on');
    await go('#'); }
}
