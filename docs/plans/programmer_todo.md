# Programmer Todo - Image Database Project

**Project:** Image Database for Cozy Builders Newsgroup
**Last Updated:** 2025-11-02

## Current Status

**Phase 1: COMPLETE** ✓
- URL extraction working (217 images from 92 messages in A/ directory)
- Blacklist filtering operational (~400+ junk images removed)
- Keyword extraction from filenames and subjects
- Index file: data/image_index.json (76KB)

**Phase 2: Implementation COMPLETE** ✓
- Dual-path download strategy implemented (requests+cookies / Selenium)
- Resume capability working
- Cookie management functional
- All unit tests passing (6 passed, 4 skipped)

**Next Task:** Phase 2.9 - Production Download Testing

---

## Phase 2: Production Testing

### Phase 2.9: Download A/ Directory Images (CURRENT TASK)
**Goal:** Validate downloads work in production with real Chrome session

**Prerequisites:**
1. Start Chrome with debug mode: `chrome.exe --remote-debugging-port=9222`
2. Log into Google Groups in Chrome

**Tasks:**
- [ ] Test with --limit 5 first
- [ ] Verify 5 images download successfully
- [ ] Run full A/ directory download (217 images)
- [ ] Monitor for errors and success rate
- [ ] Document results in `docs/notes/phase2_results.md`:
  - Success rate
  - Common failures (if any)
  - Total disk space
- [ ] Commit: "Complete Phase 2: Production downloads validated"

**When Phase 2.9 Complete:**
- [ ] Mark Phase 2 fully complete
- [ ] Move to Phase 3

---

## Phase 3: Thumbnail Generation

**Goal:** Create 200x200px center-cropped thumbnails

### High-Level Tasks
1. Create `generate_thumbnails.py` module (TDD)
   - `generate_thumbnail()` function with PIL
   - Center crop to square, resize to 200x200
   - Save as JPEG quality=85
2. Create `generate_thumbnails_cli.py`
3. Run on A/ directory downloads
4. Document results in `docs/notes/phase3_results.md`

**Deliverable:** images/thumbs/ populated with 200x200 thumbnails

---

## Phase 4: LLM Keyword Tagging

**Goal:** Use local LLM to tag messages with curated keywords

**REVISED 2025-11-02:** LLM provides semantic understanding at index-time, not query-time.

### High-Level Tasks
1. Build master keyword list (50-200 terms)
   - Sample 100-message batches from corpus
   - Ask local LLM to extract aircraft-building keywords
   - Tom reviews and prunes list
   - Iterate until stable
2. Create LLM keyword tagger (TDD)
   - Prompt: "Which of these keywords appear in this message?"
   - LLM handles synonyms (e.g., "cowl" = "cowling")
3. Tag all A/ directory messages (~325 messages, 10-15 min)
4. Create message_keywords.json: `{messageID: [keywords]}`
5. Validate tagging quality (>80% accuracy on manual review)
6. Document in `docs/notes/phase4_results.md`

**Deliverable:** message_keywords.json with LLM-tagged keywords per message

---

## Phase 5: Keyword-Based Query Interface

**Goal:** Simple query interface using Phase 4 keywords

**NOTE:** No ChromaDB integration - just keyword lookup

### High-Level Tasks
1. Create query function (TDD)
   - Input: keyword(s)
   - Output: messages+images matching those keywords
2. Create CLI query tool
3. Create HTML thumbnail viewer
4. Test queries: "firewall", "cowling", "panel", "landing gear"
5. Validate query quality
6. Document in `docs/notes/phase5_results.md`

**Deliverable:** Working keyword-based image search

---

## Important Implementation Notes

### Dual-Path Download Strategy
- URLs **without** &view=1: Direct download via requests + cookies
- URLs **with** &view=1: Selenium parses HTML wrapper to extract image URL
- Cookie extraction happens once at batch start

### Index Format
```json
{
  "A1NtxlDfY4c": {
    "metadata": {...},
    "images": [
      {
        "url": "...",
        "filename": "...",
        "local_filename": "A1NtxlDfY4c_part0_1_image.jpg",
        "keywords": ["landing", "light"]
      }
    ]
  }
}
```

### Key Files
- `imageGetter/extract_image_urls.py` - Phase 1
- `imageGetter/download_images.py` - Phase 2 core
- `imageGetter/download_images_cli.py` - Phase 2 CLI
- `imageGetter/generate_thumbnails.py` - Phase 3 (not created yet)
- `data/image_index.json` - Master index

---

## Before Every Commit
- [ ] Run tests: `pytest`
- [ ] Update this file with progress
- [ ] Include updated programmer_todo.md in commit

## When to Escalate to Architect
- Download success rate < 50%
- Query interface design unclear
- ChromaDB metadata approach not working
- Major technical blockers

Use "Strange things are afoot at the Circle K" for urgent issues.

---

**Last Updated:** 2025-11-02 by Claude (Architect)
