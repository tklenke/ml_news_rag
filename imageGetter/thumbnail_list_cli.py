#!/usr/bin/env python3
# ABOUTME: CLI tool to write the list of the thumbnails the gallery index names, one per line
# ABOUTME: The list is what is uploaded to the server (rsync --files-from), so removed pictures stay off it

import argparse
import json
import sys
from pathlib import Path
from gallery_index import thumbnail_filenames


def main():
    parser = argparse.ArgumentParser(
        description='Write the list of the thumbnails the gallery index names',
        usage='%(prog)s [-h] GALLERY_INDEX THUMBS_DIR OUTPUT',
        epilog='''
Example:
  %(prog)s ../data/images/gallery261123b.idx ../data/images/thumbs \\
      ../data/images/thumbs261123b.txt
        '''
    )
    parser.add_argument('gallery_file', metavar='GALLERY_INDEX', help='Gallery index')
    parser.add_argument('thumbs_dir', metavar='THUMBS_DIR', help='Directory of the thumbnails')
    parser.add_argument('output_file', metavar='OUTPUT', help='List to create')

    args = parser.parse_args()

    for strPath in (args.gallery_file, args.thumbs_dir):
        if not Path(strPath).exists():
            print(f"Error: Not found: {strPath}", file=sys.stderr)
            return 1
    if Path(args.output_file).exists():
        print(f"Error: Already exists: {args.output_file}", file=sys.stderr)
        return 1

    with open(args.gallery_file, 'r', encoding='utf-8') as f:
        dctGallery = json.load(f)

    try:
        lstNames = thumbnail_filenames(dctGallery)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    lstMissing = [strName for strName in lstNames if not (Path(args.thumbs_dir) / strName).is_file()]
    if lstMissing:
        for strName in lstMissing:
            print(f"Error: Thumbnail not on disk: {strName}", file=sys.stderr)
        return 1

    with open(args.output_file, 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(f"{strName}\n" for strName in lstNames)

    intBytes = sum((Path(args.thumbs_dir) / strName).stat().st_size for strName in lstNames)
    print(f"Thumbnails listed:  {len(lstNames)}")
    print(f"Their size:         {intBytes / 1024 / 1024:.1f} MB")
    print(f"Wrote: {args.output_file}")
    return 0


if __name__ == "__main__":
    exit(main())
