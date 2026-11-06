# Film folder

Created by `scripts/new-film.sh <slug>`. Work top to bottom; each step has a skill in `skills/`.

| Path | What goes in it | Made by |
| --- | --- | --- |
| `RESEARCH.md` | Every fact with its source link, and every quote with its timestamp | you (skill: source-cut-research) |
| `SCRIPT.md` | The narration, line by line, with the picture for each line | you (skill: source-cut-script) |
| `voice/lines.tsv`, `voice/pron.json` | Narration lines for the voice, pronunciation fixes | you |
| `media/voice/` | `<id>.mp3` per line + `words.jsonl` | `tools/voice/azure_tts.py`, `azure_stt.py` |
| `media/images/commons.json` → `media/images/` | Photos + `CREDITS.md` | `tools/sources/commons_fetch.py` |
| `edit/pages.py` → `media/artifacts/` | Document captures + `rects.json` | `tools/sources/pages.py` |
| `media/raw/` → `edit/quotes.json` → `media/footage/` | Quote clips and bands + `words.jsonl` | `yt_sections.sh`, `clip_words.sh`, `qcut.py` |
| `media/bgm/` | Music you have the rights to | you |
| `film/build.py`, `short/build.py` | The 16:9 film and the 9:16 Short | the engine (skill: source-cut-edit) |
| `thumbnail/gpt.json` | Thumbnail A/B/C | `tools/thumbnails/gpt_thumbs.py` |
| `UPLOAD.md` | Titles, description, chapters, sources, credits, tags | you (skill: source-cut-upload) |

Nothing in `media/`, `renders/` or `assets/` is committed: the licences belong to their owners.
