# ABOUTME: imageGetter module extracts and downloads attachment images from Cozy Builders Google Groups messages
# ABOUTME: Filters URLs to include only attachment images, excluding profile photos and logos

# imageGetter Module

## Purpose

Extract and download attachment images from Cozy Builders Google Groups markdown files. This module:
1. Parses markdown files to find attachment image URLs
2. Filters out profile photos, logos, and tracking pixels
3. Downloads images using Selenium (authenticated via Chrome debug mode)
4. Generates 200x200px center-cropped thumbnails
5. Builds an index mapping message IDs to images

## Directory Structure

```
imageGetter/
├── README.md (this file)
├── requirements.txt
├── venv/ (local virtual environment, not committed)
├── tests/
│   ├── test_extract_urls.py
│   └── fixtures/
│       └── (sample markdown files for testing)
├── extract_image_urls.py (Phase 1: URL extraction)
├── download_images.py (Phase 2: Image download)
└── generate_thumbnails.py (Phase 3: Thumbnail generation)
```

## Setup

### 1. Create Virtual Environment

```bash
cd imageGetter
python -m venv venv
```

### 2. Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Prerequisites

### For Image Download (Phase 2)

**Phase 2.2-2.4:** Uses standard HTTP requests (requests library)
- Most Google Groups attachment URLs are publicly accessible
- Includes retry logic with exponential backoff
- Validates images after download

**Fallback (if needed):** If attachments require authentication, we'll use Selenium with Chrome debug mode:

```bash
# Windows
chrome.exe --remote-debugging-port=9222

# Linux/Mac
google-chrome --remote-debugging-port=9222
```

**Important:** Log into Google Groups in the Chrome instance before running download scripts.

### ChromeDriver (only if Selenium needed)

ChromeDriver must be available at `../../chromedriver-win64/chromedriver.exe` (relative to this directory).

## Usage

### Phase 1: Extract Image URLs

```bash
python extract_image_urls.py \
  ../data/msgs_md/A \
  ../data \
  --dry-run
```

**Note:** Creates `index{timestamp}.idx` in the output directory

### Phase 2: Download Images

```bash
# Make sure Chrome is running with --remote-debugging-port=9222 first!
python download_images_cli.py \
  ../data/image_index.json \
  ../data/images/full \
  --limit 5
```

### Phase 3: Generate Thumbnails

```bash
python generate_thumbnails_cli.py \
  ../data/images/full \
  ../data/images/thumbs
```

## Image Curation Workflow

After downloading and processing images, use this workflow to dedupe, tag, review, and curate your image collection:

### Phase 4: Deduplicate Images

Remove duplicate images (based on file size) and missing files from the index:

```bash
python dedupe_images_cli.py \
  ../data/image_index.json \
  ../data/image_index_deduped.json \
  --images-dir ../data/images/full
```

**Example output:**
```
Loading index from ../data/image_index.json...
Loaded 1234 messages with 6789 images

Processing messages...
100%|████████████████████| 1234/1234 [00:15<00:00, 82.27 messages/s]

============================================================
DEDUPLICATION SUMMARY
============================================================
Total messages:          1234
Messages processed:      1234

Images before:           6789
Duplicates removed:      691
Missing files removed:   23
Images after:            6075
============================================================

Saving deduped index to ../data/image_index_deduped.json...
```

### Phase 5: Tag Messages with Keywords

Tag messages with semantic keywords using LLM (automatically skips already-tagged messages):

```bash
python tag_messages_cli.py \
  ../data/image_index_deduped.json \
  ../data/image_index_tagged.json \
  --keywords aircraft_keywords.txt
```

**Example output:**
```
Tagging messages from ../data/image_index_deduped.json
Output file: ../data/image_index_tagged.json
Keywords: aircraft_keywords.txt
Limit: ALL messages (no limit)

Loading image index...
Loaded 1234 messages

Loading keywords...
Loaded 557 keywords

Messages to process: 1234
Already tagged (will skip): 0

Tagging messages with keywords...
LLM timeout per message: 30s (configurable in llm_config.py)

[1/1234] Installing firewall today
[2/1234] Re: Cowling attachment
...
  → Auto-saved after 50 messages
...

============================================================
TAGGING STATISTICS
============================================================
Total messages in index:     1234
Messages processed:          1234
Messages skipped:            0
Messages with errors:        0

Keywords per message:
  Average:                   2.3
  Min:                       0
  Max:                       8
============================================================

Results saved to: ../data/image_index_tagged.json
```

**Notes:**
- Messages with existing `llm_keywords` are skipped automatically (idempotent)
- Auto-saves every 50 messages for crash recovery
- Use `--limit N` to tag only first N messages (for testing)
- Use `--verbose` to see detailed LLM responses

### Phase 6: Generate Paginated HTML Review

Create an interactive HTML view to review images by keyword (210 images per page):

```bash
python analyze_tag_statistics.py \
  ../data/image_index_tagged.json \
  ../data/tag_review.txt \
  --thumb-dir ../data/images/thumbs \
  --page-size 210
```

**Example output:**
```
Loaded 1234 messages
Extracted 45 unique keywords

Tag Statistics:
  aircraft: 1245 images
  helicopters: 856 images
  experimental: 634 images
  ...

HTML pages generated:
  tag_review_view_page1.html (210 images)
  tag_review_view_page2.html (210 images)
  ...
  tag_review_view_page29.html (75 images)
```

### Phase 7: Review and Select Images

1. Open the HTML files in your browser (e.g., `tag_review_view_page1.html`)
2. Review images and check boxes for images you want to remove
3. Click "Export Selected to File" button on each page
4. This creates `images_to_remove_pageN.txt` files for each page

**Navigation:**
- Each page includes << First | < Previous | Page N of M | Next > | Last >> links
- "Select All" and "Clear All" buttons for bulk operations
- Selected images highlighted in red

### Phase 8: Remove Selected Images

Process the removal list files to create a cleaned index:

```bash
python remove_images_cli.py \
  ../data/image_index_tagged.json \
  ../data/image_index_cleaned.json \
  --remove-list images_to_remove_page*.txt
```

**Example output:**
```
Loading index from ../data/image_index_tagged.json...
Loaded 1234 messages with 6075 images

Loading removal lists...
  - images_to_remove_page1.txt
  - images_to_remove_page2.txt
  - images_to_remove_page8.txt
  - images_to_remove_page9.txt
Loaded 356 unique filenames to remove

Removing images from index...

============================================================
REMOVAL SUMMARY
============================================================
Total messages:              1234
Messages affected:           198
Messages removed:            157

Images before:               6075
Images removed:              356
Images after:                5719
============================================================

Saving cleaned index to ../data/image_index_cleaned.json...
Cleaned index saved to: ../data/image_index_cleaned.json
```

**Notes:**
- Messages with all images removed are deleted entirely from the index
- Original index files are never modified (read-only)
- Multiple removal list files are automatically deduplicated
- The cleaned index is ready for further processing or analysis

## Testing

```bash
# Activate venv first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## Development Notes

- Follow TDD: Write tests first (RED), implement (GREEN), refactor (REFACTOR)
- Use Hungarian notation: `strVariableName`, `intCount`, `lstItems`, `dctMapping`
- Add ABOUTME comments to all new files
- Update `docs/plans/programmer_todo.md` as tasks are completed
- Commit frequently

## Related Documentation

- Architecture: `../docs/plans/image_database_architecture.md`
- Implementation Plan: `../docs/plans/image_database_implementation_plan.md`
- URL Patterns: `../docs/notes/image_url_patterns.md`
