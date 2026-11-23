#!/usr/bin/env python3
# ABOUTME: CLI tool to start the local review tool of image contents on 127.0.0.1
# ABOUTME: Each click in the browser is saved at once to the decisions file

import argparse
import json
import sys
from pathlib import Path
from review_images import ReviewState, make_server

DEFAULT_PORT = 8765


def main():
    parser = argparse.ArgumentParser(
        description='Serve the review tool of image contents on 127.0.0.1',
        usage='%(prog)s [-h] [--port PORT] INDEX FULL_DIR THUMBS_DIR DECISIONS SUGGESTIONS',
        epilog='''
Example:
  %(prog)s ../data/images/index261123105058.idx ../data/images/full ../data/images/thumbs \\
      image_decisions.json image_suggestions.json
        '''
    )
    parser.add_argument('index_file', metavar='INDEX', help='Measured image index')
    parser.add_argument('full_dir', metavar='FULL_DIR', help='Directory of the pictures')
    parser.add_argument('thumbs_dir', metavar='THUMBS_DIR', help='Directory of the thumbnails')
    parser.add_argument('decisions_file', metavar='DECISIONS', help='Decisions file, written at each click')
    parser.add_argument('suggestions_file', metavar='SUGGESTIONS',
                        help='Contents removed in some copies only in 2025, shown as suggested')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Port (default {DEFAULT_PORT})')

    args = parser.parse_args()

    for strPath in (args.index_file, args.full_dir, args.thumbs_dir, args.decisions_file,
                    args.suggestions_file):
        if not Path(strPath).exists():
            print(f"Error: Not found: {strPath}", file=sys.stderr)
            return 1

    with open(args.index_file, 'r', encoding='utf-8') as f:
        dctIndex = json.load(f)
    with open(args.suggestions_file, 'r', encoding='utf-8') as f:
        setSuggestions = set(json.load(f))

    state = ReviewState(dctIndex, setSuggestions, args.decisions_file)
    httpd = make_server(state, args.full_dir, args.thumbs_dir, "127.0.0.1", args.port)
    print(f"Review tool on http://127.0.0.1:{args.port}/  (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    exit(main())
