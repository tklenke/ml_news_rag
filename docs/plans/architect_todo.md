# Architect Todo - Image Database Project

**Last Updated:** 2025-11-06

---

# ACTIVE WORKSTREAM: Annual RAG/Website Refresh (started 2026-11-21)

**Status:** Discovery complete, plan NOT yet written. Resume here next session.

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

## OPEN QUESTIONS — blocking plan authoring (need Tom)

1. **User-requested features** — Tom mentioned "a couple of features users would like to add."
   NOT yet described. Need the list to scope them.
2. **OpenAI sunset specifics** — WHICH model is sunset (`gpt-4o-mini`, `gpt-4.1`, or both)?
   Deadline? (Then research successor options.)
3. **LLM strategy decision** (options prepared, not yet answered): evaluate-then-decide
   (use modelTesting harness) / stay OpenAI successors / go local Ollama / switch to Claude.
4. **Chunk-size approach decision** (options prepared, not yet answered): run a sweep
   experiment / pick a value & re-embed / leave as-is.

## NEXT STEPS (resume point)

- [ ] Get answers to the 4 open questions above (was mid-asking when session paused).
- [ ] Decide plan-doc location/scope (proposed: a master refresh plan in `ml/docs/plans/`,
      noting cross-repo tasks that land in `../site_2024/`).
- [ ] Write the refresh plan + programmer_todo breakdown.

## Housekeeping

- [x] Work moved to branch `wip/annual-refresh`.
- [x] `docs/acronyms.md` and `docs/style-guide.md` named the wrong project (`ea_tools`); corrected
      to `ml_news_rag`. Unused KiCAD acronym (SD) removed, RAG added.
- [x] Untracked debugging snippet `docs/input/compare.html` deleted per Tom.
- [ ] `docs/notes/opportunities_for_improvement.md` referenced by architect role but does not
      exist. Create it when there is a first item to log.
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
