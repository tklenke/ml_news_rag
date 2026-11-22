# Architect Todo

**Last Updated:** 2026-11-21

Active workstream: the annual RAG / website refresh. The plan is
`annual_refresh_plan.md`; read it first. The finished image database work is in
`docs/archive/architect_todo_image_database.md`.

## Resume point

Plan revised on 2026-11-21 (fourth revision). Phase 0 is deployed. The Programmer's notes
of 2026-11-21 are all decided and folded into the plan; none are outstanding. Next is the
Programmer's Phase 1 code change (1.0, 1.1, S1, S2, S4, S5, S6, S10, S11), one deploy, with
a code review before it.

## Open

- [ ] Approve the nginx rate Programmer proposes for S2b.
- [ ] If the evaluation shows a candidate failing or too slow at its default reasoning
      effort: read OpenAI's documentation for the reasoning setting and take the question
      of a `site.ini` setting to Tom (plan 1.3).
- [ ] Have `ml/requirements.txt` created when Phase 2 adds tests to `embedder/` (the
      role files tell every session to read it; it does not exist).
- [ ] Design reference links (plan 4.1) and image gallery (4.2) once the model choice is known.

## Notes from Programmer

None outstanding.

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
- [x] Programmer's five notes after the Phase 0 deploy decided and folded into the plan
      (fourth revision, 2026-11-21; default reasoning effort approved by Tom, D24): the restart exception in `sudo_renew_cert.sh`
      confirmed (0.2); smoke-call report reviewed, models evaluated at their default
      reasoning effort with reasoning tokens recorded (0.7, 1.3, 1.4); deploy facts and
      memory measurements recorded (0.6, 0.8, D22, D23,
      `docs/notes/refresh_phase0_memory.md`); the empty job file read designed as S11.

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
- The server runs `main` at `bed83f4`, delivered by `git pull`. The state before Phase 0
  (`906ffd8` plus a stash) is kept there as the rollback until the server cleanup
  (`programmer_todo.md`).
- The server has 1.9 GiB of memory, 2 CPUs, a 2 GB swap file, Docker 29.10.0 and Compose
  5.8.0. gunicorn runs 2 workers. With the model loaded, 771 MiB is available. 36 GB of
  disk was free before the Phase 0 deploy.
- The site stays down after a server reboot until `docker compose up -d` is run (open
  with Tom in `required_from_tom.md`).
- `ml/docker-compose.yaml` mounts `../site_2024/data/chroma`, the same directory the
  site's Chroma uses locally. Both compose files must name the same Chroma version.
- Local Chroma data has been opened by 1.5.9. The 1.1.1 backup is
  `site_2024/data/chroma_backup_1.1.1`; rehearsal baseline and probe script are in
  `site_2024/data/rehearsal/`. Both old images are kept locally under the tag `old-stack`.
- The copy of `server/nginx_all_apps.conf` in the reference file lost trailing spaces in
  pasting. The committed file is the exact one.
- The live certificate expires 2027-02-20.
