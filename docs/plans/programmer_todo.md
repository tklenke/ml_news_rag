# Programmer Todo

**Last Updated:** 2026-11-26

# ACTIVE: Annual RAG / Website Refresh

**READ FIRST: `docs/plans/annual_refresh_plan.md`.** Read the whole document before any
task, every session. The tasks below are only a checklist; section numbers refer to the plan.

**Branches:** `wip/annual-refresh` in `ml/` and in `../site_2024/`.

**Stopped for this year (Tom, 2026-11-26).** Both repos are merged to `main` and pushed
(`ml` `1784972`, `site_2024` `4bcdd79`). Three groups below are still open. For each, Tom
has not yet decided whether it is finished, dropped or deferred to 2027; ask him before
starting any of them:

1. CP8 is not done. `msgGetter/README.md` step 8 and its troubleshooting do not yet say
   what the fetch does now, and the report to Architect is not written. The yearly update
   of 2027 runs from that README.
2. Phase 2 stops before the labelling (2.3). The five collections stay in
   `data/chunk_experiment/`.
3. Server cleanup is not done. The rollback copies stay on the server, and the check of the
   world-writable directories (D59) has not been made. Until each entry is done, no
   `docker system prune` on the server.

**Order:**

1. CP8, the closing report of the collapsed posts.
2. Phase 2 (2.3 to 2.5, D41).

"Server cleanup" is done with Tom from 2026-11-28. One session per group; start each session
fresh. Code review happens once per deploy, not per commit.

**Deploys.** The rules are in `CLAUDE.md`, "Deploys and server work". The yearly update
(fetch, pictures, embedding, deploy) is in the top-level `README.md`; a deploy of the site's
code alone is in the `site_2024` README, "Deploy a change of the code". nginx looks up the
name `flask` only when it starts: a deploy or rollback that recreates the flask container
ends with `docker compose restart nginx`. Keep lines for the server short: a long line
wrapped when pasted and broke a `grep` pattern. Tom's paste puts two spaces before every
line: a heredoc's closing word then never matches, and Python sent by `python -c` must start
`"if 1:` with an indented body (top-level README, step 3). Print a line count beside any
comparison of two outputs.

All code tasks follow TDD. Escalate design questions to Architect; do not resolve them yourself.

Everything finished (the server runs `site_2024` `4bcdd79`) is under "Done" at the end, with
the facts still worth knowing. Task details of finished work are in the git history of this
file (CP1 to CP6 and RL1 to RL6 at `4a1cf3a`; RL7, the code review R1 to R5 and the deploy
DP1 to DP6 at `247b98b`). The finished image database tasks are in
`docs/archive/programmer_todo_image_database.md`.

## Collapsed posts: closing (repo: `ml/`, D58)

Plan "Collapsed posts", "As found and built". CP1 to CP7 are done; CP7 was the deploy of
2026-11-26.

- [ ] CP8 `msgGetter/README.md` step 8 and troubleshooting say what the fetch does now; the
      note in `docs/notes/opportunities_for_improvement.md` if anything is left. Report to
      Architect: the threads repaired and not, pictures gained, chunks before and after.
      The cause is already recorded in the plan. Tom accepted review finding R4 as it is
      (2026-11-26): a thread whose old `.md` holds a collapsed post is read from that `.md`
      and never fetched again; the troubleshooting can say to set such a `.md` aside.

## Phase 2: Chunk-size experiment (repo: `ml/`)

Plan 2.1 to 2.5. The five variants are embedded and Architect found them fit for the
labelling (plan 2.2a, "Result").

Do not write to the Chroma on port 8000 and do not stop or change a container of `site_2024`.

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
  chunk size or overlap without `--collection` is refused.
- The experiment's Chroma is the container `chunk_experiment_chroma` on port 8010 (data in
  `data/chunk_experiment/chroma`; an empty `defaultdb` stays in it). The collections are
  `words250_overlap0`, `words150_overlap0`, `words400_overlap0`, `words250_overlap50` and
  `words400_overlap80`. The GPU Ollama container is removed; to embed a question, the
  site's Ollama on port 11434 has the same model.
  The command the Chroma container was made with:

      docker run -d --name chunk_experiment_chroma -p 127.0.0.1:8010:8000 \
          -v /home/tom/projects/ml/data/chunk_experiment/chroma:/data chromadb/chroma:1.5.9

- The collections were made before the refetch of 2026-11-25: they lack the 60 threads of
  D59 and hold the 33 repaired threads as they were. They are not embedded again (plan,
  "Collapsed posts").
- The checks of the embedding: `data/chunk_experiment/check_variants.py` and `checks.json`.

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

      The local leftovers of this deploy were deleted 2026-11-24. Since 2026-11-26 the
      rollback of the data goes back two collections: it also drops the repaired threads.

- [ ] **From the deploy of the citations and the repaired collection (2026-11-26).** Not
      before 2026-12-03, and only if Tom says the site has run well. By the top-level
      `README.md`, step 8, with `OLD=4f85f9e; D=261126`: the check block first, the removal
      in a later block. On the server: `~/chroma_before_261126` (the collection of
      2026-11-22), `~/gallery_before_261126.idx` (`gallery261123b.idx`), `~/update_deploy`,
      and the image name `site_2024-flask:4f85f9e`, which has the same ID as `latest`
      (`c0bbdf9222ee`): removing it removes only the name. Locally, by the same step:
      `~/update_deploy` and `~/update_records`. There is no `data/refetch_backup` this
      year; the old copies of the repaired threads are in `data/collapsed_backup` and stay.

      The ways back are the README's "The way back" with those values (not run). For the
      citations alone the setting off is enough: revert `4bcdd79`, push, then on the
      server `git pull` and `docker compose restart flask` (the settings are read at the
      start; the container is not recreated, so nginx needs no restart).

- [ ] **World-writable directories (D59).** With the full cleanup, after the server has run
      for a week: `~/site_2024`, `~/www` and `~/chroma_before_corpus_update` are
      world-writable. First a read-only step that shows why (who owns them, which user the
      containers write as); change nothing before Tom and Architect have seen it.

## Done

Deployed: Phase 0 (2026-11-21, `bed83f4`), the Phase 1 code change and site fixes
(2026-11-21, `3278e9e`), the follow-on fixes (2026-11-22, `c311cda`), the answer display, the
corpus update and the model change (2026-11-22, `775692d`), the pictures of an answer
(2026-11-24, `site_2024` `4f85f9e`, `ml` `72957f4`), the citations with the repaired
collection (2026-11-26, `site_2024` `4bcdd79`, `ml` `247b98b`). Done and not deployed: the
model evaluation, the image update (plan 4.0), the yearly update instructions (D57). Tom
waived the code reviews of the deploys so far, in whole or in the rest.

Still useful, the collapsed posts (deployed 2026-11-26):

- "Expand all" does nothing while the debug Chrome is minimized: it stays on screen during a
  fetch (`msgGetter/README.md`, step 6). The fetch reads the page again for up to 15 s and
  saves no thread that still holds a collapsed post; it prints and counts it. That waiting
  has no test (it needs Google's page).
- `msgGetter/f_collapsed.py` is the check, and as a command it lists the affected threads
  of `data/msgs_md` (0 today).
- Never delete a file of `data/msgs` or `data/msgs_md`: set it aside. The old copies of the
  33 repaired threads are in `data/collapsed_backup`, their ids in `data/collapsed_ids.txt`;
  the 60 ids of D59 in `data/msgids_never_fetched_2024-09-03_2025-10-02.txt`. The probe and
  its runs are in `data/collapsed_probe/`.
- Top 15 of the 52 questions before and after the repair are in `data/collapsed_update/`.

Still useful, the citations (deployed 2026-11-26, setting on; `site_2024` `4bcdd79`):

- `build_prompt(..., numbered=)` numbers the chunks; the setting is `[PROMPTS] NUMBER_DOCS`
  in `site.ini`, on; every record holds `numbered_docs`. A test pins the three prompts of
  today character for character. Do not change the wording of the prompt: it is Architect's.
- `get_result_for_display` numbers the rows of the source list and gives `citations`;
  `get_answer_html(text, citations)` makes the links. The rating page passes no citations
  and shows its answers as before. The renderer reads no link definitions (`[1]: https://`),
  and a mark inside a link the answer writes itself stays as written.
- The trial: `evaluation/cite_trial.py` (paid) and `evaluation/count_citations.py`; answers
  in `evaluation/output/cite_trial/`, report in `cite_trial_count.md` (git-ignored). Q08
  cannot be rebuilt from its saved prompt: its chunk ids changed in the corpus update.
- 412 tests passed at `4bcdd79`.

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
- The local site shows thumbnails only while a server on port 8090 runs (`site_local.ini`):
  `python3 -m http.server 8090 --bind 127.0.0.1 --directory data/images/thumbs`, from `ml/`.
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

- On the server and locally: 42,577 chunks of 11,448 sources (2026-11-26), id hash
  `4e273635...` (`~/update_records/after.txt`); 42 prefix-only chunks are still in it.
  Chunk ids are `<source>#<number>`.
- For the production collection only the containers of `site_2024` are used; do not start
  those of `ml/docker-compose.yaml`.
- `data/corpus_update/`: `before.json`, `after.json` and `snapshot.py`, which made them (count,
  id hash, top 15 of the 52 questions).
- The repair F2 was stopped after about 3,360 of 36,500 chunks and was not finished (D46). It
  continues from `embedder/` with `../venv/bin/python repair_collection.py 11998`.

Still useful, the pictures:

- Never delete or overwrite a file in `data/images` or `imageGetter/input`. Both and `data/`
  are git-ignored: a test carries its own small pictures.
- Gallery index on the server since 2026-11-26: `data/images/gallery261125.idx` (2,407
  threads, 5,795 pictures; thumbnails listed in `thumbs261125.txt`), made by
  `gallery_index_cli.py`; the server has it as `data/gallery/gallery.idx`. It drops by
  decision only and stops on a file on disk that is not measured.
- Working index: `data/images/index261125103303.idx`, built from `data/msgs_md` and measured
  by `measure_images_cli.py`.
- One thumbnail cannot be made: `eJJziZ0ar3U_..._Ahaa.jpg` of 2025 is truncated and in
  neither gallery.
- Decisions: `imageGetter/image_decisions.json` (tracked; content hash to `remove` / `keep`);
  nothing is undecided. The review tool is `review_images_cli.py`, port 8765 (another
  project may hold it; `--port 8790` works).
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
