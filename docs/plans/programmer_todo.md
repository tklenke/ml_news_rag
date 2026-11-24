# Programmer Todo

**Last Updated:** 2026-11-23

# ACTIVE: Annual RAG / Website Refresh

**READ FIRST: `docs/plans/annual_refresh_plan.md`.** Read the whole document before any
task, every session. The tasks below are only a checklist; section numbers refer to the plan.

**Branches:** `wip/annual-refresh` in `ml/` and in `../site_2024/`.

**Order:** everything through the answer display, the corpus update and the model change is
deployed (`775692d`), and the image update is done. **Now: "Pictures of an answer" (PA1 to
PA9), then "Reference links: the trial" (RL1 to RL5)**, both under Phase 4. Beside them: 2.2d
when the overnight embedding has run all five variants. The rest of Phase 2 follows Phase 4
(D41). "Yearly update instructions" has no place yet: ask Tom. One session per group; start
each session fresh. Code review happens once per deploy, not per commit.

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

- [ ] **From the upload of the pictures (2026-11-24, PA8).** Only after the PA9 deploy and its
      checks. The thumbnails and the index are already in place; this is the upload copy.

          rm -r ~/pictures_deploy

      Local leftover, Tom's choice: `~/pictures_deploy`.

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

### Pictures of an answer (repos: `ml/` and `../site_2024/`, one deploy)

Plan: "4.2 Pictures of an answer (D52 to D55)". Read it whole; the tests are listed there. The
tests of `site_2024` carry a small index and job files of their own and do not read `ml/`.
Nothing of the 2025 pages under `/cgimages/` is changed or deleted (D54), and no full picture
goes to the server (D53).

- [x] PA1 `ml`: the gallery index names the thumbnail of each picture. Test first. Make the
      gallery index again and check that nothing else in it changed (2,368 threads, 5,661
      pictures) and that every named thumbnail is on disk.
      Done 2026-11-23. Each picture entry has `thumbnail_filename` (`thumbnail_name` of
      `rename_images.py`). New gallery index `data/images/gallery261123b.idx` (the CLI does
      not overwrite; `gallery261123.idx` stays): without that field it equals the old one,
      key order included; 2,368 threads, 5,661 pictures, 5,661 distinct thumbnail names,
      all on disk in `data/images/thumbs`.
- [x] PA2 `ml`: the step that writes the list of the thumbnails the gallery index names. Test
      first: the list holds exactly those.
      Done 2026-11-23: `imageGetter/thumbnail_list_cli.py` (function `thumbnail_filenames`
      in `gallery_index.py`), one name per line for `rsync --files-from`; it stops on a
      name with a line break or a thumbnail not on disk. Written:
      `data/images/thumbs261123b.txt`, 5,661 names, 54.8 MB. For PA9: no name holds a
      plain space; 15 hold U+202F (narrow no-break space), 6 a `#`, 3 a `%`. The check
      "a thumbnail whose name holds a space" uses one of the 15. 100 names start with `-`.
- [x] PA3 `site_2024`: the settings (path of the index, base address of the thumbnails) and
      the loading of the index, once in each worker. No setting, or a file that cannot be
      read: no pictures, one line in the log, the site works. Tests first, the log line
      captured.
      Done 2026-11-23 (`site_2024` `4ce6064`): `fwww/src/pictures.py` (`PictureIndex`),
      `site_app.Pictures`; `site.ini` `[PICTURES]` `INDEX = /app/gallery/gallery.idx`,
      `THUMBS_URL = /cgimages/pictures/thumbs`. The plan names `/cgimages/pictures` as the
      base; the setting is the thumbnails' own address so the code adds no `/thumbs`.
      The pages that show "the site works" without an index are tested in PA5 and PA6.
      `data/` is git-ignored in `site_2024` (plan's check). Full suite: 303 passed.
- [x] PA4 The one function that takes the documents of a job and the index and returns the
      threads with their pictures, in order, each thread once. Tests first: a thread in the
      provided and the related documents, a document of a newsletter, a link that does not
      start with `https://groups.google.com/`.
      Done 2026-11-23 (`site_2024` `f84300b`): `get_pictures` in `fwww/src/pictures.py`
      returns (provided threads, related threads not among them). A thread: subject, date,
      link (`url_from_source`), pictures (`thumbnail_url`, `url` or `None`). Full suite: 311.
- [x] PA5 The results page: the section under the answer and its short disclaimer, above the
      feedback buttons, at most 12 thumbnails, the link with the count. Tests of the plan
      first, through the page, also through the status response.
      Done 2026-11-23 (`site_2024` `d51897f`): `render_results` in `site_app.py` serves
      both the page and the status response; the cut to 12 is `first_pictures`. Thumbnails
      are shown at 120 x 120, `loading="lazy"`; links open in a new tab. The test app now has
      an empty gallery index (`conftest.py`), so no test gets the "No pictures" line by
      chance of order. Full suite: 326.
- [x] PA6 The pictures page `/cozyrag/<job id>/pictures`, with its 404 cases. Tests first.
      Done 2026-11-23 (`site_2024` `6dfee65`): `cozyrag_pictures.html`
      extends `layout.html` (the `/processid` page does not); a job without pictures gets
      "No pictures were found for this answer." The threads of both pages are one include,
      `picture_threads.html`. The 404 cases are in the existing tests of `test_pages.py`.
      Full suite: 342.
- [x] PA7 Local check with Tom before the review: settle how the local site shows the
      thumbnails without changing a file the server uses (plan, "Local check"). He looks at
      an answer with few pictures, one with over 12, the pictures page, a dig deeper and a
      narrow window. If he wants the look changed, report to Architect; do not restyle on
      your own.
      2026-11-23: local setup: index copied to `site_2024/data/gallery/gallery.idx` (sudo,
      `data/` is root's), `THUMBS_URL = http://127.0.0.1:8090` in `site_local.ini`, and
      `python3 -m http.server 8090 --bind 127.0.0.1 --directory ~/projects/ml/data/images/thumbs`.
      Tom moved the pictures below Provided Docs (D55 amended; note in `architect_todo.md`;
      `site_2024` commit "Show the pictures of an answer after the provided docs").
      Done 2026-11-23: Tom checked on the local site with the R2 fix loaded; the look stays
      as it is. Of the latest 150 local answers none has under 13 pictures, and job
      `7OCvxGFMr6` has 133 on its pictures page (the plan's measure was at most 80).
- [x] PA8 The compose line for the index directory; the upload commands for Tom (`rsync` of
      the listed thumbnails, then the index) and the check that the server holds every file
      of the list with its size. Short lines, and a line count beside any comparison.
      2026-11-23: compose line done (`site_2024` `25187e5`, `./data/gallery:/app/gallery:ro`).
      Done 2026-11-23: the upload commands and the check, below. Tar, SHA-256 and `scp`
      as for the Chroma tar, not `rsync`: Tom moves files that way, and `rsync` is not
      installed locally. The check is a SHA-256 of each file, which covers its size.
      Rehearsed locally into a scratch "server" directory: 5,661 files, 0 failures. With
      one file removed and one changed, the check printed 5 lines. Without
      `--verbatim-files-from`, tar reads the 100 names that start with `-` as options.
      Run by Tom on the server 2026-11-24, step by step: `df -h` 27 GB free on `/` (59 GB,
      54% used); `~/www/cgimages` is admin's, `~/site_2024/data` root's; `upload.sha256`
      3 OK; thumbnails 0 failures, 5661 files; `data/gallery` was empty; index hash
      `2f67e99e…8ca8`, equal to the one uploaded. The site does not read it until PA9.

      Local: make the upload directory (62 MB tar, 3.8 MB index).

          mkdir ~/pictures_deploy
          cd ~/projects/ml/data/images/thumbs
          L=../thumbs261123b.txt
          tr '\n' '\0' < $L | xargs -0 sha256sum -- \
            > ~/pictures_deploy/thumbs.sha256
          wc -l < ~/pictures_deploy/thumbs.sha256      # 5661
          tar -cf ~/pictures_deploy/thumbs.tar \
            --verbatim-files-from -T $L
          cp ../gallery261123b.idx ~/pictures_deploy/gallery.idx
          cd ~/pictures_deploy
          sha256sum thumbs.tar thumbs.sha256 gallery.idx \
            > upload.sha256

      Local: copy it to the server's home directory, as for the Chroma tar.

          scp -r ~/pictures_deploy <server>:~

      Server: free space for the record, owners, then the upload checked.

          df -h
          ls -ld ~/www/cgimages ~/site_2024/data
          cd ~/pictures_deploy
          sha256sum -c upload.sha256                   # 3 lines, each OK

      Server: the thumbnails, then the check. This assumes `admin` owns `~/www/cgimages`;
      if `ls -ld` showed root, stop and ask.

          mkdir -p ~/www/cgimages/pictures/thumbs
          cd ~/www/cgimages/pictures/thumbs
          tar -xf ~/pictures_deploy/thumbs.tar
          sha256sum -c --quiet \
            ~/pictures_deploy/thumbs.sha256 2>&1 | wc -l   # 0
          ls -A | wc -l                                # 5661

      Server: the index, after the thumbnails. `data/` is root's locally; `sudo` assumes
      the same there.

          cd ~/site_2024
          sudo mkdir -p data/gallery
          sudo cp ~/pictures_deploy/gallery.idx data/gallery/gallery.idx
          sha256sum data/gallery/gallery.idx
          grep gallery.idx ~/pictures_deploy/upload.sha256  # same hash

      `~/pictures_deploy` on the server is on the "Server cleanup" list.
- [ ] PA9 Code review of both repos, then merge with Tom's approval and deploy by the plan's
      "Delivery", ending with `docker compose restart nginx`. The checks of the plan, among
      them what a browser not signed in to Google gets from a click on a thumbnail, written
      down as seen. Add the upload and the index to the yearly steps of `imageGetter`
      (YU3). Report to Architect in a note in `architect_todo.md`: the checks, what the
      deploy left on the server, and anything in the design that did not fit the code.

#### Code review results (2026-11-23)

Reviewed, at Tom's request before PA7 and PA8 are finished: `ml` `a75299b..8bbe31f` (PA1,
PA2) and `site_2024` `main..d21cee0` (PA3 to PA6, the compose line `25187e5`, Tom's move
`d21cee0`). The PA8 commits still to come get a review of their own.

**Verdict: Not approved** (R1 is open).

Checked and fine: the code matches plan 4.2 and the tests cover every test the plan lists.
`site_2024` full suite: 343 passed, output clean. `ml` `imageGetter`: 170 passed, 12
skipped; every skip was there before this work. The job `source` values are the index's
thread ids (read from a real job). Subjects are escaped, thumbnail names percent-encoded,
and the author is never shown. Thumbnails are 200 x 200 squares, so `width="120"
height="120"` does not stretch them. `gallery261123b.idx` without `thumbnail_filename`
equals `gallery261123.idx` (compared). No list name starts with `#` or `;`. The loaded
index holds about 9 MB in each worker (tracemalloc).

- [x] R1 MUST FIX `docs/plans/programmer_todo.md` PA8: `site_2024` `25187e5` (the compose
      line of PA8) is committed, but PA8 is still `[ ]` and its notes do not mention the
      commit. Seen in the git log. Done: PA8 marked `[~]` and naming `25187e5`.
      Fixed: `ml` `e589235`.
- [x] R2 SHOULD FIX `site_2024/fwww/src/pictures.py:55`: an index that reads as a JSON
      object but lacks a field the page uses breaks every answer that has a thread with
      pictures. The likeliest case is uploading `gallery261123.idx` (no
      `thumbnail_filename`), which sits right beside `gallery261123b.idx`; the same applies
      to a thread without `metadata` or `images`, or a picture without `url`. Reproduced:
      `get_pictures` with the older index raises `KeyError: 'thumbnail_filename'`. Then
      `/processid` returns 500, and so does `/status`. On a 500, the polling page
      (`cozyrag_answer.html:19`) fails to parse the reply as JSON, stops polling, and never
      shows the answer. Plan 4.2 says an index that cannot be read gives no pictures and the
      site works. Done: `PictureIndex.read` treats an index whose entries lack those fields
      as unreadable (no pictures, one log line), tests first, the line captured. A PA8
      upload check alone is not enough, because the index is replaced by hand every year.
      Fixed: `site_2024` `4f85f9e` (`check_thread`; full suite 348). `gallery261123b.idx`
      loads whole; `gallery261123.idx` gives no pictures and one log line.
- [x] R3 SHOULD FIX `ml/imageGetter/thumbnail_list_cli.py:46`: the check that every listed
      thumbnail is on disk (the guard of the upload) is in the CLI and has no test.
      CLAUDE.md requires tests for all functionality. Read from the code, not tried. Done:
      a test where a thumbnail is missing, either for a function in `gallery_index.py` that
      the CLI calls or for the CLI itself run as a subprocess.
      Fixed: `ml` `aa27933` (`thumbnails_not_on_disk` in `gallery_index.py`). On the real
      data the CLI writes the same list as `thumbs261123b.txt`.
- [ ] R4 CONSIDER `site_2024/fwww/site_app.py:17`: since Tom's move (`d21cee0`), the
      pictures sit below Provided Docs and not directly under the answer. The name
      `PICTURES_UNDER_ANSWER` and its comment ("thumbnails shown under an answer") still
      hold loosely, but a name like `PICTURES_ON_RESULTS_PAGE` would fit the page as it is
      now. Read from the code.

For Architect: nothing. The D55 amendment is already in the Programmer's note in
`architect_todo.md`.

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

### Yearly update instructions (repo: `ml/`, modules `msgGetter/` and `imageGetter/`)

Asked for by Tom on 2026-11-23. Tom will run the message fetch and the image update himself
in about a year, alone, from the page. **Write for a reader who has forgotten everything:** he
knows what the project is and can use a terminal, and remembers no path, no command, no order
of steps and none of this year's surprises. Documentation only: no code change in this task. A
fault found while writing is reported to Tom, not fixed here.

The measure of done: Tom can go from "a year has passed" to new messages in `data/msgs_md` and
a new gallery index without asking anyone and without reading the code.

What exists today:

- `msgGetter/Readme.md`: five lines of steps and old notes. It names a script that does not
  exist (`process_messages.py`; the file is `process_message.py`), and says nothing of where
  the output lands or of anything found in 2026.
- `imageGetter/README.md`: the section "Yearly Update" has this year's seven commands in
  order, and "Prerequisites" has the Chrome setup. The file is written for the one who built
  it: it does not say what to expect from a step, how to tell that it worked, or what to do
  when it did not. The rest of the file (Phases 1 to 6) describes the build of 2025.

Tasks:

- [ ] YU1 Read both modules' code and the two READMEs, then settle with Tom, before writing:
      a. **Where the commands are run from.** The image download of 2026 ran with the
         Windows Python from the WSL directory (`\\wsl.localhost\...`). The message fetch
         of 2026 ran in the Windows clone (`C:\Users\tom\Documents\projects\ml`), an older
         copy with uncommitted edits, and its files were copied to WSL afterwards. Tom finds
         the clone brittle. Ask him which way the instructions describe. If he wants the
         message fetch run from the WSL directory too, that has not been tried: try it with
         him on a few ids before it is written down as the way. If it needs a code change,
         stop and report to Architect.
      b. **Where the instructions live.** Architect's suggestion: one section "Yearly Update"
         at the top of each module's README, complete in itself, and the top-level
         `README.md` procedure naming the two in order with what comes between and after
         them (the embedding and the deploy are not this task; name them and point to where
         they are described). `msgGetter/Readme.md` becomes `README.md` (`git mv`). Tom may
         prefer one file for both.
- [ ] YU2 `msgGetter`: the yearly fetch, written out. It must cover at least:
      - What the step is for and what it produces: the id list file, a `.md` per thread in
        `data/msgs_md`, a `.txt` per thread in `data/msgs`, and which later step reads which.
      - What has to be installed on Windows and how to check each: Python and its packages
        (give the `pip install` line and a command that shows they import), Chrome,
        ChromeDriver. For ChromeDriver: where to see Chrome's version, where to download the
        matching one, into which folder to unzip it so that the path written in the scripts
        finds it, and what the error looks like when the versions differ.
      - Starting Chrome on the debug port: the exact command, that every Chrome window is
        closed first, that Chrome needs a profile of its own for the port to open (found in
        2026 for the images; `chrome_with_debug.bat` names another profile folder: say which
        one is used and make the file and the text agree), how to check that the port is
        open, and that he signs in to Google Groups in that window.
      - The start date: where the last run's date is found (the name of the newest
        `msgids_*.txt`), which line of `get_msg_ids.py` to edit, and whether the range starts
        on the last run's end date or a day before it (the id files of 2025 and 2026
        overlap by a day; ask Tom which he wants and say why).
      - Each command, where it is run from, about how long it took in 2026, what the screen
        shows while it runs, and how to tell it finished well: the number of ids, the number
        of files written, where to look.
      - That it can be stopped and run again, and what it skips when run again.
      - **Known threads with new replies.** A thread that already has a `.txt` is passed
        over, so replies of the last year to an older thread are not fetched. In 2026 this
        was 10 threads; they were fetched again by moving their `.txt` and `.md` aside (D44).
        Write how to list such threads from the new id file and how to fetch them again,
        with the rule that a refetched file shorter than the one it replaces is not used.
      - Getting the files to where the next steps read them, if they are not written there
        (depends on YU1a), and a count that shows nothing was lost on the way.
      - The filter: what `f_filter.py` removes, that the `.txt` can be made again from the
        `.md` in WSL without Chrome, and the command for it.
      - A check at the end: how many new threads to expect (227 in 2026, for scale), opening
        two or three of the new `.md` files and what a good one looks like, and what the
        button text of his own posts looked like before the filter knew it.
      - What follows: the embedding. Name the step and where it is described; if it is
        described nowhere he could follow, say so in the report (YU5).
      - Troubleshooting, each with the message as it appears and what to do: ChromeDriver
        and Chrome versions differ; the debug port is not open; not signed in (what the
        fetched page then holds); Google slows or blocks the fetch; a thread that fails.
        Where a case has not been seen, say so instead of guessing its message.
- [ ] YU3 `imageGetter`: the section "Yearly Update" made complete in itself, on the same
      pattern. Keep the seven steps and add at least:
      - That it starts only after the messages are in `data/msgs_md`, and how to check that.
      - For each step: where it is run (WSL or Windows PowerShell), the command with the
        parts that change each year marked (the index name with its date and time, the log
        name, the gallery index name) and how to find this year's value, what it prints,
        about how long it took in 2026, and how to tell it worked.
      - The numbers of 2026 for scale: 2,631 threads and 6,811 entries in the index, 591
        downloaded with none failed, 346 new contents to review, 611 thumbnails, 2,368
        threads and 5,661 pictures in the gallery index.
      - The download: the Chrome setup in full here or by a link to "Prerequisites" that
        lands on the exact lines; that WSL has to be running; that PowerShell is needed and
        why cmd does not work; what a failed download looks like in the log and that running
        the step again fetches only what is missing.
      - The review tool, as a short user's guide: how to start it, the address to open, the
        three lists and which to do first, what the dashed frame means, what a click does,
        what the button at the end of a page does, that a decision is saved at once and can
        be changed but not undone, how to know he is finished (Suggested and New empty), how
        to stop the tool, and that `image_decisions.json` is then committed (give the git
        commands).
      - What a signature picture or other clutter looked like in 2026, in two or three
        examples in words, so that he recognises the kind.
      - What is left alone on purpose: files in `data/images` are never deleted by these
        steps; the copies `full_before_rename` and `thumbs_before_rename` belong to the one
        rename of 2026 and are not part of a yearly run; `rename_images_cli.py` and
        `load_removals_cli.py` were run once and are not run again.
      - What follows: how the thumbnails and the gallery index reach the site (plan 4.2,
        "Delivery"). If "Pictures of an answer" is deployed, write the step with the commands
        as run (PA9). If not yet, leave a line that says so and names the task.
      - Mark the older sections of the file (Phases 1 to 6) for what they are, so that he
        does not take them for steps of the yearly run. Do not delete them.
      - Troubleshooting, as in YU2.
- [ ] YU4 Proof by Tom. He reads both from the top and walks through them without help:
      every command that changes nothing is run (the checks, starting Chrome, the review
      tool on a scratch copy of the decisions); the others he reads and says what he would
      type. Every place where he stops to ask is a gap: fix the text, not the answer in the
      chat. A fresh fetch is not made for this.
- [ ] YU5 Top-level `README.md`: the update procedure names the steps in order and points
      to the two sections (its step 4 is empty today). Report to Architect in a note in
      `architect_todo.md`: what was settled in YU1, anything in the code that made the
      instructions awkward or that Tom should not have to do by hand (an edited constant,
      a path written in a script), and any later step of the yearly update that has no
      instructions he could follow.

Rules for the writing:

- Every command is one he can paste: full paths or the `cd` before it, and no placeholder
  without a line that says how to find the value.
- A command is written down only if it was run this year or is run now, and the text says
  which. Nothing is described from reading the code alone without saying so.
- One step, one action, one way to tell it worked. Short sentences. No "simply" and no
  "as usual": there is no usual after 12 months.
- Dates and versions of 2026 are given as examples and marked as such (Chrome and
  ChromeDriver 158, Python 3.13 on Windows).
