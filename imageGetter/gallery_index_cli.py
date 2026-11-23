#!/usr/bin/env python3
# ABOUTME: CLI tool to make the index the gallery reads, after measuring and Tom's review
# ABOUTME: Reads the full image index and the decisions file, writes a new gallery index and reports counts

import argparse
import json
import sys
from pathlib import Path
from gallery_index import build_gallery_index
from image_decisions import load_decisions


def main():
    parser = argparse.ArgumentParser(
        description='Make the index the gallery reads from the full image index and the decisions',
        usage='%(prog)s [-h] INDEX FULL_DIR DECISIONS OUTPUT',
        epilog='''
Example:
  %(prog)s ../data/images/index261123105058.idx ../data/images/full \\
      image_decisions.json ../data/images/gallery261123.idx
        '''
    )
    parser.add_argument('index_file', metavar='INDEX', help='Measured image index')
    parser.add_argument('full_dir', metavar='FULL_DIR', help='Directory of the pictures')
    parser.add_argument('decisions_file', metavar='DECISIONS', help='Decisions file')
    parser.add_argument('output_file', metavar='OUTPUT', help='Gallery index to create')

    args = parser.parse_args()

    for strPath in (args.index_file, args.full_dir, args.decisions_file):
        if not Path(strPath).exists():
            print(f"Error: Not found: {strPath}", file=sys.stderr)
            return 1
    if Path(args.output_file).exists():
        print(f"Error: Already exists: {args.output_file}", file=sys.stderr)
        return 1

    with open(args.index_file, 'r', encoding='utf-8') as f:
        dctIndex = json.load(f)

    try:
        dctGallery, dctStats = build_gallery_index(dctIndex, load_decisions(args.decisions_file), args.full_dir)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(dctGallery, f, indent=1, ensure_ascii=False)

    print(f"Threads in the gallery index:    {dctStats['threads']}")
    print(f"Pictures in the gallery index:   {dctStats['pictures']}")
    print(f"  of them contents undecided:    {dctStats['undecided_contents']}")
    print(f"Dropped, marked remove:          {dctStats['removed']}")
    print(f"Dropped, file not on disk:       {dctStats['missing']}")
    print(f"Dropped, repeated in a thread:   {dctStats['repeated_in_thread']}")
    print(f"Wrote: {args.output_file}")
    return 0


if __name__ == "__main__":
    exit(main())
