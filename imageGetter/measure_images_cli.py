#!/usr/bin/env python3
# ABOUTME: CLI tool to measure downloaded images into the image index, run in WSL after a download
# ABOUTME: Writes size, width, height and content hash into each entry whose file is on disk

import argparse
import json
import sys
from pathlib import Path
from measure_images import measure_index


def main():
    parser = argparse.ArgumentParser(
        description='Measure downloaded images and write the measures into the image index',
        usage='%(prog)s [-h] INDEX FULL_DIR',
        epilog='''
Example:
  %(prog)s ../data/images/index261123120000.idx ../data/images/full
        '''
    )
    parser.add_argument('index_file', metavar='INDEX', help='Image index; measures are written into it')
    parser.add_argument('full_dir', metavar='FULL_DIR', help='Directory of the pictures')

    args = parser.parse_args()

    for strPath in (args.index_file, args.full_dir):
        if not Path(strPath).exists():
            print(f"Error: Not found: {strPath}", file=sys.stderr)
            return 1

    with open(args.index_file, 'r', encoding='utf-8') as f:
        dctIndex = json.load(f)

    dctStats = measure_index(dctIndex, args.full_dir)

    with open(args.index_file, 'w', encoding='utf-8') as f:
        json.dump(dctIndex, f, indent=1, ensure_ascii=False)

    print(f"Measured:                    {dctStats['measured']}")
    print(f"  of them not a picture:     {dctStats['not_a_picture']}")
    print(f"Already measured:            {dctStats['already_measured']}")
    print(f"File not on disk:            {dctStats['missing']}")
    print(f"Wrote index: {args.index_file}")
    return 0


if __name__ == "__main__":
    exit(main())
