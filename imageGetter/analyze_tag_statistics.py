#!/usr/bin/env python3
# ABOUTME: Analyze keyword and chapter statistics from tagged image index
# ABOUTME: Combines LLM keywords and non-LLM keywords, groups by frequency

import json
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime


def load_index(index_file: str) -> dict:
    """Load image index from JSON file."""
    with open(index_file, 'r') as f:
        return json.load(f)


def analyze_keywords(index_data: dict) -> Counter:
    """Analyze keyword frequencies across all messages.

    Combines both LLM keywords and non-LLM keywords from images.
    """
    keyword_counter = Counter()

    for message in index_data.values():
        # Collect LLM keywords
        llm_keywords = message.get("llm_keywords", [])
        for kw in llm_keywords:
            keyword_counter[kw.lower()] += 1

        # Collect non-LLM keywords from images
        images = message.get("images", [])
        for image in images:
            keywords = image.get("keywords", [])
            for kw in keywords:
                keyword_counter[kw.lower()] += 1

    return keyword_counter


def analyze_chapters(index_data: dict) -> Counter:
    """Analyze chapter frequencies across all messages."""
    chapter_counter = Counter()

    for message in index_data.values():
        chapters = message.get("chapters", [])
        for ch in chapters:
            chapter_counter[ch] += 1

    return chapter_counter


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


def format_chapter_statistics(chapter_counter: Counter) -> str:
    """Format chapter statistics."""
    output = []
    output.append("=" * 70)
    output.append("CHAPTER STATISTICS")
    output.append("=" * 70)
    output.append(f"Total unique chapters: {len(chapter_counter)}")
    output.append(f"Total chapter assignments: {sum(chapter_counter.values())}")
    output.append("")

    if chapter_counter:
        output.append("Chapters by occurrence (sorted by chapter number):")
        output.append("-" * 70)

        # Sort by chapter number
        sorted_chapters = sorted(chapter_counter.items(), key=lambda x: x[0])

        for chapter, count in sorted_chapters:
            output.append(f"  Chapter {chapter:2d}:  {count:4d} occurrences")
        output.append("")

    return "\n".join(output)


def format_summary(index_data: dict, keyword_counter: Counter, chapter_counter: Counter) -> str:
    """Format summary statistics."""
    output = []
    output.append("=" * 70)
    output.append("SUMMARY")
    output.append("=" * 70)

    total_messages = len(index_data)
    messages_with_llm_keywords = sum(1 for m in index_data.values() if m.get("llm_keywords"))
    messages_with_chapters = sum(1 for m in index_data.values() if m.get("chapters"))
    messages_with_image_keywords = sum(1 for m in index_data.values() if any(img.get("keywords") for img in m.get("images", [])))

    output.append(f"Total messages: {total_messages}")
    output.append(f"Messages with LLM keywords: {messages_with_llm_keywords}")
    output.append(f"Messages with image keywords: {messages_with_image_keywords}")
    output.append(f"Messages with chapters: {messages_with_chapters}")
    output.append("")
    output.append(f"Total unique keywords: {len(keyword_counter)}")
    output.append(f"Total unique chapters: {len(chapter_counter)}")
    output.append("")

    # Averages
    if messages_with_llm_keywords > 0 or messages_with_image_keywords > 0:
        total_kw_count = sum(keyword_counter.values())
        avg_keywords = total_kw_count / total_messages
        output.append(f"Average keywords per message: {avg_keywords:.2f}")

    if messages_with_chapters > 0:
        total_ch_count = sum(chapter_counter.values())
        avg_chapters = total_ch_count / total_messages
        output.append(f"Average chapters per message: {avg_chapters:.2f}")

    output.append("")

    return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_tag_statistics.py <index_file> [output_file]")
        print("Example: python analyze_tag_statistics.py tests/test.idx tag_statistics.txt")
        sys.exit(1)

    index_file = sys.argv[1]

    # Generate default output filename if not provided
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"tag_statistics_{timestamp}.txt"

    print(f"Loading index from {index_file}...")
    index_data = load_index(index_file)
    print(f"Loaded {len(index_data)} messages")

    print("Analyzing keywords...")
    keyword_counter = analyze_keywords(index_data)

    print("Analyzing chapters...")
    chapter_counter = analyze_chapters(index_data)

    print(f"Writing statistics to {output_file}...")

    with open(output_file, 'w') as f:
        # Header
        f.write("TAG STATISTICS REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Index file: {index_file}\n")
        f.write("\n\n")

        # Summary
        f.write(format_summary(index_data, keyword_counter, chapter_counter))
        f.write("\n\n")

        # Chapter statistics
        f.write(format_chapter_statistics(chapter_counter))
        f.write("\n\n")

        # Keyword statistics
        f.write(format_keyword_statistics(keyword_counter))

    print(f"\nStatistics written to: {output_file}")
    print(f"Total unique keywords: {len(keyword_counter)}")
    print(f"Total unique chapters: {len(chapter_counter)}")


if __name__ == "__main__":
    main()
