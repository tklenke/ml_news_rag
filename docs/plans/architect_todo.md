# Architect Todo - Image Database Project

**Last Updated:** 2025-11-06

---

# ACTIVE WORKSTREAM: Annual RAG/Website Refresh (started 2026-11-21)

**Status:** Plan written: `annual_refresh_plan.md`. Tom's decisions recorded there and in
`required_from_tom.md`. Phase 1 (model migration, deadline 2027-01-14) is ready for Programmer.

## Goal (from Tom)

Annual refresh of the RAG system + website; image database later. Focus areas:
1. **Retrieval mechanism** — "cludgy but works," probably leave as-is.
2. **RAG ingestion** — reconsider chunk size (currently 250 words, no overlap).
3. **Model + results** — OpenAI is sunsetting the model in use; must choose a replacement.
4. **Website** — refresh.
5. **Stretch:** add a link on the results page to a dynamic page showing all images
   from the messages that "made the RAG cut." (Ties back to image database.)

## Key Architecture Findings (from code investigation)

**The refresh spans TWO repositories:**

| Concern | Lives in | Current state |
|---|---|---|
| RAG ingestion (chunk + embed) | `ml/embedder/` (this repo) | `nomic-embed-text`; **chunk = 250 words, NO overlap** (`CHUNKSIZE=250` in `embedder.py`, split logic in `f_embed.py:chunksplitter`); doc prefix `search_document:` |
| Retrieval + LLM + results page | `../site_2024/fwww/` (SEPARATE git repo) | Flask job-queue; **two-stage LLM: draft=`gpt-4o-mini` → revise=`gpt-4.1`** (`fwww/src/llm_functions.py`) |
| Model experimentation | `ml/asker/`, `ml/modelTesting/` | throwaway harnesses (`ask_models.py`, `ask_chatgpt.py`, `askQuestions.py`) |
| Image database | `ml/imageGetter/` | Phase 6 done; revisit later |

**Live production RAG config** (`../site_2024/fwww/site.ini`):
- `EMBED = nomic-embed-text`, `PREFIX = search_query:` (asymmetric prefix is CORRECT — no bug)
- `LLM_DRAFT = gpt-4o-mini`, `LLM_REVISE = gpt-4.1` (both OpenAI → sunset exposure)
- `MAX_DISTANCE = .35`, `MIN_DOCUMENTS = 5`, `MAX_DOCUMENTS = 60`, `MAX_DRAFT_DOCUMENTS = 15`
- `USE_GPT = True`, `SHOW_REVISE = True`

**Observations shaping the plan:**
- Retrieval is fine. Only cludgy bit: `get_num_draft_docs()` in `llm_functions.py` (scans
  backward for last doc under threshold). Works; low priority.
- **Image-gallery stretch feature is very feasible.** Results page (`fwww/templates/cozyrag_results.html`)
  already renders each doc's `source` (= Google Groups message ID) via `originid_anchor`.
  The image DB (`imageGetter/`) is keyed by the SAME message IDs → direct join.
- **Chunk-size change = full corpus re-embed** (data/msgs, news, aeroelectric, cozybuilders).
  Only worth it if it measurably improves retrieval → wants an experiment, not a guess.
- Note: `ml/asker/` harnesses query the `all-minilm` collection, but production + embedder use
  `nomic-embed-text`. The asker/ scripts are stale test harnesses, NOT the production path.

## Questions answered by Tom (2026-11-21)

1. **User-requested feature:** reference links to source documents inside the answer text
   (as Gemini does). Nice-to-have; evaluate after the other work.
2. **OpenAI sunset:** all GPT-4 versions. Both production models shut down 2027-01-14.
3. **LLM strategy:** stay with OpenAI; keep cheap first answer plus better "dig deeper" model.
4. **Chunk size:** test it; Architect guides test design and evaluation criteria.

## Completed

- [x] Get answers to the 4 open questions.
- [x] Decide plan-doc location: master plan in `ml/docs/plans/annual_refresh_plan.md`,
      cross-repo tasks noted per phase.
- [x] Write the refresh plan, `required_from_tom.md`, and the Phase 1 / Phase 2 breakdown
      in `programmer_todo.md`.

## NEXT STEPS (resume point)

- [x] Propose a shortlist from https://m24tom.com/cozyrag/jobs for Tom to pick from:
      52 candidates in `refresh_question_candidates.csv` (25 factual, 27 broad; `long_doc`
      marks likely newsletter / Canard Pusher / AeroElectric answers). Built from the 835
      logged jobs: 691 first-answer jobs, 624 after dropping short entries and exact repeats.
- [x] Tom approved all 52. Candidates file renamed to `refresh_questions.csv` with a `use`
      column: three balanced batches of 10, 10 chunk-only, 12 reserve.
- [x] Note for Programmer to get the production nginx config from Tom at the start.
- [ ] Review Programmer's finding on the suspected revise-context defect (plan 1.1).
- [ ] Review Programmer's smoke-call report on the GPT-6 candidates (plan 1.3).
- [x] Scope the website refresh with Tom: reference links and images only (plan Phase 4).
- [x] Review `site_2024` code and live server for serious errors and security concerns;
      findings S1 to S9 in plan Phase 3.
- [x] Add 10 / 20 / 30 checkpoints to the model evaluation (plan 1.5).
- [x] Propose the chunk experiment question set: same 30 plus about 10 new (plan 2.3).
- [x] Get Tom's choice of which S findings to fix; tasks added to `programmer_todo.md`,
      S1 and S2 designs added to the plan.
- [x] Get Tom's confirmation of the chunk experiment question set (mixed).
- [x] Create `docs/notes/opportunities_for_improvement.md` with the job-processing item (S8).
- [ ] Approve the nginx rate Programmer proposes for S2b.
- [ ] Design reference links (plan 4.1) and image gallery (4.2) after Phase 1.

## Findings from the production job log (2026-11-21)

- About 850 logged questions; about 45 carry a rating and roughly 20 of those are `n/a`.
  Rating scale changed over time (awesome/useful/meh, later perfect/ok/not_good).
- Typical first answer: about 4,500 tokens in, 300 out, 5 s on `gpt-4o-mini`.
  Follow-up sampled: about 21,000 tokens in on `gpt-4.1`.
- Answers do not cite sources in their text.
- `site_2024` has no automated tests.

## Housekeeping

- [x] Work moved to branch `wip/annual-refresh`.
- [x] `docs/acronyms.md` and `docs/style-guide.md` named the wrong project (`ea_tools`); corrected
      to `ml_news_rag`. Unused KiCAD acronym (SD) removed, RAG added.
- [x] Untracked debugging snippet `docs/input/compare.html` deleted per Tom.
- [x] `docs/notes/opportunities_for_improvement.md` created with its first item.
- Note: no root `requirements.txt`; dependencies are per-module.

---

## Current Status

**Phase:** Phase 6 (Keyword Scoring) design complete, ready for Programmer implementation

**Documentation:**
- Design: `image_database_design.md` (updated with Phase 6 scoring design)
- Programmer instructions: `programmer_todo.md` (rewritten with 7 detailed implementation tasks)

---

## Completed Tasks

### Phase 6 Design - Keyword Scoring
- [x] Design image-level keyword scoring approach
- [x] Define JSON schema for scored keywords: `[["keyword", score], ...]`
- [x] Document KeywordScorer algorithm (proximity + subject bonus + frequency + length)
- [x] Update image_database_design.md with Phase 6 details
- [x] Write comprehensive programmer_todo.md with TDD instructions
- [x] Plan archival strategy for unused LLM tagger code

---

## Pending Tasks

### Phase 6 Oversight
- [ ] Monitor Programmer implementation progress
- [ ] Review any design questions that arise during implementation
- [ ] Validate scoring algorithm parameters if issues arise
- [ ] Review completed implementation before deployment

### User Testing and Evaluation (Post Phase 6)
- [ ] Review Phase 6 after Tom tests scored static site
  - [ ] Assess if scoring improves image relevance ordering
  - [ ] Determine appropriate score threshold value (currently 0)
  - [ ] Decide if scores should be displayed to users or hidden
  - [ ] Evaluate if 557 keywords provide adequate coverage
- [ ] If issues arise, revise scoring parameters or keyword strategy

---

## Open Questions

1. Is vocabulary size (557 keywords) sufficient for coverage?
2. What score threshold should we use for display filtering? (default: 0, but may want 10-20)
3. Should we display scores to users or keep them invisible for ranking only?
4. Will image-level scoring be accurate enough, or do we need multimodal embeddings?
5. Should we track query analytics to improve keyword list and scoring weights?

---

## Current Risks

1. **Scoring algorithm parameters may need tuning**
   - Mitigation: Designed with configurable threshold, can adjust weights if needed
   - Designed for fast iteration (no LLM dependency)

2. **Image-level scoring may not match user expectations**
   - Mitigation: User testing will validate approach
   - Can fall back to multimodal embeddings if text-based scoring insufficient

---

## Design Decisions Made (Phase 6)

1. **Image-level scoring only** (no message-level keywords)
   - Rationale: Each image in multi-image message needs independent scores

2. **Proximity-based scoring** (exponential decay from image URL)
   - Rationale: Keywords near image are more relevant than distant ones

3. **Integer scores** (rounded from float calculations)
   - Rationale: Reduces JSON file size ~25%, precision loss negligible for ranking

4. **Score threshold parameter** (WAPGNI - probably gonna need it!)
   - Rationale: Allows future noise filtering without code changes

5. **Archive LLM tagger** (not delete)
   - Rationale: Not being used, search-based scoring sufficient and faster

---

## Escalation Protocol

**When Programmer should escalate to Architect:**
- Design ambiguities or conflicts in implementation
- Scoring algorithm parameters causing issues
- Performance problems with scoring
- Test failures suggesting design problems
- Major technical blockers

Use "Strange things are afoot at the Circle K" for immediate attention.

---

**Last Updated:** 2025-11-06 by Claude (Architect)
