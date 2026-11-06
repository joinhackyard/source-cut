---
name: source-cut-voice
description: Voice a Source Cut script with Azure AI Speech, fix pronunciations, and get word timings for captions and marker sweeps (tools/voice). Use after the script is locked, or to re-voice changed lines.
---

# Voice and word timings

```bash
python3 tools/voice/azure_tts.py films/<slug>/voice/lines.tsv films/<slug>/media/voice
python3 tools/voice/azure_stt.py films/<slug>/media/voice films/<slug>/media/voice/words.jsonl --small
```

- Voice: `SPEECH_VOICE` (default `en-US-Andrew:DragonHDLatestNeural`): an international, calm documentary read.
- Run **one** transcription job at a time. Parallel jobs were throttled and came back with empty word lists.

## Pronunciation loop

1. Read the transcript back (`azure_stt.py` prints each line). A name the transcriber spells wrong is often a name the
   voice says wrong: listen to that line.
2. Add a fix to `voice/pron.json`: IPA (`<phoneme alphabet="ipa" ph="ˈnɔɪmən">Neumann</phoneme>`) or an alias
   (`<sub alias="spack">SPAC</sub>`).
3. Re-voice just those lines: `tools/voice/revoice.sh films/<slug> w1b w3a`. It merges the new timings into
   `words.jsonl`.

## How timings are used

The engine aligns the script's words to the transcriber's words, so captions always show the script (for example
"forty-seven" stays a word in the caption even if the transcriber wrote "$47"). Spelled-out numbers are spread over the
whole spoken span so the marker and caption land while the number is said.

## Checks

- Every id in `lines.tsv` has an mp3 and a row in `words.jsonl` with words.
- Total length is close to the plan (about 150 words a minute).
