#!/usr/bin/env bash
# Derived data, then build. curio_recipes, boss_stats and boss_order edit src/data.js in place (idempotent); gear_pipeline and wiki_data write their files from JSON.
# The one-time curio edits are in build/migrations (applied already; not run here).
set -e; H=$(cd "$(dirname "$0")" && pwd)
for p in curio_recipes boss_stats boss_order gear_pipeline wiki_data; do python3 "$H/$p.py"; done
python3 "$H/../build.py"
# curio power tiers come from the built site's measured curio scores (gear.js); when they change (exit 3), write them in and
# build again; any other non-zero exit is a crash of the tier run and fails the build (set -e does not see a status caught by ||)
[ -f "$H/curio_tiers.json" ] || echo '{}' > "$H/curio_tiers.json"
rc=0; NODE_PATH=${NODE_PATH:-$(npm root -g)} node "$H/curio_tiers.js" || rc=$?
if [ $rc -eq 3 ]; then python3 "$H/wiki_data.py"; python3 "$H/../build.py"; elif [ $rc -ne 0 ]; then echo "apply_all: curio_tiers.js failed (exit $rc)" >&2; exit $rc; fi
