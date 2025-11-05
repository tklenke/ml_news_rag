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


def count_images_per_keyword(index_data: dict) -> Dict[str, int]:
    """Count how many images are tagged with each keyword.

    Args:
        index_data: Dictionary of messages from image index

    Returns:
        Dictionary mapping keyword -> image count
    """
    keyword_counts = Counter()

    for message in index_data.values():
        # Get keywords for this message
        keywords = message.get("keywords", [])

        # Count images in this message
        num_images = len(message.get("images", []))

        # Add image count for each keyword
        for keyword in keywords:
            keyword_counts[keyword.lower()] += num_images

    return dict(keyword_counts)


def sort_keywords_alphabetically(keyword_counts: Dict[str, int]) -> List[Tuple[str, int]]:
    """Sort keywords alphabetically.

    Args:
        keyword_counts: Dictionary mapping keyword -> image count

    Returns:
        List of (keyword, count) tuples sorted alphabetically by keyword
    """
    return sorted(keyword_counts.items(), key=lambda x: x[0])


def generate_index_html(keyword_counts: List[Tuple[str, int]], output_file: str) -> None:
    """Generate index.html with links to all images and keyword pages.

    Args:
        keyword_counts: List of (keyword, count) tuples sorted alphabetically
        output_file: Path to write index.html
    """
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html>")
    html.append("<head>")
    html.append("<meta charset='utf-8'>")
    html.append("<title>Cozy Builders Image Database</title>")
    html.append("</head>")
    html.append("<body>")
    html.append("<h1>Cozy Builders Image Database</h1>")

    # Link to all images
    html.append("<p><a href='all/page1.html'>All Images (chronological)</a></p>")

    # Browse by keyword section
    html.append("<h2>Browse by Keyword</h2>")

    if keyword_counts:
        html.append("<ul>")
        for keyword, count in keyword_counts:
            # Sanitize keyword for filename
            safe_keyword = keyword.replace(" ", "_").lower()
            html.append(f"<li><a href='keywords/{safe_keyword}_page1.html'>{keyword} ({count} images)</a></li>")
        html.append("</ul>")
    else:
        html.append("<p>No keywords found.</p>")

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
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html>")
    html.append("<head>")
    html.append("<meta charset='utf-8'>")
    html.append("<title>All Images - Page {}</title>".format(page_num))
    html.append("</head>")
    html.append("<body>")

    # Breadcrumb
    html.append("<p><a href='../index.html'>&larr; Back to Index</a></p>")
    html.append("<h1>All Images (Chronological)</h1>")

    # Year headers (only show on first page for now)
    if page_num == 1 and year_groups:
        html.append("<div class='year-summary'>")
        for year, count in year_groups:
            html.append(f"<div>{year} ({count} images)</div>")
        html.append("</div>")

    # Top pagination
    html.append("<div class='pagination'>")
    if page_num > 1:
        html.append(f"<a href='page1.html'>&lt;&lt; First</a>")
        html.append(f"<a href='page{page_num-1}.html'>&lt; Previous</a>")
    else:
        html.append("<span class='disabled'>&lt;&lt; First</span>")
        html.append("<span class='disabled'>&lt; Previous</span>")

    html.append(f"<span>Page {page_num} of {total_pages}</span>")

    if page_num < total_pages:
        html.append(f"<a href='page{page_num+1}.html'>Next &gt;</a>")
        html.append(f"<a href='page{total_pages}.html'>Last &gt;&gt;</a>")
    else:
        html.append("<span class='disabled'>Next &gt;</span>")
        html.append("<span class='disabled'>Last &gt;&gt;</span>")
    html.append("</div>")

    # Image grid (6 columns)
    html.append("<table>")
    for i in range(0, len(images), 6):
        html.append("<tr>")
        for j in range(6):
            idx = i + j
            if idx < len(images):
                img = images[idx]
                html.append("<td>")
                html.append(f"<div class='subject'>{img.get('subject', 'No subject')}</div>")
                html.append(f"<div class='msg-id'>{img.get('message_id', '')}</div>")
                html.append(f"<a href='{img.get('full_path', '')}'>")
                html.append(f"<img src='{img.get('thumbnail_path', '')}' />")
                html.append("</a>")
                keywords_str = ", ".join(img.get('keywords', []))
                html.append(f"<div class='keywords'>keywords: {keywords_str}</div>")
                html.append("</td>")
            else:
                html.append("<td></td>")
        html.append("</tr>")
    html.append("</table>")

    # Bottom pagination (same as top)
    html.append("<div class='pagination'>")
    if page_num > 1:
        html.append(f"<a href='page1.html'>&lt;&lt; First</a>")
        html.append(f"<a href='page{page_num-1}.html'>&lt; Previous</a>")
    else:
        html.append("<span class='disabled'>&lt;&lt; First</span>")
        html.append("<span class='disabled'>&lt; Previous</span>")

    html.append(f"<span>Page {page_num} of {total_pages}</span>")

    if page_num < total_pages:
        html.append(f"<a href='page{page_num+1}.html'>Next &gt;</a>")
        html.append(f"<a href='page{total_pages}.html'>Last &gt;&gt;</a>")
    else:
        html.append("<span class='disabled'>Next &gt;</span>")
        html.append("<span class='disabled'>Last &gt;&gt;</span>")
    html.append("</div>")

    html.append("</body>")
    html.append("</html>")

    # Write to file
    Path(output_file).write_text("\n".join(html))
