# Architect Todo - Image Database Project

**Project:** Image Database for Cozy Builders Newsgroup
**Architect:** Claude
**Created:** 2025-11-01
**Last Updated:** 2025-11-02

## Current Status

Phase: **Phase 1-2 Complete, Phase 3-5 Pending**
Next: Production download testing (Phase 2.9), then Programmer implements Phase 3

---

## Architectural Deliverables

### Design Phase
- [x] Analyze user requirements and constraints
- [x] Design overall architecture (simple text-based approach, not multimodal)
- [x] Create `docs/plans/image_database_architecture.md`
- [x] Create `docs/plans/image_database_implementation_plan.md`
- [x] Break down implementation into testable increments
- [x] Create `docs/plans/architect_todo.md` (this file)
- [x] Create `docs/plans/programmer_todo.md`

### Completed Architectural Tasks (2025-11-02)
- [x] Review Phase 1 implementation results
- [x] Validate URL filtering approach (blacklist strategy effective)
- [x] Review Phase 2 implementation (dual-path download working)
- [x] Document implementation details in architecture document
- [x] Prune programmer_todo.md (740 lines → 150 lines)
- [x] Update architecture document with actual implementation

### Completed Architectural Tasks (2025-11-03)
- [x] Finalize Phase 4b implementation design with Tom
- [x] Decide keywords storage location (image_index.json, not separate file)
- [x] Clarify scope (7k messages with images, not full corpus)
- [x] Design CLI interface (--limit, --overwrite, --keywords, --model flags)
- [x] Review existing LLM patterns (embedder/f_llm.py, asker/ask_models.py)
- [x] Design LLM tagging architecture (class-based KeywordTagger following f_llm.py pattern)
- [x] Design llm_config.py for Tom to edit model and prompt
- [x] Break down Phase 4b into TDD increments (4b.1-4b.6)
- [x] Update architecture document with Phase 4b details and LLM architecture
- [x] Update programmer_todo.md with detailed Phase 4b tasks and LLM guidance
- [x] Reorganize phases: Phase 4 → Phase 4b, create placeholder for Phase 4a

### Pending Architectural Tasks
- [ ] Design Phase 4a (Tom to specify requirements)
- [ ] Review Phase 4b LLM keyword tagging approach (after implementation)
  - [ ] Assess keyword list quality (coverage, precision)
  - [ ] Evaluate tagging accuracy
  - [ ] Decide if LLM prompts need refinement
  - [ ] Decide which Ollama model to use (gemma2:2b? llama?)
- [ ] Review Phase 5 keyword-based query results
  - [ ] Assess query precision/recall
  - [ ] Evaluate if keyword approach sufficient or need ChromaDB fallback

### Future Architectural Considerations (Post-Phase 5)
- [ ] Evaluate if text-based retrieval is sufficient
  - If not, design multimodal embedding architecture (CLIP/LLaVA)
- [ ] Design web interface architecture (if Tom requests it)
- [ ] Consider duplicate image detection strategy
- [ ] Consider image classification/tagging system

---

## Decision Log

### 2025-11-03: Phase Renumbering - Create Phase 4a Slot

**Decision:** Rename existing Phase 4 (LLM tagging) to Phase 4b, create Phase 4a for new program

**Rationale:**
- Tom has a new program to add before LLM tagging
- Renumber to preserve logical sequence
- Phase 4b design remains unchanged

**Changes:**
- Phase 4 → Phase 4b (all sub-phases: 4.1→4b.1, 4.2→4b.2, etc.)
- Phase 4a placeholder created (Tom to specify)
- All documentation updated (programmer_todo, architecture, architect_todo)

### 2025-11-03: Phase 4b Implementation Details - Keywords in Index

**Decision:** Store `llm_keywords` field inside image_index.json (not separate file)

**Rationale:**
- Scope is image search tool, not full corpus search (Tom has separate tool for that)
- Only tagging 7k messages with images (exact set in image_index.json)
- One source of truth - all image metadata in one file
- Simpler query logic - load one file, filter by keyword
- Natural structure - keywords are message metadata like subject/author

**CLI Interface Decisions:**
- `--limit N` processes first N messages (not counting skipped messages)
- `--overwrite` flag to retag existing llm_keywords (default: skip if present)
- `--keywords FILE` to use custom keyword list (default: keywords_seed.txt)
- Default behavior: skip messages where llm_keywords exists and not empty

**llm_keywords Field States:**
- `["firewall", "cowling"]` = tagged with keyword matches
- `[]` = tagged but no keywords matched (valid state, don't retag)
- Field missing = not yet tagged (needs processing)

**Keyword Discovery Process:**
- Small batch size: 5 messages (not 100) for faster review cycles
- Optional tool: `build_keyword_list.py --sample 5` to help expand keyword list
- Tom may use keywords_seed.txt (110 terms) as-is or expand iteratively

**Architecture Impact:**
- No separate message_keywords.json file needed
- Simpler query interface (Phase 5)
- Resume capability built-in (skip existing llm_keywords)
- Incremental processing with --limit flag

**LLM Configuration Design (llm_config.py):**
- Tom requested separate config file for model and prompt (not hardcoded)
- Pattern: Follow embedder/f_llm.py (class-based KeywordTagger)
- Error handling: Log and continue (don't crash on LLM errors)
- File contents:
  - OLLAMA_HOST = "http://localhost:11434"
  - LLM_MODEL = "gemma3:1b" (Tom can edit)
  - KEYWORD_TAGGING_PROMPT = "..." (Tom can experiment with prompt)
- Rationale: Separates configuration from code, enables rapid iteration on prompt engineering

### 2025-11-02: Phase 4b-5 Architecture Revision - LLM Keyword Tagging

**Decision:** Replace ChromaDB semantic search (original plan) with LLM keyword tagging approach

**Rationale:**
- **Simpler architecture** - No ChromaDB integration needed for image search
- **More interpretable** - Know exactly why images matched (keyword present)
- **Better precision** - Curated keyword list + LLM semantic matching at index-time
- **Faster queries** - Simple keyword lookup vs embedding computation
- **One-time cost** - LLM processing during indexing, not per-query
- **Debuggable** - Can review and refine keyword assignments

**New Phase Structure:**
- **Phase 4a:** TBD (Tom to specify)
- **Phase 4b: LLM Keyword Tagging** - Build keyword list, tag messages, store in image_index.json
- **Phase 5: Keyword-Based Query** - Simple lookup and HTML viewer
- **Old "Scale to full corpus" removed** - already happening organically

**Architecture Impact:**
- No ChromaDB metadata updates needed
- No embedding computation during queries
- New data file: message_keywords.json
- Query interface significantly simplified

### 2025-11-02: Phase 1-2 Implementation Review

**Implementation Enhancements Approved:**
- Blacklist filtering approach (~400+ junk images filtered at extraction time)
- Keyword extraction from filenames and message subjects for better searchability
- Dual-path download strategy (requests+cookies vs Selenium based on URL type)
- Size filtering removed (blacklist makes it redundant)
- Cookie extraction optimized (once at batch start, not per-image)

**Rationale:**
- Blacklist approach more precise than size filtering
- Keywords enable better search without multimodal embeddings
- Dual-path download handles Google Groups' two response types
- Optimizations prevent Selenium errors and improve performance

**Architecture Impact:**
- Index format evolved to message-centric structure with keywords
- Download strategy more complex but handles all URL types
- No fundamental architecture changes needed

### 2025-11-01: Initial Architecture Decisions

**Decision:** Use text-based RAG rather than multimodal embeddings for initial implementation
**Rationale:**
- Message text provides rich context ("here's my firewall")
- Simpler to implement and debug
- Leverages existing RAG infrastructure
- Can add multimodal later if insufficient

**Decision:** Center crop for thumbnails rather than smart crop
**Rationale:**
- Most build photos have subject centered
- Faster, no AI needed
- Consistent appearance
- Can iterate later if needed

**Decision:** 200x200px thumbnail size
**Rationale:**
- Good balance between visibility and disk space
- Standard size for grid displays
- Tom approved this size

**Decision:** JSON index rather than SQLite database
**Rationale:**
- Simpler, human-readable
- No additional dependencies
- Easy to version control and debug
- Can migrate to SQLite later if performance issues

**Decision:** Test on A/ directory before scaling to full corpus
**Rationale:**
- Tom requested this approach
- Validate architecture on subset
- Discover edge cases early
- Easier to iterate on small dataset

**Decision:** Filter out profile photos, logos, emojis
**Rationale:**
- Tom explicitly requested this
- Only want actual build/aircraft photos
- Profile photos are googleusercontent.com domain
- Attachments are groups.google.com/attach/ URLs

---

## Risks and Open Issues

### Current Risks
1. **Google Groups may block scraping**
   - Mitigation: Rate limiting, respectful user-agent, monitor for 429 errors
   - Status: Will assess during Phase 2

2. **Many image URLs may be broken (old posts)**
   - Mitigation: Accept if >60% success rate
   - Status: Will measure during Phase 2

3. **Text-based retrieval may have poor precision**
   - Mitigation: Can add multimodal embeddings in Phase 6+
   - Status: Will assess during Phase 4b

4. **Disk space may be insufficient**
   - Mitigation: Estimate after Phase 3, can use external drive
   - Status: Will measure after A/ directory complete

### Open Questions
1. Should we store original markdown path in image_index.json?
   - **Decision needed after Phase 1 results**

2. Do we need image versioning if re-downloading improves quality?
   - **Decision deferred until Phase 2 complete**

3. Should thumbnail size be configurable or fixed at 200x200?
   - **Current decision: Fixed at 200x200, can make configurable later if needed**

---

## Notes from Tom

- Wants simple approach, start easy and work up
- Prefers thumbnails grid (50-100 at a time) with click to expand
- Test on A/ directory first
- Filter out profile photos, emojis, logos
- 200x200 thumbnails with center crop

---

## Phase Review Schedule

After Programmer completes each phase, Architect should:
1. Review results and statistics
2. Validate architecture decisions still sound
3. Identify any issues requiring design changes
4. Update this todo with decisions made
5. Approve moving to next phase OR request design revision

---

## Communication with Programmer

**For Programmer:** See `programmer_todo.md` for detailed implementation tasks.

**When to escalate to Architect:**
- URL filtering not working as expected (too many false positives/negatives)
- Download success rate unexpectedly low (<50%)
- Integration with existing RAG system unclear
- Architectural assumptions don't match reality
- Major technical blockers

Use "Strange things are afoot at the Circle K" if you need immediate architectural attention.

---

## Deliverables Status

| Deliverable | Status | Location |
|------------|--------|----------|
| Architecture Document | Complete | `docs/plans/image_database_architecture.md` |
| Implementation Plan | Complete | `docs/plans/image_database_implementation_plan.md` |
| Architect Todo | Complete | `docs/plans/architect_todo.md` (this file) |
| Programmer Todo | Complete | `docs/plans/programmer_todo.md` |
| Phase 1 Review | Pending | After Programmer completes Phase 1 |
| Phase 2 Review | Pending | After Programmer completes Phase 2 |
| Phase 3 Review | Pending | After Programmer completes Phase 3 |
| Phase 4a Review | Pending | After Programmer completes Phase 4a |
| Phase 4b Review | Pending | After Programmer completes Phase 4b |
| Phase 5 Review | Pending | After Programmer completes Phase 5 |

---

**Last Updated:** 2025-11-03 by Claude (Architect)
