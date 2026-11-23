# Pre-PA3 state

State of `harvest-moon-awl-recomp` (binary `hmawl`) on 2026-11-22, before the first PA3 phase.

## What the project is
- Native Linux recompilation of Harvest Moon: A Wonderful Life, GameCube NTSC-U, disc ID **GYWEE9**, built on the
  `gcn-recomp` runtime (developer's fork, branch `harvest-moon-fixes`). `README.md`
- Superproject: `CMakeLists.txt` (REL-module config), `recomp/*.txt` (recomp tables: hle, idle, names, patches,
  special_calls), `analysis/` (dtk `config.yml`, split maps), `harvest_rel_seed.py` (heuristic REL symbol seeds),
  `gcn-recomp/` submodule (runtime and renderer). `README.md` § Source layout
- No PA3 phase has run yet: `phase-ends/current/` is empty, `phase-ends/LEGACY_INDEX.md` lists no legacy phases.
  `PROJECT_CONTEXT.md` and `GENERATION_PLAN.md` named in `CLAUDE.md` do not exist yet.

## Where it stands
- Works (developer's working local build): the game launches and runs natively on CachyOS; dynamic REL modules
  load; memory-card saving works. Not a verified portable release; no binaries shipped. `README.md` § Status
- **Major open defect:** checkerboard corruption on a building and nearby trees in the outdoor scene. Dolphin
  renders the same scene correctly. Seen inside the emulated EFB, before presentation. `README.md` § Known graphics issue
- Already tried before PA3, without effect: draw isolation works; more aggressive texture-cache hashing did not fix it. `README.md`
- Build restored in this checkout 2026-11-22: GYWEE9 ISO at repo root, `rom/main.dol` + `rom/wlp{0,1,2}.rel`
  extracted, `analysis/symbols.txt` and `analysis/rel-symbols/` regenerated, `build-rel/hmawl` built (~19 s with
  `ninja -C build-rel hmawl`). Smoke run: boots, SDK init, 25 s without crash. Outdoor scene, saving and REL areas
  not reached (need interactive play; `saves/memcard_a.raw` is a blank card).
  `docs/dev/gx-checkerboard-investigation.md` § Build restored
- The regenerated `analysis/symbols.txt` and the REL symbols are heuristic seeds, not the original files the
  developer's earlier build used. same doc

## In flight (uncommitted)
- Branch `fix/gx-checkerboard` (main is `master`). Commits: initial project, README status, PA3 install.
- `gcn-recomp` is detached at the pinned commit `5ae33b9` ("WIP: Harvest Moon runtime support and GX debugging")
  with two uncommitted edits:
  - `runtime/gx/render_gl.cpp` `get_sampler()`: **candidate checkerboard fix**. The old 32-bit sampler-cache key
    `(mode0 & 0x3FFFFF) ^ (mode1 << 22) ^ (levels << 30)` dropped most of max_lod and wrapped levels mod 4, so a
    single-level texture/EFB copy (max_lod 0, levels 1) shared a sampler with a mipmapped one (max_lod 4.0,
    levels 5), giving level-0-only minification and aliasing on distant textures. New: 64-bit key, fields packed
    without overlap; map is `unordered_map<uint64_t, GLuint>`. Brute-force check: 33.5M colliding states before, 0
    after. Compiles; **not runtime-verified**: whether it is *the* cause is unknown.
    `docs/dev/gx-checkerboard-investigation.md` § Candidate defect fixed, § Key verification
  - `runtime/boot.cpp:55`: a `[TMPDBG]` FST-words `fprintf`, marked `// TEMP`; debug only, to be removed before commit.
- `docs/dev/gx-checkerboard-investigation.md` itself is untracked (the card names it as a living doc).

## Next (from the investigation doc § Next action)
1. Run the outdoor scene with and without the fix (A/B via `git -C gcn-recomp stash`), compare the building/trees
   with Dolphin. This needs the developer at the controls.
2. If the checkerboard persists: use the GX debug overlay on an affected draw, record mode0/mode1, level count,
   tex format/address, compare with the Dolphin FIFO capture `test.dff` for the same draw.
3. Regression check: title/UI text, memory-card save, REL-loaded scenes.
4. If it works: commit in `gcn-recomp`, bump the submodule pin in the superproject, drop the TEMP print.

## Decided; do not undo
- Rule L1 (`rules/L1.md`): memory-card saving and REL loading must survive every runtime change; fixes are isolated
  and reversible; incomplete TMEM placement/bank emulation (BP `0x60`-`0x63` preloads) is a hypothesis, not a
  confirmed cause.
- Rule L2 (`rules/L2.md`): no original game data in git (images, DOL/REL, textures, symbol maps, saves, `*.dff`);
  each developer uses their own legally obtained dump; `.gitignore` enforces it. `README.md` § Legal
- Audited, no defect found; do not redo: `texture.cpp` tiled decoders (I4 through CMPR), TLUT load/lookup offsets,
  the preload path for RAM-contiguous textures (TMEM matters only if the game preloads from a source other than
  TexImage3 or reuses TMEM with a stale base). Noted, not changed: `xf.cpp resolve_texture` uses floor for levels
  where Dolphin uses ceil (fractional top LOD only). `docs/dev/gx-checkerboard-investigation.md` § Audited
- The right disc is GYWEE9 (DOL sha1 `1ccfd9df...`). `Another Wonderful Life` (G4GEE9) is a different game; the
  earlier attempt with it sits in `.run/g4g-experiment/`, left untouched. Inputs are never faked or regenerated from
  the wrong disc. same doc § Build restoration attempt
- `dtk dol split` errors "Unaligned symbol" after `analysis/symbols.txt` is written; that file is usable.

## Where details live
- Build-from-dump steps: `docs/dev/gx-checkerboard-investigation.md` § Build restored; standing facts: `HOW_WE_WORK.md`.
- Renderer diagnostics (`GCN_DRAWLOG`, `GCN_DRAWLOG_VERBOSE`, `GCN_DRAW_SKIP`, `GCN_PIXEL`): `README.md` § Debugging
  and the fork's `docs/gx-debug-overlay.md`.
- Archived memory (the old checkerboard status note): `.claude-state/memory/gen3.2.md`.
