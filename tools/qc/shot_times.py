#!/usr/bin/env python3
"""shot_times.py <index.html> [--late]: one snapshot time per shot of a HyperFrames composition, comma separated.

Cards (documents, charts, chapters, key lines) are sampled 60% of the way in, when the marker has usually swept;
--late samples them at 92%, to check the end state (every mark drawn, nothing clipped). Videos are sampled at the middle.
Times closer than 1.2 s are merged. Feed the output to `hyperframes snapshot --at`.
"""
import re
import sys

s = open(sys.argv[1]).read()
late = "--late" in sys.argv
CARDS = ["artc", "barcard", "tlcard", "choicecard", "numcard", "qcard", "chapter", "checklist", "gridcard", "st-K", "st-T", "st-O"]
pts = set()
for m in re.finditer(r'class="clip ([a-z][^"]*)"[^>]*?data-start="([\d.]+)" data-duration="([\d.]+)"', s):
    if any(k in m[1] for k in CARDS):
        a, d = float(m[2]), float(m[3])
        pts.add(round(a + d * (0.92 if late else 0.6), 1))
for m in re.finditer(r'<video[^>]*?data-start="([\d.]+)" data-duration="([\d.]+)"', s):
    a, d = float(m[1]), float(m[2])
    pts.add(round(a + d * 0.5, 1))
out = []
for t in sorted(pts):
    if not out or t - out[-1] >= 1.2:
        out.append(t)
print(len(out), "shots", file=sys.stderr)
print(",".join(map(str, out)))
