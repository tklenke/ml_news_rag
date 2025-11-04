# Programmer Todo - Image Database Project

**Last Updated:** 2025-11-04 (Architect review)

## Current Status

**Completed:**
- Phase 1-3: URL extraction, downloads, thumbnails ✓
- Phase 4a: Keyword building code (Tom bypassed execution) ✓
- Phase 4b: LLM keyword tagging and chapter categorization ✓

**Next:** Phase 5 - Keyword-Based Query Interface

**Test Status:** 95 tests passing, 14 skipped

---

## Phase 5: Keyword-Based Query Interface

**Goal:** Simple query interface using Phase 4b keywords and chapters

**Scope:** No ChromaDB integration - just keyword/chapter lookup in image_index.json

**Status:** PENDING

### Phase 5.1: Query Function (TDD)
**Deliverable:** Function to search messages by keyword and/or chapter

**Tasks:**
1. [ ] Create `imageGetter/query_images.py` with ABOUTME comments
2. [ ] Create `imageGetter/tests/test_query.py`
3. [ ] Write failing test: `test_query_by_single_keyword()`
4. [ ] Write failing test: `test_query_by_multiple_keywords()` (OR logic)
5. [ ] Write failing test: `test_query_by_chapter()`
6. [ ] Write failing test: `test_query_by_keyword_and_chapter()` (AND logic)
7. [ ] Write failing test: `test_return_images_for_matching_messages()`
8. [ ] Write failing test: `test_handle_keyword_not_found()`
9. [ ] Run tests - verify all fail
10. [ ] Implement `query_images(keywords=None, chapters=None, index_data=None) -> list[dict]`
11. [ ] Run tests - verify all pass
12. [ ] Commit: "Implement keyword and chapter query function"

**Output Format:**
```python
[
  {
    "message_id": "A1NtxlDfY4c",
    "subject": "Re: Firewall installation",
    "matched_keywords": ["firewall", "engine mount"],
    "matched_chapters": [4, 15],
    "images": [
      {
        "thumbnail_path": "data/images/thumbs/A1NtxlDfY4c_part0_1_thumb.jpg",
        "full_path": "data/images/full/A1NtxlDfY4c_part0_1.jpg"
      }
    ]
  }
]
```

---

### Phase 5.2: CLI Query Tool
**Deliverable:** Command-line tool to search for images

**Tasks:**
1. [ ] Create `imageGetter/query_images_cli.py` script with ABOUTME comments
2. [ ] Add command-line arguments:
   - `--keywords` (comma-separated list)
   - `--chapters` (comma-separated chapter numbers)
   - `--index` (path to image_index.json)
   - `--max-results` (default 50)
3. [ ] Display results:
   - Message subject and ID
   - Matched keywords and chapters
   - List of thumbnail paths
   - Total results count
4. [ ] Test with sample queries
5. [ ] Commit: "Add CLI tool for keyword and chapter queries"

**Usage:**
```bash
# Query by keywords
python query_images_cli.py --keywords firewall,cowling --index ../data/image_index.json

# Query by chapter
python query_images_cli.py --chapters 4,15 --index ../data/image_index.json

# Query by both
python query_images_cli.py --keywords firewall --chapters 15 --index ../data/image_index.json
```

---

### Phase 5.3: Simple Thumbnail Viewer
**Deliverable:** HTML page to view thumbnail grid

**Tasks:**
1. [ ] Create `imageGetter/generate_thumbnail_page.py` script with ABOUTME comments
2. [ ] Takes query results and generates static HTML file
3. [ ] HTML displays:
   - Thumbnail grid (3-4 columns)
   - Message subject/ID under each thumbnail
   - Matched keywords and chapters displayed
   - Click thumbnail to view full resolution
4. [ ] Test with firewall query results
5. [ ] Commit: "Add HTML thumbnail viewer"

**Usage:**
```bash
python query_images_cli.py --keywords firewall --output results.json
python generate_thumbnail_page.py results.json --output results.html
```

---

### Phase 5.4: Validate Phase 5 Results
**Deliverable:** Assessment of query quality

**Tasks:**
1. [ ] Test queries:
   - "firewall" - expect firewall/bulkhead photos
   - "cowling" - expect cowling/engine cowl photos
   - Chapter 4 - expect fuselage bulkhead photos
   - Chapter 23 - expect engine installation photos
2. [ ] Assess results:
   - Are returned images relevant?
   - Any false positives?
   - Any obvious missing results?
3. [ ] Document in `docs/notes/phase5_results.md`:
   - Query examples and results
   - Precision/recall estimates
   - User experience assessment
4. [ ] Get Tom's feedback on query quality
5. [ ] Commit: "Complete Phase 5 with validation results"

---

## When to Escalate to Architect

- Query interface design unclear
- Major technical blockers
- Architecture assumptions don't match reality

Use "Strange things are afoot at the Circle K" for urgent issues.

---

## Before Every Commit

- [ ] Run tests: `pytest`
- [ ] Update this file with progress
- [ ] Include updated programmer_todo.md in commit

---

**Last Updated:** 2025-11-04 by Claude (Architect)
