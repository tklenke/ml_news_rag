# Programmer Todo - Image Database Project

**Last Updated:** 2025-11-05

## Current Status

**Completed:** Phases 1-4b (URL extraction, downloads, thumbnails, keyword tagging, curation tools)

**Next:** Phase 5 - Static Site Generation

**Tests:** 110+ passing, 14 skipped

**History:** See git log and `image_database_design.md` for implementation details

---

## Phase 5: Static Site Generation

**Goal:** Generate static HTML site for browsing tagged images

**Approach:** Adapt code from `analyze_tag_statistics.py` (copy, don't share)

**Starting Point:** Use existing HTML/CSS from analyze_tag_statistics.py as template

---

### Phase 5.1: Generate Index Page (TDD)

**Deliverable:** `index.html` with links to "All Images" and alphabetical keyword list

**Tasks:**
1. [x] Create `imageGetter/generate_static_site.py` with ABOUTME comments
2. [x] Create `imageGetter/tests/test_generate_static_site.py`
3. [x] Write failing test: `test_load_index_data()`
4. [x] Write failing test: `test_count_images_per_keyword()`
5. [x] Write failing test: `test_generate_index_html()`
6. [x] Write failing test: `test_alphabetical_keyword_sort()`
7. [x] Run tests - verify all fail
8. [x] Implement functions to:
   - Load image_index.json
   - Count images per keyword
   - Sort keywords alphabetically
   - Generate index.html with:
     - Link to "All Images" (→ all/page1.html)
     - Alphabetical keyword list with counts: `firewall (127 images)`
     - Breadcrumb navigation at top
9. [x] Run tests - verify all pass
10. [ ] Manual test: Open index.html in browser, verify layout (deferred for now)
11. [x] Commit: "Implement index page generation"

**HTML Structure (index.html):**
```html
<h1>Cozy Builders Image Database</h1>
<p><a href="all/page1.html">All Images (chronological)</a></p>
<h2>Browse by Keyword</h2>
<ul>
  <li><a href="keywords/aileron_page1.html">aileron (45 images)</a></li>
  <li><a href="keywords/firewall_page1.html">firewall (127 images)</a></li>
  ...
</ul>
```

---

### Phase 5.2: Generate "All Images" Pages (TDD)

**Deliverable:** `all/page1.html`, `all/page2.html`, etc. with chronological images

**Tasks:**
1. [x] Write failing test: `test_sort_messages_by_date_descending()`
2. [x] Write failing test: `test_group_by_year()`
3. [x] Write failing test: `test_paginate_images()`
4. [x] Write failing test: `test_generate_all_images_page()`
5. [x] Write failing test: `test_first_prev_next_last_navigation()`
6. [x] Run tests - verify all fail
7. [x] Implement functions to:
   - Sort messages by date (descending, newest first)
   - Group by year (for year headers)
   - Paginate (210 images per page, 6 columns × 35 rows)
   - Generate all/pageN.html files with:
     - Breadcrumb: `← Back to Index`
     - Year headers: `2024 (345 images)`, `2023 (512 images)`, etc.
     - 6-column thumbnail grid
     - First/Previous/Next/Last navigation (top and bottom)
     - Each thumbnail shows: image, subject, message ID, keywords
8. [x] Run tests - verify all pass
9. [ ] Manual test: Generate pages, verify navigation works (deferred)
10. [ ] Commit: "Implement all images chronological pages"

**Pagination Logic:**
- 210 images per page (6 columns × 35 rows)
- First/Previous/Next/Last links at top and bottom
- Disable Previous/First on page 1
- Disable Next/Last on final page

---

### Phase 5.3: Generate Keyword Pages (TDD)

**Deliverable:** `keywords/firewall_page1.html`, etc. for each keyword

**Tasks:**
1. [x] Write failing test: `test_filter_messages_by_keyword()`
2. [x] Write failing test: `test_generate_keyword_page()`
3. [x] Write failing test: `test_keyword_page_navigation()`
4. [x] Write failing test: `test_safe_keyword_filenames()`
5. [x] Run tests - verify all fail
6. [x] Implement functions to:
   - Filter messages by keyword
   - Generate keywords/KEYWORD_pageN.html files with:
     - Breadcrumb: `← Back to Index | Keyword: firewall`
     - Same 6-column grid layout
     - Same pagination (210 per page)
     - First/Previous/Next/Last navigation
   - Handle special characters in keyword filenames (sanitize)
7. [x] Run tests - verify all pass
8. [ ] Manual test: Generate keyword pages, verify links work (deferred)
9. [ ] Commit: "Implement keyword-specific pages"

**Filename Sanitization:**
- Replace spaces/special chars with underscores
- Lowercase for consistency
- Example: "landing gear" → `keywords/landing_gear_page1.html`

---

### Phase 5.4: CLI Tool and Full Generation

**Deliverable:** CLI tool to generate complete static site

**Tasks:**
1. [ ] Create `imageGetter/generate_static_site_cli.py` with ABOUTME comments
2. [ ] Add command-line arguments:
   - `SOURCE` (path to image_index.json)
   - `DEST` (output directory for static site)
   - `--images-per-page` (default 210)
3. [ ] Implement:
   - Create output directory structure (all/, keywords/)
   - Generate index.html
   - Generate all/pageN.html files
   - Generate keywords/KEYWORD_pageN.html files for each keyword
   - Progress reporting
4. [ ] Test on actual image_index.json
5. [ ] Commit: "Add CLI tool for static site generation"

**Usage:**
```bash
python generate_static_site_cli.py ../data/image_index.json ../data/static_site
# Generates:
#   ../data/static_site/index.html
#   ../data/static_site/all/page1.html, page2.html, ...
#   ../data/static_site/keywords/firewall_page1.html, ...
```

---

### Phase 5.5: HTML Layout with Skeleton CSS

**Deliverable:** HTML pages using Skeleton CSS framework to match existing site

**Context:**
- Main site: http://m24tom.com uses Skeleton CSS (http://getskeleton.com/)
- Static site location: http://m24tom.com/cgimages/index.html
- Match existing site's look and feel
- Use Skeleton CSS grid system for layout

**Tasks:**
1. [ ] Inspect http://m24tom.com source to find CSS references
   - Note skeleton.css path
   - Note normalize.css path (Skeleton dependency)
   - Note any custom CSS files
2. [ ] Review `analyze_tag_statistics.py` HTML for thumbnail grid structure
3. [ ] Create HTML template using Skeleton CSS:
   - Use Skeleton grid system (12 columns)
   - 6-column thumbnail layout = 2-column Skeleton grid (each thumbnail = 2 Skeleton columns)
   - Responsive layout (Skeleton handles mobile)
4. [ ] For testing: Use full URLs for CSS:
   - `<link rel="stylesheet" href="http://m24tom.com/path/to/skeleton.css">`
   - `<link rel="stylesheet" href="http://m24tom.com/path/to/normalize.css">`
5. [ ] For production: Use site-relative paths:
   - `<link rel="stylesheet" href="/path/to/skeleton.css">`
6. [ ] Remove interactive features from analyze_tag_statistics:
   - Checkboxes
   - Select All/Clear All buttons
   - Export removal list button
   - JavaScript for interactivity
7. [ ] Keep static features:
   - Thumbnail grid (adapt to Skeleton)
   - Click to view full resolution
   - Navigation links (First/Prev/Next/Last)
   - Keyword display under thumbnails
8. [ ] Add minimal custom CSS for:
   - Thumbnail sizing
   - Navigation button spacing
   - Year header styling
   - Breadcrumb navigation
9. [ ] Test in browser at cgimages/ path, adjust layout as needed
10. [ ] Commit: "Implement HTML layout with Skeleton CSS"

**Skeleton CSS Grid Example:**
```html
<div class="container">
  <div class="row">
    <div class="two columns"><!-- thumbnail 1 --></div>
    <div class="two columns"><!-- thumbnail 2 --></div>
    <div class="two columns"><!-- thumbnail 3 --></div>
    <div class="two columns"><!-- thumbnail 4 --></div>
    <div class="two columns"><!-- thumbnail 5 --></div>
    <div class="two columns"><!-- thumbnail 6 --></div>
  </div>
</div>
```

**CSS Reference Strategy:**
- Testing: Full URLs `http://m24tom.com/css/...`
- Production: Relative URLs `/css/...` or `../css/...`
- Thumbnails: Relative paths from cgimages/ directory

---

### Phase 5.6: Validate and Document

**Deliverable:** Working static site with documentation

**Tasks:**
1. [ ] Generate full static site from current image_index.json
2. [ ] Manual validation:
   - Index page links work correctly
   - All images pages navigate properly
   - Keyword pages show correct images
   - Year headers display correctly
   - Breadcrumbs navigate back to index
   - Thumbnails link to full resolution
3. [ ] Test edge cases:
   - Keywords with 0 images (should not appear in index)
   - Keywords with 1 page (no Next/Last links)
   - Messages with no keywords (appear in "all" but not keyword pages)
4. [ ] Document in `imageGetter/README.md`:
   - Static site generation workflow
   - CLI usage examples
   - Output directory structure
5. [ ] Create `docs/notes/phase5_results.md`:
   - Site structure overview
   - Total pages generated
   - Navigation patterns
   - User experience assessment
6. [ ] Commit: "Complete Phase 5 static site generation"

---

## Escalation Protocol

**When to escalate to Architect:**
- Site structure unclear
- Performance issues with large datasets
- Major technical blockers

Use "Strange things are afoot at the Circle K" for urgent issues.

---

## Before Every Commit

- [ ] Run tests: `pytest`
- [ ] Update this file with progress
- [ ] Include updated programmer_todo.md in commit

---

**Last Updated:** 2025-11-05 by Claude (Architect)
