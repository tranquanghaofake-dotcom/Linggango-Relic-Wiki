#!/usr/bin/env bash
# Proof that English did not change (docs/I18N.md): the English pages of a build, before and after your change, must be identical.
#   bash build/i18n/tools/identity.sh --save /tmp/base    run BEFORE editing: copies the built index.html and static/ of the current tree
#   ... edit, bash build/patches/apply_all.sh ...
#   bash build/i18n/tools/identity.sh /tmp/base           dumps tooltips, curio pages, Equipment pages and 17 routes of both and compares them
# Run from the repo root. Needs playwright (NODE_PATH=$(npm root -g)).
set -e
T="$(dirname "$0")"; export NODE_PATH="${NODE_PATH:-$(npm root -g)}"
if [ "$1" = "--save" ]; then rm -rf "$2"; mkdir -p "$2"; cp index.html "$2/"; cp -r static "$2/"; echo "baseline saved in $2"; exit 0; fi
B="$1"; [ -f "$B/index.html" ] || { echo "usage: identity.sh --save DIR | identity.sh DIR"; exit 2; }
W="$(mktemp -d)"; bad=0
for t in tips pages gear; do   # one after the other: two captures at once change the timing
  node "$T/dump_$t.js" "$B/index.html" "$W/$t.base.json" >/dev/null; node "$T/dump_$t.js" index.html "$W/$t.new.json" >/dev/null
  if cmp -s "$W/$t.base.json" "$W/$t.new.json"; then echo "$t: identical"; else echo "$t: DIFFERENT"; bad=1; fi
done
node "$T/domdump.js" "$B/index.html" "$W/dom.base.json" >/dev/null; node "$T/domdump.js" index.html "$W/dom.new.json" >/dev/null
python3 "$T/domcmp.py" "$W/dom.base.json" "$W/dom.new.json" | tail -3 | tee "$W/dom.txt"; grep -q " 0 differences" "$W/dom.txt" || bad=1
[ $bad = 0 ] && echo "English identical" || { echo "English CHANGED (dumps in $W)"; exit 1; }
