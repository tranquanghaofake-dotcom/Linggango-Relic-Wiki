# Linggango Relic Wiki: working rules

## Branches
- `main` is the site plus everything needed to rebuild it, nothing else. GitHub serves `index.html` from the root of `main`.
- `workspace` is an orphan branch for notes, plans, prompts, old history and agent skills (`NOTES.md`, `PROMPT.md`, `build/RUNTIME_PLAN.md`, `build/migrations/`, `.claude/skills/`…). Files keep the paths they had on `main`. Never merge it into `main`; bring one file back with `git checkout workspace -- <path>`.
- No other branches and no pull requests unless the user asks.

## Build
- Edit sources only: `build/src/*`, `build/style.game.css`, data in `build/patches/`. Never edit `index.html`, `static/` or `dist/` by hand.
- `python3 build/build.py` after a front-end edit; `bash build/patches/apply_all.sh` after a data edit (runs the patches, then the build). Outputs:
  - the site: a small `index.html` plus content-hashed `static/*.js|css`;
  - `dist/Linggango_Relic_Wiki.html`: one self-contained file for offline use.
- Commit `index.html`, `static/` and `dist/` together (`git add -A static` so old hashed files are removed).
- `bash build/check.sh` before every push (Chromium via playwright, `NODE_PATH=$(npm root -g)`). CI runs the same on `main`.
- How it works: `build/README.md`; why it is shaped that way: `build/ARCHITECTURE.md`.

## End of every session
1. Build, run `check.sh`, look at the changed pages in a browser.
2. Commit and push to `main`.
3. Add a short entry to `NOTES.md` on `workspace` (e.g. `git worktree add ../ws workspace`), commit, push `workspace`.

## Design
- A clean wiki with the game's identity: pixel face for headings, the vanilla tooltip palette, rarity colours, item slots.
- No looping animation (exceptions: an item's own animated texture, the loading bar). No drop shadows, glows, bevelled buttons or hover lift/zoom; state is shown by colour and one border.
- Do not build what the reader cannot see yet (The Path builds a collapsed Act's tiles when it opens).
- Desktop and laptop first.

## Content
- Naming: the progression as a whole is "The Path"; each stage is an "Act" (Act 0–I, Act II, … Warden Act).
- Numbers come from the game export first, then pack files, then the jar reading. External sites are reference only. Estimates are labelled as estimates.
- The wiki text stays in English; the user reads Vietnamese, so talk to them in Vietnamese.
