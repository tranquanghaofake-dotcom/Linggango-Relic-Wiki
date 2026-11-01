# 2026-11-01: process changes after the audit fix pass

## Why
The audit fix pass (NOTES, 2026-10-31 "audit fix pass") found and fixed 79 defects, but it hit the account's five-hour
limit four times (6–8 hours idle), had to drop its review stage to finish, split findings across groups so invariants
piled up for the integrator, and every cherry-pick of a `data.js` edit conflicted. Three of the causes are in the repo,
the rest are habits.

## Changes in the repo
1. `.gitattributes`: `docs/NOTES.md merge=union`. NOTES is append-only; two sessions appending at once no longer conflict.
2. `build/checks/*.js`: invariants one file per topic, loaded by `check.js` after its core invariants (function bodies
   run in the page with `bad` and `acts`). A fix adds its invariant in its own file, so parallel fixes never edit
   `check.js` together. The audit's invariants moved to `build/checks/audit-2026-10-31.js`.
3. `build/patches/curio_fix.json` + `curio_fix.py`: hand corrections to curios (set fields, add, remove), applied first by
   `apply_all.sh`. `data.js` is then written only by scripts, so a conflict in it is resolved by taking either side and
   running `apply_all.sh`. Existing content stays in `data.js`; only new corrections go through the file.

## Changes in CLAUDE.md (Process)
Budget, shipping in waves, one finding per group, dry-run of workflow scripts, generated files committed with their
source, at most two parallel builds. Checked: `check.sh` green; a probe file in `build/checks/` fails `check.js`;
`curio_fix.py` sets, adds and removes, and a second run changes nothing.
