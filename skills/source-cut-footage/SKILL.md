---
name: source-cut-footage
description: Turn archive video into Source Cut quote clips and b-roll bands - download only the needed sections, check the frames, transcribe, find quotes by their words, and cut clips with word timings (tools/sources/yt_sections.sh, tools/qc/sheet.py, tools/edit). Use when the film needs a person speaking on camera or real period footage.
---

# Quotes and bands

```bash
tools/sources/yt_sections.sh films/<slug>/media/raw <videoId> 1:02-1:31,4:10-4:40
python3 tools/qc/sheet.py films/<slug>/media/raw /tmp/raw-sheet.jpg      # look before you cut
tools/edit/clip_words.sh films/<slug>/media/raw films/<slug>/media/raw/words.jsonl
```

Pick each quote by reading the timed lines `clip_words.sh` prints. Get its exact span with
`qspec.span(W, "<videoId>-102-131", "first words", "last words")`, list it in `edit/quotes.json`, and run
`python3 tools/edit/qcut.py films/<slug>/edit/quotes.json`. Clips land in `media/footage/` at 1280x720/25 fps with their
words in `media/footage/words.jsonl`.

## Downloading

YouTube's bot check needs a PO-token provider (bgutil server on 127.0.0.1:4416), Node.js for yt-dlp's JS runtime, and
the `mweb,web_safari` player clients for 720p. The script waits a few seconds between requests: keep it polite.

## Rules that came from mistakes

- **Never slow a speech clip.** Lips drift off the voice. The engine holds on black past a clip's last frame instead.
- **Check every band for burned-in text** (lower thirds, tickers, logos) and for the wrong subject (an interviewer
  instead of the company). Re-cut on exact scene boundaries.
- **Low-resolution clips** (under about 640 px wide) look broken on a 1080p film: play the person's audio over a
  credited photo of them instead.
- In a 9:16 Short, people sit in a full-width 16:9 band with captions under it, never cropped to fill the frame.
- Quotes start about 0.15 s before the first word and end 0.4 s after the last (qcut does this).
- Credit every clip on screen (speaker, programme, date) and in the description with a link.

Rights: short quotes for commentary and criticism are common practice, but the call is yours and the rules differ by
country and platform. Prefer the original channel, keep clips short, and never re-upload whole programmes.
