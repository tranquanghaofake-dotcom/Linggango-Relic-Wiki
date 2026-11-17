// Linggango wiki: what spell power changes in each Iron's spell, read from the running game (2026-11-17, docs/plans/2026-11-17-spell-library.md).
// For every spell of Iron's SpellRegistry it asks the spell for its tooltip lines (AbstractSpell.getUniqueInfo(level, caster): "12.5 Damage",
// "3 Radius"...) as a FakePlayer with no gear would see them, at the lowest and the highest level, then again at the highest level with the spell's
// school power doubled, and with the general spell power doubled. A line that changes with the power is one that spell power raises; a line that only
// changes with the level is one the level raises. Writes kubejs/lgw_spellpower.json (build/pack_audit/spell_power.py turns it into patches/spell_power.json).
// Iron's builds its spell config (levels, power multiplier...) from the datapack reload and applies it on the next datapack sync (SpellConfigManager:
// apply -> handleServerConfigUpdate marks it dirty, onDatapackSync builds it); a server with no player never syncs, so the run calls onDatapackSync
// itself and checks that Fireball reads its configured 5 levels (the 2026-11-14 registry dump, without that, read every spell at level 1). Not /reload:
// in this pack a reload holds one server tick past the 60 s watchdog (an enchantment check of the weapon mod loops over items) and the server stops.
// Run in game (op): /kubejs custom_command lgw_spellpower. On a dedicated server started for this, create kubejs/lgw_spellpower_auto.json ({}) and the
// dump runs once the server has loaded. Written for KubeJS's Rhino: var and function only.
var LGWP = {}
// Mojang name first, then the SRG name (1.20.1): Component getContents m_214077_, getSiblings m_7360_, getString m_6111_; TranslatableContents getKey
// m_237508_, getArgs m_237523_; LiteralContents text m_237368_; LivingEntity getAttribute m_21051_; AttributeInstance getBaseValue m_22115_,
// setBaseValue m_22100_; ServerLevel / MinecraftServer overworld m_129783_
LGWP.SRG = { getContents: ['m_214077_'], getSiblings: ['m_7360_'], getString: ['m_6111_'], getKey: ['m_237508_'], getArgs: ['m_237523_'], text: ['m_237368_'],
  getAttribute: ['m_21051_'], getBaseValue: ['m_22115_'], setBaseValue: ['m_22100_'], overworld: ['m_129783_'], getPlayerList: ['m_6846_'] }
LGWP.fn = function (o, n) {
  try { if (typeof o[n] === 'function') return n } catch (e) {}
  var l = LGWP.SRG[n] || []
  for (var j = 0; j < l.length; j++) { try { if (typeof o[l[j]] === 'function') return l[j] } catch (e) {} }
  return n
}
LGWP.c0 = function (o, n) { return o[LGWP.fn(o, n)]() }
// a tooltip line as data: the translation key and its arguments (numbers come as strings the spell already rounded), with the text as the server reads it
LGWP.ser = function (c) {
  var out = { k: null, a: [], t: null, s: [] }
  try { out.t = '' + LGWP.c0(c, 'getString') } catch (e) {}
  try {
    var ct = LGWP.c0(c, 'getContents')
    try { out.k = '' + LGWP.c0(ct, 'getKey') } catch (e) { out.k = null }
    try { var args = LGWP.c0(ct, 'getArgs'); for (var i = 0; i < args.length; i++) { var x = args[i]; out.a.push(x != null && typeof x === 'object' && LGWP.isComp(x) ? LGWP.ser(x) : '' + x) } } catch (e) {}
    if (out.k == null) { try { out.lit = '' + LGWP.c0(ct, 'text') } catch (e) {} }
  } catch (e) {}
  try { var sib = LGWP.c0(c, 'getSiblings'); for (var j = 0; j < sib.size(); j++) out.s.push(LGWP.ser(sib.get(j))) } catch (e) {}
  return out
}
LGWP.isComp = function (x) { try { return typeof x[LGWP.fn(x, 'getContents')] === 'function' } catch (e) { return false } }
LGWP.lines = function (s, lv, P) {   // copied into an ArrayList: Rhino may not call size() on the immutable List.of the spells return
  var l = new (Java.loadClass('java.util.ArrayList'))(s.getUniqueInfo(lv, P)), out = []
  for (var i = 0; i < l.size(); i++) out.push(LGWP.ser(l.get(i)))
  return out
}
LGWP.dump = function (server) {
  var SpellRegistry = Java.loadClass('io.redspace.ironsspellbooks.api.registry.SpellRegistry')
  var SchoolRegistry = Java.loadClass('io.redspace.ironsspellbooks.api.registry.SchoolRegistry')
  var ForgeRegistries = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
  var FakePlayerFactory = Java.loadClass('net.minecraftforge.common.util.FakePlayerFactory')
  var GameProfile = Java.loadClass('com.mojang.authlib.GameProfile')
  var UUID = Java.loadClass('java.util.UUID')
  var level = LGWP.c0(server, 'overworld')
  var P = FakePlayerFactory.get(level, new GameProfile(UUID.fromString('3f6b1c2e-7d4a-4e8b-9c1d-5a2e8f7b6c4d'), '[lgw_power]'))
  var out = { schools: [], spells: [], errors: [], attrs: [] }
  // the attributes that can move a school's power: every registered attribute whose id says power, tried one at a time
  var A = [], ai = ForgeRegistries.ATTRIBUTES.getKeys().iterator()
  while (ai.hasNext()) { var key = ai.next(); if (('' + key).indexOf('power') >= 0) { var at = ForgeRegistries.ATTRIBUTES.getValue(key), inst = null
    try { inst = P[LGWP.fn(P, 'getAttribute')](at) } catch (e) { inst = null } if (inst != null) A.push({ id: '' + key, inst: inst }) } }
  out.attrs = A.map(function (a) { return a.id })
  var bump = function (a, f) { var b = a.inst[LGWP.fn(a.inst, 'getBaseValue')](); a.inst[LGWP.fn(a.inst, 'setBaseValue')](b * 2 > 0 ? b * 2 : 1); try { return f() } finally { a.inst[LGWP.fn(a.inst, 'setBaseValue')](b) } }
  var schoolAttr = {}, general = null
  var si = SchoolRegistry.REGISTRY.get().getValues().iterator()
  while (si.hasNext()) {
    var sc = si.next(), sid = '' + sc.getId(), base = sc.getPowerFor(P), moved = []
    for (var k = 0; k < A.length; k++) { var v = bump(A[k], function () { return sc.getPowerFor(P) }); if (Math.abs(v - base) > 1e-6) moved.push(A[k].id) }
    out.schools.push({ id: sid, base: base, moved: moved })
  }
  // the general attribute (Iron's spell_power) moves every school that reads it; a school's own attribute moves only that school
  if (A.some(function (a) { return a.id === 'irons_spellbooks:spell_power' })) general = 'irons_spellbooks:spell_power'
  out.schools.forEach(function (x) { var own = x.moved.filter(function (m) { return m !== general }); x.own = own.length === 1 ? own[0] : null; schoolAttr[x.id] = x.own })
  out.general = general
  var byId = {}; A.forEach(function (a) { byId[a.id] = a })
  var it = SpellRegistry.REGISTRY.get().getValues().iterator()
  while (it.hasNext()) {
    var s = it.next(), r = { id: '' + s.getSpellId() }
    if (r.id === 'irons_spellbooks:none') continue
    try {
      r.school = '' + s.getSchoolType().getId(); r.min = s.getMinLevel(); r.max = s.getMaxLevel(); r.enabled = s.isEnabled()
      r.lo = LGWP.lines(s, r.min, P); r.hi = LGWP.lines(s, r.max, P)
      r.sp = [s.getSpellPower(r.min, P), s.getSpellPower(r.max, P)]
      var own = schoolAttr[r.school]
      if (own && byId[own]) { r.schoolAttr = own; r.school2 = bump(byId[own], function () { return LGWP.lines(s, r.max, P) }); r.sp2 = bump(byId[own], function () { return s.getSpellPower(r.max, P) }) }
      if (general && byId[general]) r.general2 = bump(byId[general], function () { return LGWP.lines(s, r.max, P) })
    } catch (e) { out.errors.push(r.id + ': ' + e) }
    out.spells.push(r)
  }
  // Goety has no spell power: a focus grows with the enchantments it accepts (Spell.acceptedEnchantments: Potency, Range, Radius...)
  out.goety = []
  try {
    var ii = ForgeRegistries.ITEMS.getKeys().iterator()
    while (ii.hasNext()) {
      var key2 = ii.next(), item = ForgeRegistries.ITEMS.getValue(key2), sp = null
      try { if (typeof item.getSpell === 'function') sp = item.getSpell() } catch (err) { sp = null }
      if (sp == null) continue
      var g = { id: '' + key2, ench: [] }
      try { var el = new (Java.loadClass('java.util.ArrayList'))(sp.acceptedEnchantments()); for (var q = 0; q < el.size(); q++) g.ench.push('' + ForgeRegistries.ENCHANTMENTS.getKey(el.get(q))) } catch (err) { g.err = '' + err }
      out.goety.push(g)
    }
  } catch (err) { out.errors.push('goety: ' + err) }
  JsonIO.write('kubejs/lgw_spellpower.json', out)
  return out
}
// build Iron's spell config the way a datapack sync does, then dump; the line says Fireball's max level (5 when the config is in)
LGWP.start = function (server, tell) {
  try {
    var Sync = Java.loadClass('net.minecraftforge.event.OnDatapackSyncEvent'), SCM = Java.loadClass('io.redspace.ironsspellbooks.api.config.SpellConfigManager')
    SCM.onDatapackSync(new Sync(LGWP.c0(server, 'getPlayerList'), null))
  } catch (e) { tell('lgw_spellpower: config sync failed: ' + e) }
  var SR = Java.loadClass('io.redspace.ironsspellbooks.api.registry.SpellRegistry'), fb = -1, it = SR.REGISTRY.get().getValues().iterator()
  while (it.hasNext()) { var s = it.next(); if (('' + s.getSpellId()) === 'irons_spellbooks:fireball') fb = s.getMaxLevel() }
  var o = LGWP.dump(server)
  tell('lgw_spellpower: ' + o.spells.length + ' spells, ' + o.schools.length + ' schools, ' + o.errors.length + ' errors, Fireball max level ' + fb + ' -> kubejs/lgw_spellpower.json')
}
ServerEvents.customCommand('lgw_spellpower', function (event) { LGWP.start(event.server, function (t) { event.player.tell(t) }) })
ServerEvents.loaded(function (event) {
  var auto = null
  try { auto = JsonIO.read('kubejs/lgw_spellpower_auto.json') } catch (err) { auto = null }
  if (!auto) return
  LGWP.start(event.server, function (t) { console.info(t) })
})
