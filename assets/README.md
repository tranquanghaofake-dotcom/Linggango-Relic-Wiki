# Asset library (workspace only, never on `main`)

Built from `PROMPT_ASSETS.md`. An asset reaches the site only when the owner picks it from `shortlist.md`, through `build/pack_audit/scenes.py`, in a separate session.

## Tiers
| Tier | Meaning | What is stored here |
|---|---|---|
| A | open licence that covers the art (MIT, BSD, Apache, MPL, LGPL, GPL, CC0, CC BY, CC BY-NC), or vanilla under the Minecraft Usage Guidelines | files in `lib/`, licence text in `LICENSES/` |
| A-SA | ShareAlike (CC BY-SA, CC BY-NC-SA) | files byte for byte: no crop, recolour or re-encode; light and shade are drawn by CSS |
| A-perm | written permission from the author (scope noted in `permissions/`) | files, as far as the permission reaches |
| B | All Rights Reserved, NoDerivatives, own licence not yet read, no licence found, assets excluded from an open code licence | **coordinates only** (CurseForge project/file, path in the archive, sha256). Never the file: this repository is public, so every branch is publication |
| X | another game's art (Terraria GUI, Terra Curio/Confluence: Re-Logic) | nothing |

## Rules
- Being in the modpack is not a licence. No licence means all rights reserved.
- A mod's licence field (Modrinth, `mods.toml`) often covers code only: read the repo's LICENSE/README for an asset exception (Create, Saint's Dragons, Starcatcher, Opposing Force, Ribbits, Goety: Awaken keep their art All Rights Reserved).
- A retexture pack cannot license the art it retextures (Fresh mowzie's mobs textures).
- A licence can change between versions (Celestisynth: MIT at 1.3.4, All Rights Reserved since 2026-08-31). Record the version; when the author has since withdrawn, ask first.
- NonCommercial art in the site keeps the whole wiki non-commercial: no ads, no paid offline copy.
- Learn a technique from Bucket B or a shader, then draw or code it from scratch; do not trace, recolour or port it.
- Credit every A / A-SA / A-perm source in the footer's Art column the way the existing ones are written.

## Files
- `sources.csv`: one row per project of Linggango V6.6.6hf (CurseForge 1343057 / 9304214: 429 mods, 24 resource packs, 2 shaders) plus the pack's own overrides and vanilla. Licence evidence (`mods.toml`, Modrinth by file hash, licence files in the archive, repo LICENSE/README), tier, confidence, and counts of effect-related files (particle textures, `particles/*.json`, effect-like entity textures, mob_effect icons, GUI, animated `.mcmeta`). `fx_score` = 3·particle + 2·entity_fx + 2·other_fx + mob_effect + 0.5·gui + animated.
- `tools/phase_a/`: how `sources.csv` was made. `W` is a scratch dir holding `src/manifest.json` from the pack zip.
  `cfmeta.py W` (cfwidget) → `cfdl.py W` (edge.forgecdn.net, ~1.8 GB) → `scan.py W` (reads the archives, executes nothing) → `modrinth.py W` (sha1 lookup) → `classify.py W` → `sources.py W out.csv`. `repolic.py DIR owner/repo…` fetches a repo's LICENSE/README at HEAD; its findings are the `MANUAL` table in `sources.py`. Run Python with `-I`.
- Confidence: `high` = repo licence read by hand; `medium` = licence declared by the jar or Modrinth, repo not read; `low` = declared in one place only, or unreadable.
