#!/usr/bin/env python3
"""Narration with Azure AI Speech, one mp3 per script line.

  python3 tools/voice/azure_tts.py <film>/voice/lines.tsv <film>/media/voice [id ...]

lines.tsv: one line per narration file, "id<TAB>text" (lines starting with # are skipped). Pass ids to voice only
those lines (re-voicing after a script fix). Pronunciation fixes live next to it in pron.json:
  {"Neumann": "<phoneme alphabet=\"ipa\" ph=\"ˈnɔɪmən\">Neumann</phoneme>", "SPAC": "<sub alias=\"spack\">SPAC</sub>"}
Find the words the voice gets wrong by transcribing the result (azure_stt.py) and reading the words back.

Settings (.env): SPEECH_KEY, SPEECH_REGION, SPEECH_VOICE (default en-US-Andrew:DragonHDLatestNeural, an HD voice with an
international, neutral read). Spell numbers the way they should be said ("forty-seven point two billion dollars").
"""
import html
import json
import pathlib
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "lib"))
from env import need  # noqa: E402

env = need("SPEECH_KEY", "SPEECH_REGION")
voice = env.get("SPEECH_VOICE", "en-US-Andrew:DragonHDLatestNeural")
src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
only = set(sys.argv[3:])
out.mkdir(parents=True, exist_ok=True)
pron_f = src.with_name("pron.json")
PRON = json.loads(pron_f.read_text()) if pron_f.exists() else {}
lines = [l.split("\t", 1) for l in src.read_text().splitlines() if l.strip() and not l.startswith("#")]
for lid, text in lines:
    if only and lid not in only:
        continue
    body = html.escape(text.strip())
    for k, v in PRON.items():  # applied after escaping, so the SSML tags survive
        body = body.replace(k, v)
    ssml = ('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">'
            f'<voice name="{voice}">{body}</voice></speak>')
    req = urllib.request.Request(
        f"https://{env['SPEECH_REGION']}.tts.speech.microsoft.com/cognitiveservices/v1", data=ssml.encode(), method="POST",
        headers={"Ocp-Apim-Subscription-Key": env["SPEECH_KEY"], "Content-Type": "application/ssml+xml",
                 "X-Microsoft-OutputFormat": "audio-48khz-192kbitrate-mono-mp3", "User-Agent": "source-cut"})
    with urllib.request.urlopen(req, timeout=90) as r:
        (out / f"{lid}.mp3").write_bytes(r.read())
    print(lid, "ok", len(text.split()), "words")
print(len(lines), "lines,", sum(len(t.split()) for _, t in lines), "words in the script")
