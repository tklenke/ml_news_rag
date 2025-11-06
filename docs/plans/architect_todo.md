# Architect Todo - Image Database Project

**Last Updated:** 2025-11-06

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
