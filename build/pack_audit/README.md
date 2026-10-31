# Pack audit (reads the modpack directly, no game run)
Work dir W holds `pack/src` (the unzipped CurseForge zip: 6.6.6hf is file 9304214) and `pack/mods` (the jars: `python3 build/gear/dl.py W`, or the
author's server pack `serverpack-slim-6.6.6hf.zip` (`mods/`, `config/`, `kubejs/`, and Forge's srg jar under `libraries/`): the reference for code,
data and configs; see build/README.md "Regenerating from the pack" for what was compared). For the wide gear scan, `srv/libraries/net/minecraft/server/1.20.1-20230612.114412/` needs Forge's
server-1.20.1-*-srg.jar: the Forge installer makes it, or remap Mojang's 1.20.1 server jar with Mojang's server.txt (class names) and
MCPConfig 1.20.1-20230612.114412 joined.tsrg (SRG member names).
1. `python3 build/gear/prep.py W` and `python3 build/gear/recipes.py W` → lang.json, ns2jar.json, gates.json, rec.json
2. `audit.py W REPO [n]` names / recipes / loot vs the wiki; `recheck.py W` recipes the pack's KubeJS removes or adds;
   `drops.py W` mob drop chances from the jars' loot tables; `tips.py W` lang tooltips for effects still without numbers.

## Shared pieces (use these instead of a new copy)
- `mcassets.py`: one reader for resource files the way the game stacks them (`Assets([kubejs dir, resource zips, mod jars,
  client jar])`, first source wins), models merged over their parents as vanilla does (textures, elements, display per
  context, gui_light, Forge render_type and loader; `forge:separate_transforms` shows its `gui` perspective), textures with
  the first frame an `.mcmeta` names, `icon(id, size, tint)` = the inventory picture, `png_b64(im)` = the smallest lossless
  PNG (indexed with an alpha table when it has 256 colours or fewer, checked pixel for pixel). `python3 -I mcassets.py
  --repack FILE... [--skip ns]` re-encodes the base64 PNGs already in a source the same way (2026-10-31: gear_icons.json
  4.74 → 3.39 MB, data.js 4.49 → 3.66 MB, every icon decoded to the same pixels; `--skip ae2` keeps AE2's CC BY-NC-SA
  icons byte for byte).
- `mcassets.NO_ART` / `pack_sources(W)` / `art_allowed(path)`: the one list of resource packs no picture may come from
  (build/README.md, licence rules) and the game's stack without them; `Assets` drops them whoever passes them.
- `tints.py`: the colours ItemColors multiplies into tinted layers, read from the jars (vanilla ItemColors/BlockColors
  run on a small interpreter; spawn eggs from `SpawnEggItem`/`ForgeSpawnEggItem` constructors, also through helpers;
  mod colour handlers run with a stand-in event); `Assets.tint_indices(id)` says which layers ask for one. Used by
  `gear/icons.py`, `name_icons.py <pack dir> [client jar]` and `uiicons.py ... [client jar]`.
- `block_render.py`: block-element models drawn exactly as the 1.20.1 GUI draws an item (display.gui transform, the GUI's
  two diffuse lights, BlockElement uv defaults, face and element rotation with rescale, z-buffer, cutout at 0.1). The
  constants were read from client-1.20.1.jar (GlStateManager.setupGui3DDiffuseLighting, Lighting, PoseStack,
  light.glsl). A full block shows top 100 %, east face left 65 %, north face right 40 %. Used by `mcassets.icon`,
  `name_icons.py` and `gear/icons.py` at 32 px (the slot at GUI scale 2, 1:1 next to x2 flat icons).
- `lootlib.py`: drop chances by vanilla 1.20.1 loot rules (rolls as distributions, weighted picks, conditions on
  composite entries, `alternatives` = first that passes, pools as a union, `set_count` ranges); `loot_chance.py`,
  `side_bosses/loot.py`, `drops.py` and `chests.py` use it. Luck, quality and bonus rolls are taken at luck 0.
- `render_page.js`: opens a three.js page (`geo_icon_render.html`, `armor_render.html`, `side_bosses/jrender.html`) in
  headless Chromium in place; the pages import `../geo2three.js` and `build/node_modules/three` (`npm install
  --no-package-lock --prefix build`), so nothing is copied as `r.html` / `armor.html` any more. `PW_CHROMIUM` picks
  another Chromium binary.

## kubejs/: measuring gear in game
Scripts to copy into the pack's `kubejs/` folder (single player with cheats, or a server as op). Untested outside the game: check `logs/latest.log` (or `kubejs/logs/`) for `dump_gear_all` / `dmg_logger` warnings the first time.
- `server_scripts/dump_gear_all.js`: `/kubejs custom_command dump_gear_all` writes `kubejs/gear_dump_all.json`, the attribute modifiers of every item (the pack's own `dump_gear.js` only covers tiered tools and armor, so staves, bows, guns and summon weapons were missing). Same format: convert it into `build/patches/gear_runtime.json` like the v27 dump.
- `startup_scripts/dmg_logger.js` + `server_scripts/dmg_logger_commands.js` + `dmg_queue.json`: a damage logger. Every hit a player deals to a target dummy (MmmMmmMmmMmm, in the pack) is recorded at `LivingDamageEvent` (final damage) under the main-hand item, split into direct / projectile / minion / dot (no-attacker damage on a dummy the player hit in the last 10 s). Commands: `dmg_next` (give the next of the 71 queued Ranged / Mage / Summon weapons), `dmg_save` (write `kubejs/dmg_log.json`: hits, median, max, damage types, DPS over the attack window), `dmg_reset`, `dmg_any`. Restart the game after adding the startup script.
- `dmg_queue.json`: the weapons worth measuring, from the tier lists of v27: per Act and playstyle up to four weapons unlocked there, top of the estimated list, without Iron's staves and Ars books (they deal no damage of their own; their value is their attributes).

## quests/: the quest book
`quests/boss_graph.py <chapters dir>` turns the Bosses chapter into `patches/boss_graph.json` (dependencies, dimension, and since 6.6.6 the
Keeper summon each Boss Soul goes into). The pack ships its quest files encrypted (LGQ1); the script reads them in plain SNBT.
`summons.py` also reads the 6.6.6 summon routes (`kubejs/data/linggango_integration/recipes/38_summon_routes`) and the Boss Soul slot.

## curio_recipes.py: recipe grids for curios that showed only an ingredient row
`python3 build/pack_audit/curio_recipes.py <dir of *.jar> <the pack's overrides/kubejs>` finds the recipe of each crafted curio
without a grid: Crafting Table (shaped, shapeless), Blood Magic's Hellfire Forge and Alchemy Array. Order as in game: what the KubeJS
server scripts add (`kubejs_recipes.js` runs them under node against a stand-in recipe event and prints adds and removes), then
`kubejs/data` recipes, then the mod jars; anything the scripts remove is skipped. Writes `patches/curio_recipes.json` (grids and
ingredient names) and icons for new ingredients into `patches/gear_icons.json`; `patches/curio_recipes.py` (first step of
`apply_all.sh`, so `boss_order` sees the new ingredients) puts them into `data.js`, marking each grid `grx`.
2026-10-28: 70 of 86 found (44 Crafting Table, 26 Blood Magic); 14 source lines name other or fewer ingredients than the pack's
recipe (usually tags, or the line was written from the mod's own recipe). The other 16 are upgrades, rituals and special mechanics.
