#!/usr/bin/env bash
# Re-apply every data patch to build/src/data.js in order (each one is idempotent), then build.
set -e; H=$(cd "$(dirname "$0")" && pwd)
for p in moreartifacts text fx_numbers pack_facts tag_reps recipe_notes drops tc_chests gear_icons boss_stats wiki_data; do python3 "$H/$p.py"; done
python3 "$H/../build.py"
