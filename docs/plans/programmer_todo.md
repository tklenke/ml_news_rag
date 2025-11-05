# Programmer Todo - Image Database Project

**Last Updated:** 2025-11-05

## Current Status

**Completed:**
- Phase 1-3: URL extraction, downloads, thumbnails ✓
- Phase 4a: Keyword building code (Tom bypassed execution) ✓
- Phase 4b: LLM keyword tagging ✓
- Image Curation Tools: dedupe, HTML review, batch removal ✓

**Next:** Phase 5 - Keyword-Based Query Interface

**Test Status:** 130 tests passing, 14 skipped (+20 new tests for search tagger)

---

## Recent Changes Summary (2025-11-04 to 2025-11-05)

### Search Tagger Keyword Merging Fix (2025-11-05)
**Commits:** bf2da16, c1abd50, f2dee1b, cc9afd9, 84cd645

**Problem Identified:**
Search tagger was **skipping messages that already had keywords** instead of merging new matches with existing keywords. This prevented proper integration with `extract_image_urls.py` which creates image-level keywords.

**Root Cause:**
Skip logic was leftover from LLM tagging where:
- Processing was slow (30s per message)
- You might need to restart and resume
- Skipping already-tagged messages made sense

But with fast search tagging:
- Processing is instant
- Workflow involves TWO keyword sources:
  1. `extract_image_urls.py` → creates image-level keywords
  2. `search_tag_messages.py` → creates message-level keywords
- Both sources needed to coexist (no data loss)

**Solution Implemented:**
Changed search_tag_messages.py to **merge keywords** instead of skip:

```python
# Get existing keywords (if any)
existing_keywords = message.get("keywords", [])

# Search for new keywords
matched_keywords = tagger.find_keywords(message_text, keywords)

# Merge and deduplicate (case-insensitive)
combined = existing_keywords + matched_keywords
# ... dedupe ...
message["keywords"] = deduplicated
```

**Changes:**
1. **search_tag_messages.py:**
   - Removed skip logic for already-tagged messages
   - Added merge + deduplicate logic
   - Process ALL messages (stats["skipped"] always 0)
   - Preserve existing keywords on error

2. **search_tag_messages_cli.py:**
   - Updated messaging: "will be merged" instead of "will skip"
   - Removed "Note: X messages skipped" output
   - Show count of messages with existing keywords

3. **tests/test_search_tag_messages.py:**
   - Updated `test_tag_messages_basic`: expect 3 processed, 0 skipped
   - Renamed `test_skip_already_tagged` → `test_merge_existing_keywords`
   - Added `test_invalid_keywords_filtered_in_batch` (integration test)
   - Verify merge behavior: existing + new keywords combined

4. **Invalid Keyword Filtering:**
   - Added INVALID_KEYWORDS list to llm_config.py (starts with "cozy")
   - SearchTagger filters invalid keywords BEFORE storing in index
   - analyze_tag_statistics shows true data (no filtering)
   - If "cozy" appears in stats → index needs re-tagging

5. **Removed Backup Files:**
   - Eliminated `.backup.*` files during auto-saves
   - Not needed since we write to new files (non-destructive)

**Test Results:**
All 7 search_tag_messages tests passing ✓

**Example Workflow:**
```bash
# 1. Extract images (creates image-level keywords)
python extract_image_urls.py msgs_md/ data/

# 2. Tag messages (merges with existing, adds message-level keywords)
python search_tag_messages_cli.py data/index.idx data/index_tagged.idx

# Result: Both image keywords AND message keywords preserved
```

**Key Learning:**
Different workflow stages create keywords from different sources. Tools must **merge, not overwrite** to prevent data loss. The "skip already tagged" pattern only makes sense for slow, resumable operations (like LLM tagging), not fast deterministic operations (like search tagging).

**Field Name Standardization (2025-11-05):**
- Renamed `llm_keywords` → `keywords` across codebase (commit 84cd645)
- Both LLM and search taggers now use same `keywords` field
- Simpler and more accurate (not LLM-specific anymore)

### Search-Based Keyword Tagger Implementation (2025-11-05)
**Commits:** 3db2bb1

**Objective:** Create fast, deterministic alternative to LLM-based tagging using simple keyword search with stemming.

**Implementation (TDD):**

Built using Test-Driven Development with 18 new tests (all passing):

1. **search_tagger.py** - Core SearchTagger class (12 tests)
   - Simple stemmer with no dependencies
   - Handles: plurals, -ing, -ed, -er, -est, -ly, -tion, -ness, -ies, -ied, etc.
   - Case-insensitive matching with word boundaries
   - Hyphenated word support ("co-pilot" matches "pilot")
   - Returns deduped list of matched keywords

2. **search_tag_messages.py** - Batch processor (6 tests)
   - Loads index and keywords
   - Tags all messages using SearchTagger
   - Auto-saves every 50 messages
   - Skips already-tagged messages (idempotent)
   - Compatible with existing tools (uses llm_keywords field)

3. **search_tag_messages_cli.py** - CLI wrapper
   - Follows standardized SOURCE [DEST] pattern
   - Default DEST: {source}_tagged{ext}
   - Options: --keywords, --limit, --verbose

**Test Results:**
```bash
# Core tagger tests (12 tests)
✓ Exact match, case-insensitive, word boundaries
✓ Stemming: plurals, -ing forms, -ed forms
✓ Dedupe, multiple keywords, empty inputs
✓ Hyphenated words

# Batch processor tests (6 tests)
✓ Load index, load keywords, extract message text
✓ Tag messages basic, skip already tagged
✓ Empty keywords valid state
```

**End-to-End Test:**
```bash
$ python search_tag_messages_cli.py input/czindex.idx output.idx --limit 5 --verbose

Loaded 2539 messages
Loaded 552 keywords
Messages to process: 5

[1/5] Best IP sunshade size and construction for a 'glass' panel?
  Matched: ['glass', 'panel', 'panels']
[2/5] WING LEADING EDGE MOLDS
  Matched: ['leading', 'wing', 'wings']
[3/5] Rapco Vacuum Pump for sale $100 obo
  Matched: ['pump', 'pumps', 'vacuum']
[4/5] Canard-calendar - June
  Matched: ['canard', 'canards']
[5/5] Invitation to view Bulent.Enginegear's Gallery
  Matched: []

TAGGING STATISTICS
Messages processed:          5
Keywords per message:
  Average:                   2.2
  Min:                       0
  Max:                       3
```

**Performance:**
- **Speed:** Instant (vs 30s per message for LLM = 10 hours for 1200 messages)
- **Accuracy:** Stemming catches plurals and common variations
- **Reliability:** No timeouts, no LLM errors, deterministic results
- **Compatibility:** Uses same llm_keywords field as LLM tagger

**Stemming Examples:**
- "firewall" matches "firewalls", "Firewall", "FIREWALL"
- "install" matches "installing", "installed", "installer"
- "wing" matches "wings", "winging"
- "panel" matches "panels", "paneling"
- Word boundaries prevent "stall" from matching "installation"

**Trade-offs vs LLM Tagger:**
| Feature | Search Tagger | LLM Tagger |
|---------|---------------|------------|
| Speed | Instant | 30s/message |
| Reliability | 100% deterministic | Can timeout/error |
| Accuracy | 80-90% (exact + stemming) | 90-95% (semantic) |
| Synonyms | No (but can add to keywords.txt) | Yes |
| Context | No | Yes |
| Dependencies | Zero | Ollama + Model |

**Recommendation:**
Use search_tag_messages_cli.py as default. It's fast enough to run on entire dataset (seconds vs hours), reliable, and good enough for most use cases. Use llm_tag_messages_cli.py only when semantic matching is critical.

**All tests passing:** 128 tests (+18 new), 14 skipped

### File Cleanup and Keyword Finalization (2025-11-05)
**Commits:** 13779b7

**Moved test files to input/ directory:**
- czindex.idx, backupcz.idx
- 28 images_to_remove_page*.txt files
- Various test index files (cleaned.idx, test_cleaned*.idx, etc.)
- tests/test.idx

**Deleted obsolete files:**
- index251102143704.idx (old timestamped index - 216KB)
- tag_statistics.txt
- test_10_thumbnails.py

**Finalized aircraft_keywords.txt:**
- Simplified vendor/manufacturer names
- Removed redundant words ("Aircraft Spruce" → "Spruce", "Ken Brock Manufacturing" → "Brock", etc.)
- Now contains 557 curated keywords ready for tagging

**Added to .gitignore:**
- imageGetter/input/ (test data and work-in-progress files)

### Tagger Rename and Search Tagger Preparation (2025-11-05)
**Commits:** 0064389

**Objective:** Prepare for two parallel tagging approaches - LLM-based (semantic) and search-based (fast/simple).

**Rationale:**
LLM tagging is slow (30s per message × 1234 messages ≈ 10 hours) and can have errors/timeouts. Search-based tagging will be:
- **Fast:** Process entire dataset in seconds
- **Reliable:** No LLM timeouts or errors
- **Deterministic:** Same input always gives same output
- **Good enough:** 557 curated keywords + stemming should catch 80-90% of relevant terms

**Files Renamed:**
- `tag_messages.py` → `llm_tag_messages.py`
- `tag_messages_cli.py` → `llm_tag_messages_cli.py`
- `tests/test_tag_messages.py` → `tests/test_llm_tag_messages.py`

**Parallel Structure:**

LLM-based tagging (semantic matching):
- `llm_tagger.py` - Core LLM KeywordTagger class
- `llm_tag_messages.py` - Batch processor using LLM
- `llm_tag_messages_cli.py` - CLI: `python llm_tag_messages_cli.py SOURCE [DEST]`
- `tests/test_llm_tag_messages.py` - 17 tests passing

Search-based tagging (keyword matching with stemming) - TO BE BUILT:
- `search_tagger.py` - Core SearchTagger class with stemming
- `search_tag_messages.py` - Batch processor using search
- `search_tag_messages_cli.py` - CLI: `python search_tag_messages_cli.py SOURCE [DEST]`
- `tests/test_search_tag_messages.py` - Tests (TDD)

**Search Tagger Design:**
1. Case-insensitive search with word boundaries
2. Stemming (e.g., "cowl" matches "cowling", "cowls", "cowled")
3. Search both subject + body of message
4. Dedupe keywords (no duplicates in output)
5. Store results in same `llm_keywords` field (compatible with existing tools)

**Tradeoffs:**
- **Lose:** Synonym matching, context understanding, related terms
- **Gain:** Speed (seconds vs hours), reliability, simplicity, maintainability
- **Mitigation:** Can always add synonyms to aircraft_keywords.txt, or use LLM for subset

**All tests passing** after rename (110 passing, 14 skipped).
**README.md updated** to reference llm_tag_messages_cli.py.

### CLI Standardization (2025-11-05)
**Commits:** bd5e142 (CLI changes), f20f9dc (README update)

**Objective:** Standardize all CLI tools to consistent interface pattern for better usability and predictability.

**Design Pattern Established:**
```
python program_name SOURCE [DEST] [options]
```

**Design Principles:**
1. **Non-destructive by default** - Never overwrite SOURCE, always write to new DEST file
2. **Smart defaults** - If DEST omitted, generate from SOURCE with descriptive suffix
3. **Consistent positional args** - SOURCE always first, DEST always second (optional)
4. **Idempotent operations** - Tools can be run multiple times safely (skip already-processed items)
5. **Preserved extensions** - DEST inherits SOURCE extension (.idx, .json, etc.)

**Changes Made:**

1. **tag_messages_cli.py** - Tag messages with LLM keywords
   - **Old:** `python tag_messages_cli.py INDEX_FILE --overwrite`
   - **New:** `python tag_messages_cli.py SOURCE [DEST]`
   - **Breaking:** Removed `--overwrite` flag
   - **Behavior:** Always skips already-tagged messages (idempotent by default)
   - **Default DEST:** `{source_stem}_tagged{source_ext}` (e.g., `test.idx` → `test_tagged.idx`)
   - **Core change:** Updated `tag_messages()` to accept `output_file` parameter instead of in-place modification
   - **Tests updated:** Removed `overwrite=True/False` from all test calls

2. **build_keywords_cli.py** - Extract keywords from messages using LLM
   - **Old:** `python build_keywords_cli.py INDEX_FILE --output keywords.txt`
   - **New:** `python build_keywords_cli.py SOURCE [DEST]`
   - **Breaking:** Moved `--output` to positional DEST
   - **Default DEST:** `{source_stem}_keywords.txt` (e.g., `test.idx` → `test_keywords.txt`)
   - **Suffix rationale:** Always `.txt` because output is plain text keyword list, not index format

3. **analyze_tag_statistics.py** - Generate statistics and HTML views
   - **Old:** `python analyze_tag_statistics.py index_file --output stats.txt`
   - **New:** `python analyze_tag_statistics.py SOURCE [DEST]`
   - **Breaking:** Moved `--output` to positional DEST
   - **Default DEST:** `{source_stem}_statistics.txt`
   - **HTML output:** Automatically generates `{dest_stem}_view_page*.html` files
   - **Example:** `test.idx` → `test_statistics.txt` + `test_statistics_view_page1.html`

**Tools Already Following Pattern:**
- `download_images_cli.py` - SOURCE=index, DEST=image directory ✓
- `extract_image_urls.py` - SOURCE=markdown dir, DEST=output dir ✓
- `dedupe_images_cli.py` - SOURCE=index, DEST=deduped index ✓
- `remove_images_cli.py` - SOURCE=index, DEST=cleaned index ✓
- `generate_thumbnails_cli.py` - SOURCE=full images dir, DEST=thumbs dir ✓
  - **Note:** Kept `--force` flag as requested (regenerate existing thumbnails)

**Suffix Naming Convention:**
- `_tagged` - After LLM keyword tagging
- `_deduped` - After deduplication
- `_cleaned` - After removal of unwanted images
- `_keywords.txt` - Extracted keyword list
- `_statistics.txt` - Statistics report
- `_statistics_view` - HTML view base name

**Migration Guide for Users:**

Old workflow:
```bash
python tag_messages_cli.py test.idx --overwrite
python build_keywords_cli.py test.idx --output keywords.txt
python analyze_tag_statistics.py test.idx --output stats.txt
```

New workflow:
```bash
python tag_messages_cli.py test.idx test_tagged.idx
python build_keywords_cli.py test.idx keywords.txt
python analyze_tag_statistics.py test.idx stats.txt
```

Or with smart defaults (recommended):
```bash
python tag_messages_cli.py test.idx                    # → test_tagged.idx
python build_keywords_cli.py test.idx                  # → test_keywords.txt
python analyze_tag_statistics.py test.idx              # → test_statistics.txt
```

**Complete Updated Workflow:**
```bash
# Extract URLs
python extract_image_urls.py ../data/msgs_md/A ../data

# Download images
python download_images_cli.py ../data/index*.idx ../data/images/full

# Generate thumbnails
python generate_thumbnails_cli.py ../data/images/full ../data/images/thumbs

# Deduplicate
python dedupe_images_cli.py data/index.idx data/index_deduped.idx

# Tag with LLM keywords
python tag_messages_cli.py data/index_deduped.idx data/index_tagged.idx

# Generate HTML review
python analyze_tag_statistics.py data/index_tagged.idx

# (Manual review in browser, export removal lists)

# Remove unwanted images
python remove_images_cli.py data/index_tagged.idx data/index_cleaned.idx --remove-list *.txt
```

**Documentation Updated:**
- `imageGetter/README.md` - Complete workflow with all phases
- All CLI examples updated to new pattern
- Added Phase 5 (LLM tagging) to workflow documentation

**Testing:**
- All 110 tests passing, 14 skipped
- No regressions introduced
- Test suite updated to match new API (removed `overwrite` parameter)

**Benefits:**
1. **Predictable** - All tools work the same way
2. **Safe** - No accidental overwrites of source data
3. **Chainable** - Easy to see data flow: `input.idx` → `_deduped` → `_tagged` → `_cleaned`
4. **Discoverable** - `--help` shows consistent pattern
5. **Scriptable** - Easier to write shell scripts with consistent interface

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
