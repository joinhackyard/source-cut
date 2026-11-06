# Series documentary template (daily YouTube film + Short)

Hackyard runs several daily series (Founder Files, How It Was Built, The Fall, Explained, Rivals, Built Here, The
Decision). Every film in every series uses one edit. Producer feedback, 3 Nov 2026: "editing should match across all
videos". Copy a finished project and change only the content, never the grammar. Hackyard's reference project was its
Rivals film on Microsoft and Apple.

The honesty rules apply to every film. Read them before you write a script:

- No AI-generated people presented as real. No invented headlines or quotes.
- Attribute characterisations ("critics called it…", "according to the SEC filing…"), never state them as fact.
- Credit every photo, clip and document on screen, and again in the description.
- Photos come from Wikimedia Commons or other licensed sources only.
- A redrawn or excerpted document is checked line by line against the original before render.

## Shared engine (never fork it per project)

- `engine/build_lib.py`, `engine/template.html` and `engine/film_helpers.py` are shared by every project. Keep one copy.
  If you vendor them into a project, check they are byte-identical with `md5` before rendering. A fix goes into every
  project, not one.
- A new project also needs `film/assets/{fonts,lib}` and `short/assets/{fonts,lib}` copied in (fonts and the vendored
  GSAP).
- Narrator: Azure `en-US-Andrew:DragonHDLatestNeural`. Captions use the script text, aligned to the STT word timings.

## Film (1920×1080, 6–8 min)

| Beat               | Code                                                                                                                    | Notes                                                                                                                                  |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Black lead-in      | `E.pause(0.7, ["black"])`                                                                                               |                                                                                                                                        |
| Cold open, 30–45 s | 4–5 lines                                                                                                               | Real footage or document first. One date stamp. A founder quote in their own clip if one exists. Ends on two black `K` question cards. |
| Series title       | `E.chapter("SERIES NAME", "Short title", 4.6)`                                                                          | Series name in capitals.                                                                                                               |
| Chapters 1–5       | `E.chapter(f"{n}/5", title, 3.8)`                                                                                       | Two-word titles where possible.                                                                                                        |
| Chapter 5 tail     | `vo(..., ["black"], gap=1.2, kw=[(0, "Tomorrow: *Next title*", "K")])`                                                  | Names the next film on the calendar.                                                                                                   |
| Lesson             | `E.chapter("", "What to take from it", 3.4)`, a picture line, three numbered black `K` lines, `E.checklist(...)`, 4.4 s | Exactly three takeaways.                                                                                                               |
| Close              | One line over footage, then black with a `K` card                                                                       |                                                                                                                                        |
| End card           | `E.endcard(4.6, "Find your people. hackyard.org")`                                                                      | The only brand mention. Swap in your own line.                                                                                         |
| Music              | Three or four segments from `media/bgm`, at 0.11, 0.09 and 0.12, crossfaded at chapter 2 and at the chapter 5 rehook    | `assert` that every segment fits its track length.                                                                                     |

- **Cards:** documents use `art()` with `V(y)` views and a marker on the words the narrator says. Photos use `photo()`
  with a label that credits the source. Footage bands carry a label with the source and date.
- **Built graphics:** `E.number`, `E.bars` and `E.timeline` carry the key numbers, one or two per chapter at most.
- **Quotes:** `E.quote(clip, label, "auto:word", low="full")`. These play the original clip with its own sound and no
  music-duck tricks.

## Short (1080×1920, 45–55 s)

- **Frame one:** a document card with the hook as `E.key("…", 0.0, …, "O", instant=True)` on the dark plate above the
  card. The hook never sits over a face.
- **Chapters:** three, via `chapter(n, title, body)`, with the `n/3` counter pill and `tick.wav`.
- **Close:** a loop line that runs into the first line, over the frame-one card. Then
  `E.mark("hackyard.org", a - 1.0, E.t)`, with no end card.
- **Music:** one track at 0.13, ending on the loop. (Hackyard used HeyGen catalog track `m-c45eea55`.)

## Checks (twice before any render)

1. `tools/qc/check.sh <proj> <tag>` snapshots every shot of the film and the Short at 60% of its length on the render
   VM and tiles them into contact sheets (`tools/qc/shot_times.py` picks the times, `tools/qc/pullsheet.py` pulls and
   tiles them). Look at every tile.
2. Fix the problems, rebuild, then run the late pass with a new tag. It snapshots each shot at 92% of its length, once
   the markers have landed. Look again.
3. Run `tools/render/render-final.sh`, then QC the final file: duration, loudness (−15 LUFS, peak ≤ −1 dB) and a contact
   sheet (`tools/qc/sheet.py`).

`render-final.sh` renders the film in four chunks, two at a time (12 workers each), renders the Short (16 workers), joins
the film chunks with the ffmpeg concat demuxer (`-c:v copy`), and normalises both with
`loudnorm=I=-15:TP=-1.5:LRA=11`, AAC 192k, 48 kHz, `+faststart`. Copy it to the render VM and run it there.

## Helper tools

| Tool                                         | Use                                                                                                                                       |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `tools/sources/yt_sections.sh`               | Downloads only the needed seconds of YouTube clips.                                                                                       |
| `tools/sources/commons_fetch.py`             | Fetches Wikimedia Commons images with their author and licence for the credit line.                                                       |
| `tools/sources/pages.py`                     | Builds verbatim excerpt pages and captures them on the VM. It asserts that every mark is in the text and reports marks outside the frame. |
| `tools/sources/capture_artifacts.mjs`        | Captures live or archived web pages and writes the pixel boxes of each marked phrase (see `artifact-reel.md`).                            |
| `tools/voice/azure_tts.py`                   | Voices the script, one file per line. Add a `PRON` table of IPA or aliases for names the voice gets wrong, and check each name with STT.  |
| `tools/voice/azure_stt.py`                   | Azure fast transcription with word timings.                                                                                               |
| `tools/voice/revoice.sh`                     | Re-voices selected lines and merges their words.                                                                                          |
| `tools/edit/clip_words.sh`                   | Transcribes source clips with Azure STT, giving word timings. Sends 16 kHz / 32 kbps copies so a slow uplink stays usable.                |
| `tools/edit/qspec.py` + `tools/edit/qcut.py` | Cut quote clips from phrase spans (0.15 s lead, 0.4 s tail, words shifted) and muted bands.                                               |
| `engine/film_helpers.py`                     | The shared `art()` / `frame()` / `vo()` helpers. Cards auto-frame on the marked words.                                                    |
| `tools/qc/sheet.py`                          | Builds a frame contact sheet per clip or per final file.                                                                                  |
| `tools/qc/check.sh`                          | The two checks above.                                                                                                                     |
| `tools/render/render-final.sh`               | The final render (run it on the VM).                                                                                                      |
| `tools/render/loudness.sh`                   | Two-pass EBU R128 loudnorm to −15 LUFS / −1.5 dBTP with the video copied, then prints the result.                                         |
| `tools/thumbnails/gpt_thumbs.py`             | Three thumbnail variants per video. See `thumbnails.md`.                                                                                  |

Never run two STT jobs at once if your STT script stages audio in a shared temp folder: they overwrite each other.

Write an `UPLOAD.md` per film: title, description, chapters, the full credit list and the thumbnail notes.

**Burned-in text:** crop away tickers, lower thirds and burned subtitles before using a clip (for example
`crop=1066:600:107:0` or `crop=960:540:0:0`). Our captions must never sit on another broadcaster's text.
