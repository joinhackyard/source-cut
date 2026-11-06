---
name: source-cut-research
description: Research a Source Cut documentary - find primary sources for every fact, exact quotes with timestamps, on-camera clips and licensed photos, and record them in RESEARCH.md and media/images/commons.json. Use before writing any script, and whenever a new claim is added.
---

# Research

The film can only say what the research pack proves. Build `RESEARCH.md` first.

## Sources, best first

1. **Primary documents:** regulatory filings (SEC EDGAR: S-1, 10-K, 10-Q, 8-K, Form RW), court records, company press
   releases and blog posts, shareholder letters, patents, official histories (for example US government histories,
   which are public domain).
2. **The person's own words on record:** interviews, keynotes, talks, books, posts.
3. **Reputable reporting:** name the outlet, the reporter and the date. Mark it REPORTED when it rests on unnamed sources.
4. Never: content farms, AI summaries, unsourced listicles, Wikipedia as the final source (use its citations).

Use the Wayback Machine for pages that changed or vanished, and save a copy of every source page you quote.

## The pack

For every fact, one row: the line as the narrator will say it, the source with link and date, the **exact words** in
the source, its status (VERIFIED primary / REPORTED by a named outlet), and how it will appear (card, quote, photo).
Write down disagreements (one source says 143 days, another 145) and say so in the description later.

Characterisations ("reckless", "visionary") are only ever quoted, with the outlet named on screen.

## Quotes on camera

Search the subject's interviews, keynotes and news reports. For each candidate: speaker, programme, date, link, the
in–out time and the exact words. Prefer the original uploader. Keep quotes short (5–25 s). Check the frames with
`tools/qc/sheet.py` before choosing: burned-in lower thirds, logos, or an interviewer instead of the subject.

## Photos

Wikimedia Commons first (check the licence on each file page: CC BY, CC BY-SA, CC0, public domain), then archives with
clear terms (for example the San Diego Air & Space Museum's Flickr archive, "no known copyright restrictions"; NASA;
national archives). List them in `media/images/commons.json` and run `tools/sources/commons_fetch.py`, which writes
`CREDITS.md` with author and licence. For failure stories, prefer a neutral or serious photo over a grin, unless the
grin is the point.

Never use AI-generated images of real people in the film, and never use frames from another broadcaster's footage as a
"photo".

## Done when

Every line you plan to say has a row, every quote has a timestamp, every photo has a licence, and nothing in the pack
is from memory.
