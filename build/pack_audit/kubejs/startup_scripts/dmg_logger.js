// Linggango wiki: damage logger (startup script: Forge events can only be hooked here; restart the game after adding it).
// Records the FINAL damage of every hit a player deals to a target dummy (LivingDamageEvent: after armor, crits, mod multipliers),
// keyed by the item in the player's main hand. Hits are split by how they landed:
//   direct     the player hit the target (melee, a staff swing)
//   projectile arrow, bullet, spell projectile fired by the player
//   minion     a summon owned by the player (getOwner / getSummoner)
//   dot        damage with no attacker (poison, burning, wither...) on a target the player hit in the last 10 s
// The server script dmg_logger_commands.js saves, resets and steps through the queue.
const LGW_Player = Java.loadClass('net.minecraft.world.entity.player.Player')
const LGW_Reg = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')

global.lgwDmg = { onlyDummy: true, items: {}, last: {} }

const lgwKey = (reg, x) => { try { return '' + reg.getKey(x) } catch (err) { return '?' } }
const lgwOwner = a => {
  if (a === null) return null
  if (a instanceof LGW_Player) return a
  try { const o = a.getOwner(); if (o instanceof LGW_Player) return o } catch (err) { }
  try { const o = a.getSummoner(); if (o instanceof LGW_Player) return o } catch (err) { }
  return null
}

ForgeEvents.onEvent('net.minecraftforge.event.entity.living.LivingDamageEvent', e => {
  try {
    const D = global.lgwDmg, target = e.getEntity(), src = e.getSource()
    const ttype = lgwKey(LGW_Reg.ENTITY_TYPES, target.getType())
    if (D.onlyDummy && ttype.indexOf('dummy') < 0) return
    const tick = target.level().getGameTime(), tid = '' + target.getUUID()
    const attacker = src.getEntity(), direct = src.getDirectEntity()
    const player = lgwOwner(attacker)
    let item, kind
    if (player !== null) {
      item = lgwKey(LGW_Reg.ITEMS, player.getMainHandItem().getItem())
      kind = attacker === player ? (direct === null || direct === player ? 'direct' : 'projectile') : 'minion'
      D.last[tid] = { item: item, tick: tick }
    } else if (attacker === null && D.last[tid] && tick - D.last[tid].tick <= 200) {
      item = D.last[tid].item; kind = 'dot'
    } else return
    const rec = D.items[item] || (D.items[item] = { direct: [], projectile: [], minion: [], dot: [] })
    if (rec[kind].length < 400)
      rec[kind].push([tick, Math.round(e.getAmount() * 1000) / 1000, '' + src.getMsgId(), direct === null ? '' : lgwKey(LGW_Reg.ENTITY_TYPES, direct.getType())])
  } catch (err) {
    console.warn('dmg_logger: ' + err)
  }
})
