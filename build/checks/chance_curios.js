// Chance curios counted at their expected value (gear.js GHITCODE / GTKCODE, 2026-11-18): the ones whose own text gives odds and size are tiered, marked as read from text.
{ const id = n => (D.find(d => d.n === n) || {}).id, tiered = d => ['ME', 'RA', 'MA', 'SU'].some(r => gTierOf(d, d.t, r, 'c'));
  for (const n of ['Lucky Dice', 'Nullifying Dice']) { const d = BYID[id(n)]; if (!d) bad.push('chance: no ' + n); else if (!tiered(d)) bad.push('chance: ' + n + ' has no tier although its odds and size are in its text'); }
  // no odds or size in the text: stays unranked rather than given a made-up number
  for (const n of ['Fuzzy Dice', 'Loaded Dice', "Slicer's Dice"]) { const d = BYID[id(n)]; if (d && tiered(d)) bad.push('chance: ' + n + ' is tiered but its text gives no odds to count'); }
  for (const k of Object.keys(GHITCODE)) if (!BYID[k]) bad.push('chance: GHITCODE names a curio that does not exist: ' + k);
  for (const k of Object.keys(GTKCODE)) if (!BYID[k] || !gEvNote(k)) bad.push('chance: ' + k + ' counts a damage-taken change with no note on its page'); }
