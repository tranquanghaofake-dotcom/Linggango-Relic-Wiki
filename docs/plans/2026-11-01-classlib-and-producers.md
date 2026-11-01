# 2026-11-01: one class layer, one interpreter, and the missing producers

Spec and plan in one file (CLAUDE.md, Process). Covers `docs/RENOVATION_PREP.md` "Still open" items 2 and 3. Nothing here
changes the site's look; every chunk is proved by a byte diff of the JSON a tool writes. Planned by Fable (max) on
2026-11-01 from the code as it stood at main 5319fde98.

## Why
Four tools read mod bytecode, each its own way: `gear/mjvm.py` (jawa, a symbolic JVM), `side_bosses/jmodel.py` (a stack
machine over `javap` text), `pack_audit/gear_fx.py` (another, over `javap` text) and `pack_audit/iss_armor.py` (regexes over
`javap` text). `side_bosses/reg.py`, `side_bosses/renders.py`, `pack_audit/tints.py` and `gear/wide/clsgraph.py` shell out to
`javap` or parse the class format by hand for lighter jobs. Every bytecode bug of the audit (signed `iinc`, long/double
slots, argument order) had to be fixed in each copy, and the two text machines run a method straight through: a loop body
runs once, and a value that differs where two paths join is taken from one path.

`side_bosses/stats.py` reads `attrs.json`, `cfg.json`, `cfg2.json` and `supers.json` that no script writes, so
`patches/side_stats.json` (hand-edited on 2026-10-31 to what the fixed script would write) cannot be regenerated;
`gear/wide/merge.py` reads a `fallback.json` with no producer; `side_bosses/assemble.py`, `loot.py` and `geofind.py` read
`W/tools2/map.json`, which has no producer either.

## What exists today
| File | How it reads classes | Own parsing | Writes |
|---|---|---|---|
| `gear/mjvm.py` | jawa `ClassFile`; `VM.idx` from `zipfile.namelist()` in jar order | `argc`/`dtypes`/`rettype`, `cst()`, `srg_tables()` | via `gear/wide/gear_extract_wide.py` → `G/ext_raw/<ns>.json` (106 files, 321 s) |
| `side_bosses/jmodel.py` | `javap -c -p -constants` + `javap -v` | own stack machine, every number a float | `renders.py` → `W/jm_in.json`; imported by `weapon_icons/plan.py` |
| `pack_audit/gear_fx.py` | `javap -c -p -constants` | `scan()`, `desc_of()`, `regnames()`; invokedynamic unknown | `patches/gear_fx.json` |
| `pack_audit/iss_armor.py` | `javap -c -p` on one unzipped class | regexes over `static {}` | `iss_mats.json` → by hand into `patches/gear_stats.json` |
| `side_bosses/reg.py` | `javap -c -p -v` in batches | method bodies, BootstrapMethods | `W/reg.json`, `W/ent_class.json` |
| `side_bosses/renders.py` | `javap`; hand-written constant-pool parser in `super_of()` | text scan | `W/jm_in.json` |
| `pack_audit/tints.py` | `javap` on the obfuscated client jar + own interpreter; `mjvm.VM` for mods | yes | tint colours |
| `gear/wide/clsgraph.py` | raw `struct` constant-pool parser | yes | `G/clsgraph.json` |

Tests: the audit's synthetic `javac` test sets live only in the session scratchpad (`agentA/j1`…`j8`), not in the repo.

### Inputs the consumers need
- `W/attrs.json` = `{jar: {dotted.entity.Class: {method: [[key, value], ...]}}}`; stats takes the first method and keeps
  `hp armor tough dmg kbr`; `value` is a number or `"AttributesConfig.<Field>"` / `"BossConfig.<Field>"`. The class key
  is the one `reg.json`/`ent_class.json` or stats' `MAN` names, so every class of the entity's chain below `net.minecraft`
  is recorded. The builder is a static method returning `AttributeSupplier$Builder`; `Builder.add` is SRG `m_22268_`.
- `W/cfg.json` + `cfg2.json` (merged) = `{ConfigSimpleName: {field: number}}` for Goety `AttributesConfig`, Soulslike
  `BossConfig`, BoMD `GauntletConfig LichConfig ObsidilithConfig VoidBlossomConfig`, Qliphoth `MalkuthConfig ChesedConfig`,
  Goety Revelation `ModConfig`; simple names collide across jars, so pick by jar; mod defaults only (the pack's values are
  laid over by `PACK` afterwards).
- `W/supers.json` = `{entity id: extends Monster}`.
- `summons.py` needs `W/rec.json` from `gear/recipes.py W` and `W/lang.json` from `gear/prep.py W`; its README omits that.
- `fallback.json` = `{id: {rec | null, src, why}}` for items mjvm left without stats; the original script is gone.
- `W/tools2/map.json` and `info.json` equal the committed `side_bosses/map.json` and `info.json`.
- Expected `stats.py` result: 78 bosses, 82 rows; `fdbosses:geburah` and `revelationfix:ice_hermit` stay without a row.

## Decisions
1. Producers first (P1), on today's `mjvm.VM`: they need only `idx`, `cf`, `supers`, `find`, `run`, `construct`, `CfgVal`,
   and give classlib a third regression baseline (`side_stats.json`). `fallback.py` waits (P2, part of the wide gear scan).
2. `classlib.py` lives in `build/gear/` next to `mjvm.py`; `gear/build.sh` and `gear_extract_wide.py` copy it too;
   `pack_audit/` imports it through `sys.path`, as `renders.py` does for `jmodel`.
3. One engine with intrinsics tables: `mjvm.VM._run` keeps its opcode semantics and becomes the only interpreter; a consumer
   supplies a hooks object. A second control-flow mode merges frames at branch targets (a worklist over basic blocks, a
   frame per block start, values kept where both sides agree, else unknown, until no entry frame changes; the design of
   ASM's `Analyzer`, BSD-3: learn it, write our own). The gear scan keeps the old mode in 1A (byte-identical output);
   jmodel and gear_fx use the new one.
4. Numbers stay typed (jmodel's "every number is a float" goes).
5. The bytecode tests move into `build/tests/bytecode/` (sources + `run.py`), a hand tool, not a CI gate.
6. Done per consumer = its JSON byte-identical to a baseline made with the current code in the same session, or every
   difference listed and explained (and shot and looked at when it changes a picture). Baselines first, always.

## Status (2026-11-01)
P1 and 1A done (on main). 1B, 1C and P2 are deferred by the owner: they change tools, not pages, and cost hours
for little a reader would see. Take 1B/1C up again only for a concrete need (a loop-built model part, an effect inside a
loop that the wiki gets wrong); take P2 up with the wide gear scan (RENOVATION_PREP item 1).

## Chunks (one heavy agent at a time, Opus; each ends with apply_all.sh, check.sh, one commit, a NOTES entry)

### P1: `attrs.py`, `cfg.py`, `supers.json`; `stats.py` and `summons.py` re-run end to end (~250–350k tokens)
New `side_bosses/attrs.py` (also writes `supers.json`) and `cfg.py`; `stats.py` reads `cfg2.json` only if present;
`assemble.py`, `loot.py`, `geofind.py` read `map.json`/`info.json` next to themselves; `pack_audit/README.md` gives the order
(`reg.py` → `attrs.py` → `cfg.py` → `stats.py`; `prep.py` and `recipes.py` before `summons.py`). `attrs.py` runs each
builder method with a `VM` subclass that models the empty builder and records `m_22268_(attr, D)`; config reads come back
as tagged values (`"<SimpleName>.<field>"`). `cfg.py` reads the nine classes through `vm.clinit`/`vm.statics`/`vm.construct`
without `load_cfg` (defaults, not the pack). Proof: `side_stats.json` and `summons.json` byte-identical (or each difference
explained), `wiki_data.js` unchanged, `check.sh` green. Risk: a class with two builder methods (stats takes the first);
lambda builders fall back to `MAN`.

### 1A: `classlib.py`; mjvm on it; `iss_armor.py` as the first consumer; tests in the repo (~350–450k)
`ClassPath(jars)` (sorted, first wins), cached `cf`, `supers`, `interfaces`, `find_method`, `Desc` (args, slots, ret),
typed `const`, cached `code`, `bootstrap`, constant-pool scans (`strings`, `class_refs`, `field_refs`, `method_refs`),
`services`, `mods_toml`. mjvm drops its own index and descriptor code. `iss_armor.py` walks `<clinit>` instructions from the
jar and gains `--gear-stats`. Proof: `diff -r` of `ext_raw/` before and after (skip `info.secs`), `iss_mats.json` identical,
`run.py` green, P1 still reproduces `side_stats.json`.

### 1B: the shared interpreter with frame merging; `gear_fx.py` on it (~300–400k)
`Interp(classpath, hooks).run(cls, method, args, mode='straight'|'merge')`; chance scopes become a frame fact (probability of
being here, multiplied at a branch on a random draw, added at a join). gear_fx hooks for `MobEffectInstance`, fire, heal,
random draws, registry unwraps; own helpers run inline. Proof: run the current script first and confirm it reproduces the
committed `gear_fx.json`; then the new one; every difference explained against the bytecode; two changed items shot with
`--diff`; `check.sh` green; the 1A `ext_raw` diff re-run.

### 1C: `jmodel.py` on the shared interpreter; `reg.py` and `renders.py` on classlib (~400–500k, the ceiling)
jmodel's tables (CubeListBuilder, PartPose, keyframes, Mth, parent constructors) become one hooks class; build and pose
modes use merging, so loops build every part. Proof: baseline `jm_in.json` with the current code first, then compare each
boss's `model`; loop-built parts are looked at (`pack.py` + `shot.js --diff`); `reg.json`/`ent_class.json` identical;
`weapon_icons/plan.py` still runs. If the budget runs short, land jmodel alone. Review (`requesting-code-review`) after 1C.

### P2 (later, with the wide gear scan): `fallback.py`
For each failed id of `extract_report.json`: find the class by its registry name, construct it with opaque properties, run
tier enums' `<clinit>`, read config values through `CfgVal`. Done = `merge.py` holds every id of `gear_table.json` with the
same values where the table's source is not the pack. ~300k tokens.

## Could not determine
- The original `attrs.py`/`cfg.py`/`fallback.py`/`supers.py` are in neither git history nor `workspace`; shapes are read back
  from the consumers (the method-name key of `attrs.json` is a guess from `next(iter(...))`).
- `W/sb_list.json` (read by `assemble.py`) has no producer; `assemble.py` looks superseded by hand edits plus `pack.py`.
- Whether `summons.json` depends on `pack_lang.json` names (the P1 diff decides).
- End-to-end times of `renders.py` and `gear_fx.py` (budget 10–20 min each).
- `tints.py` and `clsgraph.py` are later candidates for classlib; `gear_pipeline.fx_doubt` and the effect-number invariant
  may be relaxable after 1B.
