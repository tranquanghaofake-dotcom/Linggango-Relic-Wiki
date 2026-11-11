// Audit of 2026-10-31: each block is a data or scoring bug that was live on the site. Runs in the page (check.js:
// `bad` and `acts` in scope).
// Mage output counted Goety's spell_potency (+1 read as +100%) and casting_speed as Iron's stats: Goety keys keep their namespace
if (GOFF.MA({spell_potency: [1, 0], casting_speed: [.03, 0]}, 5) !== 1) bad.push('GOFF.MA reads Goety spell_potency/casting_speed');
for (const g of [...GE, ...GS]) { const at = g.at || {};
  if ((at.spell_power || [0])[0] !== 0) bad.push('additive spell_power (another mod folded into Iron\'s) ' + (g.id || g.k));
  for (const k of ['spell_potency', 'casting_speed', 'spell_power_multiplier', 'cast_duration', 'spell_cooldown', 'soul_discount']) if (k in at) bad.push('unprefixed Goety key ' + k + ' on ' + (g.id || g.k)); }
{ const d = GS.find(x => x.k === 'goety:dark'); if (d && !(gOff(d, 'MA', 5) < 1.5)) bad.push('Dark set Mage output ' + gOff(d, 'MA', 5)); }
// Summoner's Bangle: a flat +2 Summon Power was scored as +100% (Mythic, #1 Summon curio); Summon Duration is not damage
{ const m = CM['ars_elemental:summon_bangle'], B = BYID['ars_elemental:summon_bangle'];
  if (!m || !m.d || m.d['ars_nouveau:ars_elemental.perk.summon_power'] !== 2) bad.push('summon_bangle summon_power ' + JSON.stringify(m && m.d));
  if (B && !(gCurioScore(B, 'SU', 7) < 1.2 && B.r < 4)) bad.push('summon_bangle scored as a multiplier');
  if (GOFF.SU({summon_duration: [0, .4]}, 7) !== 1) bad.push('summon_duration counted as summon damage'); }
// Resistance follows Linggango Fixes' curve (0.2 + 0.04444 a level), not 20% a level
for (let L = 1; L <= 5; L++) { const e = 0.2 + (L - 1) * 0.04444, a = gCurioAt({fx: [['minecraft:resistance', L, 100]]}).resistance[1];
  if (Math.abs(a - e) > 1e-9) bad.push('resistance L' + L + ' ' + a); }
// curio 'Measured in game' rows: flat attributes printed as flat, nothing beyond ±1000%
{ const kp = BYID['brutality:knights_pendant']; if (kp && !gCurioMs(kp).includes('+4 Lethality')) bad.push("Knight's Pendant lethality not flat");
  for (const id in CM) for (const li of gCurioMs(BYID[id] || {id, fx: []}).match(/[+-][\d.]+%/g) || []) if (Math.abs(parseFloat(li)) > 1000) bad.push('measured row ' + id + ' ' + li); }
// every lock names its boss (GATEN had no 6.3, 9 or 12); nothing sits below its own gate
for (const g of [...GE, ...GS]) { if (g.ga && !GATEN[g.ga]) bad.push('gate without a name ' + (g.id || g.k) + ' ' + g.ga); if (oiA(g.a) < oiA(g.ga || 0)) bad.push('below its gate ' + (g.id || g.k)); }
// armor families are one set each (Living, Robe, Geomancer... were four one-piece sets); no two sets share a name in a mod
if (GS.filter(x => x.k.startsWith('mowziesmobs:geomancer')).length !== 1) bad.push('Geomancer split');
{ const seen = {}; for (const x of GS) { const k = x.n + '|' + x.k.split(':')[0]; if (seen[k]) bad.push('two sets named ' + k); seen[k] = 1; } }
// the pack disables Mystical Agriculture armor and never loads Tide Piercer's recipe: not in any tier list
{ const tp = GBY['somakespells:tide_piercer']; if (tp && gTierOf(tp, 5, 'MA', 'w') !== null) bad.push('Tide Piercer tiered');
  const ma = GS.find(x => x.k === 'mysticalagriculture:awakened_supremium'); if (ma && gTierOf(ma, 8, 'RA', 'a') !== null) bad.push('MA armor tiered'); }
// bosses: Keepers, Wither and Ender Dragon are exempt from Hardmode (forge:armageddon_bosses); the Dragon is 600 HP / 30 armor
if (typeof BST !== 'undefined') { if (!(BST.ender_dragon && BST.ender_dragon.effective.hp === 600 && BST.ender_dragon.effective.armor === 30)) bad.push('Ender Dragon stats');
  for (const k in BST) for (const ph of BST[k].phases || []) if (ph.hardmode) bad.push('Hardmode applied to ' + k); }
// the pack's soul_bosses pin side-boss health and armor
if (typeof SSTAT !== 'undefined') { const ig = (SSTAT.Ignis || [])[0]; if (!(ig && ig.hp === 3200 && ig.pinned)) bad.push('Ignis not pinned to the pack\'s 3200 HP'); }
// the Keepers' names are the game's (The Discord, Fourth Calamity), not wiki-made
if (document.documentElement.outerHTML.includes('Keeper of the Calamities')) bad.push('wiki-made Keeper name');
