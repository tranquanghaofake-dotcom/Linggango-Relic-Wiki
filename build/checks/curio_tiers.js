// Curio tiers, layer 1 (docs/plans/2026-11-18-rank-all-curios.md): a curio the game test measured to help, whose text is only attribute numbers, gets a tier, Common at the lowest; one with a mechanic the test cannot see is left to layers 2 and 3.
{ const roles = ['ME', 'RA', 'MA', 'SU'], miss = [];
  for (const d of D) { if (d.r === 6 || !CM[d.id] || gCtx(d)) continue;
    const g = Math.max(...roles.map(r => gCurioScore(d, r, d.t) - 1)), t = CTIER[d.id];
    if (g > .005 && gPlain(d) && !t) miss.push(d.n);
    if (t && t[0] === 0 && !gPlain(d)) bad.push('tiers: ' + d.n + ' is Common by the measurement but its text has a mechanic the test cannot see');
    if (t && (t[0] < 0 || t[0] > 5)) bad.push('tiers: ' + d.n + ' has tier ' + t[0]);
    if (t && d.pe) bad.push('tiers: ' + d.n + ' is tiered from the measurement but still marked as an estimate'); }
  if (miss.length) bad.push('tiers: measured to help, no tier: ' + miss.slice(0, 6).join(', ') + (miss.length > 6 ? ' (+' + (miss.length - 6) + ')' : '')); }
// the reason line: every curio still rated from its text says what its text is about
{ for (const d of D) if (d.pe && !gUnrKind(d)) bad.push('tiers: no reason for ' + d.n); }
// crit chance, crit damage and lifesteal are stats, not a chance of something: the curios that only add them are ranked by what the test measured
{ for (const n of ['Hemograft Needle', 'Energy Focuser', 'Deadshot Brooch']) { const d = D.find(x => x.n === n); if (!d) bad.push('tiers: no ' + n); else if (!gPlain(d)) bad.push('tiers: ' + n + ' is plain stats but gPlain says it is not'); else if (!CTIER[d.id]) bad.push('tiers: ' + n + ' has no tier'); } }
