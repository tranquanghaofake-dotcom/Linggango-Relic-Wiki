# Pack audit (reads the modpack directly, no game run)
Work dir W holds `pack/src` (unzipped Linggango-V6.6.5b4.zip from CurseForge file 9071626) and `pack/mods` (the 476 jars, `python3 build/gear/dl.py W`).
1. `python3 build/gear/prep.py W` and `python3 build/gear/recipes.py W` → lang.json, ns2jar.json, gates.json, rec.json
2. `audit.py W REPO [n]` names / recipes / loot vs the wiki; `recheck.py W` recipes the pack's KubeJS removes or adds;
   `drops.py W` mob drop chances from the jars' loot tables; `tips.py W` lang tooltips for effects still without numbers.

## kubejs/: measuring gear in game
Scripts to copy into the pack's `kubejs/` folder (single player with cheats, or a server as op). Untested outside the game: check `logs/latest.log` (or `kubejs/logs/`) for `dump_gear_all` / `dmg_logger` warnings the first time.
- `server_scripts/dump_gear_all.js`: `/kubejs custom_command dump_gear_all` writes `kubejs/gear_dump_all.json`, the attribute modifiers of every item (the pack's own `dump_gear.js` only covers tiered tools and armor, so staves, bows, guns and summon weapons were missing). Same format: convert it into `build/patches/gear_runtime.json` like the v27 dump.
- `startup_scripts/dmg_logger.js` + `server_scripts/dmg_logger_commands.js` + `dmg_queue.json`: a damage logger. Every hit a player deals to a target dummy (MmmMmmMmmMmm, in the pack) is recorded at `LivingDamageEvent` (final damage) under the main-hand item, split into direct / projectile / minion / dot (no-attacker damage on a dummy the player hit in the last 10 s). Commands: `dmg_next` (give the next of the 71 queued Ranged / Mage / Summon weapons), `dmg_save` (write `kubejs/dmg_log.json`: hits, median, max, damage types, DPS over the attack window), `dmg_reset`, `dmg_any`. Restart the game after adding the startup script.
- `dmg_queue.json`: the weapons worth measuring, from the tier lists of v27: per Act and playstyle up to four weapons unlocked there, top of the estimated list, without Iron's staves and Ars books (they deal no damage of their own; their value is their attributes).
