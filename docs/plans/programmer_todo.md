# Programmer Todo

**Last Updated:** 2026-11-22

# ACTIVE: Annual RAG / Website Refresh

**READ FIRST: `docs/plans/annual_refresh_plan.md`.** Read the whole document before any
task, every session. The tasks below are only a checklist; section numbers refer to the plan.

**Branches:** `wip/annual-refresh` in `ml/` and in `../site_2024/`.

**Order:** Phase 0, the Phase 1 code change with the site fixes, the follow-on fixes, and the
answer display with the corpus update and the model change are deployed (`775692d`). Next is
Phase 4, then Phase 2 (D41). One session per group; start each
session fresh. Code review happens once per deploy, not per commit.

**Deploys:** nginx looks up the name `flask` only when it starts. A deploy or rollback that
recreates the flask container ends with `docker compose restart nginx`.

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

- [ ] **From the deploy of the answer display and the corpus update (2026-11-22).** Not before 2026-11-28,
      and only if Tom says the site has run well. Ends both rollbacks
      below. The image and the data directory can be removed separately.

          cd ~/site_2024
          docker image rm site_2024-flask:c311cda
          sudo rm -r ~/chroma_before_corpus_update
          rm ~/chroma_corpus_update.tar.gz ~/chroma_corpus_update.sha256
          rm ~/collection_check.py ~/query_check.py

      Rollback of the code (not rehearsed). Forward again: `git checkout main`,
      `docker compose build flask`, then the last two lines.

          cd ~/site_2024
          git checkout c311cda
          docker tag site_2024-flask:c311cda site_2024-flask:latest
          docker compose up -d --force-recreate flask
          docker compose restart nginx

      Rollback of the data (not rehearsed):

          cd ~/site_2024
          docker compose stop flask chroma-rag
          sudo mv data/chroma ~/chroma_rejected
          sudo mv ~/chroma_before_corpus_update data/chroma
          docker compose up -d
          docker compose restart nginx

      Local leftovers, Tom's choice: `~/chroma_deploy`,
      `site_2024/data/chroma_before_corpus_update`, and `refetch_backup` on Windows.

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

- D33 recognises a used-up budget by the rule Tom approved (plan, D33 table). A real response of
  a used-up budget has not been seen. The rejected
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

## Phase 1 evaluation and model change (repo: `../site_2024/`)

1.3 to 1.5 were done on 2026-11-22; task details and the tally after each batch are in the git
history of this file. Tom decided that only the first answer is evaluated (D35).

Result, 30 answers per model, rated blind by Tom:

    model             perfect        ok  not_good    errors  median_s reasoning  $/answer
    gpt-4o-mini            17         8         5         2       5.3         0   0.00086
    gpt-6-luna             14        13         3         2       5.6       328   0.00074
    gpt-6.1-terra          11        15         4         1       5.0        30   0.00574

- [x] 1.6 Deploy Tom's choice of 2026-11-22: `LLM_DRAFT` = `gpt-6-luna`, `LLM_REVISE` =
      `gpt-6.2-sol` (not evaluated). Set in the tracked `site.ini` (`1e72014`) and tried on the
      local site with one question and one dig deeper. Tom waived the code review of this change.
      Deployed 2026-11-22 (`775692d`) with "Answer display" and "Corpus update" (D38, D42).

Still useful:

- The scripts are in `site_2024/evaluation/` and are not used by the site: `answer_models.py`
  (paid; needs Chroma, and Ollama for a question without a saved prompt), `review_answers.py` (the
  rating page), `tally_ratings.py`, `export_answers.py`. Run from `site_2024`, for example:

      PYTHONPATH=fwww .venv/bin/python evaluation/tally_ratings.py batch1 batch2 batch3

- The ratings and key are in `docs/archive/first_answer_ratings`; the answers of the three models
  are in `docs/archive/gpt4o_mini_baseline_answers`, `gpt6_luna_candidate_answers` and
  `gpt6_1_terra_candidate_answers`. The prompts are only in `evaluation/output/` (git-ignored),
  because they can hold email addresses.
- `evaluation/output/trial` holds random clicks of a trial. They are not ratings.
- A job's `result` holds the model name OpenAI returned (`llm_functions.py`, `r['model']`), and
  the results page shows it.

## Answer display (repo: `../site_2024/`, one deploy with 1.6)

Plan: "Answer display (D39, D40)". Read it whole; the tests are listed there. The archived
answers named there are in `ml/docs/archive/`; copy the text a test needs into the test's own
data, since the tests of `site_2024` do not read `ml/`.

- [x] AD1 Add `markdown-it-py` to `requirements_direct.txt` and freeze. Record the version.
- [x] AD2 The function that gives the HTML of an answer, with the settings of the plan. Tests
      first: table, list after a text line, nested bullets, hostile text.
- [x] AD3 The results page uses it, with the answer in the `overflow-x` container. The site's own
      pages keep `markdown_to_html`; test that one with raw HTML still shows it.
- [x] AD4 `evaluation/review_answers.py` uses the same function.
- [x] AD5 `README.md`: the models now used.
- [x] AD6 Local check with Tom before the review: a table answer in a narrow browser window.
      If it reads badly, stop and report to Architect; do not restyle on your own.
      Tom approved the look on 2026-11-22.
- [x] AD7 Merge and deploy (Tom waived the code review of all of it, D47)
      with 1.6 and the corpus update (CU8) by the plan's deploy steps and checks. Add what the deploy leaves on the server to "Server cleanup".
      Deployed 2026-11-22: `775692d`, count and id hash and the three query results as expected.
      nginx then gave 502: the deploy steps did not restart it. `docker compose restart nginx`
      gave 200 (the log was not read, so the stale address is inferred). Tom did the
      browser checks on 2026-11-22: all passed.

## Corpus update (repo: `ml/`; data in `../site_2024/data/chroma`)

Plan: "Corpus update (D42 to D44)". Read it whole. Only the containers of `site_2024` are used;
do not start those of `ml/docker-compose.yaml`.

- [x] CU0 Delivery step 1: copy of the local Chroma directory, count and id hash saved, top 15 of
      the 52 questions saved. Before anything below writes to the collection.
      Done: `data/corpus_update/before.json` (41,427 ids, hash `bb73f996...`), made by `snapshot.py`
      there; `embedstatus_before.txt` beside it. The directory copy is identical by checksum.
- [x] CU1 `ml/requirements.txt` (`chromadb-client` 1.5.9, `ollama`, `markdownify`, `pytest`, and
      what the tests need) and the venv brought to it. The client works with the local server.
- [x] CU2 Tests for `chunksplitter` covering current behaviour (was 2.1a).
- [x] CU3 Failing test, then fix: no prefix-only chunk when the word count is an exact multiple of
      the chunk size, or for an empty file (was 2.1b).
- [x] CU4 Failing test, then fix: chunk ids are `<source>#<number>`; `cp__no2` and `cp__no21`
      are both stored whole.
- [x] CU5 The repairs F1 and F2, under TDD, as a script in `embedder/`. F2 can be stopped and
      continued. Report how many vectors were updated and how many chunks were added (80 expected).
      F1 done: 80 chunks added. F2 stopped after about 3,360 of 36,500 chunks (3 replaced): Tom
      needed the GPU. It ran in a container of the site's Ollama image with `--gpus all` on port
      11998 (same vectors as the CPU); it continues from `embedder/` with
      `../venv/bin/python repair_collection.py 11998`. Not finished before the deploy (D46).
- [x] CU6 The messages:
      a. Copy the 227 markdown files, and the 10 refetched ones once Tom reports them done, from
         the Windows copy to `data/msgs_md`. A refetched file shorter than the one it replaces
         is not used; report it.
      b. The unchanged filter reproduces the present `.txt` of the 227. If not, stop and report.
      c. Failing test, then the filter pattern for the button text. Make the `.txt` files again.
      d. For the refetched threads: delete their stored chunks and their lines in
         `embedstatus.txt`.
      e. Run the embedder. Report the files and chunks added.
      Done. a: 227 new and 8 refetched; `IO1b3H0WdYI` and `UklKWGIn43Q` came back with the same
      posts and are not used. b: no difference. c: 24 files changed. d: 57 chunks deleted.
      e: 727 chunks of new threads, 99 of the 8 refetched. 42,276 in the collection.
- [x] CU7 The plan's "Checks before the deploy". Report 1 to 3 to Architect.
      1 passed: 42,276 unique ids, 11,388 sources, every source whole, nothing extra but the 42
      prefix-only chunks. 3: 17 of 52 questions changed; 27 of 780 places are new chunks (21 from
      new threads, 4 from refetched ones, 2 from the Canard Pushers added by F1). Results in
      `data/corpus_update/after.json` (id hash `92d43eed...`). 2: 99 short chunks, smallest
      cosine 0.99998. 4: passed on the local site (`gpt-6-luna`, new thread among the sources).
      Tar, SHA-256 and check script for the server: `~/chroma_deploy` (local).
- [x] CU8 Deploy with AD7 by the plan's "Delivery" steps. Add `~/chroma_before_corpus_update` and
      the tar to "Server cleanup".
      Deployed 2026-11-22: 42,276 chunks, id hash `92d43eed...`. The check with a
      question about a new thread passed (Tom, with AD7).

## Phase 2: Chunk-size experiment (repo: `ml/`)

Start after Phase 4 (D41). 2.1a and 2.1b are done as CU2 and CU3.

- [ ] 2.1c Add overlap to `chunksplitter` (default 0 reproduces current chunks)
- [ ] 2.1d `embedder.py` takes chunk size, overlap and collection name as parameters,
      with a progress file per collection
- [ ] 2.2 Embed variant B on the full corpus and report the time taken before running A (rebuilt,
      plan 2.2), C, D, E
- [ ] 2.3 Pooling: write `chunk_labels.csv` for Tom, one batch of 10 questions at a time (plan 2.3)
- [ ] 2.4 Scoring: compute the four metrics per variant from Tom's labels, rerun after
      each batch (plan 2.4)
- [ ] 2.5 Question set is the three batches plus the `chunk_only` rows of
      `refresh_questions.csv` (40 questions, plan 2.3). `reserve` rows are not used unless
      Architect says so.

## Phase 4 (not yet designed)

The image gallery (plan 4.2) first, then reference links (4.1) (D41). S3 is done by "Answer display".
