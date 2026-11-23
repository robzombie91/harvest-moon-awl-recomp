# GX checkerboard investigation (2026-11-22)

## State of this checkout
- Fresh clone: no `analysis/symbols.txt`, `analysis/rel-symbols/`, `rom/` inputs or `build-rel/`.
  The game cannot be built or run here, so nothing below is runtime-verified.
- `gcn-recomp` submodule was initialised at pinned 5ae33b9; the fix is an uncommitted edit there.

## Candidate defect fixed (source-level, unverified at runtime)
`gcn-recomp/runtime/gx/render_gl.cpp` `get_sampler()` cached GL samplers under a 32-bit key
`(mode0 & 0x3FFFFF) ^ (mode1 << 22) ^ (levels << 30)`:
- mode1 bits 10-15 (most of max_lod) were shifted out; bits 8-9 overlapped `levels`.
- `levels << 30` wraps mod 4, so levels 1 and 5 (2 and 6, ...) collide.
- e.g. max_lod 0 / levels 1 (any single-level texture or EFB copy, which passes levels=1)
  has the same key as max_lod 4.0 / levels 5 → mipmapped texture reuses a sampler with
  MAX_LOD 0 and a non-mip min filter → level 0 only when minified → heavy aliasing/moire on
  distant high-frequency textures (buildings, foliage), rendered into the EFB.
Fix: 64-bit key, fields packed without overlap (mode0 22b | mode1 16b | levels>1). Map type
changed to `unordered_map<uint64_t, GLuint>`. `clang++ -fsyntax-only` passes.

## Audited, no defect found
- texture.cpp tiled decoders (I4/I8/IA4/IA8/565/5A3/RGBA8/CI4/CI8/CI14X2/CMPR) match GX layout.
- TLUT load offset `(v&0x3FF)<<9` and lookup `(tlut&0x3FF)<<9` are consistent.
- Preload path: decoded from snapshot of RAM at TexImage3 address. For RAM-contiguous
  textures, Dolphin's TMEM decode (RGBA8 even/odd split, mips alternating even/odd banks)
  yields identical texels, so TMEM only matters if the game preloads from a different
  source than TexImage3 or reuses TMEM with stale image_base. Not proven.

## Minor differences noted (not changed)
- xf.cpp `resolve_texture`: levels = floor(max_lod/16)+1; Dolphin uses ceil. Only affects a
  fractional top LOD.

## Next action
1. Build with the game inputs, go to the outdoor scene, compare with/without the fix
   (`git -C gcn-recomp stash` to A/B).
2. If the checkerboard persists: use the overlay on an affected draw, record mode0/mode1,
   level count, tex fmt/addr; compare against Dolphin FIFO (test.dff) for the same draw.
3. Regression check: title/UI text, save to memory card, REL-loaded scenes.

## Key verification (second session)
Standalone brute-force test (not committed) over mode0 bits 0-16 x mode1 (65k sampled values) x
levels in {1,2,5}: 100.7M distinct sampler states. Old key: 33.5M states collided with a
different state. New 64-bit key: 0 collisions. Concrete case with the old formula:
levels=1/max_lod=0 and levels=5/max_lod=4.0 (mode0=0x1F0) both gave key 0x400001f0.
`get_sampler` reads only mode0 bits 0-16 and mode1 bits 0-15, plus `levels>1`; all are in the new key.
The collision is real; whether it is *the* checkerboard cause still needs the runtime A/B below.

## Apply and test in the local build (Fish)
    cd ~/Projects/harvest-moon-awl-recomp
    git -C gcn-recomp diff > /tmp/sampler-key.patch    # patch as it exists in this checkout
    # in the working tree that has the game inputs and build-rel/:
    git -C gcn-recomp apply /tmp/sampler-key.patch
    cmake --build build-rel; and ./build-rel/hmawl
    # A/B: revert with `git -C gcn-recomp stash`, rebuild, compare the outdoor building/trees

## Build restoration attempt (third session)
Blocked: GYWEE9 inputs not present anywhere local. Checked: project dir, `find /` for
*.iso/*.rvz/*.gcm/*.ciso/main.dol/wlp0.rel/GYWE*, Dolphin config. Only game image is
`Harvest Moon - Another Wonderful Life (USA).iso` (G4GEE9; its DOL sha1 d3a9cd68...,
config expects GYWEE9 DOL sha1 1ccfd9df...). `.run/g4g-experiment/` is an earlier G4G
attempt, left untouched. Dolphin has only `~/.cache/dolphin-emu/GYWEE9.uidcache` (no image).
Missing, needed for a build: GYWEE9 disc image (or `rom/main.dol` with that sha1 plus
`wlp0/1/2.rel`), `analysis/symbols.txt`, `analysis/rel-symbols/`. Not regenerated/faked.

## Build restored (fourth session, 2026-11-22)
GYWEE9 image present; DOL sha1 1ccfd9df... verified. Steps used (all outputs gitignored):
    gcn-recomp/tools/dtk vfs cp "<iso>:sys/main.dol" rom/main.dol ; same for files/wlp{0,1,2}.rel
    gcn-recomp/tools/dtk dol split analysis/config.yml analysis/split   # writes analysis/symbols.txt; the
        later asm-writing step errors ("Unaligned symbol") but symbols.txt is already written and sufficient
    python3 harvest_rel_seed.py rom/wlp{0,1,2}.rel -o analysis/rel-symbols
    cmake -S . -B build-rel -G Ninja -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
        -DCMAKE_BUILD_TYPE=Release "-DGAME_ISO=$PWD/Harvest Moon - A Wonderful Life (USA).iso"
    ninja -C build-rel hmawl        # ~19 s, includes the sampler fix
Smoke run: boots, SDK init, 25 s without crash. Not reached: outdoor scene, saving, REL areas
(needs interactive play; saves/memcard_a.raw is a fresh blank card). Checkerboard UNVERIFIED.
Note: the analysis/symbols.txt is regenerated, so REL symbols are heuristic seeds, not the original files.

## Startup restored, checkerboard persists (fifth session, 2026-11-22)
- Black screen fixed (phase 1.1, T2): BI2 ArgOffset zeroed (gcn-recomp db65cdf), OSLink/OSUnlink named
  in recomp/names.txt, the 80086634 stubs split in analysis/symbols.txt (generated, gitignored). Details in phase-ends/current/logs/T2*.md.
- Game is playable; developer reached the outdoor scene via an imported save.
- RUNTIME RESULT: with the 64-bit sampler-key fix applied the checkerboard is STILL present
  (large alternating squares of corrupt/valid texture on building, trees, surroundings; HUD fine).
  So the sampler key was not (or not the only) cause. Hypotheses open: texture decode, memory
  addressing, EFB copy, TEV. Next: isolate the affected draws (GCN_DRAWLOG / GCN_DRAW_SKIP / GCN_COPYDUMP).
- Recorded input logs: saves/inputs/<stamp>/inputs.txt (replay with hmawl --replay <dir>).

## Status update 2026-11-22 (phase 1.1 / T2)
- Startup now works: BI2 ArgOffset fix (gcn-recomp db65cdf), OSLink/OSUnlink named in `recomp/names.txt`, thunk stubs 80086634..8008664C split in `analysis/symbols.txt`. The game is playable; the outdoor scene is reached with the imported card (`saves/memcard_a.imported.raw`).
- The checkerboard is still present with the 64-bit sampler-cache fix applied: large alternating squares of corrupted/valid texture data over building, trees and surroundings; HUD largely fine (developer screenshot). So the sampler key was not the (sole) cause.
- Next: one focused investigation (draw isolation, EFB-copy dump, draw log) to attribute the squares to texture decode, memory addressing, EFB-copy handling or TEV; all four are hypotheses.

## RESOLVED 2026-11-23: GX texture-coordinate scale ignored
- Cause: the pixel shader scaled every stage's coordinate by the bound texture's size (`shadergen.cpp`
  `tc = uv * u_texsize[map]`) and never read SU_SSIZE/SU_TSIZE (bp[0x30+2c], bp[0x31+2c], low 16 bits =
  scale-1). The game sets them itself: for the building-transparency stipple masks (textures 103-106,
  I4 16x16, ordered-dither alpha masks of 94/88/75/50% density, correct data) it sets 640x448 on a
  screen-normalised texgen, i.e. one texel per screen pixel; we mapped the mask once across the screen.
- Ruled out on the way: texture decode (correct), stale data (static, decoded once), TEV/alpha test
  (alpha>127 AND alpha>127, stage1 = CPREV*TEXC / APREV*TEXA, correct), texgen matrices (match the game).
- Fix (gcn-recomp, uncommitted): per-texcoord uniform `u_tcscale[8]` from bp[0x30..0x3F] in `render_gl.cpp`;
  `shadergen.cpp` uses it for non-substituted stages (eye-grab substituted stages keep texture size).
  Sampler 64-bit key fix is kept (separate, valid defect). Developer visual test: checkerboard gone,
  fine stipple, player visible through buildings.
- Scale register values seen at frame 1650 (texcoord 1): 128x128 (1194 draws), 640x448 (85), 320x224 (66).
- Not verified: Dolphin side-by-side; title/UI text, memory-card save and REL scenes after the change (L1);
  other scenes where scale != texture size now render differently (as on hardware). Debug prints
  (GCN_TGLOG in xf.cpp, [TMPDBG] in boot.cpp) removed.
