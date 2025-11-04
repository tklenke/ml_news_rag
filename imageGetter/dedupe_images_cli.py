#!/usr/bin/env python3
# ABOUTME: CLI tool to deduplicate images in index based on file size
# ABOUTME: Removes duplicate images (same size) and missing files, prints statistics

import argparse
from pathlib import Path
from dedupe_images import load_index, dedupe_message_images, save_index


def main():
    parser = argparse.ArgumentParser(
        description='Deduplicate images within messages based on file size and remove missing files'
    )

    parser.add_argument('index_file',
                        help='Path to input image index JSON file')
    parser.add_argument('output_file',
                        help='Path to output deduped index JSON file')
    parser.add_argument('--images_dir', default='../data/images/full',
                        help='Path to images directory (default: ../data/images/full)')

    args = parser.parse_args()

    # Validate input file exists
    if not Path(args.index_file).exists():
        print(f"Error: Input file not found: {args.index_file}")
        return 1

    # Validate images directory exists
    if not Path(args.images_dir).exists():
        print(f"Error: Images directory not found: {args.images_dir}")
        return 1

    print(f"Loading index from {args.index_file}...")
    index_data = load_index(args.index_file)
    print(f"Loaded {len(index_data)} messages")
    print()

    # Process each message
    total_images_before = 0
    total_images_after = 0
    total_duplicates = 0
    total_missing = 0
    messages_affected = 0

    print("Processing messages...")
    for msg_id, message in index_data.items():
        images_before = len(message.get("images", []))
        total_images_before += images_before

        # Dedupe and remove missing
        deduped_message, stats = dedupe_message_images(message, args.images_dir)
        index_data[msg_id] = deduped_message

        images_after = len(deduped_message.get("images", []))
        total_images_after += images_after

        # Track statistics
        duplicates = stats["duplicates_removed"]
        missing = stats["missing_removed"]
        total_duplicates += duplicates
        total_missing += missing

        # Print output for affected messages
        if duplicates > 0 or missing > 0:
            messages_affected += 1
            subject = message.get("metadata", {}).get("subject", "Unknown")
            print(f"  {msg_id}: \"{subject[:60]}\"")
            if duplicates > 0:
                print(f"    - Removed {duplicates} duplicate image(s) (same file size)")
            if missing > 0:
                print(f"    - Removed {missing} missing image(s) (file not found)")

    # Save deduped index
    print()
    print(f"Saving deduped index to {args.output_file}...")
    save_index(index_data, args.output_file)

    # Print summary
    print()
    print("="*60)
    print("DEDUPLICATION SUMMARY")
    print("="*60)
    print(f"Total messages processed:      {len(index_data)}")
    print(f"Messages affected:             {messages_affected}")
    print()
    print(f"Total images before:           {total_images_before}")
    print(f"Total images after:            {total_images_after}")
    print(f"Total images removed:          {total_images_before - total_images_after}")
    print()
    print(f"  Duplicates removed:          {total_duplicates}")
    print(f"  Missing files removed:       {total_missing}")
    print("="*60)
    print()
    print(f"Deduped index saved to: {args.output_file}")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
