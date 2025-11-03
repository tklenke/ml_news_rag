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

**Phase 4a: PENDING**
- Details TBD (Tom to specify)

**Phase 4b: PENDING**
- 6 sub-phases: 4b.1 (optional keyword discovery), 4b.2 (config file), 4b.3 (LLM tagger core), 4b.4 (batch processor), 4b.5 (CLI), 4b.6 (validation)
- Next: Start with Phase 4b.2 (create llm_config.py)

**Next Task:** Phase 4a - TBD

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

## Phase 4a: TBD

**Goal:** TBD (Tom to specify)

---

## Phase 4b: LLM Keyword Tagging

**Goal:** Use local LLM to tag messages with curated keywords

**REVISED 2025-11-03:** Store keywords IN image_index.json as `llm_keywords` field

**Scope:**
- Tag only messages with images (~7k messages in image_index.json)
- Use keywords_seed.txt (110 keywords) as starting point
- Store results in image_index.json (not separate file)

### Phase 4b.1: Keyword Discovery Tool (Optional - Tom may skip)

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

### Phase 4b.2: LLM Configuration File

**Goal:** Create config file for LLM parameters and prompt

**Tasks:**
1. [ ] Create `imageGetter/llm_config.py` with ABOUTME comments
2. [ ] Add configuration constants:
   ```python
   # LLM Configuration
   OLLAMA_HOST = "http://localhost:11434"
   LLM_MODEL = "gemma3:1b"  # Tom will edit this as needed

   # Prompt template for keyword tagging
   KEYWORD_TAGGING_PROMPT = """You are analyzing aircraft builder messages. Given this list of keywords, return ONLY the keywords that are relevant to the message below.

Keywords: {keywords}

Message: {message}

Return the matching keywords as a comma-separated list. If no keywords match, return "NONE". Do not include explanations or extra text."""
   ```
3. [ ] Document that Tom can edit model and prompt in this file
4. [ ] Commit: "Add LLM configuration file (Phase 4b.2)"

**Deliverable:** llm_config.py with editable prompt and model

---

### Phase 4b.3: LLM Keyword Tagger Core (TDD)

**Goal:** Class-based tagger using Ollama (following embedder/f_llm.py pattern)

**Reference:** See `embedder/f_llm.py` for existing LLM interaction pattern

**Tasks:**
1. [ ] Create `imageGetter/llm_tagger.py` with ABOUTME comments
2. [ ] Add ollama to imageGetter/requirements.txt if not present
3. [ ] Write failing test: `test_tag_message_exact_match()`
   - Message contains "firewall", keywords list includes "firewall"
   - Expected: returns ["firewall"]
4. [ ] Write failing test: `test_tag_message_synonym_match()`
   - Message contains "cowl", keywords list includes "cowling"
   - Expected: returns ["cowling"] (LLM understands synonym)
5. [ ] Write failing test: `test_tag_message_context_match()`
   - Message contains "Rotax installation", keywords list includes "engine"
   - Expected: returns ["engine"] (semantic understanding)
6. [ ] Write failing test: `test_tag_message_no_match()`
   - Message about "weather delays", keywords about aircraft parts
   - Expected: returns []
7. [ ] Write failing test: `test_tag_message_multiple_keywords()`
   - Message about firewall and cowling
   - Expected: returns ["firewall", "cowling"]
8. [ ] Write failing test: `test_llm_error_handling()`
   - Ollama unavailable or LLM error
   - Expected: returns [], logs error, doesn't crash
9. [ ] Run tests - verify all fail
10. [ ] Implement `KeywordTagger` class:
    ```python
    class KeywordTagger:
        def __init__(self, ollamahost=None):
            # Use llm_config.OLLAMA_HOST if ollamahost not specified
            self.ollamaclient = ollama.Client(ollamahost or OLLAMA_HOST)

        def tag_message(self, message_text: str, keywords: list[str], model=None) -> list[str]:
            # Use llm_config.LLM_MODEL if model not specified
            # Format prompt using llm_config.KEYWORD_TAGGING_PROMPT
            # Call self.ollamaclient.generate()
            # Parse response (comma-separated list or "NONE")
            # Validate matches against master keyword list
            # Return list of valid keywords
            # On error: log error, return []
    ```
11. [ ] Run tests - verify all pass
12. [ ] Refactor if needed
13. [ ] Commit: "Implement LLM keyword tagger core (Phase 4b.3)"

**Implementation Notes:**
- Follow pattern from `embedder/f_llm.py` (class-based, ollama.Client)
- Import config from llm_config.py
- Graceful error handling: log and continue (don't crash)
- Validate LLM responses against master keyword list (prevent hallucination)
- Handle various response formats: "keyword1, keyword2" or "NONE" or empty

**Deliverable:** KeywordTagger class with 6+ passing tests

---

### Phase 4b.4: Batch Message Tagger (TDD)

**Goal:** Process image_index.json and add llm_keywords to each message

**Tasks:**
1. [ ] Create `imageGetter/tag_messages.py` with ABOUTME comments
2. [ ] Write failing test: `test_load_image_index()`
3. [ ] Write failing test: `test_skip_already_tagged_messages()`
   - Message has `llm_keywords: ["firewall"]` → skip
   - Message missing llm_keywords → process
4. [ ] Write failing test: `test_overwrite_existing_keywords()`
   - With --overwrite flag, retag message even if llm_keywords exists
5. [ ] Write failing test: `test_tag_empty_list_valid_state()`
   - Message tagged but no keywords match → `llm_keywords: []` is valid
6. [ ] Write failing test: `test_limit_processing()`
   - With --limit 10, process exactly 10 messages (not counting skipped)
7. [ ] Run tests - verify all fail
8. [ ] Implement `tag_messages.py` module:
   - Load image_index.json
   - Load keywords from keywords_seed.txt (or custom file)
   - Create KeywordTagger instance
   - For each message in image_index.json:
     - Skip if llm_keywords exists and not empty (unless --overwrite)
     - Extract message text (subject + any other text fields)
     - Call tagger.tag_message(message_text, keywords)
     - Add llm_keywords field to message
     - Handle LLM errors gracefully (log and continue)
   - Write back to image_index.json
   - Auto-save every 50 messages (crash recovery)
9. [ ] Run tests - verify all pass
10. [ ] Commit: "Implement batch message tagger (Phase 4b.4)"

**Deliverable:** Core processing logic with tests

---

### Phase 4b.5: CLI Interface

**Goal:** Command line tool for tagging messages

**Tasks:**
1. [ ] Create `imageGetter/tag_messages_cli.py` with ABOUTME comments
2. [ ] Add argument parsing:
   - Positional: `INDEX_FILE` (path to image_index.json)
   - `--limit N` - process first N messages
   - `--overwrite` - retag existing llm_keywords
   - `--keywords FILE` - use custom keyword file (default: ../docs/input/keywords_seed.txt)
   - `--model MODEL` - override LLM model from llm_config.py
3. [ ] Add progress bar (tqdm)
4. [ ] Add statistics:
   - Messages processed
   - Messages skipped (already tagged)
   - Keywords found per message (avg/min/max)
   - LLM errors encountered
   - Processing time
5. [ ] Test with --limit 5 on image_index.json
6. [ ] Test with --overwrite flag
7. [ ] Document usage in imageGetter/README.md
8. [ ] Commit: "Add CLI for message tagging (Phase 4b.5)"

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

# Override model from config
python tag_messages_cli.py ../data/image_index.json --model gemma2:2b
```

**Deliverable:** Working CLI tool

---

### Phase 4b.6: Validate and Document

**Goal:** Run on real data and validate quality

**Tasks:**
1. [ ] Run on first 10 messages: `--limit 10`
2. [ ] Manually review llm_keywords accuracy (>80% target)
3. [ ] If quality poor, iterate on LLM prompt
4. [ ] Run on all A/ directory messages (~92 messages with images)
5. [ ] Review statistics and sample results
6. [ ] Create `docs/notes/phase4b_results.md`:
   - Messages processed
   - Keywords per message (distribution)
   - Sample results (show 5-10 messages with keywords)
   - Accuracy assessment
   - Any issues found
7. [ ] Commit results documentation
8. [ ] Mark Phase 4b complete in this file

**Deliverable:** image_index.json with llm_keywords populated, results documented

---

### Important Notes for Phase 4b

**LLM Setup:**
- Use Ollama with local model (already installed via docker-compose)
- Model configured in `imageGetter/llm_config.py` (default: gemma3:1b)
- Prompt template also in llm_config.py (Tom can edit both)
- API endpoint: http://localhost:11434 (configured in llm_config.py)
- Follow pattern from `embedder/f_llm.py` (class-based KeywordTagger)

**Keywords File:**
- Located: `docs/input/keywords_seed.txt`
- 110 keywords currently
- Tom may expand during Phase 4.1 or use as-is

**Error Handling:**
- If Ollama not running → clear error message
- If LLM fails on a message → log error, continue processing (don't crash)
- If JSON corrupted → backup before writing
- LLM errors return [] and log, processing continues

**Processing Strategy:**
- Process in batches to show progress
- Auto-save every 50 messages (in case of crash)
- Resume capability built-in (skip already-tagged)
- Validate LLM responses against master keyword list (prevent hallucination)

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
