// Build planner: the starter builds (bPreset, 2026-11-23). Runs in the page (check.js: `bad` and `acts` in scope).
// Each starter build is graded 0-5, one point a rule, on the measured model the Equipment -> Curios tiers use (gBuildVal):
//  1 no trap: nothing past the Act, no condition on what it gives (bCtx), no cost its text states (bDraw), nothing measured to hurt the playstyle
//  2 no waste: one Looting Charm at most, no copy that does not stack, no third copy, no ladder curio switched off
//  3 full: at least 85% of the slots that have a curio for this playstyle are filled
//  4 the best are in: 4 of the 5 best measured curios for the playstyle at this Act (by themselves, that fit the slots together) are worn (Movement, Utility,
//    Gambler: 70% of what is worn is given that playstyle by its text, or adds slots, or is the Looting Charm)
//  5 no easy swap: no measured curio does nothing by itself and for the build, and swapping one for a curio not worn never adds 2% or more
// The grade must average 4.5 or more over every Act and playstyle checked, and none may be under 4. Set PRESET_ACTS to grade others.
{ const RID = new Set(Object.values(RQRING)), M = ['ME', 'RA', 'MA', 'SU', 'HE', 'TA'], grades = [], at = (typeof PRESET_ACTS !== 'undefined' ? PRESET_ACTS : [0, 4, 8, 12]);
  // for reference, not graded (PRESET_DUMP only): how many community best-in-slot picks (patches/community_picks.json) the build wears
  const COMM = typeof PRESET_DUMP !== 'undefined' && typeof patchJSON !== 'undefined' ? (await patchJSON('community_picks.json')).picks : null;
  const ringBefore = BS.g, pBefore = BS.p, sBefore = JSON.stringify(BS.s), dump = typeof PRESET_DUMP !== 'undefined';
  for (const a of at) for (const role of [...Object.keys(ROLE), 'RNG']) {
    BS.p = a; BS.g = ''; bPreset(role);
    const items = Object.entries(BS.s).flatMap(([k, v]) => v.map(id => [k, id])).filter(x => !RID.has(x[1])), ids = items.map(x => x[1]);
    const m = M.includes(role), vr = m ? role : 'TA', solo = d => gPart(d) ? gBuildVal([[gPart(d), 1]], vr, a) : null;
    const valid = d => bAvail(d) && !d.inv && bRing(d) && !RID.has(d.id) && !bCtx(d) && !bDraw(d) && !(solo(d) < -.01);
    const why = [];
    // 1 no trap
    const trap = ids.filter(id => { const d = BYID[id]; return !bAvail(d) || bCtx(d) || bDraw(d) || solo(d) < -.01 });
    if (trap.length) why.push('trap: ' + trap.map(id => BYID[id].n).join(', '));
    // 2 no waste
    const cnt = {}, lf = skLadder(ids); ids.forEach(id => cnt[id] = (cnt[id] || 0) + 1);
    const waste = Object.keys(cnt).filter(id => cnt[id] > 2 || cnt[id] > 1 && !(bStk(id) && SK.i[id].s !== 'u')).concat(ids.filter(id => lf[id] === 0));
    if (ids.filter(id => LOOTRX.test(BYID[id].n)).length > 1) waste.push('two Looting Charms');
    if (waste.length) why.push('waste: ' + waste.map(id => BYID[id] ? BYID[id].n : id).join(', '));
    // 3 full
    const fit = d => role === 'RNG' ? bRng(d) : d.ro.includes(role) || m && solo(d) > .002, caps = bCaps();
    let want = 0, got = 0; for (const k in caps) { const n = D.filter(d => valid(d) && fit(d) && bFits(d, k)).length; want += Math.min(caps[k], n); got += Math.min(caps[k], (BS.s[k] || []).length) }
    if (got < .85 * want) why.push(`full: ${got} of ${want} slots`);
    // 4 the best are in
    if (m) { const all = D.filter(d => valid(d) && gPart(d) && !Object.keys(slotAdds(d)).length).map(d => [d, solo(d)]).sort((x, y) => y[1] - x[1]), room = {}, top = [];
      for (const [d] of all) { if (top.length >= 5) break; const k = d.sl.find(s => caps[s] > (room[s] || 0)); if (k) { room[k] = (room[k] || 0) + 1; top.push(d) } }
      // a top curio left out because a better one of its ladder is worn is not missing
      const miss = top.filter(d => !ids.includes(d.id) && !(SK.i[d.id] && SK.i[d.id].l && ids.some(j => SK.i[j] && SK.i[j].l && SK.i[j].l[0] === SK.i[d.id].l[0])));
      if (miss.length > 1) why.push('best missing: ' + miss.map(d => d.n).join(', '));
    } else { const ok = ids.filter(id => { const d = BYID[id]; return fit(d) || Object.keys(slotAdds(d)).length || LOOTRX.test(d.n) }).length;
      if (ok < .7 * ids.length) why.push(`off-role: ${ids.length - ok} of ${ids.length}`) }
    // 5 no easy swap
    if (m) { const V = xs => { const l = skLadder(xs); return gBuildVal(xs.map(id => [gPart(BYID[id]), l[id] ?? 1]), vr, a) }, v0 = V(ids), meas = items.filter(x => gPart(BYID[x[1]]) && !Object.keys(slotAdds(BYID[x[1]])).length && !LOOTRX.test(BYID[x[1]].n));
      const cand = D.filter(d => valid(d) && gPart(d) && solo(d) > .002 && !Object.keys(slotAdds(d)).length);
      let dead = [], swap = null;
      for (const [k, id] of meas) { const i = ids.indexOf(id), rest = ids.filter((_, j) => j !== i);
        if (v0 - V(rest) < .001 && !(solo(BYID[id]) > .002) && !BYID[id].ro.includes(role)) dead.push(BYID[id].n);
        for (const d of cand) { if (ids.includes(d.id) || !bFits(d, k)) continue; const g = V([...rest, d.id]) - v0; if (g > Math.log(1.02) && (!swap || g > swap[2])) swap = [BYID[id].n, d.n, g] } }
      if (dead.length) why.push('does nothing: ' + dead.join(', '));
      if (swap) why.push(`swap ${swap[0]} for ${swap[1]}: +${Math.round((Math.exp(swap[2]) - 1) * 100)}%`) }
    else if (ids.some(id => !(fit(BYID[id]) || Object.keys(slotAdds(BYID[id])).length || LOOTRX.test(BYID[id].n)))) why.push('worn without a reason');
    const g = 5 - why.length; grades.push([a, role, g, why]);
    if (COMM) { const has = new Set(ids), av = new Set(D.filter(d => bAvail(d) && !d.inv && bRing(d)).map(d => d.id));
      const bis = Object.keys(COMM).filter(id => COMM[id].t === 'bis' && COMM[id].r.includes(role) && av.has(id) && !(COMM[id].x || []).some(x => av.has(x)));
      if (bis.length) console.log(`  community: ${bis.filter(id => has.has(id)).length}/${bis.length} worn; missing ${bis.filter(id => !has.has(id)).map(id => BYID[id].n).join(', ')}`) }
    if (dump) console.log(`Act ${a} ${role}: ${g}/5 ${why.join(' | ')}`);
  }
  const avg = grades.reduce((s, x) => s + x[2], 0) / grades.length, low = grades.filter(x => x[2] < 4);
  if (dump) console.log('average ' + avg.toFixed(2) + ' over ' + grades.length);
  if (avg < 4.5) bad.push('starter builds average ' + avg.toFixed(2) + '/5 (under 4.5)');
  low.forEach(([a, r, g, w]) => bad.push(`starter build Act ${a} ${r}: ${g}/5 (${w.join(' | ')})`));
  // hard rules whatever the grade: no trap, no second Looting Charm, nothing past the Act
  grades.filter(x => x[3].some(w => /^trap/.test(w))).forEach(([a, r, , w]) => bad.push(`starter build Act ${a} ${r}: ${w.find(x => /^trap/.test(x))}`));
  BS.g = ringBefore; BS.p = pBefore; BS.s = JSON.parse(sBefore); }
// the whole-build model (gBuildVal) against what was sampled in game and read from the jars
{ const v = (ids, r, a) => Math.exp(gBuildVal(ids.map(id => [gPart(BYID[id]), 1]), r, a));
  // Luck: Lucky Dice with Gambler's Ring (Luck III) reads the Luck 3 sample of curio_chance.json (x1.329), alone the Luck 0 one (x1.123)
  const ld = v(['terramity:lucky_dice', 'terramity:gamblers_ring'], 'ME', 9), l0 = v(['terramity:lucky_dice'], 'ME', 9);
  if (Math.abs(ld - 1.329) > .01 || Math.abs(l0 - 1.123) > .01) bad.push(`Luck: Lucky Dice + Gambler's Ring x${ld.toFixed(3)} (want 1.329), alone x${l0.toFixed(3)} (want 1.123)`);
  if (Math.abs(v(['terramity:gamblers_ring'], 'ME', 9) - 1) > .02) bad.push("Luck: Gambler's Ring alone should add nothing");
  // armor: Brutality penetration and lethality count against the next Keeper's armor (melee); Goety Revelation's penetration does not run on player hits
  if (!(v(['brutality:warpslice_scabbard'], 'ME', 6) > 1.2)) bad.push('armor: Warpslice Scabbard (7 lethality, 20% penetration) adds under 20% at Act VI');
  // the same count gives the Curios tiers (gCurioScore): armor pierce curios the 0-armor test saw nothing of are tiered
  if (!CTIER['brutality:warpslice_scabbard'] || !CTIER['brutality:daemonium_sewing_kit']) bad.push('armor: Warpslice Scabbard or Daemonium Sewing Kit has no tier');
  if (Math.abs(v(['brutality:warpslice_scabbard'], 'MA', 6) - 1) > .02) bad.push('armor: penetration counted for spells, which skip armor');
  if (BYID['goety_revelation:the_needle'] && Math.abs(v(['goety_revelation:the_needle'], 'ME', 6) - 1) > .02) bad.push("armor: The Needle's Goety Revelation penetration counted");
  // dodge: Brutality's and Apothic's roll apart, each under its own cap
  if (Math.abs(gEHP({ arm: 0, tough: 0, hp: 0, kbr: 0, dtk: 0, at: { dodge_chance: [.3, 0], apo_dodge: [.3, 0] } }, 5) / gEHP({ arm: 0, tough: 0, hp: 0, kbr: 0, dtk: 0, at: {} }, 5) - 1 / .49) > .01) bad.push('dodge: 30% + 30% should avoid 51% of hits (1 - 0.7 x 0.7)'); }
