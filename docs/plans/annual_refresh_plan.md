# Annual RAG / Website Refresh Plan

**Created:** 2026-11-21
**Status:** Revised 2026-11-22 (eleventh revision); Phase 0, the Phase 1 code change and the follow-on fixes deployed (`c311cda`); models chosen; the answer display is designed and deploys with them
**Owner:** Architect (design), Programmer (implementation)

## Design Revision History

- **2026-11-22 (eleventh revision):** The UI changes that deploy with the model change
  are designed ("Answer display"). They are the display of answers only (D39): tables,
  lists that follow a text line directly, and S3. Answers are rendered by
  `markdown-it-py` with raw HTML off (D40), which Tom chose after seeing the archived
  answers rendered both ways. S3 is closed by that renderer and no longer waits for the
  reference links; no allow-list sanitiser is added. A job does record the model that
  answered it; the tenth revision said otherwise.
- **2026-11-22 (tenth revision):** The evaluation is done and recorded as it was run.
  Tom decided that only the first answer is evaluated (D35), chose `gpt-6-luna` for it
  and `gpt-6.2-sol`, not evaluated, for dig deeper (D36), and wants the model change
  deployed together with UI changes that are still to be designed (D38). 1.2 to 1.6
  until now described two evaluated tiers. The rule that recognises a used-up OpenAI
  budget is the one Tom approved and the Programmer built, from OpenAI's documentation
  (D33 table). The follow-on fixes are deployed (`c311cda`).
- **2026-11-22 (ninth revision):** Two findings of the code review of the follow-on
  deploy, decided by Tom. A failed OpenAI call now ends the job in `error` like any other
  failure, and where Tom has to act the visitor is shown the reason to pass on (D33;
  "OpenAI failures and the reason shown"). Until now the error text was saved as the
  answer of a `complete` job, and replaced the draft on a failed revise (R4). A job file
  read in the moment it is still empty is accepted as it is (D34, R5).
- **2026-11-22 (eighth revision):** The certificate also covers `www.m24tom.com`, and
  nginx sends `www` to `m24tom.com` (D32; "The `www` name"). Until now `www` resolved to
  the server and showed a certificate warning over HTTPS. Joins the follow-on deploy.
- **2026-11-22 (seventh revision):** Three decisions by Tom after the Phase 1 deploy,
  shipped together as one small deploy (see "Order of work", step 3). A follow-up no
  longer sends a chunk twice (D29; 1.1 item 8): the plan had not said, and the paid run
  sent 6 and 5 of 15 chunks in both places. An exception in the job thread no longer
  silences the worker (D30; S12): the Programmer found that any exception ends the
  thread until a restart. The containers start again after a server reboot (D31).
- **2026-11-21 (sixth revision):** Tom decided what revise and follow-up receive (D26,
  D27; 1.1 items 6 to 8). Correcting the garbled prior context (1.1 item 1) showed what
  the code had always meant to send: up to 60 chunks to a revise, and those plus 60 new
  ones to a follow-up, growing with each further follow-up. The job record also kept
  one chunk per source, so a revise lacked text the draft was written from. The
  missing space after `search_query:` is closed by measurement: it changes nothing
  (1.1, "Checked and left alone").
- **2026-11-21 (fifth revision):** S2 has no nginx rate limit (D25). The OpenAI budget
  has no auto reload, so abuse can use up the budget and no more; a limit in nginx
  would add a part without lowering that ceiling. In its place a question's job starts
  when the question is submitted, so reading a page never pays for an answer.
- **2026-11-21 (fourth revision):** Phase 0 is deployed (`bed83f4`) and the certificate
  is renewed to 2027-02-20. Memory was measured again; gunicorn runs 2 workers and the
  server has a swap file (D23). All four candidate models answer the production call
  (0.7); two of them spend reasoning tokens, so the evaluation runs them as production
  would call them and records those tokens (1.3, 1.4). A defect found during the
  memory runs, a job file read as empty while it is being rewritten, joins the Phase 1
  code change as S11. One exception to "stop at the first error" in the renewal script
  is confirmed (0.2).
- **2026-11-21 (third revision):** Rehearsal (0.6) passed and is approved. Tom's
  decisions D17 to D21 folded in: the wikis are deleted, not tarred; delivery by
  `git pull` is confirmed; the draft context is corrected to 15 chunks; keys move out
  of `site.ini` (S10). Untracked server files decided (0.2). Deploy steps (0.8)
  rewritten after the Programmer found that `git pull` aborts on untracked files the
  repo now tracks. Two unused dependencies dropped (0.4). The revise-context defect
  (1.1) is confirmed, and two more items are added to 1.1.
- **2026-11-21 (second revision):** Phase 0 (infrastructure refresh) added at Tom's
  request: current Python, Chroma, OpenAI SDK and images, DokuWiki removed, the repo
  made to match production, delivery by `git pull`. Tom is not concerned about the
  January 14 date, so work is reordered to avoid doing anything twice (see "Order of
  work"): site fixes S4 to S6 move into the Phase 1 code change, S7 is replaced by
  the DokuWiki removal, and the smoke calls move into Phase 0.
- **2026-11-21:** Website refresh defined by Tom as reference links plus images (Phase 4).
  Phase 3 is now the fixes arising from a review of the site code and live server.
  Model evaluation gets checkpoints at 10, 20 and 30 questions. Chunk experiment
  question set proposed as the same 30 plus about 10 new, labelled in batches.

## Goal

Keep CozyRAG running past the OpenAI model shutdown, find out whether a different
chunk size improves retrieval, refresh the website, and evaluate two user-facing
additions (reference links in answers, image gallery for a result).

## Model shutdown date

**[REVISED - 2026-11-21]** Tom expects the whole refresh to take a few days of effort
and does not want the date to shape the order of work (D15). It remains the date
after which the baseline (1.2) cannot be captured.

**January 14, 2027.** OpenAI shuts down `gpt-4o-mini-2024-07-18` and
`gpt-4.1-2025-04-14` on that date (notice dated Oct 14, 2026; recommended
replacement `gpt-6-luna`). The deprecations page lists only dated snapshots, not
the `gpt-4o-mini` / `gpt-4.1` aliases that `site.ini` uses; plan on the aliases
stopping the same day.

Source: https://developers.openai.com/api/docs/deprecations (read 2026-11-21)

## Decisions made by Tom (2026-11-21)

| # | Decision |
|---|---|
| D1 | Stay with OpenAI for this version. No local models, no other provider. |
| D2 | Keep two tiers: a cheap model for the first answer, a better model for "dig deeper" (revise and follow-up). |
| D3 | Chunk size is decided by experiment, not by guess. |
| D4 | Work order: model migration, chunk experiment, website refresh, then reference links and image gallery. |
| D5 | Reference links in answers are a nice-to-have. Evaluate after the other work is done. |
| D6 | `site_2024/CozyRAG_rev1_Back_Test.pdf` is superseded by the evaluation in this plan. |
| D7 | Retrieval mechanism stays as is. |
| D8 | The website refresh is the reference links and the images. No other redesign. |
| D9 | Model evaluation is checked at 10, 20 and 30 questions so a call can be made early. |
| D10 | A full email address is never sent to a web page. No password on the jobs page; Tom reads the job files on the server when he needs an address. |
| D11 | Chunk experiment uses the mixed question set: the same 30 plus about 10 new. |
| D12 | Site review findings are fixed: S3 with the reference links, S8 logged as an opportunity for improvement. Scheduling of the rest revised by D15: see Phase 3. |
| D13 | The server is refreshed to current stable versions: Python, Chroma, the OpenAI SDK and the other dependencies (Phase 0). |
| D14 | The two DokuWiki sites (`/dokucozy/`, `/dokuN657CZ/`) are removed; they are not used. |
| D15 | The January 14 date is not a constraint. Order the work for the least repeated effort. |
| D16 | Finished image database sections of the todo files are archived. |
| D17 | Wiki data is not kept. Everything needed has been pulled; both wiki directories are deleted from the server after the Phase 0 deploy checks pass. |
| D18 | `fwww/static/test_08_fixture/` was a test upload and is removed from the server. |
| D19 | Changes reach the server by `git pull`. |
| D20 | The first answer gets 15 chunks, as `MAX_DRAFT_DOCUMENTS` says. The code that sends 14 is corrected before the baseline (1.1). |
| D21 | Keys move out of `site.ini` into a git-ignored `site_local.ini` (S10). One OpenAI key serves the server and local runs. |
| D22 | Code review of the Phase 0 branch is waived. |
| D23 | gunicorn runs 2 workers, and the server has a 2 GB swap file. |
| D24 | The model evaluation runs every model at its default reasoning effort; no reasoning setting is sent (1.3). |
| D25 | No nginx rate limit. The OpenAI budget limit, which has no auto reload, is the limit on abuse (S2). |
| D26 | A revise is given every chunk retrieved for the question (provided and related, up to `MAX_DOCUMENTS`), and the job record keeps every chunk id, not one per source (1.1). |
| D27 | A follow-up is given only the chunks the previous answer was given, plus new chunks cut by the same rule as a first answer (1.1). |
| D28 | Code review of the Phase 1 deploy (`3278e9e`) is waived. |
| D29 | (2026-11-22) A follow-up's additional content leaves out chunks already in its previous content. The gap is not filled with further chunks (1.1 item 8). |
| D30 | (2026-11-22) An exception in the job thread is fixed now, not left with S8: the job is marked failed and the thread carries on (S12). |
| D31 | (2026-11-22) The site containers start again after a server reboot (`restart: unless-stopped`). |
| D32 | (2026-11-22) The certificate covers `www.m24tom.com` as well, and nginx redirects `www` to `m24tom.com`. |
| D33 | (2026-11-22) A failed OpenAI call ends the job in `error` (S12). When the cause is one Tom has to fix (budget used up, key rejected, model gone), the visitor is asked to let Tom know and is given the reason. No contact address is shown: those who know Tom can reach him. |
| D34 | (2026-11-22) A job file read while still empty, which can leave the job unanswered or in `error`, is accepted and logged as an opportunity for improvement (R5). |
| D35 | (2026-11-22) The model evaluation covers the first answer only. The dig-deeper model is not evaluated (1.2 to 1.5). |
| D36 | (2026-11-22) First answer: `gpt-6-luna`. Dig deeper: `gpt-6.2-sol` (1.5). |
| D37 | (2026-11-22) Code review of the model change (`1e72014`) is waived. The waiver does not cover the UI changes. |
| D38 | (2026-11-22) The model change is deployed in one deploy with the UI changes Tom designs with Architect. Answers that hold a table are to be displayed usefully. |
| D39 | (2026-11-22) The UI changes of that deploy are the display of answers only: tables, lists and S3. Reference links (4.1) and the image gallery (4.2) are not part of it, and the prompts do not change. |
| D40 | (2026-11-22) Answers are rendered by `markdown-it-py` with raw HTML off. The site's own pages keep Python-Markdown. |

## Two repositories

| Concern | Repo | Key files |
|---|---|---|
| Chunking and embedding | `ml/` (this repo) | `embedder/embedder.py`, `embedder/f_embed.py` |
| Retrieval, prompts, LLM calls, results page | `../site_2024/` | `fwww/src/llm_functions.py`, `fwww/site.ini`, `fwww/templates/` |
| Image database | `ml/` | `imageGetter/` |

**[REVISED - 2026-11-21]** The only automated tests in `site_2024` are those of the
certificate renewal script (`tests/test_sudo_renew_cert.py`); the application code has
none until Phase 1.1. Its branch `wip/annual-refresh` carries Phase 0, merged to `main`
at `bed83f4`. Programmer follows the same version-control rules there.

## Order of work

**[REVISED - 2026-11-21]** Chosen so that nothing is built, tested or deployed twice (D15).

1. **Phase 0, one deploy:** infrastructure refresh. Tests and the evaluation harness
   are then written once, on the stack production runs.
2. **Phase 1 code change with the site fixes, one deploy:** 1.1 plus S1, S2, S4, S5, S6, S10, S11.
   They touch the same files (`site_app.py`, `llm_functions.py`, `site_functions.py`,
   `open_with_lock.py`). Deployed 2026-11-21 (`3278e9e`).
3. **[REVISED - 2026-11-22] Follow-on fixes, one small deploy:** D29 (1.1 item 8), S12
   with the OpenAI failures (D33), the restart policy (D31) and the `www` name (D32).
   Before the harness, so the harness is written against the
   prompt code production then runs. None of them changes a first answer or a
   revise that succeeds, which is all the evaluation measures. Deployed 2026-11-22
   (`c311cda`).
4. **[REVISED - 2026-11-22] Phase 1 evaluation:** harness, baseline, blind rating by
   Tom. Done 2026-11-22 (1.5).
5. **Phase 2,** overlapping step 4: the embedding runs take hours of machine time
   while Tom rates.
6. **[REVISED - 2026-11-22] Answer display with the model change, one deploy (D38,
   D39):** see "Answer display". It carries S3.
7. **Phase 4:** reference links and image gallery, not yet designed.

One Programmer session per step. Code review once per deploy.

---

## Phase 0: Infrastructure refresh

**[REVISED - 2026-11-21]** New phase (D13, D14).

All changes are in `site_2024` unless stated. They ship as one deploy, which is only
safe because the whole stack is first run locally (0.6).

### Settled assumptions

**[REVISED - 2026-11-21]** All three points this section used to list as assumed are settled.

- Docker's WSL integration is enabled on Tom's machine, so the whole stack was
  rehearsed locally and the Chroma upgrade stays in the one deploy.
- Wiki data is deleted, not tarred (D17). Old wiki URLs get a 404, no redirects.
- Changes reach the server by `git pull` (D19).

### 0.1 Needed from Tom first

- Enable Docker Desktop's WSL integration for this distro (Settings, Resources, WSL
  integration). Docker Desktop is installed; `docker` in WSL currently reports that
  integration is off.
- `cat` the four untracked server files: `exclude_from_tar.txt`,
  `sudo_renew_cert.sh`, `server/old.nginx_all_apps.conf`, and a listing of
  `fwww/static/test_08_fixture/`.

### 0.2 The repo becomes the source of truth for deployment config

Production code already matches the repo's `main`; only two config files differ
(details and Tom's verbatim outputs:
`docs/references/site_2024_production_state_2026-11-21.md`).

- Commit the production `server/nginx_all_apps.conf` (HTTPS blocks live, `/cgimages/`
  served with `root /var/www/`) and the absolute mount
  `/home/admin/www/cgimages:/var/www/cgimages/:ro` in `docker-compose.yaml`. This is
  its own commit, before any other change, so it can be checked: on the server,
  `git fetch` then `git diff <that commit> -- server/nginx_all_apps.conf docker-compose.yaml`
  must show nothing.
- **[REVISED - 2026-11-21]** Untracked server files, decided:
  - `exclude_from_tar.txt`: already tracked on `main` (since `63cca77`). Remove the
    two wiki lines (one is misspelt `dokuN667CZ`) and add `fwww/site.ini`, so a
    project tar never carries the keys.
  - `sudo_renew_cert.sh`: tracked, **after it is fixed**. As written it deletes the
    live `fullchain.pem` and `privkey.pem`, then copies from names that do not exist
    in the archive directory (the files there are numbered), and carries on after the
    error. The site would then have no certificate. Required behaviour: stop at the
    first error; take the highest-numbered `fullchainN.pem` and `privkeyN.pem`; put
    the copies in place before removing anything, so a failure leaves the current
    certificate working. **[REVISED - 2026-11-21]** One exception to stopping at the
    first error, confirmed by Architect: a failed `docker compose restart` after the
    new files are in place goes on to the "is the site responding" question, because
    that question is what offers the rollback. Stopping there would leave the new
    files in place with nginx in an unknown state. The script was deployed and run
    once on 2026-11-21: the certificate now expires 2027-02-20. Its rollback branch
    has not been exercised on the server.
  - `server/old.nginx_all_apps.conf`: not tracked. It is the production config
    without `/cgimages/`. It stays on the server untouched; Tom may delete it.
  - `fwww/static/test_08_fixture/`: removed from the server (D18).
- An HTTP-only config for local runs is not built. Local rehearsal does not start nginx.

### 0.3 Compose and nginx changes

- **DokuWiki removal (D14, replaces S7):** remove both nginx `location` blocks, the
  `php1` and `php2` services, their `depends_on` entries, the two volume mounts and the
  README mention. Requests to the old paths then reach Flask and get a 404.
  **[REVISED - 2026-11-21]** On the server the two `data/doku*` directories are
  deleted after the deploy checks pass (D17). They are not tarred.
- **Published ports:** bind flask 8001, chroma 8000 and ollama 11434 to `127.0.0.1`.
  Today only the Lightsail firewall keeps them private.
- **Pinned images:** `nginx` and `ollama/ollama` (in `ollama.dockerfile`) get a
  current stable version tag instead of `latest`. Programmer records the tags chosen.

### 0.4 Python and requirements

- `flask.dockerfile` moves from `python:3.11-slim` to `python:3.13-slim`. 3.13 is what
  Tom's Debian ships, so a plain local venv matches the image.
- `requirements.txt` today is a 100-line `pip freeze`. Replace with a short file of
  direct dependencies (Flask, gunicorn, openai, ollama, Markdown, chromadb-client),
  let pip resolve the latest versions, and freeze the result for the image. Test
  packages go in a separate file that the image does not install.
  **[REVISED - 2026-11-21]** `Flask-Markdown` and `python-dotenv` are dropped: nothing
  imports them.
- Latest versions on 2026-11-21, for reference: openai 3.57.0 (pinned 1.51.2, two
  major versions behind, so expect call-site changes), flask 3.1.3, gunicorn 27.0.1,
  ollama 0.6.3, markdown 3.11.3.

### 0.5 Chroma

- Server image `chromadb/chroma:1.1.1` to **1.5.9**, in `site_2024/docker-compose.yaml`
  and in `ml/docker-compose.yaml`. Both mount the same `site_2024/data/chroma` on
  Tom's machine, so they must name the same version.
- The site uses only `chromadb.HttpClient`. Replace the `chromadb` package with
  `chromadb-client` 1.5.9, the HTTP-only client. This drops onnxruntime (the package
  with no Python 3.13 build at the old pin, and the source of the stderr warning on
  import) and most of the frozen pins.
- Release notes: Architect scanned the GitHub release notes for 1.2.2 through 1.5.9
  on 2026-11-21 for the words migration, breaking, compatibility, deprecation and
  downgrade. Nothing refers to a single-server storage change or a breaking client
  change; the migration entries concern the distributed (Spanner) deployment. This
  was a keyword scan of change titles, not a guarantee. Whether the upgraded server
  can be rolled back onto the same data is **unknown**: treat the upgrade as one-way
  and rely on the backup.

### 0.6 Local rehearsal (before any deploy)

1. Copy `site_2024/data/chroma` (553 MB) to a backup directory. The rehearsal
   upgrades the working copy in place.
2. With the old stack: record each collection's name and count, and the top 10
   result ids for three questions from `refresh_questions.csv`.
3. Build and start `flask`, `chroma-rag` and `ollama-rag` with the new compose file.
   nginx is not started locally (no certificates).
4. Pass criteria: collection names and counts unchanged; the same top 10 ids for the
   three questions; one question answered end to end through the Flask app on
   `127.0.0.1:8001` (needs a local `site.ini` with a key from Tom); no errors in
   the container logs.
5. Report to Architect. Any failure stops the deploy.

**[REVISED - 2026-11-21]** Result: every criterion passed and Architect approved the
deploy. The rehearsal ran with `Flask-Markdown` and `python-dotenv` installed; after
they are dropped, the image is rebuilt and one question answered locally before the
merge. The backup is `site_2024/data/chroma_backup_1.1.1`.

**[REVISED - 2026-11-21]** Memory, measured again by the Programmer (the earlier 882
against 806 MiB were single readings). Peak anonymous memory of the three containers
together, measured locally with model calls faked: old stack 790 MiB; new stack with
4 workers 900 to 919 MiB; new stack with 2 workers 750 MiB. The increase is Ollama's
server process. Tom decided on 2 workers and a 2 GB swap file (D23). On the server
after the deploy, with the model loaded, 771 MiB is available. The method
and the full table are in `docs/notes/refresh_phase0_memory.md`.

### 0.7 Smoke calls

One call to each candidate in 1.3 and to both current models, on the upgraded SDK.
This shows whether Tom's account has access and what the call looks like now. If the
call sites need changing for the new SDK, that change is part of Phase 0.

**[REVISED - 2026-11-21]** Result: both current models answer on SDK 3.57.0 with no
call-site change. All four candidates return 403 (no access for this OpenAI project).
Tom is arranging access; the candidate calls are repeated then. The Phase 0 deploy
does not wait for this.

**[REVISED - 2026-11-21]** Repeated after Tom arranged access: all four candidates
answer the production `chat.completions` call unchanged. Two spend reasoning tokens
on it; see 1.3.

### 0.8 Deploy

**[REVISED - 2026-11-21]** Steps rewritten. A plain `git pull` aborts on the server
because untracked files there are tracked in the new `main`; the old images are
tagged so a rollback needs no rebuild; the wikis are deleted rather than tarred.

Tom runs the server commands; Programmer supplies them and reads the output.

**[REVISED - 2026-11-21]** Done on 2026-11-21: `bed83f4` is deployed and every check
in step 6 passed. Tom waived the code review in step 1 (D22). Tom patched and rebooted
the server first; it runs Docker 29.10.0 and Compose 5.8.0 (the rehearsal used 28.3.2
and 2.39.1). What the deploy left on the server as its rollback, and when to remove
it, is in `programmer_todo.md`, "Server cleanup".

1. Code review of the branch, then merge to `main` with Tom's approval and push.
2. On the server, before stopping anything: tag the two locally built images (flask
   and ollama) as `old-stack`.
3. Stop the stack with the old compose file, which also removes the `php1` and `php2`
   containers. Tar `data/chroma` to a directory outside the checkout.
   `chmod 600 fwww/site.ini`.
4. Move `exclude_from_tar.txt` and `sudo_renew_cert.sh` to a directory outside the
   checkout (both are tracked in the new `main`). `git stash` the edits to tracked
   files (do not discard), then `git pull`. Compare the stash and the two moved files
   with the new checkout; the only differences allowed are the ones this plan makes.
   Git-ignored files (`site.ini`, key files) are untouched by this.
5. Rebuild and start. Check the nginx config with `nginx -t` in the container.
6. Checks: the site loads over HTTPS; a question is answered; `/cgimages/` serves;
   `/dokucozy/` returns 404; ports 8000, 8001 and 11434 listen on `127.0.0.1` only.
7. Only after the checks pass: delete `data/dokucozy`, `data/dokuN657CZ` and
   `fwww/static/test_08_fixture`, and remove the `php:7-fpm` image. Commands are in
   `programmer_todo.md` 0.8. Tom looks at each directory before removing it.
8. Rollback: stop, restore the `data/chroma` tar, check out `906ffd8`, `git stash pop`,
   move the two files back, give the `old-stack` images their original names, start.
   After step 7 a rollback still starts the old stack, but the wiki paths are empty.

Each evaluation harness lives in the repo whose code it exercises: the model
evaluation in `site_2024`, the chunk experiment in `ml`.

## Shared asset: the question set

**[REVISED - 2026-11-21]**

Questions are drawn from the production log at
https://m24tom.com/cozyrag/jobs (about 850 real questions as of 2026-11-21).
The model evaluation uses 30. The chunk experiment reuses those 30 and adds about
10 more (see 2.3).

- **Size:** 30 questions, ordered into three batches of 10. Each batch has the same
  mix of `factual` and `broad` so a checkpoint after any batch is a fair sample.
- **Selection:** Tom picks, with Architect proposing a shortlist. Mix narrow factual
  lookups (torque values, part numbers, where-to-buy) with broad questions
  (experience, sentiment, comparisons). Include the questions users rated
  `not_good` and several rated `perfect`. Exclude test entries.
- **Format:** `docs/plans/refresh_questions.csv` with columns `question_id`, `use`,
  `kind` (`factual` / `broad`), `long_doc`, `prod_rating`, `prod_job_id`, `question`.
- **`use` column:** `batch1`, `batch2`, `batch3` are the 30 for the model
  evaluation (5 factual and 5 broad each). `chunk_only` are the 10 extra for the
  chunk experiment, all expected to be answered from long documents. `reserve`
  are 12 approved spares: use them to replace a question that proves unusable or
  to extend either experiment if a result is too close to call.
- Tom approved all 52 on 2026-11-21 and asked that weak-looking ones (for example
  "length of a cozy") stay in, since they show how a model handles thin questions.
- The logged per-question sources are **not** an answer key. They are what the
  current 250-word setup retrieved, so using them as truth would favour the baseline.

---

## Phase 1: Model migration

### 1.1 Defects to settle before any comparison

These change what the "dig deeper" tier actually sees, so they come first.

1. **[REVISED - 2026-11-21] Confirmed: prior context is garbled in revise and follow-up.**
   `llm_functions.py` builds `priordocs` with `'\n\n'.join(rPriorDocs['documents'][0])`.
   Chroma `collection.get()` returns a flat list of documents, so `[0]` is a single
   chunk's text and the join splits it into characters. Programmer saw this on real
   data during the rehearsal. The failing test is still written first, then the fix.
2. **Prompts name the model.** `revise_prompt` and `followup_prompt` say "the draft
   response from GPT-4o-mini". Reword so no model is named.
3. **Stale `__main__` block** in `llm_functions.py` passes a string to
   `process_question`, which expects a dict. **[REVISED - 2026-11-21]** It is removed;
   Tom approved.
4. **[REVISED - 2026-11-21] The first answer gets 14 chunks, not 15 (D20).**
   `get_num_draft_docs` returns the index of the last chunk inside the distance
   cutoff and the caller uses it as a count, so that chunk is dropped. The function
   returns a count instead: with 60 close matches and `MAX_DRAFT_DOCUMENTS = 15` it
   returns 15. Fixed before the baseline, so the baseline, the setting and the
   chunk metrics (2.4) all mean 15. Production answers before this fix used 14.
5. **[REVISED - 2026-11-21] `[PROMPTS]` `INITIAL` and `SECONDARY` have no effect.**
   `process_question` uses the module constants, not the values passed to
   `set_prompts`. The two settings and the code that carries them are removed; the
   prompts stay in the code, where 1.1 puts them under test. `PREFIX` stays.

6. **[REVISED - 2026-11-21] The job record keeps every chunk (D26).** `provided_docs`
   and `related_docs` hold one entry per chunk, in the order retrieved. Today
   `get_doc_list_from_result` keeps one chunk per source, so a revise is asked to
   verify a draft without some of the text the draft was written from (in one job 19
   chunks became 12 ids). One row per source is still what the results page shows:
   the reduction moves to where a job is prepared for display. It must also work for
   entries with no `score`, which is what a revise or follow-up record holds. `number
   provided docs` stays the chunk count. Job files written before this change are not
   converted; a revise of one uses the ids it has.
7. **[REVISED - 2026-11-21] A revise gets every retrieved chunk, in rank order (D26).**
   Provided chunks first, then related, each in the order retrieved. Today the ids
   pass through a `set` and `collection.get()`, so the text arrives in no particular
   order. Its record's `provided_docs` lists those chunks in that order.
8. **[REVISED - 2026-11-21] A follow-up gets less (D27).** Previous content: the
   chunks the answer being followed up was given, which is that record's
   `provided_docs` and not its `related_docs`. Additional content: the new retrieval,
   cut by `get_num_draft_docs` exactly as for a first answer (5 to 15 chunks), not all
   60. Its record's `provided_docs` is the previous chunks followed by the additional
   ones, no id twice, and it has no `related_docs`. A chain of follow-ups then grows by
   at most `MAX_DRAFT_DOCUMENTS` chunks each time. Before this, a follow-up carried up
   to 60 prior chunks plus 60 new ones and saved all of them as the next one's prior
   context.

   **[REVISED - 2026-11-22] No chunk is sent twice (D29).** A chunk of the new retrieval
   that is already in the previous content is left out of the additional content. The
   cut by `get_num_draft_docs` is made first and the duplicates are removed afterwards;
   the gap is not filled from further down the ranking. The additional content can
   therefore hold fewer than `MIN_DOCUMENTS` chunks, or none: the prompt must read
   sensibly when it is empty. The record is unchanged by this, since it already listed
   each id once. As deployed at `3278e9e` the duplicates were sent in both places.

Size of a revise prompt with items 1, 6 and 7 (Programmer's measurement on 16 local
jobs, before item 6 adds the dropped chunks): 33,000 to 68,000 characters where 60
chunks were retrieved, against about 5,000 with the defect. The evaluation (1.4)
records the cost.

**Checked and left alone:** `PREFIX = search_query:` reaches the embedder with no
space before the question, while documents were embedded as `search_document: ` with
one. Architect measured it on 2026-11-21 against the local Ollama and Chroma: for all
52 questions in `refresh_questions.csv` the embedding is identical with and without
the space, and so are the top 60 results. The model's tokenizer splits at the colon
either way. (Control: removing the prefix altogether does change the vector.) Nothing
is changed and Phase 2 has no variant for it.

To make these testable, prompt construction is separated from the thread and the
API call: a function that takes the job data and document lists and returns the
prompt string. The evaluation harness (1.3) calls the same function, so it measures
what production sends. This is a small refactor of `process_question`, not a rewrite.

### 1.2 Capture the baseline before shutdown

Run the 30 questions through the current models (`gpt-4o-mini` first answer,
`gpt-4.1` revise) and save answers, token counts and latency. After January 14
this cannot be recreated. Do this after 1.1 so the baseline reflects the corrected
revise step; if 1.1 slips, capture the baseline anyway and note which code produced it.

**[REVISED - 2026-11-22]** Captured for the first answer only (D35): the 30 answers of
`gpt-4o-mini`, by the code of `c311cda`, are in
`docs/archive/gpt4o_mini_baseline_answers`. No `gpt-4.1` revise was captured, and after
January 14 none can be.

### 1.3 Candidates

Prices per million tokens, input / output, from
https://developers.openai.com/api/docs/models (read 2026-11-21):

| Model | Price | First answer | Dig deeper |
|---|---|---|---|
| `gpt-6-luna` | $0.10 / $0.50 | candidate | |
| `gpt-6.1-terra` | $1 / $5 | candidate | candidate |
| `gpt-6.2-sol` | $2 / $10 | | candidate |
| `gpt-6.2-astra` | $8 / $40 | | only if `sol` is not good enough |

**[REVISED - 2026-11-21]** All four accept the `chat.completions` call the site makes
today (0.7).

**Reasoning tokens.** On a one-sentence question `gpt-6-luna` spent 50 of its 80
completion tokens on hidden reasoning and `gpt-6.1-terra` 34 of 72; `gpt-6.2-sol` and
`gpt-6.2-astra` spent none. One sample each on a short prompt, so the share on a real
4,500-token question is unknown. Reasoning tokens are billed as output and add to the
response time.

Decision (Architect, approved by Tom, D24): the evaluation calls every model exactly as production does,
with no reasoning setting, so each runs at its own default. That measures what the
`site.ini` switch (1.6) would deliver, and it needs no code beyond the harness. A
reasoning setting in `site.ini` is built only if the results call for it: a candidate
that fails on quality or is too slow at its default, where another effort level might
change the outcome. That case goes back to Tom before anything is built. The API's
reasoning parameter and each model's default have not been read from OpenAI's
documentation; that is done only if the setting is needed.

**[REVISED - 2026-11-22]** Evaluated: `gpt-6-luna` and `gpt-6.1-terra` for the first
answer. The dig-deeper column was not evaluated (D35), and `gpt-6.2-astra` was not
tried. On the 30 questions the median reasoning tokens were 328 for `gpt-6-luna` and 30
for `gpt-6.1-terra`, with median latencies of 5.6 s and 5.0 s against 5.3 s for
`gpt-4o-mini`. Neither is slow at its default, so no reasoning setting is built for the
first answer. The speed and cost of `gpt-6.2-sol` on a dig deeper were not measured.

### 1.4 Evaluation method

- Retrieval is run once per question and the same documents are given to every
  model, so only the model varies.
- Output: one review file per tier with, for each question, the answers from each
  model in random order and unlabelled. A separate key file maps positions to models.
- Tom rates each answer `perfect` / `ok` / `not_good` (the scale the site already
  uses) and notes any factual error. Factual errors matter most: this is aircraft
  construction advice.
- Harness also records tokens in, tokens out, latency, and computed cost per answer.
  **[REVISED - 2026-11-21]** It records reasoning tokens as a separate figure, read from
  the same usage details the Programmer read them from in 0.7 (zero when absent).
  They are already inside `completion_tokens`, so cost is computed from
  `completion_tokens` and they are not added again. The tally after each batch (1.5)
  shows, per model, median latency, median reasoning tokens and cost per answer beside
  the ratings. These inform Tom's choice; the decision rule itself is unchanged.
- **[REVISED - 2026-11-22]** A model call that fails is recorded as a failure with its
  cause. Error text is never recorded as an answer or put in a review file (D33).
- **[REVISED - 2026-11-22]** As run: one tier, the first answer (D35). Tom rated on a
  local page that shows the answers unlabelled (`evaluation/review_answers.py` in
  `site_2024`), not in a review file. The ratings and the key are in
  `docs/archive/first_answer_ratings`.

### 1.5 Decision rule

**[REVISED - 2026-11-21]** Checkpoints added at Tom's request.

For each tier, choose the **cheapest** candidate that has no more `not_good`
ratings and no more factual errors than the baseline. If none qualifies, escalate
to the next model up and discuss with Tom.

Tom rates one batch of 10 at a time. After each batch, per tier:

- **Stop and adopt** the cheapest candidate if it has no `not_good` and no factual
  error so far, and at least as many `perfect` ratings as the baseline.
- **Drop a candidate** if it has 3 or more `not_good` or factual errors beyond the
  baseline's count. It is not rated in later batches.
- **Otherwise continue** to the next batch. After 30, apply the rule above as written.

Ten questions is a small sample. Stopping early is acceptable here because the
choice is a `site.ini` setting and can be reversed in minutes if production
ratings disagree.

**[REVISED - 2026-11-22] Result.** All three batches were rated, 30 answers per model:

| Model | `perfect` | `ok` | `not_good` | Factual errors | Median s | Median reasoning tokens | $ per answer |
|---|---|---|---|---|---|---|---|
| `gpt-4o-mini` (baseline) | 17 | 8 | 5 | 2 | 5.3 | 0 | 0.00086 |
| `gpt-6-luna` | 14 | 13 | 3 | 2 | 5.6 | 328 | 0.00074 |
| `gpt-6.1-terra` | 11 | 15 | 4 | 1 | 5.0 | 30 | 0.00574 |

- **First answer: `gpt-6-luna` (D36).** It is the cheapest candidate and has no more
  `not_good` ratings and no more factual errors than the baseline, which is the rule
  after 30. It has fewer `perfect` ratings than the baseline (14 against 17); the rule
  does not count those.
- **Dig deeper: `gpt-6.2-sol` (D36).** Tom's choice. The rule was not applied: no
  dig-deeper answer was rated (D35). It was tried on the local site with one question
  and one dig deeper.
- To watch after the deploy: in Q05 `gpt-6-luna` named a seller while saying the
  documents do not mention one (rated a factual error). A search of its other answers
  for that wording found none, but would miss an unsupported claim made without saying so.
- A job's `result` holds the model name OpenAI returned (`completion.model`), and the
  results page shows it as "GPT Model". Production ratings before and after the switch
  can be told apart by it.

### 1.6 Rollout

Model names are already in `site.ini` (`LLM_DRAFT`, `LLM_REVISE`), so the switch is
a config change. The prompt wording from 1.1 is already deployed by then.
**[REVISED - 2026-11-21]** After S10 `site.ini` is tracked, so the switch is a commit
and a `git pull`.

**[REVISED - 2026-11-22]** The commit is `1e72014` on `wip/annual-refresh` in
`site_2024`, pushed and not merged. It is not deployed alone: it goes out with the UI
changes (D38). Its code review is waived (D37); the UI changes are reviewed. Until that
deploy the server uses `gpt-4o-mini` and `gpt-4.1`, which stop on January 14.

---

## Phase 2: Chunk-size experiment

Independent of Phase 1: it measures retrieval only and calls no LLM.

### 2.1 Prerequisites in `embedder/`

- **Defect:** `chunksplitter` appends a chunk that contains only the prefix when a
  document's word count is an exact multiple of the chunk size, and for empty
  files (the `if current_chunk:` test is always true). Fix under TDD.
- Add overlap to `chunksplitter` (default 0, which reproduces current behaviour).
- `embedder.py` takes chunk size, overlap and collection name as parameters
  instead of edited constants, with a separate progress file per collection.
- `embedder/` has no tests today; these changes add them.

### 2.2 Variants

Each variant goes in its own Chroma collection. The production collection
(`nomic-embed-text`) is never modified.

| Variant | Words | Overlap |
|---|---|---|
| A (baseline, existing collection) | 250 | 0 |
| B | 150 | 0 |
| C | 400 | 0 |
| D | 250 | 50 |
| E | 400 | 80 |

Embedding model (`nomic-embed-text`) and prefixes stay fixed.

**Corpus:** full corpus (about 11,000 files, 100 MB). A subset would make retrieval
artificially easy. Programmer times variant B first; if a full variant takes more
than a few hours, stop and discuss before running the rest.

### 2.3 Questions and labelling (needs Tom)

**[REVISED - 2026-11-21]** Question set confirmed by Tom (D11).

**Which questions:** the same 30 as the model evaluation, plus about 10 new ones.

- Reusing the 30 is safe: nothing is tuned on the model ratings, so there is no
  contamination. Tom already knows what a good answer to each looks like, which
  makes labelling faster, and the winner's answers can be compared with the
  Phase 1 answers afterwards.
- The 10 new ones target where chunk size matters most: answers inside long
  documents (newsletters, Canard Pusher, long threads). Measured on the corpus
  2026-11-21: 92% of message words are in files over 250 words, and newsletters
  have a median of about 7,900 words. Files of 250 words or fewer (45% of
  messages) are a single chunk in every variant except B.

**Batches:** labelled 10 questions at a time, with the metrics recomputed after
each batch. Stop early if one variant is already ahead by the 2.5 margin or if
all variants are within one question of each other after 20.

**Labelling steps:**

1. For each question, take the top 10 chunks from every variant and merge them by
   source document.
2. Harness writes `chunk_labels.csv`: `question_id`, `source_id`, link to the
   message or newsletter, a short excerpt, and an empty `relevant` column. Rows are
   shuffled and do not say which variant found them.
3. Tom marks each row `y` or `n`: does this document help answer the question?

Expected effort: roughly 15 to 25 rows per question, so 150 to 250 judgements per
batch of 10 and 600 to 1,000 if all 40 are needed. This is the main cost of the experiment and it falls on Tom.

### 2.4 Metrics

Measured at a fixed 15 chunks (what the first-answer model receives), because the
`MAX_DISTANCE = .35` cutoff is not comparable between chunk sizes.

- **Hit rate:** share of questions with at least one relevant source in the top 15.
- **Relevant sources found:** average count of distinct relevant sources in the top 15.
- **First relevant rank:** average position of the first relevant chunk.
- **Context size:** average words in the top 15, since larger chunks cost more per question.

### 2.5 Decision rule (fixed before running)

Re-embed production only if a variant beats the baseline on hit rate by at least
one question in ten (3 of 30, 4 of 40), or matches it on hit rate and finds clearly more relevant
sources. Otherwise leave chunking alone and record the result.

If a variant wins:
- Read answers side by side on 10 questions (baseline versus winner) as a sanity check.
- Re-tune `MAX_DISTANCE`, `MAX_DRAFT_DOCUMENTS` for the new chunk size.
- The site selects its collection by embed-model name. Add a collection setting to
  `site.ini` so the switch and any rollback are config changes. Not built unless a
  variant wins.

---

## Phase 3: Site fixes from review

**[REVISED - 2026-11-21]**

Architect reviewed `site_2024` code and made a small number of read-only requests
to the live server on 2026-11-21. Tom's stated risk tolerance is low concern:
nothing else of value is on the server. Tom chooses which findings to fix.

What was checked and found sound: Chroma (8000), Ollama (11434) and gunicorn (8001)
are not reachable from outside; HTTP redirects to HTTPS; `site.ini` and the key
files are git-ignored; route parameters cannot contain a slash, so job and page
lookups cannot escape their directories.

| # | Severity | Finding | Where | Suggested fix |
|---|---|---|---|---|
| S1 | High (privacy) | Full submitter email addresses are public. `/cozyrag/<id>/status` returns the whole job record as JSON and the results page prints `Submitted By: <email>`. Every job id is listed on the public jobs page. | `site_app.py` `cozyrag_status`, `cozyrag_results.html` | See "S1 design" below (D10). |
| S2 | Medium (cost) | No rate limit on questions. Anyone can script submissions; each follow-up sends about 20,000 tokens to the better model. `/cozyrag/revise` also runs on a plain GET. | `site_app.py`, nginx | **[REVISED - 2026-11-21]** See "S2 design" below (D25). |
| S3 | Medium | **[REVISED - 2026-11-22]** Fixed by the answer renderer, without a sanitiser: see "Answer display" (D40). Original finding: Model output is rendered as raw HTML: the answer goes through Markdown, which passes HTML through, and is marked `safe`. A question can instruct the model to emit a script tag, and the result is stored and linked from the jobs page. | `cozyrag_results.html` line 11 | Sanitise the rendered HTML with an allow-list (for example `nh3`) before marking it safe. |
| S4 | Low | `sanitize()` does the opposite of its name: it wraps input in `Markup`, declaring it safe. Not exploitable today because values pass through JSON before display, but one template change away from being so. | `site_functions.py` | Remove the `Markup` wrap. |
| S5 | Low | Unknown job ids and several routes return HTTP 500: `processid` and `status` with a bad id, `jobs/<bad column>` (`abort` is never imported), and `revise` / `feedback` / `answer` without a session. | `site_app.py` | Return 404 or redirect to the question form. |
| S6 | Low | Feedback accepts any text as the rating, which is why the log contains values outside the three buttons. | `cozyrag_feedback` | Accept only `perfect`, `ok`, `not_good`. |
| S7 | Replaced | **[REVISED - 2026-11-21]** Both wikis are removed (D14, Phase 0.3). Original finding: DokuWiki page source is served directly (`/dokucozy/data/pages/start.txt` returns 200), bypassing any wiki access rules. Matters only if a wiki has private pages. PHP 7 is past end of life. | nginx config, `php:7-fpm` | Deny `data/`, `conf/`, `bin/`, `inc/` in nginx. PHP upgrade is outside this refresh. |
| S8 | Low | Each gunicorn worker (4 at the review, 2 since D23) starts its own job thread and scans every job file; `super().__init__()` is called after `daemon = True`, which resets it; a job whose worker dies stays in `start` forever. The jobs page reads every job file on each view. Works at current volume. | `llm_functions.py`, `site_functions.py` | Leave unless symptoms appear; log as an opportunity for improvement. |
| S10 | Low | **[REVISED - 2026-11-21]** Keys share a file with the settings. `site.ini` holds the OpenAI and session keys beside the model names and retrieval limits, so it cannot be tracked: production settings are not in the repo, the template has drifted from what the code reads, and every tool or person reading a setting also reads the keys. The README's project tar includes `site.ini`. | `site.ini`, `site_app.py`, `exclude_from_tar.txt` | See "S10 design" below (D21). |
| S11 | Medium | **[REVISED - 2026-11-21]** A job file can be read as empty while it is being rewritten. `open_with_lock` opens an existing file for writing with `O_TRUNC`, which empties it before the lock is held; if a reader holds the lock, the writer waits and retries with the file left empty. A read in that window returns `{}`: `/status` then raises `KeyError: 'created'` (500) and the polling page stops, so the visitor keeps seeing "Running Query"; the jobs page fails the same way; and `update_process_status` would save the job back without its question. Seen once as a 500 in the Phase 0 memory runs. Each retry also leaves a file descriptor open. | `open_with_lock.py`, `site_functions.py` | See "S11 design" below. |
| S12 | Medium | **[REVISED - 2026-11-22]** Any exception in the job thread ends it. `FileProcessorThread.run()` has no handler, so one failed job (Chroma, Ollama or OpenAI unreachable, a malformed job file) stops that worker's thread; the worker goes on serving pages and answers nothing until the container restarts. With 2 workers, two such failures leave the site accepting questions and answering none. Found by the Programmer; the Chroma and Ollama cases are read from the code, not tried. A job in `error` status also leaves the visitor's page polling without end. | `llm_functions.py`, `site_app.py`, `cozyrag_answer.html` | See "S12 design" below (D30). |
| S9 | Info | `.env_flask` is tracked in git with an `OPENAI_KEY` value that looks like a placeholder (24 characters, no `sk-` prefix). Tom to confirm it was never a real key. The repo's nginx config has HTTPS commented out, so it does not match production. No security headers (HSTS and similar) are sent. | repo root, `server/` | Confirm; no action otherwise. |

### S1 design (D10)

A full email address never leaves the server in any response.

- One function produces the shortened form of an address (the first 5 characters
  followed by `...`, as the jobs page shows today; empty when there is none). It
  is applied where a job record is prepared for display, not in each template, so
  the three places below cannot drift apart.
- `/cozyrag/<id>/status` returns only what the polling page uses: `status`,
  `status_text`, `result_html`. It no longer returns the job record.
- The results page and the jobs page show the shortened form only.
- Job files on disk are unchanged and keep the full address.
- Tests assert that a known full address does not appear anywhere in the response
  body of `status`, `processid`, `jobs` and `jobs/email`.

Questions and answers remain public on the jobs page. That is accepted.

### S2 design

**[REVISED - 2026-11-21]** The nginx rate limit is dropped (D25).

- The OpenAI account has a budget limit with no auto reload (Tom confirmed it is on).
  A script can use up the budget; the site then answers with errors until Tom tops it
  up. It cannot cost more than the budget. This is the limit on abuse.
- No nginx `limit_req`. It would slow a script down without lowering that ceiling.
- Only a POST starts paid work. `/cozyrag/revise` accepts POST only (the button already
  posts). A question's job starts in the `/cozyrag/query` POST; `/cozyrag/answer`
  starts none, so repeating a GET does not pay for the question again.

### S10 design (D21)

**[REVISED - 2026-11-21]** New.

What is already sound: `site.ini` is git-ignored, is mounted into the container
rather than built into the image, and is not under any path nginx or Flask serves.
The key has not leaked by any route found. The changes below remove the ways it
could, and put the production settings under version control.

- **Keys leave `site.ini`.** A git-ignored `fwww/site_local.ini` holds `[KEYS]`
  (`SESSION`, `OPENAI`). The app reads `site.ini` and then `site_local.ini`, so a
  value in the second file wins; a local run can also put machine-specific settings
  there. The app refuses to start, with a message naming the file, if a key is missing.
- **`site.ini` is tracked** and holds the production settings with no `[KEYS]`
  section. The model switch (1.6) is then a commit delivered by `git pull`, and
  rollback is a revert. `site.ini.template` is replaced by a `site_local.ini.template`.
  `.env_flask` and the commented `env_file` lines in the compose file are removed:
  nothing reads them.
- **File mode and tar:** `site_local.ini` is mode 600 on the server and is listed in
  `exclude_from_tar.txt`.
- **One OpenAI key (Tom, 2026-11-21):** the same key is used on the server and for
  local and evaluation runs. Architect suggested a second key; Tom decided one is
  enough. The account's monthly spend cap (S2) is the limit on a harness mistake.
- **Deploy step:** on the server the existing `site.ini` is moved aside before the
  pull (it becomes tracked), `site_local.ini` is created from its `[KEYS]` section,
  and the rest is compared with the tracked `site.ini` to show no setting changed.

Not done: moving keys to environment variables or Docker secrets. For one container
on a single-user server that adds parts without removing a real exposure.

### S11 design

**[REVISED - 2026-11-21]** New. Found by the Programmer, cause confirmed by Architect
from the code.

- `open_with_lock` opens an existing file for writing without emptying it, takes the
  exclusive lock, and only then empties it. Readers take a shared lock, so they see
  the previous content or the complete replacement, never an empty file. The
  descriptor is closed before each retry.
- The locking scheme stays. Writing to a temporary file and renaming it was considered
  and not chosen: a rename replaces the file the locks are held on, so it would mean
  redesigning the locking rather than correcting it.
- Test, deterministic and without timing luck: hold a shared lock on a job file that
  has content, start a write in a second thread, and while the writer is waiting read
  the file directly. It must still hold the previous content. Then release the lock
  and check the write completes with the replacement.
- Not addressed: two read-then-write updates of the same job (for example feedback
  arriving while the job thread saves a status) can still overwrite each other. Not
  observed; logged with S8 in `docs/notes/opportunities_for_improvement.md`.
- Not added: a retry in the polling page after a failed request. With the cause
  removed and S5a returning 404 for an unknown job, a page that retried would poll a
  missing job without end.

### S12 design (D30)

**[REVISED - 2026-11-22]** New.

- In `run()`, everything done for one job (from reading its file to saving the result)
  is inside one handler. On any exception the traceback is written to the container
  log with the job's file name, the job's status is set to `error`, and the loop goes
  on to the next job. A job is never retried: a retry of a failing paid call would pay
  again each time.
- If saving the `error` status itself fails (the job file is unreadable), that is
  logged and the job is not looked at again by this thread until a restart. The
  thread still carries on.
- The existing `error` path for a job without a `query` stays as it is.
- A failed revise or follow-up changes only the status: the `result` already in the
  job file is left as it was.
- The visitor is told. `/cozyrag/<id>/status` for a job in `error` returns a
  `status_text` (**[REVISED - 2026-11-22]** its wording is in "OpenAI failures and the
  reason shown" below), and the
  polling page stops polling when the status is `error`. Today it would show
  `Status: error` and poll without end.
- Tests: a job whose processing raises is left in `error`, and a second job queued
  behind it is answered by the same thread; the status response for an `error` job.
  The logged traceback is captured and asserted, so test output stays clean. The
  failure is produced by a real unreachable Chroma address or a malformed job file,
  not by a mocked exception inside the code under test, where that is practical.
- Not addressed, still with S8: a worker killed mid-job leaves the job in `start`; the
  OpenAI call has no timeout.
- **[REVISED - 2026-11-22]** Accepted (D34, review finding R5): a job file is empty for a
  moment between its creation and the lock. A scan that reads it then treats it as
  unreadable and that worker never answers it; if the file becomes readable before the
  status is saved, the job ends in `error` instead. Not seen in 12,000 jobs unless the
  timing was forced. Logged with S8.

### OpenAI failures and the reason shown (D33)

**[REVISED - 2026-11-22]** New. Review finding R4.

As deployed, `process_question` catches `openai.APIError` and returns the error text as
the answer. The job ends `complete`; on a revise the error text replaces the draft. The
S12 handler never sees the failure.

- `process_question` no longer catches OpenAI errors. They reach the handler in `run()`
  like any other exception, so the job ends in `error`, the traceback with OpenAI's own
  message is in the container log, and a failed revise or follow-up keeps its `result`.
- The handler works out a **reason** from the exception and saves it in the job file as
  `error_reason` together with the `error` status. Only failures that Tom has to fix have
  a reason:

  | `error_reason` | Recognised by | Shown to the visitor as |
  |---|---|---|
  | `openai_budget` | **[REVISED - 2026-11-22]** `openai.RateLimitError` whose `code` is `credit_balance_exhausted`, `organization_spend_limit_exceeded`, `project_spend_limit_exceeded` or `organization_usage_limit_exceeded`, or whose `code` or `type` is `insufficient_quota` | OpenAI budget used up |
  | `openai_access` | `openai.AuthenticationError`, `openai.PermissionDeniedError` | OpenAI key rejected |
  | `openai_model` | `openai.NotFoundError` | OpenAI model not available |

  Every other failure has none: other rate limits, timeouts, connection errors, OpenAI
  5xx, and whatever is not an OpenAI error (Chroma, Ollama, a malformed job file). A
  failure without a reason removes an `error_reason` left by an earlier failure of the
  same job.
- The status response chooses the `status_text` of an `error` job by the reason:
  - with a reason: "The site cannot answer questions until Tom fixes it. Please let him
    know: OpenAI budget used up." (the phrase from the table)
  - without: "The question could not be answered. Please try again in a few minutes. If
    it keeps failing, please let Tom know."
- The reason codes, how each is recognised and its phrase are defined in one place.
- Never shown to a visitor or saved in the job file: the exception's own text. It can
  carry account details.
- No contact address is shown (D33). The visitors Tom cares about know how to reach him.
- **[REVISED - 2026-11-22]** The budget rule is from OpenAI's page of error codes
  (https://developers.openai.com/api/docs/guides/error-codes, read 2026-11-22), which
  does not give `insufficient_quota` as a `code`; Tom approved the rule. A real response
  of a used-up budget has not been seen: the account was not used up to get one.
- **[REVISED - 2026-11-22]** Known and left as they are (Architect). That page documents
  no 404 for a model that is gone, so `openai_model` is unconfirmed. A model the project
  has no access to answers 403 (0.7) and is shown as "OpenAI key rejected". In both
  cases the container log has OpenAI's own message.
- Tests: each row of the table and one failure without a reason, from the exception to
  the `status_text`; a failed revise keeps its draft and ends in `error`; a failure
  without a reason clears an earlier one. The failures are raised by the real SDK
  against a local address that answers with the status and body (or does not answer),
  not by raising inside the code under test.
- Not done: the jobs page does not show the reason (the job file and the log hold it);
  the site does not send Tom a message itself. Tom may set a spend alert in the OpenAI
  account, which would reach him before a visitor does; what the account offers was not
  checked.

### Restart after a reboot (D31)

**[REVISED - 2026-11-22]** New.

- `restart: unless-stopped` on the four services of `site_2024/docker-compose.yaml`
  (`nginx`, `flask`, `chroma-rag`, `ollama-rag`). The line is already there, commented
  out, with a comment calling it optional; that comment goes.
- It relies on the Docker service itself starting at boot. On the server
  `systemctl is-enabled docker` must say `enabled`; if it does not, enabling it is
  part of the deploy.
- A container stopped with `docker compose stop` stays stopped across a reboot, so the
  rollback steps in `programmer_todo.md` are unaffected.
- The same file runs on Tom's machine, where the containers will now also come back
  when Docker Desktop starts, until `docker compose down`. A server-only override file
  would avoid that and was not chosen: it is one more file that must match on deploy.
- The real check is a server reboot followed by a question answered with no command
  run. Tom decides at the deploy whether to reboot for it.

### The `www` name (D32)

**[REVISED - 2026-11-22]** New.

Today: `www.m24tom.com` resolves to the server and both nginx server blocks answer for
it. The HTTP block redirects to `https://$host`, so `www` stays `www`; the certificate
names `m24tom.com` only, so `https://www.m24tom.com` shows a certificate warning. Read
from the config and DNS on 2026-11-22; the live URL was not requested.

**nginx** (`server/nginx_all_apps.conf`):

- The HTTP block redirects to `https://m24tom.com$request_uri`, so `http://www...`
  reaches the site in one hop. The ACME challenge location keeps answering for both
  names: the certificate authority checks each name over HTTP.
- A separate HTTPS server block for `www.m24tom.com`, with the same certificate files,
  does nothing but `return 301 https://m24tom.com$request_uri`. The main HTTPS block
  no longer lists `www`.
- This can ship before the certificate covers `www`: until then `https://www` shows the
  same warning as today, and nothing else changes.

**Certificate** (`sudo_renew_cert.sh`):

- Both certbot calls (dry run and real) ask for `m24tom.com` and `www.m24tom.com`,
  with `m24tom.com` first.
- **Not known:** what certbot does on the server when the list of names changes. The
  script assumes each run leaves a new `m24tom.com-NNNN` directory in `archive/` and
  takes the highest. With a changed list certbot may instead ask to expand an existing
  certificate, or name the directory differently; the script would then install an
  older certificate and report success. Programmer reads certbot's documentation for
  `certonly` with a changed `-d` list, and Tom runs `certbot certificates` (through the
  compose file) on the server so the existing names are known, before the script is
  changed. If that shows the directory choice needs redesign, it comes back to Architect.
- Whatever certbot does, the script checks the files it is about to install, before
  replacing anything: the certificate names both `m24tom.com` and `www.m24tom.com`, and
  it is not older than the one in place. If not, it stops and the current certificate
  stays. This closes the case above whichever way certbot behaves.
- The closing question asks Tom to check both `https://m24tom.com` and
  `https://www.m24tom.com`.
- Script changes under TDD in `tests/test_sudo_renew_cert.py`, as before.

**Deploy:** after the pull and restart, run the script once. Checks:
`curl -sI http://www.m24tom.com/x`, `curl -sI https://www.m24tom.com/x` and
`curl -sI http://m24tom.com/x` each answer 301 with `Location: https://m24tom.com/x`;
`https://www.m24tom.com` gives no certificate warning; the site answers a question.
The script's rollback branch has still not been exercised on the server (0.2).

### Scheduling

**[REVISED - 2026-11-21]** (D15)

- With the Phase 1 code change, in one deploy: S1, S2, S4, S5, S6, S10, S11.
- **[REVISED - 2026-11-22]** In the follow-on deploy: S12 with D33, and D29, D31 and D32.
- **[REVISED - 2026-11-22]** With the answer display and the model change: S3.
- Replaced by the DokuWiki removal in Phase 0.3: S7.
- Not scheduled: S8 (in `docs/notes/opportunities_for_improvement.md`).
- Closed: S9. Tom confirmed the tracked `.env_flask` only ever held a placeholder;
  the nginx mismatch is fixed by Phase 0.2.

## Answer display (D39, D40)

**[REVISED - 2026-11-22]** New. One deploy with the model change (D38).

**What is wrong today.** Answers go through `markdown.Markdown()` with no extension and
are marked `safe`. A Markdown table is shown as raw `|` lines (4 of the 90 evaluation
answers). A list that follows a text line with no blank line between is shown as run-on
text (3 of 90). Raw HTML in an answer reaches the page as HTML (S3).

**Scope (D39).** The display of an answer on the results page. The prompts are not
changed, so the answers are those of the prompt Tom rated. Not part of it: reference
links, the image gallery, the jobs page.

**Renderer (D40).**

- One function takes the text of an answer and returns its HTML. It is the only place
  that knows how an answer is rendered. The results page uses it, and so does the
  rating page (`evaluation/review_answers.py`), so that page keeps showing answers as
  the site does.
- It renders with `markdown-it-py`: the `commonmark` preset with `html` set to false,
  the `table` rule enabled and the `image` rule disabled.
  - `html` false: a tag written in an answer is shown as text. This is the fix of S3.
  - `table`: the tables the models write. A column alignment asked for in the table is
    kept (a `style="text-align:..."` on the cell, written by the renderer).
  - `image` disabled: an answer cannot make a visitor's browser load a picture from
    another site. No evaluation answer has one. The Markdown for a picture becomes a
    `!` followed by a link.
- The site's own pages (`home`, `links`, `cozy`) keep Python-Markdown through
  `markdown_to_html`. They are Tom's text, and may use raw HTML.
- `markdown-it-py` joins `requirements_direct.txt` and the frozen file. `Markdown` stays.
  The image is rebuilt at the deploy.

**Why this and not Python-Markdown with a sanitiser.** Considered: Python-Markdown with
its `tables` extension, a step of our own that puts a blank line before a list, and
`nh3` to sanitise. Rendered by Architect on the 90 archived answers (2026-11-22, not
site code): both fix the 4 tables and the 3 lists, and 79 of 90 answers come out the
same. Where they differ, the alternative flattens bullets indented under a numbered item
(4 `gpt-4o-mini` answers) and drops the column alignment of a table (`nh3` removes
`style`). It is also two parts against one. Tom saw both and chose (D40).

**What S3 now rests on.** The page holds only the tags the renderer itself writes; there
is no allow-list. Tried by Architect with `markdown-it-py` 4.3.0: script and image tags,
inline and as a block, are shown as text; links with `javascript:`, `vbscript:`,
`data:` and `file:` targets, also in mixed case, as autolinks and as reference
definitions, are not made into links; a quote in a link title is escaped. That is a set
of samples, not an audit of the library. If a later feature needs HTML from the model,
this has to be designed again.

**Wide tables.** The answer is put in a `div` with `overflow-x: auto`, as an inline
style like the other styles in the templates. A table wider than the screen then
scrolls inside the answer and the page keeps its width. The tables seen have 2 to 3
columns and cells up to 357 characters, which wrap. **Not seen:** a table on a real
phone. Tom looks at one before the merge (local site, narrow window) and after the
deploy.

**Stored answers.** An answer is rendered when it is viewed, so the about 850 answers
on the server change renderer too. Checked: the 30 `gpt-4o-mini` evaluation answers,
where the only visible changes are lists that now show as lists and bullets that nest.
The server's stored answers were not rendered. A deploy check looks at some.

**Tests,** through the results page with Flask's test client where the page is the
subject, and with real archived answers as the text:

- An answer with a table (`gpt-6-luna` Q32) gives a `table`, and no line of the page
  starts with `|`.
- An answer whose list follows a text line directly (`gpt-6-luna` Q09) gives list items.
- Bullets indented under a numbered item (`gpt-4o-mini` Q02) are a list inside that item.
- Hostile text: the page has no `<script`, no `<img` and no `href` that starts with
  `javascript:` or `data:` from an answer that tries each; the tags appear as text.
- The answer is inside the `overflow-x` container.
- A site page with raw HTML in its Markdown still shows it as HTML.
- The rating page renders an answer with the same function.

**Also in this deploy.** `README.md` of `site_2024` names the models now used; it still
recommends `gpt-4o-mini`, `gpt-4o` and `gpt-5`.

**Deploy.** Code review of everything after `c311cda` except the model commit `1e72014`
(D37). Merge with Tom's approval, `git pull` on the server, rebuild the flask image,
start. Checks:

- A question is answered, and its statistics name `gpt-6-luna`.
- A dig deeper is answered, and its statistics name `gpt-6.2-sol`.
- A question that asks for a comparison in a table shows a table, also in a narrow window.
- Three stored answers from before the deploy, one of them with a list, read well.
- The home page looks as before.

Rollback: `git checkout c311cda`, rebuild, start. That also returns to `gpt-4o-mini`
and `gpt-4.1`, which answer until January 14.

**To watch afterwards.** `gpt-6.2-sol` answers were never sampled, so what a dig deeper
or a follow-up writes (code, quotes, wider tables) is unknown. CommonMark renders all of
those; how they look with the site's stylesheet was not seen.

---

## Phase 4: Website refresh: reference links and images

**[REVISED - 2026-11-21]** Per D8 these two items are the website refresh.

### 4.1 Reference links inside answers (D5)

Users want links to the source documents within the answer text, as Gemini does.
Today sources are listed below the answer only. To evaluate: label each chunk in
the prompt with its source id, ask the model to cite ids, convert ids to links
when rendering. Open points: citation accuracy of the cheap tier, and how to link
non-message sources (newsletters, Canard Pusher). Links rendered from model
output must go through the same sanitising as S3. Design after Phase 1.

**[REVISED - 2026-11-22]** Not part of the deploy with the model change (D39). It changes
the prompt, so its answers are not the ones Tom rated, and citation accuracy needs its
own check. S3 is closed by the answer renderer ("Answer display"); the links of this
feature are to be made by the site from ids, not taken as HTML from the model.

### 4.2 Image gallery for a result

A link on the results page to a page showing images from the messages that were
given to the model. The results page already carries each document's `source`
(Google Groups message id) and `imageGetter`'s index is keyed by the same ids, so
this is a lookup. Design after Phase 1.

---

## Risks

| Risk | Mitigation |
|---|---|
| Shutdown date reached before the model switch | **[REVISED - 2026-11-22]** The switch is committed (`1e72014`) and waits for the UI changes (D38). If those are not ready in time, it can be merged and deployed alone. |
| New models reject the current API call | Closed: all four candidates answer the current call on the upgraded SDK (0.7). |
| Chroma upgrade damages or cannot read the collection | Rehearsed on a local copy with before and after checks (0.6, passed); server data tarred before the deploy (0.8). A re-embed takes hours if both fail. |
| One deploy carries many changes | The full stack runs locally first; without Docker locally, Chroma is split out (Phase 0 assumptions). |
| Tom's rating and labelling time | 30 questions, not 50; pooled candidates capped at top 10 per variant. |
| Chunk experiment shows no clear winner | That is a valid result; the decision rule says leave it alone. |
| `site_2024` application code has no tests | Phase 1.1 introduces the first ones around prompt construction. Phase 0 was verified by the rehearsal checks instead. |
