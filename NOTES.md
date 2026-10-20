# Linggango Relic Wiki: overhaul notes (17 Oct 2026)

Output: `dist/Linggango_Relic_Wiki.html` (single file, works offline, 3.67 MB; the original was 3.27 MB).
The task prompt is in `PROMPT.md`; every path or rarity change is listed in `build/changes.csv`.

## Rebuild

```bash
python3 build/transform.py   # data: paths, rarity, plain-English text, vanilla textures → build/out/data.js
python3 build/build.py       # assemble dist/Linggango_Relic_Wiki.html
```

`original/` keeps the uploaded file untouched; `transform.py` always reads from it.

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
