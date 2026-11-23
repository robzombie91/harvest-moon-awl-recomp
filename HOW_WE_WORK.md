# How we work — harvest-moon-awl-recomp

<!-- The card: standing facts for every agent. Never appended to; the cap is
     card.max_chars in .claude/pa.json (default 10000), enforced by the archive.
     Each role prints its slice with `tools/card.py slice <role>`.
     Written at install (interview) and edited in the same task as whatever changed it (H7). -->

## Project <!-- roles: claude expert coder planner review auditor curator -->
harvest-moon-awl-recomp — hmawl. Constitution `PROJECT_CONTEXT.md`; roadmap `GENERATION_PLAN.md`;
rules `rules/INDEX.md`; techniques `cookbook/INDEX.md`; ops detail `docs/ops/INDEX.md`.

## Developer <!-- roles: claude planner review auditor curator -->
Who: robzombie91. Experience: advanced. Domain: harvest-moon-awl-recomp.
Preferences: recommendations, not questions. Plain-English recaps at phase end. A notification
whenever anything waits on them. Autonomy: full inside an approved plan; stop only at the two gates. Notification channel: toast.
Their login shell is fish: commands handed to them use fish syntax (`; and`, not `&&`).
The developer pushes; agents never do. They ratify rules at the next plan approval.

## Tools <!-- roles: expert coder planner review auditor curator -->
PY = /usr/bin/python

| Name | Command | Purpose |
|---|---|---|
| launch | `PY tools/launch.py --state-json` | the state detector: the mod's read-only report; never typed by the developer |
| plan_edit | `PY tools/plan_edit.py` | the only writer of `PHASE_PLAN.md` (status, Changes, add/reopen) |
| status | `PY tools/status.py` | `.run/status.json` for the statusline; INBOX consume; waiting flags |
| task_log | `PY tools/task_log.py` | lint and finish a task summary |
| research_add | `PY tools/research_add.py` | allocate a report id, write the index line |
| rules_add | `PY tools/rules_add.py` | add, supersede, promote, retire a rule |
| skill_add | `PY tools/skill_add.py` | turn a `workflow:` gotcha into `.claude/skills/<name>/SKILL.md` |
| cookbook_add | `bash tools/cookbook_add.sh` | add a cookbook entry and its index line |
| phaseend_index | `PY tools/phaseend_index.py` | assemble and archive a PhaseEnd; `history` rebuilds `docs/PHASE_HISTORY.md` |
| genend_index | `PY tools/genend_index.py` | assemble a GenerationEnd |
| commit_task | `bash tools/commit_task.sh` | the only commit path; explicit paths, no trailers, never pushes |
| run | `bash tools/run.sh` | any command that may print >40 lines |
| curate | `PY tools/curate.py` | `memory --route\|--reindex`, `rules --reseed\|--demote`, `cookbook --demote`, `claude-md\|card --refresh`, `living-docs --entry`, `how-we-work --retire`; `--dry-run` first |
| dtk | `gcn-recomp/tools/dtk` | extract DOL/RELs from the disc image (`vfs cp`), `dol split` writes `analysis/symbols.txt` |

## Skills <!-- roles: expert planner -->
<!-- one line per captured workflow; the SKILL.md is the canonical text -->
- (none yet)

## Paths <!-- roles: claude expert coder planner review auditor curator -->
- Oracles (the ground truth X3 names): Dolphin Emulator rendering the same scene; Dolphin FIFO capture `test.dff` (local only)
- Data: the developer's GYWEE9 dump `Harvest Moon - A Wonderful Life (USA).iso` (repo root, gitignored; rule L2) → `rom/main.dol`, `rom/wlp{0,1,2}.rel`
- Generated (never hand-edited, H1): `analysis/symbols.txt`, `analysis/rel-symbols/`, `analysis/split/`, `build-rel/`, `saves/`
- Hand-edited: `CMakeLists.txt`, `recomp/*.txt`, `analysis/config.yml`, `analysis/*splits.txt`, `harvest_rel_seed.py`; runtime in submodule `gcn-recomp/` (fork branch `harvest-moon-fixes`, commit pinned here)
- Scratch: all of a phase's work in `.run/` goes under `.run/<phase>/` (gitignored; never the system temp), nowhere
  else in `.run/`. It is a temp folder only, never a home for long-term content: what the project needs lives in its
  proper place in the repo. The phase's cleanup task checks it and
  the close deletes it; a tool deletes its own temp folders when it finishes.

## Build / run / test <!-- roles: claude expert coder planner review auditor curator -->
- Build: `ninja -C build-rel hmawl` (~19 s); first configure and input regeneration: `docs/dev/gx-checkerboard-investigation.md` § Build restored
- Run: `./build-rel/hmawl` (agents can smoke-run boot only; scenes need interactive play)
- Test / the gate: no automated test; the developer plays the outdoor scene — green means no checkerboard on the building/trees (matches Dolphin) and title/UI text, memory-card save and REL scenes still work (L1)
- Modes: renderer diagnostics via env `GCN_DRAWLOG`, `GCN_DRAWLOG_VERBOSE`, `GCN_DRAW_SKIP`, `GCN_PIXEL`, EFB-copy diagnostics
Long gates go through `tools/run.sh` with a raised timeout, never a poll loop.

## Conventions & house style <!-- roles: claude expert coder planner review auditor curator -->
- Runtime fixes are made in `gcn-recomp/`, committed there, then the superproject bumps the submodule pin
- Never commit game data (L2); preserve saves and RELs, TMEM is a hypothesis (L1)
<!-- project-specific only; the general house style is in the project-architect skill -->

## Environment <!-- roles: claude expert coder planner review auditor curator -->
- OS / shells: CachyOS Linux / bash, zsh; toolchain Clang, CMake, Ninja
- Python: /usr/bin/python (3.14.10)
- Pins: `gcn-recomp` submodule commit (5ae33b9); GYWEE9 DOL sha1 `1ccfd9df...` (not G4GEE9 Another Wonderful Life)
- Harness gotchas that bite here: `dtk dol split` errors "Unaligned symbol" after `symbols.txt` is written; the file is usable

## Docs map <!-- roles: expert coder planner review auditor curator -->
- `docs/ops/INDEX.md` — setup, env, pins, per-topic ops notes
- `cookbook/INDEX.md` — techniques, grep by tag
- `rules/INDEX.md` — full rule texts
- `phase-ends/TASK_INDEX.md`, `phase-ends/RESEARCH_INDEX.md` — what was done and what was learned
- `docs/research-archive/` — migrated legacy reports
- `docs/retired/` — everything moved out of the load order

## Living docs <!-- roles: claude expert planner curator -->
- `README.md`: project status, source layout, prerequisites and legal stance; update when status or build prerequisites change
- `docs/dev/gx-checkerboard-investigation.md`: GX checkerboard findings, the build-from-dump steps, next A/B; update in the same change as any checkerboard finding or build step
