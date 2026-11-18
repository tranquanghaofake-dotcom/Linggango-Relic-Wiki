// Chance curios (2026-11-18): a dice, a coin or a proc is sampled in game (patches/curio_chance.json, window CCH; pack_audit/measure/import_chance.py): the mean over
// hundreds of swings and hits stands in for the single swing the first measurement could read.
{ const by = n => D.find(d => d.n === n), cc = n => CCH[(by(n) || {}).id], tiered = d => ['ME', 'RA', 'MA', 'SU'].some(r => gTierOf(d, d.t, r, 'c'));
  if (Object.keys(CCH).length < 80) bad.push('chance: only ' + Object.keys(CCH).length + ' curios sampled');
  for (const id in CCH) { if (!BYID[id]) bad.push('chance: ' + id + ' is not a curio of the wiki'); else if (!(CCH[id].n >= 200)) bad.push('chance: ' + id + ' has only ' + CCH[id].n + ' swings'); if (CCH[id].hs && !(CCH[id].hs > 0.2 && CCH[id].hs < 6)) bad.push('chance: ' + id + ' reads damage ×' + CCH[id].hs); }
  // what the sampling found must hold: Lucky Dice 20% True Crit for ×1.66 (×1.13 over the bare tester's mean), Fateful Coin hurts as it helps, Nullifying Dice cancels a share of hits
  const ld = cc('Lucky Dice'), fc = cc('Fateful Coin'), nd = cc('Nullifying Dice');
  if (!ld || !ld.hs || Math.abs(ld.hs - 1.13) > .06) bad.push('chance: Lucky Dice should read about ×1.13 damage dealt, got ' + (ld && ld.hs));
  if (!fc || !fc.hs || fc.hs < 1.15 || !fc.tk || !(fc.tk.melee > 1.3)) bad.push('chance: Fateful Coin should deal more and take more (melee), got ' + JSON.stringify(fc && [fc.hs, fc.tk]));
  if (!nd || !nd.tk || !(nd.tk.melee < 1)) bad.push('chance: Nullifying Dice should cut the damage taken, got ' + JSON.stringify(nd && nd.tk));
  // the Luck effect, not the Luck attribute, raises the odds (2026-11-18: Luck I and V on Lucky Dice read 29% and 73% True Crit; attribute 0, 5, 20 read the same)
  if (ld && ld.lk && !(ld.lk[ld.lk.length - 1][1] > ld.hs)) bad.push('chance: Lucky Dice should rise with the Luck effect');
  // a sampled curio is scored by the sample (no text-read number any more), and its page says so
  for (const n of ['Lucky Dice', 'Fateful Coin', 'Nullifying Dice']) { const d = by(n); if (!d) { bad.push('chance: no ' + n); continue; } if (!gChanceNote(d)) bad.push('chance: ' + n + ' has no sampled note'); if (/Read from its text, not measured/.test(gCurioMs(d))) bad.push('chance: ' + n + ' still says read from its text'); }
  if (!tiered(by('Lucky Dice'))) bad.push('chance: Lucky Dice has no tier although it is sampled'); }
