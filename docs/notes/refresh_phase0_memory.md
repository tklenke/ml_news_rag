# Annual refresh, Phase 0: memory measurements

See `docs/plans/annual_refresh_plan.md` 0.6.

Measured by the Programmer on 2026-11-21 at Tom's request, before the Phase 0 deploy; the 882
against 806 MiB first reported for the rehearsal were single readings. Method: both stacks on copies of the 1.1.1 backup,
2 CPUs, sampled at 10 Hz through startup, first question, ten in turn and eight at once,
each with a revise, model calls faked. Peak anonymous memory, MiB:

| | chroma | ollama | flask | peak of the sum |
|---|---|---|---|---|
| old stack | 162 | 316 | 313 | 790 |
| new stack, 4 workers (3 runs) | 166 to 168 | 413 to 431 | 320 to 323 | 900 to 919 |
| new stack, 2 workers (1 run) | 166 | 412 | 172 | 750 |

- The increase is Ollama, mostly its server process (120 anonymous against 26 MiB).
  `GOMEMLIMIT=64MiB` with `OLLAMA_NUM_PARALLEL=1` made no difference.
- The 1.5.9 first start on 1.1.1 data showed no memory spike.
- Not measured: the server itself, the image build, and real model calls.
- Server, old stack, 2 CPUs, no swap, 1941 MB (Tom, 2026-11-21): available 774 MB with the
  model unloaded, 518 MB just after a question. `docker stats` then: flask 431, ollama 476,
  chroma 167, php 34 and 9, nginx 9 MiB. No out-of-memory lines in `dmesg`.
- Estimate for the new stack just after a question, from those readings and the local
  differences: about 400 MB available with 4 workers, about 570 with 2. It fits either way.
- With the stack stopped for the build, only about 300 MB is in use.
- Tom decided (2026-11-21): 2 gunicorn workers (two questions processed at once rather than
  four; `server/gunicorn.conf`) and a 2 GB swap file on the server.
- One `docker stats` reading of Ollama was 630 MiB. Not reproduced: 411 to 426 MiB anonymous
  in every later run. A cold file cache adds about 260 MiB, which the kernel can reclaim; that
  is the likely explanation, not a proven one.
- Server after the deploy (2026-11-21), new stack, 2 workers, model loaded: 771 MiB
  available.
