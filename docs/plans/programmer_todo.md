# Programmer Todo

**Last Updated:** 2026-11-24

# ACTIVE: Annual RAG / Website Refresh

**READ FIRST: `docs/plans/annual_refresh_plan.md`.** Read the whole document before any
task, every session. The tasks below are only a checklist; section numbers refer to the plan.

**Branches:** `wip/annual-refresh` in `ml/` and in `../site_2024/`.

**Order:** everything through the answer display, the corpus update and the model change is
deployed (`775692d`); the image update is done; "Pictures of an answer" is deployed
(`4f85f9e`); the yearly update instructions are written and approved. **Now: 2.2d (all five
variants have run, 2026-11-23 21:57), then "Collapsed posts" (CP1 to CP8, D58), both before
anything else.** After them "Reference links: the trial" (RL1 to RL5) under Phase 4. The rest of Phase 2 follows Phase 4 (D41). One session per group;
start each session fresh. Code review happens once per deploy, not per commit.

**The yearly update** (fetch, pictures, embedding, deploy) is in the top-level `README.md`.
A deploy of the site's code alone: `site_2024` README, "Deploy a change of the code". Server
commands go to Tom in short blocks, each with what to expect, and he pastes the output.

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
- Rebooted 2026-11-24: Docker is enabled, the four containers come up on their own, nginx
  finds `flask` without a restart, and the swap file is in `/etc/fstab`. `swapon` is in
  `/sbin`, not on `admin`'s path; `free -h` shows the swap.
- `python-dotenv` stays in `requirements.txt` because `pydantic-settings` requires it.
- Known log warnings: gunicorn wants its config file to have a `.py` extension; Ollama reports
  the requested context (8192) exceeds the embedding model's 2048. Neither investigated.
- Not exercised on the server: the rollback in `sudo_renew_cert.sh`.

## Server cleanup (with Tom)

Leftovers kept on the server as the rollback for each deploy. Add to this list whenever a deploy
leaves something behind. Until an entry is done, no `docker system prune` on the server.

Done 2026-11-24, early at Tom's word: the entries of the Phase 0 deploy, the Phase 1 deploy
and the pictures deploy (details in the git history of this file). Still Tom's choice, on no
schedule: `server/old.nginx_all_apps.conf`, `server/certbot/conf/live/m24tom.old`,
`~/project.tar.gz`, `~/certbot_bu.tar`, the exited `hello-world` container. Keep
`certbot/certbot:latest`: the certificate renewal uses it.

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

      The local leftovers of this deploy were deleted 2026-11-24.

- [ ] **World-writable directories (D59).** With the full cleanup, after the server has run
      for a week: `~/site_2024`, `~/www` and `~/chroma_before_corpus_update` are
      world-writable. First a read-only step that shows why (who owns them, which user the
      containers write as); change nothing before Tom and Architect have seen it.

- [x] **From the deploy of the pictures of an answer (2026-11-24, PA8 and PA9).** Done
      2026-11-24, early at Tom's word: image `site_2024-flask:775692d` and `~/pictures_deploy`
      removed on the server, `~/pictures_deploy` locally. Rollback of the code now needs a
      rebuild of `775692d`.

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

Deployed 2026-11-22 (`775692d`): `LLM_DRAFT` = `gpt-6-luna`, `LLM_REVISE` = `gpt-6.2-sol` (not
evaluated). Tom waived the code review of this change.

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

## Answer display and corpus update (done)

Deployed 2026-11-22 (`775692d`) with the model change; Tom waived the code review (D47) and his
browser checks all passed. Task details (AD1 to AD7, CU0 to CU8) are in the git history of
this file.

Still useful:

- The HTML of an answer comes from one function (`fwww/src/answer_html.py`, `markdown-it-py`),
  used by the results page and by `evaluation/review_answers.py`. The site's own pages keep
  `markdown_to_html`.
- The tests of `site_2024` do not read `ml/`; a test carries its own data.
- At that deploy nginx gave 502 until `docker compose restart nginx` (the log was not read, so
  the stale address is inferred).
- The collection: 42,276 chunks of 11,388 sources, id hash `92d43eed...`; 42 prefix-only
  chunks are still in it. Chunk ids are `<source>#<number>`.
- For the production collection only the containers of `site_2024` are used; do not start
  those of `ml/docker-compose.yaml`.
- `data/corpus_update/`: `before.json` (41,427 ids), `after.json` and `snapshot.py`, which
  made them (count, id hash, top 15 of the 52 questions).
- The repair F2 was stopped after about 3,360 of 36,500 chunks (3 replaced) and was not
  finished (D46). It continues from `embedder/` with
  `../venv/bin/python repair_collection.py 11998`.
- Messages of 2026: 227 new threads and 8 fetched again; `IO1b3H0WdYI` and `UklKWGIn43Q` came
  back with the same posts and were not used.
- The tar, its SHA-256 and the check script of the deploy: `~/chroma_deploy` (local).

## Phase 2: Chunk-size experiment (repo: `ml/`)

2.1a to 2.2c are done (2026-11-22; details in the git history of this file). Open: 2.2d, when
all five variants have run. 2.3 to 2.5 start after Phase 4 (D41). Plan 2.1 to 2.4.

Do not write to the Chroma on port 8000 and do not stop or change a container of `site_2024`.

Still useful:

- `chunksplitter` takes an overlap (default 0 gives the present chunks). It makes the plan's
  count of chunks for all five variants.
- `embedder.py` takes chunk size, overlap, `--collection`, Chroma port, Ollama port and
  `--sources`, with a progress file per collection; with no parameters it does what it did. A
  chunk size or overlap without `--collection` is refused. A file that fails is logged and
  left out of the progress file; 20 failures in a row end the variant.
- The queue is `embedder/chunk_queue.py` (A, C, B, D, E). The experiment's Chroma is on port
  8010 (data in `data/chunk_experiment/chroma`; an empty `defaultdb` stays in it), the GPU
  Ollama on port 11998. The queue's `start` runs both; the commands they were made with:

      docker run -d --name chunk_experiment_chroma -p 127.0.0.1:8010:8000 \
          -v /home/tom/projects/ml/data/chunk_experiment/chroma:/data chromadb/chroma:1.5.9
      docker run -d --name chunk_experiment_ollama --gpus all \
          -p 127.0.0.1:11998:11434 site_2024-ollama-rag

- Started 2026-11-22 18:25:38. 0.239 s per chunk at 250 words, storing included.
- [ ] 2.2d When all five have run: the five checks of plan 2.2a, reported in a note in
      `architect_todo.md`. Then stop and remove the GPU Ollama container; the experiment's
      Chroma stays for 2.3.

### Start and stop (for Tom)

Evening, start or continue (starts both containers and the queue; refused while the queue is
running):

    ~/projects/ml/venv/bin/python ~/projects/ml/embedder/chunk_queue.py start

Morning, stop (ends the queue, then stops the GPU Ollama container; the GPU is free). Ctrl-C does
not stop the queue, which runs in the background:

    ~/projects/ml/venv/bin/python ~/projects/ml/embedder/chunk_queue.py stop

Keep a WSL terminal open at night: WSL may end background processes when the last one closes
(not tried here). After a restart of Windows, Docker Desktop has to be running first.

Log: `~/projects/ml/data/chunk_experiment/queue.log`. `END ... exit code 1` means files failed
(search for `FAILED`); the next continue tries them again.
A stop writes `STOPPED by the stop command` to the log.

### For Tom in the morning

- 2026-11-23 08:29: A, C, B and D done, each count equal to the plan's table, no file failed.
  E stopped by Tom at 08:25 after 4,647 of 11,388 files (13,734 chunks); about 1.8 hours left.
- Tom stopped the queue at about 20:37 (after about 9,070 files of A) and started it at 21:48.
  The log shows no line for a stop; `docker events` keeps too little history to show one.

- [ ] 2.3 Pooling: write `chunk_labels.csv` for Tom, one batch of 10 questions at a time (plan 2.3)
- [ ] 2.4 Scoring: compute the four metrics per variant from Tom's labels, rerun after
      each batch (plan 2.4)
- [ ] 2.5 Question set is the three batches plus the `chunk_only` rows of
      `refresh_questions.csv` (40 questions, plan 2.3). `reserve` rows are not used unless
      Architect says so.

## Collapsed posts (repo: `ml/`, D58)

Plan: "Collapsed posts (D58)". Read all of it; the numbers and the hypothesis are there. Do
2.2d first: the refetch changes files its first check reads. Never delete a file of
`data/msgs` or `data/msgs_md`: set it aside. Nothing is fetched into `data` before CP3 is
done.

- [ ] CP1 The cause, with Tom at Chrome on Windows. Reproduce into a scratch directory; show
      what the page held when it was read and why; look at three of the older single-post
      files in a browser. No fix yet.
- [ ] CP2 Report the cause in a note in `architect_todo.md` and tell Tom. Go on to CP3 if the
      cause is one of timing and the plan's points for the fix fit it; otherwise stop for
      Architect.
- [ ] CP3 The fix, tests first (plan, step 3): a thread is saved only with no post collapsed;
      one that stays collapsed leaves no file, is printed and counted, and the run goes on;
      one function for the check, used by the fetch and by a command that lists the affected
      threads.
- [ ] CP4 The refetch with Tom (`msgGetter/README.md` steps 5 to 7; you supply the id file).
      Take a thread over only if its new copy has no collapsed post and at least as many
      posts. Report the threads not taken over. Pass mark: none of 2026 left collapsed.
      In the same run the 60 ids of 2024-25 that were never fetched (D59; plan, step 4),
      from an id file of their own in `data`. They go through CP5 and CP6 as new threads.
      Do not remove `msgGetter/msgids_2024-09-03_2025-10-02.txt` without Tom's word.
- [ ] CP5 The pictures: the index built again; if it names pictures not on disk, the download
      and Tom's review, the gallery index and the thumbnails. Say which it was.
- [ ] CP6 The embedding into the production collection (`embedder/README.md`) and the three
      local checks of the plan, step 6. Not the chunk experiment's collections.
- [ ] CP7 Code review, then the deploy with Tom by the top-level `README.md` (steps 3 and 5
      to 8). Correct the README wherever a step does not work as written.
- [ ] CP8 `msgGetter/README.md` step 8 and troubleshooting say what the fetch does now; the
      note in `docs/notes/opportunities_for_improvement.md` if anything is left. Report to
      Architect: the cause, the threads repaired and not, pictures gained, chunks before and
      after, what the deploy steps needed corrected.

## Phase 4

The image update (plan 4.0) is done. Next, in this order (Tom, 2026-11-23): "Pictures of an
answer" (plan 4.2), then "Reference links: the trial" (plan 4.1a). "Yearly update
instructions" has no place in that order yet: ask Tom when he wants it. All three are at the
end of this section. S3 is done by "Answer display".

### Image update (done)

Plan 4.0. Done 2026-11-23 in `ml/imageGetter/`; Tom waived the code review. Nothing of it is
on the server. Task details (IU1 to IU9) are in the git history of this file.

Still useful:

- Never delete or overwrite a file in `data/images` or `imageGetter/input`. Both and `data/`
  are git-ignored: a test carries its own small pictures.
- Gallery index: `data/images/gallery261123.idx`, 2,368 threads, 5,661 pictures, made by
  `gallery_index_cli.py`. It drops by decision only, never by size, and stops on a file on
  disk that is not measured.
- Working index: `data/images/index261123105058.idx` (2,631 threads, 6,811 entries), built
  from `data/msgs_md` and measured by `measure_images_cli.py`. Copies beside it:
  `..._before_measure.idx`, `..._before_download.idx`.
- Decisions: `imageGetter/image_decisions.json` (tracked; content hash to `remove` / `keep`).
  Nothing is undecided: 5,734 contents, of them 333 `remove`. `image_suggestions.json` feeds
  the Suggested list of the review tool (`review_images_cli.py`, port 8765).
- Run once in 2026 and not again: `rename_images_cli.py` (copies `full_before_rename`,
  `thumbs_before_rename`; map `data/images/rename_map.json`) and `load_removals_cli.py`.
  `input/remove_list2` was not loaded (Tom).
- 10 thumbnails of 2025 keep their old names (each was shared by two pictures); each of the
  20 pictures also has a thumbnail under its own name.
- Left on disk and named by no index: 11 zero-byte files cut at a `:`, and 8 pictures.
- A local name: each of `< > : " / \ | ? *` becomes `_`, at most 180 bytes, extension kept.
- The download ran in Windows PowerShell from the WSL `imageGetter` directory with the Windows
  Python 3.13, Chrome on the debug port with a profile of its own
  (`--user-data-dir=C:\chrome-debug`), Chrome and ChromeDriver 158. 591 fetched, 0 failed. It
  rewrote the index with CRLF; the content was unchanged.
- One thumbnail cannot be made: a truncated file of 2025, marked `remove`.
- Tom waived TDD for the download (IU3). `test_handle_download_failure` passes only because a
  Mock's `get_cookies()` cannot be iterated (told to Tom).
- The review tool's page script is checked for syntax only (`node --check`).
- One full-suite run had 7 failures that four runs after it did not repeat; which tests is not
  known. If it comes back, keep the whole output.

### Pictures of an answer (done)

Plan 4.2. Deployed 2026-11-24 (`site_2024` `4f85f9e`, `ml` `72957f4`); every check of the
plan's "Delivery" passed, and a click on a thumbnail without a Google sign-in gives Google's
sign-in page (D53, accepted). Tom waived the rest of the code review; R4 dropped by Tom.
Upload by tar, SHA-256 and `scp` (not `rsync`). Task details are in the git history of this
file; the yearly upload is in the top-level `README.md`.

### Reference links: the trial (repo: `../site_2024/`)

Plan: "4.1 Reference links inside answers", 4.1a. Read all of 4.1; the tests are listed there.
After "Pictures of an answer". Nothing of this is deployed with numbering on: the setting stays
off, and with it off every prompt is what it is today. The display (4.1b) has no tasks yet;
do not start it.

- [ ] RL1 `build_prompt` numbers the chunks when told to, with the plan's wording, for all
      three kinds of prompt; the setting in `site.ini`, off; the record says whether an answer
      was numbered. Tests first, the first of them that the prompts with numbering off are
      unchanged.
- [ ] RL2 The run: the 30 questions, `gpt-6-luna`, the chunks fetched by the ids saved with the
      evaluation's prompts. Before any paid call: with numbering off, the prompt built from
      the fetched chunks equals the saved prompt, for each question; report those where it
      does not and leave them out. Answers into a directory of their own. Then the paid run
      (about 3 cents); tell Tom before it starts.
- [ ] RL3 The counting script of the plan, tests first, and its output for the run.
- [ ] RL4 The page for Tom: batch 1, the rating of each answer as in the evaluation, and up to
      5 citations of each answer, chosen at random, the sentence beside the text of its chunk,
      `yes` or `no`. Each click saved at once. Show it to Tom on two answers before he does
      the ten.
- [ ] RL5 Report to Architect in a note in `architect_todo.md`: the counts, Tom's ratings
      beside his ratings of the `gpt-6-luna` answers to the same questions, his `yes` and `no`,
      the questions left out, the answers without a number (by question id). Do not apply the
      rule yourself and do not change the wording of the prompt: both are Architect's.

### Yearly update instructions (done)

Written and approved by Tom 2026-11-24 (YU1 to YU5): "Yearly Update" in `msgGetter/README.md`,
`imageGetter/README.md` and `embedder/README.md` for the work on this machine, and in the
top-level `README.md` the order, the check of the server's collection, the packing, the one
deploy of everything, the checks, the way back and the cleanup. `site_2024` README: "Deploy a
change of the code". Settled with Tom: Windows Python from cmd via `pushd` into the WSL folder,
`chrome_with_debug.bat` for both modules, ChromeDriver in `/home/tom/projects/chromedriver-win64`.
The fetch from the WSL folder was tried (`docs/plans/yu1_fetch_trial.md`). The Windows clone
is deleted. Faults found and the awkward steps are with Architect. Task details are in the git
history of this file.
