#!/usr/bin/env python3
# ABOUTME: CLI tool for the one loading of the 2025 removal lists into the decisions file
# ABOUTME: Carries the listed names through the rename map and decides by content hash

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from image_decisions import decisions_from_removals, save_decisions
from remove_images import load_removal_lists


def main():
    parser = argparse.ArgumentParser(
        description='Load the 2025 removal lists once into the decisions file',
        usage='%(prog)s [-h] INDEX RENAME_MAP DECISIONS SUGGESTIONS --remove-list FILE [FILE ...]',
        epilog='''
Example:
  %(prog)s ../data/images/index261123105058.idx ../data/images/rename_map.json \\
      image_decisions.json image_suggestions.json --remove-list input/remove_list/*.txt
        '''
    )
    parser.add_argument('index_file', metavar='INDEX', help='Measured image index (new names)')
    parser.add_argument('map_file', metavar='RENAME_MAP', help='Map of 2025 names to new names')
    parser.add_argument('decisions_file', metavar='DECISIONS', help='Decisions file to create')
    parser.add_argument('suggestions_file', metavar='SUGGESTIONS',
                        help='File to create with the contents removed in some copies only')
    parser.add_argument('--remove-list', nargs='+', required=True, metavar='FILE',
                        help='Removal list files of 2025 (images_to_remove*.txt)')

    args = parser.parse_args()

    for strPath in [args.index_file, args.map_file] + args.remove_list:
        if not Path(strPath).exists():
            print(f"Error: Not found: {strPath}", file=sys.stderr)
            return 1
    for strPath in (args.decisions_file, args.suggestions_file):
        if Path(strPath).exists():
            print(f"Error: Already exists, the lists have been loaded: {strPath}", file=sys.stderr)
            return 1

    with open(args.index_file, 'r', encoding='utf-8') as f:
        dctIndex = json.load(f)
    with open(args.map_file, 'r', encoding='utf-8') as f:
        dctRenames = json.load(f)

    setListed = load_removal_lists(args.remove_list)
    setRemoved = {dctRenames[strName] for strName in setListed if strName in dctRenames}
    lstNotOnDisk = sorted(setListed - set(dctRenames))

    dctDecisions, setMixed = decisions_from_removals(dctIndex, setRemoved)

    dctThreads = defaultdict(set)
    for strMessageId, dctEntry in dctIndex.items():
        for dctImage in dctEntry.get("images", []):
            if dctImage.get("content_hash") in setMixed:
                dctThreads[dctImage["content_hash"]].add(strMessageId)
    intMixedAcrossThreads = sum(1 for setIds in dctThreads.values() if len(setIds) > 1)

    save_decisions(args.decisions_file, dctDecisions)
    with open(args.suggestions_file, 'w', encoding='utf-8') as f:
        json.dump(sorted(setMixed), f, indent=1)
        f.write('\n')

    print(f"Names in the removal lists:          {len(setListed)}")
    print(f"  carried to a file on disk:         {len(setRemoved)}")
    print(f"  never on disk under that name:     {len(lstNotOnDisk)}")
    print(f"Contents decided 'remove':           {len(dctDecisions)}")
    print(f"Contents removed in some copies only: {len(setMixed)}")
    print(f"  of them in more than one thread:   {intMixedAcrossThreads}")
    print(f"Wrote: {args.decisions_file}, {args.suggestions_file}")
    return 0


if __name__ == "__main__":
    exit(main())
