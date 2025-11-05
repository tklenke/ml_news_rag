#!/usr/bin/env python3
# ABOUTME: CLI tool to generate complete static HTML site from image index
# ABOUTME: Generates index, all images pages, and keyword-specific pages

import argparse
import sys
from pathlib import Path
from typing import List, Tuple
from generate_static_site import (
    load_index_data,
    count_images_per_keyword,
    sort_keywords_alphabetically,
    generate_index_html,
    sort_messages_by_date,
    group_messages_by_year,
    paginate_images,
    generate_all_images_page,
    filter_messages_by_keyword,
    sanitize_keyword_for_filename,
    generate_keyword_page,
)


def prepare_image_list(index_data: dict, base_path: str = "") -> List[dict]:
    """Prepare flat list of all images with metadata.

    Args:
        index_data: Dictionary of messages from image index
        base_path: Base path for image files (if needed)

    Returns:
        List of image dictionaries with message metadata
    """
    images = []

    for msg_id, msg_data in index_data.items():
        metadata = msg_data.get("metadata", {})
        keywords = msg_data.get("keywords", [])
        msg_images = msg_data.get("images", [])

        for img in msg_images:
            local_filename = img.get("local_filename", "")
            original_url = img.get("url", "")

            # Build thumbnail path - just "thumbs/filename_thumb.jpg"
            thumb_filename = local_filename.rsplit('.', 1)[0] + '_thumb.jpg'
            thumb_path = f"thumbs/{thumb_filename}"

            images.append({
                "message_id": msg_id,
                "subject": metadata.get("subject", "No subject"),
                "keywords": keywords,
                "thumbnail_path": thumb_path,
                "original_url": original_url,
                "date": metadata.get("date", ""),
                "year": extract_year_from_date(metadata.get("date", ""))
            })

    return images


def extract_year_from_date(date_str: str) -> int:
    """Extract year from date string."""
    from datetime import datetime
    try:
        dt = datetime.strptime(date_str, "%b %d, %Y")
        return dt.year
    except:
        return 1970


def generate_site(source: str, dest: str, images_per_page: int = 210):
    """Generate complete static site.

    Args:
        source: Path to image_index.json
        dest: Output directory for static site
        images_per_page: Number of images per page (default 210)
    """
    print(f"Loading index from {source}...")
    index_data = load_index_data(source)
    print(f"Loaded {len(index_data)} messages")

    # Create output directories
    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)
    (dest_path / "all").mkdir(exist_ok=True)
    (dest_path / "keywords").mkdir(exist_ok=True)

    # Generate index page
    print("\nGenerating index page...")
    keyword_counts = count_images_per_keyword(index_data)
    keyword_counts_sorted = sort_keywords_alphabetically(keyword_counts)
    generate_index_html(keyword_counts_sorted, str(dest_path / "index.html"))
    print(f"  Generated index.html with {len(keyword_counts_sorted)} keywords")

    # Prepare image list
    print("\nPreparing image list...")
    all_images = prepare_image_list(index_data)
    print(f"  Found {len(all_images)} total images")

    # Sort by date
    sorted_messages = sort_messages_by_date(index_data)
    year_groups = group_messages_by_year(sorted_messages)
    print(f"  Year distribution: {dict(year_groups)}")

    # Generate all images pages
    print("\nGenerating all images pages...")
    pages = paginate_images(all_images, images_per_page)
    total_pages = len(pages)

    for page_num, page_images in enumerate(pages, start=1):
        output_file = dest_path / "all" / f"page{page_num}.html"
        generate_all_images_page(
            images=page_images,
            page_num=page_num,
            total_pages=total_pages,
            output_file=str(output_file),
            year_groups=year_groups
        )
        print(f"  Generated all/page{page_num}.html ({len(page_images)} images)")

    # Generate keyword pages
    print("\nGenerating keyword pages...")
    for keyword, count in keyword_counts_sorted:
        # Filter messages and prepare images for this keyword
        filtered_messages = filter_messages_by_keyword(index_data, keyword)
        keyword_images = prepare_image_list(filtered_messages)

        # Paginate keyword images
        keyword_pages = paginate_images(keyword_images, images_per_page)
        keyword_total_pages = len(keyword_pages)

        safe_keyword = sanitize_keyword_for_filename(keyword)

        for page_num, page_images in enumerate(keyword_pages, start=1):
            output_file = dest_path / "keywords" / f"{safe_keyword}_page{page_num}.html"
            generate_keyword_page(
                keyword=keyword,
                images=page_images,
                page_num=page_num,
                total_pages=keyword_total_pages,
                output_file=str(output_file)
            )

        print(f"  Generated {keyword_total_pages} page(s) for '{keyword}' ({count} images)")

    print(f"\nSite generation complete!")
    print(f"Output: {dest}")
    print(f"  - index.html")
    print(f"  - all/page1.html ... all/page{total_pages}.html")
    print(f"  - keywords/ ({len(keyword_counts_sorted)} keywords)")


def main():
    parser = argparse.ArgumentParser(
        description="Generate static HTML site for browsing tagged images"
    )
    parser.add_argument(
        "source",
        help="Path to image_index.json file"
    )
    parser.add_argument(
        "dest",
        help="Output directory for static site"
    )
    parser.add_argument(
        "--images-per-page",
        type=int,
        default=210,
        help="Number of images per page (default: 210)"
    )

    args = parser.parse_args()

    # Validate source file
    if not Path(args.source).exists():
        print(f"Error: Source file not found: {args.source}", file=sys.stderr)
        sys.exit(1)

    generate_site(args.source, args.dest, args.images_per_page)


if __name__ == "__main__":
    main()
