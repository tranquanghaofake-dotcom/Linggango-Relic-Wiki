# workspace: notes, plans and prompts for the Linggango Relic Wiki

This branch is not the site. `main` holds only what the wiki needs to run and to be rebuilt.
Everything here keeps the path it had on `main`, so any file can be brought back with
`git checkout workspace -- <path>` from a `main` checkout.

| Path | What it is |
|---|---|
| `NOTES.md` | Change log, one entry per session (v1 →) |
| `PROMPT.md` | The original overhaul prompt |
| `build/RUNTIME_PLAN.md` | Plan: every wiki number from the game |
| `build/changes.csv`, `build/transform.py`, `assets/vanilla/` | The one-off that turned `original/` into the first `data.js` (history, not used to rebuild) |
| `build/migrations/` | The nine one-time edits that shaped `data.js` |
| `shots/` | Old screenshots |
| `.claude/skills/`, `skills-lock.json` | Agent skills installed in v25 (vercel-labs/agent-skills) |

The branch has no common history with `main` (orphan): it is never merged into it.
