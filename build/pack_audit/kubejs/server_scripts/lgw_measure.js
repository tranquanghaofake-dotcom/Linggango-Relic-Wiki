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
// Every step is guarded on its own: a failing step is counted in "errors" (grouped by message, with the cause chain, the
// first stack frames and up to 5 item ids) and the rest goes on. A check of each step runs first and is reported in chat,
// as are the first 3 kinds of error.
// Minecraft methods are called through K(): Rhino turns the runtime (SRG) names into Mojang ones, but not on every class
// (the first run failed on FakePlayer.clearFire, likely a mod's mixin redeclaring it), so each call falls back to the SRG
// name. The table comes from Mojang's server.txt and MCPConfig's joined.tsrg for 1.20.1, matched by full descriptor.
var LGW = {}
LGW.SRG = {
  clearFire: ['m_20095_'], setPos: ['m_6034_'], setYRot: ['m_146922_'], setXRot: ['m_146926_'], getRemainingFireTicks: ['m_20094_'],
  discard: ['m_146870_'], setNoGravity: ['m_20242_'], setSilent: ['m_20225_'], setInvulnerable: ['m_20331_'],
  damageSources: ['m_269291_', 'm_269111_'], getX: ['m_20185_', 'm_123341_'], getY: ['m_20186_', 'm_123342_'], getZ: ['m_20189_', 'm_123343_'],
  removeAllEffects: ['m_21219_'], getActiveEffects: ['m_21220_'], getAttributeValue: ['m_21133_'], getAttribute: ['m_21051_', 'm_22099_'],
  setHealth: ['m_21153_'], getMaxHealth: ['m_21233_'], getHealth: ['m_21223_'], getArmorValue: ['m_21230_'], getAttributes: ['m_21204_'],
  getInventory: ['m_150109_'], getAttackStrengthScale: ['m_36403_'], attack: ['m_5706_'], getAbsorptionAmount: ['m_6103_'],
  setItemSlot: ['m_8061_'], doTick: ['m_9240_'], setNoAi: ['m_21557_'], getSharedSpawnPos: ['m_220360_'], addFreshEntity: ['m_7967_'],
  clearContent: ['m_6211_'], setBaseValue: ['m_22100_'], getValue: ['m_22135_'], getSyncableAttributes: ['m_22170_'],
  getDefaultValue: ['m_22082_'], getEffect: ['m_19544_'], getAmplifier: ['m_19564_'], getDuration: ['m_19557_'],
  mobAttack: ['m_269333_'], inFire: ['m_269387_'], magic: ['m_269425_'], explosion: ['m_269036_'], fall: ['m_268989_'],
  is: ['m_269533_'], getDamageAfterAbsorb: ['m_19272_'], isEmpty: ['m_41619_'], create: ['m_20615_'],
  setRemainingFireTicks: ['m_7311_'], moveTo: ['m_7678_'], hurt: ['m_6469_'], getLastDamageSource: ['m_21225_'], playerAttack: ['m_269075_'],
  hurtEnemy: ['m_41640_'], getMainHandItem: ['m_21205_'], getLookAngle: ['m_20154_'],
  getAdvancements: ['m_129889_', 'm_8960_'], getAdvancement: ['m_136041_'], award: ['m_135988_'], getOrStartProgress: ['m_135996_'],
  getCriteria: ['m_138325_'], isDone: ['m_8193_'], grantProgress: ['m_8196_'], getAbilities: ['m_150110_'],
  setYBodyRot: ['m_5618_'], setYHeadRot: ['m_5616_'],
  releaseUsing: ['m_5551_'], getUseDuration: ['m_8105_'], use: ['m_7203_'], getItem: ['m_41720_'], add: ['m_36054_'], isCharged: ['m_40932_'],
  isUsingItem: ['m_6117_'], releaseUsingItem: ['m_21253_'], getTicksUsingItem: ['m_21252_'], arrow: ['m_269418_'], getEncodeId: ['m_20078_'],
  getDeltaMovement: ['m_20184_'], getBaseDamage: ['m_36789_'], getOwner: ['m_19749_'], setOwner: ['m_5602_'], shoot: ['m_6686_']
}
LGW.FLD = { MAX_HEALTH: 'f_22276_', ARMOR: 'f_22284_', ARMOR_TOUGHNESS: 'f_22285_', ATTACK_DAMAGE: 'f_22281_', ATTACK_SPEED: 'f_22283_',
  BYPASSES_ARMOR: 'f_268490_', EMPTY: 'f_41583_', instabuild: 'f_35937_', hurtTime: 'f_20916_' }
// the member name to use on o: the Mojang one if Rhino shows it, else the first SRG name o has
LGW.K = (o, n) => {
  try { if (typeof o[n] === 'function') return n } catch (x) {}
  var l = LGW.SRG[n] || []
  for (var j = 0; j < l.length; j++) { try { if (typeof o[l[j]] === 'function') return l[j] } catch (x) {} }
  return n
}
// No == or === against null on Java values: KubeJS's Rhino runs both through specialEquals, and an empty ItemStack equals null
// there (ItemStack.EMPTY looked missing). typeof does not compare. A missing member reads as undefined on an object and
// throws on a class.
LGW.none = v => typeof v === 'undefined'
LGW.fld = (o, n) => {
  var v; try { v = o[n] } catch (x) {}
  if (LGW.none(v)) { try { v = o[LGW.FLD[n]] } catch (x) {} }
  return v
}
// the message of a caught error with its Java causes and where the deepest one was thrown
LGW.why = e => {
  var s = '' + e, t = null, last = null, n = 0
  try { t = e && e.javaException ? e.javaException : (e && e.getStackTrace ? e : null) } catch (x) {}
  try {
    while (t && n < 6) { last = t; if (n > 0) s += ' <- ' + t; var c = t.getCause(); if (!c || c == t) break; t = c; n++ }
    if (last) { var st = last.getStackTrace(), fr = []; for (var k = 0; k < st.length && fr.length < 8; k++) fr.push('' + st[k]); s += ' @ ' + fr.join(' | ') }
  } catch (x) {}
  return s
}
LGW.run = (server, who, name) => {
  var base = name || 'lgw'
  var K = LGW.K, fld = LGW.fld
  // calls by arity: Rhino picks the overload by argument count, so no padding with undefined
  var c0 = (o, n) => o[K(o, n)]()
  var c1 = (o, n, a) => o[K(o, n)](a)
  var c2 = (o, n, a, b) => o[K(o, n)](a, b)
  var c3 = (o, n, a, b, d) => o[K(o, n)](a, b, d)
  var c4 = (o, n, a, b, d, e) => o[K(o, n)](a, b, d, e)
  var c5 = (o, n, a, b, d, e, f) => o[K(o, n)](a, b, d, e, f)
  var ForgeRegistries = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
  var FakePlayerFactory = Java.loadClass('net.minecraftforge.common.util.FakePlayerFactory')
  var GameProfile = Java.loadClass('com.mojang.authlib.GameProfile')
  var UUID = Java.loadClass('java.util.UUID')
  var EquipmentSlot = Java.loadClass('net.minecraft.world.entity.EquipmentSlot')
  var MinecraftForge = Java.loadClass('net.minecraftforge.common.MinecraftForge')
  var LivingHurtEvent = Java.loadClass('net.minecraftforge.event.entity.living.LivingHurtEvent')
  var LivingDamageEvent = Java.loadClass('net.minecraftforge.event.entity.living.LivingDamageEvent')
  var LivingAttackEvent = Java.loadClass('net.minecraftforge.event.entity.living.LivingAttackEvent')
  var AttackEntityEvent = Java.loadClass('net.minecraftforge.event.entity.player.AttackEntityEvent')
  var CombatRules = Java.loadClass('net.minecraft.world.damagesource.CombatRules')
  var Attributes = Java.loadClass('net.minecraft.world.entity.ai.attributes.Attributes')
  var DamageTypeTags = Java.loadClass('net.minecraft.tags.DamageTypeTags')
  var ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
  var EMPTY = fld(Java.loadClass('net.minecraft.world.item.ItemStack'), 'EMPTY')
  if (LGW.none(EMPTY)) EMPTY = Item.of('minecraft:air')
  var A_HP = fld(Attributes, 'MAX_HEALTH'), A_ARMOR = fld(Attributes, 'ARMOR'), A_TOUGH = fld(Attributes, 'ARMOR_TOUGHNESS')
  var A_AD = fld(Attributes, 'ATTACK_DAMAGE'), A_AS = fld(Attributes, 'ATTACK_SPEED'), T_BYPASS = fld(DamageTypeTags, 'BYPASSES_ARMOR')

  var plan = JsonIO.read('kubejs/' + base + '_items.json')
  if (!plan) { var m = 'kubejs/' + base + '_items.json is missing'; console.warn('lgw_measure: ' + m); try { who.tell(m) } catch (e) {} return }
  var HITS = plan.hits || 3
  var level = who ? who.level : server.overworld()
  var say = m => { console.info('lgw_measure: ' + m); try { if (who) who.tell(m) } catch (e) {} }
  var out = { started: '' + new Date(), check: {}, attrs: {}, melee: {}, armor: {}, grows: {}, curios: {}, ranged: {}, blocks: {}, errors: {} }
  var told = 0
  var err = (stage, e, id) => {
    var w = typeof e == 'string' ? e : LGW.why(e), k = stage + ': ' + w.split(' @ ')[0].substring(0, 300)
    var o = out.errors[k]; if (!o) { o = out.errors[k] = { n: 0, ids: [], at: w }; if (told++ < 3) say('error ' + k.substring(0, 240)) }
    o.n++; if (id && o.ids.length < 5) o.ids.push(id)
  }
  var safe = (stage, f, id) => { try { f(); return true } catch (e) { err(stage, e, id); return false } }
  var P = FakePlayerFactory.get(level, new GameProfile(UUID.fromString('6c9a3f1e-0b7d-4c55-9e2a-1f0d3b4a5c6e'), '[lgw_tester]'))
  // next to whoever ran the command (their chunk is loaded), else above the world spawn
  var X, Y, Z
  if (who) { X = Math.floor(who.x) + 0.5; Y = Math.floor(who.y) + 3; Z = Math.floor(who.z) + 0.5 }
  else { var sp = c0(level, 'getSharedSpawnPos'); X = c0(sp, 'getX') + 0.5; Y = c0(sp, 'getY') + 3; Z = c0(sp, 'getZ') + 0.5 }
  var spawned = []
  // Armageddon's progression: tools and armor of a tier deal no damage (LivingAttackEvent cancelled) until the player has that
  // tier's Keeper advancement (fourth run: every weapon hit cancelled by DiamondToolsDealingDamagesPreventionProcedure). The tester
  // is given them all, i.e. it measures a player past every Keeper; creative would skip the check too but changes other mods.
  // Linggango's own item gates exempt FakePlayers.
  var KEEPERS = ['the_iron_keeper', 'the_gold_keeper', 'the_emerald_keeper', 'the_diamond_keeper', 'the_netherite_keeper', 'the_blood_keeper',
    'the_shadow_keeper', 'the_cataclysm_keeper', 'the_elvenite_keeper', 'the_voiderite_keeper', 'the_sun_keeper', 'overworld_conqueror']
  var grant = () => {
    var mgr, pa, got = [], miss = []
    if (!safe('grant', () => { mgr = c0(server, 'getAdvancements'); pa = c0(P, 'getAdvancements') })) { say('could not give the tester the Keeper advancements'); return }
    KEEPERS.forEach(k => {
      var ok = safe('grant ' + k, () => {
        var adv = c1(mgr, 'getAdvancement', new ResourceLocation('armageddon_mod:' + k))
        if (('' + adv) === 'null') throw 'no such advancement'
        // Forge's award() refuses FakePlayers (fifth run: 0 of 12), so the progress is also ticked off directly
        var crit = c0(adv, 'getCriteria').keySet()
        crit.forEach(cr => { try { c2(pa, 'award', adv, cr) } catch (e) {} })
        var pr = c1(pa, 'getOrStartProgress', adv)
        if (!c0(pr, 'isDone')) crit.forEach(cr => { c1(pr, 'grantProgress', cr) })
        if (!c0(pr, 'isDone')) throw 'not done after award or grantProgress'
      })
      ;(ok ? got : miss).push(k)
    })
    out.granted = got; if (miss.length) out.notGranted = miss
    // last resort: Armageddon lets abilities.instabuild through; only that flag is set, the game mode stays survival
    if (miss.length) {
      var ok = safe('instabuild', () => {
        var ab = c0(P, 'getAbilities')
        try { ab.instabuild = true } catch (e) {}
        if (fld(ab, 'instabuild') !== true) ab[LGW.FLD.instabuild] = true
        if (fld(ab, 'instabuild') !== true) throw 'flag did not stick'
      })
      out.instabuild = ok
      say(ok ? 'Keepers not given; abilities.instabuild set instead (Armageddon lets it through)' : 'neither the Keepers nor instabuild could be set: tiered weapons will read 0')
    }
    say('tester given ' + got.length + '/' + KEEPERS.length + ' Armageddon Keeper advancements' + (miss.length ? ' (missing: ' + miss.join(', ') + ')' : ''))
  }
  var SLOT = { HEAD: EquipmentSlot.HEAD, CHEST: EquipmentSlot.CHEST, LEGS: EquipmentSlot.LEGS, FEET: EquipmentSlot.FEET, MAINHAND: EquipmentSlot.MAINHAND, OFFHAND: EquipmentSlot.OFFHAND }
  var rl = s => new ResourceLocation(s)
  var hp = e => c0(e, 'getHealth')
  var wear = (sl, st) => c2(P, 'setItemSlot', sl, st)
  var fx = e => {
    var o = {}
    c0(e, 'getActiveEffects').forEach(i => { o['' + ForgeRegistries.MOB_EFFECTS.getKey(c0(i, 'getEffect'))] = [c0(i, 'getAmplifier'), c0(i, 'getDuration')] })
    return o
  }
  // doTick() runs every mod's player-tick handler on the fake player; after 5 failures in a row it is left out and the
  // rest is measured without ticks (attack strength then does not recharge: each hit records the strength it had)
  var tickOk = true, tickFails = 0
  var ticks = n => {
    for (var i = 0; i < n && tickOk; i++) {
      if (safe('doTick', () => c0(P, 'doTick'))) tickFails = 0
      else if (++tickFails >= 5) { tickOk = false; say('the player tick keeps failing; going on without it') }
    }
  }
  var reset = () => {
    safe('reset inventory', () => c0(c0(P, 'getInventory'), 'clearContent'))
    safe('reset effects', () => c0(P, 'removeAllEffects'))
    // clearFire and setYRot are not reachable on the FakePlayer under either name (second run); these do the same
    safe('reset fire', () => { try { c0(P, 'clearFire') } catch (e) { c1(P, 'setRemainingFireTicks', 0) } })
    // facing +x matters for shots (third test run: moveTo fell back to setPos and the tester faced south). KubeJS's own
    // setPositionAndRotation runs on the Java side, clear of Rhino's member names
    safe('reset position', () => { try { P.setPositionAndRotation(X, Y, Z, -90, 0) } catch (e) { try { c5(P, 'moveTo', X, Y, Z, -90, 0) } catch (e2) { c3(P, 'setPos', X, Y, Z) } } })
    safe('reset slots', () => { for (var s in SLOT) wear(SLOT[s], EMPTY) })
    safe('reset curios', () => clearCurios())
    ticks(3)
    safe('reset health', () => c1(P, 'setHealth', c0(P, 'getMaxHealth')))
  }

  // 1. attribute modifiers of every planned item, per slot
  var slots = [EquipmentSlot.MAINHAND, EquipmentSlot.OFFHAND, EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET]
  var attrsOf = id => {
    var st = Item.of(id), r = {}
    slots.forEach(sl => {
      var mods; try { mods = st.getAttributeModifiers(sl) } catch (e) { err('mods', e, id); return }
      if (!mods || mods.isEmpty()) return
      var l = []; mods.entries().forEach(en => { var k = ForgeRegistries.ATTRIBUTES.getKey(en.getKey()); l.push(['' + k, en.getValue().getAmount(), '' + en.getValue().getOperation()]) })
      r['' + sl.getName()] = l
    })
    return r
  }

  // 2. melee: swing at a dummy pig
  var types = {}
  var newEnt = id => {
    try { return level.createEntity(id) } catch (e) {}
    if (!types[id]) types[id] = ForgeRegistries.ENTITY_TYPES.getValue(rl(id))
    return c1(types[id], 'create', level)
  }
  var newPig = () => newEnt('minecraft:pig')
  // the test target: a pig with no AI and no armor, o.dx blocks in front of the tester (who looks along +x; default 1.2), raised
  // o.dy (a shot leaves the eyes, so a pig for shots floats at eye height). o.max / o.cur set its max and current health (default
  // 100,000 both); o.yaw turns it: 90 faces the tester, -90 turns its back, 0 side-on. moveTo on a pig resolves to another
  // overload (second extra run: 48 "turn pig" errors), so the rotations are set one by one
  var dummy = o => {
    o = o || {}
    var d = newPig(), mx = o.max || 100000, cu = o.cur || mx
    c3(d, 'setPos', X + (o.dx || 1.2), Y + (o.dy || 0), Z); c1(d, 'setNoAi', true); c1(d, 'setSilent', true); c1(d, 'setNoGravity', true); c1(d, 'setInvulnerable', false)
    if (typeof o.yaw === 'number') safe('turn pig', () => { d.setRotation(o.yaw, 0); c1(d, 'setYBodyRot', o.yaw); c1(d, 'setYHeadRot', o.yaw) })
    spawned.push(d)
    c1(c1(d, 'getAttribute', A_HP), 'setBaseValue', mx); c1(c1(d, 'getAttribute', A_ARMOR), 'setBaseValue', 0); c1(d, 'setHealth', cu)
    c1(level, 'addFreshEntity', d); return d
  }
  var drop = d => { safe('discard', () => c0(d, 'discard')); var j = spawned.indexOf(d); if (j >= 0) spawned.splice(j, 1) }
  // the hit as the damage events see it, for when Player.attack is stopped before it hurts the target (third run: every weapon
  // hit cancelled, the bare hand not): LivingAttackEvent -> LivingHurtEvent -> (no armor on the pig) -> LivingDamageEvent with
  // the player's attack damage, then the held stack's hurtEnemy (on-hit effects written on the item). Mixins into
  // Player.attack and the vanilla enchantment / crit / sweep maths are not in it.
  var evHit = () => {
    var d = dummy(), r = {}, amt = c1(P, 'getAttributeValue', A_AD), src = c1(c0(P, 'damageSources'), 'playerAttack', P)
    safe('event hit', () => {
      var a = new LivingAttackEvent(d, src, amt); MinecraftForge.EVENT_BUS.post(a)
      if (a.isCanceled()) { r.cancelled = 'LivingAttackEvent'; return }
      var h = new LivingHurtEvent(d, src, amt); MinecraftForge.EVENT_BUS.post(h); amt = h.isCanceled() ? 0 : h.getAmount()
      var g = new LivingDamageEvent(d, src, amt); MinecraftForge.EVENT_BUS.post(g); amt = g.isCanceled() ? 0 : g.getAmount()
      r.dmg = Math.round(amt * 100) / 100
    })
    safe('event hit hurtEnemy', () => { var st = c0(P, 'getMainHandItem'); c2(st, 'hurtEnemy', d, P) })
    r.tfx = fx(d); r.fire = c0(d, 'getRemainingFireTicks'); r.sfx = fx(P)
    drop(d)
    return r
  }
  var known = id => { try { return !c0(Item.of(id), 'isEmpty') } catch (e) { return false } }
  // n swings at full attack strength, each at a fresh pig (o: its health and facing, see dummy); keepFx leaves the tester's
  // effects on (a curio's worn effects), else they are cleared so a hit's own effects on the attacker show
  var swings = (n, id, o, keepFx) => {
    var hits = []
    for (var k = 0; k < n; k++) {
      var w = 0; while (tickOk && c1(P, 'getAttackStrengthScale', 0.5) < 1 && w < 400) { ticks(1); w++ }
      var d = dummy(o); c1(P, 'setHealth', Math.max(1, c0(P, 'getMaxHealth') - 10)); if (!keepFx) c0(P, 'removeAllEffects')
      var h0 = hp(d), p0 = hp(P), str = c1(P, 'getAttackStrengthScale', 0.5)
      safe('attack', () => c1(P, 'attack', d), id)
      hits.push({ dmg: Math.round((h0 - hp(d)) * 100) / 100, str: Math.round(str * 100) / 100, tfx: fx(d), fire: c0(d, 'getRemainingFireTicks'), sfx: fx(P), heal: Math.round((hp(P) - p0) * 100) / 100, wait: w })
      drop(d)
    }
    return hits
  }
  var melee = id => {
    reset(); wear(EquipmentSlot.MAINHAND, Item.of(id)); ticks(5)
    var r = { ad: c1(P, 'getAttributeValue', A_AD), as: c1(P, 'getAttributeValue', A_AS), ticked: tickOk, hits: swings(HITS, id) }
    if (r.hits.every(h => h.dmg == 0)) r.ev = evHit()
    return r
  }
  // a weapon whose hit rose far above its attack damage on the 100,000-health pig (first full run): two swings at each target,
  // to split damage from the target's max health, from its current health, and from where the tester stands
  var TARGETS = [['max1000', { max: 1000 }], ['max10000', { max: 10000 }], ['max100000', { max: 100000 }], ['cur5000', { max: 10000, cur: 5000 }],
    ['front', { max: 10000, yaw: 90 }], ['behind', { max: 10000, yaw: -90 }]]
  var grows = id => {
    reset(); wear(EquipmentSlot.MAINHAND, Item.of(id)); ticks(5)
    var r = { ad: c1(P, 'getAttributeValue', A_AD), as: c1(P, 'getAttributeValue', A_AS) }
    TARGETS.forEach(t => { r[t[0]] = swings(2, id, t[1]).map(h => h.dmg) })
    return r
  }

  // 3. armor: wear the set, read what it gives, send test hits through the damage events
  var ATTR = ['minecraft:generic.armor', 'minecraft:generic.armor_toughness', 'minecraft:generic.max_health', 'minecraft:generic.movement_speed', 'minecraft:generic.knockback_resistance',
    'minecraft:generic.attack_damage', 'minecraft:generic.attack_speed', 'minecraft:generic.luck']
  var extraAttrs = () => {
    var o = {}
    c0(c0(P, 'getAttributes'), 'getSyncableAttributes').forEach(a => {
      var at = c0(a, 'getAttribute'), k = '' + ForgeRegistries.ATTRIBUTES.getKey(at), v = c0(a, 'getValue'), b = c0(at, 'getDefaultValue')
      if (Math.abs(v - b) > 1e-9 || ATTR.indexOf(k) >= 0) o[k] = Math.round(v * 1000) / 1000
    })
    return o
  }
  var cur = ''
  // magic and fall skip armor in vanilla's bypasses_armor tag; the tag is read when it can be
  var bypass = (k, s) => { try { return !!c1(s, 'is', T_BYPASS) } catch (e) { return k == 'magic' || k == 'fall' } }
  // amt: the test hit (20 for armor; 8 for curios, under the pack's cap of a melee hit at half the bare tester's 20 health,
  // which would hide a curio's damage reduction)
  var hurt = amt => {
    amt = amt || 20
    var ds = c0(level, 'damageSources'), src = {}, o = {}
    safe('hurt sources', () => {
      src.melee = c1(ds, 'mobAttack', dummy()); src.fire = c0(ds, 'inFire'); src.magic = c0(ds, 'magic')
      src.explosion = c2(ds, 'explosion', null, null); src.fall = c0(ds, 'fall')
    }, cur)
    for (var k in src) {
      var s = src[k]
      try {
        var a = new LivingHurtEvent(P, s, amt); MinecraftForge.EVENT_BUS.post(a); var v = a.isCanceled() ? 0 : a.getAmount()
        if (!bypass(k, s)) v = c3(CombatRules, 'getDamageAfterAbsorb', v, c0(P, 'getArmorValue'), c1(P, 'getAttributeValue', A_TOUGH))
        var b = new LivingDamageEvent(P, s, v); MinecraftForge.EVENT_BUS.post(b)
        o[k] = [Math.round(a.getAmount() * 100) / 100, Math.round((b.isCanceled() ? 0 : b.getAmount()) * 100) / 100]
      } catch (e) { err('hurt ' + k, e, cur) }
    }
    while (spawned.length) drop(spawned[spawned.length - 1])
    return o
  }
  // curios (Curios API): equipped in the first slot type the item takes, the slot grown if the tester has none of that type
  var CuriosApi = null
  try { CuriosApi = Java.loadClass('top.theillusivec4.curios.api.CuriosApi') } catch (e) {}
  var curioInv = () => { var o = CuriosApi.getCuriosInventory(P).resolve(); if (!o.isPresent()) throw 'the tester has no curios inventory'; return o.get() }
  var clearCurios = () => { if (!CuriosApi) return; curioInv().getCurios().values().forEach(sh => { var st = sh.getStacks(); for (var j = 0; j < st.getSlots(); j++) st.setStackInSlot(j, EMPTY) }) }
  var equipCurio = id => {
    var st = Item.of(id), h = curioInv(), ids = []
    CuriosApi.getItemStackSlots(st, P).keySet().forEach(k => ids.push('' + k))
    if (!ids.length) throw 'no curio slot takes it'
    var slot = ids[0], o = h.getStacksHandler(slot)
    if (!o.isPresent()) throw 'the tester has no ' + slot + ' slot type'
    if (o.get().getSlots() < 1) { try { h.growSlotType(slot, 1) } catch (e) { o.get().grow(1) } }
    h.setEquippedCurio(slot, 0, st)
    return slot
  }
  // a curio worn for 40 ticks: attribute totals, effects, health, then two diamond-sword swings (damage and on-hit effects with it
  // on) and the damage-taken test
  var REF = 'minecraft:diamond_sword'
  var curio = id => {
    reset(); var r = {}
    if (id) r.slot = equipCurio(id)
    ticks(40)
    r.attrs = extraAttrs(); r.fx = fx(P); r.hp = hp(P); r.abs = c0(P, 'getAbsorptionAmount')
    wear(EquipmentSlot.MAINHAND, Item.of(REF)); ticks(5)
    r.hits = swings(2, id || REF, null, true)
    r.hurt = hurt(8)
    return r
  }
  // 4. shots: a bow, crossbow or thrown weapon drawn 40 ticks (bows reach full draw at 20) and let go, or for a crossbow loaded and
  // then fired, at a 10,000-health pig 5 blocks ahead at eye height; the arrow flies on the server's own ticks, so the job waits
  // 20 ticks before reading the pig. Three shots, a fresh pig each; arrows are given (64) and cleared after
  var MAIN = Java.loadClass('net.minecraft.world.InteractionHand').MAIN_HAND
  var clearShots = () => { try { server.runCommandSilent('kill @e[type=#minecraft:arrows]') } catch (e) {} }
  var r1 = v => Math.round(v * 10) / 10
  // the projectiles around the tester: what flies, where (blocks from the tester), how fast, its base damage and owner. Third
  // run: 113 of 118 shooters did no damage, yet Frostbite and Winter Bow left their effect on the pig, so a shot can land and
  // still do nothing
  var near = () => {
    var all = null, l = []
    try { all = level.getEntities() } catch (e) { try { all = level.entities } catch (e2) {} }
    if (!all) return null
    all.forEach(e => {
      var id = ''; try { id = '' + c0(e, 'getEncodeId') } catch (x) {}
      if (!id || id == 'null' || id == 'minecraft:pig') return
      var x = c0(e, 'getX') - X, y = c0(e, 'getY') - Y, z = c0(e, 'getZ') - Z
      if (Math.abs(x) > 24 || Math.abs(y) > 12 || Math.abs(z) > 24) return
      var o = { id: id, at: [r1(x), r1(y), r1(z)] }
      try { o.v = '' + c0(e, 'getDeltaMovement') } catch (x2) {}
      try { o.base = c0(e, 'getBaseDamage') } catch (x2) {}
      try { var w = c0(e, 'getOwner'); o.owner = w ? ('' + w).substring(0, 40) : 'none' } catch (x2) {}
      o.e = e; l.push(o)
    })
    return l
  }
  var plain = l => l ? l.map(o => { var c = {}; for (var k in o) if (k != 'e') c[k] = o[k]; return c }) : l
  // what the pig was last hurt by, and its hurt timer (10 right after a hit that landed)
  var hitOf = d => { var o = {}; try { o.src = '' + c0(d, 'getLastDamageSource') } catch (e) {} try { o.hurtTime = fld(d, 'hurtTime') } catch (e) {} return o }
  // 4. shots: a pig 5 blocks in front of the tester at eye height, shot the way a player does: use() (right click), 40 ticks of
  // drawing, releaseUsingItem() (letting go), and a charged crossbow used again to fire; an item that is not drawn (thrown
  // weapons) is thrown by use(). Arrows in the off hand, where a bow looks first (third test run: added to the inventory they
  // went into the held slot and the bow replaced them); the item is held afresh for each shot (a thrown trident leaves the hand).
  // In a probe run each shot also notes the projectiles 3 ticks after it and the pig's last damage source, and the first
  // projectile's hit is walked through the damage events' listeners
  var ranged = id => {
    reset(); wear(EquipmentSlot.OFFHAND, Item.of('minecraft:arrow', 64))
    var r = { ad: c1(P, 'getAttributeValue', A_AD), shots: [] }, k = 0
    var shot = () => {
      wear(EquipmentSlot.MAINHAND, Item.of(id)); ticks(5)
      var d = dummy({ max: 10000, dx: 5, dy: 0.9 }), h0 = hp(d), st = c0(P, 'getMainHandItem'), how = '', s = {}
      safe('shoot', () => {
        var it = c0(st, 'getItem')
        c3(it, 'use', level, P, MAIN)
        if (!c0(P, 'isUsingItem')) { how = 'use'; return }
        ticks(40); s.drawn = c0(P, 'getTicksUsingItem'); c0(P, 'releaseUsingItem'); how = 'draw'
        var cb = false; try { cb = !!c1(it, 'isCharged', st) } catch (e) {}
        if (cb) { c3(it, 'use', level, P, MAIN); how = 'crossbow' }
      }, id)
      var fin = () => {
        s.dmg = Math.round((h0 - hp(d)) * 100) / 100; s.how = how; s.tfx = fx(d); s.fire = c0(d, 'getRemainingFireTicks')
        if (plan.probe) { var h = hitOf(d); s.src = h.src; s.hurtTime = h.hurtTime }
        r.shots.push(s); drop(d); clearShots()
        if (++k < 3) return shot()
        out.ranged[id] = r; return null
      }
      if (!plan.probe) return { wait: 20, then: fin }
      return { wait: 3, then: () => {
        var l = near(); s.flying = plain(l)
        if (k == 0 && l && l.length) safe('trace shot', () => {
          var t = { of: l[0].id }, dd = dummy(); walkHit(t, dd, c2(c0(level, 'damageSources'), 'arrow', l[0].e, P), id); r.trace = t; drop(dd)
        }, id)
        return { wait: 17, then: () => { s.after = plain(near()); return fin() } } } }
    }
    return shot()
  }
  // a probe run first shoots plain arrows from the script itself, owned by the tester and owned by no one, at the same pig: if
  // those land and the bows' do not, the draw is at fault; if the owned one does nothing and the ownerless one hurts, the
  // tester's ownership is
  var arrowProbe = owned => {
    var d = dummy({ max: 10000, dx: 5, dy: 0.9 }), h0 = hp(d), o = { owned: owned }, a = null
    safe('probe arrow', () => {
      a = newEnt('minecraft:arrow'); c3(a, 'setPos', X + 0.8, Y + 1.35, Z)
      if (owned) c1(a, 'setOwner', P)
      c5(a, 'shoot', 1, 0, 0, 3, 0); c1(level, 'addFreshEntity', a)
    })
    return { wait: 20, then: () => { o.dmg = Math.round((h0 - hp(d)) * 100) / 100; var h = hitOf(d); o.src = h.src; o.hurtTime = h.hurtTime
      o.after = plain(near()); out.probe.push(o); drop(d); clearShots()
      say('plain arrow ' + (owned ? 'owned by the tester' : 'with no owner') + ': ' + o.dmg + ' damage, pig last hurt by ' + o.src); return null } }
  }
  // 5. a curio that cancelled its one test hit (first extra run): ten 8-damage hits 20 ticks apart (the tester ticked through
  // them too, so cooldowns run either way), to see how often it blocks
  var blocks = id => {
    reset(); equipCurio(id); ticks(40)
    var res = [], k = 0
    var one = () => {
      var h = hurt(8); res.push(h.melee ? h.melee[1] : null)
      if (++k < 10) { ticks(20); return { wait: 20, then: one } }
      out.blocks[id] = res; return null
    }
    return one()
  }
  var armor = pieces => {
    reset(); pieces.forEach(pc2 => wear(SLOT[pc2[1]], Item.of(pc2[0]))); ticks(40)
    return { attrs: extraAttrs(), fx: fx(P), hp: hp(P), abs: c0(P, 'getAbsorptionAmount'), ticked: tickOk, hurt: hurt() }
  }

  // the listeners of an event class on the Forge bus: each mod has its own bus too (400+), so take the bus id with the most
  var listeners = ev => {
    var best = null, bus = -1
    for (var b = 0; b < 4096; b++) {
      var l; try { l = ev.getListenerList().getListeners(b) } catch (e) { if (b > 64) break; continue }
      if (l && (!best || l.length > best.length)) { best = l; bus = b }
    }
    return [best, bus]
  }
  var walk = (r, name, mk, amt) => {
    var o = {}, ev = mk()
    MinecraftForge.EVENT_BUS.post(ev); o.posted = ev.isCanceled() ? 'cancelled' : (amt ? ev.getAmount() : 'passed')
    var lb = listeners(ev), ls = lb[0], steps = []
    o.bus = lb[1]; o.listeners = ls ? ls.length : 0
    if (ls) {
      ev = mk(); var a0 = amt ? ev.getAmount() : 0
      for (var j = 0; j < ls.length; j++) {
        try { ls[j].invoke(ev) } catch (e) { steps.push('threw ' + ls[j] + ': ' + e) }
        if (ev.isCanceled()) { steps.push('CANCELLED by ' + ls[j]); break }
        if (amt) { var a1 = ev.getAmount(); if (Math.abs(a1 - a0) > 1e-6) { steps.push(a0 + ' -> ' + a1 + ' by ' + ls[j]); a0 = a1 } }
      }
    }
    o.steps = steps; r[name] = o
  }
  // the three damage events of a hit from src on d, listener by listener
  var walkHit = (r, d, src, id) => {
    safe('trace LivingAttackEvent', () => walk(r, 'LivingAttackEvent', () => new LivingAttackEvent(d, src, 15), true), id)
    safe('trace LivingHurtEvent', () => walk(r, 'LivingHurtEvent', () => new LivingHurtEvent(d, src, 15), true), id)
    safe('trace LivingDamageEvent', () => walk(r, 'LivingDamageEvent', () => new LivingDamageEvent(d, src, 15), true), id)
  }
  // why a weapon hit does no damage (second run: 0 for every weapon, 1 bare-handed): each Forge event of the hit is run through
  // its listeners one at a time, the way EventBus.post does, noting which listener cancels it or changes the amount; then a
  // direct hurt() and a real attack on fresh pigs
  var trace = id => {
    reset(); wear(EquipmentSlot.MAINHAND, Item.of(id)); ticks(30)
    var r = { item: id, ad: c1(P, 'getAttributeValue', A_AD), str: c1(P, 'getAttackStrengthScale', 0.5) }, d = dummy()
    var src = c1(c0(P, 'damageSources'), 'playerAttack', P)
    safe('trace AttackEntityEvent', () => walk(r, 'AttackEntityEvent', () => new AttackEntityEvent(P, d), false), id)
    walkHit(r, d, src, id)
    drop(d)
    safe('trace event hit', () => { r.eventHit = evHit() }, id)
    safe('trace attack', () => { var e = dummy(), h = hp(e); c1(P, 'attack', e); r.attack = h - hp(e); r.lastSource = '' + c0(e, 'getLastDamageSource'); drop(e) }, id)
    return r
  }

  // 0. check each step once and say in chat which ones work
  var check = () => {
    var r = []
    var t = (name, f) => { var ok = safe('check ' + name, f); out.check[name] = ok; r.push(name + (ok ? ' ok' : ' FAILED')) }
    t('reset', () => { reset(); out.check.look = '' + c0(P, 'getLookAngle') })
    t('tick', () => c0(P, 'doTick'))
    t('pig', () => { drop(dummy()) })
    t('hold', () => wear(EquipmentSlot.MAINHAND, Item.of('minecraft:iron_sword')))
    t('attack', () => { var d = dummy(), h = hp(d); c1(P, 'attack', d); out.check.ironSword = h - hp(d); drop(d) })
    t('hurt', () => { var h = hurt(); if (!Object.keys(h).length) throw 'no damage kind worked' })
    say('check: ' + r.join(', '))
    out.trace = [trace('minecraft:diamond_sword'), trace('minecraft:air')]
    var tr = out.trace[0]
    var stop = ['AttackEntityEvent', 'LivingAttackEvent'].filter(k => tr[k] && tr[k].posted == 'cancelled')
    var by = []; stop.forEach(k => tr[k].steps.forEach(x => { if (('' + x).indexOf('CANCELLED') == 0) by.push(x) }))
    say('diamond sword: attack ' + tr.attack + ', event hit ' + (tr.eventHit ? tr.eventHit.dmg : '?') + '; cancelled: ' + (stop.join(', ') || 'none') + (by.length ? ' ' + by.join('; ').substring(0, 200) : ''))
  }

  // run in slices so one server tick never holds the watchdog
  var jobs = []
  ;(plan.attrs || []).forEach(id => jobs.push(() => { out.attrs[id] = attrsOf(id) }))
  jobs.push(() => { out.melee['(none)'] = melee('minecraft:air') })
  jobs.push(() => { cur = '(none)'; out.armor['(none)'] = armor([]) })
  ;(plan.melee || []).forEach(id => jobs.push(() => { if (!known(id)) { err('unknown item', 'not in this game', id); return } safe('melee', () => { out.melee[id] = melee(id) }, id) }))
  ;(plan.sets || []).forEach(s => jobs.push(() => { cur = s.k; safe('armor', () => { out.armor[s.k] = armor(s.p) }, s.k) }))
  ;(plan.grows || []).forEach(id => jobs.push(() => { safe('grows', () => { out.grows[id] = grows(id) }, id) }))
  if ((plan.curios || []).length) jobs.push(() => { cur = '(none)'; safe('curio', () => { out.curios['(none)'] = curio(null) }, '(none)') })
  ;(plan.curios || []).forEach(id => jobs.push(() => { if (!known(id)) { err('unknown item', 'not in this game', id); return } cur = id; safe('curio', () => { out.curios[id] = curio(id) }, id) }))
  // jobs that return { wait, then } go on after that many server ticks (shots in flight)
  if (plan.probe) { out.probe = []; jobs.push(() => { reset(); return arrowProbe(true) }); jobs.push(() => arrowProbe(false)) }
  ;(plan.ranged || []).forEach(id => jobs.push(() => { if (!known(id)) { err('unknown item', 'not in this game', id); return null } var w = null; safe('ranged', () => { w = ranged(id) }, id); return w }))
  ;(plan.blocks || []).forEach(id => jobs.push(() => { if (!known(id)) { err('unknown item', 'not in this game', id); return null } cur = id; var w = null; safe('blocks', () => { w = blocks(id) }, id); return w }))
  var i = 0, next = 0
  say('starting: ' + jobs.length + ' measurements; the game slows down until it is done')
  grant()
  check()
  var pend = w => server.scheduleInTicks(w.wait, () => {
    var n = null; try { n = w.then() } catch (e) { err('job', e) }
    if (n && n.wait) pend(n); else server.scheduleInTicks(1, step)
  })
  var step = () => {
    var t0 = Date.now()
    while (i < jobs.length && Date.now() - t0 < 200) {
      var w = null; try { w = jobs[i]() } catch (e) { err('job', e) } i++
      if (w && w.wait) { pend(w); return }
    }
    if (i < jobs.length) { var pc = Math.floor(i * 100 / jobs.length); if (pc >= next) { say(pc + '% (' + i + '/' + jobs.length + ')'); next += 10 } server.scheduleInTicks(1, step); return }
    out.finished = '' + new Date()
    JsonIO.write('kubejs/' + base + '_measure.json', out)
    while (spawned.length) drop(spawned[spawned.length - 1])
    say('done: kubejs/' + base + '_measure.json (' + Object.keys(out.melee).length + ' weapons, ' + Object.keys(out.armor).length + ' sets, '
      + Object.keys(out.grows).length + ' re-measured, ' + Object.keys(out.curios).length + ' curios, ' + Object.keys(out.ranged).length + ' shooters, '
      + Object.keys(out.blocks).length + ' blockers, ' + Object.keys(out.errors).length + ' kinds of error)')
    if (plan.stop) server.runCommandSilent('stop')
  }
  step()
}
ServerEvents.loaded(event => { var p = JsonIO.read('kubejs/lgw_items.json'); if (p && p.auto) event.server.scheduleInTicks(200, () => LGW.run(event.server, null, 'lgw')) })
// lgw_measure_test reads kubejs/lgw_test_items.json (a handful of items, about a minute) and writes kubejs/lgw_test_measure.json
ServerEvents.customCommand('lgw_measure_test', event => {
  try { LGW.run(event.server, event.player, 'lgw_test') } catch (e) { console.error('lgw_measure failed: ' + LGW.why(e)); try { event.player.tell('lgw_measure failed: ' + e) } catch (x) {} }
})
// lgw_measure_extra reads kubejs/lgw_extra_items.json (the weapons to re-measure on several targets, and the curios) and writes
// kubejs/lgw_extra_measure.json; lgw_measure_extra_test reads kubejs/lgw_extra_test_items.json (2 weapons, 6 curios)
ServerEvents.customCommand('lgw_measure_extra', event => {
  try { LGW.run(event.server, event.player, 'lgw_extra') } catch (e) { console.error('lgw_measure failed: ' + LGW.why(e)); try { event.player.tell('lgw_measure failed: ' + e) } catch (x) {} }
})
ServerEvents.customCommand('lgw_measure_extra_test', event => {
  try { LGW.run(event.server, event.player, 'lgw_extra_test') } catch (e) { console.error('lgw_measure failed: ' + LGW.why(e)); try { event.player.tell('lgw_measure failed: ' + e) } catch (x) {} }
})
// lgw_measure_third reads kubejs/lgw_third_items.json (bows, crossbows and thrown weapons; the target-dependent weapons again
// with the pig turned; the curios that blocked a hit) and writes kubejs/lgw_third_measure.json; lgw_measure_third_test a handful
ServerEvents.customCommand('lgw_measure_third', event => {
  try { LGW.run(event.server, event.player, 'lgw_third') } catch (e) { console.error('lgw_measure failed: ' + LGW.why(e)); try { event.player.tell('lgw_measure failed: ' + e) } catch (x) {} }
})
ServerEvents.customCommand('lgw_measure_third_test', event => {
  try { LGW.run(event.server, event.player, 'lgw_third_test') } catch (e) { console.error('lgw_measure failed: ' + LGW.why(e)); try { event.player.tell('lgw_measure failed: ' + e) } catch (x) {} }
})
ServerEvents.customCommand('lgw_measure', event => {
  try { LGW.run(event.server, event.player, 'lgw') } catch (e) { console.error('lgw_measure failed: ' + LGW.why(e)); try { event.player.tell('lgw_measure failed: ' + e) } catch (x) {} }
})
