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
1. [ ] Create `imageGetter/generate_static_site.py` with ABOUTME comments
2. [ ] Create `imageGetter/tests/test_generate_static_site.py`
3. [ ] Write failing test: `test_load_index_data()`
4. [ ] Write failing test: `test_count_images_per_keyword()`
5. [ ] Write failing test: `test_generate_index_html()`
6. [ ] Write failing test: `test_alphabetical_keyword_sort()`
7. [ ] Run tests - verify all fail
8. [ ] Implement functions to:
   - Load image_index.json
   - Count images per keyword
   - Sort keywords alphabetically
   - Generate index.html with:
     - Link to "All Images" (→ all/page1.html)
     - Alphabetical keyword list with counts: `firewall (127 images)`
     - Breadcrumb navigation at top
9. [ ] Run tests - verify all pass
10. [ ] Manual test: Open index.html in browser, verify layout
11. [ ] Commit: "Implement index page generation"

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
1. [ ] Write failing test: `test_sort_messages_by_date_descending()`
2. [ ] Write failing test: `test_group_by_year()`
3. [ ] Write failing test: `test_paginate_images()`
4. [ ] Write failing test: `test_generate_all_images_page()`
5. [ ] Write failing test: `test_first_prev_next_last_navigation()`
6. [ ] Run tests - verify all fail
7. [ ] Implement functions to:
   - Sort messages by date (descending, newest first)
   - Group by year (for year headers)
   - Paginate (210 images per page, 6 columns × 35 rows)
   - Generate all/pageN.html files with:
     - Breadcrumb: `← Back to Index`
     - Year headers: `2024 (345 images)`, `2023 (512 images)`, etc.
     - 6-column thumbnail grid
     - First/Previous/Next/Last navigation (top and bottom)
     - Each thumbnail shows: image, subject, message ID, keywords
8. [ ] Run tests - verify all pass
9. [ ] Manual test: Generate pages, verify navigation works
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
1. [ ] Write failing test: `test_filter_messages_by_keyword()`
2. [ ] Write failing test: `test_generate_keyword_page()`
3. [ ] Write failing test: `test_keyword_page_navigation()`
4. [ ] Write failing test: `test_safe_keyword_filenames()`
5. [ ] Run tests - verify all fail
6. [ ] Implement functions to:
   - Filter messages by keyword
   - Generate keywords/KEYWORD_pageN.html files with:
     - Breadcrumb: `← Back to Index | Keyword: firewall`
     - Same 6-column grid layout
     - Same pagination (210 per page)
     - First/Previous/Next/Last navigation
   - Handle special characters in keyword filenames (sanitize)
7. [ ] Run tests - verify all pass
8. [ ] Manual test: Generate keyword pages, verify links work
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

### Phase 5.5: Copy HTML/CSS from analyze_tag_statistics

**Deliverable:** Adapt existing HTML/CSS for static site

**Tasks:**
1. [ ] Review `analyze_tag_statistics.py` HTML generation code
2. [ ] Copy relevant CSS styles:
   - 6-column grid layout
   - Thumbnail sizing
   - Navigation button styles
   - Page layout
3. [ ] Remove interactive features:
   - Checkboxes
   - Select All/Clear All buttons
   - Export removal list button
   - JavaScript for interactivity
4. [ ] Keep static features:
   - Thumbnail grid
   - Click to view full resolution
   - Navigation links (First/Prev/Next/Last)
   - Keyword display under thumbnails
5. [ ] Add breadcrumb navigation styles
6. [ ] Test in browser, adjust spacing/layout as needed
7. [ ] Commit: "Adapt HTML/CSS from analyze_tag_statistics"

**CSS Notes:**
- Thumbnails link to full resolution image (relative path)
- Simple, clean layout
- No JavaScript required

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
