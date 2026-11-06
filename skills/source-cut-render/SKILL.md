---
name: source-cut-render
description: Render a reviewed Source Cut film and Short on the VM in chunks, queue renders back to back, normalise loudness with two-pass EBU R128 plus a limiter, and verify the result (tools/render). Use only after the user approved the reviewed edit.
---

# Render

```bash
tools/render/vm.sh films/<slug>/film lint            # sync the film (and its assets) to the VM
tools/render/vm.sh films/<slug>/short lint
scp tools/render/render-final.sh tools/render/loudness.sh <host>:
ssh <host> 'nohup ./render-final.sh $SOURCE_CUT_REMOTE_ROOT/films/<slug> <film end seconds> <tag> > /dev/null 2>&1 &'
```

`render-final.sh` renders the film in four chunks, two at a time, then the Short, then joins the chunks. It writes
`/tmp/<tag>-done` when finished and logs to `/tmp/<tag>-*.log`. The film's end time is the last line `build.py` prints.

## Queue, never overlap

Two renders at once starve each other and snapshots time out. Queue the next film behind the current one:

```bash
nohup sh -c "while [ ! -f /tmp/<prev>-done ]; do sleep 20; done; ./render-final.sh ... <next>" > /dev/null 2>&1 &
```

## Loudness

On the VM, for the film and the Short:

```bash
./loudness.sh <film>/film/renders/joined.mp4 <film>/film/renders/final.mp4
```

Two passes plus a limiter land at -15 to -15.5 LUFS integrated with true peaks at or under -1.3 dB. The script prints
the measured values; record them in `UPLOAD.md`.

## Pull and verify

`tools/render/vm.sh films/<slug>/film --pull renders/final.mp4` (and the Short). Then check:
- length matches the build;
- a contact sheet of the final file (one frame every few seconds) matches the reviewed edit;
- the subtitles (`renders/*.srt` from `build.py`) line up at the start, middle and end.

Leave the VM running only while you need it; stop it after a batch.
