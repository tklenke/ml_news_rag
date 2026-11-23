# ABOUTME: Command-line interface for batch downloading images from Google Groups
# ABOUTME: Uses Selenium with Chrome debug mode for authenticated downloads

import argparse
import sys
from pathlib import Path
from download_images import download_batch, DEFAULT_TIMEOUT_SECONDS


def main():
    """CLI entry point for batch image downloads."""
    parser = argparse.ArgumentParser(
        description="Download images from Google Groups using image index",
        usage="%(prog)s [-h] [--limit N] [--timeout S] --chromedriver PATH --log FILE SOURCE DEST"
    )
    parser.add_argument(
        "source",
        metavar="SOURCE",
        help="Path to image index file (*.idx or *.json)"
    )
    parser.add_argument(
        "dest",
        metavar="DEST",
        help="Directory to save downloaded images"
    )
    parser.add_argument(
        "--chromedriver",
        required=True,
        metavar="PATH",
        help="Path of chromedriver.exe"
    )
    parser.add_argument(
        "--log",
        required=True,
        metavar="FILE",
        help="Log file; lists each failed download and the totals"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        metavar="S",
        help=f"Seconds a request or page load may take (default {DEFAULT_TIMEOUT_SECONDS})"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on number of images to download (for testing)"
    )

    args = parser.parse_args()

    # Validate input file exists
    pathIndex = Path(args.source)
    if not pathIndex.exists():
        print(f"Error: Index file not found: {args.source}", file=sys.stderr)
        sys.exit(1)

    # Display configuration
    print("Image Batch Download")
    print("=" * 50)
    print(f"Index file: {args.source}")
    print(f"Output directory: {args.dest}")
    print(f"Chromedriver: {args.chromedriver}")
    print(f"Log file: {args.log}")
    print(f"Timeout: {args.timeout} s")
    if args.limit:
        print(f"Limit: {args.limit} images")
    print()

    # Remind user about Chrome debug mode
    print("IMPORTANT: Make sure Chrome is running with:")
    print("  chrome.exe --remote-debugging-port=9222")
    print("  (and logged into Google Groups)")
    print()

    # Download batch
    try:
        dctStats = download_batch(
            strIndexPath=args.source,
            strOutputDir=args.dest,
            intLimit=args.limit,
            seleniumDriver=None,  # Will create new driver
            strChromedriverPath=args.chromedriver,
            strLogPath=args.log,
            fltTimeout=args.timeout
        )

        # Display results
        print()
        print("=" * 50)
        print("Download Complete")
        print(f"  Total images: {dctStats['total']}")
        print(f"  Successful: {dctStats['success']}")
        print(f"  Skipped (already exist): {dctStats['skipped']}")
        print(f"  Failed: {dctStats['failed']}")
        print()

        # Exit with error code if any failed
        if dctStats['failed'] > 0:
            sys.exit(1)

    except Exception as e:
        print(f"Error during batch download: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
