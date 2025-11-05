#!/usr/bin/env python3
# ABOUTME: CLI tool for tagging messages with keywords using search and stemming
# ABOUTME: Fast, deterministic alternative to LLM-based tagging

import argparse
from pathlib import Path
from search_tag_messages import (
    load_image_index,
    load_keywords,
    tag_messages
)


def main():
    parser = argparse.ArgumentParser(
        description='Tag messages with keywords using search and stemming (fast)',
        usage='%(prog)s [options] SOURCE [DEST]'
    )

    # Positional arguments
    parser.add_argument('source', metavar='SOURCE',
                        help='Path to input image index file')
    parser.add_argument('dest', metavar='DEST', nargs='?',
                        help='Path to output file (default: SOURCE with _tagged suffix)')

    # Optional arguments
    parser.add_argument('--keywords', type=str, default='aircraft_keywords.txt',
                        help='Keywords file to use (default: aircraft_keywords.txt)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Process only first N messages (default: all)')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed progress for each message')

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

    print("Loading keywords...")
    keywords = load_keywords(args.keywords)
    print(f"Loaded {len(keywords)} keywords")
    print()

    # Count messages with existing keywords
    messages_with_keywords = sum(1 for m in index_data.values() if m.get("keywords"))
    messages_to_process = len(index_data)

    if args.limit and args.limit < messages_to_process:
        messages_to_process = args.limit

    print(f"Messages to process: {messages_to_process}")
    if messages_with_keywords > 0:
        print(f"Messages with existing keywords: {messages_with_keywords} (will be merged)")
    print()

    # Process messages
    print("Tagging messages with keywords...")
    if args.verbose:
        print("Verbose mode enabled - showing progress for each message")
    print()

    # Call tag_messages() to process batch
    stats = tag_messages(
        index_file=args.source,
        keywords_file=args.keywords,
        output_file=args.dest,
        limit=args.limit,
        verbose=args.verbose
    )

    processed_count = stats["processed"]
    skipped_count = stats["skipped"]
    error_count = stats["errors"]

    # Reload index to get updated data for statistics
    index_data = load_image_index(args.dest)

    # Statistics
    print("\n" + "="*60)
    print("TAGGING STATISTICS")
    print("="*60)
    print(f"Total messages in index:     {total_messages}")
    print(f"Messages processed:          {processed_count}")
    print(f"Messages skipped:            {skipped_count}")
    print(f"Messages with errors:        {error_count}")

    # Keyword statistics
    keyword_counts = []
    for message in index_data.values():
        if "keywords" in message:
            keyword_counts.append(len(message["keywords"]))

    if keyword_counts:
        print(f"\nKeywords per message:")
        print(f"  Average:                   {sum(keyword_counts)/len(keyword_counts):.1f}")
        print(f"  Min:                       {min(keyword_counts)}")
        print(f"  Max:                       {max(keyword_counts)}")

    print("="*60)
    print()
    print(f"Results saved to: {args.dest}")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
