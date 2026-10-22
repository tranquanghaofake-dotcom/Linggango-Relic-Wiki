// Linggango wiki: commands for the damage logger (startup_scripts/dmg_logger.js). All need op:
//   /kubejs custom_command dmg_next    give the next weapon from kubejs/dmg_queue.json (and say which one it is)
//   /kubejs custom_command dmg_save    write kubejs/dmg_log.json: per item, hits by kind, median hit, damage per second
//   /kubejs custom_command dmg_reset   forget everything logged so far
//   /kubejs custom_command dmg_any     also count hits on any mob, not only target dummies (run again to switch back)
// How to measure one weapon: stand ~8 blocks from a target dummy, attack for about 10 s without pausing
// (bows fully drawn), then wait ~10 s so poison / burning finish. Then dmg_next for the next one, dmg_save at the end.
const lgwSay = (event, msg) => {
  console.info('[dmg] ' + msg)
  try { event.server.runCommandSilent('tellraw @a ' + JSON.stringify({ text: '[dmg] ' + msg, color: 'gold' })) } catch (err) { }
}

ServerEvents.customCommand('dmg_next', event => {
  let items
  try { const q = JsonIO.read('kubejs/dmg_queue.json'); items = q.items || q.get('items') } catch (err) { lgwSay(event, 'cannot read kubejs/dmg_queue.json: ' + err); return }
  global.lgwQ = (global.lgwQ === undefined ? -1 : global.lgwQ) + 1
  if (global.lgwQ >= items.length) { lgwSay(event, 'queue done (' + items.length + ' items): run dmg_save'); return }
  const it = items[global.lgwQ], id = '' + (it.id || it.get('id')), name = '' + (it.name || it.get('name'))
  event.server.runCommandSilent('give @p ' + id)
  lgwSay(event, (global.lgwQ + 1) + '/' + items.length + ': ' + name + ' (' + id + ')')
})

ServerEvents.customCommand('dmg_reset', event => {
  global.lgwDmg.items = {}; global.lgwDmg.last = {}; global.lgwQ = undefined
  lgwSay(event, 'log cleared, queue back to the start')
})

ServerEvents.customCommand('dmg_any', event => {
  global.lgwDmg.onlyDummy = !global.lgwDmg.onlyDummy
  lgwSay(event, global.lgwDmg.onlyDummy ? 'counting target dummies only' : 'counting hits on any mob')
})

// written with var / forEach / plain objects only: KubeJS 6's Rhino is unreliable with const in loops, for...of and Set
ServerEvents.customCommand('dmg_save', event => {
  var med = function (xs) { if (!xs.length) return 0; var s = xs.slice().sort(function (a, b) { return a - b }); return s[Math.floor(s.length / 2)] }
  var out = {}, n = 0, items = global.lgwDmg.items
  Object.keys(items).forEach(function (item) {
    var r = items[item], sum = {}, first = null, last = null, total = 0
    ;['direct', 'projectile', 'minion', 'dot'].forEach(function (kind) {
      var xs = r[kind]
      if (!xs.length) return
      var amt = xs.map(function (x) { return x[1] }), types = {}
      xs.forEach(function (x) { types[x[2] + (x[3] ? ' / ' + x[3] : '')] = 1 })
      var t = Math.round(amt.reduce(function (a, b) { return a + b }, 0) * 100) / 100
      sum[kind] = { hits: xs.length, total: t, median: med(amt), max: Math.max.apply(null, amt), types: Object.keys(types) }
      total += t
      if (kind !== 'dot') xs.forEach(function (x) { if (first === null || x[0] < first) first = x[0]; if (last === null || x[0] > last) last = x[0] })
    })
    // damage per second over the time you were attacking (+1 s so a single hit does not divide by zero), dot included
    var secs = first === null ? 0 : (last - first) / 20 + 1
    out[item] = { kinds: sum, seconds: secs, dps: secs ? Math.round(total / secs * 100) / 100 : 0, raw: r }
    n++
  })
  JsonIO.write('kubejs/dmg_log.json', { items: out })
  lgwSay(event, n + ' items saved to kubejs/dmg_log.json')
})
