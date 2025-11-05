#!/usr/bin/env python3
# ABOUTME: CLI tool to remove images from index based on removal list files
# ABOUTME: Reads images_to_remove*.txt files and creates cleaned index

import argparse
from pathlib import Path
from remove_images import load_index, load_removal_lists, remove_images_from_index, save_index


def main():
    parser = argparse.ArgumentParser(
        description='Remove images from index based on removal list files',
        usage='%(prog)s [-h] INPUT_INDEX OUTPUT_INDEX --remove-list FILE [FILE ...]',
        epilog='''
Examples:
  %(prog)s index.json cleaned.json --remove-list images_to_remove.txt
  %(prog)s index.json cleaned.json --remove-list page1.txt page2.txt page3.txt
  %(prog)s index.json cleaned.json --remove-list images_to_remove_page*.txt
        '''
    )

    parser.add_argument('index_file', metavar='INPUT_INDEX',
                        help='Path to input image index JSON file')
    parser.add_argument('output_file', metavar='OUTPUT_INDEX',
                        help='Path to output cleaned index JSON file')
    parser.add_argument('--remove-list', nargs='+', required=True,
                        metavar='FILE',
                        help='One or more removal list files (images_to_remove*.txt)')

    args = parser.parse_args()

    # Validate input file exists
    if not Path(args.index_file).exists():
        print(f"Error: Input file not found: {args.index_file}")
        return 1

    # Validate removal list files exist
    for removal_file in args.remove_list:
        if not Path(removal_file).exists():
            print(f"Error: Removal list file not found: {removal_file}")
            return 1

    print(f"Loading index from {args.index_file}...")
    index_data = load_index(args.index_file)
    total_messages = len(index_data)
    total_images_before = sum(len(m.get("images", [])) for m in index_data.values())
    print(f"Loaded {total_messages} messages with {total_images_before} images")
    print()

    print(f"Loading removal lists...")
    for removal_file in args.remove_list:
        print(f"  - {removal_file}")
    removal_set = load_removal_lists(args.remove_list)
    print(f"Loaded {len(removal_set)} unique filenames to remove")
    print()

    print("Removing images from index...")
    cleaned_index, stats = remove_images_from_index(index_data, removal_set)

    total_images_after = sum(len(m.get("images", [])) for m in cleaned_index.values())

    print()
    print("="*60)
    print("REMOVAL SUMMARY")
    print("="*60)
    print(f"Total messages:              {total_messages}")
    print(f"Messages affected:           {stats['messages_affected']}")
    print(f"Messages removed:            {stats['messages_removed']}")
    print()
    print(f"Images before:               {total_images_before}")
    print(f"Images removed:              {stats['images_removed']}")
    print(f"Images after:                {total_images_after}")
    print("="*60)
    print()

    print(f"Saving cleaned index to {args.output_file}...")
    save_index(cleaned_index, args.output_file)
    print(f"Cleaned index saved to: {args.output_file}")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
