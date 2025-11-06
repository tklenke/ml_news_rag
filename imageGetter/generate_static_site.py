#!/usr/bin/env python3
# ABOUTME: Generate static HTML site for browsing tagged images
# ABOUTME: Creates index page, chronological all images pages, and keyword-specific pages

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter


def load_index_data(index_file: str) -> dict:
    """Load image index from JSON file.

    Args:
        index_file: Path to image index JSON file

    Returns:
        Dictionary of messages keyed by message ID
    """
    with open(index_file, 'r') as f:
        return json.load(f)


def count_images_per_keyword(index_data: dict, min_score: int = 0) -> Dict[str, int]:
    """Count how many images are tagged with each keyword.

    Phase 6: Handles image-level scored keywords.

    Args:
        index_data: Dictionary of messages from image index
        min_score: Minimum score threshold (default: 0, include all)

    Returns:
        Dictionary mapping keyword -> image count
    """
    keyword_counts = Counter()

    for message in index_data.values():
        # Count images per keyword (Phase 6: image-level keywords)
        for image in message.get("images", []):
            # Get scored keywords for this image: {"keyword": score, ...}
            for kw, score in image.get("keywords", {}).items():
                if score >= min_score:
                    keyword_counts[kw.lower()] += 1

    return dict(keyword_counts)


def sort_keywords_alphabetically(keyword_counts: Dict[str, int]) -> List[Tuple[str, int]]:
    """Sort keywords alphabetically.

    Args:
        keyword_counts: Dictionary mapping keyword -> image count

    Returns:
        List of (keyword, count) tuples sorted alphabetically by keyword
    """
    return sorted(keyword_counts.items(), key=lambda x: x[0])


def generate_html_head(title: str) -> List[str]:
    """Generate HTML head section with Skeleton CSS.

    Args:
        title: Page title

    Returns:
        List of HTML lines for head section
    """
    head = []
    head.append("<!DOCTYPE html>")
    head.append("<html lang='en'>")
    head.append("<head>")
    head.append("  <meta charset='utf-8'>")
    head.append("  <meta name='viewport' content='width=device-width, initial-scale=1'>")
    head.append(f"  <title>{title}</title>")
    # Using CDN for testing - can be changed to site-relative paths for production
    head.append("  <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css'>")
    head.append("  <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css'>")
    # Custom CSS for thumbnails and layout
    head.append("  <style>")
    head.append("    .thumbnail { width: 100%; height: auto; margin-bottom: 5px; }")
    head.append("    .img-cell { text-align: center; margin-bottom: 20px; }")
    head.append("    .subject { font-size: 12px; margin: 5px 0; }")
    head.append("    .msg-id { font-size: 10px; color: #999; margin: 3px 0; }")
    head.append("    .keywords { font-size: 10px; color: #666; margin: 3px 0; }")
    head.append("    .year-header { font-size: 18px; font-weight: bold; margin: 20px 0 10px 0; }")
    head.append("    .pagination { margin: 20px 0; text-align: center; }")
    head.append("    .pagination a, .pagination span { margin: 0 5px; }")
    head.append("    .pagination .disabled { color: #ccc; }")
    head.append("  </style>")
    head.append("</head>")
    head.append("<body>")
    head.append("  <div class='container'>")
    return head


def generate_index_html(keyword_counts: List[Tuple[str, int]], output_file: str) -> None:
    """Generate index.html with links to all images and keyword pages.

    Args:
        keyword_counts: List of (keyword, count) tuples sorted alphabetically
        output_file: Path to write index.html
    """
    html = generate_html_head("Cozy Builders Image Database")
    html.append("    <h1>Cozy Builders Image Database</h1>")

    # Link to all images
    html.append("    <p><a href='all/page1.html'>All Images (chronological)</a></p>")

    # Browse by keyword section
    html.append("    <h2>Browse by Keyword</h2>")

    if keyword_counts:
        html.append("    <ul>")
        for keyword, count in keyword_counts:
            # Sanitize keyword for filename
            safe_keyword = keyword.replace(" ", "_").lower()
            html.append(f"      <li><a href='keywords/{safe_keyword}_page1.html'>{keyword} ({count} images)</a></li>")
        html.append("    </ul>")
    else:
        html.append("    <p>No keywords found.</p>")

    html.append("  </div>") # Close container
    html.append("</body>")
    html.append("</html>")

    # Write to file
    Path(output_file).write_text("\n".join(html))


def sort_messages_by_date(index_data: dict) -> List[Tuple[str, dict]]:
    """Sort messages by date, newest first.

    Args:
        index_data: Dictionary of messages from image index

    Returns:
        List of (message_id, message_data) tuples sorted by date descending
    """
    from datetime import datetime

    def parse_date(date_str: str) -> datetime:
        """Parse date string like 'Jan 15, 2023' into datetime."""
        try:
            return datetime.strptime(date_str, "%b %d, %Y")
        except:
            # If parsing fails, return epoch (very old date)
            return datetime(1970, 1, 1)

    # Convert to list of tuples
    messages = [(msg_id, msg_data) for msg_id, msg_data in index_data.items()]

    # Sort by date, newest first
    messages.sort(key=lambda x: parse_date(x[1]["metadata"].get("date", "")), reverse=True)

    return messages


def group_messages_by_year(sorted_messages: List[Tuple[str, dict]]) -> List[Tuple[int, int]]:
    """Group messages by year and count images.

    Args:
        sorted_messages: List of (message_id, message_data) tuples sorted by date

    Returns:
        List of (year, image_count) tuples ordered by year descending
    """
    from datetime import datetime
    from collections import defaultdict

    def extract_year(date_str: str) -> int:
        """Extract year from date string."""
        try:
            dt = datetime.strptime(date_str, "%b %d, %Y")
            return dt.year
        except:
            return 1970

    year_counts = defaultdict(int)

    for msg_id, msg_data in sorted_messages:
        year = extract_year(msg_data["metadata"].get("date", ""))
        image_count = len(msg_data.get("images", []))
        year_counts[year] += image_count

    # Convert to sorted list (newest year first)
    return sorted(year_counts.items(), key=lambda x: x[0], reverse=True)


def paginate_images(images: List[dict], images_per_page: int = 210) -> List[List[dict]]:
    """Paginate list of images.

    Args:
        images: List of image dictionaries
        images_per_page: Number of images per page (default 210)

    Returns:
        List of pages, each page is a list of images
    """
    pages = []
    for i in range(0, len(images), images_per_page):
        pages.append(images[i:i + images_per_page])
    return pages


def generate_all_images_page(
    images: List[dict],
    page_num: int,
    total_pages: int,
    output_file: str,
    year_groups: List[Tuple[int, int]]
) -> None:
    """Generate a single all images page.

    Args:
        images: List of image dictionaries for this page
        page_num: Current page number (1-indexed)
        total_pages: Total number of pages
        output_file: Path to write HTML file
        year_groups: List of (year, image_count) tuples for year headers
    """
    html = generate_html_head(f"All Images - Page {page_num}")

    # Breadcrumb
    html.append("    <p><a href='../index.html'>&larr; Back to Index</a></p>")
    html.append("    <h1>All Images (Chronological)</h1>")

    # Top pagination
    html.append("    <div class='pagination'>")
    if page_num > 1:
        html.append(f"      <a href='page1.html'>&lt;&lt; First</a>")
        html.append(f"      <a href='page{page_num-1}.html'>&lt; Previous</a>")
    else:
        html.append("      <span class='disabled'>&lt;&lt; First</span>")
        html.append("      <span class='disabled'>&lt; Previous</span>")

    html.append(f"      <span><strong>Page {page_num} of {total_pages}</strong></span>")

    if page_num < total_pages:
        html.append(f"      <a href='page{page_num+1}.html'>Next &gt;</a>")
        html.append(f"      <a href='page{total_pages}.html'>Last &gt;&gt;</a>")
    else:
        html.append("      <span class='disabled'>Next &gt;</span>")
        html.append("      <span class='disabled'>Last &gt;&gt;</span>")
    html.append("    </div>")

    # Image grid using Skeleton CSS (6 columns = 2 Skeleton columns each)
    for i in range(0, len(images), 6):
        html.append("    <div class='row'>")
        for j in range(6):
            idx = i + j
            if idx < len(images):
                img = images[idx]
                html.append("      <div class='two columns img-cell'>")
                html.append(f"        <div class='subject'><a href='https://groups.google.com/g/cozy_builders/c/{img.get('message_id', '')}'>{img.get('subject', 'No subject')[:30]}</a></div>")
                html.append(f"        <div class='msg-id'>{img.get('message_id', '')}</div>")
                html.append(f"        <a href='{img.get('original_url', '')}'>")
                html.append(f"          <img src='{img.get('thumbnail_path', '')}' class='thumbnail' />")
                html.append("        </a>")
                # Phase 6: Display keywords with scores
                keywords_dict = img.get('keywords', {})
                if keywords_dict:
                    # Sort by score descending and take top 5
                    top_keywords = sorted(keywords_dict.items(), key=lambda x: x[1], reverse=True)[:5]
                    # Format as "keyword (score), keyword (score), ..."
                    kw_strings = [f"{kw} ({score})" for kw, score in top_keywords]
                    keywords_str = ", ".join(kw_strings)
                    if len(keywords_dict) > 5:
                        keywords_str += "..."
                else:
                    keywords_str = ""
                html.append(f"        <div class='keywords'>{keywords_str}</div>")
                html.append("      </div>")
        html.append("    </div>")

    # Bottom pagination (same as top)
    html.append("    <div class='pagination'>")
    if page_num > 1:
        html.append(f"      <a href='page1.html'>&lt;&lt; First</a>")
        html.append(f"      <a href='page{page_num-1}.html'>&lt; Previous</a>")
    else:
        html.append("      <span class='disabled'>&lt;&lt; First</span>")
        html.append("      <span class='disabled'>&lt; Previous</span>")

    html.append(f"      <span><strong>Page {page_num} of {total_pages}</strong></span>")

    if page_num < total_pages:
        html.append(f"      <a href='page{page_num+1}.html'>Next &gt;</a>")
        html.append(f"      <a href='page{total_pages}.html'>Last &gt;&gt;</a>")
    else:
        html.append("      <span class='disabled'>Next &gt;</span>")
        html.append("      <span class='disabled'>Last &gt;&gt;</span>")
    html.append("    </div>")

    html.append("  </div>") # Close container
    html.append("</body>")
    html.append("</html>")

    # Write to file
    Path(output_file).write_text("\n".join(html))


def build_keyword_index_with_scores(index_data: dict, min_score: int = 0) -> Dict[str, List[Tuple[str, dict, int]]]:
    """Build inverted index mapping keywords to (message_id, image, score) tuples.

    Phase 6: Returns images sorted by score descending for each keyword.

    Args:
        index_data: Dictionary of messages from image index
        min_score: Minimum score threshold (default: 0, include all)

    Returns:
        Dictionary mapping keyword -> [(msg_id, image_dict, score), ...] sorted by score desc
    """
    keyword_index = {}

    for msg_id, msg_data in index_data.items():
        for image in msg_data.get("images", []):
            # Extract scored keywords: {"keyword": score, ...}
            for kw, score in image.get("keywords", {}).items():
                if score >= min_score:
                    kw_lower = kw.lower()
                    if kw_lower not in keyword_index:
                        keyword_index[kw_lower] = []

                    # Store (msg_id, image, score) tuple
                    keyword_index[kw_lower].append((msg_id, image, score))

    # Sort each keyword's images by score descending (highest first)
    for keyword in keyword_index:
        keyword_index[keyword].sort(key=lambda x: x[2], reverse=True)

    return keyword_index


def get_images_for_keyword(index_data: dict, keyword: str, min_score: int = 0) -> List[dict]:
    """Get all images for a keyword, sorted by score descending.

    Phase 6: Returns images with score, subject, message_id attached.

    Args:
        index_data: Dictionary of messages from image index
        keyword: Keyword to filter by (case-insensitive)
        min_score: Minimum score threshold (default: 0)

    Returns:
        List of image dictionaries with added metadata, sorted by score descending
    """
    images = []
    keyword_lower = keyword.lower()

    for msg_id, msg_data in index_data.items():
        metadata = msg_data.get("metadata", {})

        for image in msg_data.get("images", []):
            # Check if this image has the keyword (dict lookup is O(1))
            keywords_dict = image.get("keywords", {})
            # Check all keyword cases (keyword might be stored with different casing)
            score = None
            for kw, kw_score in keywords_dict.items():
                if kw.lower() == keyword_lower:
                    score = kw_score
                    break

            if score is not None and score >= min_score:
                # Create enriched image dict with metadata
                img_copy = image.copy()
                img_copy["message_id"] = msg_id
                img_copy["subject"] = metadata.get("subject", "")
                img_copy["score"] = score
                img_copy["original_url"] = image.get("url", "")
                img_copy["thumbnail_path"] = f"../thumbs/{image.get('local_filename', '')}"

                images.append(img_copy)

    # Sort by score descending (highest scores first)
    images.sort(key=lambda x: x["score"], reverse=True)

    return images


def filter_messages_by_keyword(index_data: dict, keyword: str) -> dict:
    """DEPRECATED: Use get_images_for_keyword instead.

    Filter messages that have a specific keyword.

    Args:
        index_data: Dictionary of messages from image index
        keyword: Keyword to filter by (case-insensitive)

    Returns:
        Dictionary of messages that have the keyword
    """
    filtered = {}
    keyword_lower = keyword.lower()

    for msg_id, msg_data in index_data.items():
        # Phase 6: Check image-level keywords
        for image in msg_data.get("images", []):
            for kw, score in image.get("keywords", {}).items():
                if kw.lower() == keyword_lower:
                    filtered[msg_id] = msg_data
                    break  # Found keyword in this message

    return filtered


def sanitize_keyword_for_filename(keyword: str) -> str:
    """Convert keyword to safe filename.

    Args:
        keyword: Keyword string

    Returns:
        Safe filename string (lowercase, spaces/special chars replaced with underscores)
    """
    import re
    # Convert to lowercase
    safe = keyword.lower()
    # Replace spaces and non-alphanumeric chars (except underscore) with underscore
    safe = re.sub(r'[^a-z0-9_]+', '_', safe)
    # Remove leading/trailing underscores
    safe = safe.strip('_')
    return safe


def generate_keyword_page(
    keyword: str,
    images: List[dict],
    page_num: int,
    total_pages: int,
    output_file: str
) -> None:
    """Generate a single keyword page.

    Args:
        keyword: The keyword for this page
        images: List of image dictionaries for this page
        page_num: Current page number (1-indexed)
        total_pages: Total number of pages for this keyword
        output_file: Path to write HTML file
    """
    safe_keyword = sanitize_keyword_for_filename(keyword)

    html = generate_html_head(f"{keyword} - Page {page_num}")

    # Breadcrumb
    html.append("    <p><a href='../index.html'>&larr; Back to Index</a></p>")
    html.append(f"    <h1>Keyword: {keyword}</h1>")

    # Top pagination
    html.append("    <div class='pagination'>")
    if page_num > 1:
        html.append(f"      <a href='{safe_keyword}_page1.html'>&lt;&lt; First</a>")
        html.append(f"      <a href='{safe_keyword}_page{page_num-1}.html'>&lt; Previous</a>")
    else:
        html.append("      <span class='disabled'>&lt;&lt; First</span>")
        html.append("      <span class='disabled'>&lt; Previous</span>")

    html.append(f"      <span><strong>Page {page_num} of {total_pages}</strong></span>")

    if page_num < total_pages:
        html.append(f"      <a href='{safe_keyword}_page{page_num+1}.html'>Next &gt;</a>")
        html.append(f"      <a href='{safe_keyword}_page{total_pages}.html'>Last &gt;&gt;</a>")
    else:
        html.append("      <span class='disabled'>Next &gt;</span>")
        html.append("      <span class='disabled'>Last &gt;&gt;</span>")
    html.append("    </div>")

    # Image grid using Skeleton CSS (6 columns = 2 Skeleton columns each)
    for i in range(0, len(images), 6):
        html.append("    <div class='row'>")
        for j in range(6):
            idx = i + j
            if idx < len(images):
                img = images[idx]
                html.append("      <div class='two columns img-cell'>")
                html.append(f"        <div class='subject'><a href='https://groups.google.com/g/cozy_builders/c/{img.get('message_id', '')}'>{img.get('subject', 'No subject')[:30]}</a></div>")
                html.append(f"        <div class='msg-id'>{img.get('message_id', '')}</div>")
                html.append(f"        <a href='{img.get('original_url', '')}'>")
                html.append(f"          <img src='{img.get('thumbnail_path', '')}' class='thumbnail' />")
                html.append("        </a>")
                # Phase 6: Display keywords with scores
                keywords_dict = img.get('keywords', {})
                if keywords_dict:
                    # Sort by score descending and take top 5
                    top_keywords = sorted(keywords_dict.items(), key=lambda x: x[1], reverse=True)[:5]
                    # Format as "keyword (score), keyword (score), ..."
                    kw_strings = [f"{kw} ({score})" for kw, score in top_keywords]
                    keywords_str = ", ".join(kw_strings)
                    if len(keywords_dict) > 5:
                        keywords_str += "..."
                else:
                    keywords_str = ""
                html.append(f"        <div class='keywords'>{keywords_str}</div>")
                html.append("      </div>")
        html.append("    </div>")

    # Bottom pagination (same as top)
    html.append("    <div class='pagination'>")
    if page_num > 1:
        html.append(f"      <a href='{safe_keyword}_page1.html'>&lt;&lt; First</a>")
        html.append(f"      <a href='{safe_keyword}_page{page_num-1}.html'>&lt; Previous</a>")
    else:
        html.append("      <span class='disabled'>&lt;&lt; First</span>")
        html.append("      <span class='disabled'>&lt; Previous</span>")

    html.append(f"      <span><strong>Page {page_num} of {total_pages}</strong></span>")

    if page_num < total_pages:
        html.append(f"      <a href='{safe_keyword}_page{page_num+1}.html'>Next &gt;</a>")
        html.append(f"      <a href='{safe_keyword}_page{total_pages}.html'>Last &gt;&gt;</a>")
    else:
        html.append("      <span class='disabled'>Next &gt;</span>")
        html.append("      <span class='disabled'>Last &gt;&gt;</span>")
    html.append("    </div>")

    html.append("  </div>") # Close container
    html.append("</body>")
    html.append("</html>")

    # Write to file
    Path(output_file).write_text("\n".join(html))
