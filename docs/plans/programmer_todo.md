# Programmer Todo

**Last Updated:** 2026-11-22

# ACTIVE: Annual RAG / Website Refresh

**READ FIRST: `docs/plans/annual_refresh_plan.md`.** Read the whole document before any
task, every session. The tasks below are only a checklist; section numbers refer to the plan.

**Branches:** `wip/annual-refresh` in `ml/` and in `../site_2024/`.

**Order:** Phase 0, the Phase 1 code change with the site fixes, and the follow-on fixes are
deployed. Next is the evaluation (1.3 to 1.6). Phase 2 can overlap it. One session per
group; start each session fresh. Code review happens once per deploy, not per commit.

All code tasks follow TDD. Escalate design questions to Architect; do not resolve them yourself.

The finished image database tasks are in `docs/archive/programmer_todo_image_database.md`.

## Phase 0: Infrastructure refresh (done)

Deployed 2026-11-21 (`bed83f4`) and every plan 0.8 check passed; Tom waived the code review.
Certificate renewed to 2027-02-20. Task details are in the git history of this file.

Still useful:

- The server runs Docker 29.10.0 and Compose 5.8.0; the local rehearsals used 28.3.2 and 2.39.1.
- The server has a 2 GB swap file, and gunicorn runs 2 workers.
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

- [ ] **From the Phase 1 deploy (2026-11-21).** Not before 2026-11-28, and only if Tom says the
      site has run well. Ends the rollback to `bed83f4` given below. The directory holds the keys.
      Expect one file, `site.ini`:

          ls -la ~/site_ini_before_s10
          rm -r ~/site_ini_before_s10

## Phase 1 code change and site fixes (repo: `../site_2024/`, one deploy)

Deployed 2026-11-21 (`3278e9e`; Tom waived the code review): 1.0,
1.1a to 1.1j, S1, S2, S4, S5, S6, S10, S11. Task details are in the git history of this file.

Still useful:

- Found while testing S1 and fixed: the jobs page returned 500 while any job was unfinished.
  With it, `processid` of an unfinished job gives 404.
- S2: no nginx rate limit (D25). The job starts in the `query` POST; reading pages starts none.
- Found while doing 1.1j and fixed: a revise or follow-up of a job without an answer ended the
  job thread (`KeyError: 'result'`); it now redirects to the question form. Any other exception
  in the job thread (Chroma or Ollama unreachable) still ends it; for Architect, with S8.
- The tracked `site.ini` holds the server's values. The local file had differed in
  `MAX_QUERY_LEN` (1024; 512 on the server).
- Prompt tokens in the local paid check (Q44): question 4,504 (15 chunks), revise 17,438 (60),
  follow-up on the revise 22,652 (69), follow-up on that 24,780 (79). The follow-ups sent 6 and 5
  of their 15 additional chunks twice, as the plan is written (note with Architect).
- Checked on the live site: a question, a revise, the pages and that no full address is shown. A
  follow-up was checked locally only.

Commands for the server: keep lines short. A long line wrapped when pasted, broke a `grep`
pattern, and the comparison of two empty outputs then reported `same`. Print a line count beside
any such comparison.

Rollback until the cleanup (git and settings part rehearsed, containers not):

    cd ~/site_2024
    docker compose stop flask
    git checkout bed83f4
    cp -p ~/site_ini_before_s10/site.ini fwww/site.ini
    docker compose up -d

`site_local.ini` is then untracked and not ignored; leave it. Forward again:
`rm fwww/site.ini`, `git checkout main`.

Running the tests: `site_2024/README.md`. Use `site_2024/.venv`; `site_2024/venv` still holds
the old stack.

The tests that read the collection need the local Chroma (`docker compose up -d chroma-rag`); the
page tests use Flask's test client.

## Follow-on fixes (repo: `../site_2024/`, one deploy)

Deployed 2026-11-22 (`c311cda`): 1.1k, S12, D31, D32a to D32c, D33, and the review findings R1
to R3. Tom waived the rest of the code review (the check of R1 and `09e3ca4..c311cda`). Task
details and the review results are in the git history of this file.

Still useful:

- D33 recognises a used-up budget by the rule Tom approved, not the one in the plan's table (note
  in `architect_todo.md`). A real response of a used-up budget has not been seen. The rejected
  key was tried against the real API, locally.
- The tests need docker, node and openssl.
- Checked on the live site: a question and a revise (reported by Tom), the three `www` and HTTP
  redirects, both names in the certificate (valid to 2027-02-20), and a question answered after
  a server reboot with no command run. A failed job was not checked there.
- The renewal script ran once on the server with both names. Its rollback was not needed.
- No rollback files were left on the server, so "Server cleanup" has no entry for this deploy.

Rollback (rehearsed locally; do not run the renewal script while rolled back):

    cd ~/site_2024
    git checkout 3278e9e
    docker compose up -d

Forward again: `git checkout main`, `docker compose up -d`.

## Phase 1 evaluation (repo: `../site_2024/`)

Tom decided on 2026-11-22: only the first answer is evaluated. The dig-deeper model is not
evaluated; it is the model one above the one chosen. The plan still has the dig-deeper tier
in 1.2 to 1.5 (note in `architect_todo.md`); where they differ, this section holds.

- [x] 1.3 Evaluation harness: reads `refresh_questions.csv`, retrieves once per question,
      sends the same documents to each model, records answer, tokens, latency, cost.
      Every model is called exactly as production calls it, with no reasoning setting.
      Reasoning tokens are recorded as a separate figure and not added to the cost a
      second time (plan 1.3, 1.4).
      Done (`259a988`): `site_2024/evaluation/answer_models.py`. No deployed
      file changes. Prompts and answers go in `evaluation/output/` (git-ignored); a saved prompt
      is used for every later model, a saved answer is not paid for again, and a failed call is
      made again by the next run. Prices read 2026-11-22. The 30 prompts were built with real
      retrieval and a stand-in for OpenAI; no paid call was made. To run (needs Chroma and
      Ollama; paid), from `site_2024`:

          PYTHONPATH=fwww .venv/bin/python evaluation/answer_models.py batch1 --models gpt-4o-mini
- [x] 1.4 Capture the baseline with the current first-answer model, `gpt-4o-mini` (it shuts
      down 2027-01-14). Done 2026-11-22 with Tom's approval: all 30 answered, $0.026, median
      5.3 s, no reasoning tokens. The answers are in `docs/archive/gpt4o_mini_baseline_answers`
      (exporter: `72ca581` in `site_2024`), without the text sent to the model,
      which can hold email addresses; that text is only in `evaluation/output/`. The files name
      the model: Tom does not open them before rating. The candidates `gpt-6-luna` and
      `gpt-6.1-terra` answered all 30 on 2026-11-22 with Tom's approval, no failures ($0.022 and
      $0.172).
- [~] 1.5 Produce the blind review files and key file (plan 1.4) for Tom to rate, one batch
      of 10 questions at a time, with a tally after each batch (plan 1.5). The
      tally shows median latency, median reasoning tokens and cost per answer per model.
      The review page is built (`f008b10`) in place of a review file:
      `evaluation/review_answers.py`, on this machine only. It saves ratings in
      `ratings.json` and the hidden order in `key.json`. Tom found the
      design good (2026-11-22) and tried it on five `chunk_only` answers, kept in
      `evaluation/output/trial`: random clicks, not scores, but every one was saved. The tally
      is built (`ada6110`): `evaluation/tally_ratings.py batch1` refuses until every answer
      of the batch is rated. To serve batch 1, from `site_2024`, once all its models are
      answered (the key refuses models added later):

          PYTHONPATH=fwww .venv/bin/python evaluation/review_answers.py batch1

      Batch 1 rated by Tom 2026-11-22 (10 answers per model; the counts were checked by hand
      against the ratings and the key):

          model             perfect        ok  not_good    errors  median_s reasoning  $/answer
          gpt-4o-mini             8         1         1         1       5.7         0   0.00082
          gpt-6-luna              6         3         1         0       3.2       134   0.00064
          gpt-6.1-terra           6         4         0         0       2.7         0   0.00530

      Rule 1.5: no early adoption (`gpt-6-luna` has a `not_good`; both candidates have fewer
      `perfect` than the baseline), no candidate dropped, so batch 2 is rated next.

- [ ] 1.6 After Tom's decision: update the tracked `site.ini`, `LLM_DRAFT` to the model chosen
      and `LLM_REVISE` to the one above it

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
