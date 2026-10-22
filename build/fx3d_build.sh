#!/usr/bin/env bash
# Rebuild src/fx3d.js (three.js r169 + fx3d.src.js + geo2three.js, one minified IIFE). Reproduces the committed file byte for byte
# (esbuild 0.19-0.25 all give the same output; the file has no trailing newline). Usage: bash build/fx3d_build.sh [--check]
set -euo pipefail; cd "$(dirname "$0")"
[ -d node_modules/esbuild ] && [ -d node_modules/three ] || npm install --no-audit --no-fund --no-package-lock >/dev/null
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
node_modules/.bin/esbuild fx3d.src.js --bundle --minify --format=iife --outfile="$T/out.js" --log-level=error
head -c -1 "$T/out.js" > "$T/nonl.js"
if [ "${1:-}" = "--check" ]; then cmp "$T/nonl.js" src/fx3d.js && echo "fx3d.js: reproducible"; else cp "$T/nonl.js" src/fx3d.js; echo "src/fx3d.js rebuilt"; fi
