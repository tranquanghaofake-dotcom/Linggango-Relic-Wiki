// Bosses: Keeper and side-boss stats, names, attacks, drops and summons. Ported from the audit fix pass of 2026-10-31 (pending
// invariants, groups boss-stats, wiki-patches and app-js); each block names the finding it guards. Runs in the page (check.js:
// `bad`, `acts` and `await patchJSON(file)` in scope).
const SIDES = Object.keys(SIDEB), main = () => document.getElementById('main');
// the cell of each stat-table row (in SSTAT row order) under the column whose head matches re
const colCells = re => { const t = [...main().querySelectorAll('table')].find(t => re.test(t.rows[0]?.innerText || '')); if (!t) return [];
  const i = [...t.rows[0].cells].findIndex(c => re.test(c.innerText)); return [...t.rows].slice(1).map(r => r.cells[i]?.innerText || ''); };
// data-bosses-mech-01/03: Armageddon's Hardmode x2.1 skips every entity in forge:armageddon_bosses (their stats are the pre-Hardmode ones);
// ender_dragon_configuration sets the Dragon to vanillaHp x defaultHpMultiplier and defaultArmorValue, on BST and VBI alike;
// no Keeper, Dragon, Wither or Warden page offers a Hardmode alternate
{ const tag = new Set((await patchJSON('armageddon_bosses.json')).values.map(v => v.includes(':') ? v : 'minecraft:' + v)), dc = await patchJSON('ender_dragon_configuration.json');
  for (const [k, b] of Object.entries(BST)) { if (k[0] === '_' || !b.phases) continue;
    for (const ph of b.phases) if (tag.has(ph.entity) && ph.hardmode != null) bad.push('Hardmode on an armageddon_bosses entity ' + k + ' ' + ph.entity);
    if (b.phases.every(ph => tag.has(ph.entity)) && JSON.stringify(b.effective) !== JSON.stringify(b.phases[0].pre_hardmode)) bad.push('boss effective is not pre_hardmode ' + k); }
  const d = BST.ender_dragon?.effective;
  if (!d || d.hp !== dc.vanillaHp * dc.defaultHpMultiplier || d.armor !== dc.defaultArmorValue) bad.push('ender dragon stats ' + JSON.stringify(d) + ' not ender_dragon_configuration');
  if (VBI.dragon.hp !== d?.hp) bad.push('VBI.dragon.hp ' + VBI.dragon.hp + ' != BST.ender_dragon ' + d?.hp);
  for (const k of new Set([...KEEPERS(), 'ender_dragon', 'wither', 'warden'])) { history.replaceState(null, '', '#boss/' + k); render();
    if (/\b(in|before) Hardmode\b/.test(main().innerText)) bad.push('Hardmode alternate shown on #boss/' + k); } }
// data-bosses-mech-02: the pack's soul_bosses pins (health, armor, damage) reach the side-boss stats, and a pinned boss's page shows
// no Hardmode alternate for its health or armor
{ const SB = await patchJSON('soul_bosses.json'), rows = Object.values(SSTAT).flat();
  for (const [e, t] of Object.entries(SB)) { const r = rows.find(x => x.entity === e); if (!r) continue;   // e.g. the sandworm has no side page
    if (r.hp !== t.health || (t.armor >= 0 && r.armor !== t.armor) || !r.pinned || r.dmg_mult !== t.damage) bad.push('soul_bosses pin not in SSTAT: ' + e); }
  for (const n of SIDES.filter(n => (SSTAT[n] || []).some(r => r.pinned))) { history.replaceState(null, '', '#side/' + encodeURIComponent(n)); render();
    for (const re of [/HEALTH/i, /ARMOR/i]) colCells(re).forEach((c, i) => { if (SSTAT[n][i]?.pinned && /Hardmode/.test(c)) bad.push('#side/' + n + ' pinned ' + SSTAT[n][i].entity + ' ' + re.source + ' shows a Hardmode alternate'); }); } }
// data-bosses-mech-04: melee multipliers of the pack (Swampjaw x3 of 12, Rosalyne x3.5 of 24)
if (SSTAT.Swampjaw?.[0].dmg !== 36) bad.push('Swampjaw dmg ' + SSTAT.Swampjaw?.[0].dmg + ' (pack melee x3 of 12 = 36)');
if (SSTAT.Rosalyne?.[0].dmg !== 84) bad.push('Rosalyne dmg ' + SSTAT.Rosalyne?.[0].dmg + ' (pack melee x3.5 of 24 = 84)');
// data-bosses-mech-05: every side-boss row says whether it is a Monster (Hardmode scales only Monsters); the non-Monster bosses show no
// Hardmode alternate on their Attack column
{ for (const [n, rows] of Object.entries(SSTAT)) for (const r of rows) if (typeof r.monster !== 'boolean') bad.push('SSTAT ' + n + ' ' + r.entity + ' has no boolean monster');
  const rows = Object.values(SSTAT).flat();
  for (const e of ['eeeabsmobs:realm_warden', 'eeeabsmobs:nameless_guardian', 'eeeabsmobs:relic_annihilator', 'eeeabsmobs:immortal', 'traveloptics:the_nightwarden', 'goety:ender_keeper']) {
    const n = Object.keys(SSTAT).find(n => SSTAT[n].some(x => x.entity === e)), r = n && SSTAT[n].find(x => x.entity === e);
    if (!r || r.monster !== false) { bad.push(e + ' must be monster:false (not a Monster subclass)'); continue; }
    if (!SIDEB[n]) continue; history.replaceState(null, '', '#side/' + encodeURIComponent(n)); render();
    if (/Hardmode/.test(colCells(/ATTACK/i)[SSTAT[n].indexOf(r)] || '')) bad.push('#side/' + n + ' Attack shows a Hardmode alternate for the non-Monster ' + e); } }
// 2026-11-01, stats.py: every side boss has a stats row but Geburah (its fight is not on health). A lookup by the bare registry name
// took goety's "endersent" for Legendary Monsters' Endersent and dropped its row; the Ice Hermit's row needs RevelationFix (nested
// in GoetyRevelation's jar) read
for (const n of SIDES) if (n !== 'Geburah' && !(SSTAT[n] || []).length) bad.push('side boss without a stats row: ' + n);
// data-bosses-mech-07: Apostle's toughness is the pack's apostleToughness (66)
if (SSTAT.Apostle?.[0].tough !== 66) bad.push('Apostle tough ' + SSTAT.Apostle?.[0].tough + ' (pack apostleToughness = 66)');
// data-bosses-mech-08: Rosalyne always drops an enchanted book (the books pool rolls 1-2, every entry a book)
{ const d = SIDEB.Rosalyne?.drops.find(x => x.id === 'minecraft:book'); if (!d || d.chance !== '100%') bad.push('Rosalyne Enchanted Book chance ' + (d && d.chance)); }
// ui-desktop-22: the Keepers carry the game's names (Armageddon's lang entity.armageddon_mod.*, § codes stripped); the wiki may drop a
// leading 'The' and lower-case 'Of', nothing else; BINFO's names and the Discord's phase names agree with BST
{ const KN = {famine: 'The Famine, First Calamity', chaos: 'The Chaos, Second Calamity', discord: 'The Discord, Fourth Calamity', arion: 'Arion, Tyrant of the Emerald Wrath', eldorath: 'Eldorath the Ancient Builder', zoranth_forgotten: 'Zoranth, the Forgotten One', elvenite_paladin: 'The Elvenite Paladin', vaedric: 'Vaedric, the Fallen Wanderer', zoranth_newborn: 'Zoranth, Newborn of the Zenith', nyxaris: 'Nyxaris, the Veil of Oblivion'};
  const norm = s => s.toLowerCase().replace(/§./g, '').replace(/^the /, '');
  for (const k in BST) { if (k[0] === '_' || !BST[k].name) continue; const want = BINFO[k]?.name || KN[k]; if (want && norm(BST[k].name) !== norm(want)) bad.push(`keeper name ${k}: '${BST[k].name}' is not the game's '${want}'`); }
  const PH = {the_famine: 'famine', the_chaos: 'chaos', bringer_of_doom: 'bringer_of_doom'};
  for (const ph of BINFO.discord?.ph || []) if (PH[ph.e] && BST[PH[ph.e]] && norm(BST[PH[ph.e]].name) !== norm(ph.name)) bad.push(`BST.${PH[ph.e]}.name '${BST[PH[ph.e]].name}' is not the game's '${ph.name}'`); }
// detail-pages-checks-10: attack cards are unique on every boss and side page, no raw entity-id phase heading, one entity per attack
// and a title on every phase of a multi-entity boss
{ for (const h of [...KEEPERS().concat('ender_dragon').map(k => '#boss/' + k), ...SIDES.map(n => '#side/' + encodeURIComponent(n))]) { history.replaceState(null, '', h); render();
    const n = [...main().querySelectorAll('.batk b')].map(x => x.textContent.trim());
    if (new Set(n).size !== n.length) bad.push('duplicate attack cards on ' + h + ': ' + n.filter((x, i) => n.indexOf(x) !== i).join(', '));
    for (const t of main().querySelectorAll('h3')) if (t.nextElementSibling?.classList.contains('batks') && /\bP \d\b|bloodp|tyrantofthe/i.test(t.textContent)) bad.push('raw entity-id phase heading on ' + h + ': ' + t.textContent); }
  for (const k in BINFO) { const seen = new Set();
    for (const ph of BINFO[k].ph || []) for (const a of ph.at || []) { if (seen.has(a.n)) bad.push('boss_info.json ' + k + ': attack ' + a.n + ' under two entities'); seen.add(a.n); }
    if ((BINFO[k].ph || []).filter(x => x.at?.length).length > 1 && BINFO[k].ph.some(x => x.at?.length && !x.title)) bad.push('boss_info.json ' + k + ': a phase entity with no title'); } }
// data-bosses-mech-06: a summon ingredient a boss's treasure bag gives says where it comes from, and is never called a common material
{ const bag = {}; for (const k in BINFO) for (const x of BINFO[k].drops || []) (bag[x.id] = bag[x.id] || []).push(x.via);
  for (const k in SUM) for (const x of SUM[k].ings || []) {
    if (!x.from && (bag[x.id] || []).includes('treasure bag')) bad.push(`summons.json ${k}: ${x.id} has no source but boss_info.json lists it in a treasure bag`);
    if (/^treasure bag:/i.test(x.from || '')) bad.push(`summons.json ${k}: ${x.id} from '${x.from}'`); }
  for (const k of KEEPERS()) { history.replaceState(null, '', '#boss/' + k); render(); const t = main().querySelector('table.sumings'); if (!t) continue;
    for (const r of [...t.rows].slice(1)) { const id = SUM[k]?.ings?.[r.rowIndex - 1]?.id;
      if (id && bag[id] && /common material/i.test(r.cells[1]?.textContent || '')) bad.push(`#boss/${k}: ${id} shown as 'common material' but boss_info.json lists it as a drop`); } } }
// detail-pages-checks-07: no '#' tag or namespaced id in a summons.json label
for (const k in SUM) for (const l of [SUM[k].ings, SUM[k].infinite?.ings, ...(SUM[k].routes || []).map(r => r.ings)]) for (const x of l || []) if (/#|[a-z]:[a-z]/.test(x.n)) bad.push(`summons.json ${k}: label '${x.n}'`);
// own-1: every side-boss landscape (PIMG.side) is an opaque scene at least 320 px wide, not a sprite
for (const [n, src] of Object.entries(PIMG.side)) { const i = new Image(); i.src = src;
  if (!await i.decode().then(() => 1, () => 0)) { bad.push('PIMG.side ' + n + ' does not decode'); continue; }
  if (i.naturalWidth < 320) bad.push(`PIMG.side ${n} is ${i.naturalWidth} px wide (a sprite, not a scene)`);
  const c = new OffscreenCanvas(i.naturalWidth, i.naturalHeight).getContext('2d'); c.drawImage(i, 0, 0);
  const d = c.getImageData(0, 0, i.naturalWidth, i.naturalHeight).data; for (let j = 3; j < d.length; j += 4) if (d[j] !== 255) { bad.push('PIMG.side ' + n + ' has transparent pixels'); break; } }
// data-bosses-mech-09: AE2.gates holds exactly the AE2-family items of the pack's gated/<tier> tags (ae2_gated.json), at their tag's Act
{ const AG = await patchJSON('ae2_gated.json');
  for (const [a, g] of Object.entries(AG.acts)) for (const [id, n] of Object.entries(g.items)) if (!(AE2.gates[a] || []).includes(n)) bad.push(`AE2 gate: ${id} (${n}, gated/${g.tier}) missing from Act ${a}`);
  for (const [a, xs] of Object.entries(AE2.gates)) for (const n of xs) if (!Object.values(AG.acts[a]?.items || {}).includes(n)) bad.push(`AE2 gate: ${n} at Act ${a} is not in gated/${AG.acts[a]?.tier}`); }
// app-logic-02: a Keeper page lists the side bosses of its own stretch of The Path (not its own name), and Previous links the Keeper before it
{ const K = KEEPERS();
  for (const [i, k] of K.entries()) { history.replaceState(null, '', '#boss/' + k); render(); const exp = SIDEV[k] ?? ORDER[ORDER.indexOf(bossPath(k)) - 1];
    const sec = [...main().querySelectorAll('section')].find(s => /Side bosses at this point/.test(s.querySelector('h2')?.textContent || ''));
    if (sec) for (const b of sec.querySelectorAll('tr td:first-child b')) { const nm = b.textContent.trim(), row = BOSSR.find(r => r[0] === nm);
      if (!row || row[1] !== exp || nm === bossName(k)) bad.push(`#boss/${k}: side row ${nm} (Act ${row && row[1]}, want ${exp})`); }
    const pa = [...document.querySelectorAll('.pnx a')].find(a => /Previous/.test(a.textContent));
    if (i > 0 && pa?.getAttribute('href') !== '#boss/' + K[i - 1]) bad.push(`#boss/${k}: previous ${pa && pa.getAttribute('href')}, want #boss/${K[i - 1]}`); } }
