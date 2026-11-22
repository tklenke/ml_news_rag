# Annual RAG / Website Refresh Plan

**Created:** 2026-11-21
**Status:** Revised 2026-11-21 (third revision); rehearsal approved, Phase 0 deploy next
**Owner:** Architect (design), Programmer (implementation)

## Design Revision History

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

## Two repositories

| Concern | Repo | Key files |
|---|---|---|
| Chunking and embedding | `ml/` (this repo) | `embedder/embedder.py`, `embedder/f_embed.py` |
| Retrieval, prompts, LLM calls, results page | `../site_2024/` | `fwww/src/llm_functions.py`, `fwww/site.ini`, `fwww/templates/` |
| Image database | `ml/` | `imageGetter/` |

`site_2024` has **no automated tests**. Its branch `wip/annual-refresh` exists with no
commits yet. Programmer follows the same version-control rules there.

## Order of work

**[REVISED - 2026-11-21]** Chosen so that nothing is built, tested or deployed twice (D15).

1. **Phase 0, one deploy:** infrastructure refresh. Tests and the evaluation harness
   are then written once, on the stack production runs.
2. **Phase 1 code change with the site fixes, one deploy:** 1.1 plus S1, S2, S4, S5, S6, S10.
   They touch the same files (`site_app.py`, `llm_functions.py`, `site_functions.py`).
3. **Phase 1 evaluation:** harness, baseline, blind review files, Tom rates, `site.ini` change.
4. **Phase 2,** overlapping step 3: the embedding runs take hours of machine time
   while Tom rates.
5. **Phase 4** with S3, designed once the model choice is known.

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
    certificate working. The live certificate expires 2027-01-26, so this must be
    deployed and tried before then.
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
merge. Memory on the new stack is 882 MiB against 806 MiB; the server has room. The
backup is `site_2024/data/chroma_backup_1.1.1`.

### 0.7 Smoke calls

One call to each candidate in 1.3 and to both current models, on the upgraded SDK.
This shows whether Tom's account has access and what the call looks like now. If the
call sites need changing for the new SDK, that change is part of Phase 0.

**[REVISED - 2026-11-21]** Result: both current models answer on SDK 3.57.0 with no
call-site change. All four candidates return 403 (no access for this OpenAI project).
Tom is arranging access; the candidate calls are repeated then. The Phase 0 deploy
does not wait for this.

### 0.8 Deploy

**[REVISED - 2026-11-21]** Steps rewritten. A plain `git pull` aborts on the server
because untracked files there are tracked in the new `main`; the old images are
tagged so a rollback needs no rebuild; the wikis are deleted rather than tarred.

Tom runs the server commands; Programmer supplies them and reads the output.

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

To make these testable, prompt construction is separated from the thread and the
API call: a function that takes the job data and document lists and returns the
prompt string. The evaluation harness (1.3) calls the same function, so it measures
what production sends. This is a small refactor of `process_question`, not a rewrite.

### 1.2 Capture the baseline before shutdown

Run the 30 questions through the current models (`gpt-4o-mini` first answer,
`gpt-4.1` revise) and save answers, token counts and latency. After January 14
this cannot be recreated. Do this after 1.1 so the baseline reflects the corrected
revise step; if 1.1 slips, capture the baseline anyway and note which code produced it.

### 1.3 Candidates

Prices per million tokens, input / output, from
https://developers.openai.com/api/docs/models (read 2026-11-21):

| Model | Price | First answer | Dig deeper |
|---|---|---|---|
| `gpt-6-luna` | $0.10 / $0.50 | candidate | |
| `gpt-6.1-terra` | $1 / $5 | candidate | candidate |
| `gpt-6.2-sol` | $2 / $10 | | candidate |
| `gpt-6.2-astra` | $8 / $40 | | only if `sol` is not good enough |

**[REVISED - 2026-11-21]** Unknown: whether these models accept the same
`chat.completions` call the site makes today. The SDK is upgraded in Phase 0 and the
smoke calls are made there (0.7).

### 1.4 Evaluation method

- Retrieval is run once per question and the same documents are given to every
  model, so only the model varies.
- Output: one review file per tier with, for each question, the answers from each
  model in random order and unlabelled. A separate key file maps positions to models.
- Tom rates each answer `perfect` / `ok` / `not_good` (the scale the site already
  uses) and notes any factual error. Factual errors matter most: this is aircraft
  construction advice.
- Harness also records tokens in, tokens out, latency, and computed cost per answer.

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

### 1.6 Rollout

Model names are already in `site.ini` (`LLM_DRAFT`, `LLM_REVISE`), so the switch is
a config change. The prompt wording from 1.1 is already deployed by then.
**[REVISED - 2026-11-21]** After S10 `site.ini` is tracked, so the switch is a commit
and a `git pull`.

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
| S2 | Medium (cost) | No rate limit on questions. Anyone can script submissions; each follow-up sends about 20,000 tokens to the better model. `/cozyrag/revise` also runs on a plain GET. | `site_app.py`, nginx | Set a monthly spend cap on the OpenAI account (Tom). Add nginx `limit_req` on `/cozyrag/`. Make revise POST-only. |
| S3 | Medium | Model output is rendered as raw HTML: the answer goes through Markdown, which passes HTML through, and is marked `safe`. A question can instruct the model to emit a script tag, and the result is stored and linked from the jobs page. | `cozyrag_results.html` line 11 | Sanitise the rendered HTML with an allow-list (for example `nh3`) before marking it safe. |
| S4 | Low | `sanitize()` does the opposite of its name: it wraps input in `Markup`, declaring it safe. Not exploitable today because values pass through JSON before display, but one template change away from being so. | `site_functions.py` | Remove the `Markup` wrap. |
| S5 | Low | Unknown job ids and several routes return HTTP 500: `processid` and `status` with a bad id, `jobs/<bad column>` (`abort` is never imported), and `revise` / `feedback` / `answer` without a session. | `site_app.py` | Return 404 or redirect to the question form. |
| S6 | Low | Feedback accepts any text as the rating, which is why the log contains values outside the three buttons. | `cozyrag_feedback` | Accept only `perfect`, `ok`, `not_good`. |
| S7 | Replaced | **[REVISED - 2026-11-21]** Both wikis are removed (D14, Phase 0.3). Original finding: DokuWiki page source is served directly (`/dokucozy/data/pages/start.txt` returns 200), bypassing any wiki access rules. Matters only if a wiki has private pages. PHP 7 is past end of life. | nginx config, `php:7-fpm` | Deny `data/`, `conf/`, `bin/`, `inc/` in nginx. PHP upgrade is outside this refresh. |
| S8 | Low | Each of the 4 gunicorn workers starts its own job thread and scans every job file; `super().__init__()` is called after `daemon = True`, which resets it; a job whose worker dies stays in `start` forever. The jobs page reads every job file on each view. Works at current volume. | `llm_functions.py`, `site_functions.py` | Leave unless symptoms appear; log as an opportunity for improvement. |
| S10 | Low | **[REVISED - 2026-11-21]** Keys share a file with the settings. `site.ini` holds the OpenAI and session keys beside the model names and retrieval limits, so it cannot be tracked: production settings are not in the repo, the template has drifted from what the code reads, and every tool or person reading a setting also reads the keys. The README's project tar includes `site.ini`. | `site.ini`, `site_app.py`, `exclude_from_tar.txt` | See "S10 design" below (D21). |
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

- Tom sets a monthly spend cap on the OpenAI account. This is the real backstop.
- `/cozyrag/revise` accepts POST only (the button already posts).
- nginx `limit_req` on `/cozyrag/query` and `/cozyrag/followup`. The repo's nginx
  config matches production after Phase 0.2. Programmer proposes the rate to Architect.

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

### Scheduling

**[REVISED - 2026-11-21]** (D15)

- With the Phase 1 code change, in one deploy: S1, S2, S4, S5, S6, S10.
- With Phase 4.1 (reference links): S3.
- Replaced by the DokuWiki removal in Phase 0.3: S7.
- Not scheduled: S8 (in `docs/notes/opportunities_for_improvement.md`).
- Closed: S9. Tom confirmed the tracked `.env_flask` only ever held a placeholder;
  the nginx mismatch is fixed by Phase 0.2.

## Phase 4: Website refresh: reference links and images

**[REVISED - 2026-11-21]** Per D8 these two items are the website refresh.

### 4.1 Reference links inside answers (D5)

Users want links to the source documents within the answer text, as Gemini does.
Today sources are listed below the answer only. To evaluate: label each chunk in
the prompt with its source id, ask the model to cite ids, convert ids to links
when rendering. Open points: citation accuracy of the cheap tier, and how to link
non-message sources (newsletters, Canard Pusher). Links rendered from model
output must go through the same sanitising as S3. Design after Phase 1.

### 4.2 Image gallery for a result

A link on the results page to a page showing images from the messages that were
given to the model. The results page already carries each document's `source`
(Google Groups message id) and `imageGetter`'s index is keyed by the same ids, so
this is a lookup. Design after Phase 1.

---

## Risks

| Risk | Mitigation |
|---|---|
| Shutdown date reached before the model switch | Tom expects a few days of effort (D15). Fallback is setting both tiers to OpenAI's recommended `gpt-6-luna` in `site.ini` without evaluation, once 0.7 shows it can be called. |
| New models reject the current API call | SDK upgraded and smoke calls made in Phase 0 (0.7). |
| Chroma upgrade damages or cannot read the collection | Rehearsed on a local copy with before and after checks (0.6, passed); server data tarred before the deploy (0.8). A re-embed takes hours if both fail. |
| One deploy carries many changes | The full stack runs locally first; without Docker locally, Chroma is split out (Phase 0 assumptions). |
| Tom's rating and labelling time | 30 questions, not 50; pooled candidates capped at top 10 per variant. |
| Chunk experiment shows no clear winner | That is a valid result; the decision rule says leave it alone. |
| `site_2024` has no tests | Phase 1.1 introduces the first ones around prompt construction. Phase 0 is verified by the rehearsal checks instead. |
