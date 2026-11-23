#!/usr/bin/env python3
# ABOUTME: CLI tool for the one rename of downloaded images to names with the attachment id (D51)
# ABOUTME: Writes the map of present to new names, then renames pictures and thumbnails

import argparse
import json
import os
import sys
from pathlib import Path
from rename_images import plan_renames, apply_renames, count_shared_names


def main():
    parser = argparse.ArgumentParser(
        description='Rename downloaded images and their thumbnails to names with the attachment id',
        usage='%(prog)s [-h] [--dry-run] INDEX FULL_DIR THUMBS_DIR MAP_FILE',
        epilog='''
Example:
  %(prog)s input/czindex.idx ../data/images/full ../data/images/thumbs ../data/images/rename_map.json
        '''
    )

    parser.add_argument('index_file', metavar='INDEX',
                        help='Image index whose local_filename values are the names on disk')
    parser.add_argument('full_dir', metavar='FULL_DIR', help='Directory of the pictures')
    parser.add_argument('thumbs_dir', metavar='THUMBS_DIR', help='Directory of the thumbnails')
    parser.add_argument('map_file', metavar='MAP_FILE',
                        help='JSON file to write the map of present name to new name')
    parser.add_argument('--dry-run', action='store_true',
                        help='Report what would be renamed; write and rename nothing')

    args = parser.parse_args()

    for strPath in (args.index_file, args.full_dir, args.thumbs_dir):
        if not Path(strPath).exists():
            print(f"Error: Not found: {strPath}", file=sys.stderr)
            return 1
    if Path(args.map_file).exists():
        print(f"Error: Map file already exists, the rename may have been done: {args.map_file}",
              file=sys.stderr)
        return 1

    with open(args.index_file, 'r', encoding='utf-8') as f:
        dctIndex = json.load(f)
    setPresent = set(os.listdir(args.full_dir))

    intSharedNames, intSharedAttachments = count_shared_names(dctIndex)
    dctRenames = plan_renames(dctIndex, setPresent)
    lstLeftAlone = sorted(setPresent - set(dctRenames))

    print(f"Pictures on disk:            {len(setPresent)}")
    print(f"Pictures to rename:          {len(dctRenames)}")
    print(f"Names shared in the index:   {intSharedNames} names by {intSharedAttachments} attachments")
    print(f"Left as they are ({len(lstLeftAlone)}, no index entry has the name):")
    for strName in lstLeftAlone:
        print(f"  {strName}")

    if args.dry_run:
        print("DRY RUN - nothing written or renamed")
        return 0

    with open(args.map_file, 'w', encoding='utf-8') as f:
        json.dump(dctRenames, f, indent=1, ensure_ascii=False)
    print(f"Wrote map to: {args.map_file}")

    intPictures, intThumbs = apply_renames(dctRenames, args.full_dir, args.thumbs_dir)
    print(f"Pictures renamed:            {intPictures}")
    print(f"Thumbnails renamed:          {intThumbs}")
    return 0


if __name__ == "__main__":
    exit(main())
