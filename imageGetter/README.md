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

You must have Chrome running in debug mode with Google Groups authentication:

```bash
# Windows
chrome.exe --remote-debugging-port=9222

# Linux/Mac
google-chrome --remote-debugging-port=9222
```

**Important:** Log into Google Groups in this Chrome instance before running download scripts.

### ChromeDriver

ChromeDriver must be available at `../../chromedriver-win64/chromedriver.exe` (relative to this directory).

## Usage

### Phase 1: Extract Image URLs

```bash
python extract_image_urls.py \
  --input ../data/msgs_md/A \
  --output ../data/image_index.json \
  --dry-run
```

### Phase 2: Download Images

```bash
# Make sure Chrome is running with --remote-debugging-port=9222 first!
python download_images_cli.py \
  --index ../data/image_index.json \
  --output ../data/images/full \
  --limit 5
```

### Phase 3: Generate Thumbnails

```bash
python generate_thumbnails_cli.py \
  --input ../data/images/full \
  --output ../data/images/thumbs \
  --index ../data/image_index.json
```

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
