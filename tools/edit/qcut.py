#!/usr/bin/env python3
"""qcut.py <spec.json>: cut quote clips (with sound) and muted b-roll bands from downloaded sections, one ffmpeg at a time.

Workflow: download the sections (tools/sources/yt_sections.sh), transcribe them (tools/edit/clip_words.sh), find each
quote's first and last word with qspec.span(), then list the quotes and bands in spec.json and run this.
Everything is scaled and padded to 1280x720 at 25 fps so the edit engine treats every clip the same way.
spec: {"raw": dir, "out": footage dir, "words": raw words.jsonl,
       "quotes": [[name, raw_stem, t_first_word, t_last_word_end]], "bands": [[name, raw_stem, start, dur]]}
Quotes start 0.15 s before the first word (the engine wants >= 0.12 s of lead-in) and end 0.4 s after the last word;
their words are written, shifted, to <out>/words.jsonl (replacing any old rows of the same name)."""
import json, subprocess, sys, pathlib
sp = json.load(open(sys.argv[1])); raw, out = pathlib.Path(sp["raw"]), pathlib.Path(sp["out"])
VF = "scale=1280:720:flags=lanczos:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=25,format=yuv420p,setsar=1"
W = {json.loads(l)["file"][:-4]: json.loads(l)["words"] for l in open(sp["words"]) if l.strip()}
dur = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout)
rows = {}
wf = out / "words.jsonl"
if wf.exists():
    for l in open(wf):
        if l.strip(): rows[json.loads(l)["file"][:-4]] = l.strip()
for name, stem, a, b in sp.get("quotes", []):
    src = raw / f"{stem}.mp4"; s = max(0.0, a - 0.15); e = min(dur(src), b + 0.4)
    ws = [[t, round(x - s, 2), round(y - s, 2)] for t, x, y in W[stem] if x >= a - 0.02 and y <= b + 0.02]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "4", "-ss", f"{s:.2f}", "-t", f"{e - s:.2f}", "-i", str(src), "-vf", VF,
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", str(out / f"{name}.mp4")], check=True)
    rows[name] = json.dumps({"file": name + ".mp3", "status": 200, "words": ws})
    print(name, f"{e - s:.2f}s", " ".join(w[0] for w in ws))
for name, stem, a, d in sp.get("bands", []):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "4", "-ss", str(a), "-t", str(d), "-i", str(raw / f"{stem}.mp4"), "-vf", VF, "-an",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", str(out / f"{name}.mp4")], check=True)
    print("band", name, d)
wf.write_text("\n".join(rows.values()) + "\n")
