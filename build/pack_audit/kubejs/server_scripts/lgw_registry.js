// Linggango wiki: dump every status effect and every spell the running game has registered (the game export the wiki's lists are checked against).
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
