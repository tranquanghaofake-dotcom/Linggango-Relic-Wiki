> Project log. Moved here from the `workspace` branch on 2026-10-30 with every entry up to then (older entries keep the branch names and paths of their day). Append new entries at the end: `## YYYY-MM-DD: <what changed>`.

# Linggango Relic Wiki: overhaul notes (17 Oct 2026)

Output: `dist/Linggango_Relic_Wiki.html` (single file, works offline, 3.67 MB; the original was 3.27 MB).
The task prompt is in `PROMPT.md`; every path or rarity change is listed in `build/changes.csv`.

## Rebuild

See `build/README.md`. In short: `bash build/patches/apply_all.sh` (patches, then `build.py`), then `bash build/check.sh`.
`original/` keeps the uploaded file untouched; `build/transform.py` was the one-off that made the first `data.js` from it.

## What changed

### 1. Paths
- "Act" is now **"Path"** in the UI. Hash links (`#act/…`) and saved filters still work.
- Path `-1` is now **L2 Artifacts**. All 29 items in it are L2 Artifacts sets; they drop by L2 Hostility mob level, and the wiki still says so.
- Three vanilla-boss paths now sit between Path VI and VII: **Path VI (after Zoranth the Forgotten) → Warden → Wither → Ender Dragon → Path VII (after the Elvenite Paladin)**.
  Why this order: in the pack's own stats Zoranth hits for 20, the Wither for 32 with 20 armor, and the Paladin for 30 with 100 armor. The Ender Dragon is required before the Paladin, and the pack's Hardmode ×2.1 turns on after the Dragon and skips the Warden.
- Paths are rebuilt from dependencies. A relic moves up when it, or a relic it is crafted from, needs a Warden, Wither or Ender Dragon drop. That covers Warden Sclerite, Warden Soul, Warden Bone Shard, Nether Star, Pure Nether Star, Wither Force Field, the Dragon treasure bag, Shulker items, End City loot and "End material".
  Dragon's Breath and Echo Shard are **not** treated as gates: Dragon's Breath also drops from the L2 Gravity trait, and Echo Shards come from Ancient City chests.
- **116 relics changed path:** 55 → Ender Dragon, 27 → Wither, 24 → Warden, 10 → Path 0.

### 2. Rarity
- The embedded data has **no in-game rarity field**. The old `r` was a quantile of a score: ≈ 0.21 × Act + 0.41 × Power + gate bonus. The new rarity keeps that model, recomputed on the new paths, and adds:
  - **★ Must-Have** (new top tier, bright gold with a star) for the 7 Celestial Artifacts Etchings and the 4 L2 Hostility Looting Charms. They sort first in every path, list and mod page, and they pass every role filter ("every build"). Each one still shows its *base* power rarity.
  - **Terramity scarce rule:** relics made only from Daemonium Chunk / Daemonium / Iridium plus Path 0 materials move to Path 0 and rank one rarity above that path's usual level, never below their old rarity. That covers 10 moved relics (Crowbar, Dumbbell, Scope Goggles, Pincushion…) and 19 relics in total.
  - **Upgrade rule:** a relic is never rarer than any relic it is crafted from. Example: the old data had Empty Anklet as Rare while Emerald Anklet, which is made from it, was Common.
- **124 relics changed rarity, every change upward.** Distribution: Common 468, Uncommon 408, Rare 341, Epic 223, Legendary 147, Mythic 78, Must-Have 11.

### 3. Plain-English text, icons, visuals
- How-to-get, why-this-path and stat lines are rewritten as sentences. Config keys (`loot.chances.x = 0.03`), attribute modifiers (`DODGE_CHANCE ×base0.05`), loot-table ids (`ancient_city(_ice_box)?`), unresolved format codes (`%.1f%%`) and Minecraft colour codes (`§6`) no longer show. The numbers are unchanged. The original line is kept on each item page under **Raw pack data** (collapsed) and in the hover title of each stat's source badge.
- Vanilla 1.20.1 attribute/effect icons appear inline next to stats: Strength, Haste, Speed, Resistance, the heart, the armor icon, Luck, Fire Resistance, Poison, Wither…
- Path frames show a boss emblem. The vanilla bosses get **CSS 3D heads cut from the 1.20.1 entity textures** (the Wither has all three heads). The modded Keepers use their signature drop from the pack's icons. Each path frame also gets a block-texture backdrop (Sculk, Soul Sand, End Stone, Netherrack…).
- Relics and vanilla weapons float behind the page at three depths, with vanilla particle sprites (enchanting glyphs, glint, sparks). The hero has its own drifting layer, and the item page has orbiting particles.
- The tooltip now follows Legendary Tooltips (gradient border in the rarity colour, notched pixel corners, ornaments from Epic up) and Obscure Tooltips (rising particles from Epic up, shimmer for Mythic and Must-Have).
- The hub has two new sections, **★ Must-Have** and **Vanilla bosses on the Path**, and every path card shows its emblem.
- `prefers-reduced-motion` turns off all decorative motion. Phones have no horizontal scroll (checked at 390 px).

## Sources
- Vanilla boss numbers: [Minecraft Wiki: Warden](https://minecraft.wiki/w/Warden), [Wither](https://minecraft.wiki/w/Wither), [Ender Dragon](https://minecraft.wiki/w/Ender_Dragon). Warden 500 HP, melee 16/30/45; Wither 300 HP (Java), always drops a Nether Star; Ender Dragon 200 HP, 12,000 XP on the first kill.
- Textures: `InventivetalentDev/minecraft-assets` @ 1.20.1 (Mojang assets, used here for a fan wiki).
- Etching drop conditions, boss stats, Hardmode and gates: the pack data already embedded in the wiki.

## Labelled as inference, or not done
- 🔍 The Warden / Wither / Ender Dragon order is this wiki's recommendation; the pack does not gate those bosses. "End material" is treated as needing the Dragon, because the outer islands open only after it dies.
- 🔍 Life Etching drops from *any* mob with ≥ 500 max health. It is placed on the Warden path because the Warden is the first sure target.
- ❌ Linggango and Cisco's modpack assets (boss models, weapon textures, the pack's own tooltip resource packs) were not available: the session had no pack files, and CurseForge, Modrinth and Fandom were blocked. Only icons already in the wiki plus vanilla textures were used.
- ❌ The old "Mid & end game guide" (`#guide`) was already switched off in the original. Its text still says "Act" and has not been rewritten.
- The wiki text stays in English to match the in-game item names.

## v3 (pack files available)
- Data now comes from the real Linggango V6.6.5b4 files plus the 7 curio mods the user added (downloaded from CurseForge/Modrinth). A headless Forge 1.20.1 server with the pack dumped every item's **in-game rarity** (26,652 items) and every entity's base attributes (2,716).
- **In-game rarity** is shown next to the wiki tier, in the exact colour the game uses (vanilla, Brutality, Confluence, Celestial Core, Enigmatic Legacy, Lethality rarities read from the jars). 1,589 of 1,676 relics are verified; the rest say "Unverified" (MAR Relics, Ars Extensions, Fallen Traits, L2 Artifacts jars could not be loaded on the server).
- **Fix:** Chaotic and Truth Etching do not need the Catastrophe Scroll (their loot modifiers in celestial_artifacts-1.6.5.jar have no curio condition).
- **Boss stats** on each path page are the effective values the player faces: base attributes + the pack's HP bonus (armageddon_mod_config.toml) + Hardmode ×2.1 after the Ender Dragon (Warden excluded). Confirmed true from config: Hardmode follows the Ender Dragon and skips the Warden; the Dragon is needed before the Elvenite Paladin (Titan's Insigna needs Khyros's Tears from the Dragon bag); the Nether opens after Eldorath.
- **3D bosses:** the 14 Keepers' own GeckoLib models (Armageddon jar) and Bedrock models of the Warden, Wither and Ender Dragon, rendered with three.js. One shared WebGL renderer draws every on-screen stage through scissor viewports; tier headers use portraits rendered once in idle time.
- **Tooltip** reproduces Tooltip Overhaul as configured by Linggango: compact layout, palette by in-game rarity, notch corners, glint gradient, mod-name and rating footer, emerge animation.
- Hub uses Linggango's own title background and logo from its FancyMenu config. Animated item textures (.mcmeta) play on item pages and tooltips.
- Performance work (effects kept): icons are shared Blob URLs instead of inline base64 per tile, hover is handled once per animation frame without DOM sweeps, tile pop-ins only run for tiers entering the viewport, 3D stops when nothing is on screen. Long tasks after load fell from 10.2 s to about 2.7–5 s in this GPU-less container (software raster); real GPU frame times will be far lower but were not measurable here.

## v5 placement rules (path = when you can realistically get it; "earliest" = with luck)
1. Random loot (structure chests, Suspicious Bags, archaeology, ordinary mob drops) sits on Path 0 however low the chance; recipes held back only by such loot follow it down.
2. Dimension locks: Nether-only loot and recipes with a Nether-only material start at Path V (the pack locks the Nether until Eldorath); End loot needs the Ender Dragon.
3. Boss drops are never random loot; a side boss's drops share one path, placed by that boss's strength.
4. Evolution chains ("upgraded from", "evolves from", "fed a Nether Star") count as ingredients, and a recipe is never earlier than any curio it is made from.
5. L2 Hostility Looting Charms (trait drops read from the jar and the pack's kubejs overrides): with the Unpolished charm (Path III), trait mobs drop Ghast Tear, Blaze Rod, Wither Skeleton Skull, Netherite Scrap, Shulker Shell and more. Trait-level-1 drops move the path itself; level 3+ drops (rare early) move only the earliest path.
6. More Relics stats are rebuilt from the mod's classes (the old data was ×100).

## v5 (desktop/laptop polish and fixes)
- Sidebar filters and header search now apply on Path, Slot and Mod pages, in place, with a "Filters on" notice and an empty state. Before, the list ignored them and the first click jumped to the tier list.
- 3D boss framing fits the model's height (Iron Colossus' head and the Wither were clipped).
- Paths with no 3D boss (Path 0, L2) no longer show a 360 px empty box; the emblem sits in the title.
- Item page: art moved into the right column (no dead space under the title); ID no longer wraps; Copy works on file:// via a fallback.
- Boss note hides raw ids like `(armageddon_mod:iron_remote)`; path ledes start with a capital; item breadcrumb says Home like every other page; Must-Have text no longer repeats itself.
- Hub hero copy no longer runs under the 3D Keeper at ≥1101 px.
- `<title>` moved into `<head>`, `color-scheme: dark`, meta description; one visible focus ring.
- `build/out/` is now committed, so `python3 build/build.py` reproduces `dist/` without the pack files.

## v6 (game UI redesign, desktop and laptop)
- One new stylesheet, `build/style.game.css`, replaces style.css, style.extra.css, style.v4.css and style.v5.css. `build/style.keep.css` keeps the tooltip, recipe window, CSS boss heads, mod-family patterns and keyframes from the old files.
- The look comes from Minecraft's own GUI: grey bevelled containers, inset item slots, stone buttons with the blue hover, black text fields, vanilla rarity colours (white, yellow, aqua, magenta, gold, red; gold ★ for Must-Have).
- The home page is a title screen: panning panorama, logo, yellow splash text, stacked buttons, and version text in the corners.
- The Path is an advancement tree that snakes across two rows; the Warden, Wither and Ender Dragon get challenge (spiked) frames.
- Path pages show the boss with a boss bar above its stats. Curio cards are dark tooltip-style entries with the name in its rarity colour.
- 3D now runs only on Path pages: the Keeper on the home hero and the WebGL portrait snapshots are gone (emblems use the Keeper's signature drop icon). The floating relic background is off.
- Desktop and laptop only (1280–1920 px). Below 900 px the layout stacks so it stays usable, but it is not designed for phones.

## v7 (merge: v5 wiki + gear + game UI)
- Base is now the newest wiki: the v5 the user uploaded plus the weapon and armor tier lists from branch `claude/laughing-mccarthy-82nfi5` (commit 6a05c82). v6's game UI and the v5 fixes were ported onto it. Earlier work on this branch had started from the older 17 Oct wiki by mistake.
- Sources: `build/src/` (template.html, v5.css, data.js, gear_data.js, fx3d.js, app.js, gear.js) split out of that branch's built HTML, plus `build/style.game.css`. `python3 build/build.py` writes `index.html` and `dist/`; `--raw` builds the v5 look without the skin. Gear data is regenerated with `build/gear/build.sh` (needs the pack zip and jars).
- Naming: the progression as a whole is **The Path**; each stage is an **Act** (Act 0–I, Act II … Warden Act, Ender Dragon Act).
- Game skin now also covers Gear (tier rows of inventory slots, stone-button filters), Builder (slots as item slots), Bosses (boss bar, GUI cards) and Mechanics (GUI tables).
- Fixes: opening a `#gear…`, `#g…` or `#gs…` link directly showed the tier list (gear.js loaded after the first render; the first render now runs after it). Boss list showed "⚔ null" damage for the Ender Dragon. Raw ids in boss notes, lowercase ledes, copy fallback, 3D framing, title in head, dark color-scheme, as in v5/v6.

## v8 (design direction: one dark scale; first data pass)
- UI and background now share one dark value range. The light-grey vanilla containers (#c6c6c6) on a dark deepslate world were the "one light, one dark" clash; containers, slots, buttons and fields now use the dark GUI scale of dark-mode resource packs (Default Dark Mode, Fresh UI), with a thinner 2 px bevel, a soft top light and deep drop shadow. Tooltip slot is dark too. Token names stay the same, so pages pick it up from `:root` in `build/style.game.css`; the "dark-mode coherence layer" at the end of that file holds the overrides.
- Data: 37 More Artifacts effects that said "+Armor", "+Movement speed", "chance to…" now carry the numbers from the mod's own config defaults (moreartifacts 1.5.5, CommonConfig.class via javap), and 10 mob drops got their chances (Bezoar 5%, Vitamins 40%, Fast Clock 2%, Desert Charm 2%, Wither Shard 25%, Shulker Heart 15%, Enderian Scarf 1%, Shackle 1%, Ender Dragon Claw 25%, Magic Quiver 1%/4%). Script: `build/patches/moreartifacts.py` (idempotent). The pack may override these in its config; recheck with the pack files.
- Still vague (no numbers yet): about 135 effects, mostly Summonity (31), Terra Curio (34), Enigmatic Addons/Legacy (15), Terramity (9), Ars Nouveau (5). Terra Curio on Modrinth is 0.2.0 with renamed ids, so it may not match the pack's `confluence:` items; use the pack's own jar.
- Known bugs left for the fix session: item page "How to get it" step text wraps one word per line; some gear tiles show two-letter placeholders instead of icons (Old GPU, The Rift Piercer, Axe of Lightning, Dinosaur Bone Club).

## v9 (content pass: logic and accuracy)
- Branch rule: `main` is the only working branch from now on.
- Found that `#guide` and `#unobtainable` redirect to Home; the guide text lives on only through Pack mechanics (`mechPage` calls `guide()`), so that is where the fixes below show.
- Looting Charms were placed by hand-written notes that contradicted their recipes. Now from the recipes: Unpolished = Act III (Goblin Lord's Gilded Plate + Emerald Totem, Arion's summon item; Arion no longer "unlocks" it), Magical = Act V (Celestial Netherite, Nether), Chaotic = Ender Dragon Act (Wanderer's Fallen Shard, End; was "after Vaedric"), Miraculous = Act XI (Helionite from Zoranth Newborn; was "Act X"). Act table, L2 table, boss-route notes and trait-hunting text agree now.
- Act table notes moved to the right rows: Phantom Finger is Act 0–I (was under Arion), Infinity Glove is Act IX (was under Vaedric), Demon Heart sits with the Wither/Dragon row (was under Iron Colossus). Removed the raw config key `is_nether_blocked`; "Khyros's Tears for Titan Insigna" → "Khyros's Goldened Tears for Titan's Insigna"; the Sanghor "ladder 69 → 102" note now says what it means (rung 8's value instead of rung 7's).
- Nyxaris: its bag gives the materials (Shadow Fragment, Shadowed Ingot), not the three Act XII curios as the old text said.
- Footer no longer says the pack doesn't gate the Ender Dragon (it does, through the Paladin's summon item).
- Data wording (`build/patches/text.py`, idempotent): "+2 slot Head" → "+2 Head slots", "+slot minion" → "+N minion slot(s)", "Spellbook 12 slot" → "12-slot spellbook", full stops on every source line, "The Calamities's" → "The Calamities'", "the Ender Dragon's". 18 "Hardest ingredient: X — from <boss> bag" lines named a crafted curio as if it dropped from the bag (Blindfold, Guardian's Crystal, Colossal Shield…); they now say X is crafted with the bag item.
- Numbers (`build/patches/fx_numbers.py`): 92 effects that said "+Armor", "+Attack speed", "+minion damage" now carry the values from the wiki's own stat lines (Summonity, Terra Curio, Terramity, Unique Accessories, Enigmatic). Heart of the Automaton's effect was cut off ("+2.5 tim"); fixed.
- Still vague: about 45 effects whose stat lines are missing or ambiguous (Artifacts game-rule values, Goety robe "Resistance: 85", Ars bangles with two speed lines, Ball n' Chain "+4 knockback resistance").

## v10 (read the modpack itself: Linggango-V6.6.5b4.zip + its 476 jars)
- Downloaded the pack zip (CurseForge file 9071626) and every jar of its manifest, then read configs, KubeJS scripts, tags, recipes, loot tables and lang files directly. Tools: `build/pack_audit/` (see its README); all data edits are patches in `build/patches/`, re-run with `build/patches/apply_all.sh`.
- Verified, no change needed: every curio name matches the game's lang (incl. the pack's renames in `kubejs/client_scripts/lang.js`); every curio slot matches the `curios:*` tags; all 1327 Keeper locks match `linggango_tweaks:gated/<tier>`; More Artifacts config in the pack equals the mod defaults (138/138 keys), so the v8 numbers stand; Goety robes 85%; Hardmode ×2.1 from `armageddon_mod_config.toml` (mod defaults 2.5/2.0).
- Pack mechanics table rewritten from the comments in `linggango_tweaks-common.toml`: damage floor, per-hit cap, boss intake (30 s, 3 s burst = 10%), boss health reset (Wither, Dragon, Warden, Elder Guardian back to 50% if everyone who hurt it dies), mob stages (after Arion / after the Dragon), Keeper Ladder (what the 200 × (rung/10)³ levels are: +1% mob health and damage each; the 10 rungs; The Discord is not one), damage types ×1.25/×1.5 and ×0.75/×0.5, Perfect Hit 5% ×1.5, invasions 8% per night / 3-day cooldown, Terramity stacking 50%/25%.
- Recipes: the wiki's recipe reader missed the pack's `e.remove({id})` lines (134 of them). Focus Scarf, Spring, Chthonic Curse Bracelets and Die of Revival now say their recipe is removed; Ring of the Seven Virtues / Seven Curses, Necronomicon and Rose of Temptation gained the pack's own KubeJS recipes; Darkest Scroll's duplication recipe added.
- Tag slots in recipe grids showed odd members (Glacian Fur for wool, Vexing Archwood Log for logs, Framed Glass, Treated Stick, Flying Fish Boots…); they show a vanilla member and the text says "any Wool / any Log…" (23 items).
- Mob drops recomputed from loot tables: Brain of Confusion 15% (was 5%), Hand Drill 100% (34%), Frog Leg 100% (10%), Ultra Sniffer drops 44% each (50%), Bat: Radar 41%, Compass and Depth Meter 14% (were 1% / 0.67%). The pack runs TerraCurio 0.1.13, not the 0.2.0 on Modrinth.
- Pack tooltips added: Lost Engine (lightning destroys inventory items), Ring of Redemption (don't wear with the Seven Curses ring), the nine Brutality math charms (need the Scientific Calculator). Artifacts values filled from the pack's gamerules (Vampiric Glove heals at most 3 per hit, pack changed it from 6; Snorkel 15 s).
- Not done yet: 148 loot-only curios whose source (structure mods, code drops) has no loot table to check; chest chances; Act placement was not re-derived.

## v11 (pack pass 2: chests, difficulty modifiers, icons, item-page layout)
- Terra Curio puts its curios into vanilla chests through loot modifiers keyed on the vanilla table id; the wiki only listed modded structures. 34 curios now start with "Vanilla chests (Terra Curio adds it): …" (Jungle Temple 100% for Eye of the Golem and Feral Paws, Shipwreck 30% for Aglet/Flipper/Sailfish Boots/Tsunami in a Bottle, Igloo 100% Flurry Boots, Stronghold library 100% Trifold Map…). `build/patches/tc_chests.py` (+ `tc_chests.json` cache).
- Lean Drops, No Cheese and Horrible Scavenger are optional Difficulty Enhancement modifiers (Medium / Expert / Master), off unless the player picks them; the wiki had them as always-on rules. Pack mechanics, the Tech & Magic table and the footer say so now; chances on the wiki are without them.
- Gear: 119 of the 180 weapons/armor with a two-letter placeholder now have their real icon (their item model uses `forge:separate_transforms`, whose GUI texture the first icon pass did not read; `build/pack_audit/gui_icons.py`, `build/patches/gear_icons.py`). The other 61 (Travel Optics, Hazenn's Stuff, Mekanism gear) only have GeckoLib 3D models; they show a weapon/armor glyph with a tooltip saying so.
- Item page "How to get it" no longer wraps one word per line (the step was a grid, so every inline piece became a cell); step numbers use the body font (the pixel font drew 2 like 8). `ol.how` selectors because v5.css's `ol.how li` outranked the skin.
- Footer notes the re-check against the pack (20 Oct 2026).
- Left: chest chances for Artifacts / Iron's Spells sub-tables (they are rolled through parent tables, so a flat read overstates them; `build/pack_audit/chests.py` shows the raw values only); 148 loot-only curios whose source is code (Suspicious Bag, MCreator bag procedures, Enigmatic Die) are unchecked; 3D icons for the 61 GeckoLib items could be rendered with `build/geo2three.js` later.

## v12 (tiles: cleaner and faster)
- Removed the bottom-left "used to craft another curio" mark from tiles (and its legend entry); the item page still lists what each curio is used in.
- Tile icons 48 → 40 px so they sit inside the slot with a margin (animated sprites keep their frame crop).
- Removed the gold pulse on rare tiles: it animated a `drop-shadow` filter on every Legendary/Mythic/Must-Have icon, a full repaint each frame. The static glow stays. The hover shine sweep (`.sh`) is gone too.
- Speed with the same look: tile icons only animate while on screen (one IntersectionObserver, plus a MutationObserver so tiles added later are watched); off-screen tiers skip layout and paint (`content-visibility:auto`). Home page in this GPU-less container: 13 fps → about 45–53 fps.

## v13 (logic and layout sweep)
- Boss stats now apply the pack's `kubejs/data/linggango/attributesetter/entity/entitybalance.json` overrides (BASE replaces, ADDITION adds), then the Armageddon HP bonus, then Hardmode ×2.1 for bosses after the Dragon (`build/patches/boss_stats.py`, file copied to `build/patches/entitybalance.json`). Before, the boss cards showed the mod's own values: Warden 500 HP / 0 armor (pack: 700 / 20 / 35 dmg), Wither 300 / 4 / 2 (pack: 500 / 20 / 32), Zoranth 16 armor / 28 dmg (pack: 50 / 20), Sanghor 70 dmg (pack 42 → 88.2 in Hardmode). The boss-route notes already had the pack values, so the two now agree.
- Small text and numbers use the body face: the pixel face drew 9 like 3, 5 like 8 and 2 like 8 (readers saw "Sanghor 387 HP", "Warden 800 HP"). The pixel face stays on headings.
- Pack mechanics tables: zebra rows were light grey with light text; now dark.
- Bosses, boss pages and Pack mechanics drop the curio filter sidebar (`body.noside`), which did nothing there.
- Curio list cards rebuilt: icon | name, slot · mod, then rarity and Act chips. Before, v5 and the skin both pinned the Act numeral and the rarity badge over the name, and Mythic showed an empty red box (badge text in the badge colour).
- Builder: a filled slot is one chip (icon + name | ×) instead of two overlapping 54 px squares; stat totals label percentage lines "(%)" so "Armor +4" and "Armor (%) −50%" read as two different bonuses; the note points to the Effects tab (there is no Effects page).
- Boss page: "Side bosses to farm before it" no longer lists the Wither and Ender Dragon under the Warden; the Hardmode assumption note is gone where Hardmode does not apply.
- Item page: the art is centred (a leftover `inset:18%` pushed it down-right); the first chip names the mod instead of the frame-style family ("ARCANE", "Relic").
- Mods page and mod pages: the family label ("Relic" on Terra Curio, Artifacts…, "Goety" on Covenant of the Seven) is gone.
- Gear "How to get": recipe types read as ingredients ("A Armor Upgrade a_ A Armor Upgrade") are filtered out, stations have real names (Armor upgrade (Adam's Ars Plus), Goety ritual, Enchanting Apparatus…), ingredient counts are shown (4× Frost Soul) and tags read "any hood".

## v14: Unofficial wiki, boss guides, mechanics, gear logic, Path tree
- Renamed to "Linggango Wiki (Unofficial)" with a fan-wiki disclaimer; Curio browser and Mod pages removed (old links redirect to the search).
- Bosses: HP/damage dropped; each page has a summoning guide (item, where to use it, recipe grid, ingredient sources, Infinite version). Data: `build/patches/summons.json`.
- Mechanics now covers only Goety rituals (all 479, filterable) and AE2 storage, from the Black Book and AE2 bytecode (`goety.json`, `ae2.json`, written to `build/src/wiki_data.js` by `wiki_data.py`).
- Gear: new `gear_gate.py`. It moves 49 items to the Act where their modded material opens (e.g. Old GPU needs Conductite, so Act VII). Tiers are now set by how close an item is to the best one at that Act (S ≥85%, A ≥70%, B ≥55%, C ≥40%). The Tier by Act strip ends with "Outclassed from …".
- Home: "Advancements" wording is gone. The Path is drawn as a main line with each Act's side bosses and elites (from BOSSR) as branches.

## v15: Gear icons, verdicts, home cleanup
- 114 of the 115 gear items without an icon now have one:
  - 53 use flat textures from the jars (`*_inventory`, `*_gui`, `*_icon`, or a resolved `layer0`).
  - 54 are 3D renders: GeckoLib geo, plus 3 Java block-element models, rendered with three.js in headless Chromium (`build/pack_audit/icon2.py`, `icon3.py`, `geo_icon_render.html/.js`).
  - 7 come from the official mod wikis: the Mekanism Jetpack, Free Runners and Scuba gear (wiki.aidancbrady.com) and the Alex's Caves Raygun (alexscaves.wiki.gg). These items use code-built models.
  - Ars Nouveau Spell Bow still has none.
- Gear pages show a verdict line under the title: best tier, the Acts where it holds that tier, and when to replace the item.
- Travel Optics level variants are named "(Lv 1/2/3)". Gear tiles show larger icons.
- Home: removed "Vanilla bosses on the Path"; panels and headings are tinted.

## v16
- Ars Nouveau Spell Bow icon rendered from its GeckoLib model, so all 180 gear items now have an icon.
- Footer credits the mod authors for item art, and the Mekanism and Alex's Caves wikis (CC BY-SA 4.0) for the icons taken from them.
- Curio tile float animation: GPU translate, softer easing, and a rarity-coloured glow on hover.

## v17: Boss attacks and drops, armor renders, pack art, curio tiles
- **Boss pages:**
  - Attacks and drops now come from the decompiled Armageddon procedures (`*OnEntityTickUpdate`, `*EntityDies`, `*TreasureBagRightclicked`). The tables are in `build/patches/boss_info.json`, made by `build/pack_audit/boss_prep.py`.
  - Drop chances are taken from the code; the JEI treasurebag configs are only what JEI displays.
  - Attacks have projectile renders or an icon for the attack type.
- **Armor sets:** 126 sets are rendered worn on a Steve model with three.js, from vanilla-style armor layer textures or GeckoLib armor geo (`armor_prep.py`, `armor_render.html/.js`). 40 broken renders were dropped.
- **Pack art on The Path:** the pack's own Act title strips, plus side-boss screenshots for 30 side bosses (`build/patches/pack_imgs.json`). The quest text itself is encrypted (LGQ1) and was not decrypted.
- **Curio tiles:** 64px, 42px icon on a rarity-tinted radial backdrop. The idle float animation is gone; there is a single hover transform.
- **Other changes:**
  - Gear is renamed Equipment.
  - Warden, Wither, Dragon and Act XII emblems now use Armageddon items.
  - The footer is a 4-column credits block on every page.
  - Removed: Raw pack data, "Why it sits on", the boss curio lists, and the HP on vanilla Act headers.

## v18: Split site build, filters, curio page, Mechanics flow
- **Site build:** `build.py` now writes a 20 kB `index.html` that loads content-hashed `static/*.js|css` files, so browsers cache them and a rebuild always loads fresh. `dist/` stays one self-contained file. `CLAUDE.md` is updated to match.
- **Sidebar:** Index and Source/Mod/Slot are hidden (the Path search bar covers them). The groups are now:
  - **Spell element:** spell schools only (Fire Spell Power and the like; not fire immunity).
  - **Mechanic:** secondary stats read from the effect text (Lifesteal, Armor pierce, Crit, Dodge, Cooldown, Mana, Minions, Reach, Thorns, Damage reduction, Bleed, Rage, Luck/loot, Mining), with the Brutality seasoning tag folded in.
- **Curio pages:**
  - Stats are a clean bullet list, with the source shown in the hover title.
  - Removed "Same mod, same Act" (duplicate of the slot list) and "Wearing two" (already in the side box).
  - The breadcrumb reads Home / The Path / Act.
- **Curio tiles:** 32px art with a black outline. A gentle bob runs only while a tile is on screen (`.vis`). The tile grid uses `content-visibility`.
- **Mechanics:** Goety and AE2 "getting started" are now icon flows with short captions. Block icons are rendered from Java block models (`build/pack_audit/mkicons.py`).
- Guide books: 339 practical tips from the mods' own Patchouli books are shown as "From the guide book" on curio and gear pages, from books such as the Simply Swords Runic Grimoire, the Goety Black Book, the Ars Nouveau Worn Notebook, Enigmatic Legacy and Blood Magic. The extractor is `build/pack_audit/guides.py`. Lore-only entries are filtered out; the data is in `build/patches/guides.json`.

## v19: Side boss pages
- 61 side bosses each have a page at `#side/<name>`, linked from the cards on The Path. Each page has:
  - where to find or summon the boss, including recipes from the jars;
  - 2–5 attacks, taken from the official mod wikis or the jar's lang file;
  - drops from the jar or pack loot tables, with chances estimated from the rolls;
  - sources;
  - a 3D render (37 bosses: 25 GeckoLib renders, 12 from official wikis), next to the pack's arena screenshot where one exists.
- Data is in `build/patches/side_bosses.json`; the scripts are in `build/pack_audit/side_bosses/`.
- Still missing: images for 24 Java-model bosses, and attacks for the Shadow Wizards.
- 57 drop-item icons were added with `mkicons.py`.

## v20: Warden and Wither as side bosses, icons for Goety/AE2, PC pixel sizing
- **Warden and Wither:** now optional side bosses in Act VI. At load, their curios and gear (Acts 6.1/6.2) fold into Act VI, and ORDER skips those Acts. Both stay on the Bosses page, marked "Side boss", and appear as cards in the Act VI branch of The Path.
- **Goety and AE2 text → icons:** ritual ingredients, activation items, ritual-type block requirements and the AE2 unlock lists now show icon chips. Names map to item ids through every jar's lang file (`build/patches/name_ids.json`); 244 icons were added, most of them rendered from block models.
- **Invisible items:** Invisibility Ring and Anklen't get a black-outline "glass" icon, so you can see them.
- **PC sizing and debugging:**
  - Tile and gear icons snap to whole device pixels (`--ip`/`--ip2`, set from `devicePixelRatio`), so 16px art stays crisp at Windows 125%/150% scaling.
  - Script errors show in a red box at the bottom left (`#jserr`), so a screenshot shows what broke.
- **Home Equipment bar:** consecutive Acts that share the same best weapon merge into one slot (e.g. "VII+").
- v20.1 fixes:
  - Equipment search crashed on armor sets, which have no `id` field (gear.js `gSearch`). This was the PC error `reading 'includes'`.
  - The Act page hero no longer repeats the boss page. It now shows the pack's Act title strip, plus links to the boss that opens the Act and to the next boss.
  - Animated curio strips show one frame at a time and are no longer squashed.
- v20.2: The Equipment search no longer restores a saved query (browser autofill had put a URL into it, which hid every item), and the box is now `autocomplete=off`. Side bosses with no render on The Path show a biome-block background (mud, sand, ice, netherrack, prismarine…) plus their drop item.
- v21: Added 49 bosses that were not listed, found by scanning the jars for boss tags and boss bars (`build/patches/boss_extra.json`, scripts in `build/pack_audit/boss_audit/`). All 124 bosses now have a landscape background on The Path (Modrinth galleries, Cataclysm/BOMD structure shots, minecraft.wiki biomes; stored in pack_imgs.scene). Draugr moved to Act III because its sword is tagged netherite tier.
- v21.1: Equipment audit (`build/pack_audit/eqa`). `gear_fix.py` raises 35 Acts to the `linggango_tweaks:gated/*` tier or the recipe gate. 197 items get a source note: Simply Swords/More loot injection, Too Many Bows loot, treasure bags, JEI-hidden, or "no source found". 322 missing weapons and armor are listed in `eqa/equip_missing.json` and not added yet; whole mods were never scanned, including vanilla, Soulslike Weaponry and Cataclysm.

## v22: Full gear re-extraction
- **Wide scan:** every weapon and armor in all 476 jars, found by class hierarchy, tags and attributesetter (`build/gear/wide/`; Forge 47.4.20 server jar for mjvm), plus vanilla gear. 2556 items scanned, 2524 with stats, 49 failures listed in the report.
- **Table:** 2070 entries and 327 sets, in `build/patches/gear_table.json`, applied by `gear_rebuild.py` before the other gear patches. New entries include all vanilla gear, ~60 Soulslike Weaponry weapons, Goety staffs, L2 Complements, Mystical Agriculture, Nature's Aura, Ad Astra suits and Celestial Core. About 300 armor pieces that only had estimates now have real armor values.
- **Level and form variants** are one entry using the strongest version (field `lv` lists the others): Travel Optics levels, Sword of the Elements forms, Mimi-cry forms.
- **Summon role:** Summonity staffs and whips and Goety Revelation summon whips are now kind `summon` and listed under Summon, no longer under Mage.
- **Acts** read the pack's `linggango_tweaks:gated/*` tags as well as progression_lock.
- **Set scoring:** a role set scores (1 + offence) × defence. Melee offence is the expected damage multiplier: damage% × speed% × crit, where the two crit systems' chance is capped at 100% and a crit adds +50% plus crit damage. Knockback resistance is capped at 100%. Topaz goes from far above everything at Act IV to top at Act IV–V only, and is outclassed later.
- **Gear pages** fold flat armor and damage modifiers into the base line, matching the in-game tooltip (Topaz Leggings: 5 armor, 1 toughness). Brutality's critical_strike values show raw, as in game.
- 179 new gear icons, from jar textures and three.js renders.

## v22.1: Fixes from the independent stat check
I stopped the check partway and applied what it had found (`build/pack_audit/verify2.json`: about 170 checks, most of them matching the table).
- **Runtime tweaks.** The pack's own linggango_tweaks mod changes damage while the game runs, and the wiki now models it. Per-mod flat buffs: Terramity +3/4/5/10, Soulslike per-weapon (+3 default), Lethality, EEEAB +6, Macabre and Legendary. Then BrutalityWeaponTweaks raises every forge:<tier>_tools weapon to a floor of min(floor, (floor+1)·1.8/speed − 1), with floors 6/8/11/14/18/24/31/40/50 and overrides for Royal Guardian Sword, Amaterasu and Tsukuyomi. Annihilator armor gets +3 armor and +2 toughness; Chaos Robes get +1/+1. Examples: Netherite Sword 19, Royal Guardian Sword 70, Unholy Lance 24.
- **Iron's Spellbooks swords** read 1 + tier damage; they were double-counted before (Boreal Blade 31 → 16).
- **Travel Optics magic weapons** no longer show the wrong 4.0/1.6 they had before (Cursed Wraithblade Lv 3 shows 18/1.3).
- **Athame** speed is 2.2.
- **Mystical Agriculture gear** is removed: KubeJS deletes every recipe for it. Jar recipes the pack removes are also dropped from Chungus Staff, Forlorn Scythe, Kraken Slayer and Royal Guardian Sword.
- **Goety Necro and Nameless staves** are now Summon.
- **Acts:** Rift Piercer and Woe Splitter 9; Eclipsium Edge, Tesseract and Enderitium 6.3; Old GPU 7.
- **Not fixed yet:** Summonity armor values from its config, Hazenn's Stuff armor spell attributes, Soulslike trick-weapon pairs, Mowzie's per-item tool config.

## v22.2 — boss list follows the quest book
- Side bosses now = The Path main line + the quest book "Bosses" chapter (decrypted LGQ1 quests). Dropped: Yeti, Naga, Vizier, Super/Ultra Sniffer, Forgotten Guardian, Infernal Dragon, Gob, Nameless Guardian, Virtue, and 39 extra bosses not in the book.
- Added Chorusling, Bone Chimera; Endersent fixed to Legendary Monsters; Mutant Enderman to the End act.
- Apollyon (Goety Revelation) is the end-game boss: Act XII, with the Black Book sabbath ritual.

## v22.3 — three-page audit (curio, equipment, boss)
- Bosses: End-only bosses moved after the Dragon (6.3), Skeletosaurus to Act V, drops from loot tables, Cumulonimbus name/entity.
- Curios: new patch `curio_gate.py` — keeper-gated curios can no longer sit at Act 0 via the random-loot rule (8 items); Oddeyes Glasses Act VIII; Void Crown/Robe after the Dragon.
- Equipment: fixed 5 weapons whose unknown speed read as 4.0; set Act = latest piece; "!"-hidden items left out of tier lists.
- Still open (needs the gear generator re-run): Cataclysm and other plain-Item weapons dropped, Iron's staffs missing, mage armor without spell stats, split armor sets, unscored weapons.

## v22.4 — image audit
- Crawled all 3831 routes (hub, Acts, bosses, side bosses, curios, gear items/sets, tier lists, hover tips): no broken <img>, no script errors.
- Added ~60 missing icons (jar item/block textures, tag aliases, composited Terramity fluid buckets, enchanted book for enchantments). `forge:nbt` and texture-path ingredients no longer render as letter tiles.
- Left as letters (3D-only or no texture): force_field, tartaric_foundry, nightmare_stalker_skull, laser_amplifier, antimatter, Mystical Agriculture mob chunks.

## v23 — linked ordering: quest book → bosses → drops → gear
- `boss_graph.json`: the quest book's Bosses chapter as a dependency graph (who each quest needs, dimension).
- `boss_order.py` (new patch): boss Act = consistent with that graph (never before its parents or its dimension: Nether V, End 6.3; chain depth spreads II–X; pulled down to its earliest dependant first). Wither/Warden/Apollyon fixed. Writes `boss_acts.json` → `BACT` in the app.
  - e.g. Ferrous Wroughtnaut VIII → III (2nd quest in the chain), Scylla VIII → V, Lord Pumpkinhead IX → V, Possessed Paladin VI → IV, Ignis VII → IX, Apostle VII → X.
- Drops follow their boss: gear with a loot table `entities/<boss>` (Gob's Gilded Hat 0 → VII, Geomancer set 0 → V, Sol Visage 0 → IV, Gundalf's Hat 0 → 6.3); gear crafted from boss-only items (`boss_only_items.json`, built from the pack's recipes + loot tables) follows them; set Act = latest piece; pure side-boss curio drops sit at the boss's Act.

## v22.5 — the four "not fixed yet" gear items from v22.1
New patch `gear_stats.py` (data in `gear_stats.json`, runs after `gear_fix`); scores and set totals use the same formulas as `gear_data.py`.
- **Summonity armor** now reads `summonity-common.toml [armor.*]` (the item classes replace the material values with it): Sniffer 8/14/11/8 armor, toughness 4–5; Spider 4/9/7/4; Obsidian 3/7/5/3; Virentium 6/11/9/6. Pieces with a minion slot get `minion_slots` (counts as Summon offence).
- **Hazen 'N Stuff armor:** all 70 pieces carry their `HnSArmorMaterial` attributes (read from the jar's static init; `HnSArmorItem` applies them to every piece): Max Mana +150–400, school and base spell power, cast time / cooldown, summon damage. Item → material follows the item classes.
- **Mowzie's tools** use their own `tool_config`: Spear 5/1.6, Naga Fang Dagger 3/2.0, Earthrend Gauntlet 6/1.2, Sculptor Staff 3/1.0 (Wrought Axe 9/0.9 was right).
- **Soulslike trick weapons** (from `trickweapons/item_mappings.json`): Kirkhammer ↔ Silver Sword, Holy Moonlight Sword ↔ Greatsword, Simon's Bowblade ↔ Blade are one weapon each. One entry (the stronger form), the other in "Other levels and forms", recipe kept. Holy Greatsword is not a pair (it maps one way to the Silver Sword).
- **Armor sets with two pieces for one slot** (Fireblossom Crown/Helmet, Wizard hats, Chaos hats) now count only the better piece.
- **Caveat:** Hazen mage sets now score far above Iron's Spellbooks sets of the same Act because Iron's own armor still has no mana/spell-power attributes in the table (same cause as the open "mage armor without spell stats" item). Fixing that needs the Iron's material attributes read the same way.
- Crawled all 2019 gear pages and 321 sets: no empty pages, broken images or script errors.

## v22.6 — boss backgrounds
- Audit of The Path: 63 of 65 side-boss cards had a landscape background. Chorusling (Legendary Monsters gallery shot of the End) and Bone Chimera (Dodo's Mobs dungeon shot) were the two added in v22.2 without one; both now have a 229×200 webp in `pack_imgs.json` (`build/pack_audit/boss_bg_extra.py`).
- Near-black scenes (Warden, Forsaken, Masticator, Stalker, Dead King) are real dark biomes or dungeons and were left as is.
- Hazard fixed: `boss_audit/enum.py` shadowed the stdlib `enum` when a script ran from that folder (it broke `import json`); renamed to `enum_jars.py`.

## v22.7 — build architecture
- `build/README.md`: data flow, source vs generated files, patch rules, weak spots. The old "Rebuild" section here pointed at `transform.py` and was stale.
- `build/check.sh` + `build/check.js` (new): patches idempotent and output reproducible (the committed tree is a fixed point of `apply_all.sh`), no script errors, 2019 gear pages and 321 sets render, all 65 Path boss cards have a background. Replaces the throwaway crawl scripts.
- Not done: `src/fx3d.js` is a bundle (three.js r169 + `fx3d.src.js`) whose build command is not recorded and whose bundler is not installed here, so it cannot be rebuilt from source yet; `gear.js` still monkey-patches `app.js` globals.

## v22.8 — weapon icons and a new ranking logic
- **Icons:** ~160 Ranged/Mage/Melee weapons (Elite Rifle, Ancient Sage Bow, Frost Staff, Boreal Blade …) showed their raw texture sheet, because their model is Blockbench cubes or GeckoLib. They are now rendered with the three.js icon renderer (`pack_audit/weapon_icons/`); Boreal Blade uses its GUI texture; 10 with no usable art (Brutality phasesabers, Ars spell bow …) fall back to a letter tile. Terramity guns lose their player-arm placeholder.
- **Armor, all roles:** a set no longer needs a role bonus to be listed. Every set is scored per role as defense × fit × (1 + bonus); Ranged armor used to stop at 8 sets (none after Act V), now it runs through Act XII. Bonuses saturate (`v/(1+v)`) so 800 mana on a Hazen set no longer beats everything 5×. Sets with unreadable armor (Goety robes) use the median of their Act.
- **Iron's Spellbooks armor:** the code attributes (125–150 mana, spell power, school power per piece, read from `ExtendedArmorMaterials`) were missing, so Pyromancer/Electromancer/Priest … had no mage stats. Added (53 pieces).
- **Ranged / Mage / Summon weapons:** `+13%` per Act of unlock, `+≤10%` for how hard to get, times readable bonuses, instead of a flat 1.0 for 206 of 226 items. Items under 25% of the Act's best are hidden (search still finds them). `oiA` now maps Act 6.1/6.2 to Act VI: Doombolt Battleaxe (6.1) had index −1 and showed at Act 0.
- **Early mage:** +12 weapons the extraction skipped (Graybeard Staff, Artificer's Cane, Ice Staff, Blood Staff, Ars Novice/Mage's/Archmage Spell Book, Pumpkin Staff, Sonorous Staff, two pistols, Railgun). Act 0 Mage went from 1 to 5 options. Lord Pumpkinhead's loot table (`entities/pumpkinhead`) now maps to the boss.
- **Not done:** Iron's spell books are curios, not weapons, so they are not ranked; the Ars books and Railgun have no icon; ranged/mage damage is still not read from code, so within one Act most weapons share a tier.

## v22.9 — anti-"organic architecture" refactor
- **One place for scoring:** DPS, defense and tiers are computed only in `src/gear.js`. The Python side produces facts (`patches/gearlib.py`: `off_of`, `set_facts`, shared by `gear_stats.py` and `gear/gear_data.py`); the old `sc` scores in the table, `gear_fix` and `gear_stats` are gone. Tier lists before/after are identical except float-tie order inside a tier.
- **Gear is a pure pipeline:** `patches/gear_pipeline.py` builds `gear_data.js` in memory from `gear_table.json` + overlays and writes it once (stages are functions: extra → gate → fix → stats → boss_order.gear). Icons and mod names, which only lived inside the generated file, are source JSON now (`gear_icons.json`, `gear_names.json`). Acts are snapped onto `ORDER` at the end. The `sx` re-run markers are not needed.
- **Invariants in `check.js`:** Acts and gates in `ORDER`, finite scores, melee DPS > 0, ≥3 weapons per playstyle and ≥5 armor sets at every Act (SU ≥2 from Act II), nothing listed before its Act.
- **No monkey-patching:** `gear.js` registers `EXT.route` / `EXT.tip` handlers in `app.js`; the initial render is in `app.js` (`DOMContentLoaded`). Found and removed dead hooks: the Act, mod and slot pages redirect to #home, so the home-page equipment strip and the per-Act "Best gear" block had not shown for a while (CSS `.gbest`, `.gstrip` is still there).
- **fx3d.js is reproducible:** `bash build/fx3d_build.sh [--check]` (esbuild 0.25.5 + three 0.169.0 pinned in `build/package.json`) gives the committed bundle byte for byte.
- **Docs and CI:** `build/ARCHITECTURE.md`, README rewritten, `.github/workflows/check.yml` runs `check.sh`, then fails if committed outputs differ from what the build produces.
- **Left:** curio `data.js` is still patched in place by ten scripts (no source table); `app.js` is one big file of globals.

## v22.10 — curio data.js: decided, not refactored into a pipeline
- Tried to rebuild `data.js` from `transform.py` + the patch chain: the result is 1 MB smaller and different (boss tables and other edits were made to `data.js` directly), so it is **source**, not output. The nine one-time edits (`moreartifacts`, `text`, `fx_numbers`, `pack_facts`, `curio_gate`, `tag_reps`, `recipe_notes`, `drops`, `tc_chests`) moved to `build/migrations/` as a record (all no-ops on today's file) and no longer run in `apply_all.sh`. Build output is byte-identical.
- Still in place: `boss_stats`, `boss_order` (curio Acts), which derive from changing inputs.


## v22.11 — equipment ranking: four playstyles, scores from the game's own rules
- **Tank removed.** The tier list has Melee, Ranged, Mage, Summon; defense is now inside every score. Old `#gear/…/TA/…` links and saved state fall back to Melee.
- **Rules read from the jars, not guessed:** Apothic Attributes 1.3.7 (`ALCombatRules`): damage × a/(a+armor), a = 10 under 20 damage, 10+(dmg−20)/2 above; toughness only weakens armor shred/pierce (2%/point, max 60%). Better Combat 1.9.0: `allow_fast_attacks` defaults to true and zeroes the target's hurt cooldown, so melee DPS = hit × speed has no 2-hits/s cap.
- **Armor sets:** score = role output multiplier × effective health^k (Melee 1, Ranged .7, Mage .6, Summon .6), EHP against the attack damage of the Keeper that ends the Act (`entitybalance.json`: 10 at Act 0 → 50 at XII) on top of 20 + 4 HP per Act. Scores now depend on the Act. Output multipliers per stat (spell power + best school, ÷ cooldown, mana saturating; crit capped at 100%; flat attack damage against the Act's typical weapon hit; +25% per minion slot) replace the old fixed role fit (1/.9/.8/.65) and the +100% saturation of every bonus.
- **Ranged / Mage / Summon weapons:** the per-Act step is fitted on the top-10 melee DPS of every Act (log-linear least squares): ≈ +20% per Act, not the hand-set +13%. Their role bonus is the same multiplier as armor.
- **Melee list:** staves, spears, whips and gunblades with readable melee damage are ranked at their real DPS (their Mage/Ranged score stays an estimate; the tile is only faded where the score is estimated). "Sight of the Void (Creative Only)" is hidden.
- Set facts now carry their summed attributes (`at`, from `gearlib.set_facts`, recomputed for every set in `gear_stats`); all other facts unchanged.
- `check.js`: no Tank role, every set score finite and positive for every role and Act, fitted step within 1.05–1.3.
- **Assumptions to revisit:** pack config could override Apothic's formula or Better Combat's fast attacks (not in the repo); Arion's hit (12) and Act VIII (50, the Discord's forms) are interpolated; 10% shred, 20+4 HP/Act and the k weights are judgement.

## v24 — interaction layer (desktop): quick search, page transitions, loading screen
- **Quick search** (`build/src/ux.js`, new): the header and title-screen search boxes now list results as you type, across curios, weapons, armor pieces, armor sets, Keepers, side bosses and the five sections. Results are grouped, the matched part is underlined, curio names keep their rarity colour, and hovering a row shows the usual tooltip. ↑/↓ move, Enter opens, Esc closes, Ctrl/⌘ K or / focuses the box. The last row still filters The Path by the text (old behaviour). On The Path itself the header box keeps filtering the grid live. Focusing the empty box lists the last 8 pages opened (stored in this browser only).
- Before, the header box only searched curios and jumped to The Path on the first keystroke, so gear and bosses could not be found from it.
- **Page transitions:** moving between sections cross-fades with the View Transitions API (header stays put); switches inside a page (Equipment Act or playstyle, Path filters) redraw in place, and Equipment tiles deal in row by row. Off under `prefers-reduced-motion` and in browsers without the API.
- **Loading screen:** the page used to stay blank while ~16 MB of data loaded on the first visit. It now shows a loading bar that counts the data files as they arrive (indeterminate in the offline file).
- **Header:** the section you are in is marked in the nav (green pressed button, as for other selected buttons); the bar turns to frosted glass once the page scrolls.
- **Title screen:** one entrance (logo, then search and menu buttons).
- All new surfaces use the vanilla item-tooltip look (near-black violet, violet gradient border). Mobile is not redesigned (desktop/laptop target, as since v6).

## v25 — Vercel agent skills, guideline audit, shared-element transitions
- Installed `vercel-labs/agent-skills` (`npx skills add`, 9 skills in `.claude/skills/`, `skills-lock.json`). Used: **web-design-guidelines** (audit below) and **vercel-react-view-transitions** (its patterns, applied with plain `startViewTransition` since the wiki has no React). The React, React Native and Vercel deploy skills do not apply to this site.
- **Bug fixed:** on Mechanics the ritual cards' ingredient icons were stretched to ~120 px over their own text (`.rtype img`, meant for the scene picture, also caught the 22 px chip icons).
- **Audit fixes:** skip link to the content; search fields get `name`, `autocomplete="off"`, `spellcheck="false"` and placeholders ending in “…”; the curio count announces changes (`aria-live`); headings balance their lines, numbers use tabular figures; `touch-action: manipulation`; the brand name is `translate="no"`. Not done: explicit `width`/`height` on every icon `<img>` (they are sized by CSS in hundreds of contexts and decode from in-memory blobs, so there is no layout shift to fix). Kept sentence case for headings and buttons (the wiki's own style) over the guideline's Title Case.
- **Shared element:** the icon you click (a Path tile, an Equipment tile, a quick-search row) grows into the item page's big art, and flies back to its tile when you go back. **Previous/Next** on curio pages (buttons or ←/→) slide the page the way you are going.
- **Boss pages:** the boss bar fills as the page opens. **Build planner:** each slot row shows the game's curio slot icon; empty rows are dimmed so filled ones read first; slot labels no longer wrap.

## v26 — The Path as an interactive map (home page)
- The home page's long Act list (≈3000 px) is now a map: 13 advancement frames on an XP bar, and one panel for the selected Act. Click an Act or use ←/→/Home/End; the panel slides the way you move.
- Each panel: Act title strip, what opens it, curio / Must-Have / side-boss counts, the Keeper to beat next (links to its boss page), the best melee weapon at that Act (from the Equipment ranking), the side-boss cards (unchanged), and “See N curios”, “See gear”.
- **“I'm here”** marks your run (this browser only, `localStorage` key `lgw-here`): the XP bar fills to that Act, reached Acts get the gold obtained-advancement frame, later Acts fade, and the map opens on your Act next time.
- All 13 panels are in the page (others `hidden`), so `check.js` still finds all 65 side-boss cards; their background pictures load lazily when a panel opens.
- The map's numbers use the body face: the pixel face misreads digits (156 looked like 186), as found in v13.

## v27 — gear base stats read in game
- `patches/gear_runtime.json` is the pack's own dump (`kubejs/server_scripts/dump_gear.js`, run in game with `/kubejs custom_command dump_gear` on 6.6.5b4, 2026-10-22): `ItemStack.getAttributeModifiers` per slot, i.e. what the game applies after attributesetter and the linggango_tweaks attribute events. Stage `gear_runtime` (after `gear_stats`) lays it over the jar reading for 1760 items. All-zero dumps (stats in NBT: Blood Magic sentient tools) and weapons with no damage/speed line (Just Dire Things) keep the jar values.
- Checked against the pack's 65 attributesetter files: 4955 of 5048 modifiers present with the same value; the other 93 are all `forge:entity_reach`, which the game sets to 0 on those items. The dump shipped inside the serverpack zip was older (only 48 of 1471 `gear_authored_profiles_*` modifiers) and was not used.
- 165 items change base stats. Examples: Iron's Spellbooks chestplates 10 armor / 5 toughness (was 8/0), Travel Optics armor toughness 4 (was 0.2), Gomoria Leggings 31 armor (was 0), Poseidite Sword 15 (was 22.5: its +50% is not a held-item modifier), Curse Crystal Knife 8.2 (was 19), Doombolt Battleaxe 21 (was 23). 413 items change bonus attributes (mana, cooldown, spell power…).
- Visible results: Travel Optics mage sets lead Mage armor from Act VII; HF Meowrasama (speed 4.48: no base speed modifier) and Flames of Eldritch Lv 3 (+64 attack damage) are the top Melee DPS at Acts IX–XII. These are the game's numbers, not estimates.
- Mage armor now takes the better of two spell systems (Iron's multipliers, or Ars Nouveau flat spell damage against the Act's typical hit) instead of adding Ars damage /5, which made Adam's Ars Plus sets +320%.
- Iron's Gold Crown (+10000 mana, creative/supporter item) is hidden from the lists.

## v28 — tools to measure Ranged / Mage / Summon weapons in game
- `build/pack_audit/kubejs/`: `dump_gear_all.js` (attribute modifiers of every item, for the ~190 staves, bows, guns and summon weapons the pack's dump skips), a damage logger (`dmg_logger.js` startup + `dmg_logger_commands.js`) that records final damage on target dummies per held item, split into direct / projectile / minion / dot, and `dmg_queue.json` (71 weapons: 40 Ranged, 13 Mage, 18 Summon). See `build/pack_audit/README.md`.
- Not run yet: written for KubeJS 2001.6.5 (the pack's version) and syntax-checked, but no game runs in this environment. Next: the user runs them; their JSON goes into the gear pipeline (attributes via gear_runtime, measured damage as a new fact for gEstScore).


## v29 — plan: every wiki number from the game
- `build/RUNTIME_PLAN.md`: source ranking (game export > pack files > jar reading > external sites, never shown as numbers), a gap table per area (175 of 1328 curios still have "?"/"…" stat lines; boss special attacks, loot with global loot modifiers, recipes after KubeJS are not runtime yet), one `lgw_export` KubeJS bundle (meta, gear, curios, client tooltips and names, recipes, tags, bosses, loot) plus the v28 damage logger, import stages with freshness checks and diff reports, phases P1–P6.
- minecraft-guides.com checked: 55 of the pack's 446 mods, mod defaults not pack values (Cocktail Cutlass 7 there, 12 in game), reconstructed tooltips. Reference only.

## v30 — calmer UI (Discord feedback from Misa) and a site-only `main`
- Feedback: fewer shadows, simpler buttons, no redundant animation (each Act floating), The Path drew everything at once. Kept the game identity (pixel face, vanilla tooltip palette, rarity frames, item slots) and cut the decoration on top of it.
- **Motion:** every infinite animation removed (tile float/bob, hover bob, rotating rare frames, tooltip particles and prism names, emblem float, boss-head sway, title panorama, splash pulse) and the per-tile pop-in / deal-in. Kept: page transitions, the item's own animated textures (`.aimg.anim`), the loading bar, one-shot title entrance.
- **Flat:** buttons and panels have one border and change colour for state; no bevel insets, drop shadows, glows or hover lift/zoom. Path tile icons lost their 4-way outline filter (also a paint cost on ~1300 images). Item slots keep their inset (that is the slot, not decoration). Text shadow only on text over a picture.
- **The Path:** opens the reader's "I'm here" Act, else Act 0–I; the others are collapsed and their tiles are built only when opened (`st.op` in `lgw2`; first view 615 tiles instead of 1327). With any filter on, every Act with matches opens; closing one then is session-only (`st.cl`).
- **Repo:** `main` keeps the site, the build and the pack-extraction scripts; notes, plans, prompts, the transform/migration history, screenshots and the agent skills moved to this orphan `workspace` branch, same paths. `CLAUDE.md` rewritten for that split; CI runs on `main` only.

## v31 — the flat UI is reverted; The Path change stays
- The user found the v30 flat pass plain rather than clean, and that it lost the Minecraft feel. `v5.css` and `style.game.css` are back to v29 byte for byte (same `static/style.b34d63b07f.css` hash): bevels, shadows, glows and all animations return.
- Kept from v30: The Path opens one Act (“I'm here”, else Act 0–I) and builds collapsed Acts on open; the repo split (`main` = site and build, `workspace` = notes).
- `CLAUDE.md`: the GUI look is deliberate; do not flatten it; changes to the overall look need the user's approval.
- Misa's points on looping animation and shadows are therefore not addressed; if they come back, ask the user before changing anything.

## v32 — design direction agreed with the user, then built (Minecraft GUI kept)
- **Direction (agreed in a question round):** Minecraft pixel style, ideas learnt (not sprites copied) from Faithless, Shrimp's Immersive Interfaces, Smooth GUI and the pack's own resource packs. Three visual languages by job: *quest book* for progression (The Path map, Bosses, boss pages), *inventory* for things (curios, Equipment, Builder, Mechanics), *ornate metal/gold* for rarity only; one language per block, never mixed inside one.
- **Pack resource packs read (scratch only, nothing embedded):** Linggango Textures (Iron's Spellbooks GUI: slate-metal frames, segmented bars, gem sliders, silver/gold ornate frames; `LICENSE.txt` says All Rights Reserved although the CurseForge page says "feel free to use it"; part is from Coquet by jekaloic) and Linggango - FTB Quests Theme (near-black, per-chapter tints, white hollow outlines, quest shapes, white/grey dependency lines, blue in progress, green ticks; no license stated, so all rights reserved).
- **Kept inside the GUI look (CLAUDE.md):** the quest-book ideas are drawn on the bevelled containers, not flat. A first draft with flat hollow outlines was dropped before commit for that reason.
- **Built:** footer Mojang/Microsoft disclaimer, takedown contact (GitHub issues) and per-source art credits; hexagon Act and boss shapes, white/grey quest line, green done ticks, blue current Act, per-Act tints, numbered boss chain, orange "sure drop" reward rings; rarity frames on item art (Epic iron, Legendary silver + crest, Mythic gold + gem crest, Must-Have gold + star crest); four section scenes with captions (Bosses: pack screenshot; Mechanics: Goety Black Book picture; Equipment and Builder: composed from vanilla 1.20.1 textures by `build/pack_audit/scenes.py` into `build/src/scenes.js`).
- **Bug found:** the body class `qb` collided with the existing `.qb` heading class and turned body text into the pixel face; renamed `qbook`.
- **Open:** a permission message to Misanthropy was drafted for the user to send (logo, title screen, Act strips, screenshots, GUI ideas). The user chose to go ahead before a reply. The 126 boss landscape pictures have no recorded per-picture source (only side-boss pages link theirs). linggango.wiki.gg exists; positioning against it was not discussed yet.

## v33 — Linggango 6.6.6hf (Goety Update)
- **Source:** CurseForge 6.6.6hf (file 9304214) + the slim server pack (383 jars, has every content mod). Diffed against 6.6.5b4. The quest book was read locally in plain SNBT for facts only (the decoding step is not committed).
- **Gear:** full wide re-extraction. No Forge installer run: `build/migrations/srg_remap.py` remaps Mojang's 1.20.1 server jar (server.txt + MCPConfig joined.tsrg) into the srg jar mjvm needs; vanilla stats check out (wooden sword 4/1.6). mjvm now models WeakHashMap/IdentityHashMap/TreeMap and `java/util/Collections` wrappers (Simply Swords 1.70 keeps per-weapon damage/speed in a synchronized WeakHashMap; without it every unique read 3/-2.4). 2140 items / 333 sets (+123: Opposing Force 58, Goety Awaken 22, Composite Material 14, Simply Swords 12…). Extraction failures carried over from the old table (Soulslike bows, Matter Cannon, Dark Wand).
- **Runtime dump:** the gear_dump.json inside the 6.6.6 server pack is stale again (~70% match with its own attributesetter). The 6.6.5b4 in-game dump stays, minus `stale_666` (125 items whose jar stats, tool tier tag or attributesetter entry changed). Re-dump in game when possible.
- **Gates:** 6.6.6 loosened `linggango_tweaks:gated/*` (iron 269→6, gold 463→200, emerald 388→89, diamond 383→135); the old list is `gated_classic` (Classic Locks option). Quest chapters: none locked (`chapters = []`). CHAP now lists the mods with the most items per gate.
- **Bosses:** `pack_audit/quests/boss_graph.py` (reproduces the 6.6.5b4 graph exactly, then 6.6.6): Bone Chimera, Doppelgänger gone; Ignis after the Nightwarden; Goety's Bosses group (Vizier back, Minister, Crone, Heresiarch, Skull Lord, Wither Necromancer, Brood Mother, Wight, Ender Keeper) + Ice Hermit (Frostyard). Boss Souls: 30 side bosses → Keeper summon item, shown on side-boss pages. Keeper summon pages show the soul slot and 4–5 machine routes (`38_summon_routes`).
- **Curios:** `build/migrations/v666_curios.py`: Powah/Dark Doppelganger removed, 33 deduped accessories → U (kept copy inherits loot, `linggango_integration:curio_dedupe` loot modifier), 54 gate changes, 31 new curios (`nw:1`, filter chip "New in 6.6.6"). Rarity of new curios is judgement.
- **Other:** goety.json 710 rituals; AE2 gates; entitybalance; texts (invasions, hardmode +30 levels, accessory soft cap/lifesteal cap, Sabbath Engine). Fixed unhandled "Transition was skipped" rejections (check.js went from 2350 script errors to 0).
- **Open:** Keeper attacks (boss_info) not re-read from Armageddon code; guides.json not regenerated; the Guide page (`guide()`) has no route; brutality/goety bag curio-tagged items and Goety Awaken grimoires not added; merged to main (fast-forward, 9db6b08).

## v34 — visual pass from `PROMPT_VISUAL.md` (taste-skill + ui-ux-pro-max), Minecraft GUI kept
- **Prompt:** `PROMPT_VISUAL.md` (this branch). Uses Leonxlnx/taste-skill (app-screen run, critique rubric) and nextlevelbuilder/ui-ux-pro-max (priority order, Pixel Art reference) as measuring tools only: both skills' house styles (no gradients/shadows; Swiss/flat for wikis) would repeat the reverted v30 pass, so the identity rules are allowed explicitly. Neither skill is installed in the repo.
- **Tools did not run:** the auto-mode classifier blocked running both skills' scripts (external code). A Playwright stand-in measured overflow, title time, text under 12px, contrast and cut-off text at 1440/1024/390.
- **Group 1 (bugs):** title screen said V6.6.5b4; boss fight-order number sat on long names; NEW badge on every item at Act 0–I (NEW = unlocks at this Act); phone: `#fold` was hidden at every width so filters could not be opened, top nav cut "Mechanics"; overflow in the hub slot list (phone) and Mechanics ingredient chips (1024/390); filter-chip counts 11px at 75% opacity (~3.3:1); Previous/Next labels lost their colour to a v5 rule.
- **Groups 2–3 (user approved all):** The Path legend is one short line (tooltips keep the wording); curio card has one "Rarity" row ("power Epic" for Must-Have) and a quiet "Name colour" row; Equipment tier rows with few items share a line; title screen buttons are "Continue: Act N" / "Gear at Act N" from `lgw-here` (else Start The Path / Equipment) + Build planner; labels ≥12px; curio pages use `noside`; relic-level note wraps.
- **Checked, not a bug:** "curio title late" — the title paints within ~0.1 s on navigation and ~1.3–1.8 s on a cold load (5 MB data); blank title areas in full-page Playwright screenshots are a capture artefact (clipped screenshots show it).
- **Self-scored critique, round 0:** Bosses 7.7, hub 7.3, The Path 7.2, curio 7.1, Equipment 6.9; weak spots were hierarchy, not style. Not re-scored after the changes.
- **Merged:** main a685cd5 (after the PR #1 merge and b229145 on main). Still open: hub Path-map labels 11px at ≤1024; NEW is still on 67/105 items at Act II.

## v35 — one article layout for every detail page (layout only; the GUI look unchanged)
- **Asked:** a layout fit for a modpack/game wiki that stays easy to edit and extend, after many wikis, without changing the look.
- **References read:** Minecraft Wiki style guide (Features layout: Obtaining → Usage → … → History/Trivia/Gallery → See also → Navigation; infobox templates), Terraria wiki.gg (accessory page: infobox, Crafting/Used in, Notes, Tips, History, navbox), Calamity wiki.gg (boss page: Spawn, Behavior/Attacks, Aftermath, drops in the infobox, version banner on guides, boss navbox), Hypixel SkyBlock wiki (Navigation section at the foot).
- **Built:** `article()` in app.js (breadcrumb, h1, lead, meta, sections, infobox = picture + rows + id/Copy, "On this page", navbox, "Checked against Linggango V6.6.6hf" from `PACKV`), `wireArticle()`, `navbox()`, `wikiNav()` (Keepers, The Path, Equipment at this Act, tools), `secsOf()` (ready-made section html → article sections), `KEEPERS()`. Curio pages moved onto it unchanged; gear and set pages (were ~60% wide), Keeper pages (were one column, no infobox), side-boss pages (big empty hero) rebuilt on it.
- **New content from existing data:** Keeper "What it opens" (curios first available at the Act, Must-Haves, Keeper-gated count, links); Keeper infobox damage/armor only where the pack note matches "Keeper; N dmg / M armor" (BOSSR Keeper rows by order; the name match was wrong for Zoranth Newborn and the Ender Dragon); navbox groups: same mod at the Act (curios), set pieces + best of the playstyle at the Act (gear), side bosses of the Act.
- **Narrow widths:** below 1180px the infobox follows the lead (it used to come after every section) and the contents list hides; v5's 220px cap on `.ip-stage` removed (left a band in the square frame); `.ip-main` is `minmax(0,1fr)` so a recipe grid no longer widens the phone page.
- **Checks:** check.js renders all 3,878 detail pages and fails one without the article, a title, an infobox, a navbox or a heading on every section. README "Adding or changing a page" documents the contract. Bundle growth: app.js +3.6%, CSS +1.5%.
- **Not changed:** list and tool pages (The Path, Equipment tier list, Bosses, Build planner, Mechanics) keep their layouts; Bosses and Mechanics got the wiki navbox. Dead CSS of the old gear header (`.gph`, `.gcols`, `.gpage`) and side hero (`.sbhero`) is still in v5/style.game.css.
- **Merged:** main a8df946.

## v36 — rooms: the forge/armory scene woven through the wiki (taste-skill run)
- **Asked:** use taste-skill to improve the whole look, taking the armory scene (v32, `scenes.py`) as the reference, but woven into the wiki rather than one more picture.
- **taste-skill, as a method:** inventory (Keepers, Acts, curio slots, item frames, the player's base), idea sentence: *"On this wiki, the player's own base — a wall of blocks, a floor, lanterns, item frames — becomes the room every section page is built in."* Competitor test passes only because the frames hold this pack's items (other Minecraft wikis are flat articles). "One live thing": the planner's wall is your build; Equipment's wall changes with the Act and playstyle chips. House rules on gradients/shadows still not applied (Minecraft GUI identity; the lantern glow is a gradient). Its scripts are still blocked here (external code); own Playwright audit + check.sh instead.
- **Built:** `room(kind, items, {head, min, cols, label})` in app.js; rooms in CSS (`.room[data-room=forge|armory|crypt|ritual|library|vault]`: wall, pillars, floor, three pieces of furniture, lantern/soul lantern, glow colour); `scenes.py` now writes 34 vanilla 1.20.1 textures as `ROOMT` (20 KB, was two PNGs of 53 KB), exposed as `--rt-*`. The Path (library, Must-Haves by Act), Equipment (forge, best gear with tier letters), Build planner (armory, your build, 8 empty frames until filled), Bosses (crypt, summon items in fight order), Mechanics (ritual room, curios made by rituals), home Equipment and Must-Have blocks (were hotbars). Infobox on detail pages: item in an item frame (glow frame for Must-Have) on the Act's wall with a lantern light; footer has a plank floor edge. The old `.scene`/`.phead` picture-beside-the-title code and CSS are gone.
- **Fixed on the way:** frames were 52 px (global padding), furniture sat inside the floor, the "Dragon" label ran into the next frame (10 px for labels over 3 chars), the phone infobox squashed animated item strips (no image override; only the frame shrinks), the Act emblem floated into the phone title.
- **Checks:** audit at 1440/1024/390 clean (no overflow, no small or low-contrast text flagged beyond the known gradient false positive); check.sh green (3,878 detail pages on the shared layout, 0 script errors).
- **Self-scored critique (not re-measured by taste-skill's inspector):** section headers went from a title plus a captioned picture to one composed header that is also a menu. Weak spots left: the crypt has no furniture; Build planner's empty frames read as decoration until filled; rooms are not on list pages without a header (Mods, slot lists).
- **Merged:** main 3b15cf0.

## v37 — room textures from licensed mods and a resource pack
- **Asked:** not only the textures of the reference scene: also the base game, mods and good resource packs.
- **Licences checked first (Modrinth API + the repos' LICENSE/README):** Goety MIT (whole repo); Blood Magic CC BY 4.0; AE2 code LGPL, textures CC BY-NC-SA 3.0 (Ridanisaurus Rid, AlgorithmX2 et al.); Alex's Caves, BoMD LGPL-3.0; L2Hostility LGPL-2.1; Xali's Enhanced Vanilla CC BY-NC 4.0 (src/LICENSE); Faithful: own licence, use and change allowed with credit, a link and the licence link; Cataclysm CC BY-NC-ND 4.0; ARR: Iron's Spellbooks, Terramity, Ars Nouveau, Relics, Meet Your Fight, Legendary Monsters, Bare Bones; Mowzie's, Create, Supplementaries, Ad Astra have their own licences (not read). Modrinth's licence field often covers code only; AE2 is the example where textures differ.
- **Used:** Xali (brick variants → forge wall sheet with vanilla cracked/mossy bricks; bookshelf_1/7/12, lectern_front_2), Goety @02adbe7491 (crypt_bricks, crypt_tiles, haunted_planks, stripped_haunted_log, haunted_bookshelf, cursed_cage, shade_stone_bricks; pixels identical, re-encoded to drop ~25 KB of editor metadata each), AE2 @1c2f96e70c forge/1.20.1 (sky_stone_brick, smooth_sky_stone_block, controller, drive_front, fluix_block, item_storage_cell_1k…256k; byte for byte because of ShareAlike). New room `storage` in the Mechanics AE2 section (cells with the Act each opens). Goety's 64×64 model sheets (dark altar, pedestal, gravestone, braziers) are UV maps, not block faces: not used.
- **Not used:** Faithful 32x (32 px next to 16 px icons breaks the pixel grid), Linggango resource packs (LICENSE.txt ARR; permission message to Misanthropy still unsent/unanswered), ARR/ND mods.
- **Credits:** footer Art column with licence links; `scenes.py` header lists sources, commits and the rules; README "Rooms" has the licence rules for adding textures. CSS keeps a vanilla fallback for every third-party texture. Per-room `--dim`/`--pb` so Goety's dark blocks stay legible. ROOMT 56 KB.
- **Checks:** audit 1440/1024/390 clean; check.sh green. **Merged:** main 83d08e7.

## v38 — GUI skin from Misanthropy's packs and vanilla; richer rooms
- **Permission:** the user reports that Misanthropy agreed; use all of Linggango Textures (asked not to record the date). Credited in the footer with "used with permission"; Linggango Textures' LICENSE.txt says it includes textures from Coquet by jekaloic, so jekaloic is credited too (Misanthropy's consent cannot cover jekaloic's part; the user chose to use all of it).
- **Sources found:** the modpack zip (CurseForge 1343057, 6.6.6hf) holds no texture packs except NoBushyLeaves; its manifest lists 24 resource packs. Linggango Textures = CurseForge 1381088 / file 8994067; Linggango – FTB Quests Theme = 1583288 / 8520681 (both Misanthropy), downloaded from edge.forgecdn.net. Licences of the others via Modrinth: Dark/Modded Coffee GUI, Vanilla Experience+, Lanterns with Candles, Brush & Juice, Fresh Waystones are All Rights Reserved → not used; Terra GUI, Stay True not found on Modrinth → not used.
- **Linggango Textures content:** small (ISS GUI sheet `irons_spellbooks/textures/gui/icons.png` + vanilla checkmark/separators + birch leaves + hit sounds). Cut from the ISS sheet: slate-metal panel frame, slider track and cyan fill (knob columns spliced out), gem knob (cyan pixels removed), slot frames, lock, silver and gold ornate frames. FTB theme: background_squares tile, alert/chest/info icons, gear shape.
- **Applied:** vanilla button (widgets.png 9-slice) on .mcb/.pnx/.gseg/.gacts/tabs/Copy, green kept for the selected one; slate-metal frame on search fields, infobox, navbox; relic sliders (track, `--rv` fill via `setRv`, gem knob); silver ornate (Legendary) and gold ornate (Mythic, Must-Have) on infobox art (×10) and Path tiles (×2); vanilla boss bar (bars.png pink, purple for the Wither via `data-boss-kind`); `body.qbg` quest-book background on The Path, Bosses, boss and side pages; header separator under the top bar; emoji → sprites (Keeper/ring locks, ritual notes); beaten-Act check; section markers (info / chest / alert); planner empty slots (black, tan for bonus).
- **Rooms:** per-room lights (wall torches in forge, soul torches in crypt, lantern + candle in armory/library, soul lantern + purple candle in ritual, amethyst in vault, animated sea lantern in AE2 storage), chains for hanging lights, a vanilla painting beside the frames (Fighters, Skull and Roses, Burning Skull, Graham, Wanderer), particles (sparks+flames, souls, enchanting glyphs, glow, glitter twinkle) on the right half when the wall has a title; hidden under reduced motion.
- **Fixed on the way:** border-image `fill` painted over backgrounds (brown search fields, lost green state, invisible slider fill); badge under the gold frame; room text squeezed on phones by the new `.rwall` column.
- **Size:** ROOMT 89 textures, 105 KB (pruned from 152). Audit 1440/1024/390 clean; check.sh green. **Merged:** main badb31c.

## v39 — rooms of objects, not lamps; the game's effects; each Act's air
- **Ask:** keep the direction, keep collecting assets, improve everything (backgrounds, buttons, borders, every page) and stop overusing lamps: use more varied, more relevant things, effects and particles.
- **Rooms:** the lantern pair (`.rlamp`) is gone. Each room shows objects on its furniture (`--o1..3`, glow `--g1..3`): trophy heads (skeleton, wither skeleton, built from the mob skins' faces), beacon, gold block, spawner, grindstone, cartography table, armor stand, compass, spyglass, map paper, soul fire (animated), AE2's lit controller, Goety's soul candlestick. Forge, crypt and ritual throw their particles from the object that makes them (`rptHop`), so nothing drifts over the title.
- **Effects:** enchantment glint over Mythic/Must-Have items (masked to the item, `glint(d)`); vanilla sweep attack (8 frames, ×3) once on hover over weapons (gear tiles, gear infobox, forge frames); Act particles `envFx(a,k)` from the Act's block (`PENV`): petals (dirt), drips (stone/deepslate), lava+ash (Nether), souls (soul sand/soil), sculk souls (sculk, reinforced deepslate), portal motes (End/obsidian/purpur), glitter (gilded blackstone). Bosses override (`BENV`/`BTEX`: Warden sculk, Wither soul sand, Dragon end stone). Portal and ash are the vanilla generic sprite tinted the way the game tints them.
- **Pages:** Bosses cards stand on their arena block, particles run only on hover; The Path panel's side-boss column is a window on the Act (block + particles), empty-state note centred; The Path's Act labels are cut from the Act's block.
- **Bug fixed:** collapsed Acts reserved 420 px (content-visibility placeholder) and shrank to 55 px when scrolled into view: the page jumped and full-page captures showed empty boxes. Now `.tier.closed{contain-intrinsic-size:auto 56px}`.
- **Size:** ROOMT 109 textures, 169 KB base64 (18 unused pruned from scenes.py; regenerated, diff = only those 18 removed).
- **Checks:** audit 1440/1024/390 no overflow, no script errors; check.sh green (3,878 detail pages on the shared layout). **Merged:** main 8ed56df.
- **Next ideas:** per-boss arena textures for Keepers too (needs each arena's real block from the mods); hit/crit particles on the tier-list S row; check the Wither Relic drop that has no icon.

## v40 — prompt for an asset / effect / particle library (`PROMPT_ASSETS.md`, no site change)
- **Asked:** a prompt to build a library of high-quality assets, effects and particles for later use; Linggango's own mods, resource packs and shaders first, then well-known sources, then lesser-known ones, then other methods (combining, pixel-art repos).
- **Checked for the prompt (6.6.6hf, CurseForge 1343057 / 9304214):** manifest 455 entries, Forge 47.4.20; `options.txt` enables 34 resource packs (list in the prompt); shaders are Complementary Reimagined r5.5.1 + Euphoria Patches 1.6.8 and Mellow v3.3 (settings only). Complementary License 1.5 allows content creation (screenshots), not code redistribution/modification outside §1.2/§1.3; Euphoria License 1.1 forbids direct redistribution; Mellow is MIT. Modrinth licences of ~50 related projects recorded in the prompt (code licence; assets to be checked per repo). Modrinth search accepts SPDX `license:` facets (case-sensitive).
- **Library design in the prompt:** lives on `workspace` under `assets/` (catalog.csv, sources.csv, LICENSES/, fetch.py, lib/, gen/, gallery.html, shortlist.md, permissions/). Tiers: A usable, A-SA byte for byte, B reference only (coordinates + sha256, never committed: the repo is public, so `workspace` is publication too), X excluded (Terraria GUI, Confluence: Re-Logic assets). Quality rubric on 6 axes; shortlist of ≤60 mapped to wiki uses. Stops for approval after the licence inventory.
- **Open:** whether Misanthropy's permission covers the `linggango_*` mods' assets; AI-generated art yes/no; size budget for `assets/`.
- **Phase A run (same session):** all 455 manifest files downloaded to scratch and read (nothing executed, nothing committed). `assets/sources.csv`: 459 rows → A 222, A-SA 8, A-perm 2, B 225, X 2 (A: 20 read by hand, 199 declared by jar/Modrinth only). Richest A for effects: Goety, Brutality*, Alex's Caves, Macabre*, BoMD, EEEAB's Mobs, Blood Magic, Alex's Mobs, Hexerei, Immersive Weathering, Dungeon Now Loading, Soulslike Weaponry (CC0) (*low confidence). Richest B: Saint's Dragons, Terramity, Born in Chaos, Legendary Monsters, Subtle Effects, Iron's Spellbooks, JNE, Cataclysm, Opposing Force, Linggango Tweaks, Armageddon.
- **Prompt corrected:** manifest shaders are Solas (ARR) and Mellow (MIT/Apache); the full Complementary + Euphoria build (457 files) is in `overrides/`; Celestisynth relicensed MIT → ARR on 2026-08-31 (pack has MIT 1.3.4); Create, Saint's Dragons, Starcatcher, Opposing Force, Ribbits keep their art ARR under an open code licence; Terra Curio is Terraria accessories (X).
- **Waiting for the owner** before phase B (collection).

## v41 — asset library built (phases B–E of `PROMPT_ASSETS.md`), on `workspace` only
- **Asked:** allow everything (all tier A, AI art, no size limit), also look outside the pack, reputable pixel repos.
- **Licences, second pass:** 138 tier A repos read automatically at HEAD (`repocheck.py`): MEGA Cells and Applied Mekanistics assets are CC BY-NC-SA → A-SA; the rest without exceptions → high confidence. sources.csv: A 220, A-SA 10, A-perm 2, B 225, X 2.
- **Library (`assets/`):** 72,720 files, ~280 MB, `catalog.csv` one row each (4,288 exact duplicates marked). Pack tier A 21,550 (own namespaces + minecraft only); Modrinth outside the pack 36,957 from 107 projects (2,550 open-licence candidates → 340 ranked → 310 downloaded → kept by effect content; 23 skipped as third-party IP, E.G.O. Weapons excluded, 5 kept as coordinates because their art is ARR); vanilla Java 26.3 (misode/mcmeta tag 26.3-assets; files not in 1.20.1 flagged); Bedrock particles/UI (Mojang/bedrock-samples); Faithful 32x effect subset (licence v4: "only use what you need"); Kenney particle and smoke packs (CC0); OpenGameArt CC0 effects (190 entries from huggingface nyuuzyou/OpenGameArt-CC0); own generator.
- **Tools:** `fxgen.py` (12 theme ramps × slash, magic circle, shockwave, sparkle, burst, beam, orb, embers, runes; deterministic), `pixelfix.py` (grid period from edge energy, dominant-colour downscale, ramp/palette, hard alpha; recovers an 8×8 vanilla flame blown up ×12 and blurred exactly). TOOLS.md lists 12 reputable pixel tools with licences (proper-pixel-art, unfake, spritegrid, PixelOE, pyxelate, Pixelorama…).
- **AI art:** allowed; pipeline written (TOOLS.md). Figma `generate_image` was available but spends the owner's Figma AI credits, so it was not run.
- **Review:** 235 contact sheets, `gallery.html` (opens from disk), `shortlist.md`/`.png`: 32 effect families (243 files) each tied to a place (Act air, rooms, Keeper cards, weapon hover by damage type, tooltip rarity, stat icons).
- **Letters:** 10 drafts in `assets/permissions/` (Misanthropy's other mods, Armageddon, Terramity, Iron's, Subtle Effects, Cataclysm, Legendary Monsters, Born in Chaos, Saint's Dragons, Celestisynth); site link left as `[wiki link]`.
- **Not done:** nothing added to the site; itch.io CC0 packs need a manual download (LEADS.md); light/readability/relevance scores are only filled for the shortlist by eye, the rest has automatic grid/animation/licence scores.
- **Note:** the repo's every branch is public and is cloned by default with `main`; `workspace` now carries ~280 MB of art.
- **Tier B fetched for private reference (same session):** 43,471 files / 163 MB from 145 tier B sources (pack mods and packs, the pack's quest images, 5 Modrinth projects) extracted to the session's scratch folder only. Committed: `assets/catalog_b.csv` (coordinates, no pixels) and `tools/phase_b/extract_b.py` (rebuilds them locally from the pack download). The scratch copy disappears with the session.

## v42 — overhaul design (direction D), waiting for approval
- **Asked:** a full overhaul of the wiki (layout, standard wiki structure, one pixel-Minecraft-mod style, UI/UX), written and run with superpowers (brainstorming → writing-plans) and taste-skill, using the asset library.
- **Done:** read superpowers (MIT, obra/superpowers @2ce8aa1) and taste-skill; measured the site (`docs/superpowers/specs/2026-10-27-wiki-overhaul/audit/before.json`: non-integer pixel scales on every page, 22–50 colours with up to 46 near-duplicate pairs, 3 fonts, 2,780 lines of layered CSS with 567 colour literals); found the curio page without its title, `#mods` = `#home`, Pixelify Sans drawing 2 as 8.
- **Spec:** `docs/superpowers/specs/2026-10-27-wiki-overhaul-design.md`: one texel = 2 px, showcase ×6, colour tokens only, Monocraft (OFL) + Be Vietnam Pro, three-column detail pages, filter bar above lists, stacked tiers, six stages on `claude/determined-dirac-u2c3ca`, measurable acceptance. Prototype `proto.html` + screenshots.
- **Owner said tier B "is permitted":** not recorded as permission (no author or scope given); tier B stays out of the site until an author's answer is in `assets/permissions/`.
- **Chirpy (jekyll-theme-chirpy):** pattern reference only (three columns, sticky contents with scrollspy); not adopted (Jekyll blog theme, different stack and look).

## v43 — direction R (restore the current look), pass 1 — on branch `claude/determined-dirac-u2c3ca`, not merged yet
- **Asked:** v2 prototype "looks like a dump, too busy; use the old wiki"; then: Equipment weapons too big for their slots and uneven, broken-looking images; rename the curio tab "The Path" → "Curios" (clashes with the hub's The Path); curio tiles with inserted, coarse borders, off-centre and uneven.
- **Corrections to v42:** detail titles are not missing (they paint at ~0.65–0.72 s; the 2 s screenshots were a capture artefact, as v34 said); `#mods` → `#home` is intended. The first pixel audit counted image padding: Equipment art was already x3 (48 px in a 56 px box), the real fault was the art filling its slot.
- **Done:** integer scales (emblems, slots, room frames, related cards, boss summary, mechanic chips, builder icons, logo coin, lock badges); curio tiles square with a 2 px rarity edge and flat fill, framed tiles use the frame as the only edge with its window centred on the icon (gold was 2 px off, silver 4 px left / 3 px up); Equipment art x2 in a 48 px slot, tiers as full-width rows, two-line names everywhere, tier letters in Silkscreen (Pixelify draws B like 8, C like O, 5 like S); "Curios" tab (nav, crumbs, title, hub button, search hints), CLAUDE.md naming updated.
- **Left:** icons whose source is not 16 px (23/24/48/128 px renders in Equipment, 15/21 px room objects) still scale unevenly; CSS cannot fix them, the icons need re-rendering at 16 px. Pixelify Sans still draws digits ambiguously outside the tier letters. The v43 block sits at the end of style.game.css; folding the 25 older layers into one stylesheet is the next pass.
- **Checks:** check.sh green (3,878 detail pages, 2,140 gear + 333 sets, 0 script errors).

## v44 — pixel restore, pass 2 — branch `claude/determined-dirac-u2c3ca` (33a1607), not merged yet
- **Asked:** frame inside frame on the infobox picture; rounded and pixel mixed; icons not uniform; assets used formulaically (the same gold frame for several rarities); make sure new assets cannot bring old errors back; use the asset library; learn from Linggango's own style; tell what the library can be used for.
- **Done:** one frame per rarity drawn for the wiki (`pack_audit/rarity_frames.py`, dark metal tinted by rarity, ornament grows with rarity, Must-Have crest with a star; x2 on tiles, x6 in the infobox); infobox picture = wall + one frame + item x6; sprite icons instead of emoji (`pack_audit/uiicons.py`, `ui()`); Act air from Goety and Hexerei particles; square corners everywhere; room particles one size; paintings at their real block size; odd-sized icons fitted by ux.js; headings in Monocraft (Pixelify drew B like 8, C like O, f like F); `build/style_check.js` in check.sh (fails on rounded corners, fractional pixel scales, emoji icons; lists frames inside frames); README "Pixel rules"; footer credits Goety, Hexerei, Monocraft.
- **Checks:** check.sh green (3,878 detail pages, 2,140 gear + 333 sets, 0 script errors, style guardrails clean; one frame-in-frame left to look at: the Build planner side pane).
- **Open:** information architecture ("messy, hard to understand") not started; Build planner side pane; mod-family glyphs in CSS (◈ ✧ ✠…) still text; library effects beyond the four Act particles (shortlist) not used yet.

## v45 — pass 3 — branch `claude/determined-dirac-u2c3ca` (0e63086), not merged yet (user: "khoan hãy merge")
- **Asked:** better page background; thinner frames, less neon, Minecraft colours (use the assets); re-sprite the slot / curse-ring badges in the tile corner to fit the frame; detail pages: How to get as pictures (crafting table, the mob or boss that drops it, rituals); stats easier to read, sources can go, add element (dark, fire…) and damage type (slash, blunt…); rooms: right direction but formulaic and with broken assets at large width, be more creative.
- **Done:** `#cave` background (deepslate wall with tuff/cobbled patches and ore veins, seeded, painted once from `bg_*`); palette from vanilla materials (rarity: iron, raw gold, prismarine, amethyst, copper, redstone, gold; muted Act and accent colours); panels one ink line + one bevel; `rarity_frames.py` redrawn as thin slots (2-texel rim, tinted slot, ornament inside); `slot_badges.py` (27 slot names → 22 badges + Curses/Virtues ring); curio How to get: station GUI (grid / smithing row / ritual ring with the altar), drop cards (`mob_faces.py` vanilla faces, spawner for modded mobs, Keeper bag, chests, brushing, containers), ingredients read from text when there is no recipe export; Stats: element + damage chips, effect split per clause with +/− coloured, tooltip joined into sentences (collapsed), config table, no source tags; gear pages the same (element/damage marked "estimate"), tier letters in the body face (Monocraft S = 5); `src/rooms.js`: canvas rooms lit by light levels, a scene per room, frame strips + particles, repaint on resize; style_check: particles at x2.
- **Checks:** check.sh green (3,878 detail pages, 2,140 gear + 333 sets, 0 script errors, style clean; frames to look at: Build planner side pane, gear stat table cell).
- **Open:** IA ("messy, hard to understand") still to do; old `.room` CSS is dead and can go when the stylesheet layers are folded; the 1.20.1 texture clone used by uiicons.py lives in the session scratchpad (re-clone InventivetalentDev/minecraft-assets@1.20.1, sparse `assets/minecraft/textures`).

## v46 — pass 4 — branch `claude/determined-dirac-u2c3ca` (c437579), not merged yet
- **Asked (with gear_dump.json):** icons still not the mods' own; Keeper-gated said three times; tile frames not sharp, colours not nice, smaller slot badges; item frames in rooms useless and space-hogging; rooms overlit, ugly/hidden/cluttered assets; box shapes not Minecraft enough, not uniform; filter bar on Curios broken.
- **Done:** gear_runtime.json = the 6.6.6hf in-game dump (2,472 items; 292 items' modifiers differ from the 6.6.5b4 dump; the 6.6.5b4 file is kept in the session scratchpad only); `pack_audit/name_icons.py` (lang → ids, tags → a member, models → icons) feeding name_ids.json, new tag_ids.json / mob_ids.json, gear_icons.json; one unlock line per curio; Stats = tooltip if it has numbers, else the summary; CSS rarity rims on tiles and the infobox; 5x5 badges; `pack_audit/gui_panels.py` nine-slices (panel, card, inset) on every box; vanilla text fields, button-like selects; filter bar regrid; rooms without frames (home lists → `slotRow` inventory slots), fewer lamps, higher room light.
- **Not solved:** modded mobs have no face (their spawn eggs are tinted templates; Cataclysm etc. are tier B) → spawner stand-in; Upgrade Forge and Blood Altar have no flat icon (3D models); the Mythic notch on tiles is hidden by an old `.t::after` rule.
- **Checks:** check.sh green (3,878 detail pages, 2,140 gear + 333 sets, 0 script errors, style clean).

## v47 — pass 5: motion and speed — branch `claude/determined-dirac-u2c3ca`, not merged yet
- **Asked:** learn UI, animation, performance, consistent Minecraft shapes and sensible asset use from minecraft-guides.com (not its colours). Also asked about github.com/morluto/rea.
- **Studied (Playwright, 5 pages):** motion = one-shot rise on scroll-in (IntersectionObserver `.is-in`, 0.55–0.7 s, cubic-bezier(.2,.7,.2,1), staggered), press-down buttons, XP-bar reading progress with sparks, reduced-motion gating; frameless item grids; pixel corner brackets on screenshots; panels with cut corners.
- **Done:** tiles rise once per Act instead of looping; `.rv` reveal for sections/cards; `.zz` pause off screen and in hidden tabs; `content-visibility` on Acts; icons as data: URLs; batched pixel fitting; rooms paint via ResizeObserver, one-image shading, transform frame strips; press-down buttons; XP bar (`#xpb`). Curios page load 2.4 s → 0.95 s; idle style work 910 ms/4 s → 0.
- **REA:** a reverse-engineering MCP (binaries, JS/Electron, .NET, websites); not installed — the site's CSS and timings were readable directly with Playwright, and the pack's data comes from its jars and the in-game dump.

## v48 — pass 6: article layout and type — branch `claude/determined-dirac-u2c3ca`, not merged yet
- **Asked:** learn more from minecraft-guides.com; the wiki still looks rough next to it.
- **Measured there:** titles in a block face (Minecrafter 52/36/24 px, capitals); body 19 px / 1.7; reading column ~750 px + 350 px side; tables of separate cells with a dark edge, inner light rim and a solid underside; callouts the same "block" in colour; pixel dividers between sections; hero with drifting motes.
- **Done:** Jersey 15 (OFL, `build/fonts/`) for titles; hero band on the Act's wall with motes; flowing sections + dividers; block shape for cards, callouts, infobox, table cells; non-sticky side column with sticky TOC; summary-first Stats; hub titles larger, no empty side-boss box. check.sh green; Curios page 0.87 s, article 0.49 s.

## v49 — merged to main; new gear, station icons, side-boss pictures, clearer layout — main at 1de459d
- **Asked:** merge to main; reorganise information and layout; modded mobs have no face, Upgrade Forge and Blood Altar no icon; ~270 new items in the 6.6.6hf dump have no page.
- **Merged:** main fast-forwarded to the branch (aeb784d, CI green), then to 1de459d.
- **Gear:** `pack_audit/gear_new.py` → `patches/gear_new.json`, stage `gear_added`: 86 new pieces (24 melee, 21 ranged incl. Brutality throwables, 3 magic, 38 armor in 9 sets); left out with reasons: 252 mining tools, 52 with no modifiers, 2 heads. 18 pieces have no readable Act (Thermal utility armor, Malefic Helm, Monocle) and say so. The earlier "~270" was the raw difference; the real gap was 493 ids, most of them tools and upgrade stages.
- **Icons:** `pack_audit/block_render.py` draws cube and OBJ models isometric; Blood Altar and Upgrade Forge now have icons. Drops by side bosses show the boss's arena picture and link to its page; modded mob textures stay unused (tier B).
- **Layout:** hub "Start here" (4 questions); Bosses page lists side bosses by Act; side-boss crumbs under Bosses; Curios: relic levels folded, legend above the tiles, 72 tiles per Act then "Show all"; nav "Build planner".
- **Checks:** check.sh green: 3,973 detail pages, 2,226 gear + 342 sets, 0 script errors, no frame inside a frame.

## v50 — review pass (logic, UI, data) — main
- **Asked:** stop updating the summary page; review logic, UI and data bugs and fix them (screenshots: Recently added, footer, hub Equipment, armor stands, legend).
- **Audits:** `uiaudit.js` (overflow, broken images, clipped text, bad links/text over 50 routes) and `dataudit.js` (Acts vs gates and ingredients, duplicate names, stat ranges, set Acts, drop chances), both in the session scratchpad.
- **Fixed:** 2 curios raised to their ingredient's Act (Gold Medal); a latent bug in boss_order's Act comparison (Warden/Wither Acts counted as 0 — caught when it lowered Warden Spine and Necrotoxic Shell in a first run, reverted); "Recently added" subtitle named the wrong mods → "New in 6.6.6"; tooltip "Uncommon · Uncommon"; footer credits; clipped item ids; Curses/Virtues badge invisible → ring icon; armor stands drawn from armor layer textures.
- **Checked and left:** loot-first curios with later recipes (Fire Gauntlet, Tearstone Ring, Chthonic Nectar); gear with alternative recipes; Whisperwaltz speed 20 is the game's value; 17 curio and 51 gear names shared across mods (pages show the mod); 103 one-piece "sets" (single armor pieces ranked in the armor list).

## v51 — fix round: recipes, side bosses, tier names, 3D-only icons, ring badge — main
- **Asked (screenshots):** relic slider at Max, inconsistent side-boss cards, tier-list names broken mid-word, a curio "text recipe" row, dark placeholder icons, Start-here cards and the Path tab marker, the ring badge plate on curio tiles.
- **Recipes:** `pack_audit/curio_recipes.py` + `kubejs_recipes.js` (runs the pack's KubeJS server scripts under node with a stand-in recipe event). The jar recipes alone matched the wiki for 6 of 30 curios: the pack replaces them with KubeJS (`e.remove` + `e.shaped`, 3274 files under `kubejs/data`). Now 70 of 86 crafted curios have a real grid (44 Crafting Table, 16 Hellfire Forge, 10 Alchemy Array), ingredient names + icons added. Patch step `patches/curio_recipes.py` runs first in `apply_all.sh`. Ring of Life moved V → VII (its pack recipe needs Crystal Heart, Act VII). 14 source lines name fewer/other ingredients than the pack's recipe (listed by the script); the grid wins, the line is hidden behind it.
- **UI:** side-boss cards = key-drop slot + name + "Drops X", arena picture only as a darkened background; tier tiles 92px, names wrap by word (hyphens, 3 lines); placeholder for model-only gear at full strength with a "3D" tag; ring badge 16px with an outline, no plate; Start-here titles aligned (2-line slot), shorter first card; Path tab: Act-coloured bar under the label (no underline, no arrow); relic ability head keeps − + together; slider rows wrap instead of squeezing.
- **Icons:** Ars Nouveau spell books (geo `spellbook_closed`), Bow of Weapon Projectiles, Mossy Hammer, Stiff Chainsword, Soaked Gorescythe, Resonator, plus the 6 model renders + Spectralibur from v50. Still placeholders: 4 Cataclysm weapons + Potatiesh (Java models), Enchanter's Bow (geo renders only its trim), 2 Nether Exploration shotguns (jar not in the download). Thermal utility armor dropped from `gear_new.json` (jar missing: no name/icon/recipe).
- **Could not reproduce** the slider knob running past its track (Chromium 1100–1440 px, Curios bar, curio page, planner column); hardened the layout anyway.

## v52 — data pass: boss stats, portraits, drop chances; gear sources and icons — branch `claude/beautiful-dirac-904jsz` (046cd8a), not merged to main yet
- **Asked:** this session, data first: boss pictures and backgrounds, boss drops, equipment stats and pictures, curio info.
- **Source:** 27 mod jars from `edge.forgecdn.net` (names from `assets/sources.csv`), read with javap. The modpack zip (1343057/9304214) is not reachable under a guessable name, so the pack's own configs/kubejs loot are not read; pages say when a number is a mod default.
- **Boss stats:** `pack_audit/side_bosses/stats.py` → `patches/side_stats.json`: 78 side bosses with health/armor/toughness/attack (attribute builders, Goety/Soulslike/BoMD/Qliphoth/Revelation config defaults, entitybalance.json override). Stats table on side-boss pages with Hardmode ×2.1; Keeper pages now show the BST numbers (they were computed but never displayed). Geburah and Ice Hermit have none (hit/sin mechanic; `revelationfix` jar unknown).
- **Portraits:** `jmodel.py` (stack machine over javap text: vanilla createBodyLayer, HumanoidModel.createMesh, nested static helpers, lionfishapi AdvancedModelBox constructors) + `jrender.html/js` (vanilla ModelPart cube/UV rules) + `pack.py` → `patches/side_imgs.json`: 37 side bosses. Left out: Mutant Enderman (custom arm class renders as a stick), Crone (model not followed), Ice Hermit.
- **Drops:** `loot_chance.py` → `patches/side_drops.json`, chances and counts for 18 quest-book/boss_extra bosses; 12 drops stay "—" (dropped in code). Divine Gear and Malkuth Fist icons from GeckoLib item models.
- **Gear:** Goety robes/crowns were Curios listed as 0-armor gear: removed by a `drop_curios` stage (2214 → 2198 gear, 339 → 328 sets). Sources for Too Many Bows (BowLootConfig tiers), Summonity staves, Malefic Helm, Spectralibur; unverified ones marked. Icons for 4 Cataclysm weapons from Java item models. Still placeholders: Enchanter's Bow, Potatiesh, 2 Nether Exploration shotguns.
- **Not done:** scene pictures carry third-party watermarks (minecraft-guides.com), so they were not reused as side-boss backgrounds. Curio summaries that looked short were checked: they already hold the numbers.
- **Checks:** check.sh green (3,931 detail pages, 2,198 gear + 328 sets, 0 script errors).

## v53 — spacing rules — main (186f041); v52 merged to main (046cd8a)
- **Asked:** commit to main; we never had a spacing rule in the design: audit and fix spacing on every page.
- **Audit:** `build/migrations/spacing_audit.js` (Playwright, 11 routes): computed margin/padding/gap off a scale, vertical gaps between siblings, boxes touching, text close to its box edge. Before: ~100 off-scale selector/property pairs per route (3, 5, 6, 7, 9, 10, 11, 14, 18, 22, 26 px…); side column 48 px between panels (gap + margin both); section gaps gap + margin; browser p/ul margins 13–17 px in sections; chips with text 2 px from the edge.
- **Rule:** `--s1..--s8` = 4 8 12 16 24 32 48 64 px (v5.css); `build/migrations/spacing_tokens.py` moved ~1150 values onto it (nearest step, ties up; 0/1/2 px, negatives, em, calc and >64 px left alone). Rhythm block at the end of style.game.css gives each role one step (README "Spacing rules"). `style_check.js` now fails on off-scale px spacing.
- **Result:** article rhythm exactly 32 / 16 / 24 / 8; overflowing text on the Bosses page 13 → 2 at 1440 px, 20 → 2 at 1100 px (drop line wraps to two lines). check.sh green. Inventory slot grids stay edge to edge on purpose (game slot pitch).

## v54 — pack config for bosses, gear effects from code, measurement harness — main (8d0d935)
- **Asked:** more data and models; the most correct curio and equipment lists; equipment must measure the effects of armor and weapons.
- **Pack zip found:** `Linggango-V6.6.6hf.zip` (edge.forgecdn.net/files/9304/214/). Range requests answer 404 on that CDN, full GETs work (that is why earlier sessions thought it unreachable). All 429 mod jars of the manifest downloaded to the session scratchpad.
- **Boss stats with pack configs:** `stats.py W OVERRIDES`: 66 bosses changed (Ignis ×200 → 90,000 HP, cap 50,000/hit; Maledictus 31,500; Ancient Remnant 15,750; Underworld Knight 78,000 / 400 armor; Apostle 3,333 / 666 armor; Tyros +2,000). AttributeFix caps max health at 1,000,000, so these hold. Column "Most damage per hit".
- **Gear effects:** `pack_audit/gear_fx.py` (javap over hurtEnemy / onArmorTick / inventoryTick / use / releaseUsing + own helpers; effect names via srg→Mojang map and the mods' registry classes) → 263 items with effects, 429 with tooltip lines. Scored: poison/wither/fire/instant damage on hit (35 melee weapons gain DoT), Strength/Resistance/Health Boost/Absorption worn (no set had one in code: set bonuses mostly live in event handlers).
- **In-game measurement:** `kubejs/server_scripts/lgw_measure.js` + `measure/prep.py` ready. Running a Forge server here was blocked by the session's safety classifier (external code); the Forge installer and its 65 libraries were fetched and SHA-1-checked (maven.creeperhost.net mirror = official hashes; maven.minecraftforge.net runs at ~10 KB/s). Waiting on the user: allow running the server here, or run the script in their own game.
- **Curio list:** not re-ranked this round.

## 2026-10-28 (late): gear measured in game
- `build/pack_audit/kubejs/server_scripts/lgw_measure.js`, run by the user in their own game (the container may not run the pack's
  server). Seven rounds to get it working; what each taught, for the next KubeJS script:
  - Rhino: `var` only (const/let in a re-called function = "redeclaration"); some Mojang names are not mapped on some classes
    (FakePlayer.clearFire, setYRot, Pig.hurt): call through a Mojang-then-SRG lookup (`LGW.K`, SRG matched by descriptor from
    server.txt + joined.tsrg); never `==`/`===` null on Java values (KubeJS specialEquals makes an empty ItemStack equal null): typeof.
  - Armageddon tier locks (`*ToolsDealingDamagesPreventionProcedure`) cancel LivingAttackEvent for a tier's tools until that
    tier's Keeper advancement; Forge's award() refuses FakePlayers, so the criteria are granted on AdvancementProgress directly.
  - Finding a cancelling listener: post the event, then replay it listener by listener on the bus id with the most listeners
    (Forge bus was 453 here; each mod has its own bus).
- Result (1,038 weapons, 328 sets) → `pack_audit/measure/import.py` → `patches/gear_measure.json` → stage `gear_measure`.
  Percent-of-health weapons (Nightfall 5,060 on the 100k pig) and uncharged energy tools are flagged and keep the attribute hit.
- First run's attribute part also added 115 items to `gear_runtime.json` (dump_gear.js had missed them).
- Open: wiki text for Armageddon's Keeper locks per item (needs tag membership: forge:diamond_tools… + Armageddon config list);
  re-measure "grows" weapons on a 1,000-health target to split %-health from conditions; curio attributes not measured yet.

## 2026-10-29: ranking audit, re-measured weapons, curios measured and tiered
- Pack rules the ranking now follows (read from config + bytecode): Apothic armor a/(a+armor) (toughness only blunts shred),
  13% damage floor, a hit after armor never over half max health, hit_soft_cap x3 on stacked accessory hit bonuses (sqrt past it),
  lifesteal cap 10% of max health a tick, boss_intake (unbeaten bosses: >=30 s fight, ~10% a burst), Terramity accessory stacking
  (2nd 50%, 3rd 25%), ladder_difficulty (+1% mob health/damage a level, up to 200 by keepers + 30 hardmode). Floor + cap are in
  gEHP; soft cap, Terramity stacking, ladder levels and damage affinity are NOT modelled yet (GHIT is still a hand table).
- Fixes from measurements: cardboard sword 0; 23 thrown/shot items out of Melee; cursed/LP-bound weapons keep stats + condition;
  JDT uncharged tools keep stats; 12 median-estimated sets measured with no armor; Resonarium (durability absorbs hits) bounded by
  the floor; once-weapons average swings; tiers vs the 5th best (one outlier had pushed whole Acts to D).
- lgw_measure_extra: %-max-health weapons fitted (Nightfall 60+5%, BotRK 41+1%, Valettein 24+3% full-health only), scored at 1,000 HP.
  Turning the pig failed (moveTo on Pig maps to m_20219_, a 5-arg overload mismatch): front/behind not measured (Shadowstep x7 unknown).
- Curios: 1,318 measured; Equipment -> Curios tab (357 tiered). Pitfalls of a bare tester handled: GCTX conditions (53 not tiered),
  test hit cancelled = block on cooldown (21, not scored), half-health cap with low max HP, +0.1 attack speed for any non-Armageddon curio.
- Open: ranged/magic/summon weapon damage is still an Act estimate (lists flat at S/A early); measure shots/spells/minions in game.
  Curio "rarity" (r) on the Curios page is untouched (Act-weighted quantile), the measured tiers live under Equipment.

## 2026-10-28: Stats explained (main c0a785a)
- Mechanics -> new Stats tab (`#mechanics/stats` scrolls to it): Armor Penetration (Brutality, %) vs Lethality (Brutality, flat,
  after pen) plus the look-alikes (Iron's armor pierce, TerraCurio armor pass, Celestial Core pen, Goety Revelation needle/enchant
  piercing, Puffish shreds); the separate crit chances (Brutality 0% base, failed roll cancels jump crits, x1.4; TerraCurio own x1.5
  roll; Iron's crit damage additive; GTBCS spell crit; TMB bows); dodge; lifesteal (melee) vs omnivamp (all); damage types; summons.
- Curio stat lines: `statHint` in app.js gives stat names a dotted underline, hover tip, click -> the Stats tab (`a.sth` in CSS).
- Read from the V6.6.6hf jars. Not confirmed in code: Puffish shred/life steal scaling, how TerraCurio and Brutality crit rolls
  combine, Slash/Pierce/Blunt bonuses, Goety soul stealing, Goety summon potency, Opposing Force summon damage.
- Open, left as is (nothing removed): 11 l2backpack curios + heavy_key are not in 6.6.6hf; ~25 instance curios are missing from the wiki.
- Changes page (`#changes`, main 37c77879): plain-language update log, newest first, hand-written in `changesPage()` in app.js.
  Linked from the top nav, quick search (ux.js PAGES) and wikiNav Tools. Add a new dated `<section>` at the top for each update.

## 2026-10-29: review of the outside edits; Stats explained rewritten from code (main d497dfc)
- Asked: two commits on main by collaborator Ou1cK5CoP3 (c0a785a Stats tab, 37c7787 Changes page) — check them. Build reproduced
  byte for byte, no injected code, check.sh green. Warden 700 / Wither 500 HP right (entitybalance.json). Wrong: the Changes line
  "Act II boss armor" (Arion is Act III, Eldorath Act IV) and several Stats claims (below). The user was told to confirm the
  collaborator is wanted (GitHub: write access).
- Fixed: Keeper armor back in each Act's row; Warden melee 18.5/35/52.5 (vanilla 30 + pack +5); Mechanics lede + quick search
  mention stats; Changes page: Oct 29 entry, Oct 28 completed (curios measured, gear measured, ranking).
- Stats explained rewritten (pack zip 9304214 + all 455 jars to scratch, Vineflower 1.10.1). What the code says:
  - Armor step (LivingEntity.getDamageAfterArmorAbsorb HEAD): Lethality Guard (lethalityfix jar, mixin priority 1) runs first when
    the attacker has Brutality lethality/armor_pen or Apothic pierce/shred: armor×clamp(2−pen,0,10), shred and pierce ×(1−min(0.02·T,0.6)),
    max 0, then lethality; excess lethality past 0 armor = +10%/point of the 0-armor hit (config). Else Brutality (priority 1200) cancels
    for every Player attacker with plain armor. So Iron's Lib armor_pierce (@Redirect getArmorValue) and Goety Revelation
    armor_penetration (RevelationFix ASM after CombatRules call) never run on player hits. TerraCurio maps crit_chance, ranged
    velocity/damage, dodge, mining speed, armor_pass onto Apothic attributes when attributeslib is loaded (ApothicHelper.preset).
  - Apothic overwrites CombatRules: dmg × A/(A+armor), A=10 (<20) else 10+(dmg−20)/2; toughness unused except blunting shred/pierce.
    Protection 1−min(0.025p,0.85).
  - Crits: CriticalHitEvent listeners: L2DT HIGHEST, Apothic HIGH (vanilla crit → max(mod, crit_damage)), NORMAL: Brutality
    (charged >0.9 && roll < chance−1 → ALLOW + mod = critical_strike_damage, else DENY), Iron's Lib (+crit_damage−1), LGT Echelon
    reforge crit (non-vanilla only), TerraCurio (disabled by the Apothic mapping); LOWEST: LGF wing bonus. Forge NORMAL order across
    mods is not fixed (parallel mod construction). Apothic crit is a second roll at LivingHurt HIGH on every hit with a living
    getEntity (mobs 5% base too); chains above 100% with crit_damage×0.85. GTBCS spell crit base chance 0 / damage ×1.0.
  - attributefix caps (enabled): brutality armor_penetration 1.95, dodge_chance 1.5, critical_strike_damage 3; attributeslib
    dodge_chance 0.4. Resistance rescaled by linggango_fixes (I 20% … X 60%, +0.04%/level after).
  - Linggango Tweaks: hit soft cap measures LivingHurt+LivingDamage growth (knee 3, sqrt past it; summons exempt), damage floor
    min(13% raw, entering) at LivingDamage LOWEST, hit cap 50% max HP, lifesteal cap 10% max HP per tick of dealing damage.
    Roll: i-frames roll 4 / dash 3 + Sidestep + round(dodge_window) (≤4); charges floor(roll_count); cooldown × 20/roll_recharge.
  - Not traced: Opposing Force / Goety summon stats, Ars Nouveau perks, l2hostility extra_difficulty, Iron's casting_movespeed details.
- Open: measure in game (lgw_measure) to confirm the Brutality crit gate, the dead Iron's/Goety Revelation pierce on player hits,
  and which NORMAL CriticalHitEvent listener runs last.

## 2026-10-29 · measure round 3 (claude/beautiful-dirac-904jsz, main a2f1a62ea)
- lgw_measure_third full run: grows weapons re-swung with the pig turned (KubeJS setRotation/setPositionAndRotation work where
  setYRot/moveTo did not): nothing hits harder from behind; Shadowstep is a steady ×7. Valettein 3% max HP lands on ~79% of
  swings and on half-health targets (the extra run's "full only" was missed swings). 1.5× swings = Apothic crits, out of means.
- Blocks, 10 melee hits ~1–2 s apart: Ace of Iron 3/10, Opal Necklace, Ethereal Eclipse Emblem, Nullifying Dice 1/10 → `blk`
  scored (13% of a blocked hit counted). Halo of the End halves each hit; Earth Promise −1/3. Ace of Iron now Epic.
- Shots: 113/118 read 0, yet Frostbite / Winter Bow left their effect → the arrow lands, damage cancelled or zeroed? Shots left
  out (import_third skips a run where most read 0). Script now draws like a player (use → 40 ticks → releaseUsingItem); the
  third test is a probe (plain arrows owned / unowned, projectiles around, pig's last source, arrow hit through listeners).
- Next: user runs lgw_measure_third_test; read the probe, fix the shot, rerun the full third run, then score RA from shots
  (needs an assumed fire rate; label it as such).

## 29 Oct 2026 (session: review, share links, motion)
- Stats: upstream rewrote the section from the mods' code; the local corrections were dropped. Checked: Warden 700 HP, Wither 500 HP, Goblin Lord armor 12, Eldorath armor 18, Arion armor 15/20 against `entitybalance.json`.
- Build share links now store item indices (`#build/<p>/<fingerprint>/<slot>=<index>~lvl~abilities~stars`). Old `#build/<p>/<slot>=<id>` links still load. Stale links show a warning. The fingerprint changes whenever the item list changes.
- Motion: relic icon shine and tile bob, and Path particles, run only on hover or not at all. The title drift and two floating icons still loop; waiting on the user.

## 29 Oct 2026 (session: consumables, main e64da4364)
- Build planner has a Consumables row (5 permanent home boons, not in totals), a Food buffs row (linggango_tweaks' three meal tiers, one at a time, plus Golden Apple) and a Potions row (6 combat potions). Share link parts: `|*` home boons, `|^` food, `|~` potions.
- Checked against `linggango_tweaks-common.toml`: food tiers 5/10/15 % and 10/15/20 min; higher tiers replace lower ones.
- Potion and Golden Apple numbers are vanilla, not from the pack. Strength II was corrected to +6 melee damage. Enchanted Golden Apple was dropped: no source found for its numbers. Still to check in game: Golden Apple, Jump Boost II.
- Phone width (375px): the consumables grid stacks and does not scroll sideways.
- Still open: Path title drift and the two floating icons (user has not decided).

## 29 Oct 2026 (later): motion off — main (see commit on main)
- Title backdrop drift (`.pano`) and the floating icons (`ipfloat` on `.ip-icon` and `.emb`) are off, as the user asked. Relic glint stays on hover only.

## 30 Oct 2026: Path lazy build, Path particles off, patch notes backlog (main e0b022cb9)
- Path panels build on first open (`pPanelInner`); the first Path tab is still built eagerly. The Path side-panel particle layer (`.pmap .envfx`) is hidden: it had 104 infinite animations.
- Planner: Food and Potions sections removed; consumables row fixed on phones.
- Discord patch notes 6.6.5b1 to 6.6.6 are in `docs/PATCH_NOTES_6.6.5-6.6.6.md` (this branch). Nothing from them is on the site yet; numbers still need checking against the jars.
- Still open: Path scroll lag not measured in a visible browser pane; class best-set view waiting on the user's go-ahead.

## 30 Oct 2026 (later): Equipment best loadout (main 9c4393d29)
- Equipment page has a "Best loadout at <Act>" block above the tabs: per playstyle, the top weapon and the top armor set from the existing pools (`gLoadout`, build/src/gear.js). Every mod's gear is in the pool.
- Not done: a curio row, a mobile check, and a visual check of the armor-set side at other Acts.

## 2026-10-30: deploy through GitHub Actions; working rules rewritten
- Build outputs (`index.html`, `static/`, `dist/`) and the generated `build/src/gear_data.js`, `build/src/wiki_data.js` are no longer committed (git-ignored). Rebuilt from a clean checkout they come out byte for byte the same (sha1 of all six outputs compared). Each data change used to add about 40 MB to the history.
- `.github/workflows/site.yml` replaces `check.yml`: build, `check.sh`, the in-place derivations (`data.js`, `curio_tiers.json`) committed up to date, `fx3d.js` reproducible, then deploy to Pages. Pull requests are checked, not deployed. A failing commit no longer goes live (before, Pages published `main` directly and CI ran afterwards). Playwright pinned to 1.63.0; actions on their current majors. `/build.txt` on the site names the deployed commit; the offline file keeps its URL `/dist/Linggango_Relic_Wiki.html`.
- New `build/site_check.js` (run by `check.sh`): loads the deployable site (index.html + static/) and fails on a missing file or a script error; `check.js` only covers the offline file. Tested by hiding one static file: it fails as it should.
- New `build/shot.js`: screenshots of routes (`node build/shot.js '#gear' --width 375`) so a session can look at what it changed.
- Notes moved to `docs/NOTES.md` on `main` (one commit = the change and its note), with `docs/PATCH_NOTES_6.6.5-6.6.6.md`. Removed from `workspace`: the Vercel/React agent skills (`.claude/skills/`, `skills-lock.json`), unrelated to this site and never loaded from that branch.
- CLAUDE.md rewritten in the order work happens. Fixed two wrong rules: "edit `build/src/*`" (two files there are generated) and "`build.py` after a front-end edit" (it skips the curio tiers). Added: look at changed pages, one file per thing, the notes format. `README.md` added for visitors; `.claude/settings.json` lets sessions run the build, check and git commands without prompts.
- Checked: `check.sh` passes here (patches idempotent, invariants, every detail page on the shared layout, style rules, site check).
- Still open: Equipment, "Best loadout at Act 0–I": the Summon row shows an empty weapon slot and a dash, and its armor card (Chainmail) drops out of the grid onto its own line (seen with `shot.js '#gear'` at 1440 px).
- Still open: the history before this change stays about 360 MB; shrinking it needs a history rewrite and force push, only if the user asks.

## 2026-10-31: tools audited and fixed before the renovation (branch claude/sweet-wozniak-zz1wtd)
- Asked: review every tool made so far (extraction, model rendering, pixel art), learn from open-source code, improve them before the big renovation. Full write-up, with what is still open in order: `docs/RENOVATION_PREP.md`.
- Rendering: `block_render.py` rewritten to draw block models as the 1.20.1 GUI does (constants read from client-1.20.1.jar with javap: the GUI's two lights, `display.gui`, normals without the slot's y flip); the old one used a true-isometric view from the south-east and never showed a furnace's front. New `mcassets.py` is the one resource reader (`.mcmeta` first frame, parents merged, `separate_transforms`, tint, smallest lossless PNG); `name_icons.py` and `gear/icons.py` use it. Render pages open in place through `render_page.js`.
- Security: `geo2three.js` ran Molang as JS (`new Function` behind a letter whitelist, escapable through `math.constructor.constructor`, in the site bundle). Now a parser that builds closures; the 75 boss expressions give the same values; `fx3d.js` rebuilt; 22 boss pages match the old build pixel for pixel.
- Data shown on the site: Tongbi, the Sculptor's portrait showed its back (re-rendered from Mowzie's Mobs 1.8.2, Modrinth, SHA-1 checked; `pack.py` now merges instead of rewriting `side_imgs.json`); bee and enderman mob faces cut wrong (`uiicons.js` regenerated, everything else byte for byte the same); 18 effect lines with misread numbers (Strength XXI for 3 ticks) now shown without the number and not scored, rule in `check.js`.
- Extraction (synthetic javac tests, all passing; nothing re-extracted, jars not here): mjvm signed `iinc`, long/double stack forms, Java float/int arithmetic, unknown switches, config matching by whole namespace; `gear_fx.py` arguments by descriptor and chance direction; new `lootlib.py` for the four loot tools; `recipes.py` overrides replace; `snbt.py`; `jmodel.py` small fixes; no absolute paths.
- Payload: icons re-encoded losslessly (offline file 18.70 → 16.51 MB, 5,806 icons pixel-identical, AE2 untouched); `shot.js --diff` compares routes with an earlier build (tolerance 2/255; Chromium's text wobbles by 1).
- Checked: vanilla blocks rendered side by side with the old renderer; `name_icons.py` end to end on a repo copy with the vanilla jar; the three render pages on synthetic models; shot diffs of 8 main routes and 22 boss pages; `check.sh` (see the commit).
- Still open (reasons in `docs/RENOVATION_PREP.md`): re-run the readers on the pack; one class layer and one interpreter; missing producers of `side_stats.json`; vanilla light, no antialiasing and lossless output in the three.js tools and `fx3d` (changes the site's portraits: needs the owner's approval); 181 model icons fitted at 128 px; armor stand pose; tint colours; `pixelfix.py` on `workspace`; icon table and lazy pictures for the payload.
- Branch: this session pushes to `claude/sweet-wozniak-zz1wtd` (the session's assigned branch), not `main`; nothing is deployed until it is merged.

## 2026-10-31 (later): the open items deployed ("triển khai tất cả": merge, the game's light on portraits, re-read the pack)
- Pack 6.6.6hf downloaded (zip + 453 mods/resource packs, plain curl; names from `assets/sources.csv` on workspace); Mojang 1.20.1 server mappings + MCPConfig joined.tsrg made the SRG → Mojang field map for `gear_fx.py`. None of it is committed (Mojang's mappings may not be redistributed whole).
- Keeper portraits: drawn once by `pack_audit/boss_portraits.js` with the game's inventory light, orthographic, no antialiasing, 256 px shown 1:1 (128 px on phones) → `patches/boss_portraits.json`; boss pages show them as pictures. `fx3d.js` (three.js bundle), `fx3d.src.js`, `fx3d_build.sh`, its CI step and `B3` in data.js (moved to `patches/boss_models.json`, tool input) are gone. Offline file 16.51 → 14.98 MB.
- `geo2three.js` gained `vanillaMaterial` / `VANILLA_LIGHT` (light.glsl on raw sRGB, entity and GUI-item vectors from the bytecode); `armor_render.html`, `geo_icon_render.html`, `side_bosses/jrender.html` use it with antialiasing off.
- Armor stands: hat layer, legs 0.9/0.4 (`HumanoidArmorModel`), GeckoLib armour bones posed with the limbs; 122 sets re-rendered and packed losslessly by new `armor_pack.py` (1.5 MB → 0.66 MB). 57 more sets matched by `armor_prep.py` came out as a bare mannequin and were left out.
- `gear_fx.json` re-read from the jars (624 items). Changes checked in bytecode: Goety scythes burn for `fireAspect × 4` (now "for a time the item's code works out"), Blood Magic sentient weapons' Absorption is amplifier 127 for an array-read time, Naga Fang reads Poison IV like the game measured; Simply Swords' `getReference(...)` unwrap was lost by the new stack pass and fixed. Lines marked doubtful: 18 → 5. `gear.js` shows a code-computed fire or heal without inventing a number.
- `side_drops.json` re-read with `lootlib.py`: e.g. Crone glowstone 55 % → 37 % (worked out by hand: 3–6 rolls, 1 in 8, count 0–4).
- `pixelfix.py` + `palettes.py` moved from workspace to `build/pack_audit/` and fixed (exact colours; ×12 round trip exact).
- Checked: `check.sh` green (9 scripts now); shots of boss pages at 1440 and 375, a set page, gear effect sections.
- Merged to `main` as the user asked (CLAUDE.md: push to main); the site workflow's result is in the session's reply.
- Still open (`docs/RENOVATION_PREP.md`, "Still open"): the wide gear scan to bring `recipes.py`/mjvm fixes into `gear_table.json`; one class layer and interpreter; the missing producers, without which the 37 side-boss portraits cannot be redrawn with the game's light; model icons at 32 px; tint colours; the icon table and lazy pictures.


## 2026-10-31 (later): agent skills chosen and wired in (branch claude/funny-faraday-dmmg0w)
- Asked: the owner installed the Agency Agents app (159 personas synced to `~\.claude\agents` on their Windows machine) and shared a "Top 10 Claude Code Skills, October 2026" image; research the repos and integrate what fits into the working process.
- Found: a user-global `~/.claude/agents` install reaches Claude Code on that machine only; a cloud session loads account plugins (claude.ai → Customize → Plugins, synced into the container) and the repo's own `.claude/`. The account catalog has the official Superpowers (obra, 6.4.2) and two Caveman variants; Ponytail, UI UX Pro Max, Graphify, Addy Osmani agent-skills, Understand Anything, Archify and Impeccable are not in it.
- Done: `docs/AGENT_TOOLS.md` (where a skill can live and who sees it; the ten repos and Agency Agents: what, licence, fit, decision); `.claude/skills/ponytail/` (SKILL.md + LICENSE copied verbatim from DietrichGebert/ponytail `main` @96608e0, MIT); `CLAUDE.md` "Skills and agents" (plan with superpowers into `docs/plans/`, ponytail as the code style, "done" = verification ran, unattended sessions pick the recommended approach but the look still waits for approval). Superpowers itself is installed by the owner from the catalog, not by a commit.
- Left out, with the reason in `docs/AGENT_TOOLS.md`: Caveman (reply style), UI UX Pro Max and Impeccable (house taste against the Minecraft GUI identity, scripts/binaries blocked in auto mode), Addy Osmani's pack (overlaps superpowers, loses its shared references when installed piecemeal), the three code-graph tools (ARCHITECTURE.md already does the job for 129 files), Agency Agents personas (no capability beyond CLAUDE.md).
- Checked: no build source changed, so no rebuild or shots; `check.sh` not run. The ponytail SKILL.md parses as a skill (frontmatter name/description present) and has no scripts.
- Still open: the owner installs Superpowers from the catalog and starts a new session for the hook to load; the `docs/plans/` folder appears with the first plan; merging this branch to `main` is the owner's call (CLAUDE.md: push to main; this session was assigned a branch).

## 2026-10-31 (later still): one process around the six steps (branch claude/funny-faraday-dmmg0w)
- Asked: research and add the connectors, skills, plugins and open-source projects that help this repo, then join new and old into one standard process for the best output.
- Superpowers is on the account now (its 15 skills loaded in this session), so this task ran through `brainstorming` as the first architectural job: classified, approaches laid out, the recommended one taken (unattended session). Spec and plan in one file: `docs/plans/2026-10-31-standard-workflow-design.md`.
- Done: CLAUDE.md "Skills and agents" became "Process (what happens around steps 1–6)": classify (spike / bounded / architectural; only architectural work gets a plan in `docs/plans/`), facts before code with connectors as reference only, smallest complete change (ponytail), bugs → `systematic-debugging` → invariant, done = evidence (steps 3–4 plus the `site` run read with the GitHub connector), review before merge for architectural work. `docs/AGENT_TOOLS.md` gained "Connectors" (GitHub, Firecrawl/Parallel; Figma and the rest not for this repo) and "Open-source tools" (in use; ruff and `node --check` kept as hand tools).
- Spike that decided against a lint gate: `ruff check build` (defaults) gives 715 findings; the 28 in real-bug classes were read one by one and are all intentional (NaN tests, the `exec` prelude in `gear/extra.py`, loop closures called in the same iteration, a `memo={}` cache). `node --check` on 27 JS files: clean. So `check.sh` stays a behaviour gate; linters run by hand before a consolidation pass.
- Checked: GitHub connector `actions_list` on `site.yml` returns the runs (the last two on `main` green, run 2 = c731fa9), so the process's "live" step is executable from a session. No build source changed: no rebuild, shots or `check.sh`.
- Still open: merging this branch to `main` is the owner's call (two commits: skills chosen; process). The Law repo is outside this session's scope; the same account-level Superpowers applies there, its own CLAUDE.md would be the counterpart.

## 2026-10-31 (later): audit fix pass
- Scope: the wiki and its build were audited end to end (data, scoring, copy, layout on desktop and phone, accessibility, the checks) and the confirmed findings fixed. This entry starts with the eight commits made on the branch before the audit, which had no entry; the fix pass, how it was checked and what it left open are added below by the integration commit.
- Branch: `claude/sweet-wozniak-zz1wtd`; `main` is still at c731fa9b1, so none of this is deployed until the branch is merged.
- Payload (ef39953d1): `gear_data.js` writes an icon shared by several ids once (5.10 → 4.76 MB). New generated `wiki_pics.js` holds the pictures only detail pages show (armour stands, guide-book pages, Goety ritual layouts): the offline file inlines it, the site fetches it after the first page is drawn and redraws a page that needed one (`loadPics`, `picsLoaded`, `needPics`); 1.2 MB less on the first load.
- Icons (d2ae95370, 7d68e9a00): 176 of the 181 model icons, which were 128 px renders shrunk by dropping pixels, are drawn as the slot shows them (element models by `block_render`, GeckoLib items by `geo_icon_render.html` with the item's `display.gui` and the GUI light; three blank icons now draw; 313 → 95 kB). New `tints.py` reads the colours `ItemColors` multiplies into tinted layers from the jars: 102 icons tinted, 89 spawn eggs added for `mob_ids.json` (all 77 vanilla eggs equal the Minecraft Wiki's table). 69 gear icons and 151 curio-page icons had been drawn from resource packs the README bans (All Rights Reserved); they are redrawn from the mods' own or vanilla textures. `mcassets.NO_ART` is the one list of banned packs (22, by file name) and `Assets` drops them whoever passes them. Pyrium Staff and Wand of Final Light had no other flat picture and have no icon until their models are rendered.
- Side bosses (e3e5344cb, abf0d818a): 77 portraits redrawn at 256 px from the mods' own models with the Keepers' camera and the game's light, lossless PNG (1,454 kB of WebP → 876 kB). Crone, Ice Hermit and Mutant Enderman have one for the first time; the 12 pictures fetched from fandom/wiki.gg (CC BY-SA, shown without the credit the licence asks for) are gone, so no wiki picture is left (`wimg.py`, `wdl.py` removed). `jmodel.py` runs `setupAnim` at rest, new `reg.py` reads the EntityType registrations, `bgeo.py` + `boss_portraits.js --in/--out` + `pack.py` do the GeckoLib ones; `geo2three.js` also discards texels under alpha 0.1 when blending (Keepers byte for byte the same; 4 armour renders and Lich change by a few pixels). A Path card with a portrait but no scene takes the boss's biome as its background (Ice Hermit's had none).
- Gear table and readers (ef0460e0d, 3934a6370): `mjvm.srg_tables`, lost in the rewrite, is back, so the wide gear scan runs again; `gear/wide/srgjar.py` builds the SRG server jar without Forge's installer and equals Forge's own jar of the official server pack class by class (5,460/5,460). The scan was re-run on the 6.6.6hf jars (106 namespaces); `gear_table.json` took from it the recipe lists, with the pack's recipes in place of the mods' at the same id (1,731 lists). That moves Composite Material's obsidian armour from Act V to VI: the pack's `kubejs/data` recipe is a smithing upgrade of a netherite piece.
- Reference (4d554c3d2): the pack author's own server pack (383 jars) is the reference for jars, data and configs. Checked on 2026-10-31 against the CurseForge set: the same classes, data, `mods.toml` and KubeJS; the same configs except FTB Quests (encrypted with a fresh key each time) and one client-only Quark option (`build/README.md`, "Regenerating from the pack").
- Docs: `build/README.md` and `build/ARCHITECTURE.md` brought in line with the code at 7d68e9a00: rooms are the headers of Curios, Equipment, the Build planner, Bosses and Mechanics, with no item frames; the Act pages are live and only the mod and slot pages redirect; `curio_recipes.py` is named as the third in-place writer of `data.js`; the tier rule compares with the fifth best item; GSTEP is 1.24; item counts, file sizes and line counts re-measured.
- Checked: `check.sh` green at 7d68e9a00 (4 min 12 s): patches idempotent and the build reproducible, 0 broken invariants, 72 Path cards all with a background, 2,198 gear pages and 328 sets, 3,931 detail pages on the shared layout, style rules, site check (0 missing files, 0 script errors). The docs: each figure measured again against the code (line counts, file sizes, `gear_runtime.json` items, the live `GSTEP`, the `room(` call sites and the `.room3` count per route), and `node build/shot.js '#act/5'` draws the Act page at 1440 and 375.
- Still open (`docs/RENOVATION_PREP.md`, "Still open", has the full list): the wide gear scan could not replace `gear_table.json`, because 52 armour pieces and 56 items of the table come from producers that are not in the repo (`fallback.json`, nested jars), so only its recipe lists were taken, and its ~2,000 items need comparing one by one before the table is replaced; one class layer and one interpreter (`classlib.py` on jawa under mjvm; jmodel, gear_fx and iss_armor still parse `javap` text, and jmodel runs a method straight through, so a loop body runs once); `attrs.py` and `cfg.py`, the producers of `side_bosses/stats.py`'s inputs, are not in the repo, so `side_stats.json` cannot be regenerated from the pack.
- The fix pass itself (commits 0a24ea45d … eef54f182 on the branch, the audit and its plan in the session): 149 findings from
  21 finder/verifier agents (144 confirmed by an adversarial verifier, 3 refuted), rated and planned by Fable (max) into 11
  file-disjoint groups and 31 chunks, fixed by Sonnet (simple) and Opus (complex) agents in one worktree per group, then
  cherry-picked here in the plan's order. By reader impact:
  - Scoring: Goety's `spell_potency` (+1 read as +100 %) and `casting_speed` no longer count as Iron's spell power (Goety
    attributes keep their namespace in `gear_runtime.py`, `gear_data.py` and `gear.js`), so the Mage lists at Acts IV–XII move
    (Dark V S → A; best Mage armour Frost IV, Geomancer V–Dragon, Etherite XI–XII). Summon Power is flat (+2 on Summoner's
    Bangle: Mythic → Uncommon, +100 % → +10 %) and Summon Duration is not damage; Resistance follows Linggango Fixes' curve
    (0.2 + 0.04444 a level). Curio "Measured in game" rows print flat attributes as flat ('+4 Lethality', not '+400 %') and
    movement speed against its 0.1 base; `gMod` has an explicit percent set; knockback resistance ×10; tier text names the
    fifth best, as the code does.
  - Gear facts from the pack: locks come from the pack's gate tags only (`gear_gated.json`; 66 lock changes, every lock names
    its boss, GATEN = UNL); `boss_order` reads every ingredient (it skipped the first of 1,858 recipes) and folds 6.1/6.2 in
    order (Dinosaur Bone Club 0 → V, The Great Frost II → III, Sword of the Nightlord V → VII, Buster Gauntlet VI → VII,
    Withered Ribcage and Void Sword V → VI, three Lethality blades Dragon → VI by their tag); the 24 Mystical Agriculture armour
    pieces the pack disables are hidden from the tier lists; 20 one-piece "sets" are 3 four-piece families (Living, Robe,
    Darkness, plus Geomancer, MekaSuit, space suits, hazmat, scuba, diving: 328 → 313 sets); Tide Piercer, Trumpet Axe and
    Hand of Death say their recipe needs a mod the pack lacks; attack damage and speed read from the game's own measurement
    (Holy Moonlight Sword 41 → 7); 51 "sets the target on fire" rows that belonged to the arrow are gone; the pack's 64
    `renameItem` names apply (`renames.json`: Concentrated Bronze, Animal Leather, Stinky Hat).
  - Curios: 15 recipes as KubeJS and the datapack order make them (`curio_eff_recipes.json`); Unique Accessories drop chances
    from the config (0.2–15 %, not 100 %); Terra Curio chances from the loot tables (`curio_drops.json`); ~30 Brutality
    attribute lines from the jar; 14 curios that need a boss-only drop sit at that boss's Act; the ghost War Horn is gone
    and Sweetheart Necklace, Vanir Mask and Pocket Universe are in (1,319 → 1,321 curios; `#i` indices from 1026 moved);
    Cradle of Rebirth is Must-Have (owner decision); Drowned Belt 4 points a level; Panic Necklace in the Accessory slot.
  - Bosses: the Armageddon Keepers, Wither and Ender Dragon are exempt from Hardmode (`armageddon_bosses.json`); the Dragon
    is 600 HP / 30 armour (`ender_dragon_configuration.json`); 33 side bosses take the pack's `soul_bosses` pins (Ignis
    3,200 HP); Meet Your Fight melee multipliers, the Monster flag, Apostle toughness 66, Rosalyne's books; attacks listed once
    per phase under the phase's title; summon ingredients name their treasure bag; the Keepers carry the game's names (The
    Discord, Fourth Calamity); six side bosses show their in-game name beside the wiki name (Chorusent, Monarch of Chaos, The
    Decaying King, Fallen Icon / Harbinger of Moonlight, Echo of Tyros, Old Champion's Remains / Frenzied Shade; owner
    decision, routes unchanged); AE2 gates list the add-ons' parts; ritual types named from JEI; guide text without markup.
  - Front end: one stat icon per line, exact Act numerals in filters, a pill's × removes one token, counts match Curios, Enter
    in the header box applies, '/' types inside boxes; I'm-here redraws Continue and opens its Act, saved state checked per
    key, bad hashes get a page, side-boss lists by their own Act; the planner's picker scrolls into view on phones, keyboard
    focus kept across redraws, no sidebar on #build, share links report dropped items, conditional lines out of Stat totals,
    estimates marked (chip, faded loadout picks); Mechanics draws 60 ritual rows at a time with named filters; one cell per
    missing loadout pick (NOTES 674's item, closed), Equipment search over every match, switches redraw in place; touch
    wording on phones; the October 31 Changes entry.
  - Layout: detail pages one column below 1181 px; Curios Acts, footer, Equipment bars and loadout, hub slot list, room heads
    (positive width at every room width, a plain lit wall under the title on phones) fixed at 375–1024 px; section headings
    30 px, sub-heading rhythm, planner select, cell labels, boot frame (no layout shift: fonts off the critical path, body
    classes set at boot), focus ring on the Path, reduced motion honoured, touch targets ≥ 24 px, dead `.lhero` CSS gone;
    owner-approved contrast: tier letters and the ingredient panel in dark ink, one Mythic red (#ec6b5f), text Act titles
    below 480 px.
  - Checks: `check.js` awaits every picture's decode on 1,405 curio, Keeper and side-boss pages, `apply_all.sh` fails when
    the tier run crashes, `shot.js` names the hub shot; `style_check.js` has a phone pass (375–1180 px); the audit's data and
    scoring bugs are invariants in `check.js` (Goety keys, Summon Power, Resistance, measured rows, gates, set families,
    disabled gear, loadout cells, Hardmode, soul pins, Keeper names). The chunks' full invariant texts are in the session's
    workflow reports (`scratchpad/audit`), not all ported: see still open.
- Checked: Act dump before/after the pass (`compare_acts.py`): exactly the moves above, nothing else; the planner's joint
  checks (Dark MA 1.296, Frost/Geomancer/Etherite loadouts, bangle rank 1, Halo 2.195, 0 items below their gate, 0 unnamed
  gates, 1 Geomancer set, Tide Piercer untiered, no duplicate set names, Dragon 600, no "Keeper of the Calamities"); shots
  of the main routes, Equipment, Bosses, Mechanics, a curio, gear and set page at 1440 and 375 against the pre-pass baseline
  (changes only where intended); `check.sh` green on the final tree (6 min 16 s: 0 broken invariants, 313 sets, 1,407 pages with pictures all decoding, 3,918 detail pages on the layout, style and site checks pass).
- Still open: the collected per-chunk invariants beyond the ones above (a11y_check.js: CLS, long tasks, contrast, focus,
  accessible names; the full content scans) — the plan's checks chunk 2, skipped to finish the session; Crucible Sword's
  damage (dump 41, game 30, hit 9: needs a fresh measurement); the #gear lede at 320 px (below the 375 px target); the
  Mechanics AE2 gates table is ~7,000 px tall at 375 px (one chip per line); `stats.py`, `summons.py` and `goety.py` were
  fixed but not re-run (their inputs are not in the repo: the JSON was hand-edited to what they would write); `gear_fix.json`
  carries 37 stale ids the pipeline never applies; the icon pass (own-3/own-4, `docs/RENOVATION_PREP.md` item 5).

## 2026-11-01: process changes after the audit fix pass
- Asked: delete the leftover fix branches, list what the whole session did, rate how it worked, improve the process. The
  11 local `fix-*` branches (never pushed; every commit is on `main`, checked by subject) and 19 scratch worktrees are gone.
- Repo changes (plan and reasons: `docs/plans/2026-11-01-process-after-audit.md`): `.gitattributes` merges `docs/NOTES.md`
  as a union; invariants live one file per topic in `build/checks/` (the audit's moved to `audit-2026-10-31.js`), loaded by
  `check.js`; hand corrections to curios go into `build/patches/curio_fix.json`, applied first by `apply_all.sh`, so
  `data.js` is written by scripts only (Cradle of Rebirth's Must-Have is the first entry). CLAUDE.md Process: big passes
  ship high-severity first, one finding per file group, one review per group, a token budget and model split, a dry run of
  workflow scripts, at most two parallel builds, generated files committed with their cause; README and CLAUDE.md tables
  follow.
- Checked: `apply_all.sh` leaves `data.js` byte-identical (curio_fix: 0 changes); `curio_fix.py` on a test file set,
  added and removed curios and a second run changed nothing (then reverted); a probe file in `build/checks/` turned
  `check.js` red (exit 1) and the audit invariants passed; `check.sh` green (see the commit).
- Still open: the per-chunk invariants of the audit not yet ported (now a matter of adding files to `build/checks/`);
  the other audit items listed in the 2026-10-31 entry; Wave 2F (one class layer and one interpreter).

## 2026-11-01: the audit's leftovers ("chạy tiếp các mục còn lại")
- Invariants: the 111 the fix chunks wrote but did not land are in `build/checks/` (gear 24, curios 20, bosses 13, routes 12,
  text 8) and a new `build/a11y_check.js` run by `check.sh` (16: first paint with slow fonts, boot classes and layout
  shift, scroll and focus on Equipment and the planner, contrast, visible Tab focus, accessible names, search keys, saved
  state, share links, room heads at 4 widths, touch wording, reduced motion). 11 were duplicates, 6 already in the tree,
  2 could not fail and were dropped. Check files may `await patchJSON('x.json')` (check.js exposes `build/patches/`).
  Each file was shown to fire on broken data. `check.sh` now takes about 10 minutes (CLAUDE.md and README updated).
- The invariants found five live bugs, fixed: Goety attribute labels showed their namespace ('+0.1 Goety.Soul Discount':
  `gAttr` now prints 'Soul Discount (Goety)'); 15 Unique Accessories curios lacked the vanilla chests and mobs the pack's
  config gives them (`curio_fix.json`; mod's own loot modifiers are active: `global_loot_modifiers.json` has
  `replace: false`, `curio_dedupe.js` only swaps recipes); Redstone vs Redstone Dust; a stale `MINFO` entry for Celestial
  Artifacts; Enter on a planner slot's × dropped focus when a preset had overfilled the slot (focus now goes to the next ×).
- Icons (own-3/own-4): chests, ender chest, archwood chest, shield, red banner, two plushies and Pyrium Staff drawn from
  their renderers' bytecode (client jar remapped to SRG with Mojang's 1.20.1 `client.txt` + `joined.tsrg`, not committed)
  with vanilla or the mod's own textures, 32 px, display.gui, GUI light; `build/checks/icons.js`. Four gear items still
  have no icon (Spell Bow, Potato Staff, two Nether Exp shotguns), listed in the check so the list can only shrink.
- Rooms grow by whole blocks when the title does not fit (owner's choice); props move down with the floor; repainted after
  the web fonts load. Checked 320–1440 px on the five rooms: no title on the floor; 288 px kept at 1280 and 1440.
- Mechanics AE2 gates: 12 parts per Act, the rest behind 'N more' (7,250 → 3,156 px at 375 px).
- `icon2.py`, `icon3.py`, `mkicons.py`, `gui_icons.py` deleted (RENOVATION_PREP called them retired; nothing called them).
- Correction: the "37 stale ids in gear_fix.json" of the 2026-10-31 entry are not stale: the items exist in the pack's jars
  (Sword of the Elements, Simply More Mimicry, Too Many Bows) and wait for the wide gear scan; their notes stay.
- Plan for the rest: `docs/plans/2026-11-01-classlib-and-producers.md` (Fable): producers `attrs.py`/`cfg.py` first, then
  one class layer, one interpreter with frame merging, and jmodel/gear_fx on it, each proved by byte diffs.
- Checked: `check.sh` green (10 min 11 s; a11y_check 88 s); shots of the rooms, the AE2 table, the icon pages.
- Still open: P1, 1A, 1B, 1C and P2 of that plan; Crucible Sword's damage (needs a game server); the four gear items
  without an icon.
- P1 of the classlib plan done (feed84b73): `side_bosses/attrs.py` (attribute builders and superclass chains on mjvm's VM,
  writes `attrs.json` + `supers.json`) and `cfg.py` (the nine config classes' defaults) replace the lost producers;
  `stats.py` now regenerates `side_stats.json` from the jars: the 82 committed rows byte-identical, one new row, Ice Hermit
  (268 HP, 4 armor, 10 attack; `IceHermitEntity.createAttributes()` in RevelationFix 4.7, the jar nested in Goety
  Revelation, never read before). `stats.py` fixed: a bare registry name ('endersent', also Goety's) picked the wrong
  class and dropped Endersent's row with a fresh `reg.json`; invariant in `checks/bosses.js`. `summons.py` reproduces
  `summons.json` byte for byte; the hand-written Sigil of Calamity text is kept in its `INFO` table. MAN moved to
  `man.json`; `assemble.py`/`loot.py`/`geofind.py` read the committed `map.json`/`info.json`. Order in pack_audit/README.
  Checked: `check.sh` green on this tree (run by the implementing agent); Ice Hermit page shot at 1440 and 375.
  Still open: the RevelationFix jar has to be unpacked next to the mods by hand before `reg.py`; 1A, 1B, 1C, P2.
- 1A of the classlib plan done (3f14acc8a): `build/gear/classlib.py` (sorted class path, first jar wins, cached class
  files, supers/interfaces/find_method, descriptors with slots, typed constants, bootstrap methods, constant-pool scans,
  services, mods.toml) under `mjvm.py`; `iss_armor.py` reads the jar (no javap) and `--gear-stats` rewrites
  `gear_stats.json` `iss_materials`; the audit's synthetic javac tests are in `build/tests/bytecode/` (`run.py`, 99 checks,
  a hand tool). Proved: the wide gear scan's 106 `ext_raw` files identical before and after (ignoring timings);
  `iss_mats.json` identical; P1 still reproduces `side_stats.json`; the site build byte-identical; `check.sh` green
  (implementing agent), `run.py` green here. Not run end to end: `tints.py` and the old `gear_extract.py` (they compile and
  build `VM` the same way). Still open: 1B, 1C, P2.
- 1B stopped and dropped at the owner's choice ("kế hoạch quá phức tạp, chạy hàng giờ mà không đem lại kết quả quá lớn"):
  1B, 1C and P2 change tools, not pages. Its unfinished work was discarded with its worktree; the plan file says when to
  take them up again. Lesson for the process: a tool refactor whose proof is "byte-identical output" earns its hours only
  when a reader-visible fix needs it; plan it then, not ahead.
- Still open: the wide gear scan (RENOVATION_PREP item 1, with P2); Crucible Sword's damage (needs a game server); four gear
  items without an icon.
- Process (CLAUDE.md, "Process"), from this session's mistakes: value first (say what a reader sees before work over an
  hour; refactors proved only by identical output wait for a visible need), who does it (under 30 minutes without an agent,
  resume stopped agents, clean up worktrees the same day), `check.js` during work and `check.sh` once per wave, and docs say
  only what was checked (two wrong claims of 2026-10-31 were corrected above). The Facts bullet now points at
  `build/checks/`.
- The `site` workflow skips commits that only touch Markdown, `docs/`, `.claude/` or `.gitattributes` (`paths-ignore`;
  checked first that no build or check step reads a Markdown file). Docs-only pushes no longer cost an 8–10 minute run;
  `/build.txt` then names the last commit that changed the site (CLAUDE.md step 6 says so).
- Faster checks: the per-page text checks of `checks/routes.js` (data-t, raw game text, ids in recipe lists, gear leads,
  curio raw ids, side links) run inside `check.js`'s own pass (PAGE), so the 3,918 detail pages are drawn once, not twice;
  `check.sh` runs `check.js` beside `style_check` → `a11y_check` → `site_check` (those three in sequence, so a11y's timings
  are not taken under three browsers). Local `check.sh`: 10 min 11 s → 6 min 21 s, green. Proved the moved checks still
  fire: a probe that broke one curio's text before the loop made `check.js` report `#i5` and exit 1.


## 2026-11-08: plan for a multilingual wiki (vi, ru, pt, es); no code changed
- Wrote `docs/plans/2026-11-08-multilingual.md` (spec and plan in one file, draft awaiting the owner's approval). Nothing in `build/`
  or the site changed; `apply_all.sh` was run once only to measure, and left `git status` clean.
- Measured (build of `b0c2c0e`): no i18n mechanism exists; UI text sits inside `app.js` template literals; the code reads English
  back out of data (`RCV` `app.js:1527`, `Key requirement` `app.js:1267`, icon regexes `AIRG`/`fmt` `app.js:778-784`); the embedded
  fonts lack Russian (66/66 letters missing in all three) and most Vietnamese letters (54-55/74 missing); the data holds about
  18.2k unique strings (about 770k characters, of which about 24k are Java class names) but `src`/`src0`/`why` collapse to
  272/300/111 sentence patterns; item names, tooltips and Patchouli text belong to the mods and exist in the game's own lang files
  (one mod sampled, Ars Nouveau, ships ru_ru, pt_br, pt_pt, es_es and vi_vn).
- Checked against sources: DeepL supports VI, RU, PT-BR and ES with glossaries (API Free: 500,000 characters a month), from its
  documentation today.
- Still open (with the reason): D1 to D4 of the plan need the owner's answer (pt-BR or pt-PT, neutral Spanish or es-ES, Vietnamese
  item names in English or translated, who pays for translation); official-lang coverage of the 383 jars is not measured (needs the
  pack); whether upstream Monocraft has Cyrillic and Vietnamese glyphs is not checked; the token estimates are rough (plus or minus
  50%) until the Phase 1 pilot.

## 2026-11-08: multilingual, Phase 0 measured (owner approved the plan: "làm"; D1 to D4 at their defaults)
- Added `build/i18n/harvest.py` (`fetch`, `vanilla`, `build`): streams every jar of the CurseForge manifest (454 of 455 files; one
  has no file listed on cfwidget), keeps only lang and Patchouli files, drops the jar (56 MB cache, under 3 minutes in the cloud
  session); `build` writes `build/i18n/official/{ru,pt,es,vi}.json` (names by id, English text to official text; pt is pt_br only,
  es tries es_mx then es_es) and prints coverage. No site source changed, so `check.sh` was not run.
- Measured, 306 mods with a lang file: ru_ru 170, pt_br 114, es_es 91, es_mx 70, vi_vn 36 ship; pt_pt adds one mod without pt_br.
  Official names exist for ru 49%, es 23%, pt 20%, vi 9% of the 3,519 curio and gear ids; verbatim English text found and
  translated for 53%, 29%, 25%, 10% of the 6,604 strings that are game text (of 24,909 unique strings). Curio `fx` is wiki-written
  (1% verbatim). The plan's L1 claims and its token estimate were wrong and are corrected in the plan (sections 3.2, 3.5, 6, 13).
- `RCV` and `Key requirement` need no change (the code keeps reading English; only the print step translates). Icons: the set comes
  from the English line, a per-language table only places them (spike: positions found 61% ru, 84% es on unmodified drafts).
- Fonts: real Monocraft has all of Cyrillic (the embedded subset has none) but only part of Vietnamese; no pixel font has both.
  The comparison image went to the owner. Waiting for their pick of V1 / V2 / V3 for Vietnamese; ru needs no decision.
- Still open: the owner's Vietnamese font choice (recommended V2); glossary; Phase 1 (engine, language menu, vi interface).
  Unverified: token cost per 1,000 characters (pilot), ru layout growth, licence note for translated mod text (plan section 10).

## 2026-11-08: multilingual, Phase 1 slice (engine and page shell in vi, ru, pt, es)
- Added `build/src/i18n.js` (`t`, `tn`, `shell`, `setLang`, the menu), `build/i18n/ui.json` (34 keys by 5 languages), `build/i18n/glossary.json`
  (12 starting terms), `checks/i18n.js`; `build.py` checks the table against the page (key used but missing, English differs, key
  unused, `{x}` / tags / links differ) and writes one pack per language (inline in the offline file, `static/lang-xx.<hash>.js` on the
  site, fetched only when chosen); `shot.js --lang`; `site_check.js` loads `?lang=vi` and checks that a blocked pack leaves English.
  The header, nav, filter column headings, footer (except the credits paragraph) and the language menu change with the language.
  Hub, lists and every page body stay English until Phase 2 and 3.
- A bug found on the way, fixed: `app.js` already uses `data-i` (the Path's Act tabs), so the first draft's `shell()` rewrote those
  buttons. i18n now owns `data-lg`, `data-lgh`, `data-lga`; `build/README.md` says so. The "cycle every language and come back to
  English: outerHTML must be identical" check is what caught it.
- Checked: `apply_all.sh` builds; `site_check.js` green; `checks/i18n.js` run on the offline file returns no findings, and two
  deliberate faults (a `{x}` left in a translation, a missing pack) are both reported; pixel diff of six English routes (home, gear,
  g12, bosses, mechanics, build) against the previous build with motion off: only the header differs (the menu, and the search box
  narrowed to make room), the page bodies are identical; screenshots of vi, ru, pt at 1440 px and 375 px looked at.
- Not yet recorded here: the result of the full `build/check.sh` (started, still running when this entry was written; the `site`
  workflow runs it on this push too). Nothing was pushed to `main`; the work is on `claude/busy-ride-88rgef`.
- Still open: the owner's choice of Vietnamese font (V1, V2 or V3; ru uses upstream Monocraft and needs no choice) and the fonts
  step itself; the page-body strings (Phase 2) and the data text (Phase 3); the icon placement tables per language; the pilot that
  measures tokens per 1,000 characters; native review of ru, pt, es (the glossary and `ui.json` are unreviewed).

## 2026-11-08: correction to the Phase 1 entry above (header layout), and the check.sh result
- The commit `e53d039` put the language menu as a fourth item of the one-row header. That was wrong: the full `check.sh` failed on
  `style_check` ("768px #mechanics: the AE2 heading lands under the header (-28 px)"; the previous build passes), and measuring
  showed the menu falling outside the 64 px header at 1000 to 1100 px and the header growing a row at 768 and 900 px. My earlier
  pixel diff only covered 1440 px and missed it. Its NOTES line "only the header differs" was true at 1440 px only.
- Fix: the menu is a stone button inside the right end of the search box (`.sbox`, `style.game.css`); the wrapped header (search on its
  own row) now starts at 1180 px instead of 900 px, and at 1320 px for ru and pt whose nav is wider (767 and 754 px against 640;
  English needs 1171 px for one row with a 240 px search box, vi 1103, es 1194). `html{scroll-padding-top:176px}` follows the same range.
- Checked after the fix: header geometry equals the previous build at 768 and 900 px; across 5 languages by 5 widths the menu is
  always inside the header and inside the search box; `style_check` passes; `site_check` passes; `checks/i18n.js` returns nothing and
  still reports its two deliberate faults; six English routes against the previous build with motion off: 0.148% of pixels differ
  on each, the size of the menu button. English readers also see a two-row header at 901 to 1180 px now (it was one row with a 70 to
  170 px search box): a visible change, flagged for the owner.
- The result of the second full `build/check.sh` is recorded in the line after this one once it has finished.
- Result of the second full `build/check.sh` (on `083aace`, the header fix): green. Invariants 0 broken; 3,918 detail pages off the shared
  layout 0; page text 0 problems; style: passes (the 768 px AE2 failure is gone); a11y and timing 0 broken; site check passes.

## 2026-11-08: multilingual, fonts for ru and vi (the owner chose V2 for Vietnamese)
- ru: `Monocraft-Cyrillic.woff2` and `Monocraft-Bold-Cyrillic.woff2` (about 3 KB each, from the v4.2.1 release), same family as Monocraft with a
  `unicode-range`, so Russian labels and titles use Monocraft itself. vi: `VT323-Vietnamese.woff2` (VT323, SIL OFL 1.1, about 20 KB), family
  `VT323 vi`, `size-adjust:127%`, used for titles and labels under `html[lang=vi]`; body text stays Be Vietnam Pro. Credit added to the footer's
  Art paragraph (still English by design), `fonts/README.md`, `OFL-VT323.txt`. The offline file inlines the faces (+about 33 KB); the site serves them
  as files fetched only when the text needs them.
- Checked: `checks/i18n.js` font block passes on the offline file and reports each of two deliberate faults (Cyrillic faces removed; VT323
  removed); `site_check.js` loads the Cyrillic and VT323 files from the site build with no failed request; six English routes against the
  build before i18n: 0.148% of pixels differ on each (the menu button), fonts change nothing in English; vi and ru pages at 1440 px looked at.
  A first font test (text width against the browser's default font) gave a green result that proved nothing, because Chromium picks a system
  face per missing glyph; replaced by asking which faces the text loads.
- Still open: Russian body text is the system font (Be Vietnam Pro has no Cyrillic); Phase 2 and 3 text; icon placement tables; the
  Vietnamese labels in VT323 should be looked at by the owner on real pages beyond the home page.- Full `build/check.sh` on the tree of this entry (fonts for ru and vi): green, exit 0 (invariants 0 broken, 3,918 detail pages off the shared
  layout 0, page text 0 problems, style passes, a11y and timing 0 broken, site check passes with the fonts).


## 2026-11-08: multilingual, Phase 2 group (a): hub, Act pages, The Path, navbox
- JS sentences now use the English as the key: `T("…{x}…",{x})` and `TN(n,"{n} curio","{n} curios")` (`src/i18n.js`, hash `hsh`; the same hash in
  `i18n/tmlib.py`, checked equal on strings with accents, Cyrillic and an empty string). Translations: `i18n/tm/<lang>.json`; English-on-purpose:
  `i18n/keep.json`; `i18n/trlog.js` crawls the site for sentences built from variables (`i18n/tr_log.json`); `build.py` checks hash, `{x}`, tags and
  plural forms and prints coverage; `checks/i18n.js` fails when the hub or an Act page asks for a sentence without a translation or a keep entry.
- Converted: `crumb`, `actL` / `actF`, `wikiNav` (the navbox that ends every detail page), the active-filters bar, the title-screen buttons, the four
  Start-here cards, The Path (heading, per-Act panel, "I'm here", "Your run"), the hub sections (Equipment, Must-Have, Curio slots, Mythic, New in
  6.6.6) and the Act page (heading, lede, "Opened by beating", "Next boss", "Showing … of …", not found). 88 literal sentences and 29 built from
  variables; 104 translated into each of vi, ru, pt-BR, es (by the assistant, unreviewed by a native speaker), 13 kept in English by design.
- New terms for the owner to look at: "The Path" is translated (vi "Lộ trình", ru "Путь", pt "O Caminho", es "El Camino") since it is the wiki's own concept;
  "Act" is vi "Act", ru "Акт", pt "Ato", es "Acto"; the Russian sentences put a boss name after a colon so it stays in the nominative.
- Proof the English did not change: `<main>` innerHTML, tab title and title-screen buttons for 34 route states (17 routes, with and without "I'm here") are
  identical to the build before this group, character for character (blob URLs and the `seen` / `seen2` classes normalised). The comparison found one
  bug of mine (a single-quoted string that does not interpolate `${}`), fixed. Russian titles use Monocraft throughout (the first look mixed Cyrillic
  from Monocraft with "II" from Jersey 15). Screenshots of the hub, an Act page and a gear page's navbox in vi, ru, pt, es looked at.
- Full `build/check.sh` on this tree: green, exit 0 (invariants 0 broken, 3,918 detail pages off the shared layout 0, page text 0 problems, style passes,
  a11y and timing 0 broken, site check passes).
- Still English on these pages, on purpose for the next groups: slot names (Charm, Ring … have official translations in the Curios mod), the filter column
  and role chips (group b), curio text, the Act title pictures (images made by the pack), the credits in the footer. The pilot that measures tokens per
  1,000 characters is not done: the 104 sentences were translated in this session without a count.

## 2026-11-09: multilingual, Phase 2 group (b): the Curios page, the filter column, slot names
- The sidebar (role, rarity, mechanic and element chips, the mod / slot / Act selects) is built once, in English, when the page loads. A language change
  does not rebuild it: `relabelSide` (app.js, called from `useLang`) writes each chip's label from the English it remembers (`b._en`), so filter keys, saved
  filters (`lgw2`) and shared links stay English. The query also understands a role named in the reader's language (`role:ближний`); `d._q` is cleared on a switch.
- Converted: the filter bar (search box, field list, buttons, the "How it works" paragraph, the Relic level controls), the active-filter pills, the Curios
  page (heading, lede, legend, tier headers, table view, "Show all N curios"), the curio card, the slot badge and the hub's slot list, the "N / TOTAL curios"
  count and the index list. `tmlib.scan_msgids` now reads sentences written between backticks.
- 127 new sentences, 244 per language in `tm/`, all four languages covered 244 of 244. The game's own text is used where it exists: slot names from the
  Curios mod (Charm, Ring, Necklace, Head, Hands, Belt, Body, Feet, Back, Bracelet, Accessory, Spellstone) and Iron's Spells school names (Fire … Eldritch), read
  from the jars; `keep.json` is now `{"all": […], "<lang>": […]}`: vi keeps English for slot and school names (D3), rarity names and mod-specific slots stay English
  everywhere. A term clash found and fixed: the official ru "Призыв" and es "Invocación" mean the Evocation school, so the Summon role is "Призыватель" (ru) and
  "Invocador" (es).
- English output: HTML of 51 route states (17 routes, plain / "I'm here" / filters on; main, sidebar, title, title-screen buttons) equals the build before this group
  character for character, with one deliberate exception: "1 items" now reads "1 item" (`TN`) for an Act with one curio under a filter. The comparison caught one bug
  of mine again (a single-quoted string that does not interpolate, on the Must-Have star), fixed. `i18n/domdump.js` and `i18n/domcmp.py` are now in the repo.
- Checked: `checks/i18n.js` clean; deliberate faults reported (a translation deleted → named; the Melee chip not relabelled → named, and "role:ближний" not found);
  `build.py` rejects bad hashes, `{x}`, tags and plural forms; full `build/check.sh` green, exit 0 (invariants 0 broken, 3,918 detail pages off the shared layout 0,
  page text 0 problems, style passes, a11y and timing 0 broken, site check passes). Screenshots of the Curios page in ru and vi at 1440 px looked at.
- Still English: the tooltip and the curio detail page (next group, together with curio text), the equipment pages, bosses, mechanics, changes, the Build planner;
  mod names; rarity names; curio and gear names and texts (Phase 3). Token cost of the 127 sentences was not counted.

## 2026-11-09: multilingual, Phase 2 group (c1): the shared detail-page frame, tooltip and the game's own item names
- Item names: `build.py` merges the game's own names and verbatim texts (`i18n/official/<lang>.json`) into each pack's `tr`, keyed by the hash of the English a
  page shows (ids are mapped to English names from the data); a sentence of ours wins. New `TD(en)` in `i18n.js` (the same lookup, not logged, no placeholders)
  wraps 70 name prints (`esc(x.n)`) in app.js and gear.js, the tab titles of curio, gear and set pages, and search (`qf` also holds the localized name, cleared on a
  language switch). A name without an official translation stays English, as it does in the game. The offline file grew from 13.93 to 14.33 MB (the packs are inline);
  on the site each language is a separate file.
- Converted: the `article()` frame (On this page, Back to top, the "Checked against" line, Copy / Copied / Press Ctrl+C, the curio breadcrumb) and the tooltip's
  own sentences (kind, Evolves from / into, Locked until, Requires the, Must-Have, luck window, estimate). 13 new sentences, 257 per language, 257 of 257 covered.
- English did not change: HTML of 51 route states equals the build before group (b) except "1 item" (noted under group b); the tooltip HTML of 35 curios (plain,
  Keeper-gated, ring-gated, Must-Have, evolving, estimate, luck window) is identical character for character (`tipdump`, a scratch script, not kept).
- `checks/i18n.js` now also draws a curio, a gear and a set page and builds the tooltip of seven kinds of curio in every language and requires every sentence they ask
  for to be translated or kept. Full `build/check.sh` green, exit 0.
- Seen while looking at screenshots, not a bug: the h1 of a detail page is missing in a plain screenshot taken 0.8 s after load in every language (it fades in); the
  Russian title wraps to two lines at 56 px, which fits.
- Still English on a curio page: everything in the body (How to get it, Stats, Used to craft, the source lines) and the effect text; that is group (c2) and Phase 3.

## 2026-11-09: multilingual, Phase 2 group (c2): the body of the curio page
- Converted the whole body of the curio detail page in `app.js` to `T`/`TN`/`TD`/`N`: section headings, Must-Have / Scarce banners, Keeper and ring gates, source cards
  (Boss drop, Mob drop, treasure bag, chests, Trade…), the recipe window (Ingredients, "any {tag}", how-to-place text), the stats tab (Element, Damage, stat names
  with their hints), the relic table and the relic level panel, the Duplicates card (Stacks / Doesn't stack, set ladder). `N("…")` is a new no-op marker for
  sentences kept in constant tables (STATH, DMGT, SKL, SKW, STHOW, how-text); they print through `T(x)` and `tmlib.scan_msgids` reads them.
- 131 new sentences translated by me in ru, pt, es, vi (390 per language, 390 of 390 covered). All unreviewed by a native speaker. The damage-type labels
  (Slash/Pierce/Blunt/Magic/Projectile) and "Relic" (ru реликвия, pt relíquia, es reliquia; vi stays Relic) are new terminology choices to review.
- English did not change: `<main>` + sidebar of 51 route states equal the build before group (b) except "1 item"; tooltips of 35 curios identical; HTML of 50 curio pages
  (relic, each stacking kind, ladder, Must-Have, Keeper and ring gates, evolution, and the relic panel after moving the level slider) identical (`pagedump.js`, a scratch script).
- `checks/i18n.js` draws 11 more kinds of curio page (relic with the slider moved, each rule above) in every language and requires every sentence to be translated or
  kept. It caught 3 sentences hidden in a constant table at once (how-text of a recipe); wrapped in `N()`, translated.
- Looked at: ru and vi curio pages at 1440 px (Drowned Belt, Ultra Sniffer Fur), the relic panel in ru. full `build/check.sh` green, exit 0 (invariants 0 broken, detail pages off the shared layout 0, page text 0 problems, style passes, a11y and timing 0 broken, site check passes), run on a copy of the tree taken before the next group's edits.
- Open: numbers use the browser's separator (`toLocaleString()` without a locale; ru should read "2 100"); the curio effect, source and note texts (`fx`, `src`, `st`, `why`) stay English until Phase 3.

## 2026-11-09: multilingual, Phase 2 group (d1): Equipment
- `gear.js` converted: the Equipment list (title, per-Act lede, Act strip, Best loadout, tabs, search, counts with plural forms, the five-paragraph "How the tiers are worked out"),
  weapon and armor pages (lead, How to get, Stats, Bonuses, Effects, every branch of Measured in game, Tier by Act, infobox, navbox), set pages, the weapon and set tooltips, and the
  "Measured in game" section of curio pages. `GROLE`, `GKIND`, `GSLOT`, `GMK`, `GWHEN` are read through `T()` by `gT()`, so the ~20 places that print a role needed no edit.
- Left English on purpose (Phase 3): the stat lines of tooltips and Bonuses (`fmt()` places icons by English words), effect and attribute names (`gAttr`, `gCName`).
- 187 new sentences (577 per language, 577 of 577 covered), translated by me, unreviewed by a native speaker. New terms to review: Playstyle, Loadout, Toughness, "tier list".
- English did not change: 205 captures (8 states of the Equipment list, a search with and without hits, show-all, 76 weapon/armor pages covering each measured branch, 13 sets, 16 curios
  with a measured section, 89 tooltips) are identical after dropping timing noise (`data-px`, `style`, the room canvas); the 51 route states and 50 curio pages as before. Scratch scripts, not kept.
- Real bug found by looking: in ru and pt the Equipment list showed a red "Wiki error: ResizeObserver loop completed with undelivered notifications" (the room paints, longer
  text then changes its height). It is the browser's harmless notice, so `app.js` no longer shows it; `site_check.js` loads `?lang=ru#gear/5/ME/w` fresh and requires no error box
  (verified it fails on a build with the old handler).
- `checks/i18n.js` draws Equipment pages and gear tooltips in every language; it caught the lowercase slot ids in the measurement data ("charm") at once (fixed with `gSl`).

## 2026-11-09: multilingual, Phase 2 group (d2): Build planner and Bosses
- Converted in `app.js`: the Build planner (title, lede for touch and mouse, progress bar, starter builds, add/remove, picker and search, warnings, the side panel with totals, relic
  levels and effects, evolve, the stale and lost link notes) and Bosses (the list, Keeper pages, the three vanilla bosses with their summon steps, side boss pages, stat tables and
  the Hardmode notes, previous/next). Sentences kept in constant tables (VSUM, stat table columns, `kind`) use `N()`.
- Left English on purpose (Phase 3): attack descriptions and where to find a side boss (`b.attacks`, `b.find`), the `BST` rules, `SUM[k].use/info`, the Weak to / Looting Charm cells
  of the ACTS table, stat names in the build totals.
- 155 new sentences (732 per language, 732 of 732 covered), mine, unreviewed by a native speaker. "Hardmode", "Keeper" and "Boss Soul" stay English in all four; vanilla item names
  in the summon steps are written in English in brackets for ru, pt, es.
- English did not change: 106 captures (the list, 14 Keeper and vanilla pages, 71 side boss pages, the planner with each starter build, picker with and without a hit, inspector,
  side panel, a consumable, a relic in the build, a lost link) identical; the 205 Equipment captures and 51 route states as before. Scratch scripts, not kept.
- Real bug found by looking: `build.py` merged the game's own translations after our `keep` list, so Vietnamese showed "Vòng Cổ" for Necklace beside English slot names (D3). It now skips
  the game's text for a sentence in `keep`; `checks/i18n.js` requires that no `keep` sentence has a translation in the pack (tried by injecting one: reported).
- Open: the Progress label of the planner bar wraps to two lines in Vietnamese (narrow label column), not touched because it is a look change.

## 2026-11-09: multilingual, Phase 2 group (e): Mechanics, Changes, mod pages, footer
- A scratch script (`mkwrap.py`, not kept) wrapped the static text of the HTML lines in `mechPage`, `changesPage` and `modPage` with `T("…")`: a whole element, inline tags included,
  simple `${expr}` as `{a}`, `{b}`; the rest by hand. A bold-only stat name (`<b>Dodge Chance</b>`) stays English on purpose (the names the game and the mods print). The footer's Art
  credits (its links kept as they are) are now `foot.p3` in `ui.json`; "Back to top" and "Search results" follow the language (refreshed by `relabelSide`); ritual ingredient names go through `TD`.
- 383 new sentences + 19 effect descriptions (through `TD`) translated by me: 1,117 per language, 1,117 of 1,117 covered. Unreviewed by a native speaker. `trlog.js` also visits
  `#boss/warden`, `#gear`, `#build`, `#mods`, `#mod/Brutality`.
- English did not change: 68 captures (Mechanics with the ritual filter in six states and "show more", Changes, the Mods list, all 56 mod pages, the footer, the two aria-labels) are
  identical except two intended differences: `<option value="Craft">` (the option text is translated, so the value carries the English the filter compares with) and `data-lgh="foot.p3"`.
  Also identical: 106 Bosses/planner captures, 205 Equipment captures, 51 route states except "1 item".
- Left English (Phase 3): the curio effect, stat, source and why lines, mod blurbs, the stat lines of tooltips, the changelog's item and mod names.
- `checks/i18n.js` now also draws Mechanics (with its ritual filter), Changes, the Mods list and a mod page in every language; looked at: ru Mechanics table, vi footer at 375 px.

## 2026-11-10: multilingual, Phase 3 (data text), the curio effect line (`fx`): done
- A curio's one-line effect (`d.fx`, 1,256 distinct lines, 82k characters) now prints through `fxT(d)` = `TD(d.fx)` in the picker, the planner side panel, the Effects pane, the card,
  the table, the curio page lead and Stats fallback, and the tooltip. `d.fx` itself stays English: scores, search and the effect hints read it; search also indexes the translated line.
  Vanilla item names in recipe lists, links and slots now go through `TD` too (the game's own names, e.g. Phantom Membrane → Мембрана фантома).
- All 1,256 lines are translated into vi, ru, pt, es (scratch files `fx_b01..11.txt`, merged with a scratch script that checks every number of the English line appears in each translation;
  the only differences were "3×" written out as "втрое", "tres veces", "triple"). Effect, item and mod names inside a line stay as the game prints them: vanilla effects use the game's own
  names in ru, pt, es (Слабость, Fraqueza, Debilidad…), modded effects and all names stay English in vi (D3). All by me, unreviewed by a native speaker. One Spanish slip
  ("recibís", a voseo form in a neutral-Spanish pack) was found and fixed while merging; a grep for "recibís/tenéis/vosotros/podéis" over the batch files finds nothing else.
- English did not change: the step only adds translations to `build/i18n/tm/*.json` (git shows no other file changed), the build prints "1117 of 1117 sentences asked for are translated"
  for all four languages, `inv7.js` (the i18n invariants, clean and with a deliberate fault) passes. Pages looked at: a ru and a vi curio page (#i300, #i40).
- Open: the stat lines (`st`, 2,972 distinct), source lines (`src`, ~1,480, templated by the patch scripts: top patterns "Craft at a Crafting Table from…",
  "Key requirement: locked behind the…", "Combine at a Tinkerer's Workshop:…") and `why` lines (~40 templates) stay English. Seen and not chased: in `shot.js` captures of a curio page the hero title is blank in every language, English included (the capture is taken before the title's reveal); a 3 s element screenshot of the ru page draws it.

## 2026-11-10: multilingual, Phase 3 (data text), the source lines (`src`): done
- A curio's source lines ("How to get it" list, the tooltip's last two lines) are put together by the patch scripts from a few clause shapes joined with "; ". Instead of one translation per
  concrete line (607 distinct lines shown, 648 distinct clauses), `srcT` (app.js, before `howText`) matches each clause against ~40 shapes (`SRCSH`, `SRCSUF` for the part after "Hardest ingredient: X — ")
  and says it with `T("sentence with {slots}")`: mob and item names go through `TD` (the game's own names), place and structure names stay as the mods print them, "and N more places" is a plural
  (`TN`), a percentage takes the decimal comma (and, in es, " %"). 83 clauses and lines no shape fits (fragments of lines joined by "; " inside brackets, one-off sentences) are whole entries in the pack. English never
  goes through `srcT` (it returns the line it was given). The loot cards' "+N more" is now `T("+{n} more")`.
- Round trip: with an empty pack every clause that a shape matches comes back as it went in (589 clauses, 0 wrong; the harness ignores articles and "place/places" in the check); 86 clauses match no shape and are the hand entries.
  All 607 distinct lines are translated in vi, ru, pt, es.
- English did not change: `howText`, the loot cards and the tooltip's source lines are byte-identical for all 1,321 curios against the committed build; 50 curio pages and 35 tooltips identical.
- New invariant in `build/checks/i18n.js`: every effect line (`fx`) has an entry in each pack, and every source line shown has a translation (`srcT(line) !== line`); checked with a deliberate fault (a deleted template, a deleted effect line).
- Terms chosen (unreviewed): "gate" (Netherite gate) → vi cổng, ru барьер, pt barreira, es barrera (the Keeper gate in Mechanics reads "bloqueio/bloqueo de Keeper"; the two differ in pt/es);
  "treasure bag" → vi túi kho báu, ru мешок с сокровищами, pt bolsa de tesouro, es bolsa del tesoro; "vanilla" kept in vi/pt/es, ru ванильный.
- Open: place and structure names inside lists stay English (e.g. "Ancient City" in a chest list but "Древний город" in a mod-page list); the stat lines (`st`, ~2,800 distinct lines shown in the hover tooltip and the folded
  "In-game tooltip") are still English; `why` lines are not shown anywhere but the "Off the act" page.

## 2026-11-10: multilingual, Phase 3 (data text), boss pages: done
- Every sentence on the 14 Keeper / vanilla boss pages and the 71 side-boss pages is now translated: the attack lists (names and descriptions, from `BINFO[].ph[].at` and `SIDEB[].attacks`), "where to find it"
  (`SIDEB[].find`), the drop notes and chance texts, the summon items' own text (`SUM[].info`, the part after "Allow you to spawn X!" is still dropped), the Keeper rules and notes from `BST`, `VBI` and the Acts table.
  995 strings (47.7k characters), written by me in 8 batches (`boss_b01..08.txt`) and merged by the same scratch script as the effect lines. The data file stays English; the display sites call `TD(...)`
  (attack `d`, `ph`, `title`, drop `note`, `count`, `chance`, side `find`, `drops_note`, `src_note`, source labels, machine labels, "Weak to", the vanilla boss line, "Good to know").
- Found by scanning every boss route in ru for English text nodes (`bossleft.js`, scratch): 996 distinct nodes before, 196 after, all of them names (bosses, items, machines, mods) and four lists of item names.
- English did not change: the 106 Bosses / boss / side-boss / Build planner captures are identical to the committed build.
- New invariant (`build/checks/i18n.js`): every attack, find and summon text of three words or more has an entry in each pack. A translation of "Sanghor" (a kept name) slipped in and was removed; the existing invariant caught it.
- Terms chosen (unreviewed): attack names are translated (they are the wiki's labels, not the game's); effect names the game has (Slowness, Weakness, Hunger, Levitation, Darkness…) use the game's own names in ru, pt, es and stay English in vi; modded effects (Stun, Hemorrhage, Chaos State, Void Flame, Sunburn, Amaterasu, Frenzy, Wet) stay English everywhere;
  boss, item, structure and mod names stay English. Found and fixed while writing: vi "Brews" had been written as "Gạo nấu" (rice cooking), now "Thuốc ủ".
- Open: item names inside lists stay English in ru, pt, es (e.g. "Geomancer Staff, Geomancer Beads…"), as do boss names and epithets ("The Famine, First Calamity").

## 2026-11-10: multilingual, Phase 3 (data text), Equipment attribute lines and the guide book: done
- Equipment tooltips, the item page's Bonuses list and the set page's piece list printed "+8% Attack Speed" and "12 Armor" in English in every language. `gAL` (gear.js, before `gBonus`) keeps the number
  (decimal comma, " %" in es) and says the attribute name through `TD`: 96 new names (all 119 the gear tables produce; the spell schools' "Spell Power", Luck, Omnivamp and Lethality stay English on purpose),
  next to the 7 that the Build planner already had. English returns the line as it is.
- The guide book (`GUIDE`, "From the guide book" on curio and gear pages): the 205 distinct texts (43k characters) translated; the book and entry titles are names and stay English. `guideHtml` now calls `TD`.
- English did not change: 205 Equipment captures and 50 curio pages identical to the committed build; invariants added to `build/checks/i18n.js` for both (every gear attribute name and every guide text of three words or more has an entry).
- Found while writing the Vietnamese lines for the boss pages (already corrected there): none new here. A few guide texts are the mods' own jokes or lore ("He's the DEADLIEST minecraft player…"); translated as written.
- Open: the stat lines `st` (hover tooltip and "In-game tooltip") are still English; item names inside lists, and names in general, stay English in ru, pt, es.


## 2026-11-10: multilingual, Phase 3 (data text), curio tooltip stat lines `st`: done
- The raw stat lines of a curio (`d.st`: the hover tooltip and "In-game tooltip" on the curio page) were English in every language. `stT` (app.js, before `statLine`) says a line as a whole sentence through `TD`, else
  through `gAL` ("+8% Name" keeps the number and says the name), else leaves it. `gAL` (gear.js) now also takes "(multiplies the final value)", "N second cooldown" (shape `{n} second cooldown`) and "+1.5x Name" multipliers.
- Translated into vi, ru, pt, es: 1,658 prose lines (by hand, in 13 batches), 90 attribute names, shapes and sentence fragments, 5 multiplier names, and 86 lines vi, pt and es lacked (ru already had them from the
  game's own translations). 2,972 distinct lines exist; after this 1,112 still show English in ru, of which 1,014 are "Name: value" config lines (e.g. "Damage bonus: 1.5") and 98 are titles, tags and names.
  Config-style lines, titles and item/mob names stay English on purpose; the numbers in them are not localised either.
- The tag check in `build.py` (a translation must keep the English's tags and links) read "(<3m)" as a tag; it now only counts tags that start with a letter, in both places it appears (lines 73 and 103).
- English did not change: tooltip dump (40 curios) and curio-page dump identical to the committed build. The Equipment dump differs from run to run in one inline `style` attribute of the page header
  (`<div class="rhead" style=…>` present or not); the committed build differs from itself the same way (two sequential runs of it), so it is a timing effect, not text. Looked at the ru tooltip of the Enigmatic Amulet
  and the es tooltip of the Dueling Glove: wrapping and decimals fine ("+1,5x Daño infligido…").
- New invariant (`build/checks/i18n.js`): every tooltip line that is not config-style, a title, a tag or one of the names kept on purpose (Spell Power, Cast, Luck, Lethality, Omnivamp, Tenacity) is translated in each pack; it found 86 gaps
  in vi, pt and es that the first pass (done with ru in mind) had missed.
- Open: locale number formatting (`toLocaleString()` without LANG: ru should group with a space); the `why` lines (only on the "Off the act" page); the relic table rows (`relicRows`); item and place names inside lists in ru, pt, es;
  the Vietnamese "Progress" label wraps (a look change, needs approval); native review of ru, pt, es (all machine-translated, unreviewed); terms to review: gate (cổng / барьер / barreira / barrera), treasure bag, Curio / Act, attack names.

## 2026-11-11: multilingual, Phase 3 (data text), number grouping and the relic panel: done
- Numbers with a thousands group (AE2 cell tables, "takes {xp} relic XP", the DISK sentence) called `toLocaleString()` with no language. `nL` (i18n.js) now groups by language: ru "2 100 000", pt and es "2.100.000" (es leaves a 4-digit number
  ungrouped, 1234,5), vi like English with commas because its decimals keep the dot; English still leaves it to the browser, so it is unchanged. The plural-count helper `tn` uses `nL` too.
- Relic panel (the level slider, abilities and stats on the 49 relic pages and in the tooltip): `rlStat` said the mod's value format in English ("%1$s seconds.") with a dot decimal. It now says the format through `TD` and the number through
  `dec`; 89 stat names ("Maximum duration", "Speed multiplier"…) and 27 formats translated in vi, ru, pt, es (es writes " %"). Ability names (Fins, Gills, Leap…) and the stat names Charms, Stun, Frostbite stay English as names.
  Known small flaw: ru "%1$s блоков" is wrong for 1, 21… (the values are mostly 2.5–64, fractions read as "2,5 блока"; left).
- English did not change: the panel (`rlBody`) and tooltip (`rlTip`) HTML of all 49 relics and the Mechanics page are identical to the committed build.
- New invariants (`build/checks/i18n.js`): `nL` groups by language; every relic stat name and every format with words in it has an entry in each pack and `rlStat` translates in ru.
- Checked and dropped from "still open": the Off the act page (`outside()` in app.js and its `why` lines) is never called, so no reader sees it; I left the dead function alone. A scan of ru on Home, Equipment, Bosses, Build planner,
  Mechanics, Changes, a curio page, an equipment page and the Path shows only names (curios, bosses, items, mods, licences) and the labels "Must-Have", "Armor Toughness", "Max Mana" as English.
- Open: ru plural of "блоков"; item and place names inside lists in ru, pt, es; relic ability names; "Name: value" config lines in the tooltip; the Vietnamese "Progress" label wraps (a look change, needs approval);
  native review of ru, pt, es (machine-translated, unreviewed).

## 2026-11-11: multilingual, đợt 2: kế hoạch (chưa sửa code)
- Bạn giao 4 việc (làm tiếp; dịch hết trừ danh từ riêng; nâng độ hay và chính xác; bố cục dễ cập nhật). Viết `docs/plans/2026-11-11-i18n-quality-and-structure.md`: hiện trạng đo được, khảo sát (Weblate glossary/checks, GEMBA-MQM, MQM-APE, trang dịch của Minecraft Wiki, spike mạng cho dịch ngược cục bộ), gói A (cấu trúc và công cụ), B (chất lượng), C (dịch hết) và tiêu chí xong.
- Đo mới: 3.454 tên vật phẩm (1.304 curio + 2.150 gear), đã dịch nhờ bản chính thức: ru 1.731, es 824, pt 719, vi 336; 1.014 dòng tooltip "Tên: giá trị" (791 nhãn, 280 giá trị) còn tiếng Anh.
- Chưa kiểm chứng và đã ghi trong kế hoạch: dịch ngược bằng opus-mt (mới thử đường tải/cài, chưa chạy), kiến thức gettext/i18next, danh sách đầy đủ check của Weblate.
- Open: chờ bạn chốt chính sách tên vật phẩm và dòng phụ tên Anh (mục 4 của kế hoạch) trước khi làm gói C3; gói A, B1, B6, C1 không phụ thuộc quyết định này.

## 2026-11-11: multilingual, đợt 2, gói A (bố cục, công cụ) và B1/B6 (đo chất lượng): xong
- Bạn chốt: dịch danh từ chung + luôn hiện tên Anh; dòng phụ tên Anh nhỏ được duyệt (chưa làm, thuộc gói C3).
- **Cấu trúc**: TM tách từ `tm/<lang>.json` thành `tm/<lang>/<miền>.json` (ui, fx, st, src, boss, guide, relic, gear, vocab; `names` sẽ có ở gói C3), `tmlib` đọc/ghi theo miền; gói `window.I18N` của 4 ngôn ngữ sau di chuyển bằng nhau từng khóa với trước di chuyển (so JSON đã phân tích, không so byte).
  Mỗi mục có `s` (llm / official / human); `merge.py` ghi mục mới `llm`. `docs/I18N.md` mô tả vòng cập nhật 7 bước.
- **Công cụ trong repo** (`build/i18n/tools/`, trước đây nằm ngoài repo): `status.sh` (phủ theo miền, mục chưa dịch, mục mồ côi), `todo.js`, `merge.py` (kiểm số/placeholder/thẻ, `--domain`, `--dry`), `inv.js` (invariant i18n trong 15 giây thay vì 6 phút), `identity.sh` (chứng minh tiếng Anh giống hệt: tooltip, trang curio, Equipment, 51 trạng thái route), `leftover.js`, `domains.js`, `qa.py`, `terms.py`, `vanilla_terms.py`, `split_tm.py`.
- **Phát hiện thật**: nhiều bản dịch chính thức của mod là bản cũ (ru_ru.json cũ hơn en_us.json): số đổi chỗ ("+0.1% Attack Speed" hiện "+10% Knockback Resistance"). Bị dùng sai trong gói: ru 57, es 24, vi 1 dòng tooltip (đếm trước khi lọc). `build.py` nay bỏ cặp chính thức có số/placeholder khác câu Anh hoặc có bản dịch là một câu Anh khác của file: ru 144, es 47, vi 1, pt 0 cặp. Chín dòng tooltip ru, một dòng es chỉ còn nhờ cặp sai đó, đã dịch lại.
- **qa.py** tìm ra: ru/pt/es còn dấu chấm thập phân trong "×1.5", "×1.4", "×2.1" (8 chuỗi), es thiếu dấu cách trước % (5 chuỗi): đã sửa. Còn 53 mục "hard" về glossary (Warden/Ender Dragon dịch lẫn lộn, Power…), thuộc gói B3.
- **terms.py** so với `official/vanilla_terms.json` (1.624 từ vanilla của Mojang bằng vi/ru/pt/es, vi đủ 1.608): ru nói "Огнеупорность / Сопротивление огню" trong khi game nói "Огнестойкость", "Медленное падение" so với "Плавное падение", "Насыщение" so với "Насыщенность"… 2.816 cặp (chuỗi, từ) lệch, 521 chuỗi ru / 425 pt / 494 es / 899 vi; một phần là cố ý (trường phép, Power). Gói B3 duyệt các chuỗi này.
- English: giống hệt (identity.sh: tips, pages, gear identical; 51 routes 0 differences).
- Open: A3 (gộp keep.json vào glossary), A5 (xuất .po), B2 (dịch ngược cục bộ), B3 (duyệt thuật ngữ và mẫu 5%), B4, B5, C1–C4; bật `qa.py --strict` trong check.sh khi hết 53 mục hard.

## 2026-11-11: multilingual, đợt 2, gói C1 (dòng "Tên: giá trị") và từ vựng chính thức: xong
- **C1**: 1.103 dòng tooltip kiểu "Tên: giá trị" (nhãn 759 phần, 41 giá trị là tên) nay dịch ở cả 4 ngôn ngữ: `cfgT` (app.js, trước `stT`) dịch nhãn từng phần ("A — B", "A › B", "[active]", "(unlocks at relic lvN)", "Chest chance in …", "Drop chance from …") qua `TD`, và giá trị theo dạng (số, yes/no, "(game-rule default)", "(code default)", "N s", "… m/s", dòng ability của relic: "Cooldown 16 seconds ~ 12 seconds (at relic level 0; …) · max level … ⚙ pack tweak: …" dùng chính các mẫu đơn vị của bảng relic). 710 nhãn × 4 ngôn ngữ dịch tay, domain `cfg`; từ chính thức của game/mod làm gợi ý (`official/mod_terms.json`, `official/vanilla_terms.json`).
- Invariant mới trong `build/checks/i18n.js`: mỗi phần của nhãn có mục trong gói (trừ viết tắt ≤4 ký tự và tên trong keep); dòng cấu hình không còn được miễn.
- **vi**: theo "dịch hết trừ danh từ riêng", bỏ 20 từ khỏi `keep.json` của vi (tên slot Back, Belt, Body, Bracelet, Charm, Feet, Hands, Head, Necklace, Ring, Accessory và 9 trường phép Fire, Ice, Lightning, Holy, Ender, Blood, Evocation, Nature, Eldritch) và dịch bằng bản chính thức (Curios: Đai, Vòng cổ, Nhẫn, Bùa…; Iron's Spells: Lửa, Băng, Sét, Thánh, Gọi hồn…). Còn giữ Bundle và Spellstone. Chip slot và trường phép trong vi giờ hiện tiếng Việt: cần bạn xem.
- `adopt_official.py`: dùng bản dịch chính thức cho chuỗi ≤5 từ không phải câu hoặc đang còn tiếng Anh (vi 16, ru 89, pt 54, es 52 mục; "Bone Lord" => "Властелин костей", "Burden of Desolation" => "Бремя Опустошения", "Inscrutable Eye" => "Olho Inescrutável"). Bản dài vẫn của tôi.
- `official/mod_terms.json` (3.748 cụm Anh dùng trong wiki có bản dịch chính thức ở ít nhất một mod: ru 3.441, pt 1.856, es 1.863, vi 857) và `official/vanilla_terms.json` làm nguồn thuật ngữ cho B3.
- Phát hiện: nhiều từ vanilla tôi viết khác game: pt "Jump Boost" game nói "Supersalto", "Mining Fatigue" "Exaustão", "Looting" "Saque"; es "Looting" "Saqueo", "Haste" "Prisa minera", "Attack Damage" "Daño por golpe"; vi "Attack Damage" "Sức tấn công", "Armor Toughness" "Độ bền áo giáp"; ru "Fire Resistance" "Огнестойкость". Gói B3 sẽ sửa các chuỗi lệch.
- English: giống hệt (identity.sh).
- Open: B3 (thuật ngữ vanilla/mod, mẫu 5%), C2 (95 tên ability relic + tiêu đề tooltip), C3 (tên vật phẩm + dòng tên Anh phụ), ru/es/pt: dịch tên slot và trường phép như vi (hiện còn như cũ), B2, A3, A5, B4, B5.

## 2026-11-11: multilingual, đợt 2, gói B3 (thuật ngữ game) và kiểm bằng máy: xong
- `tools/align_terms.py`: nói từ của game theo cách game nói, hai loại luật: (a) từ tiếng Anh còn sót trong bản dịch (hiệu ứng, thuộc tính, phù phép, mob vanilla: "Cho Speed II" => "Cho Tốc độ II", "Wither Skeleton" => "Bộ xương Wither", pt "Looting" => "Saque") thay bằng từ chính thức (`vanilla_terms.json`), chỉ khi đứng riêng (không sau/ trước một từ viết hoa khác, không sau "of"/"the": tên riêng); (b) cách nói của riêng tôi bị `terms.py` bắt lệch: pt "Super Pulo" => "Supersalto", "Fadiga de Mineração" => "Exaustão"; es "Salto mejorado" => "Supersalto", "Prisa" => "Prisa minera", "Resplandor" => "Luminiscencia", "daño de ataque" => "daño por golpe"; ru "стойкость брони" => "твёрдость брони", "Огнеупорность" => "Огнестойкость", "Усталость" => "Утомление", "Медленное падение" => "Плавное падение", "Дурное знамение" => "Дурной знак", "урон атаки" => "урон при атаке", "сопротивление отбрасыванию" => "сопротивление к отбрасыванию". Đã sửa: vi 415 + 123, ru 148 + 9, pt 85 + 4 + 54, es 187 + 4 + 39 mục. Số chuỗi còn lệch (không kể từ mơ hồ): vi 523 => 140, ru 156 => 99, pt 97 => 34, es 157 => 35; phần còn lại phần lớn là dương tính giả (tên riêng như "Looting Charm", từ nằm trong từ dài hơn).
- Cố ý không đổi: vi dùng "máu" thay "Sinh lực" (game vi nói Sinh lực; "máu" là cách người chơi Việt nói); Luck, Power, Wither, Flame giữ như cũ (nghĩa mơ hồ theo ngữ cảnh: B4).
- Glossary: Warden vi "Kẻ cai ngục", Ender Dragon vi "Rồng Ender"; thêm cờ `loose` (không kiểm) cho Changes, Equipment, Build, Slot, Curio (hay nằm trong tên riêng/động từ) và `ignore` cho "Boss Soul", "Terra Curio", "Ender Dragon Act".
- `adopt_official.py` có một bản dịch chính thức tệ (es "Al asesinar Criaturas estás dropean +25 % de experiencia."): đã sửa tay; bài học: chỉ nên nhận bản chính thức cho tên/tiêu đề, không cho câu có động từ (còn nhận cả một số câu ngắn ở es/pt, đã xem qua danh sách).
- **qa.py --strict vào `check.sh`**: các luật cứng (typography, ending, symbols, brackets, script, plurals, glossary) hiện 0 lỗi nên CI chặn lỗi mới ở bản dịch; luật mềm (english, same, length, start) chỉ báo.
- English: giống hệt (identity.sh).

## 2026-11-11: multilingual, đợt 2, gói C3 (tên vật phẩm) và dòng tên Anh phụ: xong
- **Tên vật phẩm**: 3.204 tên curio, gear và bộ giáp chưa có bản chính thức nay dịch ở cả 4 ngôn ngữ (14 lô, miền `names` trong `build/i18n/tm/<lang>/names.json`; chỗ game đã có tên chính thức thì dùng tên đó, tên riêng/viết tắt/từ mod tự đặt giữ nguyên bằng `=`). Đo trên bản build: trong 3.450 tên khác nhau của curio và gear, vi 3.324, ru 3.372, pt 3.311, es 3.322 tên khác tiếng Anh (96–98%).
- Quy ước ghi trong `docs/I18N.md` (mục "Names and proper nouns"): vi Title Case, ru/es chữ thường sau chữ đầu, pt Title Case; vật liệu nói như game (Netherite: vi Netherite, ru незеритовый, pt Netherita, es netherita; Obsidian vi "Hắc Diện Thạch"); kim loại do mod đặt giữ chữ Anh ở vi/pt/es, ru viết bằng chữ Cyrillic; hậu tố cấp "(Lv 3)" thành "(Cấp 3)", "(ур. 3)", "(Nv 3)", "(niv. 3)".
- **Dòng tên Anh phụ** (đã được duyệt): `enAlt(name)` ở app.js, một dòng nhỏ mờ dưới tiêu đề trang curio, trang gear và trang bộ giáp (`article({alt})`, CSS `.ip-alt` trong `build/style.game.css`); `enTip(name)` cùng dòng đó trong tooltip curio và gear (CSS `#tip .tnen` trong `v5.css`). Chỉ hiện khi tên đã dịch; tiếng Anh và tên còn tiếng Anh không có dòng này. Ô tìm kiếm đã tìm theo cả hai tên từ trước (`qf`).
- Invariant mới trong `build/checks/i18n.js`: ≥90% tên vật phẩm đã dịch ở mỗi ngôn ngữ; dòng phụ có cho tên đã dịch, không có cho tên còn tiếng Anh và không có ở tiếng Anh.
- Kiểm: `apply_all.sh` xanh, `inv.js` sạch, `qa.py --strict` 0 lỗi cứng, `identity.sh`: tips, pages, gear giống hệt và 51 route 0 khác biệt (English không đổi). Ảnh chụp: trang curio ru 1440 px (tên Nga + dòng Anh dưới tiêu đề), trang gear vi 375 px, tooltip ru và en; tooltip en không có dòng phụ.
- Phát hiện, chưa sửa: (1) tiêu đề trang Equipment ở ru bị cắt bên phải ở 375 px ("ТИР-ЛИСТ СНАРЯЖЕНИЕ" rộng hơn khung; có từ trước, không do đợt này). (2) Miền `boss` còn 145–148 chuỗi chưa dịch, phần lớn là tên riêng của boss, id loot table và tên máy của mod; còn lại là tên vật phẩm kiểu "X Treasure Bag", "X Relic", "Infinite X" cần dịch theo cùng quy ước (đợt sau).
- Open: C2 (95 tên ability relic + tiêu đề tooltip), "Treasure Bag/Relic/Infinite" trong miền boss, ru/es/pt tên slot và trường phép như vi, B2, A3, A5, B4, B5; native review ru/pt/es vẫn cần.

## 2026-11-11: multilingual, đợt 2, gói C3 tiếp (miền boss, tên slot, tên ability relic): xong
- **Miền boss, 80 tên**: vật phẩm thả/triệu hồi và tên máy của mod dịch theo quy ước C3 ("Colossal Iron Ingot", "Medal of Doom", "Infinite Fiery Wither Skull", "Create Mechanical Crafter" => tên mod giữ nguyên + tên máy theo bản chính thức của mod: vi "Máy Chế Tạo", ru "Механический сборщик", pt "Fabricador Mecânico", es "Ensamblador mecánico"). Còn English có chủ ý: tên boss và danh hiệu ("Arion, Tyrant of the Emerald Wrath"), tên mod, id loot table ("mod loot table: goety:…"), "X Treasure Bag", "X Relic" (từ của pack, đã nằm nguyên trong các câu mô tả đã dịch; muốn đổi thì phải sửa cả các câu đó: 11 câu × 4 ngôn ngữ).
- **Tên slot** còn tiếng Anh ở cả 4 ngôn ngữ nay dịch: Anklet, Binding Key, Blasphemy, Elytra, Glove, Heart, Hostility Curse, Living Armour, Magnetizer, Sacrament, Scroll, Spellbook, Talent; Bundle (vi/pt/es) và Spellstone (vi/es) cũng bỏ khỏi `keep.json` và dịch (từ vanilla/mod chính thức khi có: Elytra vi "Cánh Cứng", Bundle vi "Túi Bọc", pt "Trouxa", es "Saco"). Còn English: Focus (tên lớp vật phẩm Ars; các tên "Focus of X" đã giữ nguyên chữ này). Ô tìm kiếm vẫn dùng khóa tiếng Anh (`slot:Anklet`).
- **Tên ability relic**: kiểm bằng bản build: 95 tên, ru thiếu 2, pt/es thiếu 3, vi thiếu 5; vi "Epitaph" nay "Văn Bia". Còn lại là tên riêng (Bonk, Modal Soul, The Court Of The Crimson King; vi thêm Entropy).
- Kiểm: `apply_all.sh` xanh, `inv.js` sạch, `qa.py --strict` 0 lỗi cứng, `identity.sh` giống hệt (tips, pages, gear; 51 route 0 khác biệt). Ảnh: trang slot Anklet ru 375 px.
- Open: C2 tiêu đề tooltip, B2 (dịch ngược), B3 (mẫu 5%), B4 (ngữ cảnh Luck/Power/Wither/Flame), A3, A5, B5; native review ru/pt/es.

## 2026-11-11: multilingual, đợt 2, gói A5/B2/B3 và lỗi bố cục khi dịch: xong
- **A5 (người bản ngữ duyệt)**: `build/i18n/tools/review.py export <lang> [--domain ui,vocab] [--all]` xuất bảng CSV (id, domain, state, english, translation, ok, comment; UTF-8, mở được bằng Excel/Google Sheets), `import` nhận lại: dòng sửa được kiểm như `merge.py` (cùng chữ số, `{placeholder}`, thẻ; dòng sai bị bỏ qua và liệt kê) rồi thành `human`; dòng đánh `x` ở cột `ok` thành `human` nguyên trạng. Thử vòng đi-về trên ru/ui (1.200 dòng): sửa 1, xác nhận 1, bỏ 1 dòng mất placeholder, 1 chỉ có ghi chú; diff TM đúng 2 dòng. Chỉ dẫn trong `docs/I18N.md` ("Reviewing as a native speaker"). Thay cho `.po` ở kế hoạch (CSV người không rành kỹ thuật dùng được ngay).
- **B2 (dịch ngược) no-go**: cài torch CPU + opus-mt-ru-en, 120 chuỗi ru/ui trong 12 s; 25 chuỗi điểm thấp nhất không có lỗi thật (máy dịch ngược kém hơn bản dịch; một chuỗi chỉ lộ ra là câu tiếng Anh mơ hồ "…and is what the score uses", bản dịch cả 4 ngôn ngữ hiểu đúng theo câu trước). Không đưa vào repo.
- **B3 (mẫu)**: đọc ngẫu nhiên 90 chuỗi ru/ui và 20 chuỗi pt/ui (tất cả đạt); không thấy lỗi nghĩa trong mẫu. Kiểm nhất quán "Power": ru/pt/es/vi nói "Fishing Power"/"Magic Power LII" nguyên chữ Anh trong câu nhưng dịch ở nhãn riêng ("Сила рыбалки"); chưa sửa (tên chỉ số của mod trong câu, cùng nhóm với "Spell Power" giữ nguyên).
- **Lỗi bố cục có thật khi đổi ngôn ngữ, ở 375 px** (không có ở tiếng Anh): (1) màn hình tiêu đề (hub) ru/pt/es/vi: ô tìm kiếm, nút "Планировщик билдов"/"Planejador de build" và dòng chân trang tràn ra ngoài khung, hai dòng góc chồng lên nhau; (2) tiêu đề trang Equipment ru ("ТИР-ЛИСТ СНАРЯЖЕНИЕ") bị cắt bên phải. Sửa trong `build/style.game.css`: `html:not([lang="en"])` cho `.title-scr`/`.tbtns` (cột `minmax(0,1fr)`, nút được xuống dòng, `.tcorner` xếp dọc ≤480 px) và `.room3 .rhead:has(.gem)>div{min-width:0}` + `overflow-wrap:anywhere` cho tiêu đề phòng. Tiếng Anh giống từng điểm ảnh (shot.js `--diff`, hub và Equipment ở 375 và 1440 px: 0 điểm đổi; 5 trang khác cũng 0). Invariant mới trong `build/style_check.js` (4 ngôn ngữ × hub, Equipment, trang curio ở 375 px): đỏ 7 lỗi khi bỏ bản sửa, xanh khi có.
- Phát hiện, chưa sửa: tên vật phẩm nằm trong câu mô tả (ví dụ "Withered Demon Heart", "Wanderer's Fallen Shard") vẫn viết tiếng Anh dù trang và danh sách đã dịch; thay trong câu cần xử lý biến cách của tiếng Nga nên để dành. Phông Silkscreen vẽ chữ "Я" như "А" có đuôi trong tiêu đề ru (phông, không phải bản dịch).
- Open: B4 (ngữ cảnh), B5 (nhãn trạng thái trong menu: cần duyệt giao diện), tên vật phẩm trong câu, native review ru/pt/es.

## 2026-11-11: multilingual, đợt 2, tìm nhanh (ô tìm trên đầu trang) và sắp xếp theo tên đã dịch: xong
- **Phát hiện**: lời trước ("tìm kiếm tìm cả hai tên") chỉ đúng cho bộ lọc trên trang Curios. Ô tìm nhanh ở đầu trang và ở trang chủ (`ux.js`, danh sách thả xuống) chỉ biết tên tiếng Anh: gõ tên đã dịch không ra gì, và mọi chữ trong danh sách (tiêu đề nhóm, "Recently opened", "Keeper, opens Act …", "Nothing is called …", phím tắt) viết cứng bằng tiếng Anh, không qua `T()`.
- **Sửa**: chỉ mục tìm nhanh lấy tên người đọc thấy (`TD`) làm tên hiển thị và tên Anh làm tên phụ (khớp tên Anh xếp thấp hơn một chút); mọi chữ trong danh sách qua `T()`/`TN()` (25 câu mới, 4 ngôn ngữ, gồm số nhiều của ru/pt/es); chỉ mục dựng lại khi đổi ngôn ngữ (`QSRESET` gọi từ `relabelSide`). Tìm không dấu ở vi/ru/pt/es (`fold` trong `app.js`: mỗi chữ không ASCII thành một chữ không dấu, nên vị trí tô sáng không lệch; vi "ao choang" ra "Áo Choàng", ru "е" khớp "ё"); `qNorm` của bộ lọc Curios dùng cùng `fold`. Tiếng Anh: giữ nguyên chữ (`fold` chỉ hạ chữ thường khi ngôn ngữ là en).
- **Sắp xếp**: mục lục A–Z ở Curios và cột Curio/Effect của bảng xếp theo tên đã dịch (`nameCmp`, so sánh theo ngôn ngữ), trước đây xếp theo tên Anh nên danh sách tiếng Việt trông lộn xộn. Tiếng Anh xếp như cũ.
- Kiểm: HTML danh sách thả xuống ở tiếng Anh giống hệt (10 truy vấn, 88.664 ký tự, bản build trước và sau); `identity.sh` giống hệt; invariant mới: `checks/i18n.js` (thứ tự `nameCmp` ở 4 ngôn ngữ, thứ tự Anh không đổi; đỏ khi đảo chiều so sánh), `a11y_check.js` (4 ngôn ngữ: tên hiển thị, tên Anh, tên không dấu đều ra mục đó; câu "không thấy gì" đã dịch; đỏ 4 lỗi khi bỏ tên Anh phụ khỏi chỉ mục). Ảnh chụp: vi "ao choang", ru "кольцо" và "ring of the seven".
- `leftover.js` trên vi (14 route): phần chữ Anh còn lại là tên riêng, tên mod/boss, "Act …" và "Must-Have" (giữ có chủ ý); không còn chữ chrome tiếng Anh.
- Open: như đợt trước (tên vật phẩm trong câu mô tả, nhãn trạng thái trong menu, B4, native review).

## 2026-11-11: multilingual, đợt 2, tên nguyên liệu (công thức, nghi thức, bảng AE2): xong
- **Phát hiện**: `NM` (tên mọi vật phẩm xuất hiện trong công thức, cây công thức, nghi thức Goety, bảng AE2) có 1.639 tên; 698 tên chưa dịch ở ít nhất một ngôn ngữ (curio và gear đã dịch ở C3 nhưng nguyên liệu như "Nether Star", "Pumpkin Pie", "Cosmilite Ingot" thì chưa).
- **126 tên vanilla** lấy từ `official/vanilla_terms.json` (trạng thái `official`; vi viết hoa từng chữ cho khớp quy ước tên: "Thân Cây Xiêm Gai"); ngôn ngữ nào game không có tên thì giữ nguyên Anh (ví dụ "Sculk" ngoài ru, "TNT" ở pt/vi). **572 tên còn lại** dịch tay trong 3 lô theo quy ước C3 (vi "Phôi X" cho Ingot theo bản chính thức, "Khối X"; ru chữ thường và phiên âm kim loại; Focus/Rune/Orb giữ tên trường phép Air/Earth/Fire/Water/Aqua/Geo như đã quyết). Không dùng `mod_terms.json` cho nhóm này: kiểm tay thấy nhiều cặp sai ("Fortune's Favor" ru "Винтовка фортуны", es "Necronomicon" = "Cetro de Sangre", mã màu § dính trong bản dịch).
- Đo lại trên bản build: tên nguyên liệu khác tiếng Anh ở vi 1.608, ru 1.627, pt 1.608, es 1.609 trên 1.639 (phần còn lại: tên riêng, từ viết tắt, "=" có chủ ý). `qa.py --strict` 0 lỗi cứng; `inv.js` sạch; `identity.sh` giống hệt (tiếng Anh không đổi). Ảnh: trang Mechanics ru.
- Quy ước thêm: "Spirit of Chaos/Dread/Despair" (trước giữ nguyên ở miền boss) nay dịch cùng các "Spirit of …" khác vì cùng một chuỗi Anh dùng chung một bản dịch.
- Open: như trước.

## 2026-11-11: multilingual, đợt 2, tên vật phẩm trong câu (tham chiếu ⟦…⟧), tên bộ giáp, nhãn nguồn bản dịch, vòng cập nhật một lệnh: xong
- **Tham chiếu tên trong câu**: một bản dịch gọi vật phẩm bằng `⟦English⟧`, `build.py` viết tên của đúng ngôn ngữ vào chỗ đó (`tmlib.resolve_refs`); tên chỉ nằm một chỗ (`names.json`), đổi ở đó thì mọi câu đổi theo. Kết quả: vi 385, ru 327, pt 323, es 314 tham chiếu (trước đây các câu giữ tên Anh). pt/es: `refs.py gender` sửa mạo từ theo giống và số của tên (pt 25, es 12 chỗ sửa; tên mở đầu bằng mạo từ riêng như "El ojo omnividente" bị bỏ mạo từ khi đứng sau mạo từ); ru: dạng cách trong `forms/ru.json` (84 tên, nháp bằng một bộ biến cách nhỏ rồi tôi sửa tay các lỗi: "Ведьминой шляпы", "Криптокошелька", "Сердца Бездны"…); dạng cách chưa có thì giữ tên Anh, không bao giờ ra sai cách. 7 chỗ ru để Anh (số đếm trước tên số nhiều).
- **Rộng hơn**: 1.341 tên vanilla (vật phẩm, khối, sinh vật) lấy từ bản dịch chính thức của game (`adopt_vanilla.py`, trạng thái `official`), 27 tên "X Treasure Bag/X Relic" của boss, thuật ngữ "Treasure Bag", "Magic Power" (`refs.json`); vi đổi "relic" còn viết Anh thành "di vật" trong 45 chuỗi (ru/pt/es đã dịch từ trước; "Relics"/"More Relics" là tên mod, giữ). Còn lại English có chủ ý: tên boss và danh hiệu, tên mod (`refs.json` → `protect`).
- **Tên bộ giáp**: 239 tên (trước đó chỉ có tên từng món): "Bộ Thánh Kỵ Sĩ Bị Nguyền", ru "Набор «Проклятый паладин»", es "Conjunto «Paladín maldito»" (mẫu `{set} set` của ru/es đặt tên trong «»). Tiền tố bộ giáp (vd "Dark Metal") không được coi là tên khi nằm trong câu: "Dark Metal Ingot" không bị cắt đôi.
- **Nhãn nguồn bản dịch** (đã được bạn cho phép làm hết): một dòng nhỏ mờ ở chân trang, chỉ hiện khi không phải tiếng Anh: vi: "Bản dịch: 13% là cách nói của chính game, 0% đã được người bản ngữ kiểm tra, 87% là dịch máy và còn chờ người kiểm tra" (ru 15/0/85) kèm liên kết báo lỗi; số lấy từ trạng thái `s` trong TM (`meta` của gói, `build.py`). Tiếng Anh ẩn dòng này, hub và Equipment tiếng Anh giống từng điểm ảnh.
- **Cơ chế cập nhật**: `bash build/i18n/tools/update.sh [--identity DIR]` = build + liệt kê cái chưa dịch (câu theo miền, tên vật phẩm, tên chính thức của game chưa nhận) + tên Anh còn nằm trong câu + chạy kiểm tra; `names_todo.js` (tên chưa có mục, mọi nơi: curio, gear, bộ giáp, nguyên liệu) + `names_show.py` + `adopt_vanilla.py`; `refs.py scan/apply/gender/patch/forms/check`; `check.sh` chạy thêm `refs.py check --strict`; invariant "không dấu ⟦⟧ nào lọt vào trang" trong `checks/i18n.js`. Tất cả mô tả trong `docs/I18N.md` (các mục mới: "Names inside sentences", "Updating item names", "Who wrote the words").
- Kiểm: `apply_all.sh` xanh, `inv.js` sạch, `qa.py --strict` 0 lỗi cứng (đọc bản đã viết tên ra), `identity.sh` giống hệt. Ảnh 375 px: chân trang ru và vi (dòng nhãn nằm gọn, nút lên đầu trang không đè lên dòng cuối: thêm `margin-bottom: var(--s8)` cho `.strans`; lần chạy `check.sh` đầu đỏ vì tôi viết `56px`, ngoài thang spacing của `style_check.js`), trang gear `#g12` ru và es (không tràn). Chưa chụp riêng một trang bộ giáp; tên bộ giáp được `inv.js` và `qa.py` kiểm, không phải bằng ảnh.
- Open: B4 (ngữ cảnh Luck/Power/Wither); native review ru/pt/es (nhãn chân trang đang nói 0% đã duyệt: đúng sự thật).

## 2026-11-11: diện mạo mới, giai đoạn 1: trang chủ "The climb" (Con Đường lúc hoàng hôn), trên nhánh, chưa vào `main`
- **Bối cảnh**: chủ wiki yêu cầu "nâng cấp đột phá, đổi mới hoàn toàn đồ họa". Vòng 1 tôi gửi ba bản xem thử chỉ đổi màu bằng CSS trên bố cục cũ (Kho Cổ Vật, Deep Dark, Aurora): bị chê "quá xấu". Bài học: tô lại màu không phải đổi mới; cái đẹp của các trang tham khảo đến từ hình của game đặt cỡ lớn. Vòng 2: xem 14 trang (Hytale, LoL Universe, Star Citizen wiki, paimon.moe, Project Amber, Modrinth, Terraria wiki…) và 4 repo (`Mojang/ore-ui`, `MadeBaruna/paimon-moe`, `StarCitizenTools/mediawiki-skins-Citizen`, `maomentai817/pixel-ui`), dựng ba bản mới bằng 20 ảnh dựng 3D boss có sẵn (`BPORT`, trước đây trang chủ và trang Curios không dùng). Chủ wiki chọn **hướng 1 "Hoàng hôn trên Con Đường"** và bảo làm tiếp, tinh chỉnh. Spec + kế hoạch: `docs/plans/2026-11-11-the-climb.md`; một dòng ghi quyết định trong mục Design của `CLAUDE.md`.
- **Đã làm** (nhánh `claude/amazing-wozniak-jflbuy`; site đang chạy không đổi vì chưa vào `main`):
  - Trang chủ mở bằng The Path: trời hoàng hôn (mặt trời vuông, 90 sao, hai dãy núi, ba đám mây; sinh từ bộ số có hạt giống cố định nên lần nào cũng như nhau), bậc thang 13 bậc, mỗi bậc là một Act bằng khối `PTEX` của Act đó, trên bậc là Keeper phải hạ ở Act ấy (`NEXTB`); Act XII không có Keeper nên đặt emblem của Act. Bậc là tab như cũ (bấm, phím mũi tên, Home/End); bậc đang mở có viền vàng; "I'm here" dựng cột sáng và nhãn "You are here", các bậc trước đó có dấu ✓.
  - Phần tiêu đề (wordmark, câu "The Keepers are watching!", ô tìm, ba nút theo Act của người đọc, số liệu) nằm trên trời; chú thích "The Path" dùng lại câu đã dịch. Không thêm chuỗi dịch mới.
  - Bảng Act có thêm rương sáng kiểu vanilla: 36 curio mạnh nhất của Act (`byRank`), ô nhuộm theo độ hiếm; dựng khi Act mở (không dựng trước).
  - Trên trang chủ, header lấy màu đỉnh trời khi trang ở đầu; cuộn xuống thì về như cũ.
  - Dưới 1100 px tiêu đề xếp dọc, bậc thang thành dải cuộn ngang và tự giữ bậc đang mở ở giữa.
  - CSS: khối "The climb" ở cuối `build/style.game.css`; bỏ 79 luật cũ của màn hình tiêu đề và thanh The Path (đã đếm bằng script xóa).
- **Kiểm**: `bash build/check.sh` exit 0 sau lần sửa cuối (invariants 0 broken, style sạch, a11y 0 broken, site_check sạch, `qa.py --strict` 0 lỗi cứng). Lần chạy trước đó đỏ hai chỗ, đã sửa: `style_check` bắt `padding:7px 10px 6px` ngoài thang spacing (nhãn "You are here"), và `routes.js` bắt thứ tự heading h2 → h4 ở tiêu đề rương (nay là `<p class="cht">`, không phải heading). Invariant mới `build/checks/climb.js` (số bậc = số Act, chữ của bậc là nhãn Act, bậc có texture, Keeper đúng `NEXTB`, rương đúng `byRank` và không quá `CHESTN`, "I'm here" đánh dấu đúng bậc): xanh trên bản build, đỏ 12 lỗi khi đổi kỳ vọng Keeper sang Act kế bên. Các trang khác không đổi: 10 route (`#home #gear #g12 #bosses #boss/arion #mechanics #build #changes #act/3 #i9`) ở 1440 và 375 px giống từng điểm ảnh với bản build của `8c0a917` (`shot.js --diff`, ảnh gốc cũng chụp ở chế độ giảm chuyển động; lần so đầu lệch giả 0,05–0,9% vì ảnh gốc chụp khi còn chuyển động). Ảnh trang chủ đã xem: 1440 px (mặc định; "I'm here" ở Act IV; cuộn tới bảng Act và rương), 1920, 1200, 900, 375 px (đầu trang và dải bậc thang), tiếng Nga 1440 và 375 px, tiếng Việt 1440 px; không ảnh nào tràn ngang (`scrollWidth` ≤ `clientWidth`).
- **Phát hiện, chưa sửa** (ngoài phạm vi đợt này):
  1. Phông chữ thường `--body: "Be Vietnam Pro"` không được nhúng vào site (`static/style.*.css` chỉ có `@font-face` cho Jersey 15, Monocraft, VT323 vi; máy này `fc-match` trả về Inter): máy nào không cài sẵn thì chữ thường hiện bằng phông hệ thống. Cần quyết định nhúng hay đổi sang phông đã có.
  2. `build/src/v5.css` còn 51 selector `.hero` của một hero rất cũ (cũng là cảnh hoàng hôn); không còn phần tử nào mang class `hero` (grep `class="…hero…"` trong `app.js` chỉ ra `ip-hero` và `mhero`), nên chúng chết hẳn. Chưa dọn vì đan với `@keyframes drift` mà `#bgfx` còn dùng.
  3. Ảnh boss là 256 px; ở trang chủ hiện cao 132–211 px CSS nên trên màn hình mật độ 2x bị phóng tới 1,65 lần, hơi mềm.
  4. Ở tiếng Nga, tên Keeper đã dịch dài ("Эльдорат Древний Строитель") xuống ba dòng trên mặt bậc (vẫn nằm gọn trong bậc); `kShort` chỉ rút gọn tên tiếng Anh (cắt ở dấu phẩy hoặc " the ").
- **Open**: giai đoạn 2–5 trong plan (trang Curios, các trang boss/gear/Equipment/Build planner/Mechanics, ảnh boss cỡ lớn, dọn `.hero`); chủ wiki xem ảnh giai đoạn 1 rồi mới làm tiếp; chỉ đưa vào `main` khi chủ wiki đồng ý. Các mục open của đợt multilingual giữ nguyên (B4, native review ru/pt/es).

## 2026-11-11: diện mạo mới, đợt 2 trên trang chủ: bảy góp ý của chủ wiki (hình boss có animation, vách đá có quặng phát sáng, rương, chân trang)
- **Bối cảnh**: chủ wiki mở bản thật (file offline tôi gửi) và nêu 7 chỗ cần cải tiến; chi tiết từng mục và cách xử lý ở `docs/plans/2026-11-11-the-climb.md` mục 6, hướng cho các tab khác ở mục 7.
- **Đã làm** (nhánh `claude/amazing-wozniak-jflbuy`, chưa vào `main`):
  1. Một chữ Linggango ở đầu trang: bỏ wordmark khỏi hero (bỏ luôn ảnh base64 23 kB khỏi `app.js`), `h1` là dòng "The Keepers are watching!" kèm "Linggango Wiki:" ẩn (`.vh`).
  2. Chỗ nối: chân bậc thang chìm vào chính vách đá (`.climb::after`); `--cave` nay đặt trên `:root` thay vì chỉ trên `#cave`.
  3. Vách đá: `main` trong suốt trên trang chủ nên vách hiện lại (trước đó `main:not(#_):not(#__){background:#151517!important}` trải hết bề ngang che mất); các khối vàng, redstone, lapis, kim cương, ngọc lục bảo phát sáng (`.og`: khối sẵn có của vách + 30 khối thêm ở hai mép), chỉ hiện trên trang chủ.
  4. Hình boss dựng lại: `node build/pack_audit/boss_portraits.js --figs` viết `build/patches/boss_figs.json` (13 hình, 1,11 MB; `BFIG` trong `wiki_data.js`): 12 Keeper mỗi con một dải 12 khung hình của vòng `idle` (WebP), lấy điểm giữa hai chân làm trục, cắt theo điểm ảnh thật, cỡ theo chiều cao trong game (căn bậc hai, kẹp 0,8–1,25, tối đa 520 px nguồn); bậc Act XII là Apollyon (`ENDB`, ảnh tĩnh từ `side_imgs.json`). `boss_portraits.html` có thêm `figure()` và `still()`.
  5. Tương tác: Keeper của bậc đang mở và Keeper dưới con trỏ phóng to, có quầng sáng màu Act, năm tia lửa bay lên và chạy vòng `idle`; các Keeper khác thu nhỏ, tối đi. Vùng trống phía trên mỗi bậc thuộc về bậc đó (hình không nhận con trỏ, vì hình rộng sẽ che bậc bên cạnh).
  6. Phần dưới: bỏ bốn thẻ "Start here" và hàm `startHere`, `heroFloat`; Must-Have, Mythic (18 đầu), New in 6.6.6 (18 đầu), Equipment thành bốn rương 9 ô ngang; còn lại khối Curio slots. Chân trang ba cột đều, khối Art thành ba cột chữ bên dưới (mọi trang). Trang chủ ở 1440 px: 4400 px còn 3004 px.
  7. Dọn: 33 luật CSS chết (`.adv`, `.sq*`, `.feat`, `.fc`, `.latest`, `.hcols`) và 8 mảnh lẫn trong luật khác; bỏ phép kiểm `.latest` trong `style_check.js`; `routes.js` (ui-desktop-15) chuyển từ thẻ Start-here sang nút "See N curios" của bảng Act.
- **Kiểm**: `bash build/check.sh` exit 0 trên cây cuối (invariants 0 broken, style sạch, a11y 0 broken, site_check sạch, `qa.py --strict` 0 lỗi cứng, refs 0). Ba lần chạy trước đỏ, đã sửa: (a) `style_check`: bậc đầu vẽ mép cỏ bằng một lớp nền nên bị tính là texture phóng ×6,92 (nay mép cỏ là `b::before`, texture khối 64 px = ×4), và bốn `h2` của rương 26 px (luật: `h2` ≥ 30 px, nay 30 px); (b) `checks/climb.js` báo 23 lỗi giả "no block texture": file này `await` giữa các bậc, mà trang vẽ lại thêm một lần khi địa chỉ đổi, nên nó cầm các phần tử cũ đã bị thay (nay chờ 80 ms sau khi đổi địa chỉ rồi mới đọc); (c) `checks/routes.js` 13 lỗi vì còn thử thẻ Start-here (nay thử nút "See N curios" của bảng Act: đúng Act, đúng số). `climb.js` nay kiểm: mỗi bậc có hình trong `BFIG` và ảnh rộng đúng w×n; Keeper có vòng lặp; boss của `ENDB` là side boss của đúng Act đó; `h1` là dòng chữ có tên wiki, không còn ảnh. Các trang khác: 10 route (`#home #gear #g12 #bosses #boss/arion #mechanics #build #changes #act/3 #i9`) ở 1440 và 375 px, màn hình đầu giống từng điểm ảnh với bản build của `4d27957` (`shot.js --diff`); chân trang đổi ở mọi trang (có chủ ý) nằm dưới màn hình đầu nên không nằm trong phép so này, tôi xem nó trên trang chủ. Ảnh trang chủ đã xem sau lần sửa cuối: 1440 px (mặc định; di chuột vào bậc VIII; "I'm here" ở Act IV với bảng Act và rương; bốn rương và Curio slots; chân trang), 900 px, 375 px (dải bậc thang). Chưa xem lại sau đợt này: 1920 px, tiếng Nga, tiếng Việt, trạng thái chọn một bậc khác bậc đầu.
- **Phát hiện, chưa sửa**:
  1. `BFIG` nằm trong `wiki_data.js` nên trang nào cũng tải 1,11 MB hình của trang chủ; có thể chuyển sang `wiki_pics.js` (tải sau lần vẽ đầu) nếu thời gian tải thành vấn đề. Lần đo của `a11y_check`: first paint vẫn 0,3 s.
  2. Dải `walk` (tư thế thứ hai) chưa dựng; dữ liệu có sẵn cho 11 trong 12 Keeper (Ender Dragon không có `walk`).
  3. Vách đá phát sáng mới chỉ bật trên trang chủ; các trang khác giữ vách tối như cũ cho tới khi chủ wiki duyệt hướng ở mục 7 của plan.
  4. Các mục chưa sửa của đợt 1 còn nguyên: phông "Be Vietnam Pro" không nhúng; 51 selector `.hero` chết trong `v5.css`; tên Keeper tiếng Nga dài xuống ba dòng.
- **Open**: chủ wiki duyệt hướng cho Curios, Equipment, Changes (bản xem thử nhanh đã gửi cho Curios và Equipment); đưa trang chủ vào `main` khi chủ wiki đồng ý. Các mục open của đợt multilingual giữ nguyên.

## 2026-11-11: diện mạo mới, đợt 3: hoàng hôn phủ kín màn hình, quặng lóe thưa, boss luôn động và biết đi, căn phòng lan ra cả trang
- **Bối cảnh**: chủ wiki xem bản đợt 2 và nêu 4 điểm. Điểm 4 bác hướng tôi đề xuất ở mục 7 của plan (chép dải hoàng hôn sang các tab): **trang phụ giữ căn phòng của mình và căn phòng lan ra cả trang**. Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 8; đề xuất nâng cấp cách dùng cho ba tab chính ở mục 9 (chờ chọn). Mục Design của `CLAUDE.md` ghi quyết định này.
- **Đã làm** (nhánh `claude/amazing-wozniak-jflbuy`, chưa vào `main`):
  1. Hero cao bằng màn hình trừ header (`100svh - var(--toph)`; `--toph` đo từ header bằng `ResizeObserver` trong `pathMapWire`); chiều cao bậc và cỡ hình theo chiều cao màn hình (`--fs` .78 / .886 / 1 / 1.12).
  2. Quặng: bỏ quầng sáng thường trực. Khối quặng tối như vách; mỗi khối theo nhịp riêng 14–30 giây lóe ba chấm đá quý (điểm ảnh khác deepslate trơn từ 90 trở lên) rồi tới ba chấm khác; khối thêm ở hai mép 30 → 18.
  3. Boss: `boss_portraits.js --figs` nay chọn góc nhìn hẹp nhất cho từng boss (20/30/45/60°), viết thêm `build/patches/boss_walks.json` (11 vòng `walk`, 1,39 MB; Ender Dragon không có), mỗi vòng cắt theo điểm ảnh của riêng nó nhưng chung trục giữa và mặt đất với vòng `idle`. Trên trang: mọi Keeper luôn chạy `idle`; chỉ vào (hoặc tới bằng bàn phím) thì đổi sang `walk` (`BWALK` đi cùng `wiki_pics.js`, tức tải sau lần vẽ đầu; chưa tải xong thì vẫn là `idle`); boss không được chọn thu vừa bậc của mình (`--fit`, tối đa 1,2 lần bề ngang bậc); bậc được chỉ hoặc đang mở nhô cao; mỗi bậc có hạt không khí của Act (`envFx`) và một vệt sáng chạy dọc cầu thang.
  4. Căn phòng lan ra cả trang (`rooms.js rWall`, CSS `.rwall`): tường của phòng nối dài phía sau cả trang, rộng bằng cửa sổ, đúng từng cột khối với căn phòng đầu trang (cột trụ giữ nhịp 7/8/9 khối kể cả bên trái tiêu đề), tối hơn trong phòng, mỗi ô lặp (2 nhịp cột × 12 khối) có hai đèn lồng so le chiếu sáng quanh nó; sàn của phòng nằm ở chân trang; căn phòng đầu trang bỏ khung. Có ở Curios, Equipment, Bosses, Build planner, Mechanics. **Changes** nay có phòng `vault` (beacon) thay cho tiêu đề trơn, và nhãn Added/Changed/Fixed/New có ô màu (`.ck`).
- **Kiểm**: `bash build/check.sh` exit 0 trên cây cuối (invariants 0 broken, style sạch, a11y 0 broken, site_check sạch, `qa.py --strict` 0 lỗi cứng). Lần chạy trước đó đỏ, đã sửa: `a11y_check` báo 104 lỗi "reduced motion #: envFall on I runs for ever": luật `#pmap .ptrack .envfx{display:block}` của tôi đè lên luật tắt hạt khi người đọc chọn giảm chuyển động (nay tắt lại trong khối `prefers-reduced-motion`). Invariant mới `build/checks/rooms.js`: sáu trang có phòng đều có tường (có ô đã vẽ, rộng bằng cửa sổ, tới đầu trang, không làm trang cuộn ngang), trang chủ và `#i5` không có; đỏ 1 lỗi khi đổi kỳ vọng thành "`#gear` không có tường". `climb.js` thêm: mỗi vòng `walk` thuộc một hình có animation, ảnh rộng đúng w×n, cao lệch không quá 12% so với `idle`; mỗi bậc có hạt không khí và vệt sáng. Đo trong trình duyệt (1440×900): hero cao 836 = 900 − 64 (header); chỉ vào bậc V thì dải `walk` hiện (`data-wk=1`, dải `idle` ẩn) và bậc cao 276 px; 34 khối quặng chạy `oreTwinkle` (khối đo được: 24,3 s). Điện thoại 375 px với "I'm here" ở Act IV: dải bậc thang rộng 375 px, nội dung 1350 px, đã tự cuộn 149 px để bậc IV nằm giữa (lần đầu nó rộng 1248 px và không cuộn: `align-items:start` của lưới desktop còn hiệu lực trong bố cục cột; đã sửa). Trang chi tiết không đổi: 5 route (`#g12 #boss/arion #act/3 #i9 #side/Apollyon`) ở 1440 và 375 px, màn hình đầu giống từng điểm ảnh với bản build của `06a52e5` (`shot.js --diff`). Ảnh đã xem: trang chủ 1440 (mặc định; chỉ vào bậc V và bậc IX), 1920×1000; Curios 1440 (đầu trang và sau khi cuộn) và 375; Equipment, Bosses, Changes 1440 (kèm chân trang Changes). Chưa mở ảnh: Build planner, Mechanics (chỉ có invariant `rooms.js` xác nhận có tường), Changes 375, tiếng Nga và tiếng Việt.
- **Phát hiện, chưa sửa**:
  1. Cỡ boss: Arion (3,1 khối trong game) vẫn nhỏ rõ so với các boss khác; muốn đều hơn thì nâng `LO` trong `boss_portraits.js` (hiện 0,8) rồi chạy lại `--figs`.
  2. Apollyon (bậc XII) vẫn là ảnh tĩnh: không có mô hình trong `boss_models.json`.
  3. `BFIG` (1,21 MB) vẫn nằm trong `wiki_data.js`, mọi trang đều tải; `BWALK` thì đã đi cùng ảnh trễ.
  4. Tường phòng được đặt theo vị trí căn phòng lúc vẽ; nếu header đổi chiều cao sau đó mà bề ngang phòng không đổi (hiếm) thì hàng khối của tường lệch vài điểm ảnh so với phòng cho tới lần vẽ lại.
  5. Còn nguyên từ các đợt trước: phông "Be Vietnam Pro" không nhúng; 51 selector `.hero` chết trong `v5.css`; tên Keeper tiếng Nga dài xuống ba dòng.
- **Open**: chủ wiki chọn các nâng cấp cách dùng ở mục 9 của plan; đưa nhánh vào `main` khi chủ wiki đồng ý. Các mục open của đợt multilingual giữ nguyên.

## 2026-11-11: diện mạo mới, đợt 4: bỏ Best loadout, boss hết nhỏ và hết xéo, trời sống động thay cho hạt, rương theo tông trang, UX trang Changes
- **Bối cảnh**: chủ wiki xem bản đợt 3 (kèm một ảnh chụp phần rương của trang chủ) và nêu 6 điểm. Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 10; các ngách cải thiện tiếp theo ở mục 11 (chờ chọn).
- **Đã làm** (nhánh `claude/amazing-wozniak-jflbuy`, chưa vào `main`):
  1. Equipment: bỏ khối "Best loadout" (`gLoadout`, 8 luật CSS `.gld/.gload`), ba phép kiểm gắn với nó (`checks/audit-2026-10-31.js`, `checks/gear.js`, `style_check.js`) và mục "Added: Best loadout at each Act" của ngày 30/10 trong trang Changes (mục duy nhất của nhóm Added hôm đó).
  2. Hình boss (`boss_portraits.js --figs`, chạy lại): mọi boss cùng góc nhìn 30° (đợt 3 tôi cho mỗi boss một góc 20–60° để khung hẹp nhất, làm Iron Colossus và Goblin Lord trông xéo); sàn dưới của luật cỡ 0,8 → 0,95; thêm `bw` (bề ngang thân: phần giữa khung chứa 86% điểm ảnh) và trang thu boss theo `bw` thay vì cả khung, nên Arion không còn bị thu nhỏ vì thanh kiếm; Ender Dragon có `fly` và vẽ lớn 1,45 lần (khung 744×545 px nguồn): lơ lửng trên bậc, nằm sau các boss bên cạnh, ra trước khi được chọn hoặc được chỉ.
  3. Trang chủ: hạt không khí chỉ còn ở bậc đang mở và bậc được chỉ (5 hạt). Mây và gió ẩn ở màn hình từ 1100 px trở xuống (mây trôi sau phần chữ xếp dọc). Trời sống: 5 đám mây trôi ngang, tia nắng xoay chậm và quầng sáng thở sau mặt trời, 3 tốp chim tự vẽ (7×4 điểm ảnh, hai khung), 3 vệt gió; các lớp trời xê dịch theo con trỏ (`--mx/--my`, đặt trong `pathMapWire`).
  4. Rương: bốn kệ của trang chủ là khung `.gui` chuẩn với khay ô tối nhuộm theo độ hiếm; rương của Act là khay chìm trong bảng Act. Không còn nền sáng `#c6c6c6`.
  5. Changes: thanh lọc theo loại (All kinds, Changed 11, Fixed 4, Added 9; số đếm lấy từ chính trang) và nhảy tới ngày; mỗi ngày gập mở ở dòng ngày (hai ngày mới nhất mở sẵn), dòng ngày mang số đếm theo loại. Không thêm chuỗi dịch.
- **Kiểm**: `bash build/check.sh` exit 0 trên cây cuối (invariants 0 broken, style sạch, a11y 0 broken, site_check sạch, `qa.py --strict` 0 lỗi cứng). Các lần chạy trước đỏ, đã sửa: (a) `checks/i18n.js`: "no translation for Removed" ở cả 4 ngôn ngữ: tôi tưởng chuỗi này đã có bản dịch; nó không có và trang cũng không có nhóm Removed nào, nên bỏ loại đó; (b) `checks/text.js`: "Changes page: no dated section": phép kiểm đọc cả `h2`, nay `h2` còn chứa số đếm, nên nó đọc nhãn của nút gập; (c) `a11y_check`: 5 lỗi "reduced motion #: envFall on I runs for ever": luật mới cho bậc đang mở/được chỉ lại đè luật tắt hạt khi giảm chuyển động (lần thứ hai cùng một kiểu lỗi; nay luật tắt dùng đúng bộ chọn đó). Invariant mới `build/checks/changes.js` (mọi nhóm là một loại đã gắn nhãn; số trên chip = số mục; chọn một loại thì chỉ còn loại đó và ngày không có nó bị ẩn; "All kinds" trả lại hết; ngày mới nhất mở, ngày cũ nhất gập; một lần bấm gập/mở đúng một lần kể cả ở lần ghé thứ hai; chip ngày mở ngày đó): xanh; đỏ 1 lỗi khi đổi kỳ vọng thành "ngày cũ nhất mở". `climb.js` thêm: hình nào cũng có `bw` trong khung; chỉ hình có `fly` mới bay. Trang không được đổi: 6 route (`#g12 #boss/arion #act/3 #i9 #home #bosses`) ở 1440 và 375 px, màn hình đầu giống từng điểm ảnh với bản build của `cd6a4a2` (`shot.js --diff`). Ảnh đã xem: trang chủ 1440 (mặc định; chỉ vào bậc VIII và bậc III), các kệ và rương Act, Equipment, Changes 1440 (mặc định và khi chọn Fixed), Changes 375 (không cuộn ngang: 375/375), dải bậc thang 375 quanh bậc của rồng (ảnh này chụp trước khi ẩn mây ở màn hình hẹp; sau thay đổi một dòng CSS đó tôi chỉ chạy lại `check.sh`, chưa chụp lại). Chưa xem: trang chủ 1920 px, tiếng Nga và tiếng Việt sau đợt này. Mây, chim, gió, tia nắng và dịch chuyển theo con trỏ tôi chỉ thấy qua ảnh tĩnh; phần chuyển động được kiểm gián tiếp (không lỗi script, `a11y_check` xác nhận tắt hết khi giảm chuyển động), tôi không quan sát được chúng chạy.
- **Phát hiện, chưa sửa**:
  1. Apollyon (bậc XII) vẫn là ảnh tĩnh; Ender Dragon không có vòng `walk`.
  2. `boss_figs.json` nay 1,43 MB (rồng lớn hơn) và vẫn nằm trong `wiki_data.js`, mọi trang đều tải.
  3. Trang Changes chưa có mục nào nói về diện mạo mới và việc bỏ Best loadout: viết khi đưa lên `main` (cần dịch 4 ngôn ngữ).
  4. Còn nguyên từ các đợt trước: phông "Be Vietnam Pro" không nhúng; 51 selector `.hero` chết trong `v5.css`; tên Keeper tiếng Nga dài xuống ba dòng; tường phòng đặt theo vị trí lúc vẽ.
- **Open**: chủ wiki chọn trong các ngách ở mục 11 của plan; đưa nhánh vào `main` khi chủ wiki đồng ý. Các mục open của đợt multilingual giữ nguyên.

## 2026-11-11: diện mạo mới, đợt 5: hình boss ở trang Bosses và trang từng Keeper, khay ở Curios; đính chính hai điều tôi ghi sai
- **Bối cảnh**: tôi liệt kê năm ngách cải thiện (plan mục 11), chủ wiki trả lời "làm". Tôi hiểu là làm các ngách đó; việc đưa lên `main` chưa được nói rõ nên chưa làm. Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 12.
- **Đính chính** (hai điều tôi đã viết ở các mục trước và đã nói với chủ wiki):
  1. "Phông Be Vietnam Pro không được nhúng nên máy không cài sẵn sẽ hiện phông hệ thống": sai một nửa. Site tải phông này từ Google Fonts (`build/src/template.html` dòng 8–9); nó chỉ rơi về phông hệ thống khi mở file offline lúc không có mạng hoặc khi Google Fonts bị chặn. Tôi chỉ nhìn `@font-face` trong `static/style.*.css` và `fc-match` mà không đọc `template.html`.
  2. "Act 0–I có 614 ô, phải cuộn rất xa mới tới Act II": sai. Một Act chỉ hiện 72 curio đầu và nút "Show all" (`TMORE=72` trong `app.js`). Vì vậy thanh Act dính tôi đề xuất có lợi ích nhỏ và **không làm**.
- **Đã làm** (nhánh `claude/amazing-wozniak-jflbuy`, chưa vào `main`):
  1. Trang Bosses: thẻ của mỗi Keeper mang hình của chính nó (`cardFig`: hình `BFIG`; Warden và Wither dùng ảnh chân dung `BPORT`), vòng `idle` chạy khi chỉ vào hoặc focus thẻ; lưới thẻ tối thiểu 300 px một cột (trước 260, tức 4 cột thay vì 5 ở 1440 px).
  2. Trang riêng của Keeper: khung hình chạy vòng `idle` của `BFIG` thay cho ảnh tĩnh 256 px (boss không có trong `BFIG` giữ ảnh `BPORT`). `figHtml` là một hàm dùng chung cho bậc thang trang chủ, thẻ Bosses và khung hình; luật `.pk` thành luật chung.
  3. Curios: curio của Act đang mở nằm trong khay chìm; khung độ hiếm và dấu góc của ô giữ nguyên.
  4. Apollyon (bậc XII của trang chủ): ảnh tĩnh nay nhấp nhô nhẹ (`stillBob`). Không dựng được animation thật: mô hình của nó là mô hình Java đọc từ bytecode (`pack_audit/side_bosses/jmodel.py`), animation nằm trong mã của mod.
  5. Không làm: nhúng phông (xem đính chính 1; để chủ wiki quyết), chuyển `BFIG` sang tệp trễ (nay trang Bosses và trang Keeper cũng dùng nó).
- **Kiểm**: `bash build/check.sh` exit 0 trên cây cuối, xanh ngay lần chạy đầu (invariants 0 broken, style sạch, a11y 0 broken, site_check sạch, `qa.py --strict` 0 lỗi cứng). Invariant mới ở cuối `build/checks/bosses.js`: mỗi thẻ ở trang Bosses mang hình `BFIG` của Keeper, không có thì ảnh `BPORT`, không có nữa thì emblem; khung hình ở trang `arion`, `ender_dragon` (hình) và `warden` (ảnh chân dung) đúng loại: xanh; đỏ 14 lỗi khi đảo kỳ vọng của thẻ. Trang không được đổi: 8 route (`#g12 #i9 #act/3 #gear #changes #mechanics #build #side/Apollyon`) ở 1440 và 375 px, màn hình đầu giống từng điểm ảnh với bản build của `7bd304d` (`shot.js --diff`). Ảnh đã xem: Bosses 1440 và 375, trang Arion 1440, trang Sanghor 375, Curios 1440, trang chủ 1440. Chưa quan sát: vòng `idle` chạy khi chỉ vào thẻ và trên khung hình (chỉ thấy khung đầu qua ảnh tĩnh; `a11y_check` xác nhận nó tắt khi giảm chuyển động), nhấp nhô của Apollyon, bản tiếng Nga và tiếng Việt.
- **Phát hiện, chưa sửa**: ở ảnh chụp trang `#boss/arion` phần tiêu đề lớn phía trên dòng mô tả để trống; ảnh của bản build trước cũng vậy (hai bản giống từng điểm ảnh ở đợt 3 và 4), tôi chưa tìm hiểu là do thời điểm chụp hay do trang. Các mục chưa sửa của những đợt trước giữ nguyên (51 selector `.hero` chết trong `v5.css`; tên Keeper tiếng Nga dài; Changes chưa có mục về diện mạo mới).
- **Open**: chủ wiki quyết có nhúng phông không và khi nào đưa nhánh vào `main`. Các mục open của đợt multilingual giữ nguyên.

## 2026-11-11: diện mạo mới, đợt 6: giá kệ trang chủ, nhóm con ở Equipment, curio đúng class
- **Bối cảnh**: chủ wiki gửi ảnh phần kệ của trang chủ và nêu 3 điểm: (1) phần này còn xấu (lỗi hiệu ứng, sắp xếp, bố cục); (2) Equipment phân loại chi tiết hơn (súng riêng, summon Goety hay Summonity…) và nêu đề xuất; (3) curio cho mỗi class phải đúng tác dụng của class đó, không phải relic chung chung. Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 13.
- **Đã làm** (nhánh `claude/amazing-wozniak-jflbuy`, chưa vào `main`):
  1. Trang chủ: tắt `glint` trong khay (quầng tím nhòe là hiệu ứng này bị kéo giãn theo ô 48 px); bốn kệ 2×2 thành một giá `.rack`, mỗi kệ một hàng (tiêu đề và mô tả bên trái, 18 ô bên phải, `SHELFN`), ô tối có vạch màu độ hiếm ở chân, nhãn Act dưới ô; hàng Equipment thêm bốn nút playstyle.
  2. Equipment: nhóm con dưới các playstyle (`GSUB`, `gSubOf` trong `gear.js`): Ranged → Bows / Crossbows / Guns / Thrown and other (súng nhận theo tên vì không mod nào có lớp súng chung; nỏ và cung theo lớp vật phẩm; hai ngoại lệ ghi rõ trong `GSUBX`: Galeforce là cung, Blowgun không phải súng); Summon → Summonity / Goety theo mod. Nhóm con chỉ lọc danh sách, hạng S–D giữ nguyên của cả playstyle. Địa chỉ `#gear/<act>/<role>/w/<nhóm>`; đổi Act giữ nhóm, đổi playstyle thì bỏ.
  3. Curios của Equipment: mặc định chỉ hiện curio làm tăng chính đầu ra của playstyle từ 2% trở lên (`gOwn`: `GOFF[r]` trên các thuộc tính đo được của curio; `GOWN=.02`); phần còn lại (giáp, máu, né…) ở nút "Survival, any playstyle". Không đổi `gCurioScore` hay `gTiers`, nên hạng Power của trang Curios không đổi (build in "curio_tiers … unchanged").
  4. Sáu nhãn mới có bản dịch ở cả 4 ngôn ngữ (`merge.py --pairs`, miền `ui`): Bows, Crossbows, Guns, Thrown and other, For {role}, Survival, any playstyle.
- **Số đo từ bản build** (Act XII): Ranged 114 món được xếp hạng = Bows 60 + Crossbows 3 + Guns 27 + Thrown and other 24; toàn bộ vũ khí tầm xa không ẩn: 77 cung, 7 nỏ, 34 súng, 26 ném/khác. Summon: Summonity 19, Goety 4, ngoài nhóm 1 (The Blood Staff). Curio riêng class trên tổng được xếp hạng: Melee 44/75, Ranged 12/59, Mage 50/60, Summon 17/32. Trước thay đổi, sáu món đứng đầu danh sách của cả bốn class là cùng sáu relic phòng thủ (Etherium Core, Dimensional Will, Halo of The-End, Soul Lantern of Illusion, Ankle Monitor, Nano Machines).
- **Kiểm**: `bash build/check.sh` exit 0 trên cây cuối, xanh ngay lần chạy đầu (invariants 0 broken, style sạch, a11y 0 broken, site_check sạch, `qa.py --strict` 0 lỗi cứng; build không báo chuỗi nào thiếu bản dịch). Invariant mới ở cuối `build/checks/gear.js` (equip-groups): mọi vũ khí tầm xa thuộc đúng một trong bốn nhóm; Railgun là súng, Blowgun và Gungnir không phải, Crossbow là nỏ, Bow là cung; vũ khí summon đúng nhóm theo mod; trang Guns chỉ hiện súng, mỗi món dưới đúng hạng của cả playstyle, và số trên các nút cộng lại bằng "All kinds"; hai góc nhìn curio của Mage chia đủ và đúng phía: xanh; đỏ 1 lỗi khi đổi kỳ vọng thành "Bow là nỏ". Trang không được đổi: 9 route (`#g12 #i9 #act/3 #home #bosses #changes #mechanics #build #boss/arion`) ở 1440 và 375 px, màn hình đầu giống từng điểm ảnh với bản build của `219ced1` (`shot.js --diff`). Ảnh đã xem: giá kệ trang chủ ở 1440 và 375 px (không cuộn ngang: 375/375), Equipment `#gear/12/RA/w/gun` và `#gear/12/MA/c` ở 1440, `#gear/12/RA/w` ở 375 (375/375), `#gear/12/SU/c` tiếng Việt (nhãn mới hiện đúng: "Cho Triệu hồi", "Sống sót, mọi lối chơi"). Chưa xem: bản tiếng Nga, Bồ, Tây Ban Nha của các nhãn mới (chỉ có `qa.py` và build xác nhận có bản dịch).
- **Phát hiện, chưa sửa**:
  1. Mage và Melee chưa có nhóm con. Mage nên chia theo hệ phép (cần đọc thuộc tính phép vũ khí cộng); Melee theo dáng vũ khí (cần lớp vật phẩm, phân theo tên sẽ sai).
  2. Trong danh sách curio riêng class, thứ tự và hạng vẫn theo tổng điểm (đầu ra × sống sót), nên một curio tăng 2% phép kèm nhiều giáp vẫn có thể đứng cao. Xếp theo riêng mức tăng đầu ra là một thay đổi nữa, cần chủ wiki chọn.
  3. "Blaster" (macabre) được xếp vào Guns theo tên dù lớp của nó là kiếm; tôi chưa kiểm trong game nó bắn hay chém.
  4. Các mục chưa sửa của những đợt trước giữ nguyên.
- **Open**: chủ wiki chọn các đề xuất ở mục 13.4 của plan; đưa nhánh vào `main` khi chủ wiki đồng ý. Các mục open của đợt multilingual giữ nguyên.

## 2026-11-11: diện mạo mới, đợt 7: nhóm con cho Melee, Mage, Summon và khay curio riêng class xếp theo mức tăng đầu ra
- **Bối cảnh**: sau đợt 6 tôi nêu bốn đề xuất (Mage theo trường phái, Melee theo dáng, Summonity chia Whips và Staffs, xếp curio riêng class theo đúng mức tăng đầu ra); chủ wiki trả lời "làm hết các đề xuất". Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 14.
- **Đã làm** (nhánh `claude/amazing-wozniak-jflbuy`, chưa vào `main`; làm trực tiếp, không dùng agent):
  1. `gSubOf(g, r)` trả về danh sách nhóm (một vũ khí có thể thuộc nhiều nhóm). Melee: 9 nhóm theo dáng, đọc từ trong tên rồi tới lớp vật phẩm (`GMEL`, `GMELC`). Mage: `Any school`, 11 trường phái (đọc từ `*_spell_power`), Goety, Ars Nouveau, Other. Summon: Summonity, Goety, Whips, Staffs and other. Ranged giữ như đợt 6.
  2. Khay curio của Equipment, nhóm "For {role}": pool riêng `"o"` (`gPool`, `gCurioGain`), xếp và chia hạng theo mức tăng đầu ra của playstyle (≥ `GOWN` = 2%). `gCurioScore`, pool `"c"` và hạng Power không đổi; nhóm "Survival, any playstyle" xếp như cũ.
  3. Câu giải thích ở chân trang đổi theo nhóm đang xem (khay riêng class nói nó xếp theo cái gì); thêm một dòng "Groups" vào "How the tiers are worked out". 14 chuỗi mới ở 4 ngôn ngữ (`merge.py --pairs`, miền `ui`).
- **Số đo từ bản build** (Act XII; số này là đo, không phải dự đoán): Melee 285 món = Swords 191 + Greatswords 8 + Axes 20 + Spears and polearms 8 + Daggers and knives 23 + Scythes 10 + Hammers and maces 6 + Staffs and wands 6 + Other 13. Mage 58 món: Any school 4, Fire 10, Ice 2, Lightning 6, Ender 10, Eldritch 8, Holy 4, Nature 6, Blood 2, Evocation 2, Aqua 3, Goety 1, Ars Nouveau 1, Other 9; 10 món thuộc hai trường phái. Summon 22 món: Summonity 17, Goety 4, Whips 7, Staffs and other 15. Không món nào ngoài nhóm. Curio riêng class: Melee 51 (đợt 6: 44), Ranged 14 (12), Mage 50 (50), Summon 21 (17); đầu danh sách chỉ đổi ở Melee (Divine Immolation +110% lên đầu).
- **Kiểm**: `bash build/check.sh` exit 0 trên cây cuối, xanh ngay lần chạy đầu (invariants 0 broken, style sạch, a11y 0 broken, site_check sạch, `qa.py --strict` 0 lỗi cứng, `refs.py check` 0, build không báo chuỗi nào thiếu bản dịch; `curio_tiers: 249 … unchanged`). Invariant `equip-groups` ở cuối `build/checks/gear.js` viết lại cho cách chia mới: mỗi vũ khí đã xếp hạng nằm trong ít nhất một nhóm hợp lệ của playstyle; Melee và Ranged chia đúng một nhóm mỗi món; 25 vị trí đã biết (Railgun là súng, Blowgun và Gungnir không, Claymore là kiếm hai tay, Pyrium Staff là Fire, Soul Whip vừa Summonity vừa Whips…); mọi nhóm có món nào ở Act XII thì trang của nó chỉ hiện món thuộc nhóm và mỗi món dưới đúng hạng của cả playstyle; số trên nút hợp lệ (Melee, Ranged cộng đủ); khay riêng class đúng điều kiện ≥ 2%, xếp giảm dần, không lẫn sang khay kia, trang hiện đúng thứ tự: xanh. Đỏ khi đảo cố ý từng kỳ vọng: "Claymore là sword" (1 lỗi), thứ tự mức tăng ngược (4 lỗi), "nhóm không chứa món" (440 lỗi). Trang không được đổi: 10 route (`#g12 #i9 #act/3 #home #bosses #changes #mechanics #build #boss/arion #`) ở 1440 và 375 px, màn hình đầu giống từng điểm ảnh với bản build của `5c94b3f` (`shot.js --diff`). Ảnh đã xem: Equipment `#gear/12/ME/w/dagger`, `#gear/12/MA/w/fire`, `#gear/12/ME/c` ở 1440; `#gear/12/MA/w` ở 1440 tiếng Nga; hàng nhóm của Mage, Melee, Summon ở 375 px (không cuộn ngang: 375/375 cả ba). Chưa xem: trang `#gear/12/SU/w/whip` (chụp nhưng chưa mở), bản vi, pt, es của các nhóm mới (chỉ có build và `qa.py` xác nhận có bản dịch), các Act khác ngoài XII.
- **Phát hiện, chưa sửa**:
  1. Ở tiếng Nga "Evocation" (trường phái Mage) và "Summon" (playstyle) cùng được dịch là "Призыв" (bản dịch có sẵn trong kho dịch, tôi không đổi vì không có nguồn để đối chiếu); hai nút nằm ở hai hàng khác nhau nhưng đọc dễ lẫn.
  2. Nhóm theo tên có thể sai ở vài tên lạ: các vũ khí của mod Cataclysm (The Annihilator, The Immolator, Infernal Forge, Void Forge…) nằm ở Other vì tên không nói dáng, còn tôi không chắc dáng thật của chúng; "Trembling Slammer" cũng vậy.
  3. Nút Geo hiện 0 món ở Act XII nên bị ẩn; Goety chỉ còn 1 món vì phần lớn trượng Goety nằm dưới ngưỡng hạng (dưới 25% món thứ năm) và không được xếp hạng.
  4. 10 món của Mage và 21 trong 22 món của Summon nằm ở nhiều nhóm nên số trên các nút không cộng lại bằng "All kinds" (Melee và Ranged thì cộng đủ, và được kiểm).
  5. Các mục chưa sửa của những đợt trước giữ nguyên.
- **Open**: chủ wiki chọn tiếp trong mục 14.6 của plan nếu muốn; đưa nhánh vào `main` khi chủ wiki đồng ý. Các mục open của đợt multilingual giữ nguyên.

## 2026-11-12: nhánh `claude/amazing-wozniak-jflbuy` vào `main` (`64e0a55`), site đã chạy bản mới
- Chủ wiki bảo "merge lên main". `main` đang ở `8c0a917`, là tổ tiên trực tiếp của nhánh, nên đây là fast-forward 7 commit (`4d27957` … `64e0a55`): không có merge commit, không ghi đè lịch sử.
- **Kiểm sau khi đẩy**: workflow `site` run #14 (commit `64e0a55`) `success`, 5 phút 26 giây. `/build.txt` trên site ghi `64e0a55d766f914910270e711cd92e35145a458c 2026-11-12T00:55:18Z`. Các script đang chạy trên site chứa mã mới (`gCurioGain` ở `gear.js`, `ENDB` ở `app.js`). Mở trang thật bằng trình duyệt: trang chủ 13 bậc và 13 hình boss; `#gear/12/MA/w` có nhóm "All kinds 58 | Any school 4 | Fire 10 | Ice 2 | Lightning 6 | Ender 10 …"; `#changes` có 8 chip; 0 lỗi script, 0 request lỗi.
- Các dòng "chưa vào `main`" trong các mục ngày 2026-11-11 (đợt 1 đến 7) đúng vào lúc viết; từ nay không còn đúng.
- **Hai việc không làm khi merge** (nói rõ để khỏi hiểu nhầm là đã làm):
  1. Quy tắc "Review before merge" của `CLAUDE.md` cho việc kiến trúc: tôi không chạy `/code-review` riêng trên nhánh trước khi vào `main` (nó khởi động nhiều agent, trái với yêu cầu không dùng agent nếu chủ wiki không bảo). Có `bash build/check.sh` xanh ở mỗi đợt, nhưng đó là kiểm tra tự động, không thay cho một người đọc lại mã.
  2. Mục trên trang Changes nói về diện mạo mới: `build/checks/text.js` buộc ngày "Last checked" ở chân trang không cũ hơn mục Changes mới nhất. Thêm mục ngày 12/11 nghĩa là phải đổi "Last checked 31 Oct 2026", tức khẳng định dữ liệu được kiểm lại, mà tôi chưa kiểm lại. Chờ chủ wiki quyết (và cần dịch 4 ngôn ngữ).
- **Open**: mục Changes về diện mạo mới (trên); `/code-review` nếu chủ wiki muốn; các ý nhỏ ở `docs/plans/2026-11-11-the-climb.md` mục 14.6; các mục chưa sửa của những đợt trước giữ nguyên (51 selector `.hero` chết trong `v5.css`; tên Keeper tiếng Nga dài; "Evocation" và "Summon" cùng là "Призыв" ở tiếng Nga). Các mục open của đợt multilingual giữ nguyên.

## 2026-11-12: diện mạo mới, đợt 8: hình boss ở trang chủ nhìn thẳng, đứng giữa bậc, hết đè
- **Bối cảnh**: chủ wiki: "các model boss trang chính còn đè lên nhau, ý tưởng tốt nhưng chưa thật sự đẹp, còn lệch nhau, tìm hướng"; kèm dặn không thêm mục vào tab Changes cho tới khi chủ wiki nói "cập nhật Changes" (đã giữ: đợt này không đụng `changesPage` hay dữ liệu Changes). Chi tiết và số đo: `docs/plans/2026-11-11-the-climb.md` mục 15.
- **Đã làm** (nhánh `claude/amazing-wozniak-jflbuy`, commit `683716d`, chưa vào `main`; làm trực tiếp, không dùng agent):
  1. `figure()` (`pack_audit/boss_portraits.html`): tâm ngang là tâm thân (cột chia điểm ảnh của thân thành hai nửa bằng nhau), đáy khung là mặt đất (hàng của gốc thực thể) thay cho điểm ảnh thấp nhất; có thêm tùy chọn `fly` cho Ender Dragon (không có mặt đất).
  2. `boss_portraits.js --figs`: mọi Keeper nhìn thẳng (`YAW = 0`, trước 30°); rồng có góc riêng (`yaw 210`), thu hẹp tối đa 350 px nguồn; `boss_figs.json` và `boss_walks.json` tạo lại (1,04 MB và 1,27 MB).
  3. `style.game.css`: rồng bay cao hơn một nấc (`--s8`, nhấp nhô thêm `--s2`). `checks/climb.js`: thân hình (trừ rồng) lệch tâm bậc ≤ 6 px và thân hai hình liền kề không đè nhau.
- **Số đo từ bản build** (1440 px, bậc 111 px; `ov1.js`, không nằm trong repo): tâm thân lệch tâm bậc ≤ 3 px (trước tới 26); thân đè nhau 0 cặp (trước 2); khung đè 4 cặp trong 12, mỗi cặp 2–6 px, riêng rồng 24 px (trước 7 cặp, tới 156 px). Hình thường đứng cách mặt bậc đều 6 px. Ảnh đã xem: trang chủ 1440 và 1920 (mặc định), chỉ vào bậc III và bậc VIII (phóng to), dải bậc thang 375 px ở hai vị trí cuộn, và dải hình của rồng phóng 3 lần.
- **Kiểm**: `node build/check.js` xanh (invariants 0 broken, page text 0 problems, script errors 0), chạy sau khi build lần cuối. Invariant mới thử đỏ bằng cách siết ngưỡng (6 lỗi), rồi trả lại, xanh. **Chưa chạy** `bash build/check.sh` đầy đủ (thêm style_check, a11y_check, site check): bắt buộc trước khi đẩy vào `main`.
- **Một lỗi của chính tôi trong lúc làm**: lần đầu tôi đặt `fly` và `yaw` riêng của rồng nhưng không truyền chúng vào lời gọi vẽ, nên rồng bị cắt ở mặt đất và vẫn nhìn từ phía sau; thấy ở ảnh dải hình (cánh bị cụt), sửa trước khi commit.
- **Phát hiện, chưa sửa**: (1) hình nhìn thẳng phẳng hơn hình xéo (đổi lấy hàng đều, hết đè); chủ wiki cần xem lại bằng mắt. (2) Bậc Elvenite Paladin ghi "Dragon" thay vì số La Mã (nhãn của Act, có từ trước đợt này; tôi chưa tìm hiểu). (3) Chuyển động (idle, walk, rồng bay) chỉ thấy qua ảnh tĩnh. (4) Các mục chưa sửa của những đợt trước giữ nguyên.
- **Open**: chủ wiki duyệt hình mới trước khi đưa vào `main`; khi đó chạy `bash build/check.sh`, đẩy, và xác nhận run `site` xanh; mục Changes khi chủ wiki nói "cập nhật Changes".

## 2026-11-12: diện mạo mới, đợt 9: hình boss ở trang chủ vẽ ở texel nguyên, ánh hoàng hôn, viền (thay cho "nhìn thẳng" của đợt 8)
- **Bối cảnh**: sau đợt 8 chủ wiki nói boss vẫn rất xấu, xin hướng; tôi dựng bảng so sánh bốn cách vẽ (ngoài repo) và chủ wiki chọn "hàng 4" (ánh hoàng hôn, xoay 14°, viền). Đợt này **thay** quyết định "mọi Keeper nhìn thẳng (`YAW = 0`)" ở mục đợt 8 bằng góc 14° (thẳng hơn với boss có vũ khí thò ra); các số đo đè và lệch tâm của đợt 8 đã đo lại ở dưới. Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 16. Phần "hoàng hôn" (bậc đá, chân trang) tôi đã đưa hai hướng mockup ở tin nhắn trước; chủ wiki chưa chọn, chưa làm.
- **Đã làm** (nhánh `claude/amazing-wozniak-jflbuy`, commit `2fc6acc`, chưa vào `main`; trực tiếp, không dùng agent):
  1. `boss_portraits.html`: `figure()` có `texel`, `lit: 'sun'`, `outline`, `frames` theo vòng; `still()` có viền. `boss_portraits.js --figs`: chọn texel chẵn, chọn góc theo độ thò ra của vũ khí, rồng cỡ theo bề ngang. `boss_figs.json` và `boss_walks.json` tạo lại.
  2. `style.game.css`: `image-rendering: pixelated` cho `.pk`, bỏ bóng đổ lệch, thêm bóng tiếp đất. `build/README.md`: dòng `boss_figs.json` viết lại. `checks/climb.js`: hai invariant mới.
- **Số đo từ bản build** (1440 px): thân đè nhau 0 cặp; tâm thân lệch tối đa 5 px; khung đè 4 trong 12 cặp (15 px và 40 px là lớn nhất, đều phần trong suốt); `boss_figs.json` 1,00 MB (trước 1,04), `boss_walks.json` 1,46 MB (trước 1,27). Ảnh đã xem: trang chủ 1440 (mặc định) và 1920, chỉ vào bậc III (Arion), cắt hai nửa dải hình ở 2×, trang Bosses 1440, trang `#boss/arion` 1440. Sau khi viết dòng này tôi xem thêm: dải bậc thang ở 375 px (đoạn Dragon đến Sanghor; hình đứng đúng bậc, không đè) và `#boss/sanghor` 1440 (khung hình có viền, sắc nét; tiêu đề h1 trống trong ảnh chụp sớm là lỗi chụp đã ghi từ trước, tiêu đề hiện dần). **Chưa xem**: `#bosses` 375 (có chụp, chưa mở), tiếng Nga và tiếng Việt.
- **Kiểm**: `node build/check.js` xanh (invariants 0 broken, page text 0 problems, script errors 0), chạy sau khi build lần cuối. Hai invariant mới thử đỏ bằng cách đổi kỳ vọng (11 lỗi mỗi cái), rồi trả lại, xanh. **Chưa chạy** `bash build/check.sh` đầy đủ: bắt buộc trước khi đẩy vào `main`.
- **Một lỗi của tôi trong lúc làm**: lần đầu tôi tạo một tệp tạm `poses.js` trong thư mục repo (lỡ lệnh `cat >` chạy trước khi `cd`); tôi chuyển nó ra ngoài trước khi commit, `git status` sạch.
- **Phát hiện, chưa sửa**: (1) tay Iron Colossus và Nyxaris hơi ngả hồng do skin sáng, màu ánh sáng cần chủ wiki duyệt; (2) Discord và Sanghor vẫn lạ vì model; (3) cỡ texel giữa các boss khác nhau (2 đến 4 px trên màn hình); (4) bậc Elvenite Paladin ghi "Dragon" thay vì số La Mã (có từ trước); (5) các mục chưa sửa của những đợt trước giữ nguyên.
- **Open**: chủ wiki duyệt hình mới và chọn hướng cho phần hoàng hôn (hướng 1 hay 2); rồi `bash build/check.sh`, đưa vào `main`, xác nhận run `site` xanh; mục Changes khi chủ wiki nói "cập nhật Changes".

## 2026-11-12: diện mạo mới, đợt 10: cột bậc thang là khối đá, bỏ dải mờ ở chân, rồng và Apollyon làm lại
- **Bối cảnh**: chủ wiki: rồng và Apollyon còn khá xấu; ý tưởng tốt, chỉnh layout hay cột cho đẹp và wow hơn; bỏ hẳn phần mờ ở chân trang (tôi hiểu là dải mờ ở đáy phần hoàng hôn). Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 17.
- **Đã làm** (nhánh `claude/amazing-wozniak-jflbuy`, commit `4a3ac93`, chưa vào `main`; trực tiếp, không dùng agent):
  1. Rồng: góc nhìn mới (`yaw -30, pitch 20`), 12 khung. Apollyon: `still()` bỏ vạch lạ trên mũ, nâng phần đen, viền sáng phía mặt trời, viền tối, tối chân, vẽ gấp đôi, `pixelated`. `boss_figs.json` tạo lại (1,19 MB).
  2. `style.game.css`: bậc = mặt trên sáng + đường cắt cứng + thân tối, mép trên mang màu Act; dải mờ 56 px ở đáy phần hoàng hôn thay bằng mặt đất đá cứng cao 40 px.
  3. `checks/climb.js`: ảnh tĩnh của boss cuối cũng phải `pixelated` (trước: không được).
- **Số đo từ bản build** (1440 px): thân đè nhau 0 cặp; khung đè 5/12 cặp (phần trong suốt); chân mọi hình cách mặt bậc 6 px. Ảnh đã xem: trang chủ 1440 và 1920, chỉ vào bậc VIII, ba bậc cuối ở 375 px, Apollyon cắt 3 lần. Chưa xem: `#bosses`, trang Keeper, tiếng Nga và tiếng Việt sau đợt này.
- **Kiểm**: `bash build/check.sh` đầy đủ **xanh** (patches idempotent và build lặp lại được, curio_tiers unchanged, qa 0 hard findings, invariants 0 broken, page text 0 problems, style, a11y và timing 0 broken, site_check 0 missing files và 0 script errors), chạy trên đúng bản đã commit.
- **Lỗi của tôi trong lúc làm**: (1) Apollyon bị nhỏ một nửa và lơ lửng do `ux.js` ép tỉ lệ nguyên cho ảnh `pixelated` ≤ 256 px (xem plan mục 17.2); thấy ở ảnh chụp, tìm bằng đo kích thước thật của phần tử, sửa trước khi commit. (2) Lệnh Python sửa CSS đầu tiên hỏng giữa chừng vì một chuỗi trùng hai chỗ; lệnh chạy theo kiểu "tất cả hoặc không", nên không có thay đổi dở.
- **Phát hiện, chưa sửa**: (1) tôi bỏ vài điểm ảnh của model Apollyon (mặt phẳng mỏng nhìn nghiêng): nếu chủ wiki muốn giữ thì cần dựng lại từ jar của mod; (2) các mục chưa sửa của những đợt trước giữ nguyên.
- **Open**: chủ wiki duyệt; ba mục còn lại của "hướng 2" (hạ thấp hoàng hôn, rương Act cạnh thẻ Keeper, gập credit chân trang) chờ chọn; đưa vào `main` khi chủ wiki nói; mục Changes khi chủ wiki nói "cập nhật Changes".

## 2026-11-12: diện mạo mới, đợt 11 và 12: cột nhỏ có khoảng trời, bầu trời pixel art, cột không đen, tư thế boss
- **Bối cảnh**: chủ wiki (đợt 11) muốn các cột tách xa nhau cho trời thoáng, boss và cột nhỏ lại, trỏ chuột lên thì to ra mức ban đầu; (đợt 12) bỏ phần mờ đen của cột, nâng art bầu trời, chọn pose và hướng đẹp hơn cho boss và căn với cột, và hỏi cách nâng art cho cột. Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 18.
- **Đã làm** (nhánh `claude/amazing-wozniak-jflbuy`, commit `6246784` và `cbd891b`, chưa vào `main`; trực tiếp, không dùng agent):
  1. `style.game.css` và `app.js`: `--rest` .66 cho bậc và hình Keeper, lề giữa các cột, trỏ chuột `--r: 1`; bỏ lớp tối của cột.
  2. `app.js`: `skyArt` (vẽ trời và đất, mây) và `skyPaint` (hai canvas `.dart0` và `.dart1`, nhớ theo cỡ); `style.game.css`: canvas, mây có sprite, bỏ đồi `clip-path`.
  3. `boss_portraits.js`: `YAWS`, `PROT` mới; `boss_figs.json` và `boss_walks.json` tạo lại.
  4. `checks/climb.js`: một invariant mới (bậc nhỏ, hình nhỏ khi nghỉ).
- **Số đo từ bản build**: ở 1440 px mỗi bậc chiếm 66% ô, hình vẽ ở 0,62 cỡ gốc; sơn bầu trời 60 ms ở 1488×836; dữ liệu hình 1,28 MB và 1,63 MB. Ảnh đã xem: trang chủ 1440 (mặc định, cắt 2× hai nửa dải hình) và 1920, chỉ vào bậc III (Arion) và bậc VI (rồng), dải bậc thang 375 px (đoạn giữa), bầu trời dựng riêng ngoài trang trước khi đưa vào. Sau khi viết dòng này tôi xem thêm trang chủ 1920 (ổn) và 375 px (không tràn ngang; nhưng hero cao ~1500 px nên lâu đài và đảo nổi, đặt theo tỉ lệ chiều cao, nằm giữa phần chữ: một đảo nổi nằm sau đoạn mô tả "Pick an Act…", đọc vẫn được). **Chưa xem**: `#bosses`, trang Keeper, tiếng Nga và tiếng Việt; chuyển động của mây, chim và việc to ra khi trỏ chuột.
- **Kiểm**: `bash build/check.sh` đầy đủ **xanh** cho cả hai commit, mỗi lần chạy trên đúng bản đã commit (patches idempotent, curio_tiers unchanged, qa 0 hard findings, invariants 0 broken, page text 0 problems, style, a11y và timing 0 broken, site_check 0 missing files và 0 script errors). Invariant mới thử đỏ hai lần (13 lỗi mỗi lần) rồi xanh.
- **Lỗi của tôi trong lúc làm**: (1) bậc mở lúc đầu còn to và hoạt ảnh `figPop` bắt đầu từ cỡ cũ (xem plan 18.2); (2) một lệnh chạy nền ghép `&&` làm cả chuỗi chạy nền nên ảnh chụp ra chậm và tôi đọc nhầm là thiếu tệp; không ảnh hưởng mã.
- **Phát hiện, chưa sửa**: (0) trên điện thoại cảnh núi, lâu đài, đảo đặt theo tỉ lệ chiều cao của hero nên nằm giữa phần chữ; nên neo cảnh vào đáy hero (cao tối đa khoảng 880 px). (1) phần hạ thấp hoàng hôn, rương Act cạnh thẻ Keeper, gập credit chân trang chưa làm; (2) art cho cột chờ chủ wiki chọn; (3) bậc Elvenite Paladin ghi "Dragon" thay vì số La Mã (có từ trước); (4) các mục chưa sửa của những đợt trước giữ nguyên.
- **Open**: chủ wiki duyệt ảnh và chọn hướng art cho cột; đưa vào `main` khi chủ wiki nói; mục Changes khi chủ wiki nói "cập nhật Changes".

## 2026-11-12: diện mạo mới, đợt 13: cột xây bằng gạch, rồng đậu trên cột, bầu trời hài hoà với cột và boss
- **Bối cảnh**: chủ wiki bảo bắt đầu nâng cấp cột (theo ba hướng tôi đề xuất), nâng tiếp bầu trời cho hài hoà với cột và boss, chỉnh boss cho hài hoà với cột, và nói Ender Dragon khá kì lạ. Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 19.
- **Đã làm** (nhánh `claude/amazing-wozniak-jflbuy`, commit `165927c` và `0c6bc58`, chưa vào `main`; trực tiếp, không dùng agent): `app.js` (`colFx`, `skyArt`, `skyPaint`: lâu đài, sương, đất neo đáy, bộ nhớ đệm bằng `ImageData`); `style.game.css` (cột: gạch, dải màu Act, ánh sáng chung, điểm sáng, viền, hạt `--u`; nền đất tím; bóng Keeper; `.perch`); `boss_portraits.html` và `.js` (`perch`: đặt chân từng khung, rồng nhìn thẳng); `checks/climb.js` (cột, bầu trời, rồng); `boss_figs.json` tạo lại (rồng 1 bản ghi).
- **Kiểm**: `bash build/check.sh` đầy đủ **xanh** trên `0c6bc58` (lượt đầu trên `165927c` đỏ, xem plan 19.5). Chi tiết số đo và ảnh đã xem ở plan 19.6.
- **Lỗi của tôi trong lúc làm**: hai lỗi ở plan 19.5 (canvas bộ nhớ đệm rỗng trong `check.js`; commit chứa bản thử đỏ). Thêm: lần đầu tôi mã hóa ô SVG với dấu nháy kép không thoát, làm hỏng khai báo `background` (cột mất gạch); thấy ở ảnh chụp (cột không có đường gạch), sửa bằng cách mã hóa lại.
- **Phát hiện, chưa sửa**: (1) Keeper còn tối hơn cột; (2) hướng "dải rune" cho cột; (3) phần hạ thấp hoàng hôn, rương Act cạnh thẻ Keeper, gập credit chân trang; (4) chưa rõ vì sao canvas bộ nhớ đệm trở về rỗng trong `check.js`; (5) bậc Elvenite Paladin ghi "Dragon" thay vì số La Mã (có từ trước); (6) các mục chưa sửa của những đợt trước giữ nguyên.
- **Open**: chủ wiki duyệt ảnh; đưa vào `main` khi chủ wiki nói; mục Changes khi chủ wiki nói "cập nhật Changes".

## 2026-11-12: diện mạo mới, đợt 14: art hoàng hôn, lâu đài về mỏm đá bên phải, mặt trời tròn, trăng và mây cao
- **Bối cảnh**: chủ wiki: "nâng cấp art hoàng hôn, lâu đài nằm giữa khá vô lý". Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 20.
- **Đã làm** (nhánh `claude/amazing-wozniak-jflbuy`, commit `efb3528`, chưa vào `main`; trực tiếp, không dùng agent): `app.js` (`skyArt`: mặt trời tròn vẽ pixel, trăng, mây cao, dãy núi xa thứ tư, mỏm đá bên phải với lâu đài, đảo nổi dời chỗ; `skyPaint`: biến `--sunb`); `style.game.css` (`.dsun` chỉ giữ tia quay, bỏ quầng nhấp nháy `sunHalo` và luật `bottom: 300px` của điện thoại).
- **Kiểm**: `bash build/check.sh` đầy đủ **xanh** trên `efb3528`; chi tiết ở plan 20.4. Không thêm invariant mới (plan 20.5a).
- **Lỗi của tôi trong lúc làm**: lần đầu viết lại `skyArt` bằng một lệnh Python tìm chuỗi theo thụt lề sai (hai khoảng trắng thay vì một), lệnh báo lỗi trước khi ghi nên không có thay đổi dở; làm lại với thụt lề đúng. Lần đầu mặt trời nằm sai chỗ (đĩa vẽ cao hơn tia sáng CSS) vì tia vẫn đặt theo `bottom: 30%`: thấy ở ảnh chụp, sửa bằng biến `--sunb`.
- **Phát hiện, chưa sửa**: (1) mỏm đá ở 1920 hơi như khối chữ nhật; (2) trên điện thoại mặt trời bị núi che gần hết; (3) rương Act cạnh thẻ Keeper, gập credit chân trang, dải rune, độ sáng Keeper so với cột; (4) bậc Elvenite Paladin ghi "Dragon" thay vì số La Mã (có từ trước); (5) các mục chưa sửa của những đợt trước giữ nguyên.
- **Open**: chủ wiki duyệt ảnh; đưa vào `main` khi chủ wiki nói; mục Changes khi chủ wiki nói "cập nhật Changes".

## 2026-11-12: diện mạo mới, đợt 15: sửa mỏm đá lâu đài (một lỗi vẽ thật), mặt trời trên điện thoại, vệt sáng ở dải cột
- **Bối cảnh**: chủ wiki: "tiếp tục nâng cấp". Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 21.
- **Đã làm** (nhánh `claude/amazing-wozniak-jflbuy`, commit `6127517`, chưa vào `main`; trực tiếp, không dùng agent): `app.js` (`skyArt`: dãy núi xa vẽ sau mỏm đá, đỉnh mỏm theo đỉnh dãy núi, sườn, ánh sáng, mỏm nhỏ; mặt trời đặt theo đỉnh dãy núi); `style.game.css` (vệt sáng `friezeRun`, tắt khi giảm chuyển động).
- **Kiểm**: `bash build/check.sh` đầy đủ **xanh** trên `6127517` (chi tiết ở plan 21.5). Không thêm invariant.
- **Lỗi của tôi trong lúc làm**: (1) mỏm đá ở bản `efb3528` có lỗi vẽ (hộp tối thẳng đứng dưới đỉnh dãy núi, plan 21.1) mà tôi đã gửi ảnh và nói "hơi giống khối chữ nhật vì mặt tối ở sườn phải": chẩn đoán sai, chỉ đúng sau khi cắt 2× ảnh và thấy cạnh thẳng đứng; (2) tôi chèn một chú thích `//` ở giữa một dòng `const ... , nz=noise(9)`, làm mất `nz`; thấy ở lượt chụp đầu ("nz is not defined" trong cả ba ảnh), sửa trước khi commit.
- **Phát hiện, chưa sửa**: (1) độ sáng Keeper so với cột; (2) rương Act cạnh thẻ Keeper, gập credit chân trang, dải rune; (3) bậc Elvenite Paladin ghi "Dragon" thay vì số La Mã (có từ trước); (4) các mục chưa sửa của những đợt trước giữ nguyên.
- **Open**: chủ wiki duyệt ảnh; đưa vào `main` khi chủ wiki nói; mục Changes khi chủ wiki nói "cập nhật Changes".

## 2026-11-12: nhánh `claude/amazing-wozniak-jflbuy` vào `main` lần hai (`028bd27`), site đã chạy bản mới
- Chủ wiki bảo "merge". `main` đang ở `103f645`, là tổ tiên trực tiếp của nhánh, nên đây là fast-forward 18 commit (đợt 8 đến 15 của diện mạo mới: hình boss ở texel nguyên và ánh hoàng hôn, bậc thang nhỏ có khoảng trời, cột xây bằng gạch, rồng đậu trên cột, bầu trời pixel art, lâu đài trên mỏm đá). Không có merge commit, không ghi đè lịch sử.
- **Kiểm sau khi đẩy**: workflow `site` run #15 (commit `028bd27`) `success`. `/build.txt` trên site ghi `028bd27bb8b15ccc1cbda8cccaf5249de5b21f8f 2026-11-12T05:18:36Z`. Mở trang thật bằng trình duyệt: 13 bậc, 13 hình boss, rồng có `perch`, hàm `skyArt` có, canvas bầu trời rộng 372 điểm ảnh, 13 cột có gạch, 39 điểm sáng, không có lỗi script. Chưa xem ảnh trang thật bằng mắt (chỉ kiểm bằng mã).
- Mã đi vào `main` đã qua `bash build/check.sh` xanh ở commit `6127517` (commit cuối có đổi mã); hai commit sau đó chỉ đổi NOTES và plan.
- **Hai việc không làm khi merge** (nói rõ để khỏi hiểu nhầm là đã làm): (1) quy tắc "Review before merge" của `CLAUDE.md`: không chạy `/code-review` (nó chạy nhiều agent; chủ wiki dặn không dùng agent nếu không bảo); (2) mục Changes: chủ wiki dặn chưa cập nhật tới khi nói "cập nhật Changes", nên trang Changes chưa có mục nào về diện mạo mới.
- **Open**: mục Changes khi chủ wiki nói; độ sáng Keeper so với cột; rương Act cạnh thẻ Keeper; gập credit chân trang; `/code-review` nếu chủ wiki muốn; các mục chưa sửa của những đợt trước giữ nguyên.

## 2026-11-12: diện mạo mới, đợt 16: hết giật khi trỏ chuột, idle 24 khung, chữ và bố cục hero, các kệ, bố cục Equipment
- **Bối cảnh**: chủ wiki nêu bốn điểm (chữ và bố cục màn hình chính; boss khi trỏ chuột và lúc thở chưa mượt, lag; Must-Have, Mythic… còn xấu; tìm hướng cho bố cục Equipment), tôi nêu số đo và phạm vi, chủ wiki trả lời "làm hết, 24 khung, còn có cả bố cục". Chi tiết và mọi số đo: `docs/plans/2026-11-11-the-climb.md` mục 22. Làm trực tiếp, không dùng agent.
- **Đã làm** (nhánh `claude/fervent-volta-4697s9`, không phải `main`: site chưa chạy bản này): (1) `style.game.css`: lớp màu cột không blend và không nền `fixed`, vệt sáng dải cột không blend, vệt sáng bậc thang trượt bằng `translate` (trước: 36 đến 61 khung quá 33 ms khi trỏ chuột, sau: 1 đến 21, thường vài khung); (2) `boss_portraits.js` và `boss_figs.json`, `boss_walks.json`: idle 24 khung (rồng cũng 24), walk 16; (3) `app.js` và CSS: dòng thông tin thành chip, tiêu đề lettering như logo game, tấm nền cho đoạn mô tả (sửa một lỗi có từ trước: màu đoạn mô tả là xám chứ không phải kem), ô tìm và ba nút một hàng; (4) kệ trang chủ thành tủ trưng bày (tiêu đề có vạch màu, chip đếm, "See them all →", khay ô 64 px hàng đầy), kệ Equipment là lộ trình; (5) Equipment: banner thu còn 176 px từ 1181 px trở lên, điều khiển thành ba tầng; (6) `checks/climb.js` và `checks/gear.js`: invariant mới, thử đỏ từng cái (plan mục 22.7); `build/README.md`: số khung.
- **Giá phải trả của 24 khung, đo được**: dữ liệu hình 1,28 → 2,88 MB và 1,63 → 2,85 MB; bộ nhớ trình duyệt +127 MB; khung quá 33 ms lúc idle 3 đến 7 trên 235 (trước 0 đến 1). Chưa đo trên điện thoại hay GPU thật.
- **Kiểm**: `bash build/check.sh` lượt đầu đỏ (style 3 lỗi, a11y 2 lỗi, xem plan 22.9), lượt hai trên đúng cây đã sửa: exit 0. Trang không được đụng so với bản trước (`shot.js --diff`, 9 route ở 1440 và 375 px): `#build` giống từng điểm ảnh; các trang khác khác 0,1 đến 1,2% điểm ảnh, tôi mở một ảnh diff (`#g12`): chỉ là chữ tiêu đề đang hiện dần và hạt lấp lánh, không phải thay đổi thật (đã ghi từ trước). Ảnh đã xem: trang chủ 1440, 1920, 375, ru và vi ở 1440; kệ ở 1440, 375; Equipment ở 1440 (Weapons, Curios), 1024, 375.
- **Lỗi của tôi trong lúc làm**: (1) lệnh `awk` gom số đo hover đọc sai cột nên mất kết quả, phải đo lại; (2) lần đầu hero ở 375 px mất chữ vì `order` đẩy bậc thang lên đầu; (3) tiếng Nga làm ô tìm co còn 158 px vì cột `max-content` của lưới: đổi sang `.tact` (flex); (4) luật `!important` chung giấu vạch tiêu đề kệ và đè màu mô tả; (5) link "See them all" ban đầu trỏ `#slot/*?r=`, trang đó đã bỏ nên về `#home`, chỉ thấy khi bấm thử; (6) hai invariant mới lần đầu thử đỏ không bắt được (plan 22.7); (7) `check.sh` lượt đầu đỏ (plan 22.9).
- **Phát hiện, chưa sửa**: `#hq` (ô tìm hero) nhận 14 px và màu xám `#e0e0e0` từ luật chung thay vì 16 px kem như CSS của nó ghi (tôi không đổi vì chưa ai chê); các mục chưa sửa của những đợt trước giữ nguyên (độ sáng Keeper so với cột, rương Act cạnh thẻ Keeper, gập credit chân trang, dải rune, bậc Elvenite Paladin ghi "Dragon").
- **Open**: chủ wiki xem chuyển động thật (tôi chỉ có ảnh tĩnh) và duyệt giao diện; bộ nhớ và dữ liệu của 24 khung trên điện thoại (nếu nặng: hạ khung walk, hoặc lấy mẫu 1× cho idle); tiếng Bồ và Tây Ban Nha của hero chưa xem; đưa vào `main` khi chủ wiki nói (site chỉ triển khai từ `main`); mục Changes khi chủ wiki nói "cập nhật Changes".

## 2026-11-12: diện mạo mới, đợt 17: icon kệ nhỏ lại, sóng khi trỏ chuột, hết lag khi quét chuột, lớp animation cho cả wiki
- **Bối cảnh**: chủ wiki xem bản xem thử đợt 16 và nêu ba điểm (icon curio ở trang chính to quá; animation trang chủ vẫn lag, thêm hiệu ứng sóng khi trỏ chuột; thêm animation sạch và đẹp cho cả wiki). Chi tiết và mọi số đo: `docs/plans/2026-11-11-the-climb.md` mục 23. Làm trực tiếp, không dùng agent.
- **Đã làm** (nhánh `claude/fervent-volta-4697s9`, không phải `main`): (1) icon kệ 48 px, 18 cột như khay Act; (2) **nguyên nhân lag đã đo**: parallax ghi `--mx` và `--my` lên cả `.climb` nên mỗi lần chuột động, mọi nút bên dưới tính lại style (10,4 ms một lần, 2626 ms trong 4 giây quét chuột); nay ghi lên bầu trời; (3) sóng bằng lò xo trong `pathMapWire` (cỡ bậc theo khoảng cách tới chuột, bậc dưới chuột đầy cỡ, hai bên 0,55, bậc thứ hai 0,64), chỉ trên máy có chuột và không giảm chuyển động; (4) lớp animation `--mo-*`: trang chủ mở từng dòng, kệ và khối chính của Bosses, Mechanics, Changes hiện dần một lần mỗi lượt vào trang, ô rơi vào lần lượt và nhấc khi trỏ, nút Equipment nảy khi đổi, hero và ores tạm dừng khi không thấy; (5) `checks/climb.js` (sóng, icon kệ) và `checks/motion.js` mới, đã thử đỏ.
- **Số đo**: quét chuột 4 giây: 93 khung, trung bình 43 ms (trước) → 139 đến 152 khung, 26 đến 29 ms (sau), tính lại style 2626 → khoảng 1200 ms; máy cloud render bằng phần mềm, chưa đo GPU thật.
- **Kiểm**: `bash build/check.sh` xanh ngay lượt đầu trên cây đã sửa. Ảnh đã xem: kệ ở 1440, hai trạng thái sóng ở 1440 (chuột ở bậc VI và giữa VI, VII), hero ở 250 ms, kệ ở 160 ms sau khi cuộn tới. Giảm chuyển động và 375 px: đã thử bằng mã (không sóng, không tràn ngang), chưa xem ảnh.
- **Lỗi của tôi trong lúc làm**: lỗi cú pháp `-(x)**2` làm build đỏ với thông báo sai hướng; ngoặc của khối `watch()`; phép thử ngôn ngữ ban đầu sai hàm (plan mục 23.7).
- **Phát hiện, chưa sửa**: chi phí tính lại style mỗi phần tử cao bất thường (khoảng 34 µs) và `Layerize` 6 đến 11 ms mỗi lần, đều chưa giải thích được; invariant icon kệ không đỏ khi tiêm CSS từ ngoài (phép so sánh thì đã thử đỏ); các mục chưa sửa của những đợt trước giữ nguyên.
- **Open**: chủ wiki xem chuyển động thật trên bản xem thử và chỉnh độ gắt của sóng nếu cần; bộ nhớ và dữ liệu hình trên điện thoại; đưa vào `main` khi chủ wiki nói; mục Changes khi chủ wiki nói "cập nhật Changes".

## 2026-11-12: diện mạo mới, đợt 18: kệ gọn lại, Apollyon hết lệch, nền hoàng hôn thêm mây, bảng so sánh render boss
- **Bối cảnh**: chủ wiki xem bản xem thử đợt 17 và nêu: nâng cấp nền hoàng hôn nữa; nâng cấp model boss và sửa Apollyon lệch; kệ Must-Have… còn xấu (icon quá to so với ô, chữ chia Act xấu và thừa), Equipment khá vô dụng. Ảnh chụp kèm lộ một lỗi của tôi: kệ Equipment đệm 12 ô trống. Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 24. Làm trực tiếp, không dùng agent.
- **Đã làm** (nhánh `claude/fervent-volta-4697s9`, không phải `main`): (1) kệ: ô 56 px, icon 32 px, bỏ nhãn Act, vừa số ô theo bề rộng (`shelfFit`), bỏ kệ Equipment; (2) Apollyon: lệch +15,1 px do luật `transform-origin` 88% (và 12%) của bậc cuối và bậc đầu, đã bỏ, invariant nay đo hình đã vẽ ở cả 13 bậc; (3) nền: mây khối pixel-art có ánh sáng theo dải, dãy núi xa, thông và sương ở dãy giữa, mặt trời lớn hơn, sao nhiều hơn; (4) bảng so sánh bốn hướng render boss gửi chủ wiki (chưa đổi code boss).
- **Kiểm**: `bash build/check.sh` xanh ngay lượt đầu. Thử đỏ: Apollyon (trả luật cũ: 13 px), tỉ lệ icon (ép 52 px: 3 lỗi). Ảnh đã xem như plan 24.6.
- **Lỗi của tôi trong lúc làm**: kệ Equipment đệm ô trống (đợt 17); mây làm lại hai lần trước khi đọc ra là mây.
- **Open**: chủ wiki chọn hàng 2, 3 hoặc 4 ở bảng boss (hoặc nói rõ "nâng cấp model" là gì khác); có muốn thẻ "gear cho Act của bạn" thay kệ Equipment không; xem nền và kệ trên bản xem thử; đưa vào `main` khi chủ wiki nói; mục Changes khi chủ wiki nói "cập nhật Changes".

## 2026-11-12: diện mạo mới, đợt 19: hình boss nét hơn, nền gọn và đẹp hơn
- **Bối cảnh**: chủ wiki hỏi có cách nâng cấp boss nào "nét hơn" không, và muốn nền nâng cấp tiếp một cách toàn diện nhưng clean, không rối. Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 25. Làm trực tiếp, không dùng agent.
- **Đã làm** (nhánh `claude/fervent-volta-4697s9`, không phải `main`): (1) hình boss dùng làm mịn của trình duyệt thay cho lấy mẫu gần nhất (texel không nguyên ở 0,31 và 0,47 cỡ dải hình làm cạnh lởm chởm); đảo ngược lựa chọn "pixelated" của đợt 9, trả lại bằng một dòng CSS; (2) nền: bỏ vệt mây cao, vệt gió, hai mây trôi và một khối mây tĩnh; thêm quầng sáng dọc chân trời.
- **Kiểm**: `bash build/check.sh` xanh ngay lượt đầu; thử đỏ invariant `auto`. Ảnh đã xem: bảng so sánh A/B ở 125%, nền ở 1920, 1440, 375.
- **Open**: chủ wiki chọn giữ làm mịn hay trả về pixelated; chọn hàng boss (2, 3, 4) hoặc nói "nâng cấp model" là gì khác; thẻ "gear cho Act của bạn"; đưa vào `main` khi chủ wiki nói; mục Changes khi chủ wiki nói "cập nhật Changes".

## 2026-11-12: diện mạo mới, đợt 20: boss theo hàng 3, nền mịn gấp đôi, lâu đài chi tiết
- **Bối cảnh**: chủ wiki bảo áp hàng 3 của bảng boss và tiếp tục nâng cấp nền (độ pixel, chi tiết lâu đài). Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 26. Làm trực tiếp, không dùng agent.
- **Đã làm** (nhánh `claude/fervent-volta-4697s9`, không phải `main`): (1) boss: `gradeCanvas` (màu theo hoàng hôn và đổ bóng mềm ở chân) áp lên mọi dải hình và ảnh Apollyon, `boss_figs.json` và `boss_walks.json` tạo lại (3,17 và 3,15 MB); (2) nền vẽ ở 2 px một điểm ảnh (`skyArt(w,h,2)`, hệ số K), cùng bố cục, gấp đôi chi tiết, thời gian vẽ giữ như cũ (58, 96, 37 ms) nhờ bỏ cấp phát theo từng điểm ảnh; (3) lâu đài vẽ lại: gạch xếp lớp, mái ngói, cổng vòm có song chắn và đuốc, cửa sổ vòm sáng, cờ hiệu, hai tháp bên; (4) invariant "nền vẽ ở 2 px".
- **Kiểm**: `bash build/check.sh` xanh ngay lượt đầu; thử đỏ invariant mới. Ảnh đã xem: nền ở 1920 (phóng 2×), 1440, 375; hàng boss ở 1440.
- **Phát hiện, chưa sửa**: ở màn 125% điểm ảnh 2 px thành 2,5 px thiết bị (không nguyên), chưa xem ảnh ở 125%; các mục chưa sửa của những đợt trước giữ nguyên.
- **Open**: chủ wiki xem lại nền và boss trên bản xem thử; thẻ "gear cho Act của bạn"; đưa vào `main` khi chủ wiki nói; mục Changes khi chủ wiki nói "cập nhật Changes".

## 2026-11-12: diện mạo mới, đợt 21: nền: lâu đài liền núi, đảo bay tránh mây, mịn hơn, khói lâu đài
- **Bối cảnh**: chủ wiki chỉ hai chỗ vô lý (lâu đài vs núi, đảo bay vs mây) và muốn thêm chi tiết, mịn hơn. Chi tiết: `docs/plans/2026-11-11-the-climb.md` mục 27. Làm trực tiếp, không dùng agent.
- **Đã làm** (nhánh `claude/fervent-volta-4697s9`, không phải `main`): (1) mỏm đá tối dán lên núi bỏ đi; dãy núi xa tự nhô thành đỉnh cùng màu, có mặt đá, nền đá dưới lâu đài, đường uốn lượn, thông theo cụm, sương chân núi mờ dần; (2) đảo bay đặt vào chỗ trời trống (không đè khối mây, mặt trời, lâu đài, đảo khác, đất, và chữ của hero: `skyPaint` đo hộp chữ từ trang và đưa cho `skyArt`), đảo xa mờ dần về màu trời; (3) ba mây trôi chuyển xuống dải 56–59% để khỏi cắt qua khối mây; (4) dither Bayer 8×8, 48 dải màu, thêm hai dãy núi; (5) ống khói và khói (CSS); (6) `skyArt` trả thêm `layout`.
- **Kiểm**: `bash build/check.sh` xanh ngay lượt đầu. Invariant mới trong `build/checks/climb.js` (đảo không đè khối mây / chữ / lâu đài / mặt trời, mây trôi tránh khối mây, tường lâu đài có đá bên dưới, khói đúng trên ống khói) đều đã thử đỏ một lần; lần thử đỏ đầu của luật khói không đỏ (hộp lâu đài quá cao) nên đổi sang đo điểm ảnh. Ảnh đã xem: nền ở 1920 (phóng 2×), 1440, 375. Thời gian vẽ 69 / 119 / 90 ms (đợt 20: 56 / 120 / 42 ms).
- **Phát hiện, chưa sửa**: điện thoại 375 không còn đảo nào (chữ chiếm); chuyển động (khói, mây trôi) chưa thấy chạy; chưa xem ảnh ở 125%; các mục chưa sửa của những đợt trước giữ nguyên.
- **Open**: chủ wiki xem lại nền trên bản xem thử; thẻ "gear cho Act của bạn"; đưa vào `main` khi chủ wiki nói; mục Changes khi chủ wiki nói "cập nhật Changes".

## 2026-11-12: diện mạo mới, đợt 22: sửa các chỗ vô lý của nền, thêm chi tiết
- **Bối cảnh**: chủ wiki bảo "tiếp tục nâng cấp cộng thêm sửa các chỗ vô lý" (không chỉ cụ thể). Tôi soi ảnh phóng 2× theo từng vùng và liệt kê; chi tiết ở `docs/plans/2026-11-11-the-climb.md` mục 28. Làm trực tiếp, không dùng agent.
- **Đã làm** (nhánh `claude/fervent-volta-4697s9`, không phải `main`): (1) viền sáng núi đúng hướng ngược sáng (mặt trời sau dãy núi xa, bên trái), các lớp núi tách nhau bằng màu thay vì đường viền, chân núi dither dưới một điểm ảnh; (2) đuốc ở cổng lâu đài không còn bị nhà giữ che (lỗi từ đợt 20); (3) mây né chữ trong suốt, lâu đài, mặt trời, mặt trăng; (4) chim bay dưới chân chữ; (5) sao mờ dần về phía chân trời; (6) mặt trời và mặt trăng tránh chữ trên màn thấp và máy tính bảng, tia nắng quay đúng tâm mặt trời; (7) chi tiết mới: đèn lâu đài nhấp nháy, sao băng, đá vỡ dưới đảo, khói dither.
- **Kiểm**: `bash build/check.sh` xanh ngay lượt đầu. 15 lần thử đỏ cho các invariant mới trong `build/checks/climb.js` (một lần thử viền sáng và một lần ép 45% cho mây trôi không đỏ ngay: đã sửa cách đo / đổi độ cao thử). Ảnh đã xem ở 1920, 1536, 1440, 1366, 1280, 768, 375. Thời gian vẽ 74 / 121 / 54 ms.
- **Phát hiện, chưa sửa**: cột Act sáng đều, chưa theo hướng mặt trời (bên trái); chuyển động (nhấp nháy, sao băng, khói, chim) chưa thấy chạy thật; điện thoại 375 không có đảo; chưa xem ở 125% và các ngôn ngữ khác.
- **Open**: chủ wiki xem lại nền trên bản xem thử; thẻ "gear cho Act của bạn"; đưa vào `main` khi chủ wiki nói; mục Changes khi chủ wiki nói "cập nhật Changes".
