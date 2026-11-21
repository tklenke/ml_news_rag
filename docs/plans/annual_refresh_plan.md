# Annual RAG / Website Refresh Plan

**Created:** 2026-11-21
**Status:** Plan approved in outline by Tom; ready for Programmer on Phase 1
**Owner:** Architect (design), Programmer (implementation)

## Design Revision History

- **2026-11-21:** Website refresh defined by Tom as reference links plus images (Phase 4).
  Phase 3 is now the fixes arising from a review of the site code and live server.
  Model evaluation gets checkpoints at 10, 20 and 30 questions. Chunk experiment
  question set proposed as the same 30 plus about 10 new, labelled in batches.

## Goal

Keep CozyRAG running past the OpenAI model shutdown, find out whether a different
chunk size improves retrieval, refresh the website, and evaluate two user-facing
additions (reference links in answers, image gallery for a result).

## Hard deadline

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
| D12 | Site review findings are fixed: S1 and S2 alongside Phase 1, S3 with the reference links, S4 to S7 after Phase 1 is deployed. S8 is logged as an opportunity for improvement. |

## Two repositories

| Concern | Repo | Key files |
|---|---|---|
| Chunking and embedding | `ml/` (this repo) | `embedder/embedder.py`, `embedder/f_embed.py` |
| Retrieval, prompts, LLM calls, results page | `../site_2024/` | `fwww/src/llm_functions.py`, `fwww/site.ini`, `fwww/templates/` |
| Image database | `ml/` | `imageGetter/` |

`site_2024` is on `main`, clean, and has **no automated tests**. Programmer follows
the same version-control rules there (WIP branch, frequent commits).

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
- **Format:** `docs/plans/refresh_questions.csv` with columns `question_id`,
  `question`, `kind` (`factual` / `broad`), `prod_job_id`, `prod_rating`.
- The logged per-question sources are **not** an answer key. They are what the
  current 250-word setup retrieved, so using them as truth would favour the baseline.

---

## Phase 1: Model migration (deadline-driven)

### 1.1 Defects to settle before any comparison

These change what the "dig deeper" tier actually sees, so they come first.

1. **Suspected: prior context is garbled in revise and follow-up.**
   `llm_functions.py` builds `priordocs` with `'\n\n'.join(rPriorDocs['documents'][0])`.
   Chroma `collection.get()` returns a flat list of documents, so `[0]` would be a
   single chunk's text and the join would split it into characters. Found by code
   reading only; **not confirmed**. Programmer writes a failing test first. If the
   test passes as written, the suspicion is wrong: record that and move on.
2. **Prompts name the model.** `revise_prompt` and `followup_prompt` say "the draft
   response from GPT-4o-mini". Reword so no model is named.
3. **Stale `__main__` block** in `llm_functions.py` passes a string to
   `process_question`, which expects a dict. Fix or remove with Tom's approval.

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

Unknown: whether these models accept the same `chat.completions` call the site
makes today. The site pins `openai==1.51.2` (October 2024), which may predate
them. Programmer makes one smoke call per candidate before building on it and
reports any difference, including a needed SDK upgrade, to Architect.

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
a config change plus the prompt wording from 1.1. Deploy with at least two weeks of
margin before January 14.

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
| S7 | Low | DokuWiki page source is served directly (`/dokucozy/data/pages/start.txt` returns 200), bypassing any wiki access rules. Matters only if a wiki has private pages. PHP 7 is past end of life. | nginx config, `php:7-fpm` | Deny `data/`, `conf/`, `bin/`, `inc/` in nginx. PHP upgrade is outside this refresh. |
| S8 | Low | Each of the 4 gunicorn workers starts its own job thread and scans every job file; `super().__init__()` is called after `daemon = True`, which resets it; a job whose worker dies stays in `start` forever. The jobs page reads every job file on each view. Works at current volume. | `llm_functions.py`, `site_functions.py` | Leave unless symptoms appear; log as an opportunity for improvement. |
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
- nginx `limit_req` on `/cozyrag/query` and `/cozyrag/followup`. The nginx config
  in the repo has HTTPS commented out and does not match production, so
  Programmer asks Tom how the production config is managed before editing it.

### Scheduling (D12)

- With Phase 1: S1, S2.
- With Phase 4.1 (reference links): S3.
- After Phase 1 is deployed: S4, S5, S6, S7. S7 has the same production nginx
  question as S2.
- Not scheduled: S8 (in `docs/notes/opportunities_for_improvement.md`), S9 (Tom confirms).

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
| Deadline missed | Phase 1 goes first; fallback is setting both tiers to OpenAI's recommended `gpt-6-luna` in `site.ini` without evaluation. |
| New models reject the current API call | Smoke call per candidate before anything else (1.3). |
| Tom's rating and labelling time | 30 questions, not 50; pooled candidates capped at top 10 per variant. |
| Chunk experiment shows no clear winner | That is a valid result; the decision rule says leave it alone. |
| `site_2024` has no tests | Phase 1.1 introduces the first ones around prompt construction. |
