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

Attachment URLs need a Google login: fetched without one they answer with the sign-in page.
The download therefore runs on Windows, through Tom's Chrome, signed in to Google Groups,
with Selenium attached to Chrome's debug port:

```powershell
chrome.exe --remote-debugging-port=9222
```

Log into Google Groups in that Chrome window before running the download.

The download is run by the Windows Python (3.13, with `selenium`, `requests`, `Pillow` and
`tqdm` installed), from this directory in WSL, so that relative paths reach `../data` in WSL.
Use PowerShell: cmd cannot use a `\\wsl.localhost\...` path as its current directory.
WSL must be running (a WSL terminal open).

ChromeDriver is given with `--chromedriver`. Its version must match the installed Chrome.

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

In PowerShell on Windows, with Chrome running as above (one command, shown on several lines):

```powershell
cd \\wsl.localhost\Debian\home\tom\projects\ml\imageGetter
python download_images_cli.py `
  --chromedriver C:\Users\tom\Documents\projects\chromedriver-win64\chromedriver.exe `
  --log ..\data\images\download_YYMMDD.log `
  ..\data\images\indexYYMMDDhhmmss.idx `
  ..\data\images\full
```

- A picture already in `full` is not fetched again, so a run can be repeated.
- A request that takes longer than `--timeout` seconds (default 60), or answers with a
  status other than 200, or is not a picture, fails and leaves no file. Each failure is
  listed in the log as `FAILED <local name> <url>`.
- `--limit N` downloads only the first N pictures, for a trial.
- The download writes the index file back as it goes.

### Phase 3: Generate Thumbnails

```bash
python generate_thumbnails_cli.py \
  ../data/images/full \
  ../data/images/thumbs
```

## Image Curation Workflow

After downloading and processing images, use this workflow to dedupe, tag, review, and curate your image collection:

### Review Pictures by Content

Run in WSL from `imageGetter/`, then open `http://127.0.0.1:8765/` in a browser:

```bash
../venv/bin/python review_images_cli.py \
  ../data/images/indexYYMMDDhhmmss.idx \
  ../data/images/full \
  ../data/images/thumbs \
  image_decisions.json \
  image_suggestions.json
```

- One content (same SHA-256) is one picture, shown under its earliest thread.
- A click on a picture switches it between keep (green) and discard (red, stored as
  `remove`); the keep and discard buttons set the choice directly. Each choice is written
  to `image_decisions.json` at once and can be changed later.
- A picture not yet clicked shows keep with a dashed frame: nothing is saved for it. The
  button at the end of a page saves every dashed picture of the page as `keep`.
- **Suggested**: undecided pictures under 1,000 bytes, in 2 or more threads, with a
  shorter side under 200 pixels, named `imageNNN` under 20,000 bytes, or removed in some copies only in 2025.
  **New**: every other undecided picture. **Decided**: everything marked.
- Commit `image_decisions.json` after a session of review.

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
