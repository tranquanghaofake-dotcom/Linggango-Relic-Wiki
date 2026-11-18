// Effects: every status effect the jars hold (pack_audit/effects.py -> patches/effects.json) is on #mechanics/effects (2026-11-14).
// Runs in the page (check.js: `bad` and `patchJSON` in scope). The list, the icons the licences allow, the gear that gives each one,
// the effects the page promised before (the hand-written entries of app.js EFFECTS) and the filters.
{ const wait = ms => new Promise(r => setTimeout(r, ms)), P = await patchJSON('effects.json'), rows = P.effects, X = window.EFX || [];
  const VANILLA = ['absorption', 'bad_omen', 'blindness', 'conduit_power', 'darkness', 'dolphins_grace', 'fire_resistance', 'glowing', 'haste', 'health_boost', 'hero_of_the_village', 'hunger', 'instant_damage', 'instant_health', 'invisibility', 'jump_boost', 'levitation', 'luck', 'mining_fatigue', 'nausea', 'night_vision', 'poison', 'regeneration', 'resistance', 'saturation', 'slow_falling', 'slowness', 'speed', 'strength', 'unluck', 'water_breathing', 'weakness', 'wither'];   // Minecraft 1.20.1's 33
  if (!X.length) bad.push('effects: window.EFX is empty (wiki_pics.js)');
  else {
    if (X.length !== rows.length) bad.push(`effects: the page has ${X.length} effects, patches/effects.json ${rows.length}`);
    // the list is the game's own (patches/game_registry.json, KubeJS lgw_registry.js in the running server pack): no effect missing, none the game lacks
    { const g = new Set((await patchJSON('game_registry.json')).effects.map(e => e.id)), have = new Set(X.map(e => e.i));
      for (const id of g) if (!have.has(id)) bad.push('effects: the game registers ' + id + ', the page lacks it');
      for (const id of have) if (!g.has(id)) bad.push('effects: ' + id + ' is on the page but the game does not register it'); }
    const ids = new Set(X.map(e => e.i));
    if (ids.size !== X.length) bad.push('effects: a registry id twice in the list');
    for (const v of VANILLA) if (!ids.has('minecraft:' + v)) bad.push('effects: no minecraft:' + v);
    for (const e of X) { if (!/^[a-z0-9_.-]+:[a-z0-9_./-]+$/.test(e.i)) bad.push('effects: odd id ' + e.i); if (!e.m) bad.push('effects: no mod on ' + e.i); }
    // the hand-written entries the page had before the full list (food buffs, Linggango's own, vanilla) are all still there, under minecraft: or linggango_tweaks:
    for (const h of EFFECTS) if (!X.some(e => e.n.toLowerCase() === h.n.toLowerCase() && /^(minecraft|linggango_tweaks):/.test(e.i))) bad.push('effects: the hand-written "' + h.n + '" has no row');
    // every effect a weapon or armour piece applies (gear_fx.json) has a row, so a "Given by" link never leads to an effect the list lacks
    for (const k of Object.keys(window.EFXG || {})) if (!ids.has(k)) bad.push('effects: gear applies ' + k + ', which is not in the list');
    // licences (build/README.md): an icon only where the jar's licence allows; nothing from an All Rights Reserved jar
    const ic = window.EFXI || {}, lic = Object.fromEntries(rows.map(r => [r.id, r.lic]));
    for (const k of Object.keys(ic)) { if (!ids.has(k)) bad.push('effects: icon for unknown ' + k); else if (/all\s*rights|\bARR\b/i.test(lic[k] || '') && !k.startsWith('minecraft:')) bad.push('effects: an icon from an All Rights Reserved jar: ' + k); }
    for (const e of X) if (e.p && !ic[e.i]) bad.push('effects: ' + e.i + ' says it has an icon, none is shipped');
    for (const id of ['irons_spellbooks', 'terramity', 'relics']) if (Object.keys(ic).some(k => k.startsWith(id + ':'))) bad.push('effects: icons from ' + id + ' (build/README.md Licence rules)');
    // the page
    location.hash = '#mechanics/effects'; await wait(80); render(); await wait(300);
    const n = () => document.querySelectorAll('#etb tr').length, q = document.getElementById('eq'), g = document.getElementById('eg'), m = document.getElementById('em'), k = document.getElementById('ek'), inp = (e, v) => { e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); };
    if (n() !== 60) bad.push('effects: the first draw has ' + n() + ' rows, want 60');
    // the page opens on the effects something in the pack gives (2026-11-18): a curio that only blocks an effect ("Immune to Darkness") is not a way to get it
    { const ng = +(g?.options[0].textContent.match(/\((\d+)\)/) || [])[1];
      if (g?.value !== 'g' || !(ng > 100 && ng < X.length)) bad.push('effects: the list does not open on "Effects you can get" (' + g?.value + ', ' + ng + ')');
      if (document.getElementById('en')?.textContent !== ng + ' of ' + ng) bad.push('effects: the count line says ' + document.getElementById('en')?.textContent + ', want ' + ng + ' of ' + ng);
      for (let i = 0; i < 10 && document.querySelector('#emore button'); i++) document.querySelector('#emore button').click();
      for (const tr of document.querySelectorAll('#etb tr')) { tr.querySelectorAll('details').forEach(d => d.open = true); const c = tr.querySelectorAll('td.nchs .nch'); if (!c.length || [...c].every(x => x.classList.contains('nblk'))) bad.push('effects: ' + tr.id + ' is in "Effects you can get" with nothing that gives it'); }
      for (const x of document.querySelectorAll('#etb .nblk a[data-t]')) { const d = D[+x.dataset.t]; if (!d || !/immun|prevent|negat|cure|remov|cleans|nullif|protect|resist|ward|unaffected/i.test(d.fx || '')) bad.push('effects: ' + x.textContent + ' is marked "blocks it" but its text blocks nothing'); }
      // a curio that says "Immune to Darkness" never stands among the curios that give Darkness
      const dk = document.getElementById('eff-minecraft-darkness');
      if (dk) for (const c of dk.querySelectorAll('.nch:not(.nblk) a[data-t]')) { const d = D[+c.dataset.t]; if (d && /immune to[^.;]*\bDarkness\b/i.test(d.fx || '')) bad.push('effects: ' + d.n + ' is immune to Darkness and listed as giving it'); }
      inp(g, ''); }
    if (document.getElementById('en')?.textContent !== X.length + ' of ' + X.length) bad.push('effects: All effects: the count line says ' + document.getElementById('en')?.textContent);
    inp(q, 'bleeding'); if (n() < 2 || n() > 60 || ![...document.querySelectorAll('#etb tr')].every(t => /bleeding/i.test(t.textContent))) bad.push('effects: filter "bleeding" gives ' + n() + ' rows');
    inp(q, 'zzzzqq'); if (n() !== 0) bad.push('effects: a nonsense filter still shows ' + n() + ' rows'); inp(q, '');
    inp(m, 'Minecraft'); if (document.getElementById('en')?.textContent !== VANILLA.length + ' of ' + X.length) bad.push('effects: mod Minecraft says ' + document.getElementById('en')?.textContent); inp(m, '');
    inp(k, 'h'); { const hit = X.filter(e => e.k === 'h').length; if (document.getElementById('en')?.textContent !== hit + ' of ' + X.length) bad.push('effects: kind Harmful says ' + document.getElementById('en')?.textContent + ', data has ' + hit); } inp(k, '');
    for (let i = 0; i < 40 && document.querySelector('#emore button'); i++) document.querySelector('#emore button').click();
    if (n() !== X.length) bad.push('effects: Show more ends at ' + n() + ' rows of ' + X.length);
    if (/undefined|NaN|\[object/.test(document.getElementById('main').innerText)) bad.push('effects: undefined, NaN or [object] on the page');
    // attribute names read as names (2026-11-18: all 67 were the id run together, "minecraftgenericluck"), and no modifier shows +0 (Strength, Weakness: the value is in the effect's code)
    for (const [a, v] of Object.entries(window.EFXA || {})) if (!v || v === a || v.toLowerCase() === a.replace(/[^a-z0-9]/gi, '').toLowerCase() || !/[A-Z]/.test(v[0])) bad.push('effects: attribute ' + a + ' is named "' + v + '"');
    for (const tr of document.querySelectorAll('#etb tr')) { const t = tr.children[2]?.textContent || ''; if (/(^|\s)[+−]0(%|\s|$)/.test(t)) bad.push('effects: ' + tr.id + ' shows a modifier of 0: ' + t.slice(0, 80));
      if (/^eff-minecraft-/.test(tr.id) && /No description/.test(t)) bad.push('effects: vanilla ' + tr.id + ' has no description'); }
    for (const a of document.querySelectorAll('#etb a[data-t]')) { const t = a.dataset.t; if (/^g\d+$/.test(t) ? !GE[+t.slice(1)] : /^\d+$/.test(t) ? !D[+t] : false) bad.push('effects: link data-t ' + t + ' resolves to nothing'); }
  }
  // descriptions the wiki wrote from an effect's code (patches/effect_desc.json): each one shows on its row with the "read from the mod's code" label
  { const ED = await patchJSON('effect_desc.json'); location.hash = '#mechanics/effects'; await wait(80); render(); await wait(300);
    const g = document.getElementById('eg'); g.value = ''; g.dispatchEvent(new Event('input', { bubbles: true }));
    for (let i = 0; i < 40 && document.querySelector('#emore button'); i++) document.querySelector('#emore button').click();
    for (const [id, v] of Object.entries(ED)) { const tr = document.getElementById('eff-' + id.replace(/[:_]/g, '-')), t = tr?.children[2];
      if (!v.d || !v.src) bad.push('effects: effect_desc.json ' + id + ' has no text or no source');
      else if (!t || !t.textContent.includes(v.d) || !t.querySelector('.edc')) bad.push('effects: ' + id + ' does not show its code-read description with the label'); } }
  // measured in game (patches/effect_measure.json, lgw_measure_fx): every effect has a reading or is marked as crashing the server; the vanilla
  // effects whose numbers are known read them (the calibration the run is trusted on); no wave of one-hit kills (2026-11-18: one effect left the
  // tester killing the 1,000-health pig in one hit for the 549 effects after it, until each effect got a fresh tester)
  { const MZ = await patchJSON('effect_measure.json'), SR = await patchJSON('effect_sources.json'), L = (id, i) => ((MZ[id] || {}).l || [])[i] || {};
    for (const e of X) if (!MZ[e.i]) bad.push('effects: ' + e.i + ' has no in-game measurement');
    const near = (a, b, t) => typeof a === 'number' && Math.abs(a - b) <= (t || 0.011);
    const at = (id, i, a) => ((L(id, i).at || {})[a] || [])[1];
    if (!near(at('minecraft:speed', 0, 'minecraft:generic.movement_speed'), 0.12, 0.002) || !near(at('minecraft:speed', 1, 'minecraft:generic.movement_speed'), 0.14, 0.002)) bad.push('effects: Speed does not read +20%/+40% movement');
    if (!near(L('minecraft:poison', 0).hp, -0.8) || !near(L('minecraft:poison', 1).hp, -1.6)) bad.push('effects: Poison does not read -0.8/-1.6 health a second');
    if (!near(L('minecraft:regeneration', 0).hp, 0.4) || !near(L('minecraft:regeneration', 1).hp, 0.8)) bad.push('effects: Regeneration does not read +0.4/+0.8 health a second');
    if (!near(L('minecraft:resistance', 0).tk, 0.8) || !near(L('minecraft:resistance', 1).tk, 0.76)) bad.push('effects: Resistance does not read Linggango\'s 20%/24%');
    if (String(L('minecraft:strength', 0).hit) !== '1,4' || String(L('minecraft:strength', 1).hit) !== '1,7') bad.push('effects: Strength does not read +3/+6 on a bare-hand hit');
    if (!near(L('minecraft:absorption', 0).ab, 4) || !near(L('minecraft:absorption', 1).ab, 8)) bad.push('effects: Absorption does not read 4/8');
    if (!(L('minecraft:levitation', 0).dy > 3)) bad.push('effects: Levitation does not lift the pig');
    if (!near(L('terramity:vulnerable', 0).tk, 1.33)) bad.push('effects: Vulnerable does not read +33% damage taken');
    if (String(L('terramity:amped', 0).hit) !== '1,1.5') bad.push('effects: Amped does not read x1.5 on a hit');
    const kills = Object.keys(MZ).filter(k => (MZ[k].l || []).some(l => l.hit && l.hit[1] >= 100));
    if (kills.length > 5) bad.push('effects: ' + kills.length + ' effects read a one-hit kill (a carried-over tester?): ' + kills.slice(0, 5).join(', '));
    if (!(SR['minecraft:speed'] || []).some(x => x[0] === 'potion' && /Swiftness/.test(x[1]))) bad.push('effects: Speed lacks the Potion of Swiftness as a source');
    location.hash = '#mechanics/effects/Speed'; await wait(80); render(); await wait(300);
    const sp = document.getElementById('eff-minecraft-speed');
    if (!sp || !sp.querySelector('.emz') || !/20%|0\.12/.test(sp.querySelector('.emz').textContent) && !/Speed/.test(sp.textContent)) bad.push('effects: the Speed row has no in-game measurement line');
    if (!sp || !/Swiftness/.test(sp.textContent)) bad.push('effects: the Speed row does not list the Potion of Swiftness'); }
  // an effect name on an item page opens the list on that effect, marked and first
  location.hash = '#mechanics/effects/Speed'; await wait(80); render(); await wait(300);
  { const f = document.querySelector('#etb tr'); if (!f || f.id !== 'eff-minecraft-speed' || !f.classList.contains('hl')) bad.push('effects: #mechanics/effects/Speed does not open on Speed, marked (' + (f && f.id) + ')'); }
  location.hash = '#mechanics'; await wait(80); render(); }
