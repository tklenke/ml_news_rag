# Image URL Patterns in Cozy Builders Markdown Files

**Created:** 2025-11-01
**Analysis:** Phase 1.1 URL Pattern Analysis

## Summary

Analyzed 14 markdown files from `data/msgs_md/A/` directory to identify patterns for filtering image URLs.

## Files Analyzed

1. `a-3RIrqeE_Q.md` - Profile photos only
2. `A-Yb8-L_4NM.md` - Profile photos only
3. `A0OiG3usNBQ.md` - Profile photos only
4. `A1NtxlDfY4c.md` - Has attachment (graycol.gif)
5. `a42YFDFx8WY.md` - Has multiple attachments (4 images)
6. `A4f8HScN-1w.md` - Has attachment (image001.png)
7. `a_XD_FslP1w.md` - Has multiple attachments (3 images)
8. `A20JX9PGHII.md` - Has attachment (image001.gif)
9. `A2I2Uf00w7E.md` - Profile photos only
10. `a2LcgTGLaoE.md` - Profile photos only
11. `A2ne3ed8CHE.md` - Profile photo only
12. `a3dnJ1Kdn5M.md` - Has inline image + PDF attachments
13. `A3uG9PRmKhM.md` - Profile photos only
14. `a3vAtljDow4.md` - Tracking pixels and logos

**Result:** 6 of 14 files (43%) contain attachment images to download

## Markdown Syntax Patterns

### Pattern 1: Inline Images (Markdown syntax)
```markdown
![alt text](url)
```

### Pattern 2: Linked Images
```markdown
[![alt text](thumbnail_url)](full_size_url)
```

### Pattern 3: Attachment Links
```markdown
filename.ext [ ](url)
```

## URL Patterns to INCLUDE (Download these)

### Attachment Images Pattern
**Base Pattern:**
```
https://groups.google.com/group/cozy_builders/attach/{messageID}/{filename}?part={partNumber}
```

**Examples:**
```
https://groups.google.com/group/cozy_builders/attach/7d6ac224e41ae/Image.jpeg?part=0.1
https://groups.google.com/group/cozy_builders/attach/7d6ac224e41ae/Image.jpeg?part=0.2
https://groups.google.com/group/cozy_builders/attach/b7b89755afd4fbca/image001.gif?part=0.1
https://groups.google.com/group/cozy_builders/attach/78e1e9035c2a/image001.jpg?part=0.1
https://groups.google.com/group/cozy_builders/attach/6a423ccac502c75a/graycol.gif?part=0.1
```

**Characteristics:**
- Domain: `groups.google.com`
- Path contains: `/group/cozy_builders/attach/`
- Has `part=` query parameter
- File extensions: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`

**Regex Pattern:**
```regex
https://groups\.google\.com/group/cozy_builders/attach/[^/]+/[^?]+\?part=[0-9.]+
```

## URL Patterns to EXCLUDE (Skip these)

### 1. Profile Photos
**Pattern:**
```
//lh3.googleusercontent.com/a-/{hash}=s40-c
//lh3.googleusercontent.com/a/default-user=s40-c
```

**Examples:**
```
//lh3.googleusercontent.com/a-/ALV-UjVbNQF0wQEyMwNrbrYCtcL6UhUH07_0j13cxhNAsF36FLdtLw=s40-c
//lh3.googleusercontent.com/a/default-user=s40-c
```

**Characteristics:**
- Domain: `googleusercontent.com`
- Path contains: `/a-/` or `/a/default-user`
- Small size indicator: `s40-c` (40px profile photos)

### 2. Tracking Pixels and Proxied Images
**Pattern:**
```
https://ci{N}.googleusercontent.com/proxy/...
```

**Examples:**
```
https://ci4.googleusercontent.com/proxy/ovY971ktMKGTvC3UYE2_MA...
https://ci6.googleusercontent.com/proxy/sPL5zBS-r5EKU__FQU-Qp...
```

**Characteristics:**
- Domain: `ci4.googleusercontent.com`, `ci6.googleusercontent.com`, etc.
- Path: `/proxy/...`
- Usually very small tracking pixels (1x1)

### 3. Inline Hosted Images
**Pattern:**
```
https://lh3.googleusercontent.com/-{hash}/{filename}
```

**Examples:**
```
https://lh3.googleusercontent.com/-T8OOZIxM9AI/WZME58OGRlI/AAAAAAAAAi8/9U6P0Dd2khAucj2dZzqPmZp7HtGvRrM9gCLcBGAs/s320/IMG_1803.JPG
```

**Characteristics:**
- Domain: `lh3.googleusercontent.com`
- Path starts with: `/-` (dash indicates user-uploaded, not attachment)
- Contains size indicators: `s320`, `s1600`, etc.

**Note:** These are inline-embedded images, not attachments. May be harder to download without authentication. Exclude for simplicity.

### 4. Logos and Signatures
**Pattern:**
```
Any image from yahoo.com, yimg.com domains
```

**Examples:**
```
http://l.yimg.com/ru/static/images/yg/img/email/new_logo/logo-groups-137x15.png
```

**Characteristics:**
- Yahoo/YImg domains
- UI elements and branding

## Filtering Strategy

### Simple Approach (Recommended)
**INCLUDE only URLs matching:**
```python
url.startswith('https://groups.google.com/group/cozy_builders/attach/')
```

**This automatically excludes:**
- All profile photos (different domain)
- All tracking pixels (different domain)
- All logos (different domain/path)
- All inline images (different path)

### Regex Approach (If needed)
```python
import re

pattern = r'https://groups\.google\.com/group/cozy_builders/attach/[^/]+/[^?]+\?part=[0-9.]+'
matches = re.findall(pattern, markdown_content)
```

## File Extension Filtering

### Expected Image Extensions
- `.jpg`, `.jpeg`
- `.png`
- `.gif`
- `.bmp` (rare)

### Non-Image Attachments to Exclude
- `.pdf` (seen in a3dnJ1Kdn5M.md)
- `.doc`, `.docx`
- `.txt`

**Note:** PDF attachments use same URL pattern as images but should be excluded from image database.

## Part Numbers

Attachment images use `?part=N.M` format:
- `?part=0.1` - First attachment
- `?part=0.2` - Second attachment
- `?part=0.3` - Third attachment
- etc.

The part number identifies which attachment in the message this is.

## Edge Cases Discovered

1. **Multiple images in one message:** `a42YFDFx8WY.md` has 4 images (parts 0.1-0.4)
2. **Mixed attachments:** `a3dnJ1Kdn5M.md` has images AND PDFs - filter by extension
3. **Linked thumbnails:** Some messages have clickable thumbnails linking to full-size googleusercontent.com images - these may require different handling
4. **Empty alt text:** Many images have no alt text or generic alt text like "Image removed by sender"

## Recommended Implementation

```python
def is_attachment_image(url: str) -> bool:
    """Check if URL is a downloadable attachment image."""
    # Must be attachment URL
    if not url.startswith('https://groups.google.com/group/cozy_builders/attach/'):
        return False

    # Must have image extension
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    url_lower = url.lower()

    return any(ext in url_lower for ext in image_extensions)
```

## Statistics from Analysis

### Initial Manual Analysis (14 files from A/ directory)
- **Total files analyzed:** 14
- **Files with attachments:** 6 (43%)
- **Total attachment image URLs found:** ~15
- **Profile photo URLs found:** ~20+
- **Tracking/logo URLs found:** ~10

### Full Corpus Scan (All 10,443 markdown files)

**Scan Date:** 2025-11-01
**Scan Tool:** `scan_image_urls.py`

**Overall Statistics:**
- **Total markdown files scanned:** 10,443
- **Files with image URLs:** 3,491 (33%)
- **Total image URLs found:** 10,060
- **Unique image URLs:** 7,643
- **Unique domains:** 111

**Domain Breakdown (Top domains by count):**
- `groups.google.com` - **7,406 URLs (97% of unique URLs)**
- `ci6.googleusercontent.com` - 1,499 (tracking pixels - EXCLUDE)
- `ci3.googleusercontent.com` - 210 (tracking pixels - EXCLUDE)
- `lh3.googleusercontent.com` - 146 (profile photos - EXCLUDE)
- `ci4.googleusercontent.com` - 146 (tracking pixels - EXCLUDE)
- `ci5.googleusercontent.com` - 143 (tracking pixels - EXCLUDE)
- `groups.yahoo.com` - 140
- `ljosnes.no` - 70 (external Cozy calendar site)
- Other domains - <40 each (external sites, vendor links, etc.)

**Path Pattern Analysis:**
- **7,396 URLs** match pattern: `https://groups.google.com/group/cozy_builders/attach/...`
- This is **96.7% of all unique URLs**
- All other patterns are tracking pixels, external links, or UI elements

**Conclusion:**
The simple filter `url.startswith('https://groups.google.com/group/cozy_builders/attach/')` captures 97% of relevant attachment images while automatically excluding all tracking pixels, profile photos, and logos.

**Detailed scan results:** See `docs/input/image_url_scan_results.txt`

## Next Steps

1. Implement `extract_image_urls()` function with simple filter
2. Test on fixture files
3. Run on full A/ directory to validate implementation
