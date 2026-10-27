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
