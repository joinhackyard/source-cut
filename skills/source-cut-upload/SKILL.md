---
name: source-cut-upload
description: Write the UPLOAD.md package for a Source Cut film and Short - titles, description with hook, chapters, sources and credits, tags, pinned comments, thumbnail test plan and a pre-publish checklist. Use when renders and thumbnails are done.
---

# Upload package

Fill `films/<slug>/UPLOAD.md` from the template. `examples/wework/UPLOAD.md` is a complete published one.

## Documentary

- **Title:** the promise, under ~60 characters; a second title for an A/B title test. Do not repeat the thumbnail text.
- **Description:** two or three sentences that restate the hook honestly; then **chapters** (`0:00 …`, taken from the
  chapter times `build.py` prints); then **sources** (every document and article with its link, in film order); then
  **footage** (speaker, programme, date, link); then **photos** from `media/images/CREDITS.md` (file, link, author,
  licence); then music credits; then the CTA line.
- Note any disagreement between sources ("Lockheed and the Smithsonian give 143 days; the Air Force's 1978 history
  gives 145").
- **Thumbnails:** A as the main thumbnail, B and C in Test & compare; list the photo and document credits, and say if
  people or documents were redrawn by an image model. Leave a line to record the winner.
- **Tags**, playlist, category, and a **pinned comment** that asks a real question about the film.

## Short

Its own title, a one-line description that points to the full film, tags, and a pinned comment. Link the documentary
as the Short's related video once both are live.

## Checklist before publishing

- [ ] Renders final, -15 LUFS, peaks under -1.3 dB; subtitles attached
- [ ] Every source, clip and photo credited in the description
- [ ] Thumbnails reviewed (spelling, invented content, likeness) and Test & compare set up
- [ ] Chapters match the final cut
