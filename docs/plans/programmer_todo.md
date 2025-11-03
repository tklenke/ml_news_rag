# Programmer Todo - Image Database Project

**Project:** Image Database for Cozy Builders Newsgroup
**Last Updated:** 2025-11-02

## Current Status

**Phase 1: COMPLETE** ✓
- URL extraction working (217 images from 92 messages in A/ directory)
- Blacklist filtering operational (~400+ junk images removed)
- Keyword extraction from filenames and subjects
- Index file: data/image_index.json (76KB)

**Phase 2: COMPLETE** ✓
- Dual-path download strategy implemented and validated
- Resume capability working
- Cookie management functional
- All unit tests passing (6 passed, 4 skipped)
- Production downloads validated: 188 images, 70MB, index251102.idx with 2,539 messages

**Phase 3: COMPLETE** ✓
- Thumbnail generation implemented (TDD, 6 tests passing)
- CLI tool created with progress bar and options
- 188 thumbnails generated (200x200, 2.2MB, 100% success)

**Next Task:** Phase 4 - LLM Keyword Tagging

---

## Phase 3: Thumbnail Generation

**Goal:** Create 200x200px center-cropped thumbnails

**Status:** COMPLETE ✓

### Completed Tasks
- [x] Create `generate_thumbnails.py` module (TDD)
  - [x] `generate_thumbnail()` function with PIL
  - [x] Center crop to square, resize to 200x200
  - [x] Save as JPEG quality=85
  - [x] All 6 unit tests passing
- [x] Create `generate_thumbnails_cli.py`
  - [x] Progress bar with tqdm
  - [x] --limit flag for testing
  - [x] Skip existing by default, --force to regenerate
  - [x] --size for custom dimensions
- [x] Generate all 188 thumbnails (100% success rate, 2.2MB total)
- [x] Document results in `docs/notes/phase3_results.md`

**Results:**
- 188 thumbnails generated (200x200, 2.2MB total)
- Processing speed: ~39 images/second
- File sizes: 3.4KB - 15KB (typical 6-12KB)
- 100% success rate

**Deliverable:** images/thumbs/ populated with 200x200 thumbnails

---

## Phase 4: LLM Keyword Tagging

**Goal:** Use local LLM to tag messages with curated keywords

**REVISED 2025-11-03:** Store keywords IN image_index.json as `llm_keywords` field

**Scope:**
- Tag only messages with images (~7k messages in image_index.json)
- Use keywords_seed.txt (110 keywords) as starting point
- Store results in image_index.json (not separate file)

### Phase 4.1: Keyword Discovery Tool (Optional - Tom may skip)

**Goal:** CLI tool to sample messages and extract candidate keywords

**Tasks:**
1. [ ] Write failing test: `test_sample_random_messages_from_index()`
2. [ ] Write failing test: `test_extract_message_text_for_llm()`
3. [ ] Implement `build_keyword_list.py` module (TDD)
   - Read image_index.json
   - Sample N random messages (--sample flag)
   - Format message text for LLM
   - Query LLM: "Extract aircraft-building keywords from these messages"
   - Output candidate keywords to file
4. [ ] Create CLI: `python build_keyword_list.py --sample 5 --output candidates.txt`
5. [ ] Test with 5 messages from A/ directory
6. [ ] Document usage in imageGetter/README.md

**Deliverable:** Tool to help Tom expand keyword list (may not be used if seed list sufficient)

---

### Phase 4.2: LLM Keyword Tagger Core (TDD)

**Goal:** Function to tag a single message with keywords using LLM

**Tasks:**
1. [ ] Write failing test: `test_tag_message_exact_match()`
   - Message contains "firewall", keywords list includes "firewall"
   - Expected: returns ["firewall"]
2. [ ] Write failing test: `test_tag_message_synonym_match()`
   - Message contains "cowl", keywords list includes "cowling"
   - Expected: returns ["cowling"] (LLM understands synonym)
3. [ ] Write failing test: `test_tag_message_context_match()`
   - Message contains "Rotax installation", keywords list includes "engine"
   - Expected: returns ["engine"] (semantic understanding)
4. [ ] Write failing test: `test_tag_message_no_match()`
   - Message about "weather delays", keywords about aircraft parts
   - Expected: returns []
5. [ ] Write failing test: `test_tag_message_multiple_keywords()`
   - Message about firewall and cowling
   - Expected: returns ["firewall", "cowling"]
6. [ ] Run tests - verify all fail
7. [ ] Implement `tag_message_with_llm(message_text: str, keywords: list[str]) -> list[str]`
   - Format prompt for LLM
   - Call Ollama API with local model
   - Parse LLM response to keyword list
   - Handle errors gracefully
8. [ ] Run tests - verify all pass
9. [ ] Refactor if needed
10. [ ] Commit: "Implement LLM keyword tagger core (Phase 4.2)"

**Deliverable:** Core tagging function with 5+ passing tests

---

### Phase 4.3: Batch Message Tagger (TDD)

**Goal:** Process image_index.json and add llm_keywords to each message

**Tasks:**
1. [ ] Write failing test: `test_load_image_index()`
2. [ ] Write failing test: `test_skip_already_tagged_messages()`
   - Message has `llm_keywords: ["firewall"]` → skip
   - Message missing llm_keywords → process
3. [ ] Write failing test: `test_overwrite_existing_keywords()`
   - With --overwrite flag, retag message even if llm_keywords exists
4. [ ] Write failing test: `test_tag_empty_list_valid_state()`
   - Message tagged but no keywords match → `llm_keywords: []` is valid
5. [ ] Write failing test: `test_limit_processing()`
   - With --limit 10, process exactly 10 messages (not counting skipped)
6. [ ] Run tests - verify all fail
7. [ ] Implement `tag_messages.py` module
   - Load image_index.json
   - Load keywords from keywords_seed.txt
   - For each message:
     - Skip if llm_keywords exists (unless --overwrite)
     - Extract message text (subject + any other text fields)
     - Call tag_message_with_llm()
     - Add llm_keywords field to message
   - Write back to image_index.json
8. [ ] Run tests - verify all pass
9. [ ] Commit: "Implement batch message tagger (Phase 4.3)"

**Deliverable:** Core processing logic with tests

---

### Phase 4.4: CLI Interface

**Goal:** Command line tool for tagging messages

**Tasks:**
1. [ ] Create `tag_messages_cli.py`
2. [ ] Add argument parsing:
   - Positional: `INDEX_FILE` (path to image_index.json)
   - `--limit N` - process first N messages
   - `--overwrite` - retag existing llm_keywords
   - `--keywords FILE` - use custom keyword file (default: keywords_seed.txt)
3. [ ] Add progress bar (tqdm)
4. [ ] Add statistics:
   - Messages processed
   - Messages skipped (already tagged)
   - Keywords found per message (avg/min/max)
   - Processing time
5. [ ] Test with --limit 5 on image_index.json
6. [ ] Test with --overwrite flag
7. [ ] Document usage in imageGetter/README.md
8. [ ] Commit: "Add CLI for message tagging (Phase 4.4)"

**Command Line Examples:**
```bash
# Tag first 50 messages
python tag_messages_cli.py ../data/image_index.json --limit 50

# Tag all untagged messages (resume capability)
python tag_messages_cli.py ../data/image_index.json

# Retag everything
python tag_messages_cli.py ../data/image_index.json --overwrite

# Use custom keywords
python tag_messages_cli.py ../data/image_index.json --keywords custom_keywords.txt
```

**Deliverable:** Working CLI tool

---

### Phase 4.5: Validate and Document

**Goal:** Run on real data and validate quality

**Tasks:**
1. [ ] Run on first 10 messages: `--limit 10`
2. [ ] Manually review llm_keywords accuracy (>80% target)
3. [ ] If quality poor, iterate on LLM prompt
4. [ ] Run on all A/ directory messages (~92 messages with images)
5. [ ] Review statistics and sample results
6. [ ] Create `docs/notes/phase4_results.md`:
   - Messages processed
   - Keywords per message (distribution)
   - Sample results (show 5-10 messages with keywords)
   - Accuracy assessment
   - Any issues found
7. [ ] Commit results documentation
8. [ ] Mark Phase 4 complete in this file

**Deliverable:** image_index.json with llm_keywords populated, results documented

---

### Important Notes for Phase 4

**LLM Setup:**
- Use Ollama with local model (already installed)
- Model selection: TBD (discuss with Tom - gemma2:2b? llama?)
- API endpoint: http://localhost:11434

**Keywords File:**
- Located: `docs/input/keywords_seed.txt`
- 110 keywords currently
- Tom may expand during Phase 4.1 or use as-is

**Error Handling:**
- If Ollama not running → clear error message
- If LLM fails on a message → log error, continue processing
- If JSON corrupted → backup before writing

**Processing Strategy:**
- Process in batches to show progress
- Auto-save every 50 messages (in case of crash)
- Resume capability built-in (skip already-tagged)

**Deliverable:** image_index.json with llm_keywords field populated for all messages

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

**Last Updated:** 2025-11-03 by Claude (Architect)
