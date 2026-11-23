## gx-checkerboard-status

---
name: gx-checkerboard-status
description: Where the GX checkerboard investigation stands; record lives in docs/dev/gx-checkerboard-investigation.md
metadata:
  type: project
---
As of 2026-11-22 a sampler-cache key collision fix (gcn-recomp render_gl.cpp get_sampler) is uncommitted and NOT runtime-verified; this checkout lacked game inputs to build. Full notes: docs/dev/gx-checkerboard-investigation.md.
**Why:** avoid redoing the source audit. **How to apply:** next session starts by building with game inputs and A/B testing the fix.
