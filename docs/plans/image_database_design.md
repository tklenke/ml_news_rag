# Image Database Architecture

**Created:** 2025-11-01
**Last Updated:** 2025-11-05
**Status:** Phases 1-4b Complete, Phase 5 Pending

## Overview

Create a searchable database of build photos from the Cozy Builders Google Groups newsgroup. Users can query for images by topic (e.g., "show me firewall pictures", "oil cooler installations") and view relevant images through a thumbnail interface.

## Design Philosophy

**Start Simple, Iterate Up:**
- Leverage existing text-based RAG system rather than introducing multimodal embeddings
- Message text provides rich context for image content
- Incremental development with testing on subset before full deployment
- YAGNI: Build only what's needed for initial functionality

## Architecture Components

### 1. Data Storage

```
data/
  images/
    full/                              # Full-resolution images
      A1NtxlDfY4c_part0.1.jpg
      A1NtxlDfY4c_part0.2.jpg
      a42YFDFx8WY_part0.1.jpeg
    thumbs/                            # 200x200px thumbnails (center crop)
      A1NtxlDfY4c_part0.1_thumb.jpg
      A1NtxlDfY4c_part0.2_thumb.jpg
  image_index.json                     # Message ID -> image mappings
```

### 2. Image Index Schema

**Actual Implementation (as built):**

```json
{
  "A1NtxlDfY4c": {
    "metadata": {
      "message_id": "A1NtxlDfY4c",
      "subject": "Re: [c-a] Van's baffles for Long-ez",
      "author": "krw...@gmail.com",
      "date": "Jul 23, 2012",
      "message_md": "A/A1NtxlDfY4c.md"
    },
    "images": [
      {
        "url": "https://groups.google.com/group/cozy_builders/attach/.../image.jpg?part=0.1",
        "part": "0.1",
        "filename": "image.jpg",
        "local_filename": "A1NtxlDfY4c_part0_1_image.jpg",
        "keywords": ["landing", "light", "van", "baffles"]
      }
    ],
    "keywords": ["firewall", "baffles", "cowling", "engine"]
  }
}
```

**Notes:**
- Top-level keys are message IDs
- `images[].keywords` extracted from image filename (Phase 1)
- `keywords` (message-level) added by taggers from master keyword list (Phase 4b)
  - Can be populated by LLM tagger (semantic matching) or search tagger (fast keyword matching with stemming)
  - Empty list `[]` = tagged but no matches (valid state)
  - Field missing = not yet tagged
- `message_md` field stores path to markdown file for full message body access
- `local_filename` uses normalized format: `{messageID}_part{X}_{Y}_{filename}`

### 3. Module Structure

#### imageGetter/
Extracts image URLs from markdown files, downloads images, and manages image database.

**URL Extraction & Download:**
- `extract_image_urls.py` - Parse msgs_md files, identify attachment URLs, extract keywords from filenames
- `download_images_cli.py` - Download images with Selenium/cookie-based approach
- `generate_thumbnails_cli.py` - Create 200x200px center-cropped thumbnails

**Keyword Tagging:**
- `aircraft_keywords.txt` - Master keyword list (557 keywords, curated with Claude Opus)
- `llm_config.py` - LLM configuration (model, Ollama host, prompts) - **Tom edits this**
- `llm_tagger.py` - KeywordTagger class using Ollama (semantic matching, handles synonyms)
- `llm_tag_messages.py` - Batch processor for LLM-based tagging
- `llm_tag_messages_cli.py` - CLI interface for LLM tagging (slow but semantic)
- `search_tagger.py` - SearchTagger class using stemming (fast, deterministic keyword matching)
- `search_tag_messages.py` - Batch processor for search-based tagging
- `search_tag_messages_cli.py` - CLI interface for search tagging (fast, recommended default)

**Image Curation:**
- `dedupe_images_cli.py` - Remove duplicate images by file size
- `analyze_tag_statistics.py` - Generate keyword statistics and interactive HTML review pages
- `remove_images_cli.py` - Batch remove images based on exported removal lists

**Data:**
- `image_index.json` - Master index of all images (message-centric structure)
- `input/` - Test data and work-in-progress files (gitignored)

**Filtering Rules (as implemented):**
- **Include:** URLs matching `groups.google.com/group/cozy_builders/attach/`
- **Exclude:** Profile photos (lh3.googleusercontent.com)
- **Exclude via Blacklist:** ~400+ junk images filtered by filename:
  - Exact matches: graycol.gif, UFAC Salutation.jpg, emoticons, animated GIFs
  - Pattern matches: wlEmoticon-*.png, ~WRD*.jpg, ole*.bmp, hex-named files
- **Note:** Attachment-only filtering removed (commit 5312ed1) - too many false positives
- **Note:** Size filtering removed - blacklist approach more effective

#### imageAsker/
Query interface for image retrieval.

**Components:**
- `query_images.py` - Query text RAG, return images for matching messages
- Web/CLI interface for displaying thumbnails
- Full-resolution image viewer

### 4. Query Flow

```
User Query: "show me firewall pictures"
    ↓
[Existing RAG System]
Query text embeddings in ChromaDB
    ↓
[Return Matching Message IDs]
["A1NtxlDfY4c", "a_XD_FslP1w", ...]
    ↓
[Image Index Lookup]
Load image_index.json
Filter to messages with images
    ↓
[Thumbnail Display]
Show 50-100 thumbnails in grid
Display message subject/date for context
    ↓
[User Interaction]
Click thumbnail → view full resolution
Click message link → view original message
```

### 5. Technology Stack

**Existing Infrastructure:**
- ChromaDB: Already embedding message text
- Ollama: Not needed for this approach (text-only embeddings)
- Python environment: PIL/Pillow for image processing

**New Dependencies:**
- `Pillow` - Image processing (thumbnails, format conversion)
- `requests` - HTTP downloads with retry
- Standard library: `json`, `pathlib`, `re`

### 6. Data Flow

```
[msgGetter]              [imageGetter]           [embedder]           [imageAsker]
    ↓                         ↓                       ↓                     ↓
msgs/ (HTML)          msgs_md/ (Markdown)     ChromaDB (text)      User Query
    ↓                         ↓                   embeddings              ↓
msgs_md/ (MD) ----→   Extract Image URLs           ↓                 Query ChromaDB
                              ↓                     ↓                      ↓
                      Download Images          [Existing]          Message IDs
                              ↓                                            ↓
                      images/full/                              Lookup image_index.json
                              ↓                                            ↓
                      Generate Thumbs                           Display Thumbnails
                              ↓
                      images/thumbs/
                              ↓
                      Update image_index.json
```

## Implementation Status

### Phase 1: Image URL Extraction ✅ COMPLETE
**Completed:** Extract image URLs from markdown files and build index
- Parse markdown files recursively from data/msgs_md/
- Extract keywords from both image filename and message subject
- Filter junk images via blacklist (~400+ patterns)
- Message-centric index structure with metadata
- **Result:** Working URL extraction with keyword indexing

### Phase 2: Image Download ✅ COMPLETE
**Completed:** Download images from Google Groups using Selenium
- Dual-path download: direct binary and HTML wrapper
- Cookie-based authentication via Selenium debug mode
- Resume capability (skip existing files)
- Standardized filename format
- **Result:** Images successfully downloaded to data/images/full/

### Phase 3: Thumbnail Generation ✅ COMPLETE
**Completed:** Generate 200x200px center-cropped thumbnails
- PIL-based thumbnail generation
- Center crop for consistent appearance
- Handles JPEG, PNG, GIF formats
- CLI tool with `--force` option to regenerate
- **Result:** Thumbnails in data/images/thumbs/

### Phase 4a: Build Master Keywords ✅ COMPLETE
**Completed:** Curated master keyword list
- Started with 110 seed keywords
- Iterative LLM-assisted curation using Claude Opus
- Tom reviewed and refined list
- **Result:** aircraft_keywords.txt with 557 curated keywords

### Phase 4b: Keyword Tagging ✅ COMPLETE
**Completed:** Two parallel tagging approaches implemented
1. **LLM Tagger (llm_tag_messages_cli.py):**
   - Semantic matching via Ollama
   - Handles synonyms and context
   - Slow (~30s per message) but accurate

2. **Search Tagger (search_tag_messages_cli.py) - RECOMMENDED:**
   - Fast keyword matching with stemming
   - Reads full message body from markdown files
   - Vocabulary restriction (filters to 557 allowed keywords)
   - Merge or replace mode for message-level keywords
   - Invalid keyword filtering (e.g., "cozy" filtered at source)
   - Default cleaning of existing invalid keywords
   - ~25 keywords per message average

**Image Curation Tools:**
- `dedupe_images_cli.py` - Remove duplicates by file size
- `analyze_tag_statistics.py` - Interactive HTML review with thumbnails, checkboxes, export removal lists
- `remove_images_cli.py` - Batch remove images from exported lists

**CLI Standardization:**
- All tools follow `SOURCE [DEST] [options]` pattern
- Non-destructive by default
- Smart default output filenames
- **Result:** Comprehensive tagging and curation workflow

### Phase 5: Static Site Generation ⏳ PENDING
**Approach:** Generate static HTML site for browsing tagged images

**Site Structure:**
- `index.html` - Main entry point
  - Link to "All Images" (chronological, newest first)
  - Alphabetical keyword list with image counts
- `all/page1.html`, `all/page2.html`, ... - All images chronologically
  - Sorted by date descending (newest first)
  - Year headers (e.g., "2024 (345 images)", "2023 (512 images)")
  - 6-column thumbnail grid
  - First/Previous/Next/Last navigation (top and bottom)
- `keywords/firewall_page1.html`, etc. - Keyword-specific pages
  - Same format as "all images" pages
  - Shows only images tagged with that keyword

**Thumbnail Display:**
Each thumbnail shows:
- Image thumbnail (clickable to full resolution)
- Message subject
- Message ID
- List of keywords for that message
- Same format as `analyze_tag_statistics.py` output

**Implementation Notes:**
- Static files only (no backend, no JavaScript)
- Read-only view (no interactive checkboxes/export features)
- Code adapted from `analyze_tag_statistics.py` (not shared, copied as starting point)
- Simple navigation: breadcrumbs and pagination links

### Phase 6: Web Interface 📋 DEFERRED
**Status:** Not needed - Phase 5 static site sufficient for initial use
- Can revisit if static site limitations become problematic

## Technical Considerations

### Image Storage
- **Estimated count:** ~10,000-50,000 images (unknown until extraction)
- **Estimated disk usage:** 5-20 GB full images, 500MB-2GB thumbnails
- **Location:** data/images/ (same disk as existing corpus)

### Download Strategy
- **Rate limiting:** Add delays between downloads to respect Google Groups servers
- **Retry logic:** 3 retries with exponential backoff for failed downloads
- **Resume capability:** Track download status in image_index.json
- **User-Agent:** Identify as legitimate scraper

### Error Handling
- **Missing images:** Some URLs may be broken (old posts, deleted images)
- **Format issues:** Handle JPEG, PNG, GIF, possibly BMP/TIFF
- **Corrupt downloads:** Validate image can be opened before marking complete
- **Disk space:** Check available space before download batches

### Keyword Tagging Approach
**Two Parallel Implementations:**

1. **Search Tagger (Recommended Default):**
   - Fast: Processes entire dataset in seconds
   - Stemming: Matches plurals and variations (e.g., "firewall" matches "firewalls", "installing")
   - Deterministic: Same input always produces same output
   - Full message text: Reads complete message body from markdown files
   - Vocabulary enforcement: Restricts keywords to allowed list (557 keywords)
   - Trade-off: No synonym matching, misses context-dependent terms

2. **LLM Tagger (Semantic Alternative):**
   - Semantic: Understands synonyms and context
   - Accurate: 90-95% precision
   - Slow: ~30s per message = ~10 hours for 1200 messages
   - Can timeout or error
   - Trade-off: Time and reliability vs. accuracy

**Keyword Merging Strategy:**
- Image-level keywords: Extracted from filename (Phase 1)
- Message-level keywords: Added by taggers (Phase 4b)
- Default behavior: Replace existing message keywords with newly searched
- Merge mode: Use `--keep-existing-keywords` to merge instead
- Invalid filtering: Removes "cozy" and other noise terms at source

**Vocabulary Restriction:**
- All keywords filtered against aircraft_keywords.txt (557 allowed terms)
- Stemming applied to both message text and keywords for fuzzy matching
- Result: 472 unique keywords in use (subset of 557 allowed)
- ~25 keywords per message average

## Future Enhancements

### Near-Term (Phase 5-6)
1. **Query Interface:** Keyword-based search with HTML viewer
2. **Web Interface:** Flask/FastAPI-based query tool with thumbnail grid

### Long-Term (Post Phase 6)
1. **Multimodal Embeddings:** If text-based retrieval insufficient, add CLIP/LLaVA embeddings
2. **Advanced Duplicate Detection:** Perceptual hashing for near-duplicate images
3. **Image Metadata:** Extract EXIF data for build progress tracking
4. **Image Classification:** Auto-categorize by component type
5. **Zoom/Pan Interface:** Better image viewing experience

## Design Decisions

### Why Not Multimodal Embeddings Initially?
- Message text provides rich context ("here's my firewall build")
- Simpler to implement and debug
- Leverages existing RAG infrastructure
- Can add later if retrieval quality insufficient

### Why Center Crop for Thumbnails?
- Most build photos have subject centered
- Faster than "smart crop" algorithms
- Consistent thumbnail appearance
- Can refine later based on user feedback

### Why Separate Full/Thumbs Directories?
- Cleaner organization
- Easy to regenerate thumbnails if needed
- Different backup/archiving strategies possible
- Faster thumbnail serving in web interface

### Why JSON Index vs Database?
- Simple, human-readable format
- No additional dependencies
- Easy to version control and debug
- Can migrate to SQLite later if needed

## Implementation Details (Phase 1-2 Complete)

### URL Extraction Enhancements
**Keyword Extraction:**
- Extract keywords from both filename and message subject line
- Filter stopwords and noise terms (img, photo, numbers, hex codes)
- Merge subject keywords with filename keywords for better searchability
- Example keywords: "landing", "light", "firewall", "cowling", "wing"

**Blacklist Filtering:**
- ~400+ junk images filtered during extraction (not download)
- Exact filename blacklist: graycol.gif, emoticons, animated GIFs
- Pattern blacklist: wlEmoticon-*.png, ~WRD*.jpg, ole*.bmp
- More effective than size-based filtering

**CLI Enhancements:**
- Positional arguments: `SOURCE DEST` (not --input/--output)
- Auto-generated timestamped output files
- Duplicate filename tracking and statistics
- Keyword frequency statistics

### Download Strategy (Dual-Path Approach)
**Google Groups returns two response types:**
- **Direct binary (56%):** URLs without &view=1 parameter
  - Chrome downloads to Downloads folder (can't capture in page_source)
  - Solution: Use requests.get() with extracted cookies from Selenium
- **HTML wrapper (44%):** URLs with &view=1 parameter
  - Returns HTML page with embedded <img> tag
  - Solution: Use Selenium to parse HTML and extract real image URL

**Cookie Management:**
- Extract cookies once at batch start (not per-image)
- Avoid "no execution context" errors
- Fallback strategy: try current page, navigate if needed

**Resume Capability:**
- Skip files that already exist locally
- Enables crash recovery and incremental processing

**Size Filtering Removed:**
- Originally planned HEAD requests to check Content-Length
- Removed in Phase 2.8.2 - blacklist filtering makes it redundant
- Simplifies code and speeds up downloads

### Index Format Evolution
**Initial design:** Flat list of images with metadata
**As implemented:** Message-centric structure
- Top-level keys are message IDs
- Metadata nested under each message
- Keywords added for searchability
- local_filename tracks normalized filenames

## Success Criteria

**Phases 1-4 Complete:** ✅
- ✓ URL extraction with keyword indexing working
- ✓ Image download pipeline functional
- ✓ Thumbnail generation complete
- ✓ Master keyword list curated (557 keywords)
- ✓ Two tagging approaches implemented (LLM and search)
- ✓ Image curation tools complete (dedupe, analyze, remove)
- ✓ CLI tools standardized and tested (110+ passing tests)
- ✓ Full message body reading for accurate tagging
- ✓ Vocabulary restriction preventing keyword sprawl

**Phase 5 Pending:** ⏳
- ☐ Keyword-based query function
- ☐ CLI query tool
- ☐ HTML thumbnail viewer
- ☐ Query quality validation

## Risks and Status

| Risk | Status | Mitigation |
|------|--------|-----------|
| Google Groups blocks scraping | ✅ Resolved | Rate limiting and Selenium authentication working |
| Many broken image links | ✅ Acceptable | Resume capability handles failures gracefully |
| Insufficient disk space | ✅ Managed | Monitoring disk usage, thumbnails reduce space needs |
| Text retrieval poor quality | ⏳ TBD | Will validate in Phase 5, can add multimodal if needed |
| Keyword sprawl (too many keywords) | ✅ Resolved | Vocabulary restriction limits to 557 allowed keywords |

## Key Design Revisions

### Phase 4: Two-Phase Keyword Approach (Nov 2025)
**Original Plan:** ChromaDB semantic search with metadata filtering
**Revised Plan:** LLM keyword tagging + simple keyword lookup

**Rationale:**
- Index-time tagging provides semantic understanding without query-time complexity
- Curated vocabulary (557 keywords) prevents keyword sprawl
- Two implementations: LLM tagger (semantic, slow) and search tagger (fast, recommended)
- Simpler, more interpretable, faster queries
- Debuggable - can review keyword assignments

**Result:** Phase 4 split into:
- Phase 4a: Build master keyword list (curated with Tom)
- Phase 4b: Tag messages with keywords from master list

### Field Name Standardization (Nov 2025)
**Change:** `llm_keywords` renamed to `keywords`
**Rationale:** Field is populated by both LLM and search taggers, not LLM-specific

### Chapter Categorization (Nov 2025)
**Attempted:** Cozy IV build chapter categorization (1-25)
**Status:** Implemented then removed (commits 48c2e91, 6450e90)
**Reason:** Not working correctly, removed from codebase

### Message Text Extraction (Nov 2025)
**Enhancement:** Full message body reading from markdown files
**Rationale:** Subject-only gave ~2 keywords/message, full body gives ~25 keywords/message
**Implementation:** Reads from data/msgs_md/ with fallback for missing files

---

## Open Questions

1. Is vocabulary size (557 keywords) sufficient for coverage?
2. Should we add multimodal embeddings if Phase 5 query quality is poor?
3. Web interface framework preference (Flask, FastAPI, static HTML)?
4. Should we track query analytics to improve keyword list?

---

**Detailed Implementation Plan:** See archived `image_database_implementation_plan.md` for original phase breakdown
