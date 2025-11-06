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

### Phase 5: Tag Images with Scored Keywords

Score keywords per image based on proximity to image URLs in message text (fast, deterministic):

```bash
python search_tag_messages_cli.py \
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

Scoring keywords for images...

============================================================
KEYWORD SCORING STATISTICS
============================================================
Total messages in index:     1234
Messages processed:          1234
Images scored:               6075
Messages with errors:        0

Keywords per image:
  Average:                   18.5
  Min:                       0
  Max:                       127
  Images with keywords:      6052

Score range:
  Min:                       12
  Max:                       847
  Average:                   156.3
============================================================

Results saved to: ../data/image_index_tagged.json
```

**Notes:**
- Scores based on keyword proximity to image URLs using exponential decay
- Subject line keywords get +200 bonus points
- Keywords stored as `[keyword, score]` tuples sorted by score descending
- Use `--limit N` to process only first N messages (for testing)
- Use `--verbose` to see detailed progress for each message
- Use `--no-clean` to skip invalid keyword filtering

### Phase 6: Generate Static HTML Site

Create a complete static HTML site for browsing images by keyword:

```bash
python generate_static_site_cli.py \
  ../data/image_index_tagged.json \
  ../data/site \
  --images-per-page 210 \
  --min-score 0
```

**Example output:**
```
Loading index from ../data/image_index_tagged.json...
Loaded 1234 messages

Generating index page...
  Generated index.html with 557 keywords

Preparing image list...
  Found 6075 total images
  Year distribution: {2024: 3245, 2023: 2830}

Generating all images pages...
  Generated all/page1.html (210 images)
  Generated all/page2.html (210 images)
  ...
  Generated all/page29.html (75 images)

Generating keyword pages...
  Generated 5 page(s) for 'firewall' (897 images)
  Generated 3 page(s) for 'cowling' (512 images)
  ...

Site generation complete!
Output: ../data/site
  - index.html
  - all/page1.html ... all/page29.html
  - keywords/ (557 keywords)
```

**Generated Site Structure:**
```
site/
├── index.html (keyword index with image counts)
├── all/
│   ├── page1.html (all images, newest first)
│   ├── page2.html
│   └── ...
└── keywords/
    ├── firewall_page1.html (images sorted by score)
    ├── firewall_page2.html
    ├── cowling_page1.html
    └── ...
```

**Notes:**
- Images on keyword pages sorted by score (highest first)
- Scores displayed on thumbnails: "firewall (245)"
- Use `--min-score N` to filter out low-scoring images
- Each page has First/Previous/Next/Last navigation
- Index page links to all keywords and "All Images" view

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
