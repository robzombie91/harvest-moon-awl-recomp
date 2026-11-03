# Harvest Moon: A Wonderful Life — GameCube native recompilation (WIP)

Experimental native Linux recompilation of **Harvest Moon: A Wonderful Life** (Nintendo GameCube, North American release, disc ID **GYWEE9**) using [gcn-recomp](https://github.com/robzombie91/gcn-recomp/tree/harvest-moon-fixes).

## Status

- The game launches and runs natively on CachyOS Linux.
- Dynamic REL modules are supported in the working local build.
- Memory-card saving works in the working local build.
- **Major known issue:** checkerboard graphics corruption on a building and nearby trees in the outdoor scene. Dolphin Emulator renders the same scene correctly.
- **Not a finished or independently verified portable release.** No prebuilt binaries are provided.

The project is under active investigation. The modified renderer and runtime are preserved in the linked **gcn-recomp** fork, at the submodule commit pinned by this repository.

## Known graphics issue

The corruption has been observed **inside the emulated embedded framebuffer (EFB)**, before window presentation. Draw isolation works. More aggressive texture-cache hashing did not fix it.

The game issues GX manual texture-preload commands (BP registers `0x60`–`0x63`), but the experimental native implementation does not fully reproduce GameCube TMEM placement or bank semantics. **TMEM is a hypothesis, not a confirmed root cause.** Other areas under investigation include EFB-copy texture resolution, tiled texture decoding, and TEV shader generation.

A Dolphin FIFO capture (`test.dff`) was collected as a reference, but it contains game data and is **not distributed** here.

## Source layout

- `CMakeLists.txt`: native project definition and REL-module configuration
- `gcn-recomp/`: submodule pinned to the modified runtime
- `recomp/`: recompilation configuration tables
- `analysis/`: non-binary analysis configuration and split maps
- `harvest_rel_seed.py`: heuristic initial symbol-candidate generation for REL modules

## Reproducing locally

A fresh checkout requires a matching, **legally obtained** GameCube disc dump and game-specific generated analysis inputs. This repository deliberately does not contain original game binaries, extracted RELs, texture dumps, symbol maps, saves, or FIFO captures.

Clone with submodules:

```sh
git clone --recurse-submodules https://github.com/robzombie91/harvest-moon-awl-recomp.git
cd harvest-moon-awl-recomp
```

**Important:** Before configuring CMake, provide the game's own `rom/main.dol`, `wlp0.rel`, `wlp1.rel`, `wlp2.rel` and corresponding symbol data from your own dump. The project references `analysis/symbols.txt` and `analysis/rel-symbols/`, which are intentionally absent from the repository. Exact extraction and regeneration instructions are not yet complete. Do not expect a clean clone to build out of the box.

Development environment used: CachyOS Linux, Clang, CMake and Ninja. Once the required game-specific inputs are available, the existing local build uses CMake/Ninja and produces `build-rel/hmawl`. Build success on a different system has **not** been independently confirmed.

## Debugging

The modified renderer includes optional instrumentation: `GCN_DRAWLOG`, `GCN_DRAWLOG_VERBOSE`, `GCN_DRAW_SKIP`, `GCN_PIXEL`, and related EFB-copy diagnostics. See [the GX debug overlay notes](https://github.com/robzombie91/gcn-recomp/blob/harvest-moon-fixes/docs/gx-debug-overlay.md).

Please prefer source-level evidence and isolated, reversible fixes. Preserve working memory-card and REL functionality and avoid treating incomplete TMEM support as a proven explanation for the checkerboard.

## Legal

This is an unofficial research/development project and is not affiliated with or endorsed by the game publisher, Nintendo, or Dolphin Emulator. No original game assets are provided. Users must supply their own legitimately obtained game files.
