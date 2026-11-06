#!/usr/bin/env bash
# check.sh <film dir> <out prefix> [--late]: snapshot every shot of the film and the Short on the render VM and tile them
# into contact sheets (<prefix>-f*.jpg for the film, <prefix>-s*.jpg for the Short). Review every sheet before rendering:
# wrong occurrence on a card, a mark that misses its words, text over a face, a lower third baked into a clip, a black gap.
set -euo pipefail
. "$(dirname "$0")/../lib/env.sh"
F=${1%/}; O=$2; Q=$(cd "$(dirname "$0")" && pwd)
for part in film short; do
  [ -f "$F/$part/index.html" ] || continue
  AT=$(python3 "$Q/shot_times.py" "$F/$part/index.html" ${3:-})
  SID=$("$Q/../render/vm.sh" "$F/$part" snapshot --at "$AT" 2>&1 | grep -o "snapshots/[^/]*/" | head -1 | cut -d/ -f2)
  if [ "$part" = film ]; then python3 "$Q/pullsheet.py" "$SOURCE_CUT_REMOTE_ROOT/$F/film" "$SID" "$O-f" 384 216 5 30
  else python3 "$Q/pullsheet.py" "$SOURCE_CUT_REMOTE_ROOT/$F/short" "$SID" "$O-s" 270 480 8 16; fi
done
