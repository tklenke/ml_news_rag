#!/usr/bin/env python3
# ABOUTME: CLI tool for tagging messages with LLM keywords
# ABOUTME: Provides statistics for keywords with verbose mode support

import argparse
from pathlib import Path
from tag_messages import (
    load_image_index,
    load_keywords,
    tag_messages
)
from llm_config import LLM_TIMEOUT


def main():
    parser = argparse.ArgumentParser(
        description='Tag messages with LLM keywords'
    )

    # Positional argument
    parser.add_argument('index_file', metavar='INDEX_FILE',
                        help='Path to image index JSON file')

    # Optional arguments
    parser.add_argument('--keywords', type=str, default='aircraft_keywords.txt',
                        help='Keywords file to use (default: aircraft_keywords.txt)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Process only first N messages (default: all)')
    parser.add_argument('--overwrite', action='store_true',
                        help='Retag messages that already have llm_keywords')
    parser.add_argument('--model', type=str, default=None,
                        help='Override LLM model from llm_config.py')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed LLM responses for keyword tagging')

    args = parser.parse_args()

    # Validate files exist
    if not Path(args.index_file).exists():
        print(f"Error: Index file not found: {args.index_file}")
        return 1

    if not Path(args.keywords).exists():
        print(f"Error: Keywords file not found: {args.keywords}")
        return 1

    print(f"Tagging messages from {args.index_file}")
    print(f"Keywords: {args.keywords}")
    if args.limit:
        print(f"Limit: {args.limit} messages")
    else:
        print(f"Limit: ALL messages (no limit)")
    if args.overwrite:
        print(f"Overwrite: YES (retag existing)")
    else:
        print(f"Overwrite: NO (skip existing)")
    print()

    # Load data
    print("Loading image index...")
    index_data = load_image_index(args.index_file)
    total_messages = len(index_data)
    print(f"Loaded {total_messages} messages")

    print("Loading keywords...")
    keywords = load_keywords(args.keywords)
    print(f"Loaded {len(keywords)} keywords")
    print()

    # Count messages to process
    messages_to_process = 0
    already_tagged = 0
    for message in index_data.values():
        has_keywords = "llm_keywords" in message and message.get("llm_keywords") is not None
        if args.overwrite or not has_keywords:
            messages_to_process += 1
        else:
            already_tagged += 1

    if args.limit and args.limit < messages_to_process:
        messages_to_process = args.limit

    print(f"Messages to process: {messages_to_process}")
    if not args.overwrite:
        print(f"Already tagged (will skip): {already_tagged}")
    print()

    # Process messages
    print("Tagging messages with keywords...")
    print(f"LLM timeout per message: {LLM_TIMEOUT}s (configurable in llm_config.py)")
    if args.verbose:
        print("Verbose mode enabled - showing detailed LLM responses")
    print()

    # Call tag_messages() to process batch
    stats = tag_messages(
        index_file=args.index_file,
        keywords_file=args.keywords,
        overwrite=args.overwrite,
        limit=args.limit,
        model=args.model,
        verbose=args.verbose
    )

    processed_count = stats["processed"]
    skipped_count = stats["skipped"]
    error_count = stats["errors"]

    # Reload index to get updated data for statistics
    index_data = load_image_index(args.index_file)

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
        if "llm_keywords" in message:
            keyword_counts.append(len(message["llm_keywords"]))

    if keyword_counts:
        print(f"\nKeywords per message:")
        print(f"  Average:                   {sum(keyword_counts)/len(keyword_counts):.1f}")
        print(f"  Min:                       {min(keyword_counts)}")
        print(f"  Max:                       {max(keyword_counts)}")

    print("="*60)
    print()
    print(f"Results saved to: {args.index_file}")
    print()

    if not args.overwrite and skipped_count > 0:
        print(f"Note: {skipped_count} messages were skipped (already tagged).")
        print("Use --overwrite to retag all messages.")
        print()

    return 0


if __name__ == "__main__":
    exit(main())
