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
