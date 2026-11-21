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
