# Worked example: The Fall, WeWork

"WeWork: From $47 Billion to a Failed IPO", a 7-minute documentary and a 50-second Short, made with Source Cut in
November 2026. Everything needed to rebuild it is here except the media, which belongs to its owners.

| File | What it shows you |
| --- | --- |
| `RESEARCH.md` | The research pack: every fact with its status (verified / reported), source link and exact words. |
| `SCRIPT.md` | The narration as written. |
| `voice/lines.tsv`, `voice/pron.json` | The 50 narration lines as voiced, and the two pronunciation fixes the voice needed. |
| `media/images/commons.json`, `CREDITS.md` | The six Commons photos and their licences. |
| `pages/*.html` | 21 excerpt pages for the SEC filings and company releases, ready to capture. |
| `film/build.py` | The full 16:9 edit: cold open, five chapters, the lesson, the close, music cues. |
| `short/build.py` | The 9:16 Short, with a frame-one hook and a seamless loop. |
| `thumbnail/gpt.json` | Thumbnail A/B/C inputs. |
| `UPLOAD.md` | Titles, description, chapters, sources, credits, tags and pinned comments as published. |

## Rebuild it

```bash
cp -R examples/wework films/wework && cd films/wework
python3 ../../tools/sources/commons_fetch.py media/images/commons.json
python3 ../../tools/voice/azure_tts.py voice/lines.tsv media/voice
python3 ../../tools/voice/azure_stt.py media/voice media/voice/words.jsonl
```

Then:

1. **Documents.** The six news pages (Fast Company, CNBC, Reuters) are not included. Rebuild them from the links in
   `RESEARCH.md` with `tools/sources/pages.py` (names: `fc-deal`, `fc-downturn`, `cc-8b`, `cc-17`, `cs-charge`,
   `cj-son`), then capture all pages to `media/artifacts/`.
2. **Quotes.** Download the clips listed under "Quotes on camera" in `RESEARCH.md` with `tools/sources/yt_sections.sh`,
   transcribe them with `tools/edit/clip_words.sh`, and cut them with `tools/edit/qcut.py` to the names the build uses
   (`wq-wegen`, `wq-community`, `wq-months`, `wq-son`, `wq-bloomberg`, `wq-regrets`, `wq-choose`, `wq-bosa`, and the band
   `wb-space`).
3. **Music.** Put tracks you have the rights to in `media/bgm/` and change the names in the music section.
4. **Build, check, render.** Run `python3 film/build.py`, review the contact sheets from `tools/qc/check.sh`, then
   render on the VM with `tools/render/render-final.sh` and normalise loudness with `tools/render/loudness.sh`.
