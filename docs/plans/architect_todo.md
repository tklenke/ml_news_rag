# Architect Todo

**Last Updated:** 2026-11-21

Active workstream: the annual RAG / website refresh. The plan is
`annual_refresh_plan.md`; read it first. The finished image database work is in
`docs/archive/architect_todo_image_database.md`.

## Resume point

Plan revised on 2026-11-21 (second revision): Phase 0 (infrastructure refresh) added,
work reordered so nothing is built, tested or deployed twice, todo files trimmed.
Programmer starts at Phase 0 once Tom has done the two items at the top of
`required_from_tom.md`.

## Open

- [ ] Confirm with Tom the three points assumed in Phase 0 (plan "Assumed, to confirm"):
      wiki data is tarred and kept with no redirects; delivery is `git pull` on the
      server; Docker WSL integration can be enabled.
- [ ] Decide which of the four untracked server files are tracked, once Tom provides them
      (plan 0.2).
- [ ] Review Programmer's rehearsal report before the Phase 0 deploy (plan 0.6). If Docker
      cannot be enabled locally, split the Chroma upgrade into its own deploy.
- [ ] Review Programmer's smoke-call report on the GPT-6 candidates (plan 0.7, 1.3).
- [ ] Review Programmer's finding on the suspected revise-context defect (plan 1.1).
- [ ] Approve the nginx rate Programmer proposes for S2b.
- [ ] Have `ml/requirements.txt` created when Phase 2 adds tests to `embedder/` (the
      role files tell every session to read it; it does not exist).
- [ ] Design reference links (plan 4.1) and image gallery (4.2) once the model choice is known.

## Notes from Programmer

**NOTE FROM PROGRAMMER (2026-11-21):** findings from the Phase 0 startup checks. The plan
is not edited; these need Architect decisions.

- **Plan 0.8 step 3, `git pull` aborts.** `exclude_from_tar.txt` is tracked on `main` since
  `63cca77` but untracked on the server, which is at `906ffd8`. A plain `git stash` leaves
  untracked files, so the pull refuses to overwrite it (reproduced in a scratch clone). The
  text of the two copies is the same. The server copy must be moved aside first, and so
  must any other untracked server file the repo starts tracking.
- **Plan 0.2, untracked files.** `old.nginx_all_apps.conf` is the production config
  without `/cgimages/`; suggest not tracking. `test_08_fixture/` is 41 generated
  wiring-diagram files (SVG, BOM, HTML), unrelated to CozyRAG; suggest not tracking, and
  asking Tom whether it should be publicly served. `exclude_from_tar.txt` has a typo:
  `dokuN667CZ` should be `dokuN657CZ`.
- **`sudo_renew_cert.sh` fails at step 5.** It copies `fullchain.pem` and `privkey.pem` from
  `archive/m24tom.com-NNNN/`, where every file is numbered (`fullchain1.pem`,
  `fullchain2.pem`), after deleting the live copies, and does not stop on error. It also
  has to pick the highest number: `-0010` holds both 1 and 2, and 2 is the latest. The live
  certificate expires 2027-01-26. Suggest fixing it before tracking it.
- **Draft context is 14 chunks at most, not 15.** `get_num_draft_docs` returns the index of
  the last chunk inside the cutoff, and the caller uses it as a count, so that chunk is
  dropped (60 close matches return 14). Plan 2.4 assumes 15. Decide before the 1.4 baseline.
- **`[PROMPTS]` `INITIAL` and `SECONDARY` in `site.ini` have no effect.** `process_question`
  uses the module constants, not the values given to `set_prompts`.
- **`site.ini.template` has `LLM`**, but the app reads `LLM_DRAFT` and `LLM_REVISE`.
- **`server/nginx_all_apps.conf` in the reference file lost trailing spaces** in pasting.
  The committed file is the exact one.

## Completed

- [x] Tom's four opening questions answered; plan, `required_from_tom.md` and task
      breakdown written (2026-11-21).
- [x] Question set: 52 approved by Tom, in `refresh_questions.csv` with a `use` column.
- [x] Website refresh scoped: reference links and images only (plan Phase 4).
- [x] `site_2024` code and live server reviewed; findings S1 to S9 (plan Phase 3).
- [x] Checkpoints at 10 / 20 / 30 questions (plan 1.5); chunk question set (plan 2.3).
- [x] `docs/notes/opportunities_for_improvement.md` created (S8, housekeeping).
- [x] Decided the Programmer's handoff items A to D (2026-11-21): dependency refresh
      (plan Phase 0), DokuWiki removal (0.3), config delivery (0.2, 0.8), published
      ports (0.3). Tom's verbatim server outputs moved to
      `docs/references/site_2024_production_state_2026-11-21.md`.
- [x] Scanned Chroma release notes 1.2.2 to 1.5.9 for storage or breaking changes
      (result in plan 0.5).
- [x] Finished image database sections of both todo files moved to `docs/archive/`
      with Tom's approval.

## Facts worth keeping

- The refresh spans two repositories: `ml/` (chunking, embedding, image database) and
  `../site_2024/` (retrieval, prompts, LLM calls, pages, deployment). See the plan.
- Production RAG settings (`site_2024/fwww/site.ini`): `EMBED = nomic-embed-text`,
  `PREFIX = search_query:` (documents are embedded with `search_document:`; the
  asymmetry is correct), `LLM_DRAFT = gpt-4o-mini`, `LLM_REVISE = gpt-4.1`,
  `MAX_DISTANCE = .35`, `MIN_DOCUMENTS = 5`, `MAX_DOCUMENTS = 60`,
  `MAX_DRAFT_DOCUMENTS = 15`.
- `ml/asker/` and `ml/modelTesting/` are stale harnesses that query an `all-minilm`
  collection. They are not the production path.
- Production job log (2026-11-21): about 850 questions, about 45 rated (roughly 20 of
  those `n/a`; the scale changed over time). Typical first answer: about 4,500 tokens
  in, 300 out, 5 s. A sampled follow-up: about 21,000 tokens in.
- The server checkout is at `906ffd8` with uncommitted edits; its code is byte-identical
  to the repo's `main`, only `server/nginx_all_apps.conf` and `docker-compose.yaml` differ.
- `ml/docker-compose.yaml` mounts `../site_2024/data/chroma`, the same directory the
  site's Chroma uses locally. Both compose files must name the same Chroma version.
