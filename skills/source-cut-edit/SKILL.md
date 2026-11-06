---
name: source-cut-edit
description: Write a Source Cut film or Short edit with the engine (engine/build_lib.py + engine/film_helpers.py) - narration lines with document cards and marker sweeps, quote clips, photos, bands, chapters, stamps, key lines, checklists, music and the end card - producing a HyperFrames index.html and subtitles. Use when building or changing film/build.py or short/build.py.
---

# Edit

The edit is Python that writes HTML. It is a **sequence on a cursor** (`E.t`): each call places its piece at the
cursor and moves it on, so the picture follows the voice and timing never drifts. Start from
`templates/film/film/build.py` and read `examples/wework/film/build.py` for a complete film.

## Setup

```python
E = Edit(ROOT, 1920, 1080)                     # 1080, 1920 for the Short
E.caps_all, E.drift, E.cap_mode = True, True, "line"   # film: every line captioned, slow drift, line captions
E.hero = {"w0a": "fortyseven"}                 # one emphasis word per line (normalised: lower case, no punctuation)
H.setup(E, chapters=5)
vo, art, photo, band, wi, chapter, M = H.vo, H.art, H.photo, H.band, H.wi, H.chapter, H.M
```

## The vocabulary

| Call | Places |
| --- | --- |
| `vo(id, [shots], gap=0.3, cuts=[...], kw=[...])` | a narration line and the shots under it; `cuts` are word indices where the picture changes; `kw` holds a key line on screen |
| `art(name, label, marks=[(phrase, word)])` | a document card: `media/artifacts/c-<name>.png`, centred on its marks, slow push-in; the marker for phrase k starts on word index `word` |
| `photo(file, label, view)` | a credited photo with a slow move (`view` = start and end `(y, zoom)`) |
| `band(name, label)` | archive footage at its own 16:9 shape with a label |
| `E.quote(clip, "Speaker · Programme, date", "auto:word,word", low="full")` | a quote clip: picture, voice, every word captioned, attribution bar |
| `chapter(n, "Title")` | chapter card with a progress bar |
| `E.stamp("August 2019", a, b)` | date or place stamp, top left |
| `E.key("Line one.\|*Line two*.", a, b, "K")` | a held key line; `*word*` is the blue highlight, `\|` a line break |
| `E.checklist(title, [rows], dur)` | the lesson recap card |
| `E.number(a, b, value)`, `E.bars(...)`, `E.timeline(...)`, `E.qcard(...)` | counters, bar charts, timelines, text quotes |
| `E.music(file, a, b, media_start, vol, fade_in, fade_out, lane)` | music cues (alternate lanes to crossfade) |
| `E.endcard(dur, "Find your people. hackyard.org")` | the brand end card (CTA on the end card only) |
| `E.write(title)`, `E.write_srt(path)` | write `index.html` and the subtitles |

`wi(id, "word", n)` finds a word's index in a line (the n-th match), so marks and cuts are written against the script,
not against seconds.

## Rules

- One idea per shot. Change the picture when the subject of the sentence changes (`cuts`).
- Every number, date or quote the narrator says is on a card with its marker, or on a key line.
- Labels are credits: "Outlet · Document, date" for documents, "Person, year · photo: author" for photos.
- Text never covers a face. Captions sit under the card on the film, under the band on the Short.
- Music sits low (about 0.09–0.13) and changes at chapter boundaries; check every cue fits its track (`E.music`
  asserts it).
- Short: frame one is the hook (`E.key(..., instant=True)` over the first card), and the last line returns to that
  card so the loop is invisible.

Run `python3 build.py`; it prints clip and tween counts, the length and the chapter times. Then `source-cut-review`.
