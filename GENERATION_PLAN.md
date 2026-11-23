# Generation 1 — Startup restored, checkerboard fix verified

Goal: `./build-rel/hmawl` starts normally again (no black screen), then the uncommitted GX sampler-cache-key fix is A/B-tested at runtime against Dolphin and landed or rejected on evidence.
Done-criteria: 1.1 and 1.2 milestones both confirmed by the developer; the sampler fix and every other pre-existing uncommitted edit are either committed on evidence or still present, never lost.

## Phases

- 1.1 Restore normal startup | milestone: `ninja -C build-rel hmawl; and ./build-rel/hmawl` shows the title screen (no black screen) on the developer's machine, with the sampler-key fix still applied; the root cause and the fix are written in `docs/dev/black-screen.md` | scope: diagnose and fix the native runtime's black screen; preserve the uncommitted `gcn-recomp` edits (sampler key in `runtime/gx/render_gl.cpp`, `[TMPDBG]` print in `runtime/boot.cpp:55`) | depends: — | status: open | phase-end: phase-ends/PhaseEnd_Phase1.1.md
- 1.2 Verify and land the checkerboard fix | milestone: the developer plays to the outdoor scene with fix on and fix off and confirms on-vs-off against Dolphin (building/trees), and title/UI text, a memory-card save and a REL-loaded scene still work (L1); on a pass the fix is committed in `gcn-recomp`, the submodule pin bumped and the `[TMPDBG]` print removed | scope: runtime A/B of the sampler-key fix; regression check; landing; if the checkerboard persists, one bounded per-draw comparison against `test.dff` per investigation doc § Next action 2 | depends: 1.1 | status: open | phase-end: phase-ends/PhaseEnd_Phase1.2.md

## Ordering rationale

- 1.1 before 1.2: no runtime verification of the checkerboard fix is possible while the game does not reach a visible frame.
- 1.2 is validation, its own phase: its gate is the developer's eyes on the outdoor scene against Dolphin, not a proxy.

## Research per phase

- 1.1: no report covers it yet. Starting facts: `docs/dev/gx-checkerboard-investigation.md` § Build restored (smoke run boots, SDK init, 25 s no crash: whether a frame appeared was never recorded), `docs/PRE_PA3_STATE.md`. The phase planner sends one `retriever-code` for the boot → VI/XFB → GL present path in `gcn-recomp/runtime/` and the uses of `analysis/symbols.txt` / `recomp/*.txt` in the build.
- 1.2: no report covers it yet. Starting facts: investigation doc § Candidate defect fixed, § Key verification, § Next action; `get_sampler()` in `gcn-recomp/runtime/gx/render_gl.cpp`.

## Phase 1.1 approach (for its planner)

- First pin down the symptom from the developer and one captured run: black window from the first frame, or after the intro; with stderr/LOG output saved under `.run/1.1/`.
- Hypotheses not covered by earlier sessions, cheapest first: (a) the regenerated heuristic `analysis/symbols.txt` / `analysis/rel-symbols/` differ from the files the developer's earlier working build used (pre-PA3 state names this), so recomp tables in `recomp/*.txt` miss functions, giving an idle/hang loop or no VI retrace callback; (b) the uncommitted edits: test by a build with the sampler hunk reversed in a scratch copy (never stash), so the fix is ruled in or out as the cause; (c) XFB/VI present path or GL context; (d) the blank memory card `saves/memcard_a.raw` stalling a boot prompt behind an unrendered layer.
- Isolate on one cheap run per hypothesis (diagnostic-grade), prove the fix with a re-run, developer confirms.
- Do not repeat: texture decoder, TLUT, preload-path audits; the sampler-key collision proof; the GYWEE9 input hunt.

## Standing constraints

- Never `git stash`, `reset`, `checkout --`, `clean` or `submodule update` in `gcn-recomp` or the superproject; the uncommitted submodule edits are irreplaceable. Before any first `gcn-recomp` edit of a phase, save `git -C gcn-recomp diff > .run/<phase>/gcn-recomp-uncommitted.patch` as a backup.
- A/B of a change is done by a scratch copy, a reversed patch applied and re-applied, or an env diagnostic toggle in the `GCN_*` family, never by stash.
- `gcn-recomp` is detached at 5ae33b9: runtime commits go on fork branch `harvest-moon-fixes` (created at the current HEAD without touching the working tree), then the superproject pin is bumped (card Conventions). A commit that would sweep in the sampler hunk before 1.2 verifies it is not made; that edit stays uncommitted until 1.2.
- Rules L1 (save and REL loading survive every runtime change; TMEM is a hypothesis) and L2 (no game data in git) bind every phase.
- Oracle: Dolphin rendering the same scene; `test.dff` FIFO capture (local only). Scene-level checks need the developer at the controls; agents may smoke-run boot only.
- Build: `ninja -C build-rel hmawl`; regenerating inputs follows the investigation doc § Build restored. All agents run at the default in-house tier (no external coders); minimal retriever use.

## Changes

<!-- - <date> claude|developer: <what> — <why> -->
