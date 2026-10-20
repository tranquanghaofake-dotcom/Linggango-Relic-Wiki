# Linggango Relic Wiki: working rules

- There is one wiki and one branch: `main`. The site link serves `index.html` from the root of `main`.
- Edit sources in `build/` (`build/src/*`, `build/style.game.css`), then run `python3 build/build.py`; it writes `index.html` and `dist/Linggango_Relic_Wiki.html`. Never edit those two files by hand.
- At the end of every session: build, check the pages, add a short entry to `NOTES.md`, commit and push straight to `main`. No side branches, no pull requests unless the user asks.
- Naming: the progression as a whole is "The Path"; each stage is an "Act" (Act 0–I, Act II, … Warden Act).
- The user reads Vietnamese; the wiki text stays in English.
