# Agent skills and tools (evaluated 2026-10-31)

Which third-party Claude Code skills, plugins and agents this repo uses, where each one lives, and which were looked
at and left out. The working rules stay in `CLAUDE.md`; no skill overrides them.

## Where a skill can live, and who sees it
| Place | Who loads it | Set by |
|---|---|---|
| Account plugin (claude.ai → Customize → Plugins) | every Claude Code session signed in to the account: cloud sessions and the owner's own machine | the owner, from the plugin catalog |
| `.claude/skills/<name>/SKILL.md` in this repo | every session that opens this repo, local or cloud | a commit here |
| `~/.claude/agents`, `~/.claude/skills`, `/plugin install` on one machine | that machine only | the Agency Agents app, the Claude Code CLI |

A cloud session sees only the first two. The 159 Agency Agents personas the app synced to `~\.claude\agents` on the
owner's Windows machine are in the third: they work in Claude Code on that machine and nowhere else.

## Used

### Superpowers — obra/superpowers (MIT), account plugin
The planning and execution method. In the catalog as "Superpowers" (Anthropic Directory, partner tier, upstream
obra/superpowers, 6.4.2 at the time of writing; upstream `main` @2ce8aa1, the same commit v42 read). Install it from
the catalog, then start a new session; its `SessionStart` hook loads `using-superpowers`.

How it maps onto this repo:
- **Anything beyond one page or one tool starts with a plan:** `brainstorming` (approaches, then a short design doc)
  → `writing-plans` → `executing-plans` or `subagent-driven-development`. Plans and design docs go to
  `docs/plans/YYYY-MM-DD-<topic>.md` (the skill's default `docs/superpowers/plans/` is overridden here; the v42
  overhaul spec lived at `docs/superpowers/specs/` on the old branch).
- **Unattended sessions:** `brainstorming` ends each message with a question, which blocks a cloud session nobody is
  watching. There, lay the approaches out in the reply, go on with the recommended one on the session's branch, and
  leave anything that changes the look for the owner's approval (`CLAUDE.md`, Design).
- **`verification-before-completion`** is `CLAUDE.md` steps 3–4 said sternly: shots looked at and `check.sh` green in
  this session, or it is not done.
- **`systematic-debugging`** for data bugs; the fix ends as an invariant in `build/check.js` (`CLAUDE.md`, Facts).
- **`test-driven-development`:** the test here is a `check.js` invariant, a `style_check.js` rule or a `shot.js --diff`,
  not a unit-test framework.
- `using-superpowers` itself says user instructions (`CLAUDE.md`) take precedence over skills.

### Ponytail — DietrichGebert/ponytail (MIT), vendored at `.claude/skills/ponytail/`
"The smallest change that fully solves the task": no abstraction, option or file nobody asked for; delete before
adding; grep every caller before a fix; finish the callers and checks the change breaks. That is this repo's
"one file per thing" rule and the renovation's "one class layer and one interpreter" written as a skill. One
`SKILL.md`, no scripts, so it runs in auto mode where skills with scripts were blocked (v34).

- Copied verbatim from upstream `main` @96608e0 (`skills/ponytail/SKILL.md`, `LICENSE`). To update, copy the same two
  files again; nothing here is edited.
- Say "ponytail" or ask for the simplest solution to invoke it; `ultra` when folding tools together (it questions the
  request before building). Its reply trailer ("what I skipped or did not check") feeds the "still open" line of the
  session's `docs/NOTES.md` entry.
- Not installed as the plugin (the band and `/ponytail-*` commands are machine-local and not in the catalog).

## Looked at and left out
| Skill | What it is | Why not here |
|---|---|---|
| Caveman (JuliusBrussee/caveman, Apache-2.0; two variants in the catalog) | Terse replies to cut tokens | The owner reads Vietnamese summaries with full diacritics and wants practical distinctions spelled out; replies are the product of a session here, the wiki text is untouched either way. The CLI also sends usage statistics. |
| UI UX Pro Max (nextlevelbuilder, MIT; premium tier) | Design-system search: styles, palettes, fonts, 119 UX rules | Evaluated in v34: its house style (flat, no shadows) would repeat the reverted v30 pass; its search scripts were blocked in auto mode. The UX rules were used once as a checklist; nothing to install. |
| Impeccable (pbakaus/impeccable, Apache-2.0) | Design-director voice, `/impeccable audit\|polish\|critique`, an anti-slop detector binary | Built for conventional web UI; the wiki's identity is Minecraft's GUI, which its taste would flatten. The detector downloads a binary into `~/.impeccable/bin`. Its anti-patterns that apply here (rounded corners, fractional pixel scales, emoji icons) are already `build/style_check.js` rules. For a critique, Anthropic's "Design" plugin (`design-critique`) is already on the account. |
| Addy Osmani agent-skills (MIT, 25 skills) | Engineering workflow: spec, plan, TDD, review, perf, ship | Overlaps Superpowers on planning, TDD, review and debugging; two bootstraps would compete. Single-skill installs lose the pack's shared `references/` checklists (upstream issue #361). Its performance skill targets Core Web Vitals on app stacks; the wiki measures with `build/perf.js` and `shot.js`. Not in the catalog. |
| Graphify (Apache-2.0 CLI, paid app), Understand Anything (MIT plugin), Archify (Apache-2.0) | Code knowledge graphs and architecture diagrams | The build is 129 Python/JS files, 12k lines, and `build/ARCHITECTURE.md` already names the single place of every decision; a graph adds little and the outputs are large (Understand Anything suggests git LFS). If the "one class layer and one interpreter" pass wants a dependency map of the `pack_audit/` and `gear/` tools first, run `graphify` once into the session scratchpad and keep nothing. |
| Awesome Claude Skills | A curated list | Nothing to install. |
| Agency Agents (msitarzewski, MIT; 159 synced on the owner's machine) | Role personas: a voice, a process, deliverables; no tools | `CLAUDE.md` already carries this project's expertise, and the built-in agent types cover fan-out. If one persona is wanted in a cloud session, copy its `.md` into `.claude/agents/` (project scope) and commit it. |

## About the "Top 10 Claude Code Skills, October 2026" image
Ranked by GitHub stars. Superpowers (293.6k) and Caveman (past 100k) match GitHub; Impeccable shows 71.7k where the
repo snapshot read 38k and its site 89–95k. The others were not re-counted. Stars say popularity, not fit: the two
kept here are the one that matches how this repo already plans (Superpowers, used in v42) and the one that matches how
it already edits (Ponytail).
