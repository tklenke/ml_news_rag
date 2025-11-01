# Programmer Todo - Image Database Project

**Project:** Image Database for Cozy Builders Newsgroup
**Created:** 2025-11-01
**Last Updated:** 2025-11-01

## Overview

Implement image database system following the incremental plan in `image_database_implementation_plan.md`.

**Architecture Document:** `docs/plans/image_database_architecture.md`
**Implementation Plan:** `docs/plans/image_database_implementation_plan.md`

---

## Current Phase: Phase 1 - Image URL Extraction

**Goal:** Extract and index image URLs from markdown files (A/ directory only)

**Before Starting:** Read the architecture and implementation plan documents completely.

---

## Phase 1: Image URL Extraction

### Phase 1.1: URL Pattern Analysis
- [x] Manually inspect 10-15 markdown files from data/msgs_md/A/ with images
- [x] Document URL patterns for attachments (INCLUDE), profile photos (EXCLUDE), logos/emojis (EXCLUDE)
- [x] Document markdown syntax patterns (inline images, links with images)
- [x] Create `docs/notes/image_url_patterns.md` with findings
- [x] Commit: "Document image URL patterns from A/ directory analysis"

### Phase 1.2: Create imageGetter Module Structure
- [x] Create `imageGetter/` directory
- [x] Create `imageGetter/README.md` with ABOUTME comments and module purpose
- [x] Create `imageGetter/requirements.txt` (empty initially)
- [x] Create `imageGetter/tests/` directory
- [x] Create `imageGetter/tests/test_extract_urls.py` (with ABOUTME, empty tests initially)
- [x] Create virtual environment: `python -m venv imageGetter/venv`
- [x] Add `imageGetter/venv/` to `.gitignore` (already present)
- [x] Document venv setup in `imageGetter/README.md`
- [x] Commit: "Create imageGetter module structure with venv"

### Phase 1.3: URL Extraction - Test Data
- [x] Create `imageGetter/tests/fixtures/` directory
- [x] Copy 3-5 sample markdown files from A/ directory to fixtures
  - At least one with attachment images
  - At least one with profile photos only
  - At least one with no images
- [x] Create expected output JSON for each fixture file
- [x] Create scan_image_urls.py to analyze full corpus
- [x] Run full corpus scan (10,443 files analyzed)
- [x] Document scan results in image_url_patterns.md
- [x] Validate simple filter captures 97% of relevant URLs
- [~] Commit: "Add URL scan results and validate filtering strategy"

### Phase 1.4: URL Extraction - Core Logic (TDD)
**RED Phase:**
- [ ] Write failing test: `test_extract_attachment_urls_from_markdown()`
- [ ] Write failing test: `test_exclude_profile_photos()`
- [ ] Write failing test: `test_exclude_logos_and_emojis()`
- [ ] Write failing test: `test_extract_from_multiple_images()`
- [ ] Write failing test: `test_handle_markdown_with_no_images()`
- [ ] Run pytest - verify all tests fail

**GREEN Phase:**
- [ ] Implement `extract_image_urls(strMarkdownContent: str) -> list[dict]`
- [ ] Run pytest - verify all tests pass

**REFACTOR Phase:**
- [ ] Refactor for clarity and maintainability while keeping tests green
- [ ] Commit: "Implement URL extraction with filtering"

### Phase 1.5: Message Metadata Extraction (TDD)
**RED Phase:**
- [ ] Write failing test: `test_extract_message_id()`
- [ ] Write failing test: `test_extract_subject()`
- [ ] Write failing test: `test_extract_author()`
- [ ] Write failing test: `test_extract_date()`
- [ ] Run pytest - verify all tests fail

**GREEN Phase:**
- [ ] Implement `extract_message_metadata(strMarkdownPath: str) -> dict`
- [ ] Run pytest - verify all tests pass

**REFACTOR Phase:**
- [ ] Refactor if needed while keeping tests green
- [ ] Commit: "Implement message metadata extraction"

### Phase 1.6: Build Image Index from Directory (TDD)
**RED Phase:**
- [ ] Write failing test: `test_process_single_markdown_file()`
- [ ] Write failing test: `test_process_directory_of_markdown_files()`
- [ ] Write failing test: `test_skip_files_without_images()`
- [ ] Write failing test: `test_handle_malformed_markdown()`
- [ ] Run pytest - verify all tests fail

**GREEN Phase:**
- [ ] Implement `build_image_index(strDirectoryPath: str) -> dict`
- [ ] Add progress logging (e.g., "Processing 45/127 files...")
- [ ] Run pytest - verify all tests pass

**REFACTOR Phase:**
- [ ] Refactor if needed while keeping tests green
- [ ] Commit: "Implement image index builder"

### Phase 1.7: CLI Tool for URL Extraction
- [ ] Create `imageGetter/extract_image_urls.py` script with ABOUTME comments
- [ ] Add command-line argument parsing (--input, --output, --dry-run)
- [ ] Add progress bar or status output
- [ ] Add error handling and logging
- [ ] Test on A/ directory with --dry-run flag
- [ ] Commit: "Add CLI tool for image URL extraction"

### Phase 1.8: Validate Phase 1 Results
- [ ] Run extraction on full A/ directory (not dry-run): `python imageGetter/extract_image_urls.py --input data/msgs_md/A --output data/image_index.json`
- [ ] Review `data/image_index.json` (check counts, spot-check 5-10 URLs)
- [ ] Create `docs/notes/phase1_results.md` with statistics:
  - Total markdown files in A/
  - Files with images
  - Total image URLs extracted
  - Sample of excluded profile/logo URLs
- [ ] Fix any issues discovered and re-run if needed
- [ ] Commit: "Complete Phase 1: URL extraction from A/ directory"

**Phase 1 Complete: Mark [x] when ALL tasks above done and committed**
- [ ] **PHASE 1 COMPLETE** - Ready for Architect review

---

## Phase 2: Image Download

**Goal:** Download images from URLs in image_index.json (A/ directory only)

**Start only after Phase 1 is complete and reviewed by Architect (if needed)**

### Phase 2.1: Create Download Module Structure
- [ ] Create `imageGetter/download_images.py` module file with ABOUTME
- [ ] Create `imageGetter/tests/test_download.py` with ABOUTME
- [ ] Create `data/images/` directory
- [ ] Create `data/images/full/` directory
- [ ] Create `data/images/thumbs/` directory (for Phase 3)
- [ ] Add `Pillow>=10.0.0` to `imageGetter/requirements.txt`
- [ ] Add `requests>=2.31.0` to `imageGetter/requirements.txt`
- [ ] Add `tqdm>=4.65.0` to `imageGetter/requirements.txt`
- [ ] Run `pip install -r imageGetter/requirements.txt` in venv
- [ ] Commit: "Create image download module structure"

### Phase 2.2: Single Image Download (TDD)
**RED Phase:**
- [ ] Write failing test: `test_download_single_image()` (use mocked HTTP)
- [ ] Write failing test: `test_handle_404_error()`
- [ ] Write failing test: `test_handle_timeout()`
- [ ] Write failing test: `test_retry_on_failure()`
- [ ] Write failing test: `test_validate_image_after_download()`
- [ ] Run pytest - verify all tests fail

**GREEN Phase:**
- [ ] Implement `download_image(strUrl: str, strOutputPath: str) -> bool`
  - Use requests library
  - 3 retries with exponential backoff
  - Validate image can be opened with PIL
  - Return True if successful, False otherwise
- [ ] Run pytest - verify all tests pass

**REFACTOR Phase:**
- [ ] Refactor if needed while keeping tests green
- [ ] Commit: "Implement single image download with retry"

### Phase 2.3: Filename Generation (TDD)
**RED Phase:**
- [ ] Write failing test: `test_generate_filename_from_message_id()`
- [ ] Write failing test: `test_preserve_file_extension()`
- [ ] Write failing test: `test_handle_missing_extension()`
- [ ] Write failing test: `test_handle_part_number()`
- [ ] Run pytest - verify all tests fail

**GREEN Phase:**
- [ ] Implement `generate_filename(strMessageId: str, strUrl: str, strPart: str) -> str`
  - Format: `{messageID}_part{part}.{ext}`
  - Example: `A1NtxlDfY4c_part0.1.jpg`
- [ ] Run pytest - verify all tests pass

**REFACTOR Phase:**
- [ ] Refactor if needed while keeping tests green
- [ ] Commit: "Implement standardized filename generation"

### Phase 2.4: Batch Download with Progress (TDD)
**RED Phase:**
- [ ] Write failing test: `test_download_batch_of_images()`
- [ ] Write failing test: `test_update_index_after_download()`
- [ ] Write failing test: `test_skip_already_downloaded()`
- [ ] Write failing test: `test_rate_limiting()`
- [ ] Run pytest - verify all tests fail

**GREEN Phase:**
- [ ] Implement `download_all_images(dctImageIndex: dict, strOutputDir: str) -> dict`
  - Add rate limiting (1.5 second delay between downloads)
  - Update image_index.json with download status
  - Log progress and errors
  - Skip files that already exist
- [ ] Run pytest - verify all tests pass

**REFACTOR Phase:**
- [ ] Refactor if needed while keeping tests green
- [ ] Commit: "Implement batch image download with rate limiting"

### Phase 2.5: CLI Tool for Image Download
- [ ] Create `imageGetter/download_images_cli.py` script with ABOUTME
- [ ] Add command-line arguments (--index, --output, --limit, --delay)
- [ ] Add progress bar (tqdm)
- [ ] Add summary statistics at end (success/fail counts)
- [ ] Test with `--limit 5` first: `python imageGetter/download_images_cli.py --index data/image_index.json --output data/images/full --limit 5`
- [ ] Verify 5 test images downloaded successfully
- [ ] Commit: "Add CLI tool for image download"

### Phase 2.6: Download Full A/ Directory Images
- [ ] Run download without --limit flag
- [ ] Monitor for errors, 404s, rate limiting issues
- [ ] Create `docs/notes/phase2_results.md` with statistics:
  - Total images attempted
  - Successful downloads
  - Failed downloads with reasons
  - Total disk space used
- [ ] Verify downloaded images (spot-check 10 images can be opened)
- [ ] Check file sizes are reasonable (> 10KB)
- [ ] Fix any issues and re-run failed downloads if needed
- [ ] Commit: "Complete Phase 2: Download A/ directory images"

**Phase 2 Complete: Mark [x] when ALL tasks above done and committed**
- [ ] **PHASE 2 COMPLETE** - Ready for Architect review

---

## Phase 3: Thumbnail Generation

**Goal:** Create 200x200px center-cropped thumbnails for all downloaded images

**Start only after Phase 2 is complete**

### Phase 3.1: Thumbnail Generation Function (TDD)
**RED Phase:**
- [ ] Write failing test: `test_generate_thumbnail_200x200()`
- [ ] Write failing test: `test_center_crop_landscape_image()`
- [ ] Write failing test: `test_center_crop_portrait_image()`
- [ ] Write failing test: `test_handle_square_image()`
- [ ] Write failing test: `test_handle_small_image()` (smaller than 200x200)
- [ ] Write failing test: `test_save_thumbnail_as_jpeg()`
- [ ] Run pytest - verify all tests fail

**GREEN Phase:**
- [ ] Create `imageGetter/generate_thumbnails.py` with ABOUTME
- [ ] Implement `generate_thumbnail(strInputPath: str, strOutputPath: str, intSize: int = 200) -> bool`
  - Use PIL/Pillow
  - Center crop to square
  - Resize to 200x200
  - Save as JPEG (quality=85)
  - Return True if successful
- [ ] Run pytest - verify all tests pass

**REFACTOR Phase:**
- [ ] Refactor if needed while keeping tests green
- [ ] Commit: "Implement thumbnail generation with center crop"

### Phase 3.2: Batch Thumbnail Generation (TDD)
**RED Phase:**
- [ ] Write failing test: `test_generate_thumbnails_for_directory()`
- [ ] Write failing test: `test_skip_existing_thumbnails()`
- [ ] Write failing test: `test_update_index_after_thumbnail()`
- [ ] Write failing test: `test_handle_corrupt_image()`
- [ ] Run pytest - verify all tests fail

**GREEN Phase:**
- [ ] Implement `generate_all_thumbnails(strInputDir: str, strOutputDir: str, dctImageIndex: dict) -> dict`
  - Process all images in input directory
  - Save to output directory with `_thumb` suffix
  - Update image_index.json with thumbnail status
  - Skip if thumbnail already exists
- [ ] Run pytest - verify all tests pass

**REFACTOR Phase:**
- [ ] Refactor if needed while keeping tests green
- [ ] Commit: "Implement batch thumbnail generation"

### Phase 3.3: CLI Tool for Thumbnail Generation
- [ ] Create `imageGetter/generate_thumbnails_cli.py` script with ABOUTME
- [ ] Add command-line arguments (--input, --output, --index, --size)
- [ ] Add progress indicator
- [ ] Add summary statistics
- [ ] Test on A/ directory images
- [ ] Commit: "Add CLI tool for thumbnail generation"

### Phase 3.4: Generate Thumbnails for A/ Directory
- [ ] Run thumbnail generation: `python imageGetter/generate_thumbnails_cli.py --input data/images/full --output data/images/thumbs --index data/image_index.json`
- [ ] Verify thumbnails (check dimensions 200x200, spot-check 10 visually)
- [ ] Verify file sizes reasonable (5-20KB typically)
- [ ] Create `docs/notes/phase3_results.md` with statistics:
  - Total thumbnails generated
  - Any failures
  - Total disk space used
- [ ] Verify image_index.json updated correctly
- [ ] Commit: "Complete Phase 3: Generate thumbnails for A/ directory"

**Phase 3 Complete: Mark [x] when ALL tasks above done and committed**
- [ ] **PHASE 3 COMPLETE** - Ready for Architect review

---

## Phase 4: Query Interface

**Goal:** Query interface that returns images based on text search

**Start only after Phase 3 is complete**

### Phase 4.1: Create imageAsker Module
- [ ] Create `imageAsker/` directory
- [ ] Create `imageAsker/README.md` with ABOUTME and module purpose
- [ ] Create `imageAsker/query_images.py` with ABOUTME
- [ ] Create `imageAsker/tests/` directory
- [ ] Create `imageAsker/tests/test_query.py` with ABOUTME
- [ ] Commit: "Create imageAsker module structure"

### Phase 4.2: Image Index Loading (TDD)
**RED Phase:**
- [ ] Write failing test: `test_load_image_index()`
- [ ] Write failing test: `test_get_images_for_message_id()`
- [ ] Write failing test: `test_get_images_for_multiple_message_ids()`
- [ ] Write failing test: `test_filter_messages_with_images()`
- [ ] Run pytest - verify all tests fail

**GREEN Phase:**
- [ ] Implement `load_image_index(strPath: str) -> dict`
- [ ] Implement `get_images_for_messages(lstMessageIds: list[str], dctImageIndex: dict) -> list[dict]`
- [ ] Run pytest - verify all tests pass

**REFACTOR Phase:**
- [ ] Refactor if needed while keeping tests green
- [ ] Commit: "Implement image index loading and lookup"

### Phase 4.3: Integration with Existing RAG
**Important:** Review existing `asker/` module to understand query interface first

- [ ] Review existing asker/ module code
- [ ] Identify how to get message IDs from text query results
- [ ] Write failing test: `test_query_text_and_return_images()`
- [ ] Write failing test: `test_handle_no_images_in_results()`
- [ ] Run pytest - verify all tests fail
- [ ] Implement `query_images(strQueryText: str, intMaxResults: int = 50) -> list[dict]`
  - Query existing RAG system
  - Extract message IDs from results
  - Lookup images in image_index.json
  - Return image data with message context
- [ ] Run pytest - verify all tests pass
- [ ] Commit: "Integrate image lookup with text RAG query"

**If existing RAG integration unclear:** STOP and escalate to Architect

### Phase 4.4: CLI Image Query Tool
- [ ] Create `imageAsker/query_images_cli.py` script with ABOUTME
- [ ] Add command-line arguments (query text, --max-results, --index)
- [ ] Display results (thumbnail paths, message subject/ID, relevance score)
- [ ] Test with queries: "firewall", "oil cooler", "panel", "wing"
- [ ] Commit: "Add CLI tool for image queries"

### Phase 4.5: Simple Thumbnail Viewer (Optional - HTML approach recommended)
- [ ] Decide on approach with Tom (HTML file recommended as simplest)
- [ ] If HTML: Create script to generate HTML file with thumbnail grid
- [ ] Test with A/ directory results
- [ ] Commit: "Add thumbnail viewer for query results"

### Phase 4.6: Validate Phase 4 Results
- [ ] Test queries on A/ directory:
  - "engine" - expect engine/installation photos
  - "panel" - expect panel/avionics photos
  - "cowling" - expect cowling photos
  - "firewall" - expect firewall photos
- [ ] Create `docs/notes/phase4_results.md` documenting:
  - Query examples and results
  - Retrieval quality assessment
  - Any issues or limitations discovered
- [ ] Get feedback from Tom on retrieval quality
- [ ] Iterate on query logic if needed
- [ ] Commit: "Complete Phase 4: Image query interface on A/ directory"

**Phase 4 Complete: Mark [x] when ALL tasks above done and committed**
- [ ] **PHASE 4 COMPLETE** - Ready for Architect review and Tom feedback

---

## Phase 5: Scale to Full Corpus

**Goal:** Process all directories (B/ through Z/) and create complete image database

**Start only after Phase 4 is complete AND Tom approves proceeding with full corpus**

### Phase 5.1: Estimate Full Corpus Scale
- [ ] Calculate statistics from A/ directory results
- [ ] Count total markdown files across all directories
- [ ] Project estimates for full corpus (total images, disk space, download time)
- [ ] Check available disk space
- [ ] Create `docs/notes/phase5_projections.md` with estimates
- [ ] Get Tom's approval to proceed based on projections
- [ ] Commit: "Document full corpus projections"

### Phase 5.2: Process All Directories
- [ ] Run URL extraction on all directories (B/ through Z/)
- [ ] Merge results into single image_index.json
- [ ] Run image download (may need to run overnight - inform Tom)
- [ ] Monitor progress and handle errors
- [ ] Run thumbnail generation
- [ ] Verify final image_index.json
- [ ] Commit: "Complete Phase 5: Full corpus image database"

### Phase 5.3: Final Validation and Documentation
- [ ] Generate final statistics document
- [ ] Test queries on full database
- [ ] Create `docs/notes/phase5_final_results.md` with complete statistics
- [ ] Update `docs/project_info.md` with image database details
- [ ] Create user guide for image query system
- [ ] Commit: "Complete Phase 5: Full image database operational"

**Phase 5 Complete: Mark [x] when ALL tasks above done and committed**
- [ ] **PHASE 5 COMPLETE** - System fully operational

---

## Important Reminders

### TDD Process
1. **RED:** Write failing test first
2. **GREEN:** Implement minimal code to pass
3. **REFACTOR:** Clean up while keeping tests green
4. **COMMIT:** After each TDD cycle

### Before Every Commit
- [ ] Run all tests (`pytest`)
- [ ] Verify tests pass
- [ ] Update this todo file marking tasks complete [x]
- [ ] Include updated programmer_todo.md in commit

### When to Escalate to Architect
- URL filtering not working (too many false positives/negatives)
- Download success rate unexpectedly low (<50%)
- Integration with existing RAG system unclear
- Architectural assumptions don't match reality
- Major technical blockers

Use "Strange things are afoot at the Circle K" if urgent architectural attention needed.

### Code Quality Standards
- All new files must have ABOUTME comments (2 lines explaining what file does)
- Follow Hungarian notation (strVariableName, intCount, lstItems, dctMapping)
- Follow TDD strictly - write tests first
- Match existing code style
- No temporal context in names ("new", "old", "legacy")
- Fix bugs immediately when found

---

## Current Task Status

**Currently Working On:** (Mark with [~] when starting a task)
- [ ] None - waiting to start

**Next Task:** Phase 1.1 - URL Pattern Analysis

---

**Last Updated:** 2025-11-01 by Claude (Architect)
**Programmer:** (Will be updated by Programmer during implementation)
