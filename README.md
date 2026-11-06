# Source Cut

**Make documentaries where every frame has a source.**

Source Cut is the open-source workflow [Hackyard](https://hackyard.org) uses to make its business documentaries: real
archive footage, real photographs and real documents on screen, with a marker that sweeps across the exact words the
narrator is saying. No stock footage. No AI-generated people presented as real. A credit for every picture, and a
source for every claim.

It is a set of small tools, an edit engine, playbooks, and Claude Code skills that walk an agent (or you) through the
whole process: research, script, narration, document cards, quotes, the edit, review, rendering, thumbnails and the
upload package. The output is a 6–8 minute 16:9 film and a 50-second 9:16 Short.

## Films made with Source Cut

<table>
  <tr>
    <td width="33%" align="center">
      <a href="https://youtu.be/ZvAy5mSSb6E"><img src="https://img.youtube.com/vi/ZvAy5mSSb6E/maxresdefault.jpg" alt="How WhatsApp Served Hundreds of Millions With About 50 People" /></a><br />
      <b>How WhatsApp Served Hundreds of Millions With About 50 People</b>
    </td>
    <td width="33%" align="center">
      <a href="https://youtu.be/QUQrXtQRFPk"><img src="https://img.youtube.com/vi/QUQrXtQRFPk/maxresdefault.jpg" alt="They Built America's First Real Jet Fighter in 143 Days" /></a><br />
      <b>They Built America's First Real Jet Fighter in 143 Days</b>
    </td>
    <td width="33%" align="center">
      <a href="https://youtu.be/QEiXUMz7bR8"><img src="https://img.youtube.com/vi/QEiXUMz7bR8/maxresdefault.jpg" alt="Fired From His Own Company: The Steve Jobs Comeback" /></a><br />
      <b>Fired From His Own Company: The Steve Jobs Comeback</b>
    </td>
  </tr>
</table>

Watch them for the edit style: document cards with the marker on the spoken words, credited archive clips and photos,
chapter cards, and the three-lesson close. More on the [Hackyard YouTube channel](https://www.youtube.com/@Hackyard).

## What a Source Cut film looks like

- **Document cards.** When the narrator says "$47.2 billion in rent it had promised to pay", the S-1 is on screen and a
  blue marker sweeps those words as they are spoken.
- **Real voices.** The people in the story speak in short, credited clips from their own interviews and keynotes.
- **Credited photos.** Wikimedia Commons and archives with clear licences, with the author on screen.
- **A clear structure.** Cold open, five chapters, a re-hook, three lessons, a close.
- **Honest thumbnails.** Three variants (face, proof, contrast) tested against each other on watch time.

## How it works

| Layer                                 | What it is                                                                                                               |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| [`docs/`](docs)                       | [Principles](docs/principles.md) and the [end-to-end workflow](docs/workflow.md)                                         |
| [`skills/`](skills)                   | 12 Claude Code skills, one per step, plus the `source-cut` overview                                                      |
| [`playbooks/`](playbooks)             | The long-form craft notes: series format, production, thumbnails, reels, motion                                          |
| [`engine/`](engine)                   | The edit engine: Python that writes a [HyperFrames](https://www.npmjs.com/package/hyperframes) composition (HTML + GSAP) |
| [`tools/`](tools)                     | Voice, sources, quote cutting, QC contact sheets, rendering, loudness, thumbnails                                        |
| [`templates/film/`](templates/film)   | The folder every new film starts from                                                                                    |
| [`examples/wework/`](examples/wework) | A complete published film, ready to rebuild                                                                              |

```
research ─► script ─┬─► Azure narration + word timings ─┐
                    ├─► document cards (+ marker rects) ─┼─► edit ─► contact-sheet review ─► VM render ─► loudness ─► upload
                    └─► quote clips + bands ─────────────┘                                          thumbnails A/B/C ─┘
```

## Quick start

Requirements: Python 3.10+, ffmpeg, Node.js, `yt-dlp`, a Linux VM with Docker for rendering, an Azure AI Speech
resource, and (for thumbnails) an Azure OpenAI image deployment.

```bash
git clone https://github.com/joinhackyard/source-cut && cd source-cut
cp .env.example .env                 # fill in your VM, Azure Speech and Azure OpenAI settings
scripts/setup-assets.sh              # fonts (SIL OFL), GSAP, synthesised sound effects
# on the VM: build the runner image from tools/render/Dockerfile (see skills/source-cut-setup)
scripts/new-film.sh my-film          # films/my-film from the template
```

Then follow [docs/workflow.md](docs/workflow.md), or ask Claude Code to make the film.

## Use it with Claude Code

Install the skills as a plugin:

```
/plugin marketplace add joinhackyard/source-cut
/plugin install source-cut@source-cut
```

Then ask: _"Make a Source Cut documentary about how Airbnb survived by selling cereal."_ The `source-cut` skill runs the
pipeline step by step and asks for your approval before the expensive steps (the final render, publishing).

## The tools

| Step             | Tool                                                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------------------- |
| Narration        | `tools/voice/azure_tts.py` (lines + pronunciation fixes)                                                |
| Word timings     | `tools/voice/azure_stt.py`, `tools/voice/revoice.sh`                                                    |
| Photos + credits | `tools/sources/commons_fetch.py`                                                                        |
| Document cards   | `tools/sources/pages.py`, `tools/sources/capture_artifacts.mjs`                                         |
| Quote sections   | `tools/sources/yt_sections.sh`, `tools/edit/clip_words.sh`, `tools/edit/qspec.py`, `tools/edit/qcut.py` |
| Edit             | `engine/build_lib.py`, `engine/film_helpers.py`, `engine/template.html`                                 |
| Review           | `tools/qc/check.sh` (+ `shot_times.py`, `pullsheet.py`), `tools/qc/sheet.py`                            |
| Render           | `tools/render/vm.sh`, `tools/render/render-final.sh`, `tools/render/loudness.sh`                        |
| Thumbnails       | `tools/thumbnails/gpt_thumbs.py`, `tools/thumbnails/html_thumbs.py`, `tools/thumbnails/cutout.sh`       |

## What is not in this repository

Footage, photographs, music, voice files and rendered films. Their licences belong to their owners. The example keeps
the links and Commons file names so you can fetch them yourself. Short quotes of others' footage for commentary are
common practice, but the rules differ by country and platform: the decision is yours.

## Credits

Made by Hackyard. Fonts: Space Grotesk and Inter Tight (SIL Open Font License). Animation: GSAP. Rendering: HyperFrames.
Narration and transcription: Azure AI Speech.

## Licence

MIT. See [LICENSE](LICENSE).

Find your people. [hackyard.org](https://hackyard.org)
