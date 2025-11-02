# ABOUTME: Extracts attachment image URLs from Cozy Builders markdown files
# ABOUTME: Filters to include only groups.google.com attachments, excludes profile photos and tracking pixels

import re
from typing import List, Dict
from urllib.parse import urlparse, parse_qs, unquote

# Blacklist: Filenames to exclude (UI elements, emoticons, signatures, temp files)
# These are non-content images that appear in email threads but aren't aircraft photos
BLACKLIST_EXACT = {
    # UI Elements and dividers
    'graycol.gif',
    'ecblank.gif',

    # Email signatures
    'UFAC Salutation.jpg',
    'UFACSalutation.jpg',

    # Animated GIFs / emoticons
    'Animation1.gif',
    'dancing-banana.gif',
    'dancing_cactus_lg_wht_3429.gif',
    'wow_waving_md_wht.gif',
    'soapbox.gif',
    'Emoticon1.gif',
    'EZ roll+circle.gif',
    'EZ%20roll%2Bcircle.gif',
    'Arrrgghh_11535.gif',

    # Temporary/embedded files
    'GPTempDownload.jpg',
    'kamp_kozy.bmp',
}

# Blacklist: Filename patterns to exclude (regex patterns)
BLACKLIST_PATTERNS = [
    r'^wlEmoticon-.*\.png$',           # Windows Live emoticons
    r'^~WRD\d+\.jpg$',                 # Word temp files
    r'^ole\d+\.bmp$',                  # OLE embedded objects
    r'^[0-9A-F]{3,4}\.gif$',           # Hex-named GIFs (tracking pixels)
    r'^[a-f0-9]{7}\.jpg$',             # 7-char hex filenames (generic/tracking)
    r'^[a-f0-9]{7}\.gif$',             # 7-char hex GIF filenames
]


def is_blacklisted(strFilename: str) -> bool:
    """
    Check if filename should be filtered out (junk/non-content images).

    Args:
        strFilename: Image filename to check

    Returns:
        True if filename is blacklisted, False otherwise
    """
    # Check exact matches
    if strFilename in BLACKLIST_EXACT:
        return True

    # Check pattern matches
    for strPattern in BLACKLIST_PATTERNS:
        if re.match(strPattern, strFilename, re.IGNORECASE):
            return True

    return False


def extract_image_urls(strMarkdownContent: str) -> List[Dict[str, str]]:
    """
    Extract attachment image URLs from markdown content.

    Filters to include only attachment images from:
    https://groups.google.com/group/cozy_builders/attach/...

    Excludes:
    - Profile photos (googleusercontent.com)
    - Tracking pixels (ci*.googleusercontent.com/proxy)
    - External site images
    - Logos and UI elements
    - Blacklisted files (emoticons, signatures, temp files, animated GIFs)

    Args:
        strMarkdownContent: Markdown file content as string

    Returns:
        List of dicts with keys: url, part, filename
        Example: [{"url": "https://...", "part": "0.1", "filename": "Image.jpeg"}]
    """
    # Regex to find all URLs with image extensions (including query parameters)
    # Matches http:// or https:// up to whitespace, ), or ]
    # This captures the full URL including query parameters
    IMAGE_URL_PATTERN = re.compile(
        r'https?://[^\s\)\]]+\.(?:jpg|jpeg|png|gif|bmp)(?:\?[^\s\)\]]*)?',
        re.IGNORECASE
    )

    # Find all image URLs
    lstAllUrls = IMAGE_URL_PATTERN.findall(strMarkdownContent)

    # Deduplicate URLs (same image may appear multiple times in markdown)
    setUniqueUrls = set(lstAllUrls)

    # Filter to only attachment URLs and extract metadata
    lstResults = []
    for strUrl in sorted(setUniqueUrls):  # Sort for consistent ordering
        if strUrl.startswith('https://groups.google.com/group/cozy_builders/attach/'):
            dctImageData = _parse_attachment_url(strUrl)
            if dctImageData:
                # Check if filename is blacklisted (junk/non-content)
                strFilename = dctImageData.get('filename', '')
                if not is_blacklisted(strFilename):
                    lstResults.append(dctImageData)
                # If blacklisted, silently skip (don't add to results)

    return lstResults


def extract_message_metadata(strMarkdownContent: str) -> Dict[str, str]:
    """
    Extract message metadata from Google Groups markdown content.

    Extracts:
    - message_id: From first line pattern [Original Message ID:...]
    - subject: From markdown heading (# Subject)
    - author: From profile section (### author name)
    - date: From timestamp line (MMM DD, YYYY)

    Args:
        strMarkdownContent: Markdown file content as string

    Returns:
        Dict with keys: message_id, subject, author, date
        Empty strings for missing fields
    """
    dctMetadata = {
        "message_id": "",
        "subject": "",
        "author": "",
        "date": ""
    }

    # Extract message ID from first line: [Original Message ID:A20JX9PGHII]
    matchMessageId = re.search(r'\[Original Message ID:([^\]]+)\]', strMarkdownContent)
    if matchMessageId:
        dctMetadata["message_id"] = matchMessageId.group(1)

    # Extract subject from markdown heading: # Subject
    matchSubject = re.search(r'^\s*#\s+(.+?)$', strMarkdownContent, re.MULTILINE)
    if matchSubject:
        dctMetadata["subject"] = matchSubject.group(1).strip()

    # Extract author from profile section: ### author name
    matchAuthor = re.search(r'###\s+(.+?)(?:\s*$)', strMarkdownContent, re.MULTILINE)
    if matchAuthor:
        dctMetadata["author"] = matchAuthor.group(1).strip()

    # Extract date from timestamp: > Feb 11, 2011, 2:21:35 AM
    # Capture only the date part: Feb 11, 2011
    matchDate = re.search(r'>\s+([A-Za-z]+\s+\d+,\s+\d{4})', strMarkdownContent)
    if matchDate:
        dctMetadata["date"] = matchDate.group(1)

    return dctMetadata


def _parse_attachment_url(strUrl: str) -> Dict[str, str]:
    """
    Parse an attachment URL to extract metadata.

    URL format:
    https://groups.google.com/group/cozy_builders/attach/{hash}/{filename}?part={part}&view=1

    Args:
        strUrl: Attachment URL

    Returns:
        Dict with url, part, filename or None if parsing fails
    """
    try:
        # Parse URL components
        parsed = urlparse(strUrl)

        # Extract filename from path
        # Path format: /group/cozy_builders/attach/{hash}/{filename}
        strPath = parsed.path
        lstPathParts = strPath.split('/')
        if len(lstPathParts) >= 5:
            strFilename = unquote(lstPathParts[-1])  # Last part is filename
        else:
            strFilename = "unknown"

        # Extract part number from query string
        dctQueryParams = parse_qs(parsed.query)
        strPart = dctQueryParams.get('part', [''])[0]

        return {
            "url": strUrl,
            "part": strPart,
            "filename": strFilename
        }
    except Exception as e:
        # If parsing fails, skip this URL
        return None


def generate_filename(strMessageId: str, strUrl: str, strPart: str) -> str:
    """
    Generate standardized local filename for downloaded image.

    Format: {message_id}_part{part}_{filename}
    - Replaces dots in part number with underscores (0.1 -> 0_1)
    - Replaces spaces in filename with underscores
    - Preserves file extension case
    - Preserves message_id case

    Args:
        strMessageId: Message ID (e.g., "a42YFDFx8WY")
        strUrl: Full image URL (used to extract filename if needed)
        strPart: Part number (e.g., "0.1", "0.2")

    Returns:
        Standardized filename (e.g., "a42YFDFx8WY_part0_1_Image.jpeg")
    """
    from urllib.parse import urlparse, unquote

    # Extract filename from URL
    parsed = urlparse(strUrl)
    strPath = parsed.path
    lstPathParts = strPath.split('/')
    if len(lstPathParts) >= 5:
        strFilename = unquote(lstPathParts[-1])  # Last part is filename
    else:
        strFilename = "unknown"

    # Replace dots in part number with underscores
    strPartNormalized = strPart.replace('.', '_')

    # Replace spaces in filename with underscores
    strFilenameNormalized = strFilename.replace(' ', '_')

    # Build final filename
    return f"{strMessageId}_part{strPartNormalized}_{strFilenameNormalized}"


def build_image_index(strPath: str) -> Dict[str, Dict]:
    """
    Build an image index from markdown file(s).

    Processes single file or all .md files in a directory.
    Extracts metadata and image URLs from each file.
    Skips files without attachment images.

    Args:
        strPath: Path to markdown file or directory

    Returns:
        Dict keyed by message_id with metadata and images list
        Format:
        {
          "A20JX9PGHII": {
            "metadata": {
              "message_id": "A20JX9PGHII",
              "subject": "WING LEADING EDGE MOLDS",
              "author": "ted davis",
              "date": "Feb 11, 2011"
            },
            "images": [
              {
                "url": "https://...",
                "part": "0.1",
                "filename": "image001.gif"
              }
            ]
          }
        }
    """
    from pathlib import Path

    dctIndex = {}
    pathInput = Path(strPath)

    # Determine if path is file or directory
    if pathInput.is_file():
        lstFiles = [pathInput]
    elif pathInput.is_dir():
        lstFiles = sorted(pathInput.rglob("*.md"))  # Recursive glob to search subdirectories
    else:
        return dctIndex  # Path doesn't exist, return empty

    # Process each markdown file
    for pathFile in lstFiles:
        try:
            # Read file content
            with open(pathFile, 'r', encoding='utf-8', errors='replace') as f:
                strContent = f.read()

            # Extract metadata
            dctMetadata = extract_message_metadata(strContent)

            # Extract image URLs
            lstImages = extract_image_urls(strContent)

            # Skip if no images or no message_id
            if not lstImages or not dctMetadata.get("message_id"):
                continue

            # Add local_filename to each image
            strMessageId = dctMetadata["message_id"]
            for dctImage in lstImages:
                strLocalFilename = generate_filename(
                    strMessageId,
                    dctImage["url"],
                    dctImage["part"]
                )
                dctImage["local_filename"] = strLocalFilename

            # Add to index keyed by message_id
            dctIndex[strMessageId] = {
                "metadata": dctMetadata,
                "images": lstImages
            }

        except Exception as e:
            # Skip files that can't be processed
            continue

    return dctIndex


if __name__ == "__main__":
    import argparse
    import json
    import sys
    from datetime import datetime
    from collections import Counter

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Extract image URLs and metadata from Cozy Builders markdown files",
        usage="%(prog)s [options] SOURCE DEST"
    )
    parser.add_argument(
        "source",
        metavar="SOURCE",
        help="Path to markdown file or directory"
    )
    parser.add_argument(
        "dest",
        metavar="DEST",
        help="Output directory for index and stats files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview results without writing to file"
    )

    args = parser.parse_args()

    # Check if input path exists
    from pathlib import Path
    pathInput = Path(args.source)
    if not pathInput.exists():
        print(f"Error: Input path does not exist: {args.source}", file=sys.stderr)
        sys.exit(1)

    # Check if output directory exists, create if needed
    pathOutputDir = Path(args.dest)
    if not args.dry_run:
        pathOutputDir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp-based filenames
    strTimestamp = datetime.now().strftime("%y%m%d%H%M%S")
    strIndexFilename = f"index{strTimestamp}.idx"
    strStatsFilename = f"index_stats_{strTimestamp}.txt"
    pathIndexFile = pathOutputDir / strIndexFilename
    pathStatsFile = pathOutputDir / strStatsFilename

    # Build image index
    print(f"Processing: {args.source}")
    print()

    try:
        dctIndex = build_image_index(args.source)
    except Exception as e:
        print(f"Error building index: {e}", file=sys.stderr)
        sys.exit(1)

    # Calculate statistics and track filename duplicates
    intTotalMessages = len(dctIndex)
    intTotalImages = 0
    dctFilenameCounts = Counter()  # Track filename occurrences

    for dctEntry in dctIndex.values():
        for dctImage in dctEntry["images"]:
            intTotalImages += 1
            # Track original filename from URL
            strFilename = dctImage["filename"]
            dctFilenameCounts[strFilename] += 1

    # Display results
    print(f"Results:")
    print(f"  Messages with images: {intTotalMessages}")
    print(f"  Total image URLs: {intTotalImages}")
    print(f"  Unique filenames: {len(dctFilenameCounts)}")
    print()

    # Show sample entries (first 3 message IDs)
    if intTotalMessages > 0:
        print("Sample entries:")
        for idx, (strMsgId, dctEntry) in enumerate(list(dctIndex.items())[:3]):
            print(f"  {strMsgId}:")
            print(f"    Subject: {dctEntry['metadata']['subject']}")
            print(f"    Images: {len(dctEntry['images'])}")
        if intTotalMessages > 3:
            print(f"  ... and {intTotalMessages - 3} more")
        print()

    # Write output or dry-run
    if args.dry_run:
        print("DRY RUN - No files written")
        print(f"Would write index to: {pathIndexFile}")
        print(f"Would write stats to: {pathStatsFile}")
    else:
        try:
            # Write index JSON
            with open(pathIndexFile, 'w', encoding='utf-8') as f:
                json.dump(dctIndex, f, indent=2, ensure_ascii=False)

            print(f"Wrote index to: {pathIndexFile}")
            print(f"Index file size: {pathIndexFile.stat().st_size} bytes")
            print()

            # Write stats file
            with open(pathStatsFile, 'w', encoding='utf-8') as f:
                f.write("=== Image Filename Statistics ===\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Source: {args.source}\n")
                f.write(f"\nTotal images: {intTotalImages}\n")
                f.write(f"Unique filenames: {len(dctFilenameCounts)}\n")
                f.write("\n")

                # Separate duplicates (count > 1) from uniques (count = 1)
                lstDuplicates = [(name, count) for name, count in dctFilenameCounts.items() if count > 1]
                lstUniques = [(name, count) for name, count in dctFilenameCounts.items() if count == 1]

                # Sort duplicates by count descending, then by name
                lstDuplicates.sort(key=lambda x: (-x[1], x[0]))

                # Sort uniques alphabetically
                lstUniques.sort(key=lambda x: x[0])

                # Write duplicates section
                if lstDuplicates:
                    f.write(f"=== Duplicate Filenames ({len(lstDuplicates)}) ===\n")
                    f.write("Count  Filename\n")
                    f.write("-" * 60 + "\n")
                    for strFilename, intCount in lstDuplicates:
                        f.write(f"{intCount:5d}  {strFilename}\n")
                    f.write("\n")

                # Write uniques section
                if lstUniques:
                    f.write(f"=== Unique Filenames ({len(lstUniques)}) ===\n")
                    for strFilename, intCount in lstUniques:
                        f.write(f"{strFilename}\n")

            print(f"Wrote stats to: {pathStatsFile}")
            print(f"Stats file size: {pathStatsFile.stat().st_size} bytes")

        except Exception as e:
            print(f"Error writing output files: {e}", file=sys.stderr)
            sys.exit(1)

    print()
    print("Done!")
