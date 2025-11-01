# Image Database Architecture

**Created:** 2025-11-01
**Status:** Design Phase

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

```json
{
  "messageID": "A1NtxlDfY4c",
  "subject": "Re: [c-a] Van's baffles for Long-ez",
  "author": "krw...@gmail.com",
  "date": "2012-07-23",
  "images": [
    {
      "filename": "A1NtxlDfY4c_part0.1.jpg",
      "url": "https://groups.google.com/group/cozy_builders/attach/.../image.jpg?part=0.1",
      "part": "0.1",
      "filesize": 245678,
      "downloaded": true,
      "thumbnail_generated": true
    }
  ]
}
```

### 3. Module Structure

#### imageGetter/
Extracts image URLs from markdown files and downloads images.

**Components:**
- `extract_image_urls.py` - Parse msgs_md files, identify attachment URLs
- `download_images.py` - Download images with retry logic, rename to standardized format
- `generate_thumbnails.py` - Create 200x200px center-cropped thumbnails
- `image_index.json` - Maintained index of all images

**Filtering Rules:**
- **Include:** URLs matching `groups.google.com/group/cozy_builders/attach/`
- **Exclude:** Profile photos (lh3.googleusercontent.com)
- **Exclude:** Logos, emojis, UI elements
- **Exclude:** Image file size < 10KB (likely icons/logos)

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

## Success Criteria

**Phase 1-3 Complete (A/ Directory Test):**
- ✓ Successfully extracted 50+ image URLs from A/ directory
- ✓ Downloaded 80%+ of identified images
- ✓ Generated thumbnails for all downloaded images
- ✓ image_index.json accurately reflects status

**Phase 4 Complete (Query Interface):**
- ✓ Query "firewall" returns relevant images
- ✓ Query "oil cooler" returns relevant images
- ✓ Thumbnails display correctly
- ✓ Full-resolution images accessible

**Phase 5 Complete (Full Corpus):**
- ✓ All directories processed
- ✓ Image database covers full newsgroup corpus
- ✓ Acceptable download success rate (>75%)

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Google Groups blocks scraping | Add rate limiting, user-agent, monitor for 429 errors |
| Many broken image links | Track success rate, acceptable if >60% valid |
| Insufficient disk space | Check space before Phase 5, estimate from Phase 1-3 |
| Text retrieval poor quality | Collect feedback, iterate on query approach, consider multimodal Phase 6 |
| Download takes too long | Implement parallel downloads, resume capability |

## Open Questions

1. Should we store original message markdown path in image_index.json for reference?
2. Do we need image versioning if re-downloading improves quality?
3. Should thumbnail size be configurable or fixed at 200x200?
4. Web interface framework preference (Flask, FastAPI, static HTML)?

---

**Next Steps:**
See `image_database_implementation_plan.md` for detailed incremental implementation plan.
