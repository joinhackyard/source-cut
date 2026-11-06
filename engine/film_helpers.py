"""Shorthand used by every film's build.py: document cards that centre on their marked lines, photos, archive bands,
chapters, and a vo() that lets a marker sweep line after line of a long phrase.

    from film_helpers import H
    H.setup(E)                       # E = build_lib.Edit(...)
    vo, art, photo, band, wi = H.vo, H.art, H.photo, H.band, H.wi
    vo("w2e", [art("s1-lease", "The We Company · Form S-1, SEC, 14 August 2019",
                   marks=[(0, wi("w2e", "fifteen")), (1, wi("w2e", "forty-seven"))])])

art(name, label, marks): name is the capture name without "c-" (media/artifacts/c-<name>.png); marks are
(phrase index in rects.json, word index in the narration line). The marker starts sweeping on that word; every
further line of a wrapped phrase starts 0.25 s after the one before.
"""
import json

import build_lib


class _Helpers:
    def setup(self, E, chapters=5):
        self.E, self.chapters, self.M = E, chapters, {}
        self.RECTS = json.loads((build_lib.MEDIA / "artifacts" / "rects.json").read_text())
        return self

    def wi(self, vid, word, n=1):
        """Index of the n-th word in a narration line that matches `word` (case and punctuation ignored)."""
        hits = [i for i, w in enumerate(self.E.words[vid]) if build_lib._norm(w[0]) == build_lib._norm(word)]
        if len(hits) < n:
            raise SystemExit(f"{vid}: word {word!r} not found {n}x in: {' '.join(w[0] for w in self.E.words[vid])}")
        return hits[n - 1]

    def art(self, name, label, marks=(), view=None, cx=0.45):
        """Document card. With no view, the card centres on the marked lines and pushes in slowly."""
        ms, xs, ys = [], [], []
        for k, t in marks:
            for j, r in enumerate(self.RECTS["c-" + name]["marks"][k]["rects"]):
                if r[2] > 4:
                    ms.append((r, t if j == 0 else ("+", t, 0.25 * j)))
                    xs += [r[0], r[0] + r[2]]
                    ys += [r[1], r[1] + r[3]]
        if view is None:
            view, cx = self.frame(name, xs, ys, 1320, 700, 1.12)
        return {"art": "artifacts/c-" + name + ".png", "label": label, "view": view, "marks": ms, "cx": cx}

    def frame(self, name, xs, ys, cw, ch, smax):
        """Centre on the marked lines; zoom no further than keeps every marked word on the card (push-in of 6%)."""
        w, h = self.RECTS["c-" + name]["w"], self.RECTS["c-" + name]["h"]
        if not xs:
            return [(0.4, 1.0), (0.42, 1.06)], 0.45
        sx = 0.92 / ((max(xs) - min(xs)) / w)
        sy = 0.8 * ch / (cw * (max(ys) - min(ys)) / w)
        s0 = round(max(1.0, min(smax, sx, sy) / 1.06), 3)
        cy = round((min(ys) + max(ys)) / 2 / h, 3)
        return [(cy, s0), (cy + 0.01, round(s0 * 1.06, 3))], round((min(xs) + max(xs)) / 2 / w, 3)

    @staticmethod
    def photo(name, label, view=((0.5, 1.0), (0.5, 1.06)), cx=0.5):
        """A photo on the card, slow push-in. view = [(y-centre, zoom) at start, (y-centre, zoom) at end]."""
        return {"art": "images/" + name, "label": label, "view": list(view), "cx": cx, "marks": []}

    @staticmethod
    def band(name, label, ms=0):
        """Archive footage (media/footage/<name>.mp4) at its own 16:9 shape, with its source label."""
        return {"band": "footage/" + name + ".mp4", "label": label, "ms": ms}

    def chapter(self, n, title, dur=3.8):
        self.M[f"c{n}"] = self.E.chapter(f"{n}/{self.chapters}", title, dur)

    def vo(self, vid, shots=(), **kw):
        E = self.E
        fixed = []
        for s in shots:
            if isinstance(s, dict) and "art" in s:
                s = dict(s, marks=[(r, t) for r, t in s["marks"] if not isinstance(t, tuple)],
                         _cont=[(r, t) for r, t in s["marks"] if isinstance(t, tuple)])
            fixed.append(s)
        start = E.t
        E.vo_times[vid] = start
        for s in fixed:
            if isinstance(s, dict) and s.get("_cont"):
                for r, (_, w, d) in s.pop("_cont"):
                    s["marks"].append((r, round(start + E.words[vid][w][1] + d, 3)))
        kw.setdefault("low", True)
        return E.vo(vid, fixed, **kw)


H = _Helpers()
