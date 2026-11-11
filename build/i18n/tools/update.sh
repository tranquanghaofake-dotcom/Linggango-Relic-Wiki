#!/usr/bin/env bash
# The whole translation update loop in one command (docs/I18N.md, "Updating"): run it after a pack, mod or code change, read what it says is missing, fill it, run it again until it is quiet.
#   bash build/i18n/tools/update.sh [--identity DIR]      DIR = a copy of the previous build's folder: also proves the English pages did not change (identity.sh)
set -e; cd "$(git rev-parse --show-toplevel)"; export NODE_PATH="${NODE_PATH:-$(npm root -g)}"; T=build/i18n/tools; D=/tmp/i18n-status; mkdir -p "$D"
echo "== 1. build (data patches, build.py, curio tiers)"
bash build/patches/apply_all.sh 2>&1 | grep -E "^i18n (vi|ru|pt|es): .*(translated sentences|references)|Traceback|Error" | sed 's/^/   /' || true
echo "== 2. what has no translation yet"
node $T/names_todo.js dist/Linggango_Relic_Wiki.html "$D/names_todo.json" | sed 's/^/   names: /'
python3 $T/adopt_vanilla.py --dry | sed 's/^/   the game'"'"'s own names still to take in: /'
bash $T/status.sh "$D" 2>&1 | sed -n '1,200p' | grep -E "^==|^ +(boss|cfg|fx|gear|guide|names|relic|src|st|ui|vocab) " | sed 's/^/   /'
echo "== 3. English names written out inside translations (turn them into ⟦references⟧)"
python3 $T/refs.py scan | sed 's/^/   /'
echo "== 4. checks"
node $T/inv.js 2>&1 | tail -2 | sed 's/^/   /'
python3 $T/qa.py --strict 2>&1 | tail -1 | sed 's/^/   qa.py: /'
python3 $T/refs.py check --strict | sed 's/^/   /'
if [ "$1" = "--identity" ] && [ -n "$2" ]; then echo "== 5. English unchanged?"; bash $T/identity.sh "$2" 2>&1 | tail -5 | sed 's/^/   /'; fi
cat <<'EOF'
== next
   a sentence missing        -> python3 build/i18n/tools/merge.py --domain <ui|fx|st|…> --pairs batch.json   (docs/I18N.md, "Adding strings")
   names missing             -> python3 build/i18n/tools/names_show.py /tmp/i18n-status/names_todo.json 0 200, write index|vi|ru|pt|es lines, merge.py --domain names <list> <batch.txt>
   English name in a sentence-> python3 build/i18n/tools/refs.py apply <lang>   (pt, es: then refs.py gender <lang>; ru: refs.py patch / forms)
   a native speaker's review -> python3 build/i18n/tools/review.py export <lang>
   then run this again; before a push: bash build/check.sh
EOF
