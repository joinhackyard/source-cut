#!/usr/bin/env bash
# clip_words.sh <raw dir> <out.jsonl>: transcribe every downloaded section (mp4) and print it as timed lines, so you can
# pick quotes by reading. Word rows go to <out.jsonl> for qspec.span() and qcut.py.
set -euo pipefail
T=$(cd "$(dirname "$0")/.." && pwd)
python3 "$T/voice/azure_stt.py" "$1" "$2" --small > /dev/null
python3 - "$2" <<'PY'
import json, sys
for l in open(sys.argv[1]):
    d = json.loads(l); line = []; t0 = None
    print("==", d["file"])
    for x in d["words"]:
        if t0 is None: t0 = x[1]
        line.append(x[0])
        if len(line) >= 14 or x[0].endswith((".", "?", "!")):
            print(f"  {t0:7.2f}-{x[2]:7.2f} {' '.join(line)}"); line = []; t0 = None
    if line: print(f"  {t0:7.2f}-       {' '.join(line)}")
PY
