#!/usr/bin/env bash
# Where the translations stand (docs/I18N.md). Run from the repo root after apply_all.sh: bash build/i18n/tools/status.sh [dir]   (the lists stay in dir for the next steps; default /tmp/i18n-status)
set -e; D="${1:-/tmp/i18n-status}"; mkdir -p "$D"; export NODE_PATH="${NODE_PATH:-$(npm root -g)}"; T="$(dirname "$0")"
node "$T/domains.js" "$D/domains.json" >/dev/null; node "$T/todo.js" "$D/todo.json" >/dev/null; python3 "$T/status.py" "$D"
