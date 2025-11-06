#!/usr/bin/env python3
# ABOUTME: CLI tool for scoring keywords per image based on proximity to image URLs
# ABOUTME: Fast, deterministic proximity-based scoring with subject line bonuses

import argparse
import json
from pathlib import Path
from search_tag_messages import (
    load_image_index,
    load_keywords,
    tag_messages
)
from config import INVALID_KEYWORDS


def filter_to_vocabulary(index_data: dict, allowed_keywords: list) -> dict:
    """Filter image keywords to only those in allowed vocabulary.

    Handles scored keyword format: [keyword, score] tuples.

    Args:
        index_data: Dictionary of messages to filter
        allowed_keywords: List of allowed keywords

    Returns:
        Dictionary with statistics:
        - image_keywords_removed: Count of image keywords removed
    """
    # Create case-insensitive set of allowed keywords
    allowed_lower = {kw.lower() for kw in allowed_keywords}

    stats = {
        'image_keywords_removed': 0
    }

    # Process each message
    for message in index_data.values():
        # Filter image-level scored keywords
        for image in message.get('images', []):
            if 'keywords' in image:
                original_count = len(image['keywords'])
                # Filter [keyword, score] tuples
                image['keywords'] = [
                    (kw, score) for kw, score in image['keywords']
                    if kw.lower() in allowed_lower
                ]
                removed = original_count - len(image['keywords'])
                stats['image_keywords_removed'] += removed

    return stats


def clean_invalid_keywords_from_index(index_data: dict) -> dict:
    """Remove invalid keywords from index data (in-place).

    Cleans image-level scored keywords.

    Args:
        index_data: Dictionary of messages to clean

    Returns:
        Dictionary with statistics:
        - image_keywords_removed: Count of image keywords removed
    """
    # Create case-insensitive set of invalid keywords
    invalid_lower = {kw.lower() for kw in INVALID_KEYWORDS}

    stats = {
        'image_keywords_removed': 0
    }

    # Process each message
    for message in index_data.values():
        # Clean image-level scored keywords
        for image in message.get('images', []):
            if 'keywords' in image:
                original_count = len(image['keywords'])
                # Filter [keyword, score] tuples
                image['keywords'] = [
                    (kw, score) for kw, score in image['keywords']
                    if kw.lower() not in invalid_lower
                ]
                removed = original_count - len(image['keywords'])
                stats['image_keywords_removed'] += removed

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Score keywords per image based on proximity to image URLs (fast, proximity-based)',
        usage='%(prog)s [-h] [--keywords KEYWORDS] [--msgs-md-dir DIR] [--limit N] [--verbose] [--no-clean] SOURCE [DEST]'
    )

    # Positional arguments
    parser.add_argument('source', metavar='SOURCE',
                        help='Path to input image index file')
    parser.add_argument('dest', metavar='DEST', nargs='?',
                        help='Path to output file (default: SOURCE with _tagged suffix)')

    # Optional arguments
    parser.add_argument('--keywords', type=str, default='aircraft_keywords.txt',
                        help='Keywords file to use (default: aircraft_keywords.txt)')
    parser.add_argument('--msgs-md-dir', type=str, default='../data/msgs_md',
                        help='Path to msgs_md directory (default: ../data/msgs_md)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Process only first N messages (default: all)')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed progress for each message')
    parser.add_argument('--no-clean', action='store_true',
                        help='Skip cleaning invalid keywords before scoring (default: clean)')

    args = parser.parse_args()

    # Generate default output filename if not provided
    if args.dest is None:
        source_path = Path(args.source)
        args.dest = str(source_path.parent / f"{source_path.stem}_tagged{source_path.suffix}")

    # Validate files exist
    if not Path(args.source).exists():
        print(f"Error: Input file not found: {args.source}")
        return 1

    if not Path(args.keywords).exists():
        print(f"Error: Keywords file not found: {args.keywords}")
        return 1

    print(f"Tagging messages from {args.source}")
    print(f"Output file: {args.dest}")
    print(f"Keywords: {args.keywords}")
    if args.limit:
        print(f"Limit: {args.limit} messages")
    else:
        print(f"Limit: ALL messages (no limit)")
    print()

    # Load data
    print("Loading image index...")
    index_data = load_image_index(args.source)
    total_messages = len(index_data)
    print(f"Loaded {total_messages} messages")

    # Load keywords FIRST so we can use them for cleaning
    print("Loading keywords...")
    keywords = load_keywords(args.keywords)
    print(f"Loaded {len(keywords)} keywords")
    print()

    # Clean invalid keywords and restrict to vocabulary (unless --no-clean)
    if not args.no_clean:
        print("Cleaning invalid keywords from index...")
        clean_stats = clean_invalid_keywords_from_index(index_data)
        if clean_stats['image_keywords_removed'] > 0:
            print(f"  Removed {clean_stats['image_keywords_removed']} image keyword entries (invalid)")
        else:
            print("  No invalid keywords found")
        print()

        # Also filter against allowed vocabulary
        print("Restricting to allowed vocabulary...")
        vocab_stats = filter_to_vocabulary(index_data, keywords)
        if vocab_stats['image_keywords_removed'] > 0:
            print(f"  Removed {vocab_stats['image_keywords_removed']} image keyword entries (not in vocabulary)")
        else:
            print("  All keywords in vocabulary")

        # Save cleaned index to output file
        print(f"Saving cleaned index to {args.dest}...")
        with open(args.dest, 'w') as f:
            json.dump(index_data, f, indent=2)
        print()

    # Count messages and images
    messages_to_process = len(index_data)
    if args.limit and args.limit < messages_to_process:
        messages_to_process = args.limit

    print(f"Messages to process: {messages_to_process}")
    print()

    # Process messages
    print("Scoring keywords for images...")
    if args.verbose:
        print("Verbose mode enabled - showing progress for each message")
    print()

    # If we cleaned, tag from the cleaned output file, otherwise from source
    input_for_tagging = args.dest if not args.no_clean else args.source

    # Call tag_messages() to process batch
    stats = tag_messages(
        index_file=input_for_tagging,
        keywords_file=args.keywords,
        output_file=args.dest,
        limit=args.limit,
        verbose=args.verbose,
        keep_existing=False,  # Not used in image-level scoring
        msgs_md_dir=args.msgs_md_dir
    )

    processed_count = stats["processed"]
    images_scored = stats.get("images_scored", 0)
    error_count = stats["errors"]

    # Reload index to get updated data for statistics
    index_data = load_image_index(args.dest)

    # Statistics
    print("\n" + "="*60)
    print("KEYWORD SCORING STATISTICS")
    print("="*60)
    print(f"Total messages in index:     {total_messages}")
    print(f"Messages processed:          {processed_count}")
    print(f"Images scored:               {images_scored}")
    print(f"Messages with errors:        {error_count}")

    # Image keyword statistics
    keyword_counts = []
    all_scores = []
    images_with_keywords = 0

    for message in index_data.values():
        for image in message.get("images", []):
            if "keywords" in image and len(image["keywords"]) > 0:
                images_with_keywords += 1
                keyword_counts.append(len(image["keywords"]))
                # Extract scores from [keyword, score] tuples
                for kw, score in image["keywords"]:
                    all_scores.append(score)

    if keyword_counts:
        print(f"\nKeywords per image:")
        print(f"  Average:                   {sum(keyword_counts)/len(keyword_counts):.1f}")
        print(f"  Min:                       {min(keyword_counts)}")
        print(f"  Max:                       {max(keyword_counts)}")
        print(f"  Images with keywords:      {images_with_keywords}")

    if all_scores:
        print(f"\nScore range:")
        print(f"  Min:                       {min(all_scores)}")
        print(f"  Max:                       {max(all_scores)}")
        print(f"  Average:                   {sum(all_scores)/len(all_scores):.1f}")

    print("="*60)
    print()
    print(f"Results saved to: {args.dest}")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
