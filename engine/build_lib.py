"""Source Cut edit engine: writes a HyperFrames composition (index.html) for a 16:9 film or a 9:16 Short.

A film folder looks like this (see templates/film/):
    my-film/voice/lines.tsv          narration script, "id<TAB>text"
    my-film/media/voice/*.mp3        narration (tools/voice/azure_tts.py) + words.jsonl (tools/voice/azure_stt.py)
    my-film/media/footage/*.mp4      cut quotes and bands (tools/edit/qcut.py) + words.jsonl
    my-film/media/images/            photos + CREDITS.md (tools/sources/commons_fetch.py)
    my-film/media/artifacts/         document captures + rects.json (tools/sources/pages.py)
    my-film/media/bgm/, media/sfx/   music and sound effects you have the rights to
    my-film/film/build.py            the 16:9 edit, written with this engine
    my-film/short/build.py           the 9:16 Short

Both edits are laid out as a sequence: narrator lines, founder clips, chapter cards and pauses are placed one after
another on a cursor, so the edit follows the voice. Captions come from Azure Speech word timings
(media/voice/words.jsonl, media/footage/words.jsonl); narrator captions show the script's words, not the
transcriber's. Every source the edit uses is copied into the project's assets/ so the render VM gets only what it needs.
"""
import difflib
import html
import json
import pathlib
import re
import shutil
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
MEDIA = None  # set by Edit() to <film>/media
FILM = None
# colour grade for archive footage and photos (HyperFrames data-color-grading): muted, slightly dark, a little grain
GRADE = html.escape((HERE / "grade.json").read_text().strip(), quote=True)
GRADE_BRIGHT = html.escape((HERE / "grade-bright.json").read_text().strip(), quote=True)


def _script_lines():
    """Narration text by line id, from <film>/voice/lines.tsv: captions show the script's words, not the transcriber's."""
    f = FILM / "voice" / "lines.tsv"
    if not f.exists():
        return {}
    return dict(l.split("\t", 1) for l in f.read_text().splitlines() if l.strip() and not l.startswith("#"))


def _norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


SCALE = {"hundred", "thousand", "million", "billion", "percent", "dollars"}


def _align(script_text, words):
    """Script tokens with timings borrowed from the transcriber's words.

    Spelled-out numbers ("four hundred and twenty-seven million dollars") come back from the transcriber as one short
    token ("$427") followed by a long "million": the whole run is spread over the full spoken span, by length, so a
    caption never starts before the word before it (which used to leave a caption on screen for the rest of the film)."""
    toks = script_text.split()
    a, b = [_norm(t) for t in toks], [_norm(w[0]) for w in words]
    times = [None] * len(toks)
    if len(toks) == len(words):  # same count: take timings one-to-one (covers "One." vs "1.")
        times = [(w[1], w[2]) for w in words]
    else:
        ops = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
        runs = []
        k = 0
        while k < len(ops):
            tag, i1, i2, j1, j2 = ops[k]
            if tag == "equal":
                for d in range(i2 - i1):
                    times[i1 + d] = (words[j1 + d][1], words[j1 + d][2])
            elif tag == "replace":
                # absorb the scale words that follow a number ("million", "dollars") into one evenly spread run
                t0, t1 = words[j1][1], words[j2 - 1][2]
                while k + 1 < len(ops) and ops[k + 1][0] in ("equal", "delete") and ops[k + 1][2] - ops[k + 1][1] <= 2 and \
                        all(a[x] in SCALE for x in range(ops[k + 1][1], ops[k + 1][2])):
                    k += 1
                    _, _, i2, nj1, nj2 = ops[k]
                    if nj2 > nj1:
                        t1 = words[nj2 - 1][2]
                runs.append((i1, i2, t0, t1))
            k += 1
        def dur_ok(x):
            return 0.075 * len(toks[x]) + 0.12

        for i1, i2, t0, t1 in runs:
            # the transcriber often gives a number ~0.05 s and hands its time to a word just before or after it
            # ("cost", "profit of", "into"): take that time back so the number is captioned while it is said
            need = sum(0.06 * len(toks[x]) + 0.03 for x in range(i1, i2))
            for back in (1, 2):
                p = i1 - back
                if t1 - t0 >= 0.6 * need or p < 0 or not times[p]:
                    break
                ps, pe = times[p]
                if pe - ps > dur_ok(p) + 0.35:
                    times[p] = (ps, round(ps + dur_ok(p), 3))
                    t = ps + dur_ok(p)
                    for q in range(p + 1, i1):  # words between keep their length, moved up
                        d = times[q][1] - times[q][0]
                        times[q] = (round(t, 3), round(t + d, 3))
                        t += d
                    t0 = t
                    break
            n = i2
            while n < len(times) and times[n] and times[n][0] < t1 + 0.01 and n < i2 + 3 and _norm(toks[n]) in SCALE:
                n += 1
            if t1 - t0 < 0.6 * need and n < len(times) and times[n]:
                ns, ne = times[n]
                if ne - ns > dur_ok(n) + 0.35:
                    times[n] = (round(ne - dur_ok(n), 3), ne)
                    t1 = ne - dur_ok(n)
            run = list(range(i1, i2))
            total = sum(len(toks[x]) + 2 for x in run)
            t = t0
            for x in run:
                d = (t1 - t0) * (len(toks[x]) + 2) / total
                times[x] = (round(t, 3), round(t + d, 3))
                t += d
        for i, tm in enumerate(times):  # script-only words: between their neighbours
            if tm is None:
                prev = next((times[j] for j in range(i - 1, -1, -1) if times[j]), (words[0][1], words[0][1]))
                nxt = next((times[j] for j in range(i + 1, len(times)) if times[j]), (words[-1][2], words[-1][2]))
                times[i] = (prev[1], max(prev[1] + 0.05, nxt[0]))
    out, last = [], 0.0
    for t, (s, e) in zip(toks, times):  # strictly in order: each word starts after the one before it
        s = max(s, last + 0.01)
        e = max(e, s + 0.05)
        out.append([t, round(s, 3), round(e, 3)])
        last = s
    return out


def load_words():
    out = {}
    script = _script_lines()
    for path in (MEDIA / "voice" / "words.jsonl", MEDIA / "footage" / "words.jsonl"):
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            d = json.loads(line)
            vid = d["file"].rsplit(".", 1)[0]
            out[vid] = _align(script[vid], d["words"]) if vid in script else d["words"]
    override = MEDIA / "footage" / "words-fixed.json"  # hand-checked founder transcripts
    if override.exists():
        for vid, text in json.loads(override.read_text()).items():
            if vid in out:
                out[vid] = _align(text, out[vid])
    return out


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


SFX_LEN = {"whoosh-1.wav": 0.7, "whoosh-2.wav": 0.85, "whoosh-3.wav": 0.9, "impact-low.wav": 2.1, "riser.wav": 2.85,
           "tick.wav": 0.1, "lock.wav": 0.28, "flap-clatter.wav": 0.6}


class Edit:
    def __init__(self, project, W, H, bright=(), recon=(), brand="Hackyard"):
        """project: the film/ or short/ folder that will hold index.html; its parent is the film folder."""
        global MEDIA, FILM
        self.root = pathlib.Path(project)
        FILM = self.root.resolve().parent
        MEDIA = FILM / "media"
        self.brand = brand
        self.W, self.H = W, H
        self.words = load_words()
        self.bright, self.recon = set(bright), set(recon)
        self.t = 0.0
        self.clips, self.tweens, self.srt = [], [], []
        self.n = 0
        self.track = 0
        self.used = set()
        self.vo_times = {}
        self.caps_all, self.hero = False, {}  # film: caption every narrator line; hero = {vid: "word,word"} emphasis words
        self.drift = False  # slow push-in / pull-out on every video shot
        self.cap_mode = "kinetic"  # reel: 1–3 words at a time; "line" (film): the phrase shows dimmed, each word lights as it's said

    # ---------- media ----------
    def asset(self, rel):
        """media/<rel> → project assets/<rel>; returns the project-relative path."""
        src = MEDIA / rel
        dst = self.root / "assets" / rel
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        self.used.add(rel)
        return f"assets/{rel}"

    def _id(self, p):
        self.n += 1
        return f"{p}{self.n}"

    def shot(self, spec, a, b, band=False, label=None):
        """Picture from a to b. spec: 'footage/x.mp4' | ('footage/x.mp4', media_start) | ('images/x.jpg', 'in'|'out'|'left'|'right') | 'black'."""
        a, b = round(a, 3), round(b, 3)
        d = round(b - a, 3)
        if d <= 0.01:
            return
        if spec == "black":
            self.clips.append(f'<div id="{self._id("k")}" class="clip card" data-start="{a}" data-duration="{d}" data-track-index="1"></div>')
            return
        if isinstance(spec, dict):
            if "band" in spec:  # archive footage at its own 16:9 shape inside a 9:16 frame
                return self.shot((spec["band"], spec.get("ms", 0)), a, b, band=True, label=spec.get("label"))
            if "phone_video" in spec:  # a screen recording in the phone frame, near its native size
                src = spec["phone_video"]
                ms = spec.get("ms", 0)
                avail = duration(MEDIA / src) - ms
                rate = f' data-playback-rate="{round(min(1.0, avail / d), 3)}"' if d > avail else ""
                pl, pt, pw, ph = self.PHONE
                self.clips.append(f'<video id="{self._id("pv")}" class="clip phone" src="{self.asset(src)}" data-start="{a}" data-duration="{d}" '
                                  f'data-media-start="{ms}" data-track-index="1"{rate} muted playsinline '
                                  f'style="left: {pl}px; top: {pt}px; width: {pw}px; height: {ph}px"></video>')
                self._label(spec.get("label"), a, d, pt - 52)
                return
            return self.artifact(spec, a, b)
        src, opt = (spec, None) if isinstance(spec, str) else spec
        name = src.rsplit("/", 1)[-1]
        gr = GRADE_BRIGHT if name in self.bright else GRADE
        path = self.asset(src)
        sid = self._id("s")
        if src.endswith((".jpg", ".png")):
            move = opt or "in"
            pos = {"in": ("scale: 1.0", "scale: 1.09"), "out": ("scale: 1.1", "scale: 1.0"),
                   "left": ("scale: 1.12, xPercent: 2.5", "scale: 1.12, xPercent: -2.5"),
                   "right": ("scale: 1.12, xPercent: -2.5", "scale: 1.12, xPercent: 2.5")}[move]
            self.clips.append(f'<div id="{sid}" class="clip full still" data-start="{a}" data-duration="{d}" data-track-index="1">'
                              f'<img src="{path}" alt="" data-color-grading="{gr}" /></div>')
            self.tweens.append(f'tl.fromTo("#{sid} img", {{{pos[0]}}}, {{{pos[1]}, duration: {d}, ease: "none"}}, {a});')
            if name in self.recon:
                self.clips.append(f'<div id="{self._id("rc")}" class="clip recon" data-start="{a}" data-duration="{d}" data-track-index="11">Reconstruction</div>')
            return
        ms = float(opt or 0)
        avail = duration(MEDIA / src) - ms
        if d > avail + 0.01:
            print(f"  ! {src} needs {d:.2f}s from {ms}, has {avail:.2f}s — slowed to fit")
        rate = min(1.0, avail / d) if d > avail else 1.0
        extra = f' data-playback-rate="{round(rate, 3)}"' if rate < 1 else ""
        # 9:16 crops 16:9 sources around a per-file focus point
        style = f' style="object-position: {self.focus.get(name, 50)}% 50%"' if self.H > self.W and not band and hasattr(self, "focus") else ""
        win = band and self.W > self.H  # 16:9 film: archive footage in a window, label under it, captions below
        cls = "full" if win else "full band" if band else "full"
        video = (f'<video id="{sid}" class="clip {cls}" src="{path}" data-start="{a}" data-duration="{d}" '
                 f'data-media-start="{ms}" data-track-index="1" data-color-grading="{gr}"{extra}{style} muted playsinline></video>')
        if win:
            bl, bt, bw, bh = self.BAND_L
            self.clips.append(f'<div class="bwin" style="left: {bl}px; top: {bt}px; width: {bw}px; height: {bh}px">'
                              f'<div id="{sid}w" class="vw">{video}</div></div>')
            self.tweens.append(f'tl.fromTo("#{sid}w", {{scale: 1.0}}, {{scale: 1.05, duration: {d}, ease: "none"}}, {a});')
            self._label(label, a, d, bt + bh + 26, left=bl)
        elif self.drift:
            # the move goes on an untimed wrapper, never on the timed media element
            self.clips.append(f'<div id="{sid}w" class="vw">{video}</div>')
            s0, s1 = ("1.0", "1.06") if self.n % 2 or band else ("1.06", "1.0")
            self.tweens.append(f'tl.fromTo("#{sid}w", {{scale: {s0}}}, {{scale: {s1}, duration: {d}, ease: "none"}}, {a});')
        else:
            self.clips.append(video)
        if name in self.recon:
            self.clips.append(f'<div id="{self._id("rc")}" class="clip recon" data-start="{a}" data-duration="{d}" data-track-index="11">Reconstruction</div>')

    # 9:16 artifact card: under the signal title, above the low captions
    CARD = (60, 600, 960, 740)
    # 16:9 artifact card: top centre, captions sit under it (low=True on the line)
    CARD_L = (300, 96, 1320, 700)
    # 9:16 phone frame for app screens and recordings (no signal title above it; captions sit lower)
    PHONE = (220, 300, 640, 1150)
    # 16:9 archive-footage window (same top and bottom as CARD_L)
    BAND_L = (338, 96, 1244, 700)

    def _label(self, text, a, d, top, left=None):
        if not text:
            return
        lid = self._id("al")
        if left is None:
            left = self.PHONE[0] if top == self.PHONE[1] - 52 else self.CARD_L[0] if self.W > self.H else 60
        self.clips.append(f'<div id="{lid}" class="clip art-label" data-start="{a}" data-duration="{round(d, 3)}" data-track-index="11" '
                          f'style="top: {top}px; left: {left}px"><span class="bar"></span>{html.escape(text)}</div>')

    def artifact(self, spec, a, b):
        """A real artifact (page capture, scan, slide, photo) on a card, with a slow camera move, marker highlights
        and a source label. spec: {"art": "artifacts/x.png", "label": str, "view": [(cy, s), (cy, s)] (cy = image
        y-fraction at the card centre, s = zoom over fit-to-width), "cx": x-fraction, "marks": [([x, y, w, h] image px,
        time)], "full": True for a full-frame page}. Mark times are film seconds (vo() resolves word indices)."""
        src = spec["art"]
        path = self.asset(src)
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(MEDIA / src)],
                           capture_output=True, text=True)
        W, H = (int(v) for v in r.stdout.split()[0].split(",")[:2])
        full, phone = spec.get("full"), spec.get("phone")
        cl, ct, cw, ch = spec.get("box") or ((0, 0, self.W, self.H) if full else self.PHONE if phone else self.CARD_L if self.W > self.H else self.CARD)
        k = cw / W
        cx = spec.get("cx", 0.5) * W

        def pose(cy, s):
            x = cw / 2 - cx * k * s
            y = ch / 2 - cy * H * k * s
            x = min(0, max(cw - W * k * s, x))  # never show past the artifact's edges
            y = min(0, max(ch - H * k * s, y)) if H * k * s >= ch else (ch - H * k * s) / 2
            return f"x: {round(x, 1)}, y: {round(y, 1)}, scale: {s}"

        (cy0, s0), (cy1, s1) = spec.get("view", [(0.5, 1.0), (0.5, 1.06)])
        sid = self._id("ar")
        marks = []
        for i, (rect, t) in enumerate(spec.get("marks", [])):
            mx, my, mw, mh = (v * k for v in rect)
            marks.append(f'<span class="mk" id="{sid}m{i}" style="left: {mx - 4:.1f}px; top: {my - 2:.1f}px; width: {mw + 8:.1f}px; height: {mh + 4:.1f}px"></span>')
            self.tweens.append(f'tl.fromTo("#{sid}m{i}", {{scaleX: 0}}, {{scaleX: 1, duration: 0.4, ease: "power2.out"}}, {round(t, 3)});')
        self.clips.append(f'<div id="{sid}" class="clip artc{" full" if full else " phone" if phone else ""}" data-start="{a}" data-duration="{round(b - a, 3)}" '
                          f'data-track-index="1" style="left: {cl}px; top: {ct}px; width: {cw}px; height: {ch}px">'
                          f'<div class="art-in" id="{sid}i" style="width: {W * k:.1f}px; height: {H * k:.1f}px">'
                          f'<img src="{path}" alt="" />{"".join(marks)}</div></div>')
        self.tweens.append(f'tl.fromTo("#{sid}i", {{{pose(cy0, s0)}}}, {{{pose(cy1, s1)}, duration: {round(b - a, 3)}, ease: "sine.inOut"}}, {a});')
        self._label(spec.get("label"), a, b - a, (self.H - 168 if full else ct - 52) if self.H > self.W else ct + ch + 26,
                    left=cl if spec.get("box") else None)

    def shots(self, specs, a, b, cuts=None):
        """Split a..b across specs; cuts = explicit film times between them (len(specs)-1)."""
        if not specs:
            return
        if cuts is None:
            step = (b - a) / len(specs)
            cuts = [a + step * i for i in range(1, len(specs))]
        edges = [a, *cuts, b]
        for spec, s, e in zip(specs, edges, edges[1:]):
            self.shot(spec, s, e)

    # ---------- voice ----------
    def wt(self, vid, i):
        return round(self.vo_times[vid] + self.words[vid][i][1], 3)

    def _audio(self, vid, src, start, vol, words):
        media = duration(MEDIA / src)
        dur = round(min(media, max(w[2] for w in words) + 0.45), 3)
        self.vtrack = getattr(self, "vtrack", 0) + 1  # voices alternate between two tracks of their own
        self.clips.append(f'<audio id="{self._id("vo")}" class="clip" src="{self.asset(src)}" data-start="{round(start, 3)}" '
                          f'data-duration="{dur}" data-track-index="{4 + self.vtrack % 2}" data-volume="{vol}"></audio>')
        self.srt.append((start, words))

    def vo(self, vid, shots=(), gap=0.6, caps=None, kw=(), cuts=None, lead=0.0, vol=1.6, low=False):
        """Narrator line at the cursor. shots fill [line start - lead, next cursor]. caps: v1 caption groups (every word).
        kw: [(word index, text, style[, until word index])] key lines, held to the end of the line or to `until`;
        with caps_all the spoken words outside the key lines are captioned. low: 9:16 captions under the picture (True) or a class such as "lower"."""
        words = self.words[vid]
        start = self.t
        self.vo_times[vid] = start
        self._audio(vid, f"voice/{vid}.mp3", start, vol, words)
        end_speech = start + words[-1][2]
        nxt = end_speech + gap
        if cuts is not None:
            cuts = [self.wt(vid, c) - 0.05 if isinstance(c, int) else c for c in cuts]
        # artifact marks given as word indices land on that word
        shots = [dict(s, marks=[(r, self.wt(vid, t) if isinstance(t, int) else t) for r, t in s.get("marks", [])])
                 if isinstance(s, dict) and "art" in s else s for s in shots]
        self.shots(list(shots), start - lead, nxt, cuts)
        if caps is None and self.caps_all:
            caps = "auto:" + self.hero.get(vid, "")
        line_tail = min(0.4, max(0.06, gap - 0.04))  # the last words clear before the next line can start
        if caps and not kw:
            self.captions(vid, start, words, caps, low if isinstance(low, str) else "low" if low else "", tail=line_tail)
        # key lines take over the screen; the spoken words around them are captioned
        spans = sorted((k[0], k[3] if len(k) > 3 else len(words)) for k in kw)
        free, k0 = [], 0
        for a, b in spans:
            free.append((k0, a))
            k0 = b
        free.append((k0, len(words)))
        if caps and kw:
            for a, b in free:
                if b <= a:
                    continue
                tail = line_tail if b == len(words) else max(0.02, words[b][1] - 0.06 - words[b - 1][2])
                self.captions(vid, start, words[a:b], caps if isinstance(caps, str) else None, low if isinstance(low, str) else "low" if low else "", tail=tail)
        for k in kw:
            wi, text, style = k[:3]
            g0 = start + words[wi][1] - 0.03
            g1 = start + words[k[3]][1] - 0.08 if len(k) > 3 else nxt - 0.15
            self.key(text, g0, g1, style)
            if self.caps_all:  # a quiet pop under the text, not a whoosh on every line
                self.sfx("lock.wav", g0, 0.14)
        self.t = nxt
        return start

    def quote(self, vid, name, caps, gap=0.5, inserts=(), vol=2.2, attrib=True, low=False):  # interview clips usually sit ~2 dB under the narration
        """Quote clip: the speaker's picture and voice, every word captioned. inserts: [(word index, spec, until word index|None)]."""
        src = f"footage/{vid}.mp4"
        if vid not in self.words or not (MEDIA / src).exists():
            print(f"  !! MISSING founder clip {vid}: skipped")
            return None
        words = self.words[vid]
        start = self.t - words[0][1] + 0.12  # first word lands 0.12 s after the cursor
        start = max(start, self.t - 0.4)
        self.vo_times[vid] = start
        end = start + words[-1][2] + 0.25
        # speech pictures are never slowed (lips stay on the voice): past the clip's last frame the gap holds on black
        ms = 0 if start >= self.t else round(self.t - start, 3)
        clip_end = min(end + gap, start + duration(MEDIA / src) - 0.02)
        band = self.H > self.W  # 9:16: founders sit in a full-width 16:9 band, never blown up to fill the frame
        if band:
            self.shot("black", self.t, end + gap)
        self.shot((src, ms), self.t, clip_end, band)
        self.shot("black", clip_end, end + gap)
        if low == "full":  # full-frame founder clip: a shade under the low captions so they read on a bright set
            self.clips.append(f'<div id="{self._id("qg")}" class="clip qgrad" data-start="{round(self.t, 3)}" '
                              f'data-duration="{round(end + gap - self.t, 3)}" data-track-index="8"></div>')
        for wi, spec, until in inserts:
            a = self.wt(vid, wi) - 0.05
            b = self.wt(vid, until) - 0.05 if until is not None else end + gap
            self.shot(spec, a, b, band)
        self._audio(vid, src, start, vol, words)
        self.captions(vid, start, words, caps, "low" if band or low else "", tail=min(0.4, max(0.06, gap - 0.04)))
        if attrib:
            aid = self._id("at")
            self.clips.append(f'<div id="{aid}" class="clip attrib{" tl" if low == "full" else " top" if low and self.W > self.H else ""}" data-start="{round(self.t + 0.2, 3)}" '
                              f'data-duration="{round(end - self.t, 3)}" data-track-index="10"><span class="bar"></span>{html.escape(name)}</div>')
            self.tweens.append(f'tl.fromTo("#{aid}", {{opacity: 0, x: -12}}, {{opacity: 1, x: 0, duration: 0.4, ease: "power2.out"}}, {round(self.t + 0.2, 3)});')
        self.t = end + gap
        return start

    def line_captions(self, start, words, hero, tail, extra=""):
        """Long-form captions: a phrase of up to ~38 characters shows dimmed, each word lights as it is spoken,
        emphasis words in the brand blue."""
        lines, cur = [], []
        for i, w in enumerate(words):
            if cur and len(" ".join(x[0] for x in cur + [w])) > 38:
                lines.append(cur)
                cur = []
            cur.append(w)
            if w[0].endswith((".", "?", "!")) or (w[0].endswith((",", ":")) and len(" ".join(x[0] for x in cur)) > 16):
                lines.append(cur)
                cur = []
        if cur:
            lines.append(cur)
        for li, ws in enumerate(lines):
            g0 = round(start + ws[0][1] - 0.06, 3)
            g1 = start + lines[li + 1][0][1] - 0.06 if li + 1 < len(lines) else start + ws[-1][2] + tail
            gid = self._id("g")
            inner = []
            for wi, w in enumerate(ws):
                hl = " hlw" if _norm(w[0]) in hero else ""
                inner.append(f'<span class="cw{hl}" id="{gid}-{wi}">{html.escape(w[0])}</span>')
                self.tweens.append(f'tl.to("#{gid}-{wi}", {{opacity: 1, duration: 0.12, ease: "power2.out"}}, {round(start + w[1], 3)});')
            self.tweens.append(f'tl.set("#{gid} .cw", {{opacity: 0.4}}, {g0});')
            self.clips.append(f'<div id="{gid}" class="clip cap st-L {extra}" data-start="{g0}" data-duration="{round(g1 - g0, 3)}" '
                              f'data-track-index="8"><span class="ln">{" ".join(inner)}</span></div>')

    def captions(self, vid, start, words, groups, extra="", tail=0.4):
        if self.cap_mode == "line" and (isinstance(groups, str) or groups is None):
            return self.line_captions(start, words, set(_norm(x) for x in (groups or "").partition(":")[2].split(",") if x), tail, extra)
        if isinstance(groups, str) or groups is None:  # "auto" / "auto:<word>,<word>" → 1–3 word groups, named words as emphasis
            hero = set(_norm(x) for x in (groups or "").partition(":")[2].split(",") if x)
            groups, run = [], 0
            for i, w in enumerate(words):
                if _norm(w[0]) in hero:
                    if run:
                        groups.append((run, "r"))
                    groups.append((1, "E"))
                    run = 0
                    continue
                run += 1
                if run == 3 or w[0].endswith((",", ".", "?")) or i == len(words) - 1:
                    groups.append((run, "r"))
                    run = 0
        assert sum(g[0] for g in groups) == len(words), (vid, len(words), [w[0] for w in words])
        k = 0
        for cnt, style in groups:
            ws = words[k:k + cnt]
            k += cnt
            g0 = round(start + ws[0][1] - 0.03, 3)
            g1 = words[k][1] + start - 0.03 if k < len(words) else start + ws[-1][2] + tail
            gid = self._id("g")
            inner = []
            for wi, w in enumerate(ws):
                t = round(start + w[1], 3)
                inner.append(f'<span class="cw" id="{gid}-{wi}">{html.escape(self.clean(w[0], style, wi == 0))}</span>')
                self.tweens.append(f'tl.to("#{gid}-{wi}", {{opacity: 1, duration: 0.07, ease: "power2.out"}}, {t});')
            body = " ".join(inner)
            if style == "S":
                body = f'<span class="hl">{body}</span>'
                self.tweens.append(f'tl.fromTo("#{gid} .hl", {{clipPath: "inset(0 100% 0 0)"}}, {{clipPath: "inset(0 0% 0 0)", duration: 0.16, ease: "power2.out"}}, {g0 + 0.02});')
            self.clips.append(f'<div id="{gid}" class="clip cap st-{style} {extra}" data-start="{g0}" data-duration="{round(g1 - g0, 3)}" data-track-index="8">{body}</div>')

    @staticmethod
    def clean(word, style, first):
        w = word
        if style in "EHSPK":
            w = w.rstrip(",")
        if first and style in "aEK" and w[:1].islower():
            w = w[0].upper() + w[1:]
        if style == "a" and w.endswith(","):
            w = w[:-1] + "."
        return w

    def key(self, text, a, b, style="K", instant=False):
        """A held on-screen line (film key words). *word* marks the blue highlight, | a line break.
        instant: already on screen at its first frame (a reel's frame-one hook)."""
        kid = self._id("kw")
        parts = re.split(r"\*(.+?)\*", html.escape(text))
        body = "".join(f'<span class="hlw">{p}</span>' if i % 2 else p for i, p in enumerate(parts)).replace("|", "<br />")
        self.clips.append(f'<div id="{kid}" class="clip cap st-{style}" data-start="{round(a, 3)}" data-duration="{round(b - a, 3)}" data-track-index="9"><span class="kl">{body}</span></div>')
        if not instant:
            self.tweens.append(f'tl.fromTo("#{kid} .kl", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.45, ease: "power3.out"}}, {round(a, 3)});')

    def number(self, a, b, value, prefix="$", sub=""):
        """A big number that counts up from 0 (money beats), centred, with a small caption under it."""
        nid = self._id("nm")
        subl = f'<div class="nm-s">{html.escape(sub)}</div>' if sub else ""
        self.clips.append(f'<div id="{nid}" class="clip numcard" data-start="{round(a, 3)}" data-duration="{round(b - a, 3)}" data-track-index="9">'
                          f'<div class="nm-v">{prefix}0</div>{subl}</div>')
        self.tweens.append(f'(function () {{ const o = {{v: 0}}, el = document.querySelector("#{nid} .nm-v"); '
                           f'tl.to(o, {{v: {value}, duration: {round(min(1.6, (b - a) * 0.5), 2)}, ease: "power2.out", '
                           f'onUpdate: () => {{ el.textContent = "{prefix}" + Math.round(o.v).toLocaleString("en-US"); }}}}, {round(a + 0.1, 3)}); }})();')
        self.tweens.append(f'tl.fromTo("#{nid}", {{opacity: 0}}, {{opacity: 1, duration: 0.35}}, {round(a, 3)});')

    def qcard(self, text, attrib, a, b):
        """A real quote as on-screen text over the picture (no voice), with its source."""
        qid = self._id("qc")
        self.clips.append(f'<div id="{qid}" class="clip qcard" data-start="{round(a, 3)}" data-duration="{round(b - a, 3)}" data-track-index="9">'
                          f'<div class="q-t">\u201c{html.escape(text)}\u201d</div><div class="q-a"><span class="bar"></span>{html.escape(attrib)}</div></div>')
        self.tweens.append(f'tl.fromTo("#{qid} .q-t", {{opacity: 0, y: 16}}, {{opacity: 1, y: 0, duration: 0.6, ease: "power3.out"}}, {round(a + 0.1, 3)});')
        self.tweens.append(f'tl.fromTo("#{qid} .q-a", {{opacity: 0}}, {{opacity: 1, duration: 0.4}}, {round(a + 0.7, 3)});')

    def grid(self, a, b, beats):
        """The four-quadrant product grid drawn on screen. beats: {"cols": t, "c1": t, "c2": t, "rows": t, "r1": t, "r2": t, "four": t}."""
        gid = self._id("gr")
        cell = '<div class="gc"><span>{}</span></div>'
        self.clips.append(f'<div id="{gid}" class="clip gridcard" data-start="{round(a, 3)}" data-duration="{round(b - a, 3)}" data-track-index="9">'
                          f'<div class="g-box"><span class="gl gv"></span><span class="gl gh"></span>'
                          f'<div class="g-c c1">Consumer</div><div class="g-c c2">Pro</div><div class="g-r r1">Desktop</div><div class="g-r r2">Portable</div>'
                          f'{"".join(cell.format(x) for x in ("iMac", "Power Mac", "iBook", "PowerBook"))}</div></div>')
        T = self.tweens.append
        T(f'tl.fromTo("#{gid} .gv", {{scaleY: 0}}, {{scaleY: 1, duration: 0.6, ease: "power2.inOut"}}, {round(beats["cols"], 3)});')
        T(f'tl.fromTo("#{gid} .c1", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {round(beats["c1"], 3)});')
        T(f'tl.fromTo("#{gid} .c2", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {round(beats["c2"], 3)});')
        T(f'tl.fromTo("#{gid} .gh", {{scaleX: 0}}, {{scaleX: 1, duration: 0.6, ease: "power2.inOut"}}, {round(beats["rows"], 3)});')
        T(f'tl.fromTo("#{gid} .r1", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {round(beats["r1"], 3)});')
        T(f'tl.fromTo("#{gid} .r2", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {round(beats["r2"], 3)});')
        T(f'tl.fromTo("#{gid} .gc", {{opacity: 0, scale: 0.9}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(1.6)", stagger: 0.18}}, {round(beats["four"], 3)});')
        T(f'tl.fromTo("#{gid}", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {round(a, 3)});')

    def choice(self, a, b, left, right, t_left, t_right, t_pick):
        """Two options side by side; the left one fades out at t_pick (Be vs NeXT)."""
        cid = self._id("cc")
        self.clips.append(f'<div id="{cid}" class="clip choicecard" data-start="{round(a, 3)}" data-duration="{round(b - a, 3)}" data-track-index="9">'
                          f'<div class="ch-o o1">{html.escape(left)}</div><div class="ch-or">or</div><div class="ch-o o2">{html.escape(right)}</div></div>')
        self.tweens.append(f'tl.fromTo("#{cid} .o1", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.4}}, {round(t_left, 3)});')
        self.tweens.append(f'tl.fromTo("#{cid} .o2, #{cid} .ch-or", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.4}}, {round(t_right, 3)});')
        self.tweens.append(f'tl.to("#{cid} .o1", {{opacity: 0.18, duration: 0.5}}, {round(t_pick, 3)});')
        self.tweens.append(f'tl.to("#{cid} .o2", {{color: "#6fb5fc", duration: 0.4}}, {round(t_pick, 3)});')
        self.tweens.append(f'tl.fromTo("#{cid}", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {round(a, 3)});')

    def bars(self, a, b, data, title, t_bars, unit="$M"):
        """A bar chart that grows on cue: data = [(label, value)], negative bars hang below the zero line."""
        gid = self._id("bc")
        top = max(abs(v) for _, v in data)
        cols = []
        for i, (lab, v) in enumerate(data):
            h = round(abs(v) / top * 300)
            cls = "neg" if v < 0 else "pos"
            val = f"{'−' if v < 0 else ''}{abs(v):,}"
            cols.append(f'<div class="bcol"><div class="bar {cls}" style="height: {h}px"><span>{val}</span></div><div class="bl">{html.escape(lab)}</div></div>')
        self.clips.append(f'<div id="{gid}" class="clip barcard" data-start="{round(a, 3)}" data-duration="{round(b - a, 3)}" data-track-index="9">'
                          f'<div class="b-t">{html.escape(title)}<small>{html.escape(unit)}</small></div><div class="b-box"><span class="zero"></span>{"".join(cols)}</div></div>')
        self.tweens.append(f'tl.fromTo("#{gid}", {{opacity: 0}}, {{opacity: 1, duration: 0.35}}, {round(a, 3)});')
        for i, t in enumerate(t_bars):
            self.tweens.append(f'tl.fromTo("#{gid} .bcol:nth-child({i + 2}) .bar", {{scaleY: 0}}, {{scaleY: 1, duration: 0.5, ease: "power3.out"}}, {round(t, 3)});')
            self.tweens.append(f'tl.fromTo("#{gid} .bcol:nth-child({i + 2}) .bar span, #{gid} .bcol:nth-child({i + 2}) .bl", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {round(t + 0.25, 3)});')

    def timeline(self, a, b, years, span, label, t_span):
        """A 1976–2001 line with year ticks; the span (y0, y1) fills in blue at t_span with its label."""
        tid = self._id("tl")
        y_lo, y_hi = years[0], years[-1]
        x = lambda y: round((y - y_lo) / (y_hi - y_lo) * 100, 2)
        ticks = "".join(f'<span class="tk" style="left: {x(y)}%"><b>{y}</b></span>' for y in years)
        s0, s1 = span
        self.clips.append(f'<div id="{tid}" class="clip tlcard" data-start="{round(a, 3)}" data-duration="{round(b - a, 3)}" data-track-index="9">'
                          f'<div class="t-line">{ticks}<span class="t-span" style="left: {x(s0)}%; width: {x(s1) - x(s0)}%"></span>'
                          f'<span class="t-lab" style="left: {(x(s0) + x(s1)) / 2}%">{html.escape(label)}</span></div></div>')
        self.tweens.append(f'tl.fromTo("#{tid}", {{opacity: 0}}, {{opacity: 1, duration: 0.4}}, {round(a, 3)});')
        self.tweens.append(f'tl.fromTo("#{tid} .tk", {{opacity: 0, y: 10}}, {{opacity: 1, y: 0, duration: 0.3, stagger: 0.08}}, {round(a + 0.2, 3)});')
        self.tweens.append(f'tl.fromTo("#{tid} .t-span", {{scaleX: 0}}, {{scaleX: 1, duration: 1.2, ease: "power2.inOut"}}, {round(t_span, 3)});')
        self.tweens.append(f'tl.fromTo("#{tid} .t-lab", {{opacity: 0, y: -10}}, {{opacity: 1, y: 0, duration: 0.4}}, {round(t_span + 0.9, 3)});')

    def mark(self, text, a, b):
        """Small site mark, bottom left (the Short's loop has no end card)."""
        mid = self._id("hm")
        self.clips.append(f'<div id="{mid}" class="clip hmark" data-start="{round(a, 3)}" data-duration="{round(b - a, 3)}" data-track-index="12">{html.escape(text)}</div>')
        self.tweens.append(f'tl.fromTo("#{mid}", {{opacity: 0}}, {{opacity: 1, duration: 0.5}}, {round(a, 3)});')

    # ---------- structure ----------
    def pause(self, s, shots=()):
        self.shots(list(shots), self.t, self.t + s)
        self.t += s

    def chapter(self, counter, title, dur=3.6, sfx=True):
        """Chapter card on black: small counter, big title."""
        a = self.t
        cid = self._id("ch")
        ctr = f'<div class="ch-n">{html.escape(counter)}</div>' if counter else ""
        prog = ""
        m = re.fullmatch(r"(\d+)/(\d+)", counter or "")
        if m and self.caps_all:  # film: where we are in the five, and how many are left
            k, n = int(m[1]), int(m[2])
            prog = '<div class="prog">' + "".join(f'<span class="{"on" if i < k else ""}"></span>' for i in range(n)) + "</div>"
            self.tweens.append(f'tl.fromTo("#{cid} .prog span:nth-child({k})", {{scaleX: 0}}, '
                               f'{{scaleX: 1, duration: 0.5, ease: "power3.out"}}, {round(a + 0.55, 3)});')
        self.clips.append(f'<div id="{cid}" class="clip chapter" data-start="{round(a, 3)}" data-duration="{dur}" data-track-index="3">'
                          f'{ctr}<div class="ch-t">{html.escape(title)}</div>{prog}</div>')
        self.tweens.append(f'tl.fromTo("#{cid} .ch-n", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {round(a + 0.15, 3)});')
        self.tweens.append(f'tl.fromTo("#{cid} .ch-t", {{opacity: 0, y: 18}}, {{opacity: 1, y: 0, duration: 0.6, ease: "power3.out"}}, {round(a + 0.3, 3)});')
        self.tweens.append(f'tl.to("#{cid} > div", {{opacity: 0, duration: 0.35}}, {round(a + dur - 0.4, 3)});')
        if sfx:
            self.sfx("tick.wav", a + 0.3, 0.4)
        self.t += dur
        return a

    def stamp(self, text, a, b):
        """Date / place stamp, top left (documentary history beats)."""
        sid = self._id("st")
        self.clips.append(f'<div id="{sid}" class="clip stamp" data-start="{round(a, 3)}" data-duration="{round(b - a, 3)}" '
                          f'data-track-index="11"><span class="bar"></span>{html.escape(text)}</div>')
        self.tweens.append(f'tl.fromTo("#{sid}", {{opacity: 0, x: -10}}, {{opacity: 1, x: 0, duration: 0.45, ease: "power2.out"}}, {round(a, 3)});')
        self.tweens.append(f'tl.to("#{sid}", {{opacity: 0, duration: 0.3}}, {round(b - 0.3, 3)});')
        self.sfx("tick.wav", a + 0.05, 0.22)

    def checklist(self, title, rows, dur):
        """A save-worthy recap card: small title, numbered rows revealed one after another."""
        a = round(self.t, 3)
        cid = self._id("cl")
        body = "".join(f'<div class="row"><b>{i}</b><span>{html.escape(r)}</span></div>' for i, r in enumerate(rows, 1))
        self.clips.append(f'<div id="{cid}" class="clip checklist" data-start="{a}" data-duration="{dur}" data-track-index="3">'
                          f'<div class="ct">{html.escape(title)}</div>{body}</div>')
        self.tweens.append(f'tl.fromTo("#{cid} .row", {{opacity: 0, x: -16}}, {{opacity: 1, x: 0, duration: 0.3, ease: "power3.out", stagger: 0.16}}, {a + 0.1});')
        self.sfx("tick.wav", a + 0.1, 0.3)
        self.t += dur

    def counter(self, text, a, b):
        cid = self._id("ct")
        self.clips.append(f'<div id="{cid}" class="clip counter" data-start="{round(a, 3)}" data-duration="{round(b - a, 3)}" data-track-index="12">{html.escape(text)}</div>')
        self.tweens.append(f'tl.fromTo("#{cid}", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {round(a, 3)});')

    def sfx(self, f, t, v):
        self.ftrack = getattr(self, "ftrack", 0) + 1
        self.clips.append(f'<audio id="{self._id("fx")}" class="clip" src="{self.asset("sfx/" + f)}" data-start="{round(t, 3)}" '
                          f'data-duration="{SFX_LEN[f]}" data-track-index="{6 + self.ftrack % 2}" data-volume="{v}"></audio>')

    def music(self, track, a, b, media_start, vol, fade_in=0.0, fade_out=0.0, lane=0):
        d = round(b - a, 3)
        assert media_start + d <= duration(MEDIA / f"bgm/{track}") + 0.01, (track, media_start, d)
        fi = f' data-fade-in="{fade_in}"' if fade_in else ""
        fo = f' data-fade-out="{fade_out}"' if fade_out else ""
        self.clips.append(f'<audio id="{self._id("bgm")}" class="clip" src="{self.asset("bgm/" + track)}" data-start="{round(a, 3)}" '
                          f'data-duration="{d}" data-media-start="{media_start}" data-track-index="{14 + lane}" data-volume="{vol}"{fi}{fo}></audio>')

    def endcard(self, dur, sub=""):
        a = round(self.t, 3)
        subline = f'<div id="end-sub">{html.escape(sub)}</div>' if sub else ""
        self.clips.append(f'''<div id="endcard" class="clip" data-start="{a}" data-duration="{dur}" data-track-index="13">
      <div id="end-wordmark"><span id="end-mark"><span class="rail"></span><span class="rail r2"></span><span class="bridge"></span>
      <span class="node n1"></span><span class="node n2"></span><span class="node n3"></span><span class="node n4"></span><span class="node n5"></span><span class="node n6"></span></span><span id="end-ackyard">{html.escape(self.brand[1:] if self.brand.startswith("H") else self.brand)}</span></div>{subline}
    </div>''')
        self.tweens.append(f'tl.fromTo("#end-mark .node", {{opacity: 0, y: -14}}, {{opacity: 1, y: 0, duration: 0.3, ease: "expo.out", stagger: 0.035}}, {a + 0.15});')
        self.tweens.append(f'tl.fromTo(["#end-mark .rail", "#end-mark .bridge"], {{opacity: 0}}, {{opacity: 1, duration: 0.2}}, {a + 0.35});')
        self.tweens.append(f'tl.fromTo("#end-ackyard", {{clipPath: "inset(0 100% 0 0)"}}, {{clipPath: "inset(0 0% 0 0)", duration: 0.45, ease: "power3.out"}}, {a + 0.4});')
        if sub:
            self.tweens.append(f'tl.fromTo("#end-sub", {{opacity: 0}}, {{opacity: 1, duration: 0.5}}, {a + 0.9});')
        self.sfx("impact-low.wav", a, 0.35)
        self.t += dur

    # ---------- output ----------
    def write(self, title, vertical=False):
        page = (HERE / "template.html").read_text()
        page = page.replace("{{CLIPS}}", "\n      ".join(self.clips)).replace("/*TWEENS*/", "\n        ".join(self.tweens))
        page = (page.replace("{{DURATION}}", str(round(self.t, 3))).replace("{{W}}", str(self.W)).replace("{{H}}", str(self.H))
                .replace("{{TITLE}}", title).replace("{{ORIENT}}", "vert" if vertical else "land"))
        (self.root / "index.html").write_text(page)
        # drop assets no longer used
        for p in (self.root / "assets").rglob("*"):
            rel = p.relative_to(self.root / "assets").as_posix()
            if p.is_file() and not rel.startswith(("fonts/", "lib/")) and rel not in self.used:
                p.unlink()
        print(f"{self.root.name}/index.html: {len(self.clips)} clips, {len(self.tweens)} tweens, {self.t:.2f}s")

    def write_srt(self, path):
        cues = []
        for start, words in sorted(self.srt, key=lambda x: x[0]):
            line, t0 = [], None
            for i, w in enumerate(words):
                if t0 is None:
                    t0 = start + w[1]
                line.append(w[0])
                text = " ".join(line)
                last = i == len(words) - 1
                if last or len(text) > 34 or w[0].endswith((".", "?")):
                    cues.append((t0, start + w[2] + 0.2, text))
                    line, t0 = [], None

        def ts(x):
            ms = int(round(x * 1000))
            return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"
        out = []
        for i, (a, b, text) in enumerate(cues, 1):
            b = min(b, cues[i][0] - 0.02) if i < len(cues) else b
            out.append(f"{i}\n{ts(a)} --> {ts(b)}\n{text}\n")
        pathlib.Path(path).write_text("\n".join(out))
