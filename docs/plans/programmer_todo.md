# Programmer Todo - Image Database Project

**Last Updated:** 2025-11-05

## Current Status

**Completed:** Phases 1-4b (URL extraction, downloads, thumbnails, keyword tagging, curation tools)

**Next:** Phase 5 - Keyword-Based Query Interface

**Tests:** 110+ passing, 14 skipped

**History:** See git log and `image_database_design.md` for implementation details

---

## Phase 5: Keyword-Based Query Interface

**Goal:** Simple query interface using keyword index from Phase 4b

**Scope:** No ChromaDB - just keyword lookup in image_index.json

### Phase 5.1: Query Function (TDD)

**Tasks:**
1. [ ] Create `imageGetter/query_images.py` with ABOUTME comments
2. [ ] Create `imageGetter/tests/test_query.py`
3. [ ] Write failing tests:
   - `test_query_by_single_keyword()`
   - `test_query_by_multiple_keywords()` (OR logic)
   - `test_return_images_for_matching_messages()`
   - `test_handle_keyword_not_found()`
4. [ ] Run tests - verify all fail
5. [ ] Implement `query_images(keywords=None, index_data=None) -> list[dict]`
6. [ ] Run tests - verify all pass
7. [ ] Commit: "Implement keyword query function"

**Output Format:**
```python
[
  {
    "message_id": "A1NtxlDfY4c",
    "subject": "Re: Firewall installation",
    "matched_keywords": ["firewall", "engine mount"],
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

**Tasks:**
1. [ ] Create `imageGetter/query_images_cli.py` script with ABOUTME comments
2. [ ] Add command-line arguments:
   - `--keywords` (comma-separated list)
   - `--index` (path to image_index.json)
   - `--max-results` (default 50)
3. [ ] Display results:
   - Message subject and ID
   - Matched keywords
   - List of thumbnail paths
   - Total results count
4. [ ] Test with sample queries
5. [ ] Commit: "Add CLI tool for keyword queries"

**Usage:**
```bash
# Query by single keyword
python query_images_cli.py --keywords firewall --index ../data/image_index.json

# Query by multiple keywords (OR logic)
python query_images_cli.py --keywords firewall,cowling --index ../data/image_index.json
```

---

### Phase 5.3: Simple Thumbnail Viewer

**Tasks:**
1. [ ] Create `imageGetter/generate_thumbnail_page.py` script with ABOUTME comments
2. [ ] Takes query results and generates static HTML file
3. [ ] HTML displays:
   - Thumbnail grid (3-4 columns)
   - Message subject/ID under each thumbnail
   - Matched keywords displayed
   - Click thumbnail to view full resolution
4. [ ] Test with firewall query results
5. [ ] Commit: "Add HTML thumbnail viewer"

**Usage:**
```bash
python query_images_cli.py --keywords firewall --output results.json
python generate_thumbnail_page.py results.json --output results.html
```

---

### Phase 5.4: Validate Results

**Tasks:**
1. [ ] Test queries:
   - "firewall" - expect firewall/bulkhead photos
   - "cowling" - expect cowling/engine cowl photos
   - "canard" - expect canard wing photos
   - "landing gear" - expect landing gear photos
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

## Escalation Protocol

**When to escalate to Architect:**
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

**Last Updated:** 2025-11-05 by Claude (Programmer)
