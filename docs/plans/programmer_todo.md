# Programmer Todo - Image Database Project

**Last Updated:** 2025-11-05

## Current Status

**Completed:**
- Phase 1-3: URL extraction, downloads, thumbnails ✓
- Phase 4a: Keyword building code (Tom bypassed execution) ✓
- Phase 4b: LLM keyword tagging ✓
- Image Curation Tools: dedupe, HTML review, batch removal ✓

**Next:** Phase 5 - Keyword-Based Query Interface

**Test Status:** 110 tests passing, 14 skipped

---

## Recent Changes Summary (2025-11-04 to 2025-11-05)

### CLI Standardization (2025-11-05)

All CLI tools now follow consistent `python program SOURCE [DEST] [options]` pattern:

**Changes made:**
1. **tag_messages_cli.py**
   - Changed from `INDEX_FILE --output` to `SOURCE [DEST]`
   - Removed `--overwrite` flag (always skips already-tagged messages)
   - Default DEST: `{source}_tagged.{ext}`
   - Updated `tag_messages()` function to accept `output_file` parameter

2. **build_keywords_cli.py**
   - Changed from `INDEX_FILE --output FILE` to `SOURCE [DEST]`
   - Moved `--output` to positional DEST argument
   - Default DEST: `{source}_keywords.txt`

3. **analyze_tag_statistics.py**
   - Changed from `index_file --output FILE` to `SOURCE [DEST]`
   - Moved `--output` to positional DEST argument
   - Default DEST: `{source}_statistics.txt`

**Tools already following pattern:**
- download_images_cli.py ✓
- extract_image_urls.py ✓
- dedupe_images_cli.py ✓
- remove_images_cli.py ✓
- generate_thumbnails_cli.py ✓ (kept --force flag as requested)

**Tests:** 110 passing, 14 skipped

### Chapter Categorization Removed
**Commits:** 48c2e91, 6450e90

Chapter tagging was not working correctly and was removed:
- Removed `categorize_message()` integration from tag_messages.py
- Removed chapter statistics from analyze_tag_statistics.py
- Removed chapter-related tests
- LLM code (`llm_tagger.categorize_message()`) remains but is not used

### Image Curation Tools Added
**Commits:** 7520d30, 8c11bea, c8bc557, 1ca0962, a03fa8e, 0d396f5, 78e0d42, 859ed27

New tools for manual image curation workflow:

1. **dedupe_images_cli.py** (commit 7520d30)
   - Removes duplicate images by file size
   - Removes images with missing files
   - Tested: removed 691 duplicates + 23 missing from test.idx
   - 7 tests passing

2. **analyze_tag_statistics.py** (commits 1ca0962, a03fa8e, 0d396f5, 78e0d42)
   - Generates paginated HTML views with thumbnails (210 per page)
   - Interactive checkboxes for image selection
   - Select All/Clear All buttons with selection counter
   - Export removal list button downloads images_to_remove_pageN.txt
   - Red highlighting for selected images
   - Navigation between pages (First/Previous/Next/Last)

3. **remove_images_cli.py** (commits 8c11bea, c8bc557)
   - Batch removes images based on removal list files
   - Supports wildcard patterns (images_to_remove_page*.txt)
   - Removes empty messages (messages with no images remaining)
   - Tested: removed 68 images from 40 messages, deleted 157 empty messages
   - 13 tests passing

4. **LLM Model Updated** (commit 859ed27)
   - Changed from gemma3:1b to gemma3:4b for better accuracy

**Workflow:** dedupe → generate HTML → review in browser → export removal lists → batch remove

See `imageGetter/README.md` for complete workflow documentation.

---

## Phase 5: Keyword-Based Query Interface

**Goal:** Simple query interface using Phase 4b keywords

**Scope:** No ChromaDB integration - just keyword lookup in image_index.json

**Status:** PENDING

### Phase 5.1: Query Function (TDD)
**Deliverable:** Function to search messages by keyword

**Tasks:**
1. [ ] Create `imageGetter/query_images.py` with ABOUTME comments
2. [ ] Create `imageGetter/tests/test_query.py`
3. [ ] Write failing test: `test_query_by_single_keyword()`
4. [ ] Write failing test: `test_query_by_multiple_keywords()` (OR logic)
5. [ ] Write failing test: `test_return_images_for_matching_messages()`
6. [ ] Write failing test: `test_handle_keyword_not_found()`
7. [ ] Run tests - verify all fail
8. [ ] Implement `query_images(keywords=None, index_data=None) -> list[dict]`
9. [ ] Run tests - verify all pass
10. [ ] Commit: "Implement keyword query function"

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
**Deliverable:** Command-line tool to search for images

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
**Deliverable:** HTML page to view thumbnail grid

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

### Phase 5.4: Validate Phase 5 Results
**Deliverable:** Assessment of query quality

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

**Last Updated:** 2025-11-05 by Claude (Programmer)
**Summary:** Updated to reflect chapter categorization removal and image curation tools added
