// Conditions (2026-11-18): a curio whose text needs a state is sampled in each of seven states (patches/curio_cond.json, window CCD; pack_audit/measure/import_cond.py).
// The size of the effect is measured; the share of the time a player is in the state is an assumption (patches/effect_uptime.json "states").
{ const by = n => D.find(d => d.n === n), ST = (UPTIME.states || {});
  const names = Object.keys(ST); if (names.length !== 7) bad.push('conditions: ' + names.length + ' state shares, want 7');
  for (const k of names) if (!(ST[k].share > 0 && ST[k].share < 1) || !ST[k].why) bad.push('conditions: state ' + k + ' needs a share between 0 and 1 and a reason');
  for (const id in CCD) { const x = CCD[id]; if (!BYID[id]) bad.push('conditions: ' + id + ' is not a curio of the wiki'); if (!x.cd || !x.cd.length) bad.push('conditions: ' + id + ' has no state'); for (const [s, h] of (x.cd || [])) { if (!ST[s]) bad.push('conditions: ' + id + ' names an unknown state ' + s); if (!(h > 0 && h < 8)) bad.push('conditions: ' + id + ' reads ×' + h + ' in ' + s); }
    // an effect the test meets by default (five or more states) is shown, never counted
    if (x.dfk && x.dfk.includes('hs') && x.hs) bad.push('conditions: ' + id + ' counts damage dealt although the test meets its condition by default'); for (const f of (x.dfk || [])) if (f.startsWith('tk:') && x.tk && x.tk[f.slice(3)]) bad.push('conditions: ' + id + ' counts damage taken (' + f.slice(3) + ') although the test meets its condition by default');
    // the counted effect is never larger than the largest state's (a share is below 1)
    const top = Math.max(...(x.cd || []).map(c => c[1]), 1), bot = Math.min(...(x.cd || []).map(c => c[1]), 1);
    if (x.hs && (x.hs > top + 1e-6 || x.hs < bot - 1e-6)) bad.push('conditions: ' + id + ' counts ×' + x.hs + ' outside its states (' + bot + ' to ' + top + ')'); }
  // the page says what was sampled, and a curio is not counted twice (chance and condition together stay inside both samples)
  const ids = Object.keys(CCD); if (ids.length < 10) bad.push('conditions: only ' + ids.length + ' curios changed in a state');
  // the known cases the test meets by default must stay out of the score: Rage Glove stacks up at once, Stillness Scarf stands still, Berserk Charm swings at half health
  for (const n of ['Stillness Scarf', 'Berserk Charm']) { const d = by(n), x = d && CCD[d.id]; if (x && !(x.dfk && x.dfk.length)) bad.push('conditions: ' + n + ' is met by default and must not be counted'); if (d && x && x.hs) bad.push('conditions: ' + n + ' counts ×' + x.hs); }
  for (const id of ids.slice(0, 20)) { const d = BYID[id]; if (d && !/By condition/.test(gChanceNote(d))) bad.push('conditions: ' + d.n + ' page does not say what the states gave'); } }
