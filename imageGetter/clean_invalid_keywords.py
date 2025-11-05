#!/usr/bin/env python3
# ABOUTME: Remove invalid keywords from image index file
# ABOUTME: Filters both message-level and image-level keywords against INVALID_KEYWORDS list

import json
import argparse
from pathlib import Path
from llm_config import INVALID_KEYWORDS


def clean_invalid_keywords(index_file: str, output_file: str = None) -> dict:
    """Remove invalid keywords from index file.

    Args:
        index_file: Path to input index file
        output_file: Path to output file (default: overwrite input)

    Returns:
        Dictionary with statistics:
        - messages_processed: Number of messages checked
        - message_keywords_removed: Count of message keywords removed
        - image_keywords_removed: Count of image keywords removed
    """
    # Load index
    with open(index_file, 'r') as f:
        index_data = json.load(f)

    # Create case-insensitive set of invalid keywords
    invalid_lower = {kw.lower() for kw in INVALID_KEYWORDS}

    stats = {
        'messages_processed': 0,
        'message_keywords_removed': 0,
        'image_keywords_removed': 0
    }

    # Process each message
    for msg_id, message in index_data.items():
        stats['messages_processed'] += 1

        # Clean message-level keywords
        if 'keywords' in message:
            original_count = len(message['keywords'])
            message['keywords'] = [
                kw for kw in message['keywords']
                if kw.lower() not in invalid_lower
            ]
            removed = original_count - len(message['keywords'])
            stats['message_keywords_removed'] += removed

        # Clean image-level keywords
        for image in message.get('images', []):
            if 'keywords' in image:
                original_count = len(image['keywords'])
                image['keywords'] = [
                    kw for kw in image['keywords']
                    if kw.lower() not in invalid_lower
                ]
                removed = original_count - len(image['keywords'])
                stats['image_keywords_removed'] += removed

    # Save result
    if output_file is None:
        output_file = index_file

    with open(output_file, 'w') as f:
        json.dump(index_data, f, indent=2)

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Remove invalid keywords from image index',
        usage='%(prog)s SOURCE [DEST]'
    )

    parser.add_argument('source', metavar='SOURCE',
                       help='Path to input image index file')
    parser.add_argument('dest', metavar='DEST', nargs='?',
                       help='Path to output file (default: overwrite SOURCE)')

    args = parser.parse_args()

    print(f"Cleaning invalid keywords from {args.source}...")
    stats = clean_invalid_keywords(args.source, args.dest)

    output_file = args.dest if args.dest else args.source
    print(f"\n{'='*60}")
    print("CLEANUP STATISTICS")
    print(f"{'='*60}")
    print(f"Messages processed:           {stats['messages_processed']}")
    print(f"Message keywords removed:     {stats['message_keywords_removed']}")
    print(f"Image keywords removed:       {stats['image_keywords_removed']}")
    print(f"Total keywords removed:       {stats['message_keywords_removed'] + stats['image_keywords_removed']}")
    print(f"{'='*60}")
    print(f"\nCleaned index saved to: {output_file}")


if __name__ == "__main__":
    main()
