# Applied one-time edits to src/data.js

`src/data.js` (curios) is hand-maintained source: `transform.py` produced its first version from `original/`, but the file has since gained
tables and edits that `transform.py` cannot reproduce (re-running the old chain on a fresh `transform.py` output gives a different, 1 MB smaller file).
These scripts are the edits that were applied to it, one by one, from jars, configs and wording passes. Each is idempotent, so on today's
`data.js` every one is a no-op; they are kept as the record of where the facts came from (jar class, config key) and as a starting point if the
same pass is needed again. They are no longer run by `patches/apply_all.sh`.

Order they were applied in: moreartifacts, text, fx_numbers, pack_facts, curio_gate, tag_reps, recipe_notes, drops, tc_chests.
`patches/boss_stats.py` and `patches/boss_order.py` (curio part) stay in the build: they derive values from files that change (entity balance, the quest-book boss graph).
Run any of these from `build/` as `python3 migrations/<name>.py` (they find `src/data.js` relative to their own folder's parent).
