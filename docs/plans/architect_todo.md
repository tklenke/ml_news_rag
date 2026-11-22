# Architect Todo

**Last Updated:** 2026-11-22

Active workstream: the annual RAG / website refresh. The plan is
`annual_refresh_plan.md`; read it first. The finished image database work is in
`docs/archive/architect_todo_image_database.md`.

## Resume point

Plan revised on 2026-11-21 (sixth revision: D25 to D27; D28 added 2026-11-22). Phase 0 and
the Phase 1 code change are deployed (`3278e9e`). Next for the Programmer is the evaluation
(1.3 to 1.6), with Phase 2 overlapping. Waiting on Architect: the two questions from the
Programmer under "Open", each of which needs Tom's decision.

## Open

- [ ] Follow-up, additional content (plan 1.1 item 8): the plan does not say whether a chunk
      already in the previous content is left out. Built as written: sent in both places,
      recorded once (6 and 5 of 15 in the paid run). Take to Tom, then state it in the plan.
- [ ] Job thread: any exception in `run()` ends it, and that worker answers nothing until a
      restart. One cause is fixed; Chroma or Ollama being unreachable would do the same (read
      from the code, not tried). Take to Tom: fix now or leave with S8.
- [ ] If the evaluation shows a candidate failing or too slow at its default reasoning
      effort: read OpenAI's documentation for the reasoning setting and take the question
      of a `site.ini` setting to Tom (plan 1.3).
- [ ] Have `ml/requirements.txt` created when Phase 2 adds tests to `embedder/` (the
      role files tell every session to read it; it does not exist).
- [ ] Design reference links (plan 4.1) and image gallery (4.2) once the model choice is known.

## Notes from Programmer

The notes of 2026-11-21 on the prior context and the `PREFIX` space are answered in plan 1.1
(items 6 to 8, and "Checked and left alone").

The note of 2026-11-21 on the Phase 1 deploy is taken up: the deploy and the waived review are
in the plan (status line, D28), and its two questions are under "Open".

## Completed

Phase 0 and the four plan revisions of 2026-11-21 are done: planning, question set, site
review, Phase 0 design and deploy approval, decisions D1 to D24, and the Programmer's notes
through the deploy. The item list is in the git history of this file.

## Facts worth keeping

- The refresh spans two repositories: `ml/` (chunking, embedding, image database) and
  `../site_2024/` (retrieval, prompts, LLM calls, pages, deployment). See the plan.
- Production RAG settings (`site_2024/fwww/site.ini`): `EMBED = nomic-embed-text`,
  `PREFIX = search_query:` (documents are embedded with `search_document:`; the
  asymmetry is correct, and the missing space after the colon changes nothing: plan 1.1), `LLM_DRAFT = gpt-4o-mini`, `LLM_REVISE = gpt-4.1`,
  `MAX_DISTANCE = .35`, `MIN_DOCUMENTS = 5`, `MAX_DOCUMENTS = 60`,
  `MAX_DRAFT_DOCUMENTS = 15`.
- `site.ini` holds real keys until S10 is done. Read settings from it with a pattern
  that names the setting; never print the file.
- `ml/asker/` and `ml/modelTesting/` are stale harnesses that query an `all-minilm`
  collection. They are not the production path.
- Production job log (2026-11-21): about 850 questions, about 45 rated (roughly 20 of
  those `n/a`; the scale changed over time). Typical first answer: about 4,500 tokens
  in, 300 out, 5 s. A sampled follow-up: about 21,000 tokens in.
- The server runs `main` at `3278e9e`, delivered by `git pull`. The rollbacks to `bed83f4`
  and to the state before Phase 0 (`906ffd8` plus a stash) are kept there until the server
  cleanup (`programmer_todo.md`).
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
- The live certificate expires 2027-02-20.
