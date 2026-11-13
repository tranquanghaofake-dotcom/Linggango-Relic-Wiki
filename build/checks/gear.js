// Equipment: scoring, stats, sets, tier lists and the gear pages' own text. Ported from the audit fix pass of 2026-10-31
// (pending invariants, groups gear-js and gear-pipeline); each block names the finding it guards. Runs in the page
// (check.js: `bad`, `acts` and `await patchJSON(file)` in scope).
const ALL = [...GE, ...GS], nm = g => g.id || g.k;
// gear-logic-combat-07: worn Resistance follows Linggango Fixes' curve (0.2 + 0.04444 a level) on gear too, not only on curios
for (let L = 1; L <= 5; L++) { const e = 0.2 + (L - 1) * 0.04444, a = gFxAt({fx: [{effect: 'minecraft:resistance', level: L, when: 'worn', who: 'self'}]}).resistance[1];
  if (Math.abs(a - e) > 1e-9) bad.push('worn resistance L' + L + ' ' + a); }
// gear-logic-combat-01: a measured curio's Goety attribute keeps its namespace (it was read as Iron's spell power)
for (const id in CM) for (const k in CM[id].d || {}) if (/^(goety|goety_revelation|goetyawaken|goety_cataclysm|bosgoety):/.test(k) && !GCK(k).includes('.')) bad.push('curio Goety key lost its namespace ' + id + ' ' + k);
// gear-logic-combat-02: every measured curio attribute has a display unit, and no percent change is beyond ±1000%
for (const id in CM) for (const k in CM[id].d || {}) { const u = gUnit(GCK(k));
  if (!['flat', 'pct', 'base', 'x10'].includes(u)) bad.push('curio unit missing ' + id + ' ' + k);
  if (u === 'pct' && Math.abs(CM[id].d[k]) > 10) bad.push('curio pct row beyond 1000% ' + id + ' ' + k); }
// gear-logic-combat-02: known 'Measured in game' rows print in the game's units (flat stays flat, percent stays percent)
for (const [id, want] of [['brutality:chocolate_bar', '+15% Movement Speed'], ['ars_elemental:summon_bangle', '+2 Summon Power']]) {
  const t = document.createElement('div'); t.innerHTML = BYID[id] ? gCurioMs(BYID[id]) : '';
  if (![...t.querySelectorAll('li')].some(li => li.textContent.trim().startsWith(want))) bad.push('curio measured row: ' + id + ' lacks ' + want + ' (' + t.textContent.trim().slice(0, 80) + ')'); }
// gear-logic-combat-06 / copy-docs-12: attribute units in gMod (dodge window in seconds, knockback resistance x10, percents)
for (const [k, v, w] of [['dodge_window', .5, '+0.5 Dodge Window'], ['overheal', .05, '+5% Overheal'], ['experience_gained', .1, '+10% XP Gained'], ['knockback_resistance', .1, '+1 Knockback Resistance']]) {
  const g = gMod(k, v, 0)[0]; if (g !== w) bad.push('gMod ' + k + ' = ' + g + ', want ' + w); }
// gear-logic-combat-06: a set page's knockback resistance is the sum of its pieces' rows
for (const s of GS) { if (!s.kbr) continue; const pc = s.ps.reduce((n, p) => n + +((gStats(p).find(r => r[1] === 'Knockback Resistance') || [0, 0, 0])[2]), 0);
  if (Math.abs(pc - gSetKbr(s)) > .05) bad.push('set kbr ' + s.n + ' ' + gSetKbr(s) + ' vs pieces ' + pc); }
// detail-pages-checks-12: mod names are trimmed (a trailing space put a space before the lead's comma)
for (const [k, v] of Object.entries(GNS)) if (v !== v.trim()) bad.push('GNS untrimmed ' + k);
// gated tooltips name the boss and the Act in full ('until  falls', 'Act Dragon')
{ const t = document.createElement('a'); document.body.appendChild(t);
  for (const g of ALL) if (g.ga) { t.dataset.t = (g.ps ? 's' : 'g') + g.ix; gearTip(t); const x = tip.textContent;
    if (/until\s+falls/.test(x)) bad.push('tip lock without boss: ' + g.n);
    if (/\bActs? Dragon\b|Outclassed from (?:Dragon|[IVX0])/.test(x)) bad.push('tip short Act: ' + g.n); }
  t.remove(); hideTip(); }
// gear-logic-combat-10: the verdict's span ends before the Act where the tier strip cuts the item
for (const g of ALL) { const v = gVerdict(g); if (!v) continue;
  const r = gMain(g), w = g.ps ? 'a' : 'w', as = acts.filter(x => oiA(x) >= oiA(g.a)), ts = as.map(x => gTierOf(g, x, r, w)), k = ts.findIndex((t, i) => i > 0 && (!t || t === 'D'));
  if (k > 0) { const body = v.split('Replace it by')[0];
    if (as.slice(k).some(x => [' ', '.', ' ('].some(e => body.includes(' ' + actL(x) + e)))) bad.push('verdict span past the strip: ' + g.n); } }
// data-gear-01: no disabled item and no set of disabled pieces in a tier list
{ const o = new Set(); for (const a of acts) for (const r of Object.keys(GROLE)) for (const w of ['w', 'a']) for (const [, xs] of gTiers(a, r, w)) for (const g of xs)
  if (gHidden(g) || (g.ps && g.ps.every(p => p.ob && p.ob[0] === '!'))) o.add('hidden item listed: ' + g.n + ' Act ' + a + ' ' + r); bad.push(...o); }
// data-gear-01: the pack disables Mystical Agriculture armor: every piece carries a '!' note and none is listed
{ const MA = new Set(['inferium', 'prudentium', 'tertium', 'imperium', 'supremium', 'awakened_supremium'].flatMap(m => ['helmet', 'chestplate', 'leggings', 'boots'].map(s => 'mysticalagriculture:' + m + '_' + s))), o = new Set();
  for (const id of MA) { const g = GBY[id]; if (!g || !(g.ob || '').startsWith('!')) o.add('MA armor without a ! note: ' + id); }
  for (const a of acts) for (const r of Object.keys(GROLE)) for (const [, xs] of gTiers(a, r, 'a')) for (const x of xs) if ((x.ps ? x.p : [x.id]).some(i => MA.has(i))) o.add('pack-disabled MA armor listed: ' + x.n);
  bad.push(...o); }
// ui-desktop-09: the gear search marks later-Act items, lists the usable ones first, prints the count, offers Show more when cut
{ const keep = GALL; GALL = false;
  for (const q of ['sword', 'bow']) for (const a of acts) { const xs = gMatch(q, a), t = document.createElement('template'); t.innerHTML = gSearch(xs, a, 'ME');
    let late = false; [...t.content.querySelectorAll('.gsr>a')].forEach((n, i) => { const L = oiA(xs[i].a) > oiA(a);
      if (L !== !!n.querySelector('.glater')) bad.push(`search ${q} Act ${a}: ${xs[i].n} later-Act mark ${!L}`);
      if (L) late = true; else if (late) bad.push(`search ${q} Act ${a}: usable ${xs[i].n} after a later one`); });
    if (!(t.content.querySelector('.gsn')?.textContent || '').includes(String(xs.length))) bad.push(`search ${q} Act ${a}: no match count`);
    if (xs.length > 80 && !t.content.querySelector('[data-gall]')) bad.push(`search ${q} Act ${a}: cut at 80 with no Show more`); }
  GALL = keep; }
// phone-10: a curio tile in the gear Curios tab is one frame (no .slot inside .gtl)
{ history.replaceState(null, '', '#gear/0/ME/c'); render(); if (document.querySelector('#main .gtl>.slot')) bad.push('curio tile frame inside a frame (.gtl>.slot)'); }
// data-gear-04: a single-recipe gear piece never sits before a gear ingredient of its recipe
for (const g of GE) if (g.rc && g.rc.length === 1 && !g.lt) for (const y of g.rc[0].i || [])
  if (typeof y === 'string' && y !== g.rc[0].t && y !== g.id && GBY[y] && oiA(GBY[y].a) > oiA(g.a)) bad.push(`${g.n} at Act ${g.a} needs ${GBY[y].n} from Act ${GBY[y].a}`);
// data-gear-04 / data-curios-03: an item only a boss drops (boss_only_items.json, at the Act of the earliest boss that drops it) bounds the
// single-recipe gear and the crafted curios made from it; and none of those items also drops from a vanilla mob
{ const ONLY = await patchJSON('boss_only_items.json'), out = new Set(), ok = a => a === 6.1 || a === 6.2 ? ORDER.indexOf(6) + Math.round((a - 6) * 10) / 10 * 3 : ORDER.indexOf(a);
  const dep = BGRAPH.dep, DROP = {}, put = (it, a) => { if (it in ONLY && !/treasure_pouch/.test(it) && (DROP[it] === undefined || ok(a) < ok(DROP[it]))) DROP[it] = a; };
  BOSSR.forEach(r => { if (r[0] in BACT && r[0] in dep) (r[4] || []).forEach(it => put(it, BACT[r[0]])); });
  Object.entries(SIDEB).forEach(([n, s]) => { if (n in BACT && n in dep) (s.drops || []).forEach(x => put(x.id, BACT[n])); });
  BEXTRA.forEach(x => { if (x[0] in BACT) (x[4] || []).forEach(it => put(it, BACT[x[0]])); });
  Object.entries(ONLY).forEach(([it, ts]) => { if (ts.some(t => t.startsWith('minecraft:entities/'))) out.add(`boss_only_items.json: ${it} also drops from a vanilla mob`); });
  D.forEach(d => { if (d.g === 'Craft' && d.gr) d.gr.c.forEach(c => { if (c && !c[1] && c[0] in DROP && ok(d.t) < ok(DROP[c[0]])) out.add(`${d.n} at Act ${d.t} needs ${c[0]}, only a boss at Act ${DROP[c[0]]} drops it`); }); });
  GE.forEach(g => { if (g.rc && g.rc.length === 1 && !g.lt) (g.rc[0].i || []).forEach(y => { if (typeof y === 'string' && y !== g.rc[0].t && y in DROP && ORDER.indexOf(g.a) < ok(DROP[y])) out.add(`${g.n} at Act ${g.a} needs ${y}, only a boss at Act ${DROP[y]} drops it`); }); });
  bad.push(...out); }
// data-gear-02 / ui-desktop-05: armor families are one set each with all their pieces, with no split leftovers; set keys are unique;
// no two one-piece sets of a mod share a stem
{ const fam = {'mowziesmobs:geomancer': 4, 'mekanism:mekasuit': 4, 'ad_astra:space_suit': 4, 'ad_astra:netherite_space_suit': 4, 'mekanism:hazmat': 4, 'mekanism:scuba': 2, 'alexscaves:darkness': 2, 'create:copper_diving': 3, 'create:netherite_diving': 3, 'immersive_armors:robe': 4, 'bloodmagic:living': 4};
  const left = {'mowziesmobs:geomancer': ['mowziesmobs:geomancer_'], 'mekanism:mekasuit': ['mekanism:mekasuit_'], 'ad_astra:space_suit': ['ad_astra:space'], 'ad_astra:netherite_space_suit': ['ad_astra:netherite_space'], 'mekanism:hazmat': ['mekanism:hazmat_'], 'mekanism:scuba': ['mekanism:scuba_'], 'alexscaves:darkness': ['alexscaves:of_darkness', 'alexscaves:cloak_of_darkness', 'alexscaves:hood_of_darkness'], 'create:copper_diving': ['create:copper_backtank', 'create:copper_diving_'], 'create:netherite_diving': ['create:netherite_backtank', 'create:netherite_diving_'], 'immersive_armors:robe': ['immersive_armors:robe_'], 'bloodmagic:living': ['bloodmagic:living']};
  for (const [k, n] of Object.entries(fam)) { const s = GS.filter(x => x.k === k);
    if (s.length !== 1 || s[0].p.length !== n) bad.push('armor family ' + k + ': ' + s.length + ' sets, ' + (s[0] ? s[0].p.length : 0) + ' pieces, want 1 set of ' + n);
    for (const st of left[k]) for (const x of GS) if (x.k !== k && x.k.startsWith(st)) bad.push('split leftover of ' + k + ': ' + x.k); }
  if (new Set(GS.map(s => s.k)).size !== GS.length) bad.push('GS keys not unique');
  const SW = /^(helmet|chestplate|leggings|boots|hood|robe|robes|cap|tunic|pants|crown|mask|greaves|sabatons|hat|chest|legs|feet|head|armor|armour|helm|plate|leggins|shoes|gown|tank|bodyarmor|suit|backtank|beads|belt|sandals|cloak|of)$/;
  const stem = i => { const [ns, n] = i.split(':'); return ns + ':' + n.split('_').filter(t => !SW.test(t)).join('_').replace(/(helmet|plate|leggings|boots)$/, ''); }, st = {};
  for (const s of GS.filter(x => x.p.length === 1)) { const q = stem(s.p[0]); if (st[q]) bad.push('one-piece sets with one stem: ' + st[q] + ' / ' + s.k); st[q] = s.k; } }
// data-gear-03: no visible gear shows a recipe with an item from a mod the pack lacks; never-loaded recipes stay hidden
{ const OK = new Set(['minecraft', 'forge', 'c', 'kubejs']);
  for (const g of GE) { if (gHidden(g)) continue; for (const r of g.rc || []) for (const x of r.i.slice(1)) if (typeof x === 'string' && !x.startsWith('#')) { const ns = x.split(':')[0]; if (!OK.has(ns) && !(ns in GNS)) bad.push(g.id + ' recipe needs ' + x + ' (mod not in the pack)'); } }
  for (const id of ['somakespells:tide_piercer', 'somakespells:trumpet_axe', 'animus:hand_of_death']) if (!GBY[id] || !(GBY[id].ob || '').startsWith('!')) bad.push(id + ' needs an absent mod but is not marked !');
  for (const id of ['minecraft:wooden_sword', 'minecraft:wooden_axe']) if (GBY[id] && (GBY[id].rc || []).length) bad.push(id + " shows the pack's forge:false stub recipe"); }
// data-gear-07: the Stats show what the held weapon reads in game: (base + added) x (1 + multiplier) against the measured hit and speed
for (const g of GE) { const m = g.ms; if (!m || m.st || !(m.ad > 1)) continue; const at = g.at || {}, A = at.attack_damage || [0, 0], S = at.attack_speed || [0, 0];
  if (g.dmg != null && Math.abs(m.hit - m.ad) <= .15 * m.ad && Math.abs((g.dmg + A[0]) * (1 + A[1]) - m.ad) > .05 * m.ad) bad.push('Stats differ from the measured attack damage: ' + g.id);
  if (g.spd != null && m.as && Math.abs((g.spd + S[0]) * (1 + S[1]) - m.as) > .05 * m.as) bad.push('Stats differ from the measured attack speed: ' + g.id); }
// data-gear-08: fire on release is an enchantment's (Flame on the arrow, Fire Aspect), never the item's
for (const g of GE) if ((g.fx || []).some(r => r.when === 'release' && r.fire !== undefined)) bad.push('release row with a fire value: ' + g.id);
// data-gear-09 / copy-docs-06: gear names follow the pack's renameItem names (renames.json), sets included
{ const RN = await patchJSON('renames.json');
  for (const id in RN) { const g = GBY[id]; if (g && g.n.replace(/ \(Lv \d+\)$/, '') !== RN[id]) bad.push('gear name ignores the pack rename: ' + id + ' ' + g.n); }
  for (const [id, n] of [['quark:forgotten_hat', 'Stinky Hat'], ['minecraft:leather_chestplate', 'Animal Leather Chestplate'], ['mekanismtools:bronze_sword', 'Concentrated Bronze Sword']]) if (GBY[id]?.n !== n) bad.push('rename ' + id + ' ' + GBY[id]?.n);
  for (const [k, n] of [['minecraft:leather', 'Animal Leather'], ['mekanismtools:bronze', 'Concentrated Bronze']]) { const s = GS.find(x => x.k === k); if (!s || !s.n.startsWith(n)) bad.push('set rename ' + k + ' ' + s?.n); } }
// data-gear-10: every armor piece is a piece of exactly one set
{ const c = {}; GS.forEach(s => s.p.forEach(i => c[i] = (c[i] || 0) + 1)); for (const g of GE) if (g.k === 'armor' && c[g.id] !== 1) bad.push('armor piece in ' + (c[g.id] || 0) + ' sets: ' + g.id); }
// copy-docs-04 / detail-pages-checks-09: no printf token in a gear tooltip line
for (const g of ALL) for (const t of g.tip || []) if (/%\d*\$?[sd]\b|%%/.test(t)) bad.push('gear tooltip with a raw format token: ' + nm(g) + ': ' + t);
// copy-docs-12: no attribute label shows a raw namespace (Goety's keys keep theirs since the audit; gAttr strips it)
for (const g of [...GE, ...GS]) for (const k in g.at || {}) if (/\./.test(gAttr(k))) bad.push('attribute label with a dot: ' + gAttr(k) + ' on ' + (g.id || g.k));
// equip-groups: the finer groups of Equipment (gear.js GSUB, gSubOf) and the curios' own view (gOwn, gCurioGain, pool "o").
// A tiered weapon is in at least one group of its playstyle and only in groups the playstyle has; Melee and Ranged split their
// weapons in exactly one group each, Mage and Summon may put one in several (a Fire and Eldritch staff). Known weapons sit where
// their words and attributes say (a Railgun is a gun, a Blowgun is not; Pyrium Staff is Fire, a Soul Whip is a Summonity whip and
// a Spectre Whip a Goety one). A group's page shows only its own weapons, each under the tier the whole playstyle gives it, and
// the button counts agree (a partition's add up). The Curios tab's own view is the curios that raise the playstyle's output by
// GOWN or more, ranked by how much, and the other view holds none of them
{ const a = acts[acts.length - 1], R = ['ME', 'RA', 'MA', 'SU'], go = async h => { location.hash = h; await new Promise(r => setTimeout(r, 80)); render(); },
    rows = () => [...document.querySelectorAll('#main .gtl-list .grow')], tiles = () => rows().flatMap(r => [...r.querySelectorAll('a.gtl')].map(t => [r, t]));
  // a playstyle's weapons: the tiered ones and those not ranked yet (their own row under the tiers), grouped the same way
  const listed = r => [...gTiers(a, r, 'w').flatMap(x => x[1]), ...gUnranked(a, r, 'w')];
  for (const r of R) { const ws = listed(r), keys = GSUB[r].map(x => x[0]);
    for (const g of ws) { const k = gSubOf(g, r); if (!k.length || k.some(x => !keys.includes(x))) bad.push(`equip-groups: ${g.n} (${r}) is in ${k.length ? 'a group the playstyle does not have' : 'no group'}`); }
    if ((r === 'ME' || r === 'RA') && ws.some(g => gSubOf(g, r).length !== 1)) bad.push(`equip-groups: a ${r} weapon is in several groups`); }
  const at = (n, r) => GE.filter(g => g.n === n && g.k !== 'armor' && r in g.sc).map(g => gSubOf(g, r)),
    want = [['Railgun', 'RA', 'gun'], ['Blowgun', 'RA', 'thrown'], ['Gungnir', 'RA', 'thrown'], ['Crossbow', 'RA', 'xbow'], ['Bow', 'RA', 'bow'],
      ['Bloody Scythe', 'ME', 'scythe'], ['Claymore', 'ME', 'great'], ['Frying Pan', 'ME', 'hammer'], ['Iron Pike', 'ME', 'polearm'], ['Dagger', 'ME', 'dagger'],
      ['Ice Staff', 'ME', 'staff'], ['Gut Whip', 'ME', 'other'], ['Elvenite Axe', 'ME', 'axe'],
      ['Pyrium Staff', 'MA', 'fire'], ['Ice Staff', 'MA', 'ice'], ['Abyss Staff', 'MA', 'goety'], ['Novice Spell Book', 'MA', 'ars'], ["Artificer's Cane", 'MA', 'any'],
      ['Flames Of Eldritch (Lv 3)', 'MA', 'fire'], ['Flames Of Eldritch (Lv 3)', 'MA', 'eldritch'],
      ['Soul Whip', 'SU', 'summonity'], ['Soul Whip', 'SU', 'whip'], ['Spectre Whip', 'SU', 'goety'], ['Spectre Whip', 'SU', 'whip'], ['Imp Staff', 'SU', 'staff']];
  for (const [n, r, k] of want) { const x = at(n, r); if (!x.length || x.some(v => !v.includes(k))) bad.push(`equip-groups: ${n} (${r}) should be in "${k}": ${JSON.stringify(x)}`); }
  for (const r of R) { await go(`#gear/${a}/${r}/w`); const all = tiles().length, counts = [...document.querySelectorAll('#main .gseg.subs a .n')].map(x => +x.textContent), total = counts[0], per = counts.slice(1), keys = GSUB[r].map(x => x[0]).filter(k => listed(r).some(g => gSubOf(g, r).includes(k)));
    if (!total || per.length !== keys.length || per.some(n => !n || n > total) || ((r === 'ME' || r === 'RA') && per.reduce((x, y) => x + y, 0) !== total)) bad.push(`equip-groups: ${r} counts ${total} / ${per.join(', ')} for groups ${keys.join(', ')}`);
    for (const k of keys) { await go(`#gear/${a}/${r}/w/${k}`); const ts = tiles();
      if (!ts.length) bad.push(`equip-groups: ${r}/${k} shows nothing`);
      for (const [row, t] of ts) { const g = GE[+t.getAttribute('href').slice(2)];
        if (!gSubOf(g, r).includes(k) || (gTierOf(g, a, r, 'w') || (gUnr(g, r) ? '?' : '')) !== row.querySelector('.glet').textContent.trim()) bad.push(`equip-groups: ${g.n} on ${r}/${k} is not in the group, or stands under another tier than the playstyle gives it`); } } }
  for (const r of R) { const own = gTiers(a, r, 'o').flatMap(x => x[1]), g = own.map(d => gCurioGain(d, r, a)), any = gTiers(a, r, 'c').flatMap(x => x[1]).filter(d => !gOwn(d, r, a));
    if (!own.length || !any.length || own.some(d => !gOwn(d, r, a)) || g.some((v, i) => i && v > g[i - 1]) || any.some(d => own.includes(d)))
      bad.push(`equip-groups: ${r} curios: ${own.length} own, ${any.length} others; an own curio below ${GOWN}, out of order, or in both views`);
    await go(`#gear/${a}/${r}/c`); const shown = tiles().map(([, t]) => D[+t.dataset.t]);
    if (!shown.length || shown.some((d, i) => d !== own[i])) bad.push(`equip-groups: the own view of ${r} does not show the ranked own curios in order`);
    await go(`#gear/${a}/${r}/c/any`); if (tiles().some(([, t]) => gOwn(D[+t.dataset.t], r, a))) bad.push(`equip-groups: the "any playstyle" view of ${r} shows a curio of the playstyle's own`); }
  // the Equipment page: the forge is a strip and the controls three tiers, so the first tier of the list begins on the first screen (it began 700 px down of 900)
  await go(`#gear/${a}/ME/w`); { const row = document.querySelector('.gear .grow'), top = row && row.getBoundingClientRect().top;
    if (!row || top > innerHeight * .66) bad.push(`equip-layout: the first tier of the list begins ${Math.round(top)} px down a ${innerHeight} px screen`);
    const roles = [...document.querySelectorAll('.gear .gseg.roles a')]; if (roles.length !== 4 || roles.some(x => getComputedStyle(x, '::before').backgroundColor === 'rgba(0, 0, 0, 0)')) bad.push('equip-layout: a playstyle button has no role colour');
    const sub = document.querySelector('.gear .gseg.subs a'); if (sub && getComputedStyle(sub).borderImageSource !== 'none') bad.push('equip-layout: the group chips wear the big button texture, not the flat chip'); }
  await go('#gear'); }
// tier-act (2026-11-13): the Act an item unlocks at only decides which lists it is in, never its place in them. A weapon's score is
// a number read or measured in game (Melee: its DPS; Mage: what its bonuses multiply your spells by) and a set's is its own armor
// and bonuses; nothing is scored by its Act or by how hard it is to get (the old power curve put every later-Act bow and staff
// above every earlier one). Ranged and Summon weapons, a weapon whose damage is computed in code and a set never measured are not
// ranked: they stand in the "?" row under the tiers, and nothing usable at an Act falls out of both the tiers and that row
{ const o = new Set(), last = acts[acts.length - 1];
  for (const g of GE) { if (g.k === 'armor') continue;
    if (g.sc.ME != null && g.sc.ME !== gR3(gMelee(g))) o.add('tier-act: Melee score is not its DPS: ' + g.id);
    if (g.sc.MA != null && !(g.sc.MA > 1.001 && g.sc.MA === gR3(gOff(g, 'MA', g.a)))) o.add('tier-act: Mage score is not its spell multiplier: ' + g.id);
    if (g.sc.RA != null || g.sc.SU != null) o.add('tier-act: Ranged or Summon weapon ranked with no measurement: ' + g.id); }
  for (const s of GS) if (!s.f && Object.values(s.sc).some(v => v != null)) o.add('tier-act: set ranked with no numbers: ' + s.k);
  for (const a of acts) for (const r of Object.keys(GROLE)) for (const w of ['w', 'a']) {
    const inList = new Set([...gPool(a, r, w).map(x => x[0]), ...gUnranked(a, r, w)]);
    for (const g of w === 'a' ? GS : GE.filter(x => x.k !== 'armor')) if (r in g.sc && oiA(g.a) <= oiA(a) && !gHidden(g) && !inList.has(g)) o.add(`tier-act: ${g.n} usable at Act ${a} is in neither the ${w}/${r} tiers nor its unranked row`); }
  for (const [r, n] of [['RA', gUnranked(last, 'RA', 'w').length], ['SU', gUnranked(last, 'SU', 'w').length]]) {
    location.hash = `#gear/${last}/${r}/w`; render(); const row = document.querySelector('#main .grow.gunr');
    if (!n || !row || row.querySelectorAll("a.gtl").length !== (GALL ? n : Math.min(n, 48)) || !row.querySelector('.note')?.textContent.trim()) o.add(`tier-act: the ${r} list at Act ${last} lacks its unranked row (${n} weapons)`); }
  bad.push(...o); }
