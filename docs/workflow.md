# The workflow, end to end

This is the path one film takes, from idea to upload, with the tool for every step. A 7-minute film and its Short take
about a day of focused work; most of it is research and review.

```
idea ─► research ─► script ─┬─► voice + timings ─┐
                            ├─► document cards ──┼─► edit (film + Short) ─► review ─► render ─► loudness ─► upload
                            └─► quotes + bands ──┘                   ▲         │                    thumbnails ─┘
                                                                     └─ fixes ─┘
```

## 1. Scaffold

```bash
scripts/new-film.sh my-film        # films/my-film from templates/film, with fonts, GSAP and sound effects
```

## 2. Research (skill: source-cut-research)

Build `RESEARCH.md`: one row per fact with its source, exact words and status; every quote with a timestamp; every
photo with a licence. List photos in `media/images/commons.json` and fetch them:

```bash
python3 tools/sources/commons_fetch.py films/my-film/media/images/commons.json
```

## 3. Script (skill: source-cut-script)

Cold open, title, five chapters, re-hook, the lesson, close. Write `SCRIPT.md` (line + picture) and
`voice/lines.tsv` (`id<TAB>text`, numbers spelled the way they are said). Short: six to eight lines that loop.

## 4. Voice and word timings (skill: source-cut-voice)

```bash
python3 tools/voice/azure_tts.py films/my-film/voice/lines.tsv films/my-film/media/voice
python3 tools/voice/azure_stt.py films/my-film/media/voice films/my-film/media/voice/words.jsonl --small
tools/voice/revoice.sh films/my-film w1b w3a        # after a pronunciation fix in voice/pron.json
```

## 5. Document cards (skill: source-cut-documents)

Excerpt pages in `edit/pages.py` (or captures of real pages), screenshotted on the VM with every marked phrase located:

```bash
python3 films/my-film/edit/pages.py     # -> media/artifacts/c-*.png + rects.json
```

## 6. Quotes and bands (skill: source-cut-footage)

```bash
tools/sources/yt_sections.sh films/my-film/media/raw <videoId> 1:02-1:31
python3 tools/qc/sheet.py films/my-film/media/raw /tmp/raw.jpg
tools/edit/clip_words.sh films/my-film/media/raw films/my-film/media/raw/words.jsonl
python3 tools/edit/qcut.py films/my-film/edit/quotes.json
```

## 7. Edit (skill: source-cut-edit)

```bash
python3 films/my-film/film/build.py && python3 films/my-film/short/build.py
```

## 8. Review (skill: source-cut-review)

```bash
tools/qc/check.sh films/my-film /tmp/my-film
tools/qc/check.sh films/my-film /tmp/my-film-late --late
```

Fix, rebuild, check again. Show the sheets and get approval before rendering.

## 9. Render and loudness (skill: source-cut-render)

`render-final.sh` on the VM (chunked, queued), then `loudness.sh` on the joined files: -15 LUFS, peaks at or under
-1.3 dB.

## 10. Thumbnails (skill: source-cut-thumbnails)

```bash
python3 tools/thumbnails/gpt_thumbs.py films/my-film      # A, B, C from thumbnail/gpt.json
```

Review every image for invented content, spelling and likeness; check at phone size; score.

## 11. Upload (skill: source-cut-upload)

`UPLOAD.md`: titles, description with chapters, sources and credits, tags, pinned comments, the thumbnail test plan.

## Batches

Five films in a week work if research and scripts are done first, voice and cards run in parallel, renders are queued
back to back on one VM, and every film still gets steps 8 and 10 in full. The checks are cheap; skipping them is how
mistakes ship.
