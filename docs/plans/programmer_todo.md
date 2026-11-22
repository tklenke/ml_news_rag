# Programmer Todo

**Last Updated:** 2026-11-21

# ACTIVE: Annual RAG / Website Refresh

**READ FIRST: `docs/plans/annual_refresh_plan.md`.** Read the whole document before any
task, every session. The tasks below are only a checklist; section numbers refer to the plan.

**Branches:** `wip/annual-refresh` in `ml/` and in `../site_2024/`.

**Order:** Phase 0, then the code change (Phase 1.0 to 1.1 with S1, S2, S4, S5, S6, S10), then
the evaluation (1.3 to 1.6). Phase 2 can overlap the evaluation. One session per group;
start each session fresh. Code review happens once per deploy, not per commit.

All code tasks follow TDD. Escalate design questions to Architect; do not resolve them yourself.

The finished image database tasks are in `docs/archive/programmer_todo_image_database.md`.

## Phase 0: Infrastructure refresh (repo: `../site_2024/`, one deploy)

Done and committed on `wip/annual-refresh`: 0.2a (config matches production), 0.3a to 0.3c
(DokuWiki removed, ports on `127.0.0.1`, nginx `1.30.7`, ollama `0.40.17`), 0.4a and 0.4b
(Python 3.13, resolved requirements), 0.5a and 0.5b (Chroma 1.5.9, `chromadb-client`),
0.6 (rehearsal passed; Architect approved the deploy).

- [x] 0.2b `exclude_from_tar.txt`: remove the `dokucozy` and `dokuN667CZ` lines, add
      `fwww/site.ini`. Checked with a tar listing: `site.ini` was in the tar before the
      edit and is not after it; `site.ini.template` still is.
- [x] 0.2c `sudo_renew_cert.sh` fixed to the behaviour in plan 0.2 and tracked.
      `tests/test_sudo_renew_cert.py` (15 tests) runs it in a scratch directory laid out
      like the server; docker is a stand-in command, the file operations are real. 11
      of the 15 failed on the script as it is on the server. Two things beyond plan 0.2:
      it also used a relative archive path after changing directory, so the copy failed
      whatever the file names; and a failed `docker compose restart` does not stop the
      script, because stopping there would skip the question that offers the rollback.
- [x] 0.4c Remove `Flask-Markdown` and `python-dotenv` from `requirements_direct.txt` and
      freeze `requirements.txt` again. Frozen in a clean Python 3.13 venv: the only change is
      that `Flask-Markdown` is gone. `python-dotenv` stays in `requirements.txt` because
      `pydantic-settings` (needed by `chromadb-client`) requires it.
- [x] 0.6b Rebuild the flask image after 0.4c and answer one question locally through
      the app; `pip check` clean; no errors in the logs. Passed 2026-11-21 (Q01, 3.6 s).
      The logs held one error, a 500 from `/cozyrag/answer` without a question in the
      session (S5c, sent by mistake while testing), and two warnings: gunicorn wants its
      config file to have a `.py` extension, and Ollama reports the requested context
      (8192) exceeds the model's 2048.
- [~] Remove the empty stray directory `site_2024/home/`. Cause found: commit `42db312`
      mounted the relative path `./home/admin/www/cgimages`, so Docker created it as root;
      the mount is absolute since `65764e2`, so nothing uses it. Needs `sudo`: Tom removes
      it (command in `required_from_tom.md`).
- [~] 0.7 Smoke calls. Current models work with no call-site change. All four candidates
      return 403; rerun when Tom says access is enabled, and report to Architect.
      The deploy does not wait for this.
- [ ] 0.8 Deploy with Tom, following plan 0.8 step by step (rewritten 2026-11-21: tag the
      old images first, move the two untracked files aside before the pull). Read
      `docker images` on the server to get the image names to tag. After the deploy
      checks pass, in `~/site_2024`, looking at each directory before removing it:

          ls -la data/dokucozy data/dokuN657CZ fwww/static/test_08_fixture
          sudo rm -r data/dokucozy
          sudo rm -r data/dokuN657CZ
          sudo rm -r fwww/static/test_08_fixture
          docker ps -a --filter name=php
          docker image rm php:7-fpm

      Then `/dokucozy/`, `/dokuN657CZ/` and `/static/test_08_fixture/index.html` return 404,
      and no `php1` or `php2` container is listed.
- [ ] 0.9 After the deploy, with Tom: run the fixed `sudo_renew_cert.sh` on the server
      once and confirm the site still serves HTTPS. The certificate expires 2027-01-26.
      Compare the expiry date before and after, since the site also loads with the old
      certificate: `echo | openssl s_client -connect m24tom.com:443 -servername m24tom.com
      2>/dev/null | openssl x509 -noout -enddate`

## Phase 1 code change and site fixes (repo: `../site_2024/`, one deploy)

- [ ] 1.0 Set up pytest in `site_2024` (its only tests are those of 0.2c, which need
      nothing but pytest)
- [ ] 1.1a Separate prompt construction from `process_question` into a function that takes
      job data and document lists and returns the prompt string. Behaviour unchanged.
- [ ] 1.1b Write a failing test for the confirmed defect: revise and follow-up prompts must
      contain the full text of every prior document. Use a real `collection.get()` result
      from the local Chroma service, not a hand-built dict.
- [ ] 1.1c Fix the prior-context join
- [ ] 1.1d Reword `revise_prompt` and `followup_prompt` so they name no model
- [ ] 1.1e Remove the stale `__main__` block in `llm_functions.py`. Tom approved the
      removal (2026-11-21).
- [ ] 1.1f Failing test, then fix: `get_num_draft_docs` returns a count, not an index
      (plan 1.1 item 4). 60 matches inside the cutoff with a maximum of 15 gives 15; one
      match fewer than the maximum inside the cutoff gives that number; none inside the
      cutoff gives the minimum. Check every caller treats the value as a count.
- [ ] 1.1g Remove the `INITIAL` and `SECONDARY` settings and the code that carries them
      (plan 1.1 item 5). `PREFIX` stays and keeps working.
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
- [ ] S10a The app reads `site.ini` then `site_local.ini`; a value in the second wins.
      Missing `SESSION` or `OPENAI` key stops startup with a message naming
      `site_local.ini`. Tests use files in a temporary directory, never the real ones.
- [ ] S10b Track `site.ini` with the production settings and no `[KEYS]` section. Take
      the values from the local `site.ini` by naming each setting; do not print the file.
      Add `site_local.ini` to `.gitignore` and to `exclude_from_tar.txt`; add
      `site_local.ini.template`; remove `site.ini.template`, `.env_flask` and the
      commented `env_file` lines in `docker-compose.yaml`.
- [ ] S10c Write the server steps for the deploy (plan "S10 design", deploy step) and
      create the local `site_local.ini` with Tom.
- [ ] Deploy: `git pull` on the server (after the S10c steps), rebuild if requirements
      changed, restart.

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
