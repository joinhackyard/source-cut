---
name: source-cut-review
description: Review a Source Cut edit before rendering - snapshot every shot on the VM, tile contact sheets, and check marks, text, faces, footage and timing against a fixed list (tools/qc/check.sh). Use after every build and after every fix, and before asking the user to approve a render.
---

# Review

```bash
tools/qc/check.sh films/<slug> /tmp/<slug>            # mid-shot sheets: <prefix>-f*.jpg (film), -s*.jpg (Short)
tools/qc/check.sh films/<slug> /tmp/<slug>-late --late   # cards at 92%: every mark drawn, nothing clipped
```

Look at every sheet. Check each shot for:

| Check | Typical failure |
| --- | --- |
| Marker on the right words | wrong occurrence of a phrase on the page; mark lands a line early |
| Card readable and framed | zoom too tight cuts a marked word; masthead or date wrong |
| No text over a face | key line or caption on a face; frame-one hook over the photo |
| Footage clean | burned-in lower third or ticker; interviewer instead of the subject; a logo bug |
| Photo right and credited | crop cuts a head; label missing or wrong author |
| No black gaps or flashes | a shot that ends before the next begins |
| Fragments marked | a quote cut mid-sentence without "…" |
| Stamps and chapters | date stamp on the right line; chapter numbering continuous |

Fix in `build.py` (or in the pages and clips), rebuild, and run the check again. Repeat until a full pass is clean.

Then show the user the sheets (or a HyperFrames preview) and get a yes before the final render.

If snapshots time out, a render is probably running on the VM: wait for it or queue.
