#!/usr/bin/env python3
# ABOUTME: Analyze keyword statistics from tagged image index
# ABOUTME: Generates text report and interactive HTML view with checkbox selection and export

import json
import argparse
from pathlib import Path
from collections import Counter
from datetime import datetime
from llm_config import INVALID_KEYWORDS


def load_index(index_file: str, limit: int = None) -> dict:
    """Load image index from JSON file.

    Args:
        index_file: Path to image index JSON file
        limit: Optional limit on number of messages to load

    Returns:
        Dictionary of messages (limited if specified)
    """
    with open(index_file, 'r') as f:
        data = json.load(f)

    if limit:
        # Limit to first N messages
        limited_data = {}
        for i, (key, value) in enumerate(data.items()):
            if i >= limit:
                break
            limited_data[key] = value
        return limited_data

    return data


def analyze_keywords(index_data: dict) -> Counter:
    """Analyze keyword frequencies across all messages.

    Combines both message keywords and image keywords.
    Filters out invalid keywords from the count.
    """
    keyword_counter = Counter()

    # Build set of invalid keywords (case-insensitive)
    invalid_lower = {kw.lower() for kw in INVALID_KEYWORDS}

    for message in index_data.values():
        # Collect message keywords
        msg_keywords = message.get("keywords", [])
        for kw in msg_keywords:
            # Skip invalid keywords
            if kw.lower() not in invalid_lower:
                keyword_counter[kw.lower()] += 1

        # Collect image keywords
        images = message.get("images", [])
        for image in images:
            keywords = image.get("keywords", [])
            for kw in keywords:
                # Skip invalid keywords
                if kw.lower() not in invalid_lower:
                    keyword_counter[kw.lower()] += 1

    return keyword_counter




def format_keyword_statistics(keyword_counter: Counter) -> str:
    """Format keyword statistics with alphabetical sorting for count >= 2."""
    output = []
    output.append("=" * 70)
    output.append("KEYWORD STATISTICS")
    output.append("=" * 70)
    output.append(f"Total unique keywords: {len(keyword_counter)}")
    output.append(f"Total keyword occurrences: {sum(keyword_counter.values())}")
    output.append("")

    # Separate keywords by frequency
    freq_1 = []
    freq_2_plus = []

    for keyword, count in keyword_counter.items():
        if count == 1:
            freq_1.append(keyword)
        else:
            freq_2_plus.append((keyword, count))

    # Sort freq 2+ by count descending, then alphabetically
    freq_2_plus.sort(key=lambda x: (-x[1], x[0]))

    # Sort freq 1 alphabetically
    freq_1.sort()

    # Output keywords with count >= 2
    if freq_2_plus:
        output.append(f"Keywords with 2+ occurrences ({len(freq_2_plus)} keywords):")
        output.append("-" * 70)
        for keyword, count in freq_2_plus:
            output.append(f"  {count:4d}  {keyword}")
        output.append("")

    # Output keywords with count = 1
    if freq_1:
        output.append(f"Keywords with 1 occurrence ({len(freq_1)} keywords):")
        output.append("-" * 70)
        # Print in columns (4 columns)
        col_width = 18
        cols = 4
        for i in range(0, len(freq_1), cols):
            row = freq_1[i:i+cols]
            output.append("  " + "".join(f"{kw:<{col_width}}" for kw in row))
        output.append("")

    return "\n".join(output)




def format_summary(index_data: dict, keyword_counter: Counter) -> str:
    """Format summary statistics."""
    output = []
    output.append("=" * 70)
    output.append("SUMMARY")
    output.append("=" * 70)

    total_messages = len(index_data)
    messages_with_keywords = sum(1 for m in index_data.values() if m.get("keywords"))
    messages_with_image_keywords = sum(1 for m in index_data.values() if any(img.get("keywords") for img in m.get("images", [])))

    output.append(f"Total messages: {total_messages}")
    output.append(f"Messages with keywords: {messages_with_keywords}")
    output.append(f"Messages with image keywords: {messages_with_image_keywords}")
    output.append("")
    output.append(f"Total unique keywords: {len(keyword_counter)}")
    output.append("")

    # Averages
    if messages_with_keywords > 0 or messages_with_image_keywords > 0:
        total_kw_count = sum(keyword_counter.values())
        avg_keywords = total_kw_count / total_messages
        output.append(f"Average keywords per message: {avg_keywords:.2f}")

    output.append("")

    return "\n".join(output)


def generate_html_page(images: list, thumb_dir: str, output_file: str,
                       page_num: int, total_pages: int, base_filename: str):
    """Generate a single HTML page with pagination.

    Args:
        images: List of image dictionaries for this page
        thumb_dir: Relative path to thumbnail directory
        output_file: Path to output HTML file
        page_num: Current page number (1-indexed)
        total_pages: Total number of pages
        base_filename: Base filename for generating page links
    """
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html>")
    html.append("<head>")
    html.append("  <meta charset='UTF-8'>")
    html.append(f"  <title>Tag View - Page {page_num} of {total_pages}</title>")
    html.append("  <style>")
    html.append("    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }")
    html.append("    h1 { color: #333; }")
    html.append("    .info { background: #fff; padding: 15px; margin-bottom: 20px; border-radius: 5px; }")
    html.append("    .pagination { background: #fff; padding: 15px; margin-bottom: 20px; border-radius: 5px; ")
    html.append("                  text-align: center; font-size: 16px; }")
    html.append("    .pagination a { margin: 0 5px; padding: 8px 12px; background: #007bff; color: white; ")
    html.append("                    text-decoration: none; border-radius: 4px; }")
    html.append("    .pagination a:hover { background: #0056b3; }")
    html.append("    .pagination a.disabled { background: #ccc; cursor: not-allowed; pointer-events: none; }")
    html.append("    .pagination .current { margin: 0 10px; font-weight: bold; }")
    html.append("    .toolbar { background: #fff; padding: 15px; margin-bottom: 20px; border-radius: 5px; ")
    html.append("               display: flex; gap: 10px; align-items: center; }")
    html.append("    .toolbar button { padding: 8px 16px; background: #007bff; color: white; border: none; ")
    html.append("                      border-radius: 4px; cursor: pointer; font-size: 14px; }")
    html.append("    .toolbar button:hover { background: #0056b3; }")
    html.append("    .toolbar button.secondary { background: #6c757d; }")
    html.append("    .toolbar button.secondary:hover { background: #545b62; }")
    html.append("    .toolbar button.export { background: #28a745; }")
    html.append("    .toolbar button.export:hover { background: #1e7e34; }")
    html.append("    .counter { font-weight: bold; color: #333; margin-left: auto; }")
    html.append("    table { border-collapse: collapse; background: #fff; }")
    html.append("    td { padding: 10px; vertical-align: top; border: 1px solid #ddd; width: 210px; position: relative; }")
    html.append("    td.selected { background: #ffe6e6; border-color: #ff6b6b; }")
    html.append("    .image-container { position: relative; }")
    html.append("    .remove-checkbox { position: absolute; top: 5px; left: 5px; width: 20px; height: 20px; ")
    html.append("                       cursor: pointer; z-index: 10; }")
    html.append("    img { width: 200px; height: auto; display: block; margin-bottom: 10px; }")
    html.append("    pre { background: #f8f8f8; padding: 8px; font-size: 10px; ")
    html.append("          border: 1px solid #ddd; border-radius: 3px; overflow-x: auto; margin: 0; ")
    html.append("          word-wrap: break-word; white-space: pre-wrap; }")
    html.append("    .subject { font-size: 11px; color: #666; margin-bottom: 5px; font-style: italic; ")
    html.append("               word-wrap: break-word; }")
    html.append("    .msg-id { font-size: 9px; color: #999; margin-bottom: 10px; }")
    html.append("  </style>")
    html.append("</head>")
    html.append("<body>")
    html.append(f"  <h1>Tag View - Page {page_num} of {total_pages}</h1>")

    # Info section
    html.append(f"  <div class='info'>")
    html.append(f"    <strong>Images on this page:</strong> {len(images)}<br>")
    html.append(f"    <strong>Page:</strong> {page_num} of {total_pages}")
    html.append(f"  </div>")

    # Pagination nav
    html.append(f"  <div class='pagination'>")
    if page_num > 1:
        html.append(f"    <a href='{base_filename}_page1.html'>&lt;&lt; First</a>")
        html.append(f"    <a href='{base_filename}_page{page_num-1}.html'>&lt; Previous</a>")
    else:
        html.append(f"    <a class='disabled'>&lt;&lt; First</a>")
        html.append(f"    <a class='disabled'>&lt; Previous</a>")

    html.append(f"    <span class='current'>Page {page_num} of {total_pages}</span>")

    if page_num < total_pages:
        html.append(f"    <a href='{base_filename}_page{page_num+1}.html'>Next &gt;</a>")
        html.append(f"    <a href='{base_filename}_page{total_pages}.html'>Last &gt;&gt;</a>")
    else:
        html.append(f"    <a class='disabled'>Next &gt;</a>")
        html.append(f"    <a class='disabled'>Last &gt;&gt;</a>")
    html.append(f"  </div>")

    # Toolbar
    html.append(f"  <div class='toolbar'>")
    html.append(f"    <button onclick='selectAll()'>Select All</button>")
    html.append(f"    <button onclick='clearAll()' class='secondary'>Clear All</button>")
    html.append(f"    <button onclick='exportList()' class='export'>Export Removal List</button>")
    html.append(f"    <div class='counter'>Selected: <span id='count'>0</span></div>")
    html.append(f"  </div>")

    # Table
    html.append("  <table>")

    # Generate table rows (6 columns)
    cols = 6
    for i in range(0, len(images), cols):
        html.append("    <tr>")
        for j in range(cols):
            idx = i + j
            if idx < len(images):
                img_data = images[idx]
                thumb_path = f"{thumb_dir}/{img_data['local_filename']}"
                # Replace file extension with _thumb.jpg
                thumb_path = thumb_path.rsplit('.', 1)[0] + '_thumb.jpg'

                # Format metadata
                keywords_str = ", ".join(img_data['keywords'][:10]) if img_data['keywords'] else "none"
                if len(img_data['keywords']) > 10:
                    keywords_str += f" ... ({len(img_data['keywords'])} total)"

                html.append(f"      <td id='cell-{idx}'>")
                html.append(f"        <div class='subject'>{img_data['subject'][:50]}</div>")
                html.append(f"        <div class='msg-id'>{img_data['msg_id']}</div>")
                html.append(f"        <div class='image-container'>")
                html.append(f"          <input type='checkbox' class='remove-checkbox' ")
                html.append(f"                 data-filename='{img_data['local_filename']}' ")
                html.append(f"                 onchange='updateSelection()'>")
                html.append(f"          <img src='{thumb_path}' alt='Image'>")
                html.append(f"        </div>")
                html.append(f"        <pre>keywords: {keywords_str}</pre>")
                html.append("      </td>")
            else:
                html.append("      <td></td>")
        html.append("    </tr>")

    html.append("  </table>")

    # Bottom pagination
    html.append(f"  <div class='pagination' style='margin-top: 20px;'>")
    if page_num > 1:
        html.append(f"    <a href='{base_filename}_page1.html'>&lt;&lt; First</a>")
        html.append(f"    <a href='{base_filename}_page{page_num-1}.html'>&lt; Previous</a>")
    else:
        html.append(f"    <a class='disabled'>&lt;&lt; First</a>")
        html.append(f"    <a class='disabled'>&lt; Previous</a>")

    html.append(f"    <span class='current'>Page {page_num} of {total_pages}</span>")

    if page_num < total_pages:
        html.append(f"    <a href='{base_filename}_page{page_num+1}.html'>Next &gt;</a>")
        html.append(f"    <a href='{base_filename}_page{total_pages}.html'>Last &gt;&gt;</a>")
    else:
        html.append(f"    <a class='disabled'>Next &gt;</a>")
        html.append(f"    <a class='disabled'>Last &gt;&gt;</a>")
    html.append(f"  </div>")

    # JavaScript
    html.append("  <script>")
    html.append("    function updateSelection() {")
    html.append("      // Update count")
    html.append("      const checkboxes = document.querySelectorAll('.remove-checkbox');")
    html.append("      const checked = Array.from(checkboxes).filter(cb => cb.checked);")
    html.append("      document.getElementById('count').textContent = checked.length;")
    html.append("      ")
    html.append("      // Update cell styling")
    html.append("      checkboxes.forEach(cb => {")
    html.append("        const cell = cb.closest('td');")
    html.append("        if (cb.checked) {")
    html.append("          cell.classList.add('selected');")
    html.append("        } else {")
    html.append("          cell.classList.remove('selected');")
    html.append("        }")
    html.append("      });")
    html.append("    }")
    html.append("    ")
    html.append("    function selectAll() {")
    html.append("      const checkboxes = document.querySelectorAll('.remove-checkbox');")
    html.append("      checkboxes.forEach(cb => cb.checked = true);")
    html.append("      updateSelection();")
    html.append("    }")
    html.append("    ")
    html.append("    function clearAll() {")
    html.append("      const checkboxes = document.querySelectorAll('.remove-checkbox');")
    html.append("      checkboxes.forEach(cb => cb.checked = false);")
    html.append("      updateSelection();")
    html.append("    }")
    html.append("    ")
    html.append(f"    const pageNum = {page_num};")
    html.append("    function exportList() {")
    html.append("      const checkboxes = document.querySelectorAll('.remove-checkbox:checked');")
    html.append("      if (checkboxes.length === 0) {")
    html.append("        alert('No images selected for removal');")
    html.append("        return;")
    html.append("      }")
    html.append("      ")
    html.append("      // Collect filenames")
    html.append("      const filenames = Array.from(checkboxes).map(cb => cb.dataset.filename);")
    html.append("      ")
    html.append("      // Create text content")
    html.append("      const content = filenames.join('\\n') + '\\n';")
    html.append("      ")
    html.append("      // Create download")
    html.append("      const blob = new Blob([content], { type: 'text/plain' });")
    html.append("      const url = URL.createObjectURL(blob);")
    html.append("      const a = document.createElement('a');")
    html.append("      a.href = url;")
    html.append("      a.download = `images_to_remove_page${pageNum}.txt`;")
    html.append("      document.body.appendChild(a);")
    html.append("      a.click();")
    html.append("      document.body.removeChild(a);")
    html.append("      URL.revokeObjectURL(url);")
    html.append("      ")
    html.append("      alert(`Exported ${filenames.length} images to images_to_remove_page${pageNum}.txt`);")
    html.append("    }")
    html.append("  </script>")
    html.append("</body>")
    html.append("</html>")

    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(html))


def generate_html_view(index_data: dict, thumb_dir: str, output_base: str, page_size: int = 210):
    """Generate paginated HTML views of tagged images.

    Args:
        index_data: Dictionary of messages with images
        thumb_dir: Relative path to thumbnail directory
        output_base: Base path for output HTML files (without extension)
        page_size: Number of images per page (default: 210)
    """
    # Collect all images with their metadata
    images = []
    for msg_id, message in index_data.items():
        metadata = message.get("metadata", {})
        subject = metadata.get("subject", "Unknown")
        msg_keywords = message.get("keywords", [])

        for image in message.get("images", []):
            local_filename = image.get("local_filename", "")
            if not local_filename:
                continue

            # Get image keywords
            img_keywords = image.get("keywords", [])

            # Combine all keywords (message + image)
            all_keywords = list(msg_keywords) + list(img_keywords)

            images.append({
                "msg_id": msg_id,
                "subject": subject,
                "local_filename": local_filename,
                "keywords": all_keywords
            })

    # Calculate number of pages
    total_images = len(images)
    total_pages = (total_images + page_size - 1) // page_size  # Ceiling division

    if total_pages == 0:
        print("No images to display")
        return

    # Extract base filename from output_base
    from pathlib import Path
    base_path = Path(output_base)
    base_filename = base_path.stem

    # Generate each page
    for page_num in range(1, total_pages + 1):
        start_idx = (page_num - 1) * page_size
        end_idx = min(start_idx + page_size, total_images)
        page_images = images[start_idx:end_idx]

        output_file = f"{output_base}_page{page_num}.html"
        generate_html_page(page_images, thumb_dir, output_file,
                          page_num, total_pages, base_filename)

    print(f"Generated {total_pages} HTML pages ({total_images} images, {page_size} per page)")
    print(f"Start at: {output_base}_page1.html")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze keyword statistics from tagged image index',
        usage='%(prog)s SOURCE [DEST] [--suppress-html] [--limit N] [--page-size N]'
    )

    # Positional arguments
    parser.add_argument('source', metavar='SOURCE',
                        help='Path to input image index file')
    parser.add_argument('dest', metavar='DEST', nargs='?',
                        help='Path to output text file (default: SOURCE with _statistics.txt suffix)')

    # Optional arguments
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of messages to process')
    parser.add_argument('--thumb_dir', default='../data/images/thumbs',
                        help='Relative path to thumbnail directory (default: ../data/images/thumbs)')
    parser.add_argument('--page-size', type=int, default=210,
                        help='Number of images per HTML page (default: 210)')
    parser.add_argument('--suppress-html', action='store_true',
                        help='Skip HTML view generation (only create text statistics)')

    args = parser.parse_args()

    # Generate default output filename if not provided
    if args.dest is None:
        source_path = Path(args.source)
        args.dest = str(source_path.parent / f"{source_path.stem}_statistics.txt")

    # HTML output base (without .html extension) - include full path
    dest_path = Path(args.dest)
    html_base = str(dest_path.parent / (dest_path.stem + '_view'))

    print(f"Loading index from {args.source}...")
    index_data = load_index(args.source, limit=args.limit)
    print(f"Loaded {len(index_data)} messages")
    if args.limit:
        print(f"(limited to first {args.limit} messages)")

    print("Analyzing keywords...")
    keyword_counter = analyze_keywords(index_data)

    # Write text statistics
    print(f"Writing statistics to {args.dest}...")
    with open(args.dest, 'w') as f:
        # Header
        f.write("TAG STATISTICS REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Index file: {args.source}\n")
        if args.limit:
            f.write(f"Limit: {args.limit} messages\n")
        f.write("\n\n")

        # Summary
        f.write(format_summary(index_data, keyword_counter))
        f.write("\n\n")

        # Keyword statistics
        f.write(format_keyword_statistics(keyword_counter))

    print(f"Statistics written to: {args.dest}")
    print(f"Total unique keywords: {len(keyword_counter)}")

    # Generate HTML view (unless suppressed)
    if not args.suppress_html:
        print(f"Generating HTML view...")
        generate_html_view(index_data, args.thumb_dir, html_base, args.page_size)
    else:
        print("HTML generation suppressed (--suppress-html)")


if __name__ == "__main__":
    main()
