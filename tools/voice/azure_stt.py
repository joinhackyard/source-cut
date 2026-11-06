#!/usr/bin/env python3
"""Word timings for every audio file in a folder, with Azure AI Speech fast transcription.

  python3 tools/voice/azure_stt.py <audio dir> <out.jsonl> [--small]

Writes one JSON line per file: {"file": "w0a.mp3", "status": 200, "words": [[text, start_s, end_s], ...]}.
The edit engine reads media/voice/words.jsonl (narration) and media/footage/words.jsonl (quote clips) to time captions,
marker sweeps and cuts to the spoken word.

--small re-encodes to 16 kHz mono 32 kbps first (much faster on a slow uplink; timings are unchanged).
Run one transcription job at a time: parallel jobs got throttled and returned empty word lists.
"""
import json
import pathlib
import subprocess
import sys
import tempfile
import urllib.request
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "lib"))
from env import need  # noqa: E402

env = need("SPEECH_KEY", "SPEECH_REGION")
src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
small = "--small" in sys.argv
url = (f"https://{env['SPEECH_REGION']}.api.cognitive.microsoft.com/speechtotext/transcriptions:transcribe"
       "?api-version=2024-11-15")
definition = json.dumps({"locales": ["en-US"], "profanityFilterMode": "None"})
files = sorted(p for p in src.iterdir() if p.suffix in (".mp3", ".wav", ".m4a", ".mp4"))
tmp = pathlib.Path(tempfile.mkdtemp())
rows = []
for p in files:
    send = p
    if small or p.suffix == ".mp4":
        send = tmp / (p.stem + ".mp3")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "4", "-i", str(p), "-vn", "-ac", "1", "-ar", "16000",
                        "-b:a", "32k", str(send)], check=True)
    b = uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"definition\"\r\nContent-Type: application/json\r\n\r\n"
            f"{definition}\r\n--{b}\r\nContent-Disposition: form-data; name=\"audio\"; filename=\"{send.name}\"\r\n"
            f"Content-Type: audio/mpeg\r\n\r\n").encode() + send.read_bytes() + f"\r\n--{b}--\r\n".encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Ocp-Apim-Subscription-Key": env["SPEECH_KEY"], "Content-Type": f"multipart/form-data; boundary={b}"})
    words, status = [], 0
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            status = r.status
            for ph in json.load(r).get("phrases", []):
                for w in ph.get("words", []):
                    s = w["offsetMilliseconds"] / 1000
                    words.append([w["text"], round(s, 3), round(s + w["durationMilliseconds"] / 1000, 3)])
    except urllib.error.HTTPError as e:
        status = e.code
    name = p.stem + ".mp3"  # the engine keys rows by <id>.mp3, for narration and clips alike
    rows.append(json.dumps({"file": name, "status": status, "words": words}))
    print(name, status, " ".join(w[0] for w in words)[:110])
out.write_text("\n".join(rows) + "\n")
