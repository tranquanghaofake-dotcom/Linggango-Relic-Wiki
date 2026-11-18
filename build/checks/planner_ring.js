// Build planner: the Starter ring toggle (BS.g) and the Gambler starter build (2026-11-18).
// Runs in the page (check.js: `bad` in scope).
{ const wait = ms => new Promise(r => setTimeout(r, ms)), names = () => [...document.querySelectorAll('.bx.on .bxi')].map(x => x.dataset.insp);
  location.hash = '#build/12'; await wait(80); render(); await wait(200);
  const gated = D.filter(d => d.rq && bAvail(d) && !d.inv);
  if (gated.length < 10) bad.push('planner ring: only ' + gated.length + ' ring-gated curios found');
  // ringless: no starter build contains a curio that needs a ring
  for (const r of ['ME', 'RA', 'MA', 'SU', 'RNG']) { BS.g = ''; bPreset(r); await wait(30);
    const hit = names().filter(id => BYID[id].rq); if (hit.length) bad.push('planner ring: ringless ' + r + ' build holds ' + hit.join(', ')); }
  // the Curses ring lets Curses curios in but never Virtues ones
  for (const r of ['ME', 'MA', 'RNG']) { BS.g = 'C'; bPreset(r); await wait(30);
    const hit = names().filter(id => BYID[id].rq === 'Virtues'); if (hit.length) bad.push('planner ring: Curses-only ' + r + ' build holds ' + hit.join(', ')); }
  // the choice survives a share link, and a bad value is dropped
  BS.g = 'CV'; if (!bHash().endsWith('|^CV')) bad.push('planner ring: link does not carry the ring: ' + bHash().slice(-12));
  bParse(bHash()); if (BS.g !== 'CV') bad.push('planner ring: link read back as "' + BS.g + '"');
  bParse('#build/12/x/^Z'); if (BS.g !== '') bad.push('planner ring: a bad ring code was kept');
  // Gambler: dice and coins turn up, and everything picked is chance-based or adds slots
  BS.g = ''; bPreset('RNG'); const g = names(), dice = g.filter(id => /dice|coin/i.test(BYID[id].n));
  if (dice.length < 4) bad.push('planner gambler: only ' + dice.length + ' dice/coin curios picked');
  // the toggle and the dimming are on the page
  BS.g = ''; BS.s = { Head: [] }; const rq = gated[0]; BS.s[rq.sl[0]] = [rq.id]; buildPage(); await wait(50);
  if (document.querySelectorAll('[data-ring]').length !== 4) bad.push('planner ring: toggle is not four buttons');
  if (!document.querySelector('.bx.on.rqoff')) bad.push('planner ring: a gated curio without its ring is not dimmed');
  BS.g = rq.rq[0]; buildPage(); await wait(50);
  if (document.querySelector('.bx.on.rqoff')) bad.push('planner ring: dimmed although its ring is chosen');
  BS.g = ''; BS.s = {}; }
// choosing a ring puts it in a Ring slot, un-choosing takes it out; a starter build keeps the chosen ring once
{ const wait = ms => new Promise(r => setTimeout(r, ms)), ring = () => (BS.s.Ring || []).slice(), C = 'enigmaticlegacy:cursed_ring', V = 'covenant_of_the_seven:virtue_ring', click = async c => { document.querySelector('[data-ring="' + c + '"]').click(); await wait(60); };
  BS.g = ''; BS.s = {}; buildPage(); await wait(50);
  await click('C'); if (ring().join() !== C) bad.push('planner ring: Curses did not put its ring in a Ring slot: ' + ring());
  await click('CV'); if (ring().sort().join() !== [C, V].sort().join()) bad.push('planner ring: Both did not give both rings: ' + ring());
  await click('V'); if (ring().join() !== V) bad.push('planner ring: Virtues left ' + ring());
  await click(''); if (ring().length) bad.push('planner ring: None left ' + ring());
  BS.g = 'C'; bPreset('ME'); if (ring().filter(x => x === C).length !== 1) bad.push('planner ring: a Melee build with Curses holds the ring ' + ring().filter(x => x === C).length + ' times');
  // Gambler: the expected-value lines follow the build's Luck
  BS.g = ''; BS.s = { Charm: ['terramity:lucky_dice', 'terramity:fateful_coin'] }; buildPage(); await wait(50);
  const t = document.querySelector('.bev') ? document.querySelector('.bev').innerText : '';
  if (!/Lucky Dice/.test(t) || !/Fateful Coin/.test(t)) bad.push('planner gambler: no expected-value lines for Lucky Dice and Fateful Coin: ' + t);
  if (!/×1\.13/.test(t)) bad.push('planner gambler: Lucky Dice at Luck 0 should average ×1.13 (20% of ×1.66): ' + t);
  BS.s = {}; BS.g = ''; }
