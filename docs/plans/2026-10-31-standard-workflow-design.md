# Standard workflow: tools around the six steps — design and plan (2026-10-31)

Spec and plan in one file: the plan is short. Written with superpowers `brainstorming`; the session ran unattended,
so the approaches are laid out here and the recommended one was taken (CLAUDE.md, Process).

## Intent
The owner asked for research into connectors, skills, plugins and open-source projects that help this wiki, adding
what helps, and one standard process that joins the new tools to the existing one (CLAUDE.md's six steps, the
renovation plan in `docs/RENOVATION_PREP.md`) for the best output. "Output" here is the deployed wiki: right numbers,
pages that look as intended at 1440 and 375 px, no script errors, and a session whose notes say what is still open.

## What was found
- **Skills.** Superpowers is now on the account (its 15 skills load in this session); ponytail is in the repo
  (`.claude/skills/ponytail`). Both chosen and reasoned in `docs/AGENT_TOOLS.md` the same day.
- **Connectors on the account that serve this repo:** GitHub (read the `site` workflow's result, the step the process
  needs before "it is live"); Firecrawl and Parallel (read external wikis, Modrinth and CurseForge pages as reference,
  never as numbers). Figma can generate images but spends the owner's credits (v41) and is not used. Gmail, Calendar,
  Drive, Notion, Canva, Hugging Face and the legal connectors do not touch this repo.
- **Open-source tools already in use:** Playwright 1.63 (`shot.js`, `perf.js`, the three check scripts), three.js
  0.169 (render tools), the 1.20.1 asset clone, Mojang mappings + MCPConfig (not committed), jawa (`mjvm.py`).
- **Spike: would a linter gate raise quality?** `ruff check build` with its default rule set reports 715 findings in
  102 Python files. The 28 in real-bug classes (`F821`, `PLR0124`, `B023`, `B006`, `S102`) were read one by one:
  `v != v` is the NaN test in `mjvm.py`; `extra.py` runs `gear_data.py`'s prelude through `exec` on purpose, so its
  names are "undefined" to a linter; the loop-variable closures in `lootlib.py`, `gear_runtime.py` and
  `measure/import.py` are called inside the same iteration; `memo={}` in `eqa/audit.py` is a deliberate cache. Zero
  real bugs, so a lint gate would add noise to `check.sh`, which already fails on behaviour (invariants, layout,
  pixel rules, a loading site). `node --check` over the 27 JS files is clean. Conclusion: linters stay one-off tools
  run by hand before a consolidation pass, not gates.
- **Graph tools, design skills, Caveman, Agency Agents personas:** evaluated the same day in `docs/AGENT_TOOLS.md`;
  nothing changed since.

## Approaches
1. **CLAUDE.md stays the one process document** (recommended). Its six steps already are the shipping half of the
   process; a "Process" section states the other half: classify, plan when architectural, smallest complete change,
   bugs become invariants, done means evidence, review before merge, CI result read through the GitHub connector.
   `docs/AGENT_TOOLS.md` grows two short sections (connectors, open-source tools) so every tool decision has one home.
   Nothing new to install or maintain.
2. **A separate `docs/PROCESS.md` runbook** with phases, templates and checklists, CLAUDE.md pointing at it. More
   to read each session and a second place the rules can drift from; CLAUDE.md is loaded automatically, a runbook is
   not.
3. **Automate the process** (ruff and a perf budget in `check.sh`, an accessibility pass, a `SessionStart` hook that
   prints the steps). The spike shows the lint gate would fail on intentional code; a frame-time budget is flaky on
   CI runners; hooks live in account or machine settings, not the repo.

Approach 1, with one calibration learned from this very task: the planning rule written earlier today ("anything
beyond one page or one tool starts with a plan") is meant for the site and the build. Documentation and process
changes are bounded; and when a plan is short, spec and plan share one file (this one).

## Design
- **CLAUDE.md:** the "Skills and agents" section becomes "Process", in the order a session works: classify →
  plan (architectural only, `docs/plans/`) → facts (Facts section, connectors as reference) → smallest complete change
  (ponytail) → bugs (systematic-debugging, invariant) → done = evidence (steps 3–4, `verification-before-completion`,
  the `site` run read with the GitHub connector) → review before merge for architectural work → where the tool
  decisions live. Same length as before; nothing else in CLAUDE.md moves.
- **docs/AGENT_TOOLS.md:** "Connectors" (which, for what, which not) and "Open-source tools" (in use; tried and kept
  as hand tools, with the ruff spike as the reason) after the "Used" section.
- **docs/NOTES.md:** this session's entry.
- Nothing in `build/`, no new dependency, no CI change.

## Steps
1. Write this file. 2. Edit CLAUDE.md's section. 3. Add the two sections to `docs/AGENT_TOOLS.md`. 4. Confirm the
GitHub connector can read this repo's workflow runs (so step 6 of the process is executable from a session). 5. Notes
entry. 6. One commit on the session's branch, push; `check.sh` not needed (no build source changed).

## Out of scope
The Law repo (same account-level Superpowers applies; its own CLAUDE.md is the counterpart, not in this session's
scope); any Agency Agents persona; ruff fixes (the findings are intentional); Figma image generation.
