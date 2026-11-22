# Architect Todo

**Last Updated:** 2026-11-21

Active workstream: the annual RAG / website refresh. The plan is
`annual_refresh_plan.md`; read it first. The finished image database work is in
`docs/archive/architect_todo_image_database.md`.

## Resume point

Plan revised on 2026-11-21 (third revision). The Phase 0 rehearsal passed and is
approved. Programmer finishes Phase 0 (tasks 0.2b, 0.2c, 0.4c, 0.6b), then code review, then
the deploy with Tom. The Programmer's notes of 2026-11-21 are all decided and folded
into the plan; none are outstanding.

## Open

- [ ] Review Programmer's smoke-call report on the GPT-6 candidates once Tom has
      arranged access (plan 0.7, 1.3). All four returned 403 on 2026-11-21.
- [ ] Approve the nginx rate Programmer proposes for S2b.
- [ ] Have `ml/requirements.txt` created when Phase 2 adds tests to `embedder/` (the
      role files tell every session to read it; it does not exist).
- [ ] Design reference links (plan 4.1) and image gallery (4.2) once the model choice is known.

## Notes from Programmer

**NOTE FROM PROGRAMMER (2026-11-21):** 0.2b, 0.2c, 0.4c and 0.6b are done; results are in
`programmer_todo.md`. Please confirm one choice in 0.2c: a failed `docker compose restart`
in `sudo_renew_cert.sh` continues to the rollback question, although plan 0.2 says to stop at
the first error.

**NOTE FROM PROGRAMMER (2026-11-21):** Smoke calls (0.7) repeated: all four candidates answer
the production `chat.completions` call unchanged, so the review item above can proceed and plan
0.7 and 1.3 need updating. On a one-sentence question two candidates spent hidden reasoning
tokens, reported inside `completion_tokens`: `gpt-6-luna` 50 of 80, `gpt-6.1-terra` 34
of 72. The current models, `gpt-6.2-sol` and `gpt-6.2-astra` spent none. One sample each,
short prompt. The plan does not say whether reasoning effort is left at the default or set
(1.3), nor that the harness records reasoning tokens separately (1.4).

**NOTE FROM PROGRAMMER (2026-11-21):** Memory measured again at Tom's request; the 882 against
806 MiB in plan 0.6 were single readings. Method: both stacks on copies of the 1.1.1 backup,
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
- Decision wanted: 2 gunicorn workers (two questions processed at once rather than four),
  and a swap file on the server. Waiting on server readings from Tom.

**NOTE FROM PROGRAMMER (2026-11-21):** One 500 from `/status` in these runs: the job file was read
as empty, so `get_process_info` returned `{}` and `cozyrag_status` raised `KeyError: 'created'`.
The polling page stops on that, so the visitor keeps seeing "Running Query". Opening with
`"w"` empties the file before the lock can be held; not yet reproduced in a test. The same
read in `update_process_status` would save the job without its question. Existing code, not
caused by Phase 0; not in S1 to S10. Suggest it joins the Phase 1 code change.

## Completed

- [x] Plan, question set (52 in `refresh_questions.csv`), site review (S1 to S9) and
      task breakdown (2026-11-21).
- [x] Phase 0 designed: dependency refresh, DokuWiki removal, config delivery, published
      ports; Chroma release notes 1.2.2 to 1.5.9 scanned (2026-11-21).
- [x] Rehearsal report reviewed and the Phase 0 deploy approved (2026-11-21).
- [x] Untracked server files decided (plan 0.2); deploy steps rewritten (plan 0.8).
- [x] Programmer's findings decided: draft context fixed to 15 (D20), dead `[PROMPTS]`
      settings removed (1.1), unused dependencies dropped (0.4), revise-context defect
      confirmed (1.1).
- [x] Key handling reviewed at Tom's request; design S10 (D21).
- [x] Tom's decisions D17 to D21 recorded in the plan and `required_from_tom.md`.

## Facts worth keeping

- The refresh spans two repositories: `ml/` (chunking, embedding, image database) and
  `../site_2024/` (retrieval, prompts, LLM calls, pages, deployment). See the plan.
- Production RAG settings (`site_2024/fwww/site.ini`): `EMBED = nomic-embed-text`,
  `PREFIX = search_query:` (documents are embedded with `search_document:`; the
  asymmetry is correct), `LLM_DRAFT = gpt-4o-mini`, `LLM_REVISE = gpt-4.1`,
  `MAX_DISTANCE = .35`, `MIN_DOCUMENTS = 5`, `MAX_DOCUMENTS = 60`,
  `MAX_DRAFT_DOCUMENTS = 15`.
- `site.ini` holds real keys until S10 is done. Read settings from it with a pattern
  that names the setting; never print the file.
- `ml/asker/` and `ml/modelTesting/` are stale harnesses that query an `all-minilm`
  collection. They are not the production path.
- Production job log (2026-11-21): about 850 questions, about 45 rated (roughly 20 of
  those `n/a`; the scale changed over time). Typical first answer: about 4,500 tokens
  in, 300 out, 5 s. A sampled follow-up: about 21,000 tokens in.
- The server checkout is at `906ffd8` with uncommitted edits; its code is byte-identical
  to the repo's `main`, only `server/nginx_all_apps.conf` and `docker-compose.yaml` differ.
  The server has 1.9 GiB of memory, no swap, and 36 GB of disk free.
- `ml/docker-compose.yaml` mounts `../site_2024/data/chroma`, the same directory the
  site's Chroma uses locally. Both compose files must name the same Chroma version.
- Local Chroma data has been opened by 1.5.9. The 1.1.1 backup is
  `site_2024/data/chroma_backup_1.1.1`; rehearsal baseline and probe script are in
  `site_2024/data/rehearsal/`. Both old images are kept locally under the tag `old-stack`.
- The copy of `server/nginx_all_apps.conf` in the reference file lost trailing spaces in
  pasting. The committed file is the exact one.
- The live certificate expires 2027-01-26.
