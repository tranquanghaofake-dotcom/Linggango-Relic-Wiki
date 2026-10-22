// Linggango wiki: dump the attribute modifiers of EVERY item, not only tiered tools and armor (the pack's dump_gear.js).
// Same output format as dump_gear.js, so build/patches/gear_runtime.json is made from it the same way.
// Staves, wands, bows, guns and summon weapons carry their spell power, cooldown, draw speed, summon damage... as modifiers:
// this is how the wiki gets them. Items whose modifiers are all empty are left out.
// Run in game (op): /kubejs custom_command dump_gear_all   ->  kubejs/gear_dump_all.json
ServerEvents.customCommand('dump_gear_all', event => {
  const ForgeRegistries = Java.loadClass('net.minecraftforge.registries.ForgeRegistries')
  const EquipmentSlot = Java.loadClass('net.minecraft.world.entity.EquipmentSlot')
  const slots = [EquipmentSlot.MAINHAND, EquipmentSlot.OFFHAND, EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET]
  const out = {}
  const errors = {}
  const note = err => { const key = '' + err; errors[key] = (errors[key] || 0) + 1 }

  const readSlot = (stack, slot) => {
    try { return stack.getAttributeModifiers(slot) } catch (err) { note('stack.getAttributeModifiers: ' + err) }
    try { return stack.getItem().getAttributeModifiers(slot, stack) } catch (err) { note('item.getAttributeModifiers: ' + err) }
    return null
  }

  let seen = 0
  ForgeRegistries.ITEMS.getValues().forEach(item => {
    seen++
    let id, stack
    try { id = '' + ForgeRegistries.ITEMS.getKey(item); stack = Item.of(id) } catch (err) { note('stack ' + err); return }
    const rec = { tags: [], slots: {} }
    slots.forEach(slot => {
      const mods = readSlot(stack, slot)
      if (mods === null || mods.isEmpty()) return
      const list = []
      mods.entries().forEach(e => {
        const key = ForgeRegistries.ATTRIBUTES.getKey(e.getKey())
        list.push({
          attribute: key === null ? '' + e.getKey().getDescriptionId() : '' + key,
          amount: e.getValue().getAmount(),
          op: '' + e.getValue().getOperation()
        })
      })
      if (list.length) rec.slots['' + slot.getName()] = list
    })
    if (Object.keys(rec.slots).length) out[id] = rec
  })

  JsonIO.write('kubejs/gear_dump_all.json', { items: out })
  console.info('dump_gear_all: ' + seen + ' items scanned, ' + Object.keys(out).length + ' with modifiers -> kubejs/gear_dump_all.json')
  for (const msg in errors) console.warn('dump_gear_all error x' + errors[msg] + ': ' + msg)
})
