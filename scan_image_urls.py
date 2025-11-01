# ABOUTME: Utility script to scan all markdown files for image URLs
# ABOUTME: Outputs unique URL patterns to docs/input/ for manual review

import re
import os
from pathlib import Path
from collections import defaultdict

# Configuration
MSGS_DIR = Path("data/msgs_md")
OUTPUT_FILE = Path("docs/input/image_url_scan_results.txt")

# Regex to find URLs with image extensions
# Matches http:// or https:// followed by anything, then image extension
IMAGE_URL_PATTERN = re.compile(
    r'https?://[^\s\)]+\.(?:jpg|jpeg|png|gif|bmp)',
    re.IGNORECASE
)

def scan_markdown_files(directory):
    """Scan all markdown files and extract image URLs."""
    lstAllUrls = []
    intFilesScanned = 0
    intFilesWithImages = 0

    print(f"Scanning {directory}...")

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.md'):
                intFilesScanned += 1
                strFilePath = os.path.join(root, filename)

                try:
                    with open(strFilePath, 'r', encoding='utf-8', errors='replace') as f:
                        strContent = f.read()
                        lstMatches = IMAGE_URL_PATTERN.findall(strContent)

                        if lstMatches:
                            intFilesWithImages += 1
                            lstAllUrls.extend(lstMatches)
                except Exception as e:
                    print(f"Error reading {strFilePath}: {e}")

                if intFilesScanned % 100 == 0:
                    print(f"  Scanned {intFilesScanned} files...")

    print(f"\nScanned {intFilesScanned} total files")
    print(f"Found {intFilesWithImages} files with image URLs")
    print(f"Found {len(lstAllUrls)} total image URLs")

    return lstAllUrls

def analyze_urls(lstUrls):
    """Analyze URLs and group by pattern."""
    dctDomains = defaultdict(int)
    dctPaths = defaultdict(int)
    setUniqueUrls = set(lstUrls)

    for strUrl in lstUrls:
        # Extract domain
        match = re.match(r'https?://([^/]+)', strUrl)
        if match:
            strDomain = match.group(1)
            dctDomains[strDomain] += 1

        # Extract path pattern (first 2-3 path segments)
        match = re.match(r'(https?://[^/]+/[^/]+/[^/]*)', strUrl)
        if match:
            strPathPattern = match.group(1)
            dctPaths[strPathPattern] += 1

    return setUniqueUrls, dctDomains, dctPaths

def write_results(setUniqueUrls, dctDomains, dctPaths, strOutputFile):
    """Write results to output file."""
    with open(strOutputFile, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("IMAGE URL SCAN RESULTS\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Total unique URLs found: {len(setUniqueUrls)}\n\n")

        # Domain statistics
        f.write("=" * 80 + "\n")
        f.write("DOMAINS (sorted by count)\n")
        f.write("=" * 80 + "\n")
        for strDomain, intCount in sorted(dctDomains.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{intCount:5d}  {strDomain}\n")

        f.write("\n")

        # Path pattern statistics (top 50)
        f.write("=" * 80 + "\n")
        f.write("PATH PATTERNS (top 50, sorted by count)\n")
        f.write("=" * 80 + "\n")
        for strPath, intCount in sorted(dctPaths.items(), key=lambda x: x[1], reverse=True)[:50]:
            f.write(f"{intCount:5d}  {strPath}\n")

        f.write("\n")

        # All unique URLs (sorted)
        f.write("=" * 80 + "\n")
        f.write("ALL UNIQUE URLs (sorted alphabetically)\n")
        f.write("=" * 80 + "\n")
        for strUrl in sorted(setUniqueUrls):
            f.write(f"{strUrl}\n")

    print(f"\nResults written to: {strOutputFile}")

def main():
    """Main execution."""
    # Scan all markdown files
    lstAllUrls = scan_markdown_files(MSGS_DIR)

    if not lstAllUrls:
        print("No image URLs found!")
        return

    # Analyze URLs
    print("\nAnalyzing URLs...")
    setUniqueUrls, dctDomains, dctPaths = analyze_urls(lstAllUrls)

    print(f"Found {len(setUniqueUrls)} unique URLs")
    print(f"Found {len(dctDomains)} unique domains")

    # Write results
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    write_results(setUniqueUrls, dctDomains, dctPaths, OUTPUT_FILE)

    print("\nDone! Review the results file to identify URL patterns.")

if __name__ == "__main__":
    main()
