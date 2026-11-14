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
    const n = () => document.querySelectorAll('#etb tr').length, q = document.getElementById('eq'), m = document.getElementById('em'), k = document.getElementById('ek'), inp = (e, v) => { e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); };
    if (n() !== 60) bad.push('effects: the first draw has ' + n() + ' rows, want 60');
    if (document.getElementById('en')?.textContent !== X.length + ' of ' + X.length) bad.push('effects: the count line says ' + document.getElementById('en')?.textContent);
    inp(q, 'bleeding'); if (n() < 2 || n() > 60 || ![...document.querySelectorAll('#etb tr')].every(t => /bleeding/i.test(t.textContent))) bad.push('effects: filter "bleeding" gives ' + n() + ' rows');
    inp(q, 'zzzzqq'); if (n() !== 0) bad.push('effects: a nonsense filter still shows ' + n() + ' rows'); inp(q, '');
    inp(m, 'Minecraft'); if (document.getElementById('en')?.textContent !== VANILLA.length + ' of ' + X.length) bad.push('effects: mod Minecraft says ' + document.getElementById('en')?.textContent); inp(m, '');
    inp(k, 'h'); { const hit = X.filter(e => e.k === 'h').length; if (document.getElementById('en')?.textContent !== hit + ' of ' + X.length) bad.push('effects: kind Harmful says ' + document.getElementById('en')?.textContent + ', data has ' + hit); } inp(k, '');
    for (let i = 0; i < 40 && document.querySelector('#emore button'); i++) document.querySelector('#emore button').click();
    if (n() !== X.length) bad.push('effects: Show more ends at ' + n() + ' rows of ' + X.length);
    if (/undefined|NaN|\[object/.test(document.getElementById('main').innerText)) bad.push('effects: undefined, NaN or [object] on the page');
    for (const a of document.querySelectorAll('#etb a[data-t]')) { const t = a.dataset.t; if (/^g\d+$/.test(t) ? !GE[+t.slice(1)] : /^\d+$/.test(t) ? !D[+t] : false) bad.push('effects: link data-t ' + t + ' resolves to nothing'); }
  }
  location.hash = '#mechanics'; await wait(80); render(); }
