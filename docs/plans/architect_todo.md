# Architect Todo

**Last Updated:** 2026-11-21

Active workstream: the annual RAG / website refresh. The plan is
`annual_refresh_plan.md`; read it first. The finished image database work is in
`docs/archive/architect_todo_image_database.md`.

## Resume point

Plan revised on 2026-11-21 (fifth revision: S2 without the nginx rate limit, D25). Phase 0
is deployed. The Phase 1 code change is written and not deployed. Its deploy waits for the
two open questions below, the paid local run and the code review (`programmer_todo.md`).

## Open

- [ ] Prior context for revise and follow-up (Programmer's note below): do the related
      documents belong in it, and does the job record keep every chunk the draft saw?
      Architect's recommendation is with Tom. The answer sets the revise baseline (1.2).
- [ ] The missing space after `search_query:` (Programmer's note below): leave, fix, or
      measure in Phase 2. With Tom.
- [ ] If the evaluation shows a candidate failing or too slow at its default reasoning
      effort: read OpenAI's documentation for the reasoning setting and take the question
      of a `site.ini` setting to Tom (plan 1.3).
- [ ] Have `ml/requirements.txt` created when Phase 2 adds tests to `embedder/` (the
      role files tell every session to read it; it does not exist).
- [ ] Design reference links (plan 4.1) and image gallery (4.2) once the model choice is known.

## Notes from Programmer

**NOTE FROM PROGRAMMER (2026-11-21):** Two facts about the corrected prior context (1.1c), measured
on the 16 local job files with a first answer:

- A revise prompt goes from about 5,000 characters (one garbled chunk) to 33,000 to 68,000 for the
  jobs with 60 retrieved chunks. The context is every provided and related document, as the code
  always intended. Each "dig deeper" costs and takes correspondingly more; follow-ups carry
  this context plus 60 new chunks. The evaluation (1.4) will show the cost.
- Job records keep one chunk per source (`dedupe_list_of_docs`), and revise fetches by those ids.
  Where several chunks came from one source, the draft model saw chunks the revise model does not:
  14 chunks became 9 to 14 ids, 19 became 12. Not changed; it is a design question whether the
  record should keep every chunk id.

Question for Architect: should the revise and follow-up context include the related documents, and
should it hold every chunk the draft saw? Either answer changes the revise baseline (1.2).

**NOTE FROM PROGRAMMER (2026-11-21):** `PREFIX = search_query:` reaches the embedder without a space
before the question ("search_query:how many"), while documents are stored with one
("search_document: Canard"). The ini parser drops trailing spaces. Unchanged (D7); recorded because
Phase 2 measures retrieval.

## Completed

Phase 0 and the four plan revisions of 2026-11-21 are done: planning, question set, site
review, Phase 0 design and deploy approval, decisions D1 to D24, and the Programmer's notes
through the deploy. The item list is in the git history of this file.

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
- The live certificate expires 2027-02-20.
