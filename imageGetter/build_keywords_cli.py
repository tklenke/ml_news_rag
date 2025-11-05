#!/usr/bin/env python3
# ABOUTME: CLI tool for iterative keyword building using LLM
# ABOUTME: Samples messages from image_index.json and extracts keywords to build master list

import argparse
from pathlib import Path
from tqdm import tqdm
from keyword_builder import (
    load_image_index,
    sample_random_messages,
    extract_message_text,
    KeywordExtractor,
    aggregate_keywords,
    load_existing_keywords,
    merge_keyword_lists,
    filter_noise_keywords,
    sort_keywords
)
from llm_config import LLM_TIMEOUT


def main():
    parser = argparse.ArgumentParser(
        description='Build keyword list by sampling messages and extracting keywords with LLM',
        usage='%(prog)s [options] SOURCE [DEST]'
    )

    # Positional arguments
    parser.add_argument('source', metavar='SOURCE',
                        help='Path to input image index file')
    parser.add_argument('dest', metavar='DEST', nargs='?',
                        help='Path to output keywords file (default: SOURCE with _keywords.txt suffix)')

    # Optional arguments
    parser.add_argument('--sample', type=int, default=None,
                        help='Number of messages to sample (default: all messages)')
    parser.add_argument('--existing', type=str, default='../docs/input/keywords_seed.txt',
                        help='Existing keywords file to merge with (default: keywords_seed.txt)')
    parser.add_argument('--model', type=str, default=None,
                        help='Override LLM model from config')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed progress including message subjects')

    args = parser.parse_args()

    # Generate default output filename if not provided
    if args.dest is None:
        source_path = Path(args.source)
        args.dest = str(source_path.parent / f"{source_path.stem}_keywords.txt")

    # Validate index file exists
    if not Path(args.source).exists():
        print(f"Error: Input file not found: {args.source}")
        return 1

    print(f"Building keyword list from {args.source}")
    print(f"Output file: {args.dest}")
    if args.sample:
        print(f"Sample size: {args.sample} messages")
    else:
        print(f"Sample size: ALL messages (no limit)")
    print(f"Existing keywords: {args.existing}")
    print()

    # Step 1: Load image index
    print("Loading image index...")
    image_index = load_image_index(args.source)
    total_messages = len(image_index)
    print(f"Loaded {total_messages} messages with images")
    print()

    # Step 2: Load existing keywords FIRST (if file exists) - to provide context to LLM
    existing_keywords = []
    if Path(args.existing).exists():
        print("Loading existing keywords to provide context to LLM...")
        existing_keywords = load_existing_keywords(args.existing)
        print(f"Loaded {len(existing_keywords)} existing keywords")
    else:
        print(f"Existing keywords file not found: {args.existing}")
        print("Starting with empty keyword list (LLM will have no context)")
    print()

    # Step 3: Sample random messages (or use all if no sample specified)
    if args.sample:
        print(f"Sampling {args.sample} random messages...")
        sampled_messages = sample_random_messages(image_index, args.sample)
        actual_sample_size = len(sampled_messages)
        print(f"Sampled {actual_sample_size} messages")
    else:
        print(f"Processing ALL {total_messages} messages (no sampling)...")
        sampled_messages = list(image_index.values())
        actual_sample_size = len(sampled_messages)
        print(f"Processing {actual_sample_size} messages")
    print()

    # Step 4: Extract keywords from messages using LLM (with existing keywords as context)
    print("Extracting keywords using LLM...")
    print(f"Timeout per message: {LLM_TIMEOUT}s (configurable in llm_config.py)")
    print("(This may take a few minutes depending on sample size and model)")
    if existing_keywords:
        print(f"Providing {len(existing_keywords)} existing keywords to LLM for context")
    if args.verbose:
        print("Verbose mode enabled - showing message subjects and errors")
    extractor = KeywordExtractor(model=args.model)

    all_keywords = []
    failed_messages = []

    for i, message in enumerate(tqdm(sampled_messages, desc="Processing messages"), 1):
        message_text = extract_message_text(message)
        message_id = message.get('metadata', {}).get('message_id', 'unknown')
        subject = message.get('metadata', {}).get('subject', 'unknown')

        try:
            if args.verbose:
                tqdm.write(f"[{i}/{len(sampled_messages)}] Processing: {subject[:50]}...")

            keywords = extractor.extract_keywords_from_message(message_text, existing_keywords)
            all_keywords.append(keywords)

        except RuntimeError as e:
            error_msg = str(e)
            if args.verbose:
                tqdm.write(f"ERROR on message {message_id}: {error_msg}")
            else:
                tqdm.write(f"WARNING: Skipping message {message_id} due to error")

            failed_messages.append({
                'message_id': message_id,
                'subject': subject,
                'error': error_msg
            })
            # Continue processing other messages
            continue

    print(f"\nExtracted keywords from {len(all_keywords)} messages")
    if failed_messages:
        print(f"WARNING: {len(failed_messages)} messages failed (skipped)")
        if args.verbose:
            print("\nFailed messages:")
            for fm in failed_messages:
                print(f"  - {fm['message_id']}: {fm['subject'][:50]}")
                print(f"    Error: {fm['error'][:80]}")

    # Step 5: Aggregate keywords
    print("Aggregating keywords...")
    unique_keywords = aggregate_keywords(all_keywords)
    print(f"Found {len(unique_keywords)} unique keywords from LLM")

    # Step 6: Merge with existing keywords
    print("\nMerging with existing keywords...")
    merged_keywords = merge_keyword_lists(existing_keywords, unique_keywords)

    # Calculate new keywords count (for statistics)
    existing_keywords_lower = set(k.lower() for k in existing_keywords)
    new_keywords_count = sum(1 for k in merged_keywords if k not in existing_keywords_lower)

    print(f"Total keywords after merge: {len(merged_keywords)}")
    print(f"New keywords: {new_keywords_count}")

    # Step 7: Filter noise keywords
    print("\nFiltering noise keywords...")
    filtered_keywords = filter_noise_keywords(merged_keywords)
    removed_count = len(merged_keywords) - len(filtered_keywords)
    print(f"Removed {removed_count} noise keywords")
    print(f"Final filtered keywords: {len(filtered_keywords)}")

    # Step 8: Sort alphabetically
    sorted_keywords = sort_keywords(filtered_keywords)

    # Step 9: Write output file (alphabetically sorted)
    print(f"\nWriting alphabetically sorted keywords to {args.dest}...")
    with open(args.dest, 'w') as f:
        for keyword in sorted_keywords:
            f.write(f"{keyword}\n")
    print(f"Successfully wrote {len(sorted_keywords)} keywords to {args.dest}")

    # Step 10: Statistics summary
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Messages processed:          {actual_sample_size}")
    print(f"Messages failed:             {len(failed_messages)}")
    print(f"Messages succeeded:          {len(all_keywords)}")
    print(f"Keywords extracted (LLM):    {len(unique_keywords)}")
    print(f"Existing keywords:           {len(existing_keywords)}")
    print(f"Total after merge:           {len(merged_keywords)}")
    print(f"New keywords found:          {new_keywords_count}")
    print(f"Noise keywords removed:      {removed_count}")
    print(f"Final candidate keywords:    {len(sorted_keywords)}")
    print("="*60)
    print()
    print(f"Output written to: {args.dest} (alphabetically sorted)")
    print()
    print("Next steps:")
    print(f"1. Review {args.dest}")
    print(f"2. Add good keywords to keywords_master.txt")
    print(f"3. Run again with different sample to find more keywords")

    return 0


if __name__ == "__main__":
    exit(main())
