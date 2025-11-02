# Image Database - Incremental Implementation Plan

**Created:** 2025-11-01
**Status:** Ready for Implementation
**Related:** `image_database_architecture.md`

## Overview

This document breaks down the image database implementation into small, testable increments. Each phase follows TDD principles and builds on the previous phase. All phases use the A/ directory as test data until Phase 5.

---

## Phase 1: Image URL Extraction

**Goal:** Extract and index image URLs from markdown files (A/ directory only)

### Phase 1.1: URL Pattern Analysis
**Deliverable:** Understanding of URL patterns in markdown files

**Tasks:**
1. ☐ Manually inspect 20-25 markdown files from A/ directory with images
2. ☐ Document URL patterns for:
   - Attachment images (INCLUDE)
   - Profile photos (EXCLUDE)
   - Logos/emojis (EXCLUDE)
3. ☐ Document markdown syntax patterns (inline images, links with images)
4. ☐ Create `docs/notes/image_url_patterns.md` with findings

**Test Data:** Files already identified in architecture phase
**Acceptance:** Clear regex/parsing strategy documented

---

### Phase 1.2: Create imageGetter Module Structure
**Deliverable:** Basic module skeleton with tests and virtual environment

**Tasks:**
1. ☐ Create `imageGetter/` directory
2. ☐ Create `imageGetter/README.md` with ABOUTME comments and module purpose
3. ☐ Create `imageGetter/requirements.txt` (empty initially, will add dependencies in later phases)
4. ☐ Create `imageGetter/tests/` directory
5. ☐ Create `imageGetter/tests/test_extract_urls.py` (with ABOUTME, empty tests initially)
6. ☐ Create virtual environment: `python -m venv imageGetter/venv`
7. ☐ Add `imageGetter/venv/` to `.gitignore` (if not already there)
8. ☐ Document venv setup in `imageGetter/README.md`:
   ```bash
   # Setup
   cd imageGetter
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

**Test:** Directory structure exists, README describes module, venv can be created
**Commit:** "Create imageGetter module structure with venv"

---

### Phase 1.3: URL Extraction - Test Data
**Deliverable:** Test fixtures for URL extraction

**Tasks:**
1. ☐ Create `imageGetter/tests/fixtures/` directory
2. ☐ Copy 3-5 sample markdown files from A/ directory to fixtures
   - At least one with attachment images
   - At least one with profile photos only
   - At least one with no images
3. ☐ Create expected output JSON for each fixture file
4. ☐ Document test fixture contents in `imageGetter/tests/fixtures/README.md`

**Test:** Fixtures exist and are documented
**Commit:** "Add test fixtures for URL extraction"

---

### Phase 1.4: URL Extraction - Core Logic (TDD)
**Deliverable:** Function to extract image URLs from markdown content

**Tasks:**
1. ☐ Write failing test: `test_extract_attachment_urls_from_markdown()`
2. ☐ Write failing test: `test_exclude_profile_photos()`
3. ☐ Write failing test: `test_exclude_logos_and_emojis()`
4. ☐ Write failing test: `test_extract_from_multiple_images()`
5. ☐ Write failing test: `test_handle_markdown_with_no_images()`
6. ☐ Run tests - verify all fail
7. ☐ Implement `extract_image_urls(strMarkdownContent: str) -> list[dict]`
8. ☐ Run tests - verify all pass
9. ☐ Refactor if needed

**Output Format:**
```python
[
  {
    "url": "https://groups.google.com/group/cozy_builders/attach/.../img.jpg?part=0.1",
    "part": "0.1",
    "filename": "img.jpg"
  }
]
```

**Test:** All tests pass, 100% code coverage for extract_image_urls()
**Commit:** "Implement URL extraction with filtering"

---

### Phase 1.5: Message Metadata Extraction (TDD)
**Deliverable:** Extract message metadata from markdown files

**Tasks:**
1. ☐ Write failing test: `test_extract_message_id()`
2. ☐ Write failing test: `test_extract_subject()`
3. ☐ Write failing test: `test_extract_author()`
4. ☐ Write failing test: `test_extract_date()`
5. ☐ Run tests - verify all fail
6. ☐ Implement `extract_message_metadata(strMarkdownPath: str) -> dict`
7. ☐ Run tests - verify all pass

**Output Format:**
```python
{
  "message_id": "A1NtxlDfY4c",
  "subject": "Re: [c-a] Van's baffles for Long-ez",
  "author": "krw...@gmail.com",
  "date": "2012-07-23"
}
```

**Test:** All tests pass
**Commit:** "Implement message metadata extraction"

---

### Phase 1.6: Build Image Index from Directory (TDD)
**Deliverable:** Process all markdown files in a directory and build index

**Tasks:**
1. ☐ Write failing test: `test_process_single_markdown_file()`
2. ☐ Write failing test: `test_process_directory_of_markdown_files()`
3. ☐ Write failing test: `test_skip_files_without_images()`
4. ☐ Write failing test: `test_handle_malformed_markdown()`
5. ☐ Run tests - verify all fail
6. ☐ Implement `build_image_index(strDirectoryPath: str) -> dict`
7. ☐ Run tests - verify all pass
8. ☐ Add progress logging (e.g., "Processing 45/127 files...")

**Output:** Dictionary ready to serialize as image_index.json
**Test:** All tests pass, processes test fixtures correctly
**Commit:** "Implement image index builder"

---

### Phase 1.7: CLI Tool for URL Extraction
**Deliverable:** Command-line tool to extract URLs from A/ directory

**Tasks:**
1. ☐ Create `imageGetter/extract_image_urls.py` script
2. ☐ Add command-line argument parsing (input dir, output file)
3. ☐ Add `--dry-run` flag to preview without writing
4. ☐ Add progress bar or status output
5. ☐ Write output to `data/image_index.json`
6. ☐ Add error handling and logging
7. ☐ Test on actual A/ directory

**Usage:**
```bash
python imageGetter/extract_image_urls.py \
  --input data/msgs_md/A \
  --output data/image_index.json \
  --dry-run
```

**Test:** Successfully processes A/ directory, creates valid JSON
**Commit:** "Add CLI tool for image URL extraction"

---

### Phase 1.8: Validate Phase 1 Results
**Deliverable:** Verified image index for A/ directory

**Tasks:**
1. ☐ Run extraction on full A/ directory (not dry-run)
2. ☐ Review `data/image_index.json`:
   - Check message count
   - Check image URL count
   - Spot-check 5-10 URLs manually (click links, verify they're attachments)
3. ☐ Document statistics in `docs/notes/phase1_results.md`:
   - Total markdown files in A/
   - Files with images
   - Total image URLs extracted
   - Sample of excluded profile/logo URLs
4. ☐ Fix any issues discovered and re-run

**Test:** image_index.json contains 50+ image URLs, spot-checks pass
**Commit:** "Complete Phase 1: URL extraction from A/ directory"

---

## Phase 2: Image Download

**Goal:** Download images from URLs in image_index.json (A/ directory only)

### Phase 2.1: Create Download Module Structure
**Deliverable:** Download module with test infrastructure

**Tasks:**
1. ☐ Create `imageGetter/download_images.py` module file with ABOUTME
2. ☐ Create `imageGetter/tests/test_download.py` with ABOUTME
3. ☐ Create `data/images/full/` directory
4. ☐ Create `data/images/thumbs/` directory (for later)
5. ☐ Add dependencies to `imageGetter/requirements.txt`:
   - `Pillow>=10.0.0` (image validation)
   - `selenium>=4.0.0` (authenticated downloads)
6. ☐ Add `imageGetter/venv/` to .gitignore (local virtual environment)
7. ☐ Document Selenium setup in `imageGetter/README.md`:
   - Tom will run Chrome with debug on port 9222
   - Chrome will be logged into Google Groups
   - Use existing pattern from msgGetter

**Test:** Directory structure exists
**Commit:** "Create image download module structure"

**Note:** Assumes Tom has Chrome running with: `chrome.exe --remote-debugging-port=9222`

---

### Phase 2.2: Selenium Setup and Single Image Download (TDD)
**Deliverable:** Function to download and save one image using Selenium

**Tasks:**
1. ☐ Create Selenium connection helper (copy pattern from msgGetter):
   ```python
   service = Service(executable_path='../../chromedriver-win64/chromedriver.exe')
   options = webdriver.ChromeOptions()
   options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
   driver = webdriver.Chrome(service=service, options=options)
   ```
2. ☐ Write failing test: `test_download_single_image()` (mocked Selenium)
3. ☐ Write failing test: `test_handle_missing_image()` (404/broken link)
4. ☐ Write failing test: `test_retry_on_failure()`
5. ☐ Write failing test: `test_validate_image_after_download()`
6. ☐ Run tests - verify all fail
7. ☐ Implement `download_image_selenium(strUrl: str, strOutputPath: str, seleniumDriver) -> bool`
   - Navigate to image URL with Selenium
   - Wait for image to load
   - Get image from browser (screenshot or download)
   - Save to output path
   - Validate image can be opened with PIL
   - Return True if successful, False otherwise
8. ☐ Add retry logic (3 retries with delays)
9. ☐ Run tests - verify all pass

**Test:** All tests pass, includes error handling
**Commit:** "Implement single image download with Selenium"

**Implementation Note:** May need to use `driver.get(url)` + `driver.save_screenshot()` or find img element and get src data.

---

### Phase 2.3: Filename Generation (TDD)
**Deliverable:** Generate standardized filenames from message ID and URL

**Tasks:**
1. ☐ Write failing test: `test_generate_filename_from_message_id()`
2. ☐ Write failing test: `test_preserve_file_extension()`
3. ☐ Write failing test: `test_handle_missing_extension()`
4. ☐ Write failing test: `test_handle_part_number()`
5. ☐ Run tests - verify all fail
6. ☐ Implement `generate_filename(strMessageId: str, strUrl: str, strPart: str) -> str`
   - Format: `{messageID}_part{part}.{ext}`
   - Example: `A1NtxlDfY4c_part0.1.jpg`
7. ☐ Run tests - verify all pass

**Test:** All tests pass
**Commit:** "Implement standardized filename generation"

---

### Phase 2.4: Batch Download with Progress (TDD)
**Deliverable:** Download all images from image_index.json

**Tasks:**
1. ☐ Write failing test: `test_download_batch_of_images()`
2. ☐ Write failing test: `test_update_index_after_download()`
3. ☐ Write failing test: `test_skip_already_downloaded()`
4. ☐ Write failing test: `test_rate_limiting()`
5. ☐ Run tests - verify all fail
6. ☐ Implement `download_all_images(dctImageIndex: dict, strOutputDir: str, seleniumDriver) -> dict`
   - Initialize Selenium driver (shared across downloads)
   - Add rate limiting (1.5-2 second delay between downloads)
   - Update image_index.json with download status after each image
   - Log progress and errors
   - Skip files that already exist
   - Handle Selenium exceptions gracefully
7. ☐ Run tests - verify all pass

**Test:** All tests pass
**Commit:** "Implement batch image download with rate limiting"

**Note:** Reuse single Selenium driver instance across all downloads for efficiency

---

### Phase 2.5: CLI Tool for Image Download
**Deliverable:** Command-line tool to download images using Selenium

**Tasks:**
1. ☐ Create `imageGetter/download_images_cli.py` script with ABOUTME
2. ☐ Add command-line arguments:
   - `--index` (path to image_index.json)
   - `--output` (directory for images)
   - `--limit` (max images to download, for testing)
   - `--delay` (seconds between downloads, default 1.5)
3. ☐ Initialize Selenium driver (connect to debug Chrome on port 9222)
4. ☐ Add progress bar (tqdm)
5. ☐ Add summary statistics at end (success/fail counts)
6. ☐ Clean up Selenium driver on exit
7. ☐ Test with `--limit 5` first

**Prerequisites:** Tom must have Chrome running with `--remote-debugging-port=9222` and logged into Google Groups

**Usage:**
```bash
# Tom runs first: chrome.exe --remote-debugging-port=9222
python imageGetter/download_images_cli.py \
  --index data/image_index.json \
  --output data/images/full \
  --limit 5
```

**Test:** Successfully downloads 5 test images
**Commit:** "Add CLI tool for image download"

---

### Phase 2.6: Download Full A/ Directory Images
**Deliverable:** All A/ directory images downloaded

**Tasks:**
1. ☐ Run download without `--limit` flag
2. ☐ Monitor for errors, 404s, rate limiting issues
3. ☐ Document results in `docs/notes/phase2_results.md`:
   - Total images attempted
   - Successful downloads
   - Failed downloads (with reasons)
   - Total disk space used
4. ☐ Verify downloaded images:
   - Spot-check 10 images can be opened
   - Check file sizes are reasonable (> 10KB)
5. ☐ Fix any issues and re-run failed downloads

**Test:** >75% download success rate, images are valid
**Commit:** "Complete Phase 2: Download A/ directory images"

---

## Phase 3: Thumbnail Generation

**Goal:** Create 200x200px center-cropped thumbnails for all downloaded images

### Phase 3.1: Thumbnail Generation Function (TDD)
**Deliverable:** Function to create thumbnail from image

**Tasks:**
1. ☐ Write failing test: `test_generate_thumbnail_200x200()`
2. ☐ Write failing test: `test_center_crop_landscape_image()`
3. ☐ Write failing test: `test_center_crop_portrait_image()`
4. ☐ Write failing test: `test_handle_square_image()`
5. ☐ Write failing test: `test_handle_small_image()` (smaller than 200x200)
6. ☐ Write failing test: `test_save_thumbnail_as_jpeg()`
7. ☐ Run tests - verify all fail
8. ☐ Implement `generate_thumbnail(strInputPath: str, strOutputPath: str, intSize: int = 200) -> bool`
   - Use PIL/Pillow
   - Center crop to square
   - Resize to 200x200
   - Save as JPEG (quality=85)
   - Return True if successful
9. ☐ Run tests - verify all pass

**Test:** All tests pass, thumbnails are correctly sized and cropped
**Commit:** "Implement thumbnail generation with center crop"

---

### Phase 3.2: Batch Thumbnail Generation (TDD)
**Deliverable:** Generate thumbnails for all downloaded images

**Tasks:**
1. ☐ Write failing test: `test_generate_thumbnails_for_directory()`
2. ☐ Write failing test: `test_skip_existing_thumbnails()`
3. ☐ Write failing test: `test_update_index_after_thumbnail()`
4. ☐ Write failing test: `test_handle_corrupt_image()`
5. ☐ Run tests - verify all fail
6. ☐ Implement `generate_all_thumbnails(strInputDir: str, strOutputDir: str, dctImageIndex: dict) -> dict`
   - Process all images in input directory
   - Save to output directory with `_thumb` suffix
   - Update image_index.json with thumbnail status
   - Skip if thumbnail already exists
7. ☐ Run tests - verify all pass

**Test:** All tests pass
**Commit:** "Implement batch thumbnail generation"

---

### Phase 3.3: CLI Tool for Thumbnail Generation
**Deliverable:** Command-line tool to generate thumbnails

**Tasks:**
1. ☐ Create `imageGetter/generate_thumbnails_cli.py` script
2. ☐ Add command-line arguments:
   - `--input` (directory with full images)
   - `--output` (directory for thumbnails)
   - `--index` (path to image_index.json)
   - `--size` (thumbnail size, default 200)
3. ☐ Add progress indicator
4. ☐ Add summary statistics

**Usage:**
```bash
python imageGetter/generate_thumbnails_cli.py \
  --input data/images/full \
  --output data/images/thumbs \
  --index data/image_index.json
```

**Test:** Successfully generates thumbnails for test images
**Commit:** "Add CLI tool for thumbnail generation"

---

### Phase 3.4: Generate Thumbnails for A/ Directory
**Deliverable:** Thumbnails for all A/ directory images

**Tasks:**
1. ☐ Run thumbnail generation on all downloaded images
2. ☐ Verify thumbnails:
   - Check dimensions (should be 200x200)
   - Spot-check 10 thumbnails visually
   - Verify file sizes reasonable (5-20KB typically)
3. ☐ Document results in `docs/notes/phase3_results.md`:
   - Total thumbnails generated
   - Any failures
   - Total disk space used
4. ☐ Verify image_index.json updated correctly

**Test:** All thumbnails generated successfully, image_index.json accurate
**Commit:** "Complete Phase 3: Generate thumbnails for A/ directory"

---

## Phase 4: LLM Keyword Tagging

**Goal:** Use local LLM to tag messages with curated aircraft-building keywords

**REVISED 2025-11-02:** This approach provides semantic understanding at index-time (one-time cost) rather than query-time, making queries fast and results debuggable. The LLM identifies which keywords (or close approximations) appear in each message.

### Phase 4.1: Build Master Keyword List
**Deliverable:** Curated list of 50-200 aircraft-building keywords

**Approach:** Iterative LLM-assisted curation
1. Take 100 random messages from corpus
2. Ask local LLM: "Extract keywords related to Cozy experimental aircraft building from these messages"
3. Review LLM output, prune irrelevant terms
4. Repeat with different 100-message batches until keyword list stabilizes
5. Final human review and cleanup

**Tasks:**
1. ☐ Create `imageAsker/` directory
2. ☐ Create `imageAsker/build_keyword_list.py` script
3. ☐ Sample 100 messages from data/msgs_md/
4. ☐ Send to local LLM (via Ollama) with prompt to extract keywords
5. ☐ Manual review: keep aircraft-specific terms, remove generic terms
6. ☐ Repeat with 3-5 different 100-message batches
7. ☐ Save master keyword list to `imageAsker/master_keywords.txt`
8. ☐ Document keyword curation process in `docs/notes/keyword_curation.md`

**Expected Keywords:** firewall, cowling, baffles, spar, canard, winglet, fuselage, avionics, panel, engine mount, landing gear, nose gear, fuel tank, etc.

**Test:** Keyword list contains 50-200 terms, all relevant to aircraft building
**Commit:** "Build master keyword list via LLM-assisted curation"

---

### Phase 4.2: LLM Keyword Tagger (TDD)
**Deliverable:** Function that tags messages with matching keywords

**Tasks:**
1. ☐ Create `imageAsker/tag_keywords.py` with ABOUTME
2. ☐ Create `imageAsker/tests/test_tag_keywords.py`
3. ☐ Write failing test: `test_tag_single_message()`
4. ☐ Write failing test: `test_handle_synonyms()` (e.g., "cowl" matches "cowling")
5. ☐ Write failing test: `test_handle_variations()` (e.g., "baffle" matches "baffles")
6. ☐ Write failing test: `test_no_false_positives()` (unrelated "spar" mention doesn't match)
7. ☐ Run tests - verify all fail
8. ☐ Implement `tag_message_with_keywords(strMessageText: str, lstKeywords: list[str]) -> list[str]`
   - Send message + keyword list to local LLM via Ollama
   - Prompt: "Which of these keywords (or close approximations) appear in this message?"
   - Parse LLM response to extract matched keywords
   - Return list of matched keywords
9. ☐ Run tests - verify all pass

**Prompt Template:**
```
You are analyzing a message from the Cozy Builders aircraft newsgroup.

Keywords: [firewall, cowling, baffles, spar, ...]

Message: [message text]

Which of these keywords (or their close approximations/synonyms) are discussed in this message?
Return ONLY the matching keywords as a comma-separated list.
```

**Test:** All tests pass, LLM correctly identifies keywords
**Commit:** "Implement LLM keyword tagger"

---

### Phase 4.3: Batch Tag All Messages (TDD)
**Deliverable:** Tag all messages with keywords and save to index

**Tasks:**
1. ☐ Write failing test: `test_tag_batch_of_messages()`
2. ☐ Write failing test: `test_save_keyword_index()`
3. ☐ Write failing test: `test_resume_from_partial_completion()`
4. ☐ Run tests - verify all fail
5. ☐ Implement `tag_all_messages(strMessagesDir: str, lstKeywords: list[str], strOutputFile: str) -> dict`
   - Load all message markdown files
   - For each message, call `tag_message_with_keywords()`
   - Build keyword index: `{messageID: [keyword1, keyword2, ...]}`
   - Save progress every 50 messages (crash recovery)
   - Add progress bar (tqdm)
6. ☐ Run tests - verify all pass

**Output Format (message_keywords.json):**
```json
{
  "A1NtxlDfY4c": ["firewall", "baffles", "engine mount"],
  "a42YFDFx8WY": ["cowling", "panel", "landing gear"]
}
```

**Test:** All tests pass
**Commit:** "Implement batch keyword tagging with progress tracking"

---

### Phase 4.4: Tag Messages from A/ Directory
**Deliverable:** Keyword index for A/ directory messages

**Tasks:**
1. ☐ Create `imageAsker/tag_messages_cli.py` script
2. ☐ Add command-line arguments:
   - `--messages` (path to messages directory)
   - `--keywords` (path to master_keywords.txt)
   - `--output` (path for message_keywords.json)
   - `--limit` (for testing, default None)
3. ☐ Test on 10 messages first with --limit 10
4. ☐ Review 10-message results manually - are keyword matches accurate?
5. ☐ Run on full A/ directory (~325 messages, estimate 10-15 minutes)
6. ☐ Review keyword index for quality
7. ☐ Document results in `docs/notes/phase4_results.md`:
   - Processing time
   - Keywords per message (average)
   - Spot-check 10 messages for accuracy

**Usage:**
```bash
python imageAsker/tag_messages_cli.py \
  --messages data/msgs_md/A \
  --keywords imageAsker/master_keywords.txt \
  --output data/message_keywords.json \
  --limit 10
```

**Test:** Keyword index created, spot-checks show accurate tagging
**Commit:** "Tag A/ directory messages with keywords"

---

### Phase 4.5: Validate Phase 4 Results
**Deliverable:** Assessment of keyword tagging quality

**Tasks:**
1. ☐ Manual review of 20 random messages:
   - Are assigned keywords accurate?
   - Any false positives (keywords that don't match)?
   - Any false negatives (obvious keywords missed)?
2. ☐ Check keyword distribution:
   - Which keywords are most common?
   - Are there any keywords that never match? (prune from master list)
3. ☐ Test a few searches manually:
   - Find all messages tagged with "firewall"
   - Find all messages tagged with "cowling"
   - Do results make sense?
4. ☐ Document assessment in `docs/notes/phase4_results.md`
5. ☐ If quality is poor, iterate on prompt or keyword list

**Test:** Keyword tagging achieves >80% accuracy on manual review
**Commit:** "Complete Phase 4: LLM keyword tagging validated"

---

## Phase 5: Keyword-Based Query Interface

**Goal:** Simple query interface using keyword index from Phase 4

**NOTE:** This phase builds on Phase 4's LLM keyword tagging. No ChromaDB integration needed - just simple keyword lookup.

### Phase 5.1: Query Function (TDD)
**Deliverable:** Function to search messages by keyword

**Tasks:**
1. ☐ Create `imageAsker/query_images.py` with ABOUTME
2. ☐ Create `imageAsker/tests/test_query.py`
3. ☐ Write failing test: `test_query_by_single_keyword()`
4. ☐ Write failing test: `test_query_by_multiple_keywords()` (AND logic)
5. ☐ Write failing test: `test_return_images_for_matching_messages()`
6. ☐ Write failing test: `test_handle_keyword_not_found()`
7. ☐ Run tests - verify all fail
8. ☐ Implement `query_images_by_keywords(lstQueryKeywords: list[str], dctKeywordIndex: dict, dctImageIndex: dict) -> list[dict]`
   - Find all messages tagged with any of the query keywords
   - Lookup images for those messages in image_index.json
   - Return list of image results with message metadata
9. ☐ Run tests - verify all pass

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

**Test:** All tests pass
**Commit:** "Implement keyword-based image query"

---

### Phase 5.2: CLI Query Tool
**Deliverable:** Command-line tool to search for images by keyword

**Tasks:**
1. ☐ Create `imageAsker/query_images_cli.py` script
2. ☐ Add command-line arguments:
   - Query keywords (positional args)
   - `--keywords-index` (path to message_keywords.json)
   - `--images-index` (path to image_index.json)
   - `--max-results` (default 50)
3. ☐ Display results:
   - Message subject and ID
   - Matched keywords
   - List of thumbnail paths
   - Total results count
4. ☐ Test with sample queries

**Usage:**
```bash
python imageAsker/query_images_cli.py firewall cowling \
  --keywords-index data/message_keywords.json \
  --images-index data/image_index.json
```

**Test:** Returns relevant images for test queries
**Commit:** "Add CLI tool for keyword-based image queries"

---

### Phase 5.3: Simple Thumbnail Viewer
**Deliverable:** HTML page to view thumbnail grid

**Tasks:**
1. ☐ Create `imageAsker/generate_thumbnail_page.py` script
2. ☐ Takes query results and generates static HTML file
3. ☐ HTML displays:
   - Thumbnail grid (3-4 columns)
   - Message subject/ID under each thumbnail
   - Click thumbnail to view full resolution
   - Matched keywords highlighted
4. ☐ Test with firewall query results

**Usage:**
```bash
python imageAsker/query_images_cli.py firewall --output results.json
python imageAsker/generate_thumbnail_page.py results.json --output results.html
```

**Test:** HTML page displays thumbnails correctly
**Commit:** "Add HTML thumbnail viewer"

---

### Phase 5.4: Validate Phase 5 Results
**Deliverable:** Assessment of query quality

**Tasks:**
1. ☐ Test queries:
   - "firewall" - expect firewall/bulkhead photos
   - "cowling" - expect cowling/engine cowl photos
   - "panel" - expect instrument panel/avionics photos
   - "landing gear" - expect landing gear photos
2. ☐ Assess results:
   - Are returned images relevant?
   - Any false positives?
   - Any obvious missing results?
3. ☐ Compare to manual search (grep through messages)
4. ☐ Document in `docs/notes/phase5_results.md`:
   - Query examples and results
   - Precision/recall estimates
   - User experience assessment
5. ☐ Get Tom's feedback on query quality

**Test:** Queries return relevant images, system is usable
**Commit:** "Complete Phase 5: Keyword-based query interface validated"

---

## Phase 6: Web Interface (Future Enhancement)

**Goal:** Web-based interface for image queries and thumbnail browsing

**Note:** This phase is out of scope for initial implementation. To be planned later based on CLI experience.

**Potential Components:**
- Flask/FastAPI backend
- Simple HTML/CSS/JS frontend
- Thumbnail grid display
- Click to view full resolution
- Link to original message context
- Search box for queries

---

## Testing Strategy

### Unit Tests
- All core functions have unit tests
- Use mocks for HTTP requests (download tests)
- Use test fixtures for file processing
- Aim for >80% code coverage

### Integration Tests
- Test end-to-end flow for small dataset
- Verify file operations (read/write/exists)
- Verify JSON serialization
- Test error handling paths

### Manual Testing
- Spot-check extracted URLs
- Verify downloaded images visually
- Test queries for relevance
- Check thumbnail quality

### Acceptance Tests
Each phase has clear acceptance criteria that must be met before proceeding to next phase.

---

## Development Environment

### Python Version
- Python 3.9+ (match existing project environment)

### Dependencies
```
# imageGetter/requirements.txt
requests>=2.31.0
Pillow>=10.0.0
tqdm>=4.65.0  # Progress bars

# imageAsker/requirements.txt
# (will reuse existing asker dependencies)
```

### Testing Dependencies
```
# tests/requirements.txt (or add to main requirements)
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1
```

---

## Rollback Strategy

If any phase fails or reveals major issues:

1. **Phase 1-3 Issues:** Iterate on current phase, adjust filters/logic
2. **Phase 4 Issues:** May need to add metadata extraction or adjust RAG query
3. **Phase 5 Issues:** Can halt scale-up and continue using A/ directory for testing
4. **Architecture Issues:** Escalate to Architect for design revision

All phases use git commits, so can revert to last working state.

---

## Success Metrics

**Phase 1:** 50+ image URLs extracted from A/ directory
**Phase 2:** >75% download success rate
**Phase 3:** 100% thumbnail generation for downloaded images
**Phase 4:** Query "firewall" returns relevant images
**Phase 5:** Full corpus processed with >60% overall success rate

---

## Timeline Estimate (for Programmer reference)

- Phase 1: 2-3 sessions (8-12 hours)
- Phase 2: 2-3 sessions (8-12 hours)
- Phase 3: 1-2 sessions (4-8 hours)
- Phase 4: 2-3 sessions (8-12 hours)
- Phase 5: 1-2 sessions (4-8 hours) + overnight processing

**Total:** ~10-15 development sessions + processing time

---

**Next Steps:**
- Create `architect_todo.md` to track architectural deliverables
- Create `programmer_todo.md` for Programmer to implement phases
- Set up initial module directories
- Begin Phase 1.1
