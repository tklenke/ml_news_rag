# Programmer Todo

**Last Updated:** 2026-11-24

# ACTIVE: Annual RAG / Website Refresh

**READ FIRST: `docs/plans/annual_refresh_plan.md`.** Read the whole document before any
task, every session. The tasks below are only a checklist; section numbers refer to the plan.

**Branches:** `wip/annual-refresh` in `ml/` and in `../site_2024/`.

**Order:**

1. 2.2d, the report on the chunk experiment's embedding ("Phase 2").
2. "Collapsed posts" (CP1 to CP8, D58).
3. "Reference links" (RL1 to RL8, D60).
4. The rest of Phase 2 (2.3 to 2.5, D41).

"Server cleanup" is done with Tom from 2026-11-28. One session per group; start each session
fresh. Code review happens once per deploy, not per commit.

**Deploys.** The rules are in `CLAUDE.md`, "Deploys and server work". The yearly update
(fetch, pictures, embedding, deploy) is in the top-level `README.md`; a deploy of the site's
code alone is in the `site_2024` README, "Deploy a change of the code". nginx looks up the
name `flask` only when it starts: a deploy or rollback that recreates the flask container
ends with `docker compose restart nginx`. Keep lines for the server short: a long line
wrapped when pasted and broke a `grep` pattern. Print a line count beside any comparison of
two outputs.

All code tasks follow TDD. Escalate design questions to Architect; do not resolve them yourself.

Everything deployed so far (the server runs `site_2024` `4f85f9e`) is under "Done" at the
end, with the facts still worth knowing. Task details of finished work are in the git
history of this file. The finished image database tasks are in
`docs/archive/programmer_todo_image_database.md`.

## Phase 2: Chunk-size experiment (repo: `ml/`)

Plan 2.1 to 2.4. 2.1a to 2.2c are done; all five variants had run on 2026-11-23 21:57.

Do not write to the Chroma on port 8000 and do not stop or change a container of `site_2024`.

- [x] 2.2d The five checks of plan 2.2a, reported in a note in `architect_todo.md`
      (2026-11-24, `7ebd92d`): every check passed. Tom removed the GPU Ollama container
      (`chunk_experiment_ollama`) the same day; the experiment's Chroma stays for 2.3.
- [ ] 2.3 Pooling: write `chunk_labels.csv` for Tom, one batch of 10 questions at a time (plan 2.3)
- [ ] 2.4 Scoring: compute the four metrics per variant from Tom's labels, rerun after
      each batch (plan 2.4)
- [ ] 2.5 Question set is the three batches plus the `chunk_only` rows of
      `refresh_questions.csv` (40 questions, plan 2.3). `reserve` rows are not used unless
      Architect says so.

Still useful:

- `chunksplitter` takes an overlap (default 0 gives the present chunks).
- `embedder.py` takes chunk size, overlap, `--collection`, Chroma port, Ollama port and
  `--sources`, with a progress file per collection; with no parameters it does what it did. A
  chunk size or overlap without `--collection` is refused. A file that fails is logged and
  left out of the progress file; 20 failures in a row end the variant.
- The queue is `embedder/chunk_queue.py` (A, C, B, D, E; `start` and `stop`). Log:
  `data/chunk_experiment/queue.log`; `END ... exit code 1` means files failed (search for
  `FAILED`).
- The experiment's Chroma is on port 8010 (data in `data/chunk_experiment/chroma`; an empty
  `defaultdb` stays in it), the GPU Ollama on port 11998. The commands they were made with:

      docker run -d --name chunk_experiment_chroma -p 127.0.0.1:8010:8000 \
          -v /home/tom/projects/ml/data/chunk_experiment/chroma:/data chromadb/chroma:1.5.9
      docker run -d --name chunk_experiment_ollama --gpus all \
          -p 127.0.0.1:11998:11434 site_2024-ollama-rag

- 0.239 s per chunk at 250 words, storing included.

## Collapsed posts (repo: `ml/`, D58)

Plan: "Collapsed posts (D58)". Read all of it; the numbers and the hypothesis are there. Do
2.2d first: the refetch changes files its first check reads. Never delete a file of
`data/msgs` or `data/msgs_md`: set it aside. Nothing is fetched into `data` before CP3 is
done.

- [x] CP1 The cause, with Tom at Chrome on Windows. Reproduce into a scratch directory; show
      what the page held when it was read and why; look at three of the older single-post
      files in a browser. No fix yet.
      Done 2026-11-24: the "Expand all" click has no effect while Chrome is minimized (4 of 5
      fetches stayed collapsed for 15 s; 47 fetches on screen, none). The wait before the
      click is not a cause. The step 8 check flags headings inside posts: 25 threads of 2026
      are affected, none older; the three older files are whole (each post has its address
      line). The probe and its runs are in `data/collapsed_probe/` (git-ignored). The random
      part of the wait before the click is Tom's, to keep Google from taking the fetch for
      scraping: the fix keeps it. Tom did not say whether the older threads looked whole in
      Chrome; the files were compared with the live post counts instead.
- [x] CP2 Report the cause in a note in `architect_todo.md` and tell Tom. Go on to CP3 if the
      cause is one of timing and the plan's points for the fix fit it; otherwise stop for
      Architect.
      Reported 2026-11-24. Not one of timing: waiting for the page does not help while the
      window is minimized. **Stopped for Architect**, who chooses how the page is made to
      expand (three options in the note). CP3 waits for that.
      **Tom decided 2026-11-25: option 1**, the debug Chrome stays on screen during the
      fetch, written in the README; the check keeps a collapsed thread from being saved.
      Architect not asked (Tom's waiver). Option 2, the switches, was tried and does not
      work (note in `architect_todo.md`).
      **Correction 2026-11-25:** "none older" in CP1 is wrong. Older files put `### name`
      in the middle of a line, after the profile photo; the CP1 sign only looked at lines
      that start with it. With the sign anywhere in a line: 33 threads, 25 of 2026 and 8
      older, all in the pattern "every post but the last collapsed". None of the 214
      collapsed posts has "Reply to author" in its preview.
- [x] CP3 The fix, tests first (plan, step 3): a thread is saved only with no post collapsed;
      one that stays collapsed leaves no file, is printed and counted, and the run goes on;
      one function for the check, used by the fetch and by a command that lists the affected
      threads.
      Done 2026-11-25 (`8748394`, `128734e`): `msgGetter/f_collapsed.py` (the check, and as a
      command the list: 33 today); the fetch reads the page again for up to 15 s until no
      post is collapsed, else does not save, prints and counts; a saved `.md` with a
      collapsed post gets no `.txt`. 15 tests on five shortened real threads. The waiting
      itself is not tested (needs Google's page): CP4 is its check. README step 6 says to
      keep Chrome on screen; step 8 runs the command.
- [x] CP4 The refetch with Tom (`msgGetter/README.md` steps 5 to 7; you supply the id file).
      Take a thread over only if its new copy has no collapsed post and at least as many
      posts. Report the threads not taken over. Pass mark: none of 2026 left collapsed.
      In the same run the 60 ids of 2024-25 that were never fetched (D59; plan, step 4),
      from an id file of their own in `data`. They go through CP5 and CP6 as new threads.
      When the 60 are fetched, `git rm msgGetter/msgids_2024-09-03_2025-10-02.txt` (Tom
      approved 2026-11-24) and take its paragraph out of `msgGetter/README.md`.
      Done 2026-11-25. Tom ran the fetch of 93 ids (33 set aside in
      `data/collapsed_backup`, ids in `data/collapsed_ids.txt`; 60 from
      `data/msgids_never_fetched_2024-09-03_2025-10-02.txt`), Chrome on screen: 93 saved, 0
      not saved, 391 s. All 33 taken over: no collapsed post and the same number of posts as
      the old copy, each of them. All 60 came back as threads with a title; 15 printed "no
      exapansion found", all single-post threads (no button). `f_collapsed.py`: 0 left.
      Pass mark met. The msgGetter copy of the id file removed from git.
- [x] CP5 The pictures: the index built again; if it names pictures not on disk, the download
      and Tom's review, the gallery index and the thumbnails. Say which it was.
      Done 2026-11-25: the index (`index261125103303.idx`) named 152 pictures not on disk, all
      from 42 of the 93 threads (69 of them in 19 of the 33 collapsed ones). Tom downloaded
      them (0 failed) and reviewed 129 new contents, all kept (`40d5b29`). 152 thumbnails
      made; 1 fails, `eJJziZ0ar3U_..._Ahaa.jpg` of 2025, truncated, in neither gallery: not
      this work. `gallery261125.idx`: 2,407 threads, 5,795 pictures (was 2,368 and 5,661);
      `thumbs261125.txt`: 5,795, 56.2 MB. Both go up in CP7. The review tool's port 8765 was
      taken by another project; it ran with `--port 8790`.
- [x] CP6 The embedding into the production collection (`embedder/README.md`) and the three
      local checks of the plan, step 6. Not the chunk experiment's collections.
      Done 2026-11-25. Before: local and server both `42276 92d43eed...` (server read by Tom).
      58 old chunks of the 33 deleted, 93 threads embedded, 359 chunks, 0 failed, 191 s.
      After: `42577 4e273635c3dec63f1e61d6c3847619ef2950ad8e6d37e7ef93fc3bfff0a1d3a5`
      (`~/update_records/after.txt`), 11,448 sources = files = `embedstatus.txt` lines.
      (1) Every source's chunks are its file's chunks: missing 0, extra 0. (2) Top 15 of the
      52 questions (`data/collapsed_update/before.json`, `after.json`): 4 questions changed,
      5 chunks entered (3 refetched, 1 new of 2024-25, 1 other). (3) "On the N249PM test
      flight, how did the plane behave at 3,000 AGL and what were the CHTs?" returns
      `SVdmlqx3aco#1` at rank 5, text the old copy did not have. The 33 gained 29,993 words.
      Server step 3's heredoc got stuck in Tom's paste (wrapped lines indent the closing
      `PY`); a one-line `python -c` worked. To correct in the README in CP7.
**Tom, 2026-11-25: CP7 and CP8 wait until the citations (RL1 to RL8) are done.** Until
then the local collection (`42577 4e273635...`) is ahead of the server's (`42276
92d43eed...`, `~/update_records/before.txt`). At the deploy, step 3 compares the server with
`before.txt`, not with the local collection, which has changed on purpose. Do not embed
into the local collection or reset it before then. The evaluation's 30 saved prompts name
none of the 33 refetched threads, so RL2 is not affected by the deleted chunks.

- [ ] CP7 Code review, then the deploy with Tom by the top-level `README.md` (steps 3 and 5
      to 8). Correct the README wherever a step does not work as written.
- [ ] CP8 `msgGetter/README.md` step 8 and troubleshooting say what the fetch does now; the
      note in `docs/notes/opportunities_for_improvement.md` if anything is left. Report to
      Architect: the cause, the threads repaired and not, pictures gained, chunks before and
      after, what the deploy steps needed corrected.

## Reference links (repo: `../site_2024/`)

Plan: "4.1 Reference links inside answers". Read all of 4.1, with the paragraphs marked
twentieth revision; the tests are listed there. After "Collapsed posts". Tom has decided
that the citations are built (D60), so the run below does not decide whether the display is
built, only whether the setting is switched on at the deploy. Until then the setting stays
off, and with it off every prompt is what it is today.

- [x] RL1 `build_prompt` numbers the chunks when told to, with the plan's wording, for all
      three kinds of prompt; the setting in `site.ini`, off; the record says whether an answer
      was numbered. Tests first, the first of them that the prompts with numbering off are
      unchanged.
      Done 2026-11-25 in `site_2024` (`8ce8a30`, `cf29c7f`): `build_prompt(...,
      numbered=)`; `[PROMPTS] NUMBER_DOCS = False` in `site.ini`; `numbered_docs` in every
      record. The wording sits before the `-----` of a first prompt (as the probe had it)
      and at the end of the revise and follow-up instructions. A test pins the three
      prompts of today character for character. 366 tests pass.
- [x] RL2 The run: the 30 questions, `gpt-6-luna`, the chunks fetched by the ids saved with the
      evaluation's prompts. Before any paid call: with numbering off, the prompt built from
      the fetched chunks equals the saved prompt, for each question; report those where it
      does not and leave them out. Answers into a directory of their own. Then the paid run
      (about 3 cents); tell Tom before it starts.
      Done 2026-11-25 in `site_2024` (`2bd5cb1`, `evaluation/cite_trial.py`, 6 tests). Check:
      29 of 30 prompts rebuilt equal; Q08 left out, its chunk `x3XodjGpYTU1` is gone (the
      thread was refetched in the corpus update, new ids `x3XodjGpYTU#n`). Paid run (Tom's
      go): 29 answered, 0 failed, $0.0209, into `evaluation/output/cite_trial/` (git-ignored),
      log `evaluation/output/cite_trial_run.log`.
- [x] RL3 The counting script of the plan, tests first, and its output for the run.
      Done 2026-11-25 in `site_2024` (`7e60f08`, `evaluation/count_citations.py`, 21 tests).
      Report in `evaluation/output/cite_trial_count.md` (git-ignored). Of 29: without a number
      1 (Q05: "The provided context doesn't say where Desser Monster retreads can be
      purchased."); numbers naming no chunk 0; other forms 0; lists of sources 0; no `[2, 5]`
      form. Medians trial / rated: completion tokens 516 / 560, reasoning 253 / 324, latency
      4.81 / 5.39 s, cost $0.00073 / $0.00074. A parenthesis counts as another form only when
      it holds only numbers or a number with a word for a piece of context ("source",
      "piece", ...): taken literally, "digits and other text" would list every "(5.15 m)".
      Every bracket of the 29 answers was also read by a script: none outside `[n]`.
- [x] RL4 Report to Architect in a note in `architect_todo.md`: the counts, the questions left
      out, the answers without a number (by question id). Do not apply the rule yourself and
      do not change the wording of the prompt: both are Architect's. Go on with RL5 without
      waiting.
      Done 2026-11-25: note in `architect_todo.md`.
- [ ] RL5 The display (plan 4.1b), tests first, in the order of the plan's list of tests: the
      rows of the source list numbered by the code that reduces the record to one row per
      source; the renderer shows the row number of a chunk's source as a link; marks that
      follow each other shown once per source; a number that names no chunk left out; the
      stored answer unchanged.
- [ ] RL6 The definition `[1]: https://...` no longer read by the answer renderer; check that
      none of the 90 archived answers is shown differently for it and report the number.
- [ ] RL7 Show Tom the local site with the setting on: three first answers, a dig deeper and a
      follow-up (plan 4.1a, "Looked at by Tom"). Do not deploy before he has said yes and
      Architect has recorded that the rule holds.
- [ ] RL8 Code review, then the deploy of the plan (4.1b, "Deploy") with Tom, in small blocks.
      Report to Architect in `architect_todo.md`.

## Server cleanup (with Tom)

Leftovers kept on the server as the rollback for each deploy. Add to this list whenever a deploy
leaves something behind. An entry waits a week (Tom, 2026-11-24). Until an entry is done, no
`docker system prune` on the server.

Still Tom's choice, on no schedule: `server/old.nginx_all_apps.conf`,
`server/certbot/conf/live/m24tom.old`, `~/project.tar.gz`, `~/certbot_bu.tar`, the exited
`hello-world` container. Keep `certbot/certbot:latest`: the certificate renewal uses it.
The entries of the Phase 0, Phase 1 and pictures deploys were done on 2026-11-24; a rollback
of the code to before the pictures now needs a rebuild of `775692d`.

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

## Done

Deployed: Phase 0 (2026-11-21, `bed83f4`), the Phase 1 code change and site fixes
(2026-11-21, `3278e9e`), the follow-on fixes (2026-11-22, `c311cda`), the answer display, the
corpus update and the model change (2026-11-22, `775692d`), the pictures of an answer
(2026-11-24, `site_2024` `4f85f9e`, `ml` `72957f4`). Done and not deployed: the model
evaluation, the image update (plan 4.0), the yearly update instructions (D57). Tom waived the
code reviews, in whole or in the rest.

Still useful, the server:

- Docker 29.10.0 and Compose 5.8.0 (the local rehearsals used 28.3.2 and 2.39.1); a 2 GB swap
  file; gunicorn runs 2 workers.
- Rebooted 2026-11-24: the four containers come up on their own and nginx finds `flask`
  without a restart. `swapon` is in `/sbin`, not on `admin`'s path; `free -h` shows the swap.
- Known log warnings: gunicorn wants its config file to have a `.py` extension; Ollama reports
  the requested context (8192) exceeds the embedding model's 2048. Neither investigated.
- Not exercised on the server: the rollback in `sudo_renew_cert.sh`. Do not run the renewal
  script while the code is rolled back to before `c311cda`.
- The tracked `site.ini` holds the server's values; the keys are in the git-ignored
  `site_local.ini`. Never print that file.
- No nginx rate limit (D25). A real response of a used-up OpenAI budget has not been seen
  (D33); a failed job was not checked on the live site.

Still useful, `site_2024`:

- Running the tests: `site_2024/README.md`. Use `site_2024/.venv`; `site_2024/venv` still holds
  the old stack. The tests need docker, node and openssl. Those that read the collection need
  the local Chroma (`docker compose up -d chroma-rag`); the page tests use Flask's test
  client. The tests do not read `ml/`; a test carries its own data.
- `python-dotenv` stays in `requirements.txt` because `pydantic-settings` requires it.
- The HTML of an answer comes from one function (`fwww/src/answer_html.py`, `markdown-it-py`),
  used by the results page and by `evaluation/review_answers.py`. The site's own pages keep
  `markdown_to_html`.
- A job's `result` holds the model name OpenAI returned, and the results page shows it.
- An exception in the job thread (Chroma or Ollama unreachable) ends it; with Architect (S8).
- The evaluation scripts are in `site_2024/evaluation/` and are not used by the site:
  `answer_models.py` (paid; needs Chroma, and Ollama for a question without a saved prompt),
  `review_answers.py`, `tally_ratings.py`, `export_answers.py`. Run from `site_2024`:

      PYTHONPATH=fwww .venv/bin/python evaluation/tally_ratings.py batch1 batch2 batch3

- The ratings and key are in `docs/archive/first_answer_ratings`, the answers of the three
  models beside them. The prompts are only in `evaluation/output/` (git-ignored), because
  they can hold email addresses. `evaluation/output/trial` holds random clicks, not ratings.

Still useful, the collection:

- 42,276 chunks of 11,388 sources (2026-11-22), id hash `92d43eed...`; 42 prefix-only chunks
  are still in it. Chunk ids are `<source>#<number>`.
- For the production collection only the containers of `site_2024` are used; do not start
  those of `ml/docker-compose.yaml`.
- `data/corpus_update/`: `before.json`, `after.json` and `snapshot.py`, which made them (count,
  id hash, top 15 of the 52 questions). The tar and check script of that deploy:
  `~/chroma_deploy` (local).
- The repair F2 was stopped after about 3,360 of 36,500 chunks and was not finished (D46). It
  continues from `embedder/` with `../venv/bin/python repair_collection.py 11998`.

Still useful, the pictures:

- Never delete or overwrite a file in `data/images` or `imageGetter/input`. Both and `data/`
  are git-ignored: a test carries its own small pictures.
- Gallery index: `data/images/gallery261123b.idx` (2,368 threads, 5,661 pictures), made by
  `gallery_index_cli.py`; the server has it as `data/gallery/gallery.idx`. It drops by
  decision only and stops on a file on disk that is not measured.
- Working index: `data/images/index261123105058.idx`, built from `data/msgs_md` and measured
  by `measure_images_cli.py`.
- Decisions: `imageGetter/image_decisions.json` (tracked; content hash to `remove` / `keep`);
  nothing is undecided. The review tool is `review_images_cli.py`, port 8765.
- Run once in 2026 and not again: `rename_images_cli.py` and `load_removals_cli.py`.
- A local name: each of `< > : " / \ | ? *` becomes `_`, at most 180 bytes, extension kept.
- The download rewrote the index with CRLF; the content was unchanged.
- `test_handle_download_failure` passes only because a Mock's `get_cookies()` cannot be
  iterated (told to Tom). The review tool's page script is checked for syntax only.
- One full-suite run had 7 failures that four runs after it did not repeat; which tests is not
  known. If it comes back, keep the whole output.

Still useful, the yearly update:

- The getters run with the Windows Python from cmd via `pushd` into the WSL folder,
  `chrome_with_debug.bat` for both modules, ChromeDriver in
  `/home/tom/projects/chromedriver-win64`. The Windows clone is deleted.
- The trial of the fetch: `docs/plans/yu1_fetch_trial.md`.
