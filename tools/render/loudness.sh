#!/usr/bin/env bash
# loudness.sh <in.mp4> <out.mp4>: two-pass EBU R128 loudnorm to -15 LUFS / -1.5 dBTP (video stream copied), then a
# true-peak limiter, then prints the measured result. Single-pass loudnorm left films at -16 to -17 LUFS; a second
# single pass overshot the peak. Two passes plus alimiter=0.78 lands at -15 to -15.5 LUFS with peaks <= -1.3 dB.
# Run it on the VM (or anywhere ffmpeg is): it is light, but it reads the whole file twice.
set -euo pipefail
IN=$1; OUT=$2
J=$(ffmpeg -hide_banner -threads 4 -i "$IN" -af loudnorm=I=-15:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -threads 4 -i "$IN" -c:v copy -af "loudnorm=I=-15:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,alimiter=limit=0.78:level=false" \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
ffmpeg -hide_banner -threads 4 -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+I:|Peak:" | tail -2 | tr -s ' ' | tr '\n' ' '; echo
