# Programmer Todo

**Last Updated:** 2026-11-21

# ACTIVE: Annual RAG / Website Refresh

**READ FIRST: `docs/plans/annual_refresh_plan.md`.** Read the whole document before any
task, every session. The tasks below are only a checklist; section numbers refer to the plan.

**Branches:** `wip/annual-refresh` in `ml/` and in `../site_2024/`.

**Order:** Phase 0 is done. Next is the code change (Phase 1.0 to 1.1 with S1, S2, S4, S5, S6, S10, S11), then
the evaluation (1.3 to 1.6). Phase 2 can overlap the evaluation. One session per group;
start each session fresh. Code review happens once per deploy, not per commit.

All code tasks follow TDD. Escalate design questions to Architect; do not resolve them yourself.

The finished image database tasks are in `docs/archive/programmer_todo_image_database.md`.

## Phase 0: Infrastructure refresh (done)

Deployed 2026-11-21 (`bed83f4`) and every plan 0.8 check passed; Tom waived the code review.
Certificate renewed to 2027-02-20. Task details are in the git history of this file.

Still useful:

- The server runs Docker 29.10.0 and Compose 5.8.0; the local rehearsals used 28.3.2 and 2.39.1.
- The server has a 2 GB swap file, and gunicorn runs 2 workers.
- The site stays down after a server reboot until `docker compose up -d` is run.
- `python-dotenv` stays in `requirements.txt` because `pydantic-settings` requires it.
- Known log warnings: gunicorn wants its config file to have a `.py` extension; Ollama reports
  the requested context (8192) exceeds the embedding model's 2048. Neither investigated.
- Not exercised on the server: the rollback in `sudo_renew_cert.sh`.

## Server cleanup (with Tom)

Leftovers kept on the server as the rollback for each deploy. Add to this list whenever a deploy
leaves something behind. Until an entry is done, no `docker system prune` on the server.

- [ ] **From the Phase 0 deploy (2026-11-21).** Not before 2026-11-28, and only if Tom says the
      site has run well. Ends the rollback to the stack before Phase 0. Check first:

          cd ~/site_2024
          git stash list
          docker ps -a
          docker images
          ls -la ~/site_backup_2026-11-21

      Expect one stash, `WIP on main: 906ffd8`, and no container using the images below. If
      a later deploy added a stash, use the number of the `906ffd8` one in the first command.

          git stash drop 'stash@{0}'
          docker image rm site_2024-flask:old-stack
          docker image rm site_2024-ollama-rag:old-stack
          docker image rm chromadb/chroma:1.1.1
          docker image rm nginx:latest
          sudo rm -r ~/site_backup_2026-11-21
          rm ~/deploy_logs.txt

      The backup directory holds the Chroma data from before the upgrade, the certbot
      directory with the private key, and the server's earlier `exclude_from_tar.txt` and
      `sudo_renew_cert.sh`. Afterwards `docker compose ps` lists the same four containers and a
      question is answered.

      Tom's choice, not part of the rollback: the untracked `server/old.nginx_all_apps.conf`,
      `server/certbot/conf/live/m24tom.old`, and the two untagged images from before Phase 0.

## Phase 1 code change and site fixes (repo: `../site_2024/`, one deploy)

- [x] 1.0 Set up pytest in `site_2024` (its only tests are those of 0.2c, which need
      nothing but pytest)
- [x] 1.1a Separate prompt construction from `process_question` into a function that takes
      job data and document lists and returns the prompt string. Behaviour unchanged.
- [x] 1.1b Write a failing test for the confirmed defect: revise and follow-up prompts must
      contain the full text of every prior document. Use a real `collection.get()` result
      from the local Chroma service, not a hand-built dict.
- [x] 1.1c Fix the prior-context join
- [x] 1.1d Reword `revise_prompt` and `followup_prompt` so they name no model
- [x] 1.1e Remove the stale `__main__` block in `llm_functions.py`. Tom approved the
      removal (2026-11-21).
- [x] 1.1f Failing test, then fix: `get_num_draft_docs` returns a count, not an index
      (plan 1.1 item 4). 60 matches inside the cutoff with a maximum of 15 gives 15; one
      match fewer than the maximum inside the cutoff gives that number; none inside the
      cutoff gives the minimum. Check every caller treats the value as a count.
- [x] 1.1g Remove the `INITIAL` and `SECONDARY` settings and the code that carries them
      (plan 1.1 item 5). `PREFIX` stays and keeps working.
- [x] S1a Function that shortens an email address for display: first 5 characters plus
      `...`; empty string for none. Replaces the `safe_truncate(job['email'],5)` calls.
- [x] S1b `/cozyrag/<id>/status` returns only `status`, `status_text`, `result_html`.
      Check `cozyrag_answer.html` still works; it reads only those three.
- [x] S1c Results page and jobs page (including `/cozyrag/jobs/email`) show the shortened
      address only, applied where the job record is prepared for display.
- [x] S1d Tests: with a job file containing a known full address, that address appears in
      none of the responses from `status`, `processid`, `jobs`, `jobs/email`.
- [x] S2a `/cozyrag/revise` accepts POST only; a GET gets 405.
- [x] S2b Tom decided (2026-11-21): no nginx rate limit. The OpenAI budget limit has no auto
      reload, so a script can use up the budget but not more. Instead the job starts when
      the question is submitted; reading pages starts none. Plan S2 is updated (D25).
- [x] S4 `sanitize()` no longer wraps input in `Markup`. Rename it to say what it does, or
      remove it if nothing remains; ask Architect if unsure.
- [x] S5a Unknown job id on `processid` and `status` returns 404, not 500.
- [x] S5b `/cozyrag/jobs/<unknown column>` returns 404 (`abort` is not imported today).
- [x] S5c `revise`, `followup`, `feedback` and `answer` without a session redirect to the
      question form instead of returning 500.
- [x] S6 Feedback accepts only `perfect`, `ok`, `not_good`; anything else is ignored with
      a redirect to the question form.
- [x] S11a Failing test for the empty job file read (plan "S11 design"): hold a shared lock
      on a job file that has content, start a write in a second thread, and while the
      writer waits read the file directly; it must still hold the previous content. After
      the lock is released the write completes with the replacement.
- [x] S11b Fix `open_with_lock`: an existing file opened for writing is emptied only after
      the exclusive lock is held, and the descriptor is closed before each retry. The
      locking scheme stays; no change to the callers.
- [x] S10a The app reads `site.ini` then `site_local.ini`; a value in the second wins.
      Missing `SESSION` or `OPENAI` key stops startup with a message naming
      `site_local.ini`. Tests use files in a temporary directory, never the real ones.
- [x] Found while testing S1: the jobs page returned 500 while any job was unfinished. Fixed.
      With it, `processid` of an unfinished job gives 404.
- [x] S10b Track `site.ini` with the production settings and no `[KEYS]` section. Take
      the values from the local `site.ini` by naming each setting; do not print the file.
      Add `site_local.ini` to `.gitignore` and to `exclude_from_tar.txt`; add
      `site_local.ini.template`; remove `site.ini.template`, `.env_flask` and the
      commented `env_file` lines in `docker-compose.yaml`.
      Values are the server's (Tom, 2026-11-21). The local file differed in `MAX_QUERY_LEN` (1024,
      512 on the server). Checked: no key in the commits; the local stack starts on the two
      files and its pages answer, with no question asked. Tom's backup with the keys is
      `~/site.ini.before_s10` on the local machine; he deletes it.
- [x] S10c Write the server steps for the deploy (plan "S10 design", deploy step) and
      create the local `site_local.ini` with Tom.
      Local file created. Server steps, rehearsed on throwaway repositories with fake keys:

          cd ~/site_2024
          docker compose stop flask
          install -d -m 700 ~/site_ini_before_s10
          mv fwww/site.ini ~/site_ini_before_s10/
          git pull
          ( umask 077; sed -n '/^\[KEYS\]/,/^\[/{/^\[KEYS\]/p;/^\[/!p}' ~/site_ini_before_s10/site.ini > fwww/site_local.ini )
          ls -l fwww/site_local.ini
          grep -cE '^(SESSION|OPENAI) *= *.' fwww/site_local.ini
          names() { grep -E '^(DEBUG|JOBS_DIR|WWW_DIR|USE_GPT|MAX_[A-Z_]+|MIN_DOCUMENTS|PROCESS_ID_LEN|OLLAMA|CHROMA|EMBED|LLM_[A-Z]+|PREFIX|SHOW_REVISE) *=' "$1" | sort; }
          diff <(names ~/site_ini_before_s10/site.ini) <(names fwww/site.ini) && echo same
          docker compose up -d

      - **`site.ini` must be moved before the pull.** It is ignored, so git replaces it with the
        tracked one without a word and the keys are lost (seen in the rehearsal).
      - flask is stopped first because the templates are live: the jobs template shows
        `job['email']` as given, which the code before this deploy does not shorten.
      - Expected: mode `-rw-------`, the count 2, and `same`. Stop if not.
      - `~/site_ini_before_s10` holds the keys; add it to "Server cleanup" after the deploy.
- [ ] 1.1h Job record keeps every chunk (plan 1.1 item 6, D26). Failing test first: a
      query result with several chunks from one source gives a record with every chunk
      id, in the order retrieved. The one-row-per-source reduction moves to where a job is
      prepared for display, and works for entries with no `score`. Test the displayed
      list too: one row per source, for a first answer and for a revise.
- [ ] 1.1i Revise context in rank order (plan 1.1 item 7, D26). Failing test first, on the
      local Chroma service as in 1.1b: the prompt holds every provided and related chunk,
      provided first, each in the order of the record, whatever order `collection.get()`
      returns.
- [ ] 1.1j Follow-up context (plan 1.1 item 8, D27). Failing tests first: previous content
      is the prior record's `provided_docs` only; additional content is cut by
      `get_num_draft_docs`; the record's `provided_docs` is previous then additional with
      no id twice, and there is no `related_docs`. A second follow-up on that record
      carries no more than `MAX_DRAFT_DOCUMENTS` further chunks.
- [ ] Before the deploy: one question, one revise, one follow-up and a follow-up on that
      follow-up answered locally (paid calls), noting the prompt tokens of each; code review.
- [ ] Deploy: `git pull` on the server (after the S10c steps), rebuild if requirements
      changed, restart.

Running the tests: `site_2024/README.md`. Use `site_2024/.venv`; `site_2024/venv` still holds
the old stack.

Flask's test client is enough for the S tasks; only 1.1b needs a live service.

## Phase 1 evaluation (repo: `../site_2024/`)

- [ ] 1.3 Evaluation harness: reads `refresh_questions.csv`, retrieves once per question,
      sends the same documents to each model, records answer, tokens, latency, cost.
      Every model is called exactly as production calls it, with no reasoning setting.
      Reasoning tokens are recorded as a separate figure and not added to the cost a
      second time (plan 1.3, 1.4).
- [ ] 1.4 Capture the baseline with the current models (they shut down 2027-01-14)
- [ ] 1.5 Produce the blind review files and key file (plan 1.4) for Tom to rate, one batch
      of 10 questions at a time, with a per-tier tally after each batch (plan 1.5). The
      tally shows median latency, median reasoning tokens and cost per answer per model
- [ ] 1.6 After Tom's decision: update the tracked `site.ini` (S10 removes the template)

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
