#!/usr/bin/env python3
"""Replace vague More Artifacts effect text with the numbers from the mod's CommonConfig defaults
(moreartifacts-1.5.5-1.20.1.jar, net/gobies/moreartifacts/config/CommonConfig.class, read with javap).
The pack may override these in config/moreartifacts-common.toml; check there when the pack files are at hand.
Run once: python3 build/patches/moreartifacts.py (edits build/src/data.js in place, idempotent)."""
import json, pathlib, re
P = pathlib.Path(__file__).resolve().parents[1] / "src" / "data.js"
FX = {
 "lucky_emerald_ring": "+1 Luck; hits have a 5% chance to drop an emerald; +25% damage to Illagers",
 "decay_stone": "Immune to Wither; 25% chance on hit to inflict Wither III for 3 s; +20% damage to withered targets; hitting a withered target heals 1 heart",
 "envenomed_quiver": "+15% arrow damage; arrows inflict Poison I and Wither I (5 s); 20% chance not to consume arrows",
 "gilded_scarf": "+10% damage dealt, 12% less damage taken; Piglins are neutral",
 "mechanical_claw": "+15% melee damage; 25% chance on hit to inflict Bleed (1 damage/s for 8 s)",
 "molten_quiver": "+15% arrow damage; arrows set targets on fire for 5 s; +5% damage to burning targets; 20% chance not to consume arrows",
 "magic_quiver": "+10% arrow damage; 20% chance not to consume arrows",
 "decay_amulet": "40% chance to inflict Wither I (5 s) on attackers",
 "golden_headgear": "+2 armor; 10% less arrow damage taken",
 "mechanical_gears": "5% chance to dodge attacks; +2% movement speed",
 "natures_mantle": "+10% movement speed; standing still during the day grants periodic Regeneration",
 "necroplasm_amulet": "50% chance on hit to heal 2 HP; 60% chance to inflict Poison I and Wither I (5 s) on attackers",
 "obsidian_skull": "Immune to burning; 50% less fire damage taken",
 "spectre_amulet": "40% chance on hit to heal 2 HP",
 "venom_amulet": "40% chance to inflict Poison I (5 s) on attackers",
 "wooden_headgear": "+1 armor; 5% less arrow damage taken",
 "hero_shield": "Resistance I; every 5th hit taken is ignored; 75% less explosion damage taken",
 "enderian_eye": "Press the key to teleport where you are looking (up to 25 blocks, 5 s cooldown)",
 "high_jumpers": "Jump higher, less fall damage; +10% movement speed",
 "leather_treads": "+5% movement speed",
 "sculk_treads": "+25% movement speed; your steps make no vibrations (Warden, Sculk Sensors)",
 "enderian_scarf": "8% less damage taken",
 "melody_plushie": "+20% max health and Regeneration I; sleeping with it on grants Health Boost II for 240 s",
 "shackle": "+1 armor",
 "dune_treads": "+5% movement speed, +10% more on sand",
 "fire_stone": "Immune to fire; 25% chance on hit to set the target ablaze for 3 s; +30% damage to burning targets; burning mobs ignite nearby mobs when they die",
 "netherite_headgear": "+3 armor; 15% less arrow damage taken",
 "blazing_treads": "+10% movement speed; hot blocks (magma) don't hurt you; immune to burning",
 "echo_glove": "+5% melee damage, +15% attack speed; 10% chance on hit to ignore the target's invulnerability frames",
 "ice_stone": "Immune to freezing; 25% chance on hit to freeze the target for 8 s; +10% damage to freezing targets",
 "mechanical_glove": "+2 melee damage",
 "venom_stone": "Immune to Poison; 25% chance on hit to inflict Poison II for 5 s (15% chance it becomes the deadlier Virulent); +20% damage to poisoned targets",
 "ender_dragon_claw": "5% chance on hit to deal +50% damage",
 "enderian_treads": "+20% movement speed; a fatal hit is avoided by void-stepping away (60 s cooldown)",
 "true_enderian_scarf": "10% less damage taken, 10% chance to evade attacks, +1 reach; Endermen are neutral",
 "ruby_ring": "+5% damage for every 20 max health, counted up to 60 max health per ring",
 "dragon_eye": "Night Vision (toggle); Endermen are friendly and fight for you, 1% chance to summon one when attacked (Fire/Ice/Lightning variants add the matching resistance)",
}
DROP = {"bezoar": "5%", "vitamins": "40%", "fast_clock": "2%", "desert_charm": "2%", "wither_shard": "25%",
        "shulker_heart": "15%", "enderian_scarf": "1%", "shackle": "1%", "ender_dragon_claw": "25%"}
s = P.read_text(encoding="utf-8")
assert s.startswith("const D=")
D, end = json.JSONDecoder().raw_decode(s, 8)
rest = s[end:]
n = 0
for d in D:
    if not d["id"].startswith("moreartifacts:"): continue
    k = d["id"].split(":")[1]
    if k in FX and d["fx"] != FX[k]: d["fx"] = FX[k]; n += 1
    if k in DROP:
        d["src"] = [re.sub(r"^Dropped by ([^.(]+)\.$", lambda m: f"Dropped by {m.group(1)} ({DROP[k]}).", x) for x in d["src"]]
    if k == "magic_quiver":
        d["src"] = [x.replace("Dropped by Skeleton, Pillager.", "Dropped by Skeleton (1%) and Pillager (4%).") for x in d["src"]]
P.write_text("const D=" + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + rest, encoding="utf-8")
print("updated", n)
