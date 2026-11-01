// Item icons (audit own-3, own-4). Runs in the page (check.js: `bad` in scope).
// Items the game draws with Java code once showed their model's particle texture (oak planks for a chest and a banner,
// obsidian for the Ender Chest, white wool for Goety's plushies) or nothing (Pyrium Staff); weapon_icons/plan.py now draws
// them from their renderers (JAVA there). An icon equal to one of those old pictures (FNV-1a of the base64) is the bug back.
{ const h = s => { let x = 0x811c9dc5; for (let i = 0; i < s.length; i++) x = Math.imul(x ^ s.charCodeAt(i), 0x01000193) >>> 0; return x.toString(16).padStart(8, '0'); };
  const OLD = {'minecraft:chest': '6c7fad72', 'minecraft:ender_chest': 'c4536614', 'minecraft:red_banner': '6c7fad72', 'minecraft:shield': '76ff45b4',
    'ars_nouveau:archwood_chest': '3b315303', 'goety:plushie': 'aded7d52', 'goety:plushie_1': 'aded7d52'};
  for (const [id, o] of Object.entries(OLD)) if (!IC[id]) bad.push('no icon ' + id); else if (h(IC[id]) === o) bad.push('particle texture as the icon of ' + id); }
// every gear item has an icon, except these (each still without a faithful picture; take one out when it gets an icon)
{ const NOICON = {
    'ars_nouveau:spell_bow': 'its geo draws only the gold trim (weapon_icons/README.md)',
    'goetyawaken:potato_staff': 'model drawn in Java code, not read yet',
    'netherexp:pump_charge_shotgun': "jar not in the pack's download",
    'netherexp:shotgun_fist': "jar not in the pack's download"};
  for (const g of GE) if (!IC[g.id] && !NOICON[g.id]) bad.push('gear without an icon ' + g.id);
  for (const id in NOICON) if (IC[id]) bad.push(id + ' has an icon now: take it out of NOICON in checks/icons.js'); }
