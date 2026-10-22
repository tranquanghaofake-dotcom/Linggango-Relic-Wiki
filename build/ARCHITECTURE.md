# Architecture

A static wiki: `index.html` + hashed `static/*.js|css` (and one offline `dist/*.html`) built by Python from data files. No server, no framework.

## Data flow
```
the CurseForge pack (476 jars + configs)
   │  gear/*, pack_audit/*  (run by hand when the pack changes; need the jars)
   ▼
build/patches/*.json  ── the committed facts: extraction table, acts, gates, notes, icons, names
   │  patches/*.py
   ├─► src/data.js        curios: hand-maintained source; boss_stats / boss_order derive into it (migrations/ = how it got here)
   ├─► src/gear_data.js   gear_pipeline.py: table → stages → one write
   └─► src/wiki_data.js   bosses, rituals, guides, images (wiki_data.py)
src/*.js + v5.css + style.game.css + template.html ──► build.py ──► index.html + static/ + dist/
```

## Where each decision lives
| Decision | Single place |
|---|---|
| What an item's raw stats and bonuses are | `patches/gearlib.py` (`off_of`, `set_facts`), fed by the extraction and the overlays in `patches/` |
| What those facts are worth (DPS, defense, tiers) | `src/gear.js` only |
| Which Act an item belongs to | gate tags + recipes (extraction), then `gear_gate`, `gear_fix`, `boss_order.gear`; finally snapped onto `ORDER` in `gear_pipeline.py` |
| Boss order and drop Acts | `patches/boss_order.py` from `boss_graph.json` (the quest book) |
| Icons | `patches/gear_icons.json` (a source file; `null` = no icon) |
| Order of gear stages | the tuple in `gear_pipeline.py` |
| How the front end plugs together | `EXT` in `app.js` (route / tooltip hooks); `build.py` `NAMES` for file order |

## Why it is shaped like this
- **Facts and judgement are separate.** Python extracts and combines facts; the ranking is a pure function of them in the browser, so a weight can be changed (and the golden lists compared) without regenerating data.
- **Generated files are written once from sources.** An earlier design patched `gear_data.js` in place seventeen times; order mattered silently and the generated file was also the source of icons and names. Now every input is a JSON file and `gear_pipeline.py` is a list of functions.
- **Estimates are labelled.** Bow, gun and spell damage lives in mod code the wiki cannot read. Those weapons are ranked by unlock rung plus a small how-hard-to-get term, and shown faded. The constants (`GSTEP` 1.13, 10% source term, `GFIT`, `GFLOOR` .25) are judgement, not data; change them in `gear.js` and read `check.js` invariants.
- **Every bug found becomes an invariant** in `check.js` (an Act of 6.1 once put a battleaxe at Act 0; Ranged armor once ended at Act V).

## Checks
`bash build/check.sh`: the patch chain is idempotent and the committed outputs are what it produces; then, in Chromium, no script errors, the invariants above, every gear and set page renders without broken images, every Path boss card has a background. `.github/workflows/check.yml` runs it on every push.

## Not done / known debt
See "Known weak spots" in `README.md` (two in-place passes on `data.js`, the large `app.js`, dead Act/mod pages).
