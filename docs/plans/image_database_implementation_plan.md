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

## Phase 4: Query Interface

**Goal:** Query interface that returns images based on text search

**IMPORTANT NOTE:** Phase 4 uses a metadata update approach (adding `has_images: True` to existing ChromaDB records) rather than creating a separate collection or re-embedding. This is simpler and reuses existing embeddings. **However, this approach may not work as expected** - ChromaDB metadata filtering behavior with existing collections needs validation. If filtering doesn't work well or retrieval quality is poor, we may need to re-embed the subset of the corpus that has images into a separate collection. Document findings in Phase 4.6 validation.

### Phase 4.1: Create imageAsker Module
**Deliverable:** Module structure for image queries

**Tasks:**
1. ☐ Create `imageAsker/` directory
2. ☐ Create `imageAsker/README.md`
3. ☐ Create `imageAsker/query_images.py`
4. ☐ Create `imageAsker/tests/` directory
5. ☐ Create `imageAsker/tests/test_query.py`
6. ☐ Add ABOUTME comments

**Test:** Module structure exists
**Commit:** "Create imageAsker module structure"

---

### Phase 4.2: Image Index Loading (TDD)
**Deliverable:** Load and query image_index.json

**Tasks:**
1. ☐ Write failing test: `test_load_image_index()`
2. ☐ Write failing test: `test_get_images_for_message_id()`
3. ☐ Write failing test: `test_get_images_for_multiple_message_ids()`
4. ☐ Write failing test: `test_filter_messages_with_images()`
5. ☐ Run tests - verify all fail
6. ☐ Implement `load_image_index(strPath: str) -> dict`
7. ☐ Implement `get_images_for_messages(lstMessageIds: list[str], dctImageIndex: dict) -> list[dict]`
8. ☐ Run tests - verify all pass

**Test:** All tests pass
**Commit:** "Implement image index loading and lookup"

---

### Phase 4.3: Update ChromaDB Metadata for Image Messages
**Deliverable:** Add "has_images" flag to ChromaDB records for messages with images

**Background:**
Existing ChromaDB structure stores message chunks with metadata: `{"source": "messageID"}`.
Each message has multiple chunks (e.g., "A1NtxlDfY4c0", "A1NtxlDfY4c1", etc.).
We'll update ALL chunks for messages that have images to add `"has_images": True`.

**Tasks:**
1. ☐ Review existing embedder code (`embedder/f_embed.py`) to understand ChromaDB structure
2. ☐ Write failing test: `test_get_all_chunks_for_message_id()`
3. ☐ Write failing test: `test_update_chunk_metadata()`
4. ☐ Write failing test: `test_update_all_message_chunks_with_image_flag()`
5. ☐ Run tests - verify all fail
6. ☐ Implement `get_chunks_for_message(strMessageId: str, chromaCollection) -> list[str]`
   - Query ChromaDB by metadata: `where={"source": "messageID"}`
   - Return list of chunk IDs
7. ☐ Implement `update_metadata_for_chunks(lstChunkIds: list[str], dctNewMetadata: dict, chromaCollection) -> bool`
   - Update metadata for list of chunk IDs
   - Add/merge `has_images: True` to existing metadata
8. ☐ Implement `add_image_flags_to_chromadb(dctImageIndex: dict, chromaCollection) -> dict`
   - For each message_id in image_index.json
   - Get all chunks for that message
   - Update their metadata with `has_images: True`
   - Log progress and statistics
9. ☐ Run tests - verify all pass
10. ☐ Create CLI script to update existing ChromaDB collection
11. ☐ Test on A/ directory messages

**Test:** All chunks for image messages have has_images=True metadata
**Commit:** "Update ChromaDB metadata with image flags"

**Note:** If ChromaDB doesn't support metadata updates well, may need to re-embed messages with updated metadata.

---

### Phase 4.4: Query ChromaDB with Image Filter (TDD)
**Deliverable:** Query function that filters to only messages with images

**Tasks:**
1. ☐ Write failing test: `test_query_chromadb_with_image_filter()`
2. ☐ Write failing test: `test_extract_message_ids_from_results()`
3. ☐ Write failing test: `test_deduplicate_message_ids()` (multiple chunks per message)
4. ☐ Write failing test: `test_query_returns_no_results_when_no_images()`
5. ☐ Run tests - verify all fail
6. ☐ Implement `query_images(strQueryText: str, intMaxResults: int = 50) -> list[dict]`
   - Get query embedding using ollama.embed()
   - Query ChromaDB with: `collection.query(query_embeddings=..., n_results=..., where={"has_images": True})`
   - Extract unique message IDs from results (deduplicate chunks from same message)
   - Lookup images in image_index.json for those message IDs
   - Return image data with message context and relevance scores
7. ☐ Run tests - verify all pass

**Output Format:**
```python
[
  {
    "message_id": "A1NtxlDfY4c",
    "subject": "Re: [c-a] Van's baffles...",
    "thumbnail_path": "data/images/thumbs/A1NtxlDfY4c_part0.1_thumb.jpg",
    "full_path": "data/images/full/A1NtxlDfY4c_part0.1.jpg",
    "relevance_score": 0.87
  }
]
```

**Test:** All tests pass, queries filter correctly
**Commit:** "Implement image query with ChromaDB metadata filter"

---

### Phase 4.5: CLI Image Query Tool
**Deliverable:** Command-line tool to query and display image results

**Tasks:**
1. ☐ Create `imageAsker/query_images_cli.py` script with ABOUTME
2. ☐ Add command-line arguments:
   - Query text (positional arg)
   - `--max-results` (default 50)
   - `--index` (path to image_index.json)
   - `--collection` (ChromaDB collection name, default from existing config)
3. ☐ Display results:
   - List thumbnail paths
   - Show message subject and ID
   - Show relevance score
4. ☐ Test with queries:
   - "firewall"
   - "oil cooler"
   - "panel"
   - "wing"

**Usage:**
```bash
python imageAsker/query_images_cli.py "firewall installation" --max-results 20
```

**Test:** Returns relevant images for test queries
**Commit:** "Add CLI tool for image queries"

---

### Phase 4.6: Simple Thumbnail Viewer (Optional)
**Deliverable:** Script to display thumbnails in terminal or simple GUI

**Tasks:**
1. ☐ Decide on approach:
   - Option A: Terminal (use ASCII art or similar)
   - Option B: Simple GUI (tkinter, pygame)
   - Option C: Generate HTML file to open in browser
2. ☐ Implement chosen approach
3. ☐ Test with A/ directory results

**Note:** HTML option is simplest and most practical

**Test:** Can view thumbnail grid from query results
**Commit:** "Add thumbnail viewer for query results"

---

### Phase 4.7: Validate Phase 4 Results
**Deliverable:** Working query interface tested on A/ directory with assessment of metadata approach

**Tasks:**
1. ☐ Verify metadata updates worked:
   - Check that has_images flag exists on updated chunks
   - Verify query with `where={"has_images": True}` returns only image messages
   - Compare result count to expected (number of messages with images)
2. ☐ Test queries on A/ directory:
   - "engine" - expect engine/installation photos
   - "panel" - expect panel/avionics photos
   - "cowling" - expect cowling photos
   - "firewall" - expect firewall photos
3. ☐ Assess retrieval quality:
   - Are results relevant to query?
   - Do images match what was requested?
   - Any false positives (irrelevant images)?
   - Any false negatives (missing relevant images)?
4. ☐ Document results in `docs/notes/phase4_results.md`:
   - Query examples and results
   - Retrieval quality assessment
   - Metadata filtering effectiveness
   - **Decision: Does metadata approach work well enough?**
   - If NO: Plan to re-embed image messages into separate collection
5. ☐ Collect feedback from Tom on retrieval quality
6. ☐ Iterate on query logic if needed OR plan Phase 4B (re-embedding)

**Test:** Queries return relevant images, system is usable, metadata approach validated
**Commit:** "Complete Phase 4: Image query interface on A/ directory"

**DECISION POINT:** If metadata filtering doesn't work well:
- Create Phase 4B to re-embed messages with images into separate collection
- Use existing embedder code with modified metadata
- Query separate collection instead of filtering main collection

---

## Phase 5: Scale to Full Corpus

**Goal:** Process all directories (B/ through Z/) and create complete image database

### Phase 5.1: Estimate Full Corpus Scale
**Deliverable:** Projections for full corpus processing

**Tasks:**
1. ☐ Calculate statistics from A/ directory:
   - Images per markdown file (average)
   - Download success rate
   - Disk space per 100 images
2. ☐ Count total markdown files across all directories
3. ☐ Project for full corpus:
   - Estimated total images
   - Estimated disk space needed
   - Estimated download time
4. ☐ Document in `docs/notes/phase5_projections.md`
5. ☐ Check available disk space

**Test:** Have clear estimates before proceeding
**Commit:** "Document full corpus projections"

---

### Phase 5.2: Process All Directories
**Deliverable:** Complete image database for all directories

**Tasks:**
1. ☐ Run URL extraction on all directories (B/ through Z/)
2. ☐ Merge results into single image_index.json
3. ☐ Run image download (consider running overnight)
4. ☐ Monitor progress and handle errors
5. ☐ Run thumbnail generation
6. ☐ Verify final image_index.json

**Test:** All directories processed, statistics match projections
**Commit:** "Complete Phase 5: Full corpus image database"

---

### Phase 5.3: Final Validation and Documentation
**Deliverable:** Complete, documented image database

**Tasks:**
1. ☐ Generate final statistics:
   - Total markdown files processed
   - Total images found
   - Total images downloaded successfully
   - Download success rate
   - Total disk space used
   - Common failure reasons
2. ☐ Test queries on full database
3. ☐ Document in `docs/notes/phase5_final_results.md`
4. ☐ Update `docs/project_info.md` with image database details
5. ☐ Create user guide for image query system

**Test:** System fully functional on complete corpus
**Commit:** "Complete Phase 5: Full image database operational"

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
