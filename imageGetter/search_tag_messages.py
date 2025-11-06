# ABOUTME: Batch processor for image-level keyword scoring
# ABOUTME: Scores keywords per image based on proximity to image URLs

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from keyword_scorer import KeywordScorer
from config import INVALID_KEYWORDS


def load_image_index(index_file: str) -> Dict:
    """Load image index from JSON file.

    Args:
        index_file: Path to JSON file

    Returns:
        Dictionary of messages
    """
    with open(index_file, 'r') as f:
        return json.load(f)


def load_keywords(keywords_file: str) -> List[str]:
    """Load keywords from text file.

    Args:
        keywords_file: Path to keywords file (one per line)

    Returns:
        List of keywords
    """
    keywords = []
    with open(keywords_file, 'r') as f:
        for line in f:
            # Strip whitespace and skip empty lines
            keyword = line.strip()
            if keyword and not keyword.startswith('#'):
                # Remove bullet points if present
                if keyword.startswith('- '):
                    keyword = keyword[2:]
                keywords.append(keyword)
    return keywords


def extract_message_text(message: Dict, msgs_md_dir: str = "../data/msgs_md") -> str:
    """Extract full message text from markdown file for keyword searching.

    Reads the full message body from the corresponding markdown file
    in data/msgs_md/{first_letter}/{message_id}.md

    Args:
        message: Message dictionary with metadata
        msgs_md_dir: Path to msgs_md directory (default: ../data/msgs_md)

    Returns:
        Clean text string for searching (subject + body)
    """
    from pathlib import Path

    metadata = message.get("metadata", {})
    subject = metadata.get("subject", "")
    message_id = metadata.get("message_id", "")

    # If no message_id, return just subject
    if not message_id:
        return subject

    # Construct path to markdown file: msgs_md/{first_letter}/{message_id}.md
    first_letter = message_id[0].upper()
    md_file = Path(msgs_md_dir) / first_letter / f"{message_id}.md"

    # If file doesn't exist, return just subject
    if not md_file.exists():
        # Try lowercase directory (some messages might be stored there)
        first_letter_lower = message_id[0].lower()
        md_file = Path(msgs_md_dir) / first_letter_lower / f"{message_id}.md"
        if not md_file.exists():
            # Also try aDigits directory for messages starting with lowercase 'a' followed by digit
            if message_id[0].lower() == 'a' and len(message_id) > 1 and message_id[1].isdigit():
                md_file = Path(msgs_md_dir) / "aDigits" / f"{message_id}.md"
                if not md_file.exists():
                    return subject
            else:
                return subject

    # Read markdown file and extract body text
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip the first few lines (metadata header) and extract body
        # The body starts after the subject line (marked with "# ")
        lines = content.split('\n')
        body_lines = []
        found_subject = False

        for line in lines:
            # Once we find the subject line, start collecting body text
            if line.strip().startswith('# '):
                found_subject = True
                continue

            # After finding subject, collect all text
            if found_subject:
                # Skip image markers and profile photos
                if not line.strip().startswith('![') and not line.strip().startswith('https://'):
                    body_lines.append(line)

        body_text = '\n'.join(body_lines).strip()

        # Return subject + body (full text for keyword searching)
        full_text = f"{subject}\n\n{body_text}"
        return full_text

    except Exception as e:
        # On any error, fall back to just subject
        print(f"Warning: Could not read message body for {message_id}: {e}")
        return subject


def tag_messages(
    index_file: str,
    keywords_file: str,
    output_file: str = None,
    limit: int = None,
    verbose: bool = False,
    keep_existing: bool = False,
    msgs_md_dir: str = "../data/msgs_md"
) -> Dict:
    """Tag images with scored keywords based on proximity to image URLs.

    Args:
        index_file: Path to image index JSON file
        keywords_file: Path to keywords file
        output_file: Path to output file (default: overwrite input file with backup)
        limit: If specified, process only first N messages
        verbose: If True, print detailed output for each message
        keep_existing: DEPRECATED - no longer used (image-level scoring always replaces)
        msgs_md_dir: Path to msgs_md directory (default: ../data/msgs_md)

    Returns:
        Dictionary with statistics:
        - processed: Number of messages processed
        - images_scored: Number of images scored
        - errors: Number of errors encountered
    """
    # Default output to input file for backward compatibility
    if output_file is None:
        output_file = index_file

    # Load data
    index_data = load_image_index(index_file)
    keywords = load_keywords(keywords_file)

    # Statistics
    stats = {
        "processed": 0,
        "images_scored": 0,
        "errors": 0
    }

    # Count total messages to process for progress tracking
    total_to_process = len(index_data)
    if limit and limit < total_to_process:
        total_to_process = limit

    # Process messages
    messages_processed = 0
    for msg_id, message in index_data.items():
        # Check limit
        if limit is not None and messages_processed >= limit:
            break

        # Extract full message text from markdown file
        message_text = extract_message_text(message, msgs_md_dir)
        subject = message.get("metadata", {}).get("subject", "")

        try:
            if verbose:
                print(f"[{messages_processed+1}/{total_to_process}] {subject[:60]}")

            # Process each image independently
            for image in message.get("images", []):
                # Find this specific image's URL position in message text
                url_pos = message_text.find(image["url"])
                if url_pos == -1:
                    # Fallback: use middle of message if URL not found
                    url_pos = len(message_text) // 2

                # Score keywords for this image
                scorer = KeywordScorer(message_text, subject, url_pos)
                scores = scorer.score_keywords_batch(keywords)

                # Store non-zero scores as dict {keyword: score}
                scored_keywords = {kw: int(score) for kw, score in scores.items() if score > 0}

                # Filter out invalid keywords
                invalid_lower = {kw.lower() for kw in INVALID_KEYWORDS}
                scored_keywords = {kw: score for kw, score in scored_keywords.items()
                                   if kw.lower() not in invalid_lower}

                # Store in image
                image["keywords"] = scored_keywords
                stats["images_scored"] += 1

                if verbose:
                    print(f"  Image: {image.get('filename', 'unknown')}")
                    print(f"  URL position: {url_pos}")
                    print(f"  Scored keywords: {len(scored_keywords)}")
                    if scored_keywords:
                        # Get top 5 keywords by score
                        top_5 = sorted(scored_keywords.items(), key=lambda x: x[1], reverse=True)[:5]
                        print(f"  Top 5: {top_5}")

            # Remove message-level keywords field if it exists
            if "keywords" in message:
                del message["keywords"]

            stats["processed"] += 1
            messages_processed += 1

        except Exception as e:
            print(f"ERROR processing message {msg_id}: {e}")
            import traceback
            traceback.print_exc()
            stats["errors"] += 1
            stats["processed"] += 1
            messages_processed += 1

        # Auto-save every 50 messages
        if stats["processed"] % 50 == 0:
            if not verbose:
                print(f"  → Auto-saved after {stats['processed']} messages")
            save_image_index(index_data, output_file)

    # Final save
    save_image_index(index_data, output_file)

    return stats


def save_image_index(index_data: Dict, index_file: str):
    """Save image index to JSON file.

    Args:
        index_data: Dictionary to save
        index_file: Path to save to
    """
    # Write data directly (no backup needed since we write to new files)
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=1)
