---
name: source-cut
description: Make an evidence-based documentary (a 6–8 minute 16:9 film plus a 50-second 9:16 Short) with the Source Cut workflow - real archive footage, real photos, real documents on screen with a marker on the exact words, Azure narration, HyperFrames edits rendered on a VM, and A/B/C thumbnails. Use when the user asks to make a documentary, explainer film, business story video or a batch of them, or asks how this workflow works.
---

# Source Cut: make a documentary where every frame has a source

You are producing a short documentary. Read `docs/principles.md` once; its rules override speed.

## The pipeline (one skill per step)

| # | Step | Skill | Output |
| --- | --- | --- | --- |
| 0 | One-time setup: VM, Docker image, Azure keys, assets | `source-cut-setup` | `.env`, `hyperframes-runner` image |
| 1 | Scaffold: `scripts/new-film.sh <slug>` | (this skill) | `films/<slug>/` |
| 2 | Research every fact, quote and photo | `source-cut-research` | `RESEARCH.md`, `media/images/` |
| 3 | Write the script | `source-cut-script` | `SCRIPT.md`, `voice/lines.tsv` |
| 4 | Voice it and get word timings | `source-cut-voice` | `media/voice/*.mp3`, `words.jsonl` |
| 5 | Build the document cards | `source-cut-documents` | `media/artifacts/*.png`, `rects.json` |
| 6 | Cut quotes and b-roll bands | `source-cut-footage` | `media/footage/*.mp4`, `words.jsonl` |
| 7 | Edit the film and the Short | `source-cut-edit` | `film/index.html`, `short/index.html` |
| 8 | Review every shot on contact sheets | `source-cut-review` | fixes |
| 9 | Render, loudness, subtitles | `source-cut-render` | `renders/final.mp4`, `.srt` |
| 10 | Thumbnails A/B/C | `source-cut-thumbnails` | `thumbnail/renders/*.jpg` |
| 11 | Upload package | `source-cut-upload` | `UPLOAD.md` |

Steps 4, 5 and 6 can run in parallel once the script is locked. Step 8 is never skipped, and it runs again after every fix.

## How to work

- Start from `examples/wework/` when unsure how a piece should look: it is a complete, published film.
- Nothing heavy runs on the user's laptop. Snapshots, renders, page captures and background removal run on the VM;
  laptops run Python that writes HTML and small ffmpeg jobs with `-threads 4`, one at a time.
- Keep keys in `.env`. Never print them, never write them into files you commit.
- In a batch of films, every film gets the same checks. Do not lower facts, depth or polish to go faster.
- Before the final render, show the user the contact sheets (or a preview) and get a yes. Renders are expensive.

## Definition of done

- Every narrated fact traces to a row in `RESEARCH.md`, and every document card's marker sits on the words being said.
- Every photo and clip is credited on screen and in the description.
- Film and Short are rendered, at -15 LUFS integrated with true peaks under -1.3 dB, with subtitles.
- Three thumbnails exist and were reviewed for invented text, spelling and likeness.
- `UPLOAD.md` is complete: titles, description with chapters, sources and credits, tags, pinned comments.
