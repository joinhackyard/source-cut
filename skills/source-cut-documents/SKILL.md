---
name: source-cut-documents
description: Build the document cards for a Source Cut film - capture real web pages or set exact excerpts on clean pages, record where each quoted phrase sits (rects.json), and verify every mark. Use when the script names a filing, release, article or letter that should appear on screen with a marker.
---

# Document cards

A document card shows the real source while the narrator reads from it, and a blue marker sweeps the exact words.

## Two ways to get a card

**1. Capture the live or archived page** (best when it reads well as it is): add a job to an `artifacts.json` with
`{name, url, width, height, anchor, marks}` and run `tools/sources/capture_artifacts.mjs` in the runner image on the VM.
`anchor` scrolls the sentence about 18% down the frame; cookie banners and sticky headers are removed; `marks` are the
phrases whose rectangles are recorded.

**2. An excerpt page** (best for a 300-page filing, a scanned PDF or a cluttered site): in `edit/pages.py`, call
`Pages.page(name, masthead, date, headline, byline, paragraphs, marks)`. Use the real outlet, date, headline and byline;
quote the paragraphs verbatim; put `"…"` where you skip text. The builder refuses a mark that is not word for word in
the text. Then `P.capture()` screenshots every page on the VM into `media/artifacts/c-<name>.png` and `rects.json`.

## Rules

- The marked phrase is the words the narrator says, from the source, not a paraphrase.
- One idea per card. Two or three marks at most, each landing on its own word in the line.
- If a phrase appears twice on a page, anchor the excerpt so the right occurrence is the one recorded. A wrong
  occurrence is a common mistake: the contact sheet will show a marker on the wrong line.
- If you trim a sentence, start the fragment with "…".
- Keep excerpts short and link the full source in the description.

## Verify

`capture()` prints each card's height and flags any mark that is missing or below the bottom of the shot. Fix those
before editing. Then look at every PNG once: masthead, date and headline must be the real ones.
