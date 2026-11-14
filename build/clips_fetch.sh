#!/usr/bin/env bash
# Fetch the spell clips (the workspace branch's clips/: <ns>__<spell>.mp4 and its .webp poster) into build/clips3, without the rest of that branch.
# build.py and patches/wiki_data.py put the approved ones (build/clips/approved.json) on the site; without them the build lists no clip.
# CI does the same with actions/checkout (.github/workflows/site.yml). Needs network; about 500 MB.
set -euo pipefail
H="$(cd "$(dirname "$0")" && pwd)"; R="$(dirname "$H")"; T="$H/clips3"
git -C "$R" fetch -q --filter=blob:none origin workspace:refs/remotes/origin/workspace
mkdir -p "$T"
git -C "$R" archive origin/workspace clips | tar -x -C "$T" --strip-components=1
echo "clips: $(ls "$T" | grep -c '\.mp4$') clips in $T"
