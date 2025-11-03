# Image Database Architecture

**Created:** 2025-11-01
**Last Updated:** 2025-11-02
**Status:** Phase 2 Implementation Complete

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
      "date": "Jul 23, 2012"
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
    "llm_keywords": ["firewall", "baffles", "cowling"]
  }
}
```

**Notes:**
- Top-level keys are message IDs
- `keywords` extracted from filename and message subject (Phase 1)
- `llm_keywords` added by LLM tagger from master keyword list (Phase 4)
- `local_filename` uses normalized format: `{messageID}_part{X}_{Y}_{filename}`

### 3. Module Structure

#### imageGetter/
Extracts image URLs from markdown files and downloads images.

**Components:**
- `extract_image_urls.py` - Parse msgs_md files, identify attachment URLs
- `download_images.py` - Download images with retry logic, rename to standardized format
- `generate_thumbnails.py` - Create 200x200px center-cropped thumbnails
- `llm_config.py` - LLM configuration (model, Ollama host, prompt template) - **Tom edits this**
- `llm_tagger.py` - KeywordTagger class using Ollama to tag messages
- `tag_messages.py` - Batch processor to add llm_keywords to image_index.json
- `tag_messages_cli.py` - CLI interface for keyword tagging
- `image_index.json` - Maintained index of all images

**Filtering Rules (as implemented):**
- **Include:** URLs matching `groups.google.com/group/cozy_builders/attach/`
- **Exclude:** Profile photos (lh3.googleusercontent.com)
- **Exclude via Blacklist:** ~400+ junk images filtered by filename:
  - Exact matches: graycol.gif, UFAC Salutation.jpg, emoticons, animated GIFs
  - Pattern matches: wlEmoticon-*.png, ~WRD*.jpg, ole*.bmp, hex-named files
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

## Implementation Phases

### Phase 1: Image URL Extraction (Test on A/ directory)
- Parse markdown files in data/msgs_md/A/
- Identify attachment URLs (filter out profiles/logos)
- Build initial image_index.json with URLs only
- **Deliverable:** image_index.json with ~50-100 image URLs from A/ directory

### Phase 2: Image Download (Test on A/ directory)
- Download images from extracted URLs
- Handle errors (404s, timeouts, rate limits)
- Save with standardized naming: {messageID}_part{N}.{ext}
- Update image_index.json with download status
- **Deliverable:** images/full/ populated with A/ directory images

### Phase 3: Thumbnail Generation (Test on A/ directory)
- Generate 200x200px center-cropped thumbnails
- Handle various image formats (JPEG, PNG, GIF)
- Save to images/thumbs/
- Update image_index.json with thumbnail status
- **Deliverable:** images/thumbs/ populated with thumbnails

### Phase 4: Query Interface (Test on A/ directory)
- CLI tool to query and display image results
- Integrate with existing asker/ RAG query
- Display thumbnails with message context
- **Deliverable:** Working CLI query tool

### Phase 5: Scale to Full Corpus
- Process all directories (B/, C/, ... Z/, etc.)
- Monitor disk space and download progress
- Handle edge cases discovered during testing
- **Deliverable:** Complete image database

### Phase 6: Web Interface (Future Enhancement)
- Simple web UI for thumbnail grid
- Click-to-view full resolution
- Link back to original message context
- **Deliverable:** Web-based image query tool

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

### Image Filtering
- **Profile photos:** Exclude URLs containing `googleusercontent.com`
- **Size filter:** Skip images < 10KB (likely icons/logos)
- **Attachment pattern:** Only process `groups.google.com/.../attach/` URLs
- **Manual review:** After A/ directory test, review results and refine filters

## Future Enhancements (Out of Scope for Initial Implementation)

1. **Multimodal Embeddings:** If text-based retrieval insufficient, add CLIP/LLaVA embeddings
2. **Image Classification:** Auto-tag images (firewall, cowling, panel, wing, etc.)
3. **Duplicate Detection:** Identify and merge duplicate images across messages
4. **Image Metadata:** Extract EXIF data for build progress tracking
5. **Zoom/Pan Interface:** Better image viewing experience in web UI

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

**Phase 1 Complete (A/ Directory Test):**
- ✓ Successfully extracted 217 image URLs from A/ directory (92 messages)
- ✓ Blacklist filtering removed ~400+ junk images
- ✓ Keywords extracted and indexed
- ✓ image_index.json created (76KB)

**Phase 2 Implementation Complete:**
- ✓ Dual-path download strategy implemented and tested
- ✓ Resume capability working
- ✓ Cookie extraction and management working
- ⏳ Production download run pending (waiting for Chrome debug mode testing)

**Phase 3-5 Pending:**
- ☐ Thumbnail generation (not started)
- ☐ Query interface (not started)
- ☐ Full corpus scaling (not started)

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Google Groups blocks scraping | Add rate limiting, user-agent, monitor for 429 errors |
| Many broken image links | Track success rate, acceptable if >60% valid |
| Insufficient disk space | Check space before Phase 5, estimate from Phase 1-3 |
| Text retrieval poor quality | Collect feedback, iterate on query approach, consider multimodal Phase 6 |
| Download takes too long | Implement parallel downloads, resume capability |

## Phase Revisions

### Phase 4 Implementation Details **[REVISED - 2025-11-03]**

**Scope Clarification:**
- Tagging only messages with images (~7k messages in image_index.json)
- NOT tagging full corpus (separate tool handles text-only search)
- Keywords stored IN image_index.json as new `llm_keywords` field

**Data Structure:**
```json
{
  "A1NtxlDfY4c": {
    "metadata": {...},
    "images": [...],
    "llm_keywords": ["firewall", "baffles", "cowling"]  // NEW FIELD
  }
}
```

**llm_keywords Field States:**
- `["firewall", "cowling"]` = tagged with matches
- `[]` = tagged but no keywords matched (valid state)
- Field missing = not yet tagged

**Command Line Interface:**
```bash
# Tag messages, limit to first 50 processed
python tag_messages.py data/image_index.json --limit 50

# Skip already-tagged (default behavior)
python tag_messages.py data/image_index.json

# Overwrite existing llm_keywords
python tag_messages.py data/image_index.json --overwrite

# Use custom keyword file
python tag_messages.py data/image_index.json --keywords custom_keywords.txt
```

**Processing Behavior:**
- Skip messages where `llm_keywords` exists and not empty (unless `--overwrite`)
- `--limit` counts processed messages (not skipped messages)
- Recursive directory processing (walks full corpus)

**Keyword Discovery Process:**
- Sample small batches (5 messages) for review
- `python build_keyword_list.py --sample 5 --output candidates.txt`
- Tom reviews and adds to keywords_seed.txt
- Iterate until keyword list stable

**Why This Design:**
- One source of truth (image_index.json contains all image metadata)
- Scope matches use case (image search tool, not text search)
- Simple query: load one file, filter by keyword
- Incremental processing with resume capability

**LLM Tagging Architecture:**
- **Configuration:** llm_config.py contains model name, Ollama host, and prompt template
  - Tom can edit model (default: gemma3:1b) and prompt without touching code
  - Follows existing pattern from embedder/f_llm.py
- **KeywordTagger Class:** Encapsulates Ollama interaction
  - `__init__(ollamahost)` - Creates ollama.Client
  - `tag_message(message_text, keywords, model)` - Tags single message
  - Graceful error handling: returns [] on error, logs issue, doesn't crash
  - Response validation: ensures LLM only returns keywords from master list
- **Batch Processing:** tag_messages.py
  - Loads image_index.json and keywords_seed.txt
  - Skips messages with existing llm_keywords (unless --overwrite)
  - Auto-saves every 50 messages (crash recovery)
  - Handles LLM errors per-message (log and continue)
- **CLI Interface:** tag_messages_cli.py with --limit, --overwrite, --keywords, --model flags

### Phase 4-5 Revision (2025-11-02)

**Original Plan:** ChromaDB semantic search with metadata filtering
**Revised Plan:** LLM keyword tagging + simple keyword lookup

**Reason for Change:**
- Tom proposed: Use LLM to tag messages with curated keywords at index-time
- Provides semantic understanding (LLM handles synonyms) without query-time complexity
- Simpler, more interpretable, faster queries
- Debuggable - can review keyword assignments

**New Phase 4:** Build keyword list (LLM-assisted), tag messages with keywords in image_index.json
**New Phase 5:** Keyword-based query interface with HTML viewer

**Old Phase 5 (Scale to Full Corpus) removed** - already scaling organically

---

## Open Questions

1. Keyword list size: 50-200 terms optimal? (Phase 4 will determine)
2. Should we store original message markdown path in image_index.json for reference?
3. Do we need image versioning if re-downloading improves quality?
4. Web interface framework preference (Flask, FastAPI, static HTML)?

---

**Next Steps:**
See `image_database_implementation_plan.md` for detailed incremental implementation plan.
