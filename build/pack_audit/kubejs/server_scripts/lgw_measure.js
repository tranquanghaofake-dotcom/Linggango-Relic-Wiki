// Linggango wiki: measure gear in a running server, the way the game applies it.
// Written for KubeJS's Rhino engine: var only (Rhino treats const/let in a function called again as a redeclaration), no destructuring.
// Run in a test world with cheats on: /kubejs custom_command lgw_measure   (needs kubejs/lgw_items.json from
// build/pack_audit/measure/prep.py; writes kubejs/lgw_measure.json). On a dedicated server the plan can set "auto": true to start
// 200 ticks after the server loads and "stop": true to shut it down when done. Progress goes to chat and the log.
// A Forge FakePlayer stands in for the player. Its tick() does nothing, so the script calls ServerPlayer.doTick(): the full player
// tick (equipment change events, armor ticks, potion effects, attack strength) runs as for a real player.
//  - attributes: every item's modifiers per slot, read from the stack (after attributesetter and the pack's attribute events);
//  - melee: the player swings at a fresh 100,000-health pig with no armor, at full attack strength, HITS times: damage dealt,
//    effects and fire put on the target, effects and health gained by the attacker;
//  - armor: the set is worn for 40 ticks: attribute totals, effects it gives, and a 20-damage hit of each kind sent through
//    LivingHurtEvent -> armor (CombatRules, which Apothic Attributes replaces with its own curve) -> LivingDamageEvent, so set
//    bonuses written as event handlers count. The FakePlayer cannot be hurt for real (isInvulnerableTo is true), hence the events.
var LGW = {}
LGW.run = (server, who, name) => {
  var base = name || 'lgw'
  var ForgeRegistries = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
  var FakePlayerFactory = Java.loadClass('net.minecraftforge.common.util.FakePlayerFactory')
  var GameProfile = Java.loadClass('com.mojang.authlib.GameProfile')
  var UUID = Java.loadClass('java.util.UUID')
  var EquipmentSlot = Java.loadClass('net.minecraft.world.entity.EquipmentSlot')
  var MinecraftForge = Java.loadClass('net.minecraftforge.common.MinecraftForge')
  var LivingHurtEvent = Java.loadClass('net.minecraftforge.event.entity.living.LivingHurtEvent')
  var LivingDamageEvent = Java.loadClass('net.minecraftforge.event.entity.living.LivingDamageEvent')
  var CombatRules = Java.loadClass('net.minecraft.world.damagesource.CombatRules')
  var Attributes = Java.loadClass('net.minecraft.world.entity.ai.attributes.Attributes')
  var DamageTypeTags = Java.loadClass('net.minecraft.tags.DamageTypeTags')
  var ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')

  var plan = JsonIO.read('kubejs/' + base + '_items.json')
  if (!plan) { var m = 'kubejs/' + base + '_items.json is missing'; console.warn('lgw_measure: ' + m); try { who.tell(m) } catch (e) {} return }
  var HITS = plan.hits || 3
  var level = who ? who.level : server.overworld()
  var say = m => { console.info('lgw_measure: ' + m); try { if (who) who.tell(m) } catch (e) {} }
  var out = { started: '' + new Date(), attrs: {}, melee: {}, armor: {}, errors: {} }
  var err = (k, e) => { var m = k + ': ' + e; out.errors[m] = (out.errors[m] || 0) + 1 }
  var P = FakePlayerFactory.get(level, new GameProfile(UUID.fromString('6c9a3f1e-0b7d-4c55-9e2a-1f0d3b4a5c6e'), '[lgw_tester]'))
  // next to whoever ran the command (their chunk is loaded), else above the world spawn
  var sp = level.getSharedSpawnPos()
  var X = who ? Math.floor(who.x) + 0.5 : sp.getX() + 0.5, Y = who ? Math.floor(who.y) + 3 : sp.getY() + 3, Z = who ? Math.floor(who.z) + 0.5 : sp.getZ() + 0.5
  var spawned = []
  var SLOT = { HEAD: EquipmentSlot.HEAD, CHEST: EquipmentSlot.CHEST, LEGS: EquipmentSlot.LEGS, FEET: EquipmentSlot.FEET, MAINHAND: EquipmentSlot.MAINHAND, OFFHAND: EquipmentSlot.OFFHAND }
  var rl = s => new ResourceLocation(s)
  var fx = e => { var o = {}; e.getActiveEffects().forEach(i => { o['' + ForgeRegistries.MOB_EFFECTS.getKey(i.getEffect())] = [i.getAmplifier(), i.getDuration()] }); return o }
  var reset = () => {
    P.getInventory().clearContent(); P.removeAllEffects(); P.clearFire(); P.setPos(X, Y, Z); P.setYRot(-90); P.setXRot(0)
    for (var s in SLOT) P.setItemSlot(SLOT[s], Item.empty)
    for (var i = 0; i < 3; i++) P.doTick()
    P.setHealth(P.getMaxHealth())
  }
  var ticks = n => { for (var i = 0; i < n; i++) { try { P.doTick() } catch (e) { err('doTick', e) } } }

  // 1. attribute modifiers of every planned item, per slot
  var slots = [EquipmentSlot.MAINHAND, EquipmentSlot.OFFHAND, EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET]
  var attrsOf = id => {
    var st = Item.of(id), r = {}
    slots.forEach(sl => {
      var mods; try { mods = st.getAttributeModifiers(sl) } catch (e) { err('mods', e); return }
      if (!mods || mods.isEmpty()) return
      var l = []; mods.entries().forEach(en => { var k = ForgeRegistries.ATTRIBUTES.getKey(en.getKey()); l.push(['' + k, en.getValue().getAmount(), '' + en.getValue().getOperation()]) })
      r['' + sl.getName()] = l
    })
    return r
  }

  // 2. melee: swing at a dummy pig
  var dummy = () => {
    var d = level.createEntity('minecraft:pig'); d.setPos(X + 1.2, Y, Z); d.setNoAi(true); d.setSilent(true); d.setNoGravity(true); d.setInvulnerable(false)
    spawned.push(d)
    d.getAttribute(Attributes.MAX_HEALTH).setBaseValue(100000); d.getAttribute(Attributes.ARMOR).setBaseValue(0); d.setHealth(100000)
    level.addFreshEntity(d); return d
  }
  var known = id => { try { return !Item.of(id).isEmpty() } catch (e) { return false } }
  var melee = id => {
    reset(); P.setItemSlot(EquipmentSlot.MAINHAND, Item.of(id)); ticks(5)
    var r = { ad: P.getAttributeValue(Attributes.ATTACK_DAMAGE), as: P.getAttributeValue(Attributes.ATTACK_SPEED), hits: [] }
    for (var k = 0; k < HITS; k++) {
      var n = 0; while (P.getAttackStrengthScale(0.5) < 1 && n < 400) { ticks(1); n++ }
      var d = dummy(); P.setHealth(Math.max(1, P.getMaxHealth() - 10)); P.removeAllEffects()
      var h0 = d.getHealth(), p0 = P.getHealth()
      try { P.attack(d) } catch (e) { err('attack ' + id, e) }
      r.hits.push({ dmg: Math.round((h0 - d.getHealth()) * 100) / 100, tfx: fx(d), fire: d.getRemainingFireTicks(), sfx: fx(P), heal: Math.round((P.getHealth() - p0) * 100) / 100, wait: n })
      d.discard(); spawned.pop()
    }
    return r
  }

  // 3. armor: wear the set, read what it gives, send test hits through the damage events
  var ATTR = ['minecraft:generic.armor', 'minecraft:generic.armor_toughness', 'minecraft:generic.max_health', 'minecraft:generic.movement_speed', 'minecraft:generic.knockback_resistance',
    'minecraft:generic.attack_damage', 'minecraft:generic.attack_speed', 'minecraft:generic.luck']
  var extraAttrs = () => { var o = {}; P.getAttributes().getSyncableAttributes().forEach(a => { var k = '' + ForgeRegistries.ATTRIBUTES.getKey(a.getAttribute()); var v = a.getValue(), b = a.getAttribute().getDefaultValue(); if (Math.abs(v - b) > 1e-9 || ATTR.indexOf(k) >= 0) o[k] = Math.round(v * 1000) / 1000 }); return o }
  var hurt = () => {
    var ds = level.damageSources(), src = { melee: ds.mobAttack(dummy()), fire: ds.inFire(), magic: ds.magic(), explosion: ds.explosion(null, null), fall: ds.fall() }
    var o = {}
    for (var k in src) {
      var s = src[k]
      try {
        var a = new LivingHurtEvent(P, s, 20); MinecraftForge.EVENT_BUS.post(a); var v = a.isCanceled() ? 0 : a.getAmount()
        if (!s.is(DamageTypeTags.BYPASSES_ARMOR)) v = CombatRules.getDamageAfterAbsorb(v, P.getArmorValue(), P.getAttributeValue(Attributes.ARMOR_TOUGHNESS))
        var b = new LivingDamageEvent(P, s, v); MinecraftForge.EVENT_BUS.post(b)
        o[k] = [Math.round(a.getAmount() * 100) / 100, Math.round((b.isCanceled() ? 0 : b.getAmount()) * 100) / 100]
      } catch (e) { err('hurt ' + k, e) }
    }
    while (spawned.length) { try { spawned.pop().discard() } catch (e) {} }
    return o
  }
  var armor = pieces => {
    reset(); pieces.forEach(pc2 => P.setItemSlot(SLOT[pc2[1]], Item.of(pc2[0]))); ticks(40)
    return { attrs: extraAttrs(), fx: fx(P), hp: P.getHealth(), abs: P.getAbsorptionAmount(), hurt: hurt() }
  }

  // run in slices so one server tick never holds the watchdog
  var jobs = []
  ;(plan.attrs || []).forEach(id => jobs.push(() => { out.attrs[id] = attrsOf(id) }))
  jobs.push(() => { out.melee['(none)'] = melee('minecraft:air'); out.armor['(none)'] = armor([]) })
  ;(plan.melee || []).forEach(id => jobs.push(() => { if (!known(id)) { err('unknown item', id); return } try { out.melee[id] = melee(id) } catch (e) { err('melee ' + id, e) } }))
  ;(plan.sets || []).forEach(s => jobs.push(() => { try { out.armor[s.k] = armor(s.p) } catch (e) { err('armor ' + s.k, e) } }))
  var i = 0, next = 0
  say('starting: ' + jobs.length + ' measurements; the game slows down until it is done')
  var step = () => {
    var t0 = Date.now()
    while (i < jobs.length && Date.now() - t0 < 200) { try { jobs[i]() } catch (e) { err('job', e) } i++ }
    if (i < jobs.length) { var pc = Math.floor(i * 100 / jobs.length); if (pc >= next) { say(pc + '% (' + i + '/' + jobs.length + ')'); next += 10 } server.scheduleInTicks(1, step); return }
    out.finished = '' + new Date()
    JsonIO.write('kubejs/' + base + '_measure.json', out)
    while (spawned.length) { try { spawned.pop().discard() } catch (e) {} }
    say('done: kubejs/' + base + '_measure.json (' + Object.keys(out.melee).length + ' weapons, ' + Object.keys(out.armor).length + ' sets, ' + Object.keys(out.errors).length + ' kinds of error)')
    if (plan.stop) server.runCommandSilent('stop')
  }
  step()
}
ServerEvents.loaded(event => { var p = JsonIO.read('kubejs/lgw_items.json'); if (p && p.auto) event.server.scheduleInTicks(200, () => LGW.run(event.server, null, 'lgw')) })
// lgw_measure_test reads kubejs/lgw_test_items.json (a handful of items, about a minute) and writes kubejs/lgw_test_measure.json
ServerEvents.customCommand('lgw_measure_test', event => {
  try { LGW.run(event.server, event.player, 'lgw_test') } catch (e) { console.error('lgw_measure failed: ' + e); try { event.player.tell('lgw_measure failed: ' + e) } catch (x) {} }
})
ServerEvents.customCommand('lgw_measure', event => {
  try { LGW.run(event.server, event.player, 'lgw') } catch (e) { console.error('lgw_measure failed: ' + e); try { event.player.tell('lgw_measure failed: ' + e) } catch (x) {} }
})
