# Architect Todo - Image Database Project

**Project:** Image Database for Cozy Builders Newsgroup
**Architect:** Claude
**Created:** 2025-11-01
**Last Updated:** 2025-11-01

## Current Status

Phase: **Design Complete**
Next: Ready for Programmer implementation

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

### Pending Architectural Tasks
- [ ] Review Phase 1 results after Programmer completes URL extraction
- [ ] Validate URL filtering approach based on A/ directory results
- [ ] Review Phase 2 results (download success rate, error patterns)
- [ ] Assess whether rate limiting strategy is adequate
- [ ] Review Phase 3 results (thumbnail quality, sizing)
- [ ] Review Phase 4 integration with existing RAG system
- [ ] Evaluate retrieval quality and decide if architecture needs revision
- [ ] Review Phase 5 full corpus statistics
- [ ] Document any architectural decisions made during implementation

### Future Architectural Considerations (Post-Phase 5)
- [ ] Evaluate if text-based retrieval is sufficient
  - If not, design multimodal embedding architecture (CLIP/LLaVA)
- [ ] Design web interface architecture (if Tom requests it)
- [ ] Consider duplicate image detection strategy
- [ ] Consider image classification/tagging system

---

## Decision Log

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
   - Status: Will assess during Phase 4

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
| Phase 4 Review | Pending | After Programmer completes Phase 4 |
| Phase 5 Review | Pending | After Programmer completes Phase 5 |

---

**Last Updated:** 2025-11-01 by Claude (Architect)
