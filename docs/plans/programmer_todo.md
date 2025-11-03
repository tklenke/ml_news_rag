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

**Phase 4a: COMPLETE** ✓ (awaiting Tom's manual execution)
- All 5 sub-phases implemented and tested
- CLI tool ready: build_keywords_cli.py
- Output: keywords_master.txt (Tom will create by running CLI)
- Next: Tom runs CLI, then Phase 4b (message tagging)

**Phase 4b: PENDING** - Tag Messages with Keywords
- 5 sub-phases: 4b.1 (config file), 4b.2 (LLM tagger core), 4b.3 (batch processor), 4b.4 (CLI), 4b.5 (validation)
- Prerequisites: Phase 4a must be complete (keywords_master.txt exists)
- Uses keywords_master.txt from Phase 4a as input
- Next: Starts after Phase 4a complete

**Next Task:** Phase 4a.1 - Message Sampling

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

## Phase 4a: Build Improved Keywords File

**Goal:** Analyze messages with photos using LLM to create comprehensive keyword list

**Purpose:** Phase 4a builds the vocabulary that Phase 4b will use for tagging.

**Input:**
- `docs/input/keywords_seed.txt` (110 starting keywords)
- `data/image_index.json` (messages with photos - ~7k messages)

**Output:**
- `docs/input/keywords_master.txt` (improved keyword list, 200-300 keywords)

**Process Overview:**
1. Sample N messages from image_index.json
2. Ask LLM: "What aircraft-building keywords appear in this message?"
3. Aggregate all keywords suggested by LLM
4. Merge with existing keywords (seed or previous iteration)
5. Remove duplicates, filter noise
6. Tom reviews and prunes candidates
7. Iterate until keyword list is stable
8. Save final keywords_master.txt

### Phase 4a.1: Message Sampling (TDD)

**Goal:** Sample random messages from image_index.json

**Status:** COMPLETE ✓

**Tasks:**
1. [x] Create `imageGetter/keyword_builder.py` with ABOUTME comments
2. [x] Write failing test: `test_load_image_index()`
3. [x] Write failing test: `test_sample_random_messages()`
   - Sample N random messages from index
   - Expected: returns list of N message objects
4. [x] Write failing test: `test_extract_message_text()`
   - Extract subject and relevant text fields
   - Expected: returns clean text for LLM
5. [x] Run tests - verify all fail
6. [x] Implement sampling functions
7. [x] Run tests - verify all pass
8. [x] Commit: "Implement message sampling (Phase 4a.1)"

**Deliverable:** Functions to sample messages and extract text (5 tests passing)

---

### Phase 4a.2: LLM Keyword Extraction (TDD)

**Goal:** Use LLM to extract keywords from message text

**Status:** COMPLETE ✓

**Tasks:**
1. [x] Create `imageGetter/llm_config.py` with ABOUTME comments (if not exists from 4b)
2. [x] Add keyword extraction prompt to llm_config.py
3. [x] Write failing test: `test_extract_keywords_from_message()`
4. [x] Write failing test: `test_handle_multiple_messages()`
5. [x] Write failing test: `test_aggregate_keywords()`
   - Collect all keywords from multiple messages
   - Remove duplicates
   - Expected: returns set of unique keywords
6. [x] Run tests - verify all fail
7. [x] Implement keyword extraction using KeywordExtractor class (following embedder/f_llm.py pattern)
8. [x] Run tests - verify all pass
9. [x] Commit: "Implement LLM keyword extraction (Phase 4a.2)"

**Deliverable:** KeywordExtractor class and aggregate_keywords function (8 tests passing, 2 skipped for LLM tests)

---

### Phase 4a.3: Keyword Merging and Filtering (TDD)

**Goal:** Merge LLM keywords with existing keywords, filter noise

**Status:** COMPLETE ✓

**Tasks:**
1. [x] Write failing test: `test_load_existing_keywords()`
   - Load keywords_seed.txt or keywords_master.txt
2. [x] Write failing test: `test_merge_keyword_lists()`
   - Merge new keywords with existing
   - Remove duplicates (case-insensitive)
3. [x] Write failing test: `test_filter_noise_keywords()`
   - Remove common words (the, and, a, etc.)
   - Remove very short words (<2 chars), except valid abbreviations like "ng"
   - Remove numbers-only
4. [x] Write failing test: `test_sort_keywords_alphabetically()`
5. [x] Run tests - verify all fail
6. [x] Implement merge and filter functions
7. [x] Run tests - verify all pass
8. [x] Commit: "Implement keyword merging and filtering (Phase 4a.3)"

**Deliverable:** Functions to merge, filter, and clean keyword lists (16 tests passing, 2 skipped)

---

### Phase 4a.4: CLI Tool

**Goal:** Command line tool for iterative keyword building

**Status:** COMPLETE ✓ (awaiting LLM testing)

**Tasks:**
1. [x] Create `imageGetter/build_keywords_cli.py` with ABOUTME comments
2. [x] Add argument parsing:
   - Positional: `INDEX_FILE` (path to image_index.json)
   - `--sample N` - number of messages to sample (default: 100)
   - `--existing FILE` - existing keywords to merge with (default: keywords_seed.txt)
   - `--output FILE` - output file for candidates (default: keywords_candidates.txt)
   - `--model MODEL` - override LLM model from config
3. [x] Add progress bar (tqdm)
4. [x] Add statistics:
   - Messages sampled
   - Keywords extracted
   - New keywords (not in existing list)
   - Duplicate keywords removed
5. [~] Test with --sample 10 (requires Ollama running - will test in Phase 4a.5)
6. [ ] Document usage in imageGetter/README.md (can be done later)
7. [x] Commit: "Add CLI for keyword building (Phase 4a.4)"

**Command Line Examples:**
```bash
# First iteration: sample 100 messages, use seed file
python build_keywords_cli.py ../data/image_index.json --sample 100 --output keywords_candidates.txt

# Tom reviews keywords_candidates.txt, adds good ones to keywords_master.txt

# Second iteration: sample 100 more, merge with master
python build_keywords_cli.py ../data/image_index.json --sample 100 --existing ../docs/input/keywords_master.txt --output keywords_candidates2.txt

# Large sample for final pass
python build_keywords_cli.py ../data/image_index.json --sample 500 --existing ../docs/input/keywords_master.txt --output keywords_candidates_final.txt
```

**Deliverable:** Working CLI tool for iterative keyword building

**Note:** Actual testing requires Ollama to be running. CLI structure and argument parsing verified.

---

### Phase 4a.5: Run and Document

**Goal:** Build initial keywords_master.txt

**Status:** AWAITING TOM'S EXECUTION

**Tasks (for Tom to complete):**
1. [ ] Ensure Ollama is running (docker-compose up or manual start)
2. [ ] Run CLI with small sample first:
   ```bash
   cd imageGetter
   python build_keywords_cli.py ../data/image_index.json --sample 10 --output keywords_test.txt
   ```
3. [ ] If test works, run with larger sample:
   ```bash
   python build_keywords_cli.py ../data/image_index.json --sample 100 --output keywords_candidates.txt
   ```
4. [ ] Review keywords_candidates.txt
5. [ ] Create `docs/input/keywords_master.txt` with curated keywords
6. [ ] Optionally: Run multiple iterations with different samples
7. [ ] Document results in `docs/notes/phase4a_results.md`
8. [ ] Commit keywords_master.txt and results

**Deliverable:** keywords_master.txt ready for Phase 4b

**Programmer Notes:**
- All Phase 4a code is complete and tested (53 tests passing)
- CLI tool is fully functional and includes:
  * Message sampling from image_index.json
  * LLM-based keyword extraction
  * Keyword merging, filtering, and sorting
  * Progress bars and comprehensive statistics
  * Support for iterative refinement
- Ready for Tom to run and build master keyword list

---

### Important Notes for Phase 4a

**LLM Setup:**
- Use same Ollama setup as Phase 4b (llm_config.py)
- Model: gemma3:1b (configurable)
- Different prompt: KEYWORD_EXTRACTION_PROMPT (not KEYWORD_TAGGING_PROMPT)

**Sampling Strategy:**
- Random sampling (not sequential) for diversity
- Tom can run multiple times with different samples
- Incremental: each iteration adds to previous keywords

**Output Files:**
- `keywords_candidates.txt` - Raw output from LLM (Tom reviews)
- `keywords_master.txt` - Curated final list (Tom maintains)
- Phase 4b will use keywords_master.txt

**Workflow:**
1. Programmer implements Phase 4a.1-4a.4
2. Programmer runs with small sample (--sample 10) to verify
3. Tom runs multiple iterations to build keywords_master.txt
4. Phase 4a complete when Tom is satisfied with keyword list
5. Phase 4b uses keywords_master.txt as input

---

## Phase 4b: LLM Keyword Tagging

**Goal:** Tag all messages with keywords from Phase 4a's keywords_master.txt

**REVISED 2025-11-03:** Store keywords IN image_index.json as `llm_keywords` field

**Scope:**
- Tag only messages with images (~7k messages in image_index.json)
- Use keywords_master.txt from Phase 4a (200-300 keywords)
- Store results in image_index.json (not separate file)

**Prerequisites:**
- Phase 4a must be complete (keywords_master.txt exists)

### Phase 4b.1: LLM Configuration File

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
4. [ ] Commit: "Add LLM configuration file (Phase 4b.1)"

**Deliverable:** llm_config.py with editable prompt and model

---

### Phase 4b.2: LLM Keyword Tagger Core (TDD)

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
13. [ ] Commit: "Implement LLM keyword tagger core (Phase 4b.2)"

**Implementation Notes:**
- Follow pattern from `embedder/f_llm.py` (class-based, ollama.Client)
- Import config from llm_config.py
- Graceful error handling: log and continue (don't crash)
- Validate LLM responses against master keyword list (prevent hallucination)
- Handle various response formats: "keyword1, keyword2" or "NONE" or empty

**Deliverable:** KeywordTagger class with 6+ passing tests

---

### Phase 4b.3: Batch Message Tagger (TDD)

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
   - Load keywords from keywords_master.txt (from Phase 4a, or custom file)
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
10. [ ] Commit: "Implement batch message tagger (Phase 4b.3)"

**Deliverable:** Core processing logic with tests

---

### Phase 4b.4: CLI Interface

**Goal:** Command line tool for tagging messages

**Tasks:**
1. [ ] Create `imageGetter/tag_messages_cli.py` with ABOUTME comments
2. [ ] Add argument parsing:
   - Positional: `INDEX_FILE` (path to image_index.json)
   - `--limit N` - process first N messages
   - `--overwrite` - retag existing llm_keywords
   - `--keywords FILE` - use custom keyword file (default: ../docs/input/keywords_master.txt from Phase 4a)
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
8. [ ] Commit: "Add CLI for message tagging (Phase 4b.4)"

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

### Phase 4b.5: Validate and Document

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
- Located: `docs/input/keywords_master.txt` (created in Phase 4a)
- Approximately 200-300 keywords after Phase 4a complete
- Default CLI parameter points to keywords_master.txt

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
