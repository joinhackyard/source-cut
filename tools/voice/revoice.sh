#!/usr/bin/env bash
# revoice.sh <film dir> <id> [id ...]: re-voice a few narration lines after a script or pronunciation fix, then
# transcribe only those lines and merge their word timings into <film>/media/voice/words.jsonl.
set -euo pipefail
F=${1%/}; shift
T=$(cd "$(dirname "$0")" && pwd)
python3 "$T/azure_tts.py" "$F/voice/lines.tsv" "$F/media/voice" "$@"
D=$(mktemp -d); for i in "$@"; do cp "$F/media/voice/$i.mp3" "$D/"; done
python3 "$T/azure_stt.py" "$D" "$D/new.jsonl"
python3 - "$D/new.jsonl" "$F/media/voice/words.jsonl" <<'PY'
import json, pathlib, sys
new = {json.loads(l)["file"]: l.strip() for l in open(sys.argv[1]) if l.strip()}
p = pathlib.Path(sys.argv[2])
old = [l.strip() for l in p.read_text().splitlines() if l.strip()] if p.exists() else []
out = [new.pop(json.loads(l)["file"], l) for l in old] + list(new.values())
p.write_text("\n".join(out) + "\n")
print("merged", len(out), "rows into", p)
PY
