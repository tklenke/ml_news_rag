# Annual RAG / Website Refresh Plan

**Created:** 2026-11-21
**Status:** Plan approved in outline by Tom; ready for Programmer on Phase 1
**Owner:** Architect (design), Programmer (implementation)

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

Both experiments use one question set drawn from the production log at
https://m24tom.com/cozyrag/jobs (about 850 real questions as of 2026-11-21).

- **Size:** 30 questions.
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
makes today. Programmer makes one smoke call per candidate before building on it
and reports any difference to Architect.

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

For each tier, choose the **cheapest** candidate that has no more `not_good`
ratings and no more factual errors than the baseline. If none qualifies, escalate
to the next model up and discuss with Tom.

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

### 2.3 Labelling (needs Tom)

1. For each question, take the top 10 chunks from every variant and merge them by
   source document.
2. Harness writes `chunk_labels.csv`: `question_id`, `source_id`, link to the
   message or newsletter, a short excerpt, and an empty `relevant` column. Rows are
   shuffled and do not say which variant found them.
3. Tom marks each row `y` or `n`: does this document help answer the question?

Expected effort: roughly 15 to 25 rows per question, so 450 to 750 judgements, a
few hours in total. This is the main cost of the experiment and it falls on Tom.

### 2.4 Metrics

Measured at a fixed 15 chunks (what the first-answer model receives), because the
`MAX_DISTANCE = .35` cutoff is not comparable between chunk sizes.

- **Hit rate:** share of questions with at least one relevant source in the top 15.
- **Relevant sources found:** average count of distinct relevant sources in the top 15.
- **First relevant rank:** average position of the first relevant chunk.
- **Context size:** average words in the top 15, since larger chunks cost more per question.

### 2.5 Decision rule (fixed before running)

Re-embed production only if a variant beats the baseline on hit rate by 3 or more
questions out of 30, or matches it on hit rate and finds clearly more relevant
sources. Otherwise leave chunking alone and record the result.

If a variant wins:
- Read answers side by side on 10 questions (baseline versus winner) as a sanity check.
- Re-tune `MAX_DISTANCE`, `MAX_DRAFT_DOCUMENTS` for the new chunk size.
- The site selects its collection by embed-model name. Add a collection setting to
  `site.ini` so the switch and any rollback are config changes. Not built unless a
  variant wins.

---

## Phase 3: Website refresh

**Not yet scoped.** Tom has said "refresh" but not what it covers. Needs a scoping
conversation before any design. Known inputs:

- The jobs page (`/cozyrag/jobs`) is readable without login and shows every
  question and truncated submitter names. Tom to say whether that is intended.
- `README.md` TODO notes (docker front end, dokucozy, TkBlog) may or may not belong here.

## Phase 4: Evaluations

### 4.1 Reference links inside answers (D5)

Users want links to the source documents within the answer text, as Gemini does.
Today sources are listed below the answer only. To evaluate: label each chunk in
the prompt with its source id, ask the model to cite ids, convert ids to links
when rendering. Open points: citation accuracy of the cheap tier, and how to link
non-message sources (newsletters, Canard Pusher). Design after Phase 1.

### 4.2 Image gallery for a result (stretch)

A link on the results page to a page showing images from the messages that were
given to the model. The results page already carries each document's `source`
(Google Groups message id) and `imageGetter`'s index is keyed by the same ids, so
this is a lookup. Design after Phase 3 scope is known.

---

## Risks

| Risk | Mitigation |
|---|---|
| Deadline missed | Phase 1 goes first; fallback is setting both tiers to OpenAI's recommended `gpt-6-luna` in `site.ini` without evaluation. |
| New models reject the current API call | Smoke call per candidate before anything else (1.3). |
| Tom's rating and labelling time | 30 questions, not 50; pooled candidates capped at top 10 per variant. |
| Chunk experiment shows no clear winner | That is a valid result; the decision rule says leave it alone. |
| `site_2024` has no tests | Phase 1.1 introduces the first ones around prompt construction. |
