# Contributing to Source Cut

Thanks for helping. Source Cut is small on purpose: plain Python, shell and HTML, no framework, every tool readable in
one sitting.

## Ground rules

- **No secrets, no private infrastructure.** Settings come from `.env` (see `.env.example`). Never commit keys, hosts,
  IPs or personal paths.
- **No third-party media.** Footage, photos, music and rendered films stay out of the repo. Add sources as links and
  `commons.json` entries, not files.
- **Keep the principles.** A change that makes it easier to show an unsourced claim, an AI-generated person as real, or
  an uncredited image will not be merged. See `docs/principles.md`.
- **Heavy work runs on the VM.** Tools that render, encode at length or run models go through `tools/render/vm.sh` or
  the VM, not the contributor's laptop.

## Pull requests

1. Open an issue first for anything larger than a fix.
2. Keep diffs small and in the style of the file you change.
3. If you change the engine, rebuild `examples/wework` (`python3 film/build.py`) and include a contact sheet of the
   affected shots.
4. If you change a skill, keep its `description` specific about when it should be used.

## Reporting a problem

Include the command you ran, the output, and your OS. Remove keys and hosts from logs before you paste them.
