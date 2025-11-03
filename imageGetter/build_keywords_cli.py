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
    parser.add_argument('--sample', type=int, default=100,
                        help='Number of messages to sample (default: 100)')
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
    print(f"Sample size: {args.sample} messages")
    print(f"Existing keywords: {args.existing}")
    print(f"Output: {args.output}")
    print()

    # Step 1: Load image index
    print("Loading image index...")
    image_index = load_image_index(args.index_file)
    total_messages = len(image_index)
    print(f"Loaded {total_messages} messages with images")
    print()

    # Step 2: Sample random messages
    print(f"Sampling {args.sample} random messages...")
    sampled_messages = sample_random_messages(image_index, args.sample)
    actual_sample_size = len(sampled_messages)
    print(f"Sampled {actual_sample_size} messages")
    print()

    # Step 3: Extract keywords from messages using LLM
    print("Extracting keywords using LLM...")
    print("(This may take a few minutes depending on sample size and model)")
    extractor = KeywordExtractor(model=args.model)

    all_keywords = []
    for message in tqdm(sampled_messages, desc="Processing messages"):
        message_text = extract_message_text(message)
        keywords = extractor.extract_keywords_from_message(message_text)
        all_keywords.append(keywords)

    print(f"\nExtracted keywords from {len(all_keywords)} messages")

    # Step 4: Aggregate keywords
    print("Aggregating keywords...")
    unique_keywords = aggregate_keywords(all_keywords)
    print(f"Found {len(unique_keywords)} unique keywords from LLM")

    # Step 5: Load existing keywords (if file exists)
    existing_keywords = []
    if Path(args.existing).exists():
        print(f"\nLoading existing keywords from {args.existing}...")
        existing_keywords = load_existing_keywords(args.existing)
        print(f"Loaded {len(existing_keywords)} existing keywords")
    else:
        print(f"\nExisting keywords file not found: {args.existing}")
        print("Starting with empty keyword list")

    # Step 6: Merge with existing keywords
    print("\nMerging with existing keywords...")
    merged_keywords = merge_keyword_lists(existing_keywords, unique_keywords)
    new_keywords_count = len(merged_keywords) - len(existing_keywords)
    print(f"Total keywords after merge: {len(merged_keywords)}")
    print(f"New keywords: {new_keywords_count}")

    # Step 7: Filter noise
    print("\nFiltering noise keywords...")
    filtered_keywords = filter_noise_keywords(merged_keywords)
    removed_count = len(merged_keywords) - len(filtered_keywords)
    print(f"Removed {removed_count} noise keywords")
    print(f"Filtered keywords: {len(filtered_keywords)}")

    # Step 8: Sort alphabetically
    sorted_keywords = sort_keywords(filtered_keywords)

    # Step 9: Write output
    print(f"\nWriting candidate keywords to {args.output}...")
    with open(args.output, 'w') as f:
        for keyword in sorted_keywords:
            f.write(f"{keyword}\n")

    print(f"Successfully wrote {len(sorted_keywords)} keywords to {args.output}")

    # Step 10: Statistics summary
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Messages sampled:           {actual_sample_size}")
    print(f"Keywords extracted (LLM):   {len(unique_keywords)}")
    print(f"Existing keywords:          {len(existing_keywords)}")
    print(f"Total after merge:          {len(merged_keywords)}")
    print(f"New keywords found:         {new_keywords_count}")
    print(f"Noise keywords removed:     {removed_count}")
    print(f"Final candidate keywords:   {len(sorted_keywords)}")
    print("="*60)
    print()
    print("Next steps:")
    print(f"1. Review {args.output}")
    print(f"2. Add good keywords to keywords_master.txt")
    print(f"3. Run again with different sample to find more keywords")

    return 0


if __name__ == "__main__":
    exit(main())
