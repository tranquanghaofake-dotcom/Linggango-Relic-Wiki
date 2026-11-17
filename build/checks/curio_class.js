// curio-class (2026-11-17): a playstyle's own curio list holds only curios of that playstyle. The test swings a sword, so every
// "+X% damage dealt" curio read as a Melee curio (Eyepatch, Band of Power, the emblems of melee, ranged and magic damage), and a
// mask of minion slots or a spellbook whose swing landed as a vanilla jump critical (x1.5) read as one too; conditions the test
// pig met by itself (full health, no AI, other mobs near) were tiered. Now: a curio that raises one playstyle (gCurioRoles) is that
// playstyle's own; one that raises several is "shared", in its own view; a hit change is melee, ranged or all damage as its text
// or attributes say, and one nothing explains is not counted (gHitKind). Mage weapons are tiered by what they add (score - 1).
// Runs in the page (check.js: `bad` and `acts` in scope).
{ const last = acts[acts.length - 1], R = Object.keys(GROLE), byId = id => BYID[id] || D.find(d => d.id === id), o = new Set();
  // the three views of a playstyle never share a curio, own curios raise no other playstyle, shared ones raise two or more
  for (const a of [3, 6, last]) for (const r of R) {
    const own = gTiers(a, r, 'o').flatMap(x => x[1]), sh = gTiers(a, r, 's').flatMap(x => x[1]),
      any = gTiers(a, r, 'v').flatMap(x => x[1]);
    for (const d of own) { if (sh.includes(d) || any.includes(d)) o.add(`curio-class: ${d.n} is in two views of ${r} at Act ${a}`);
      const other = R.filter(x => x !== r && gCurioGain(d, x, a) >= GOWN); if (other.length) o.add(`curio-class: ${d.n} is ${r}'s own but raises ${other.join(', ')} too`); }
    for (const d of sh) { if (any.includes(d)) o.add(`curio-class: ${d.n} is shared and survival for ${r}`); if (gCurioRoles(d, a).length < 2) o.add(`curio-class: ${d.n} is shared but raises only ${gCurioRoles(d, a)}`); }
    for (const d of any) if (gOwn(d, r, a) || gShared(d, r, a)) o.add(`curio-class: ${d.n} is in the survival view of ${r} but raises its damage`);
    for (const [d] of [...gPool(a, r, 'o'), ...gPool(a, r, 's'), ...gPool(a, r, 'v')]) if (gCtx(d)) o.add(`curio-class: ${d.n} depends on "${gCtx(d)}" and is listed`);
    // each view is tiered among its own curios: the survival view keeps its curios when a strong damage curio joins the playstyle
    if (a === last && any.length < 15) o.add(`curio-class: the survival view of ${r} at Act ${a} holds only ${any.length} curios`); }
  // known curios, by what their text says they do (curio_measure.json numbers, Act XII)
  const want = [['terramity:eyepatch', 's'], ['terramity:band_of_power', 's'], ['confluence:avenger_emblem', 's'], ['confluence:destroyer_emblem', 's'],
    ['terramity:chthonic_cursemark', 's'], ['terramity:magma_stone', 'ME'], ['confluence:warrior_emblem', 'ME'],
    ['summonity:gobs_mask', 'SU'], ['traveloptics:chronicles_of_the_firelord', 'MA'], ['brutality:portable_quantum_thingamabob', 's'], ['uniqueaccessories:devils_eyeball', 's']];
  for (const [id, k] of want) { const d = byId(id); if (!d || !CM[id]) { o.add('curio-class: no curio ' + id); continue; }
    const rs = gCurioRoles(d, last), ok = k === 's' ? rs.length >= 2 && rs.includes('ME') && rs.includes('RA') : rs.length === 1 && rs[0] === k;
    if (!ok) o.add(`curio-class: ${d.n} raises ${rs.join(', ') || 'nothing'}, want ${k === 's' ? 'melee and ranged both (shared)' : k + ' only'}`); }
  // read in the jars (2026-11-17): Chthonic Shell Casing checks the distance to the target (> 3 m), not the kind of hit: shots and
  // spells, not melee; Apothic crit and Brutality lethality act on any damage the player causes, spells included
  { const d = byId('terramity:chthonic_shell_casing'), rs = d ? gCurioRoles(d, last).join() : '';
    if (rs !== 'RA,MA') o.add(`curio-class: Chthonic Shell Casing raises ${rs}, want Ranged and Mage (any hit from range)`);
    for (const id of ['brutality:portable_quantum_thingamabob', 'uniqueaccessories:devils_eyeball']) { const e = byId(id);
      if (!e || gCurioGain(e, 'MA', last) < GOWN) o.add(`curio-class: ${id} (lethality or Apothic crit, any hit) adds nothing to Mage`); } }
  // a "damage dealt" curio counts for spells as it does for a sword; a minion's hits are its own
  { const e = byId('terramity:eyepatch'), g = r => gCurioGain(e, r, last);
    if (Math.abs(g('ME') - g('MA')) > .005 || g('MA') < .3 || g('SU') !== 0) o.add(`curio-class: Eyepatch (x1.33 damage dealt) adds Melee ${g('ME')}, Mage ${g('MA')}, Summon ${g('SU')}`); }
  // a hit change nothing explains is not counted: Gob's Mask (minion slots, hit x1.5) adds nothing to Melee
  for (const id of ['summonity:gobs_mask', 'traveloptics:chronicles_of_the_firelord', 'uniqueaccessories:amplifier_stone']) { const d = byId(id);
    if (!d || gHitKind(d, CM[id]) !== '' || gCurioGain(d, 'ME', last) >= GOWN) o.add(`curio-class: ${id}'s unexplained x1.5 hit still counts for Melee`); }
  // the test's own conditions are not tiered: the pig at full health, with no AI, among other mobs
  for (const id of ['brutality:crowbar', 'oddaccessories:malice', 'brutality:greed']) { const d = byId(id); if (!d || !gCtx(d)) o.add(`curio-class: ${id} is tiered though the test pig met its condition`); }
  // Mage weapons by what they add: S is not most of the list (Act VI had 21 S of 22), and each tier is the gain's ratio
  for (const a of [6, last]) { const t = gTiers(a, 'MA', 'w'), n = t.reduce((s, x) => s + x[1].length, 0), top = t.top;
    if (!n || t[0][1].length * 2 > n) o.add(`curio-class: Mage weapons at Act ${a}: ${t[0][1].length} S of ${n}`);
    t.forEach(([k, xs], i) => xs.forEach(g => { const q = (g.sc.MA - 1) / (top - 1), want = GTIER_R.findIndex(f => q >= f);
      if (want !== i) o.add(`curio-class: ${g.n} is ${k} at Act ${a}, its gain says ${GTIER[want] ? GTIER[want][0] : '-'}`); })); }
  // the page: each view shows its own curios, and Summon has no shared view (no curio raises minions and another playstyle)
  const go = async h => { location.hash = h; await new Promise(r => setTimeout(r, 80)); render(); },
    shown = () => [...document.querySelectorAll('#main .gtl-list a.gtl')].map(t => D[+t.dataset.t]);
  for (const r of R) { const sh = gTiers(last, r, 's').flatMap(x => x[1]);
    await go(`#gear/${last}/${r}/c`); const btn = [...document.querySelectorAll('#main .gseg.subs a')].some(a => a.getAttribute('href').endsWith('/c/shared'));
    if (btn !== (r !== 'SU') || btn !== sh.length > 0) o.add(`curio-class: the shared button of ${r} is ${btn ? 'shown' : 'missing'} (${sh.length} shared)`);
    await go(`#gear/${last}/${r}/c/shared`); const xs = shown();
    if (xs.length !== sh.length || xs.some(d => !gShared(d, r, last))) o.add(`curio-class: the shared view of ${r} shows ${xs.length}, want ${sh.length}`); }
  await go('#gear');
  bad.push(...o); }
