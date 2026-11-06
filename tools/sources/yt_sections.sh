#!/usr/bin/env bash
# yt_sections.sh <out dir> <video id> <start-end[,start-end...]> [<video id> <sections> ...]
# Download only the sections you will quote (720p H.264 + AAC), e.g.
#   tools/sources/yt_sections.sh films/my-film/media/raw dQw4w9WgXcQ 1:02-1:31,4:10-4:40
#
# Use this for short quotes you will credit on screen and link in the description, and check the rules where you
# publish. Prefer the original uploader's channel, keep clips short, and never re-upload whole programmes.
#
# YouTube's bot check (late 2026) needs three things: a PO token provider (bgutil-ytdlp-pot-provider server running on
# 127.0.0.1:4416), the Node.js runtime for yt-dlp's JS challenges, and the mweb + web_safari clients for 720p.
set -euo pipefail
O=$1; shift
mkdir -p "$O"; cd "$O"
X=(--js-runtimes node --extractor-args "youtube:player_client=mweb,web_safari")
while [ $# -gt 1 ]; do
  id=$1; secs=$2; shift 2
  IFS=',' read -ra parts <<< "$secs"
  for sec in "${parts[@]}"; do
    tag=${sec//:/}
    yt-dlp -q --no-warnings "${X[@]}" -f "bv*[height<=720][vcodec^=avc1]+ba[ext=m4a]/b[height<=720]" --merge-output-format mp4 \
      --download-sections "*$sec" --postprocessor-args "ffmpeg:-threads 4" \
      -o "$id-$tag.%(ext)s" "https://www.youtube.com/watch?v=$id" && echo "ok $id $sec" || echo "FAIL $id $sec"
    sleep 6   # stay polite: one request every few seconds
  done
done
