# Asset library (workspace only, never on `main`)

Built from `PROMPT_ASSETS.md` (phases A–E, 2026-10-27). **Nothing here is in the site.** An asset reaches the site only when the owner picks it
(start from `shortlist.md`), through `build/pack_audit/scenes.py`, in a separate session; a change to the overall look needs the owner first.

Open `gallery.html` from disk to browse: shortlist, generator sheet, and 235 contact sheets (filter by name or tier).

## What is in it
72,720 files in `lib/` (about 280 MB), one row each in `catalog.csv`; 4,288 exact duplicates are marked `duplicate_of`.

| Source group | Files |
|---|---|
| Modrinth, outside the pack | 36,957 |
| Linggango pack (tier A mods and packs) | 21,550 |
| OpenGameArt CC0 effects | 7,580 |
| Vanilla Java 26.3 | 4,079 |
| Bedrock (Mojang/bedrock-samples) | 1,953 |
| Faithful 32x 1.20.1 (effect subset) | 320 |
| Kenney CC0 | 173 |
| Own generator (fxgen.py) | 108 |

Sources and their licence evidence: `sources.csv` (the 455 files of Linggango V6.6.6hf + overrides + vanilla), `sources_modrinth.csv`
(310 Modrinth projects looked at: 107 kept, the rest dropped with the reason), `TOOLS.md` (pixel tools), `LEADS.md` (good sources that need a manual download).

## Tiers
| Tier | Meaning | Stored here |
|---|---|---|
| A | licence covers the art: MIT, BSD, Apache, MPL, LGPL, GPL, CC0, CC BY, CC BY-NC; vanilla under the Minecraft Usage Guidelines; Faithful Licence; own work | yes |
| A-SA | ShareAlike (CC BY-SA, CC BY-NC-SA): AE2, Quark, Deeper and Darker, MEGA Cells, Applied Mekanistics, Aerial Hell, BetterNether, Immersive Weapons, several Modrinth packs | yes, **byte for byte**: no crop, recolour or re-encode; light and shade drawn by CSS |
| A-perm | written permission: Misanthropy's Linggango Textures and FTB Quests theme | yes, within the permission |
| B | All Rights Reserved, NoDerivatives, own licence not read, no licence, art excluded from an open code licence | **coordinates only** (`sources*.csv`): this repository is public, so every branch is publication |
| X | another company's IP (Terraria: Terra GUI, Terra Curio; Project Moon: E.G.O. Weapons; Pokémon and similar names filtered out) | nothing |

`confidence`: `high` = the repo's LICENSE/README was read (by hand or by `repocheck.py`, which flags sentences that put art under other terms);
`medium` = declared by the jar or Modrinth only; `low` = one place only, or doubtful (Brutality, Lethality: Terramity add-ons; Macabre: AFL).

## Rules
- Being in the modpack is not a licence; no licence means all rights reserved.
- A code licence may leave the art out: Create, Saint's Dragons, Starcatcher, Opposing Force, Ribbits, Goety: Awaken, Mythic Metals, LR Tactical keep their art ARR.
- A retexture cannot license the art it retextures (Fresh mowzie's mobs textures → B). Resource packs from Modrinth: only their `minecraft`/`realms` textures were kept.
- A licence can change: Celestisynth was MIT at 1.3.4 (the pack's version) and ARR since 2026-08-31 → B until the author answers.
- Mods: only their own namespaces (+ `minecraft` overrides) were copied; other mods' namespaces inside a jar were skipped.
- NonCommercial or Faithful art in the site keeps the wiki non-commercial: no ads, no paid copy, no donations tied to it.
- Faithful Licence v4 asks to "only use what you need": only its effect subset (particle, mob_effect, gui, misc, environment) is here; it is 32 px, so it breaks the 16 px grid next to item icons.
- Vanilla 26.3 files not in 1.20.1 carry a note: newer than Linggango's game, decoration only.
- Learn from tier B and from shaders, then draw or code from scratch (`tools/fxgen.py`); never trace, recolour or port them.
- Credit every source used in the site in the footer's Art column, the way the existing ones are written.

## Files
- `catalog.csv`: id, tier, confidence, kind (particle, particle_def, entity_fx, other_fx, effect_sheet, mob_effect, gui, misc, environment, block, item, entity, armor, other), source, version, paths, author, licence, derivative_ok, sharealike, noncommercial, size, frames, frametime, colours, semi-transparent share, sha256, automatic scores (grid, animation, licence), use_on_wiki, status (new / shortlist), duplicate_of, note.
- `shortlist.md`, `shortlist.png`: 32 effect families (243 files), each with the place it would go.
- `sheets/`: contact sheets per source (+ cell → id json). `lib/lgw-fxgen/contact_sheet.png`: the generator's 12 themes.
- `catalog_b.csv`: tier B **coordinates** (43,471 files from 145 sources: where to download, path inside the archive, sha256, size, frames; no pixels). `tools/phase_b/extract_b.py <work> <assets> <local folder>` rebuilds the files on your own machine for private reference; it refuses a folder inside the repository. Nothing from tier B may go into the site or any branch until the author allows it.
- `permissions/`: 10 draft letters for the richest tier B sources (Misanthropy's other mods, Armageddon, Terramity, Iron's Spellbooks, Subtle Effects, Cataclysm, Legendary Monsters, Born in Chaos, Saint's Dragons, Celestisynth). Not sent.
- `tools/`: `fxgen.py` (effect generator), `pixelfix.py` (grid and palette forcing for AI or upscaled art), `palettes.py`;
  `phase_a/` (licence inventory → `sources.csv`), `phase_b/` (`build_library.sh` rebuilds `lib/`, `catalog.csv`, sheets, shortlist, gallery from a work dir; see its header), `data/` (inputs: Modrinth selections and scans, repo checks, OpenGameArt selection, 1.20.1 path list).
