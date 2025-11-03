#!/usr/bin/env python3
# ABOUTME: CLI tool for tagging messages with LLM keywords
# ABOUTME: Provides progress tracking, statistics, and resume capability

import argparse
from pathlib import Path
from tqdm import tqdm
from tag_messages import (
    load_image_index,
    load_keywords,
    tag_messages,
    extract_message_text,
    save_image_index
)
from llm_tagger import KeywordTagger
from llm_config import LLM_TIMEOUT


def main():
    parser = argparse.ArgumentParser(
        description='Tag messages with LLM keywords from master keyword list'
    )

    # Positional argument
    parser.add_argument('index_file', metavar='INDEX_FILE',
                        help='Path to image index JSON file')

    # Optional arguments
    parser.add_argument('--keywords', type=str, default='kw2.txt',
                        help='Keywords file to use (default: kw2.txt)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Process only first N messages (default: all)')
    parser.add_argument('--overwrite', action='store_true',
                        help='Retag messages that already have llm_keywords')
    parser.add_argument('--model', type=str, default=None,
                        help='Override LLM model from llm_config.py')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed progress including message subjects')

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

    # Initialize tagger
    print("Initializing LLM keyword tagger...")
    print(f"Timeout per message: {LLM_TIMEOUT}s (configurable in llm_config.py)")
    tagger = KeywordTagger()
    print()

    # Count messages to process
    messages_to_process = 0
    already_tagged = 0
    for message in index_data.values():
        if args.overwrite or "llm_keywords" not in message or not message["llm_keywords"]:
            messages_to_process += 1
        else:
            already_tagged += 1

    if args.limit and args.limit < messages_to_process:
        messages_to_process = args.limit

    print(f"Messages to process: {messages_to_process}")
    if not args.overwrite:
        print(f"Already tagged (will skip): {already_tagged}")
    print()

    # Process messages with progress bar
    print("Tagging messages...")
    if args.verbose:
        print("Verbose mode enabled - showing message subjects")

    processed_count = 0
    skipped_count = 0
    error_count = 0
    keywords_found = []

    for msg_id, message in tqdm(index_data.items(), desc="Processing messages", total=total_messages):
        # Check limit
        if args.limit and processed_count >= args.limit:
            break

        # Skip if already tagged (unless overwrite)
        if not args.overwrite and "llm_keywords" in message and message["llm_keywords"]:
            skipped_count += 1
            continue

        # Extract and tag
        message_text = extract_message_text(message)
        subject = message.get("metadata", {}).get("subject", "unknown")

        try:
            if args.verbose:
                tqdm.write(f"[{processed_count+1}/{messages_to_process}] Processing: {subject[:60]}...")

            matched_keywords = tagger.tag_message(message_text, keywords, model=args.model)
            message["llm_keywords"] = matched_keywords
            processed_count += 1
            keywords_found.append(len(matched_keywords))

            if args.verbose and matched_keywords:
                tqdm.write(f"  Found keywords: {', '.join(matched_keywords)}")

        except Exception as e:
            if args.verbose:
                tqdm.write(f"ERROR on message {msg_id}: {e}")
            else:
                tqdm.write(f"WARNING: Error tagging message {msg_id}, setting empty list")

            message["llm_keywords"] = []
            error_count += 1
            processed_count += 1
            keywords_found.append(0)

        # Auto-save every 50 messages
        if processed_count % 50 == 0:
            if args.verbose:
                tqdm.write(f"Auto-saving after {processed_count} messages...")
            save_image_index(index_data, args.index_file)

    # Final save
    print("\nSaving results...")
    save_image_index(index_data, args.index_file)

    # Statistics
    print("\n" + "="*60)
    print("TAGGING STATISTICS")
    print("="*60)
    print(f"Total messages in index:     {total_messages}")
    print(f"Messages processed:          {processed_count}")
    print(f"Messages skipped:            {skipped_count}")
    print(f"Messages with errors:        {error_count}")

    if keywords_found:
        avg_keywords = sum(keywords_found) / len(keywords_found)
        min_keywords = min(keywords_found)
        max_keywords = max(keywords_found)
        print(f"\nKeywords per message:")
        print(f"  Average:                   {avg_keywords:.1f}")
        print(f"  Min:                       {min_keywords}")
        print(f"  Max:                       {max_keywords}")

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
