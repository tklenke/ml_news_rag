# Programmer Todo

**Last Updated:** 2026-11-21

# ACTIVE: Annual RAG / Website Refresh

**READ FIRST: `docs/plans/annual_refresh_plan.md`.** Read the whole document before any
task, every session. The tasks below are only a checklist; section numbers refer to the plan.

**Branches:** `wip/annual-refresh` in `ml/` and in `../site_2024/` (exists, no commits yet).

**Order:** Phase 0, then the code change (Phase 1.0 to 1.1 with S1, S2, S4, S5, S6), then
the evaluation (1.3 to 1.6). Phase 2 can overlap the evaluation. One session per group;
start each session fresh. Code review happens once per deploy, not per commit.

All code tasks follow TDD. Escalate design questions to Architect; do not resolve them yourself.

The finished image database tasks are in `docs/archive/programmer_todo_image_database.md`.

## Phase 0: Infrastructure refresh (repo: `../site_2024/`, one deploy)

Blocked until Tom has enabled Docker's WSL integration and provided the four untracked
server files (`required_from_tom.md`). If Docker cannot be enabled, stop and tell Architect.

- [ ] 0.2a Make `server/nginx_all_apps.conf` and the `cgimages` mount in
      `docker-compose.yaml` match production (text in
      `docs/references/site_2024_production_state_2026-11-21.md`). Commit this alone.
- [ ] 0.2b Add the untracked server files Architect says to track.
- [ ] 0.3a Remove DokuWiki: both nginx `location` blocks, `php1`, `php2`, their
      `depends_on` entries, both volume mounts, the README mention.
- [ ] 0.3b Bind the published ports for flask, chroma and ollama to `127.0.0.1`.
- [ ] 0.3c Pin `nginx` and `ollama/ollama` to a current stable version tag.
- [ ] 0.4a `flask.dockerfile` on `python:3.13-slim`.
- [ ] 0.4b Requirements: a file of direct dependencies only, resolved and frozen into
      `requirements.txt`; test packages in a separate file not installed in the image.
- [ ] 0.5a Chroma server image to the plan's target version in `site_2024` **and** in
      `ml/docker-compose.yaml` (same data directory).
- [ ] 0.5b Replace `chromadb` with `chromadb-client` at the same version.
- [ ] 0.6 Local rehearsal per plan 0.6. Copy `data/chroma` first. Report the results to
      Architect before any deploy.
- [ ] 0.7 Smoke call to each candidate model and both current models on the upgraded
      OpenAI SDK; fix the call sites if the SDK changed them. Report to Architect.
- [ ] 0.8 Deploy with Tom per plan 0.8.

## Phase 1 code change and site fixes (repo: `../site_2024/`, one deploy)

- [ ] 1.0 Set up pytest in `site_2024` (it has no tests today)
- [ ] 1.1a Separate prompt construction from `process_question` into a function that takes
      job data and document lists and returns the prompt string. Behaviour unchanged.
- [ ] 1.1b Write a failing test for the suspected defect: revise and follow-up prompts must
      contain the full text of every prior document. Use a real `collection.get()` result
      from the local Chroma service, not a hand-built dict. If the test passes without a
      code change, the suspicion is wrong: note it in `architect_todo.md` and skip the fix.
- [ ] 1.1c Fix the prior-context join if 1.1b failed
- [ ] 1.1d Reword `revise_prompt` and `followup_prompt` so they name no model
- [ ] 1.1e Ask Tom before fixing or removing the stale `__main__` block in
      `llm_functions.py` (it passes a string to `process_question` and calls
      `set_docs_params` with three arguments)
- [ ] S1a Function that shortens an email address for display: first 5 characters plus
      `...`; empty string for none. Replaces the `safe_truncate(job['email'],5)` calls.
- [ ] S1b `/cozyrag/<id>/status` returns only `status`, `status_text`, `result_html`.
      Check `cozyrag_answer.html` still works; it reads only those three.
- [ ] S1c Results page and jobs page (including `/cozyrag/jobs/email`) show the shortened
      address only, applied where the job record is prepared for display.
- [ ] S1d Tests: with a job file containing a known full address, that address appears in
      none of the responses from `status`, `processid`, `jobs`, `jobs/email`.
- [ ] S2a `/cozyrag/revise` accepts POST only; a GET gets 405.
- [ ] S2b nginx `limit_req` for `/cozyrag/query` and `/cozyrag/followup`. Propose the rate
      to Architect before deploying.
- [ ] S4 `sanitize()` no longer wraps input in `Markup`. Rename it to say what it does, or
      remove it if nothing remains; ask Architect if unsure.
- [ ] S5a Unknown job id on `processid` and `status` returns 404, not 500.
- [ ] S5b `/cozyrag/jobs/<unknown column>` returns 404 (`abort` is not imported today).
- [ ] S5c `revise`, `followup`, `feedback` and `answer` without a session redirect to the
      question form instead of returning 500.
- [ ] S6 Feedback accepts only `perfect`, `ok`, `not_good`; anything else is ignored with
      a redirect to the question form.
- [ ] Deploy: `git pull` on the server, rebuild if requirements changed, restart.

Flask's test client is enough for the S tasks; only 1.1b needs a live service.

## Phase 1 evaluation (repo: `../site_2024/`)

- [ ] 1.3 Evaluation harness: reads `refresh_questions.csv`, retrieves once per question,
      sends the same documents to each model, records answer, tokens, latency, cost
- [ ] 1.4 Capture the baseline with the current models (they shut down 2027-01-14)
- [ ] 1.5 Produce the blind review files and key file (plan 1.4) for Tom to rate, one batch
      of 10 questions at a time, with a per-tier tally after each batch (plan 1.5)
- [ ] 1.6 After Tom's decision: update `site.ini` and `site.ini.template`

Questions: `docs/plans/refresh_questions.csv`, rows whose `use` is `batch1`, `batch2`,
`batch3`, in that order.

## Phase 2: Chunk-size experiment (repo: `ml/`)

Start after Phase 0 is deployed, so the variant collections are built on the upgraded
Chroma. Check that the `chromadb` client in the `ml` venv works with that server first.

- [ ] 2.1a Tests for `chunksplitter` covering current behaviour
- [ ] 2.1b Failing test, then fix: no prefix-only chunk when the word count is an exact
      multiple of the chunk size, or for an empty file
- [ ] 2.1c Add overlap to `chunksplitter` (default 0 reproduces current chunks)
- [ ] 2.1d `embedder.py` takes chunk size, overlap and collection name as parameters,
      with a progress file per collection
- [ ] 2.2 Embed variant B on the full corpus and report the time taken before running C, D, E
- [ ] 2.3 Pooling: write `chunk_labels.csv` for Tom, one batch of 10 questions at a time (plan 2.3)
- [ ] 2.4 Scoring: compute the four metrics per variant from Tom's labels, rerun after
      each batch (plan 2.4)
- [ ] 2.5 Question set is the three batches plus the `chunk_only` rows of
      `refresh_questions.csv` (40 questions, plan 2.3). `reserve` rows are not used unless
      Architect says so.

## Phase 4 (not yet designed)

- [ ] S3 Sanitise rendered answer HTML with an allow-list before it is marked safe.
      Wait for the reference-links design; it decides which tags and link targets are allowed.
