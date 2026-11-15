// Linggango wiki: dump every status effect and every spell (Iron's, Goety focuses, Ars glyphs, Brutality) the running game has registered (the game export the wiki's lists are checked against).
// Written for KubeJS's Rhino engine: var only, no destructuring. Writes kubejs/lgw_registry.json.
// Run in game (op): /kubejs custom_command lgw_registry. On a dedicated server started only for this, create kubejs/lgw_registry_auto.json
// ({"stop": true}) and the dump runs once the server has loaded, then the server stops.
// Minecraft methods are called by their Mojang name with the SRG name as fallback (1.20.1, read from the Forge srg server jar with javap):
// MobEffect getDescriptionId m_19481_, getCategory m_19483_, getColor m_19484_, getAttributeModifiers m_19485_, isInstantenous m_8093_;
// AttributeModifier getOperation m_22217_, getAmount m_22218_.
var LGWR = {}
LGWR.call = function (o, names) {
  for (var i = 0; i < names.length; i++) { try { if (typeof o[names[i]] === 'function') return o[names[i]]() } catch (e) {} }
  return null
}
LGWR.dump = function () {
  var ForgeRegistries = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
  var out = { effects: [], spells: [], errors: [] }
  var it = ForgeRegistries.MOB_EFFECTS.getKeys().iterator()
  while (it.hasNext()) {
    var rl = it.next(), row = { id: '' + rl }
    try {
      var e = ForgeRegistries.MOB_EFFECTS.getValue(rl)
      row.cls = '' + e.getClass().getName()
      row.desc = '' + LGWR.call(e, ['getDescriptionId', 'm_19481_'])
      var cat = LGWR.call(e, ['getCategory', 'm_19483_']); row.cat = cat == null ? null : ('' + cat.name()).toLowerCase()
      row.color = LGWR.call(e, ['getColor', 'm_19484_'])
      row.instant = LGWR.call(e, ['isInstantenous', 'm_8093_'])
      var mods = LGWR.call(e, ['getAttributeModifiers', 'm_19485_']), list = []
      if (mods != null) {
        var mi = mods.entrySet().iterator()
        while (mi.hasNext()) {
          var en = mi.next(), m = en.getValue(), op = LGWR.call(m, ['getOperation', 'm_22217_'])
          list.push({ attr: '' + ForgeRegistries.ATTRIBUTES.getKey(en.getKey()), amount: LGWR.call(m, ['getAmount', 'm_22218_']), op: op == null ? null : '' + op.name() })
        }
      }
      row.mods = list
    } catch (err) { out.errors.push('effect ' + rl + ': ' + err) }
    out.effects.push(row)
  }
  // spells: Iron's Spells' own registry (addons register into it)
  try {
    var SpellRegistry = Java.loadClass('io.redspace.ironsspellbooks.api.registry.SpellRegistry')
    var spells = SpellRegistry.REGISTRY.get().getValues().iterator()
    while (spells.hasNext()) {
      var s = spells.next(), r = {}
      try { r.id = '' + s.getSpellId() } catch (err) { r.id = '?' }
      var tries = { enabled: function () { return s.isEnabled() }, max: function () { return s.getMaxLevel() }, min: function () { return s.getMinLevel() },
        rarity: function () { return '' + s.getMinRarity() }, school: function () { return '' + s.getSchoolType().getId() }, cast: function () { return '' + s.getCastType() },
        cooldown: function () { return s.getSpellCooldown() } }
      for (var k in tries) { try { r[k] = tries[k]() } catch (err) { r[k] = null } }
      try { var mana = [], ct = []; for (var lv = 1; lv <= (r.max || 1); lv++) { mana.push(s.getManaCost(lv)); ct.push(s.getCastTime(lv)) } r.mana = mana; r.castTime = ct } catch (err) { out.errors.push('spell ' + r.id + ' mana/cast: ' + err) }
      out.spells.push(r)
    }
  } catch (err) { out.errors.push('spells: ' + err) }
  // the other spell systems (2026-11-15): Goety focuses (items whose class has getSpell: the focus and its spell, the soul cost, cast time and cooldown
  // after the pack's config), Ars Nouveau glyphs (GlyphRegistry: type, tier, mana cost, enabled), Brutality spells (its SpellRegistry)
  out.goety = []
  try {
    var ForgeRegistries2 = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
    var ii = ForgeRegistries2.ITEMS.getKeys().iterator()
    while (ii.hasNext()) {
      var key = ii.next(), item = ForgeRegistries2.ITEMS.getValue(key), sp = null
      try { if (typeof item.getSpell === 'function') sp = item.getSpell() } catch (err) { sp = null }
      if (sp == null) continue
      var g = { id: '' + key, cls: '' + sp.getClass().getName() }
      var gt = { cost: function () { return sp.defaultSoulCost() }, cast: function () { return sp.defaultCastDuration() }, cooldown: function () { return sp.defaultSpellCooldown() },
        type: function () { return '' + sp.getSpellType() }, kind: function () { return '' + sp.getClass().getSuperclass().getSimpleName() } }
      for (var gk in gt) { try { g[gk] = gt[gk]() } catch (err) { g[gk] = null } }
      out.goety.push(g)
    }
  } catch (err) { out.errors.push('goety: ' + err) }
  out.ars = []
  try {
    var GlyphRegistry = Java.loadClass('com.hollingsworth.arsnouveau.api.registry.GlyphRegistry')
    var gi = GlyphRegistry.getSpellpartMap().entrySet().iterator()
    while (gi.hasNext()) {
      var en2 = gi.next(), part = en2.getValue(), a = { id: '' + en2.getKey() }
      var at = { name: function () { return '' + part.getName() }, cost: function () { return part.getCastingCost() }, tier: function () { return '' + part.getConfigTier() },
        type: function () { return part.getTypeIndex() }, cls: function () { return '' + part.getClass().getSuperclass().getSimpleName() }, enabled: function () { return part.isEnabled() },
        glyph: function () { return '' + ForgeRegistries2.ITEMS.getKey(part.getGlyph()) }, desc: function () { return '' + part.getBookDescription() } }
      for (var ak in at) { try { a[ak] = at[ak]() } catch (err) { a[ak] = null } }
      out.ars.push(a)
    }
  } catch (err) { out.errors.push('ars: ' + err) }
  out.brutality = []
  try {
    var BSR = Java.loadClass('net.goo.brutality.magic.SpellRegistry')
    var bi = BSR.SPELLS.entrySet().iterator()
    while (bi.hasNext()) {
      var en3 = bi.next(), b = en3.getValue(), r3 = { id: '' + en3.getKey(), cls: '' + b.getClass().getName() }
      var bt = { name: function () { return '' + b.getSpellName() }, mana: function () { return b.getBaseManaCost() }, manaLv: function () { return b.getManaCostLevelScaling() },
        damage: function () { return b.getBaseDamage() }, damageLv: function () { return b.getDamageLevelScaling() }, cooldown: function () { return b.getBaseCooldown() },
        cooldownLv: function () { return b.getCooldownLevelScaling() }, cast: function () { return b.getBaseCastTime() }, castLv: function () { return b.getCastTimeLevelScaling() },
        school: function () { return '' + b.getSchool() }, cats: function () { return '' + b.getCategories() }, icon: function () { return '' + b.getIcon() } }
      for (var bk in bt) { try { r3[bk] = bt[bk]() } catch (err) { r3[bk] = null } }
      out.brutality.push(r3)
    }
  } catch (err) { out.errors.push('brutality: ' + err) }
  JsonIO.write('kubejs/lgw_registry.json', out)
  return out
}
ServerEvents.customCommand('lgw_registry', function (event) {
  var o = LGWR.dump()
  event.player.tell('lgw_registry: ' + o.effects.length + ' effects, ' + o.spells.length + ' spells, ' + o.errors.length + ' errors -> kubejs/lgw_registry.json')
})
ServerEvents.loaded(function (event) {
  var auto = null
  try { auto = JsonIO.read('kubejs/lgw_registry_auto.json') } catch (err) { auto = null }
  if (!auto) return
  var o = LGWR.dump()
  console.info('lgw_registry: ' + o.effects.length + ' effects, ' + o.spells.length + ' spells, ' + o.errors.length + ' errors')
  if (auto.stop || (auto.get && auto.get('stop'))) event.server.runCommandSilent('stop')
})
