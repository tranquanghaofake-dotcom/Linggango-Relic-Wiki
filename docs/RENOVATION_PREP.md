# Tools before the renovation (audit of 2026-10-31)

What the wiki's own tools are, what was wrong with them, what was fixed, and what to do first when the big
renovation starts. The look itself is not decided here: any change to the overall look needs the owner's approval
(CLAUDE.md, Design).

## The tools, by job
| Job | Tools | State after this pass |
|---|---|---|
| Read item stats from bytecode | `gear/mjvm.py` (symbolic JVM on jawa), `gear/gear_extract.py`, `gear/wide/*`, `gear/gear_data.py` | number and stack semantics fixed (see below); one interpreter planned |
| Read effects, armor, models from bytecode | `pack_audit/gear_fx.py`, `iss_armor.py`, `side_bosses/jmodel.py` (a second stack machine on `javap` text), `renders.py` | gear_fx argument reading fixed; jmodel small fixes; javap users to move onto one class layer |
| Recipes, loot, quests | `gear/recipes.py`, `pack_audit/lootlib.py` (new) + `loot_chance.py`, `loot.py`, `drops.py`, `chests.py`; `quests/snbt.py`, `boss_graph.py`; `curio_recipes.py` + `kubejs_recipes.js` | one loot module with vanilla semantics; SNBT parser fixed; recipe overrides replace instead of stacking |
| Item and block icons | `pack_audit/mcassets.py` (new), `block_render.py` (rewritten), `name_icons.py`, `gear/icons.py`; one-offs `icon2.py`, `icon3.py`, `mkicons.py`, `gui_icons.py` | one asset reader; block models drawn as the GUI draws them; one-offs superseded by `mcassets.icon` |
| 3D portraits and model icons | `geo2three.js`, `fx3d.src.js`, `geo_icon_render.*`, `armor_render.*`, `side_bosses/jrender.*`, `weapon_icons/*`, `render_page.js` (new) | Molang no longer runs as JS; Tongbi faces the camera; pages open in place; light and pixel issues open |
| Pixel art made here | `rarity_frames.py`, `slot_badges.py`, `mob_faces.py`, `uiicons.py`, `scenes.py`, `gui_panels.py`; on `workspace`: `assets/tools/fxgen.py`, `pixelfix.py`, `palettes.py` | two mob faces fixed; `pixelfix.py` colour bug open |
| Site checks | `check.sh`, `check.js`, `style_check.js`, `site_check.js`, `shot.js` | `shot.js --diff` added; new data invariant (effect numbers) |

## Fixed in this pass, and how each was checked
- **Block icons were drawn from the wrong side, at the wrong angle and light.** The old `block_render.py` used a true
  isometric view (√3:1 top), the south and east faces, 100/80/60 % shade, and stretched every model to fill the slot.
  The game (client-1.20.1.jar, read with javap: `GlStateManager.setupGui3DDiffuseLighting` = `rotationYXZ(1.0821041,
  3.2375858, 0).rotateYXZ(-π/8, 3π/4, 0)`, `Lighting` lights (0.2, 1, −0.7) and (−0.2, 1, 0.7), `PoseStack.mulPoseMatrix`
  leaving the normal matrix alone, `light.glsl` 0.4 + 0.6·diffuse) shows the top, the **east face on the left (65 %)
  and the north face on the right (40 %)**, a 2:1 top, and keeps small models small. A furnace's front is on the north
  face, so the old renderer never showed it. Rewritten as a z-buffered rasterizer with the model's own `display.gui`
  (stairs and walls use [30, 135, 0]), BlockElement uv defaults, face and element rotation (rescale 1/cos 22.5° or 45°:
  deepslate always uses √2, which is wrong for 22.5°), cutout at alpha 0.1, translucent faces blended. Checked on 22
  vanilla blocks side by side with the old output; hopper and cauldron, empty before, now draw.
- **Animated textures**: every icon tool cut frame 0 (`crop(0, 0, w, w)`) and cropped any tall texture even without an
  `.mcmeta`. `mcassets.first_frame` follows the `.mcmeta` (frame size, the first entry of `frames`).
- **Tint**: tinted layers (spawn eggs, grass, leaves) came out grey. `mcassets.icon(..., tint={index: 0xRRGGBB})`
  multiplies them in as the item shader does; the colours themselves still have to be read (spawn eggs: the two ints of
  `SpawnEggItem`/`ForgeSpawnEggItem`'s constructor, which mjvm can read).
- **Five icon scripts each had their own jar index and model walk** (`name_icons.py`, `gear/icons.py`, `icon2.py`,
  `icon3.py`, `mkicons.py`, plus `gui_icons.py` for `forge:separate_transforms`). `name_icons.py` and `gear/icons.py` now
  use `mcassets`; tested end to end on a copy of the repo with the vanilla jar as the pack (44 new icons, blocks in 3D).
- **Payload**: the embedded icons were plain RGBA PNGs. Re-encoded losslessly (indexed with an alpha table when ≤ 256
  colours): offline file 18.70 → 16.51 MB, `gear_data.js` 6.46 → 5.10 MB, `data.js` 4.50 → 3.66 MB. Every one of the
  5,806 icons decodes to the same pixels; screenshots of eight routes match the previous build (`shot.js --diff`).
  AE2 icons (CC BY-NC-SA) were left byte for byte, as the repo's licence rule asks.
- **Render pages** were opened as `r.html` / `armor.html` copies next to a hand-installed three.js, with Chromium at
  `/opt/pw-browsers/chromium`. `render_page.js` opens them in place; tested with synthetic GeckoLib, element and
  ModelPart models.
- **Molang ran as JavaScript** (security): `geo2three.js` turned Molang into JS source behind a character whitelist and
  ran it with `new Function`, in the site bundle (`fx3d.js`). Letters alone are enough to reach `Function`
  (`math.constructor.constructor`), so animation data from a mod jar could have run code for readers; a 246-character
  test expression did. Replaced with a parser that builds closures (no eval), with GeckoLib 4's rules (statements on
  `;`, the last value, assignments, unknown names read 0, `random_integer`, `die_roll_integer`). The 75 animation
  expressions in the current boss data give the same values as before, and the 22 boss pages (3D portraits included)
  match the previous build pixel for pixel. Three easing details now follow GeckoLib 4.8.4 (`easeInQuint` is its
  `pow(4)`, the back-easing argument scales 1.70158, Catmull-Rom shapes only the segment ending at its keyframe).
- **Tongbi, the Sculptor faced away**: `side_bosses/jrender.html` turned GeckoLib models half a turn too far, so the
  site showed Tongbi's back. Fixed and re-rendered from Mowzie's Mobs 1.8.2 (the pack's version; Modrinth file, SHA-1
  checked). `side_bosses/pack.py` used to rewrite `side_imgs.json` with only the bosses it was given; it now merges.
- **Mob faces**: the bee was cut at (13, 13), half of it empty (BeeModel's body front is at (10, 10)); the enderman lacked
  its jaw rows (the "hat" box at (8, 24) sits behind the head). `uiicons.js` regenerated from client-1.20.1.jar: every
  other texture came out byte for byte the same.
- **Oversized icons** were shrunk to 64 px at any ratio (96 px became ×2/3); now by a whole factor (1/n of the source).
- **The bytecode readers** (synthetic Java classes compiled with javac and run through each tool; 9 test files, every case
  passing after the fix, most failing before; nothing re-extracted, the jars are not here):
  - `mjvm.py`: a negative `iinc` came out as +255 (jawa reads the operand unsigned), so a count-down loop ran to the step
    budget; `dup2`/`pop2` and the other long/double stack forms were wrong (`a[i] += x` lost the add); floats were not
    rounded to 32 bits (`(int)(0.7f*10)` gave 6), ints did not wrap, `irem` had Python's sign, `f2i` did not saturate;
    a `switch` on an unknown value abandoned the method; any static `(String, …, number)` method was taken for a config
    lookup; config files were matched by a 6-letter prefix anywhere in the path (`simplyswords`/`simplymore` read each
    other's files, `ad` matched almost anything) in an unsorted walk. All fixed; config files now match the whole
    namespace (`cfg_ns`, falling back to its first part), booleans are read, unparsable files are listed, and code
    that raises inside the interpreter is recorded (`vm.errors`, printed by the extract scripts) instead of vanishing.
  - `gear_fx.py`: effect arguments are read by their place in the constructor's descriptor (a value that is not a
    constant is unknown, not the next constant along), and a chance takes its direction from the `if` that follows
    (`nextFloat() > 0.8f` is a 20 % chance, not 80 %) and applies to that branch only.
  - Loot: four tools had four copies of the drop-chance arithmetic, each wrong somewhere (conditions on groups dropped,
    `alternatives` flattened, uniform rolls taken at their maximum, `inverted` ignored, two pools as a maximum instead of
    a union). `lootlib.py` follows vanilla 1.20.1 and the four use it. A drop whose count can come out 0 now has that in
    its chance ("100 %, 0–4" becomes "80 %, 1–4").
  - `recipes.py`: a pack recipe or loot table at the same id now replaces the mod's instead of sitting beside it (the
    older, cheaper recipe could pull an item into an earlier Act); tag `replace` is honoured; recipe types no longer
    count as ingredients.
  - `snbt.py`: single-quoted strings, escapes, signed exponents and long integers (grammar after nbtlib, MIT, credited).
  - `jmodel.py`: integer division, `invokedynamic` string concatenation, arguments by descriptor position, `Math`
    functions. `drops.py`, `recheck.py`, `tips.py`: no absolute `/home/user/...` path; `data.js` found by a regex.
- **Effect numbers on gear pages** (data bug, now an invariant in `check.js`): `gear_fx.py` took durations and levels
  from whatever constants preceded the call, so the site said Frostmourne gives Strength XXI for 3 ticks. Until
  `gear_fx.py` is re-run with its fix, `gear_pipeline.fx_doubt` drops a level over 10 or a duration under half a second
  unless the item's tooltip states it (Royal Guardian Sword's "Pulverized XXV for 3 ticks" stays, and the game's own
  measurement agrees); 18 lines are shown as "number not read reliably" and not scored.

## Still open, in the order to do them
1. **Re-run the readers on the pack** with the fixes: `gear_fx.py` (effects; then `fx_doubt` should find nothing to
   drop), the loot tools (side-boss drop chances in `side_drops.json`), `gear/recipes.py` (Acts can move where a pack
   recipe replaced a mod's), the wide gear scan (mjvm's number and config fixes). Needs the pack downloaded
   (`gear/dl.py`, a few GB); compare the JSON before and after, item by item, before committing. Smaller items found on
   the way: `import_curios.py` guesses an attribute's default where `lgw_measure.js` could report it
   (`getDefaultValue()`); Ferrous Wroughtnaut's damage may count Mowzie's multiplier twice (check in game);
   `recheck.py`, `summons.py` and `goety.py` read KubeJS removals with a regex while `kubejs_recipes.js` already runs the
   scripts; `gear_fx.py` does not read `nextInt` chances yet.
2. **One class layer and one interpreter**: `classlib.py` on jawa (sorted class index, typed constants, descriptor
   slots) under mjvm, with jmodel, gear_fx and iss_armor as intrinsics tables instead of their own `javap` parsers;
   control flow by merging frames at branch targets (the design of ASM's Analyzer, BSD-3: learn the algorithm, do not
   port it). jmodel still runs a method straight through, so a loop body runs once.
3. **Missing producers**: `attrs.py`, `reg.py`, `cfg.py` (inputs of `side_bosses/stats.py`), `fallback.py` (`merge.py`)
   and `tools2/map.json` are on neither branch, so `side_stats.json` cannot be rebuilt. Recover or rewrite them.
4. **One icon run through `mcassets`**: then retire `icon2.py`, `icon3.py`, `mkicons.py` and `gui_icons.py` (each walks
   models its own way and takes the top-left square as the first frame) once its output matches or beats theirs.
5. **Light and pixels in the three.js tools** (`jrender`, `armor_render`, `geo_icon_render`, and the site's `fx3d`):
   three.js Lambert light in linear space gives 0.80–1.09 × the texel colour where the game gives 0.40–1.00 (never
   brighter); `antialias: true`; portraits shrunk with LANCZOS and saved as lossy WebP (`pack.py`, `imgs.py`: two
   colours became thousands). Use the game's `minecraft_mix_light` (the vectors are in `block_render.LIGHTS`; portraits
   use `setupForEntityInInventory`'s), no antialiasing, a whole scale, PNG. The site's portraits change with it, so this
   needs the owner's go-ahead. Better still, draw the 20 portraits at build time with the numpy rasterizer and drop
   `fx3d.js` (496 KB) and the boss models in `data.js` (~410 KB) from the page: `snapshot()` is the site's only use of it.
6. **Model icons**: 181 icons are 128 px renders fitted to the canvas and shown at 32 or 16 px by dropping pixels (spear
   and staff shafts break into dots). `geo_icon_render.html`'s element path also ignores rescale, the default face uv,
   `translation`/`scale`, and invents a [30, 225, 0] view when the model has none (vanilla uses none). Route `kind: 'el'`
   to `block_render.render_model` at 32 px and give GeckoLib items their item JSON's `display.gui`.
7. **Armor stand** (`armor_render.html`): the GeckoLib armour bones are not posed with the mannequin, the helmet overlay
   (hat layer) is missing, and the leg inflate is 1.0/0.5 where `HumanoidArmorModel` uses 0.9/0.4.
8. **Tint colours**: `mcassets` can tint, but the colours are not read yet (spawn eggs, potions, leather; the Allay egg in
   a smithing recipe is grey).
9. **`pixelfix.py` on `workspace`** keys colours by `r>>3<<3` and writes the truncated colour ((255, 241, 103) became
   (248, 240, 96)). Output the most common exact colour of each bucket. (Not changed here: `workspace` is an archive.)
10. **Payload, next step**: 0.39 MB of `gear_data.js` is the same icon stored under several ids, and `wiki_data.js` carries
   5.3 MB of WebP renders inline. An icon table referenced by index, and pictures loaded when their page opens, would
   halve the first visit. This changes data formats read by `gear.js`/`app.js`, so it belongs to the renovation itself.
11. **Before any visual change**: shoot the current build (`node build/shot.js <routes> --out <dir>`, at 1440 and 375),
   keep the folder, and compare every pass with `--diff`.

## Open-source code looked at (reference only; nothing copied)
| Project | Licence (checked) | What is worth learning |
|---|---|---|
| misode/deepslate 0.27.2 | MIT | block/item model meshes, display transforms, item tints (ItemTint.ts); not to copy: its rescale is √2 at every angle, it merges `display` field by field (vanilla takes the whole transform), its light is a world-style guess |
| GeckoLib 4.8.4 (branch 1.20.1) | MIT | the spec for geo2three.js: BakedModelFactory, EasingType, MolangParser |
| JannisX11/MolangJS 1.7.1 | MIT | a tree-evaluating Molang parser with no eval; geo2three.js now has its own small one (no new dependency in the bundle) |
| bridge-core/molang 2.0.1 (npm `molang`) | MIT | the same, faster; used by bridge.'s model viewer (MIT) |
| vberlier/nbtlib 2.0.4 | MIT | SNBT number and quoted-string grammar (it rejects FTB's comma-less files, so not a drop-in) |
| TkTech/jawa 2.2.0 | MIT | already used by mjvm; its `iinc` operand is unsigned, which caused mjvm's sign bug |
| ASM (OW2) | BSD-3 | `Analyzer`/`Frame` design for following branches |
| mapbox/pixelmatch 8.0.0 | ISC | the threshold idea behind `shot.js --diff` (the diff runs in the page, no dependency) |
| oxipng (pyoxipng 9.1.1) | MIT | measured: 39–66 % on the icons; Pillow's indexed PNG reaches most of it with no new dependency, so it was not added |

Licence note: reading code to learn how a format works is free; copying code brings the licence along (MIT and ISC
need the notice kept; GPL code such as Blockbench's would bind the wiki's code to the GPL). Re-encoding a PNG without
changing a pixel is a format change, which CC 4.0 §2(a)(4) allows without making adapted material; the repo still keeps
ShareAlike files byte for byte, which is the stricter choice.
