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


def main():
    parser = argparse.ArgumentParser(
        description='Build keyword list by sampling messages and extracting keywords with LLM'
    )

    # Positional argument
    parser.add_argument('index_file', metavar='INDEX_FILE',
                        help='Path to image_index.json')

    # Optional arguments
    parser.add_argument('--sample', type=int, default=None,
                        help='Number of messages to sample (default: all messages)')
    parser.add_argument('--existing', type=str, default='../docs/input/keywords_seed.txt',
                        help='Existing keywords file to merge with (default: keywords_seed.txt)')
    parser.add_argument('--output', type=str, default='keywords_candidates.txt',
                        help='Output file for candidate keywords (default: keywords_candidates.txt)')
    parser.add_argument('--model', type=str, default=None,
                        help='Override LLM model from config')

    args = parser.parse_args()

    # Validate index file exists
    if not Path(args.index_file).exists():
        print(f"Error: Index file not found: {args.index_file}")
        return 1

    print(f"Building keyword list from {args.index_file}")
    if args.sample:
        print(f"Sample size: {args.sample} messages")
    else:
        print(f"Sample size: ALL messages (no limit)")
    print(f"Existing keywords: {args.existing}")
    print(f"Output: {args.output}")
    print()

    # Step 1: Load image index
    print("Loading image index...")
    image_index = load_image_index(args.index_file)
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
    print("(This may take a few minutes depending on sample size and model)")
    if existing_keywords:
        print(f"Providing {len(existing_keywords)} existing keywords to LLM for context")
    extractor = KeywordExtractor(model=args.model)

    all_keywords = []
    for message in tqdm(sampled_messages, desc="Processing messages"):
        message_text = extract_message_text(message)
        keywords = extractor.extract_keywords_from_message(message_text, existing_keywords)
        all_keywords.append(keywords)

    print(f"\nExtracted keywords from {len(all_keywords)} messages")

    # Step 5: Aggregate keywords
    print("Aggregating keywords...")
    unique_keywords = aggregate_keywords(all_keywords)
    print(f"Found {len(unique_keywords)} unique keywords from LLM")

    # Step 6: Merge with existing keywords and identify new ones
    print("\nMerging with existing keywords...")
    merged_keywords = merge_keyword_lists(existing_keywords, unique_keywords)

    # Identify which keywords are new (not in existing)
    existing_keywords_lower = set(k.lower() for k in existing_keywords)
    new_keywords_only = set(k for k in merged_keywords if k not in existing_keywords_lower)

    print(f"Total keywords after merge: {len(merged_keywords)}")
    print(f"New keywords: {len(new_keywords_only)}")

    # Step 7: Filter noise from both merged and new-only keywords
    print("\nFiltering noise keywords...")
    filtered_keywords = filter_noise_keywords(merged_keywords)
    filtered_new_only = filter_noise_keywords(new_keywords_only)
    removed_count = len(merged_keywords) - len(filtered_keywords)
    print(f"Removed {removed_count} noise keywords from merged list")
    print(f"Filtered keywords (all): {len(filtered_keywords)}")
    print(f"Filtered keywords (new only): {len(filtered_new_only)}")

    # Step 8: Sort alphabetically
    sorted_keywords = sort_keywords(filtered_keywords)
    sorted_new_only = sort_keywords(filtered_new_only)

    # Step 9: Write output files
    print(f"\nWriting candidate keywords to {args.output}...")
    with open(args.output, 'w') as f:
        for keyword in sorted_keywords:
            f.write(f"{keyword}\n")
    print(f"Successfully wrote {len(sorted_keywords)} keywords to {args.output}")

    # Write new keywords to separate file
    new_output = args.output.replace('.txt', '_new.txt')
    print(f"\nWriting NEW keywords only to {new_output}...")
    with open(new_output, 'w') as f:
        for keyword in sorted_new_only:
            f.write(f"{keyword}\n")
    print(f"Successfully wrote {len(sorted_new_only)} NEW keywords to {new_output}")

    # Step 10: Statistics summary
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Messages sampled:               {actual_sample_size}")
    print(f"Keywords extracted (LLM):       {len(unique_keywords)}")
    print(f"Existing keywords:              {len(existing_keywords)}")
    print(f"Total after merge:              {len(merged_keywords)}")
    print(f"New keywords found:             {len(new_keywords_only)}")
    print(f"Noise keywords removed:         {removed_count}")
    print(f"Final candidate keywords (all): {len(sorted_keywords)}")
    print(f"Final new keywords only:        {len(sorted_new_only)}")
    print("="*60)
    print()
    print("Output files created:")
    print(f"  {args.output} - All keywords (existing + new, filtered)")
    print(f"  {new_output} - NEW keywords only (for easy review)")
    print()
    print("Next steps:")
    print(f"1. Review {new_output} to see what's new")
    print(f"2. Add good keywords from {new_output} to keywords_master.txt")
    print(f"3. Run again with different sample to find more keywords")

    return 0


if __name__ == "__main__":
    exit(main())
