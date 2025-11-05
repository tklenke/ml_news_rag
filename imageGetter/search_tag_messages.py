# ABOUTME: Batch processor for search-based keyword tagging
# ABOUTME: Tags all messages in image index using SearchTagger with stemming

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from search_tagger import SearchTagger
from llm_config import INVALID_KEYWORDS


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


def extract_message_text(message: Dict) -> str:
    """Extract searchable text from message.

    Extracts subject and message body for keyword searching.

    Args:
        message: Message dictionary

    Returns:
        Combined text from subject and body
    """
    parts = []

    # Get subject
    metadata = message.get("metadata", {})
    subject = metadata.get("subject", "")
    if subject:
        parts.append(subject)

    # Get message body if available
    message_md = metadata.get("message_md", "")
    if message_md:
        parts.append(message_md)

    return " ".join(parts)


def tag_messages(
    index_file: str,
    keywords_file: str,
    output_file: str = None,
    limit: int = None,
    verbose: bool = False,
    keep_existing: bool = False
) -> Dict:
    """Tag messages in index with keywords using search and stemming.

    Args:
        index_file: Path to image index JSON file
        keywords_file: Path to keywords file
        output_file: Path to output file (default: overwrite input file with backup)
        limit: If specified, process only first N messages
        verbose: If True, print detailed output for each message
        keep_existing: If True, merge with existing keywords; if False, replace (default: False)

    Returns:
        Dictionary with statistics:
        - processed: Number of messages tagged
        - skipped: Number of messages skipped (already tagged)
        - errors: Number of errors encountered
    """
    # Default output to input file for backward compatibility
    if output_file is None:
        output_file = index_file

    # Load data
    index_data = load_image_index(index_file)
    keywords = load_keywords(keywords_file)

    # Initialize tagger
    tagger = SearchTagger()

    # Statistics
    stats = {
        "processed": 0,
        "skipped": 0,
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

        # Extract message text
        message_text = extract_message_text(message)

        try:
            if verbose:
                subject = message.get("metadata", {}).get("subject", "Unknown")
                print(f"[{messages_processed+1}/{total_to_process}] {subject[:60]}")

            # Get existing keywords (if any)
            existing_keywords = message.get("keywords", [])

            # Create allowed vocabulary (case-insensitive) from aircraft_keywords.txt
            allowed_keywords_lower = {kw.lower() for kw in keywords}

            # Filter existing keywords: keep only those in allowed vocabulary
            valid_existing = [kw for kw in existing_keywords if kw.lower() in allowed_keywords_lower]

            # Search for keywords in message text
            matched_keywords = tagger.find_keywords(message_text, keywords)

            # Decide whether to merge or replace
            if keep_existing:
                # Merge valid existing and newly matched keywords, deduplicate (case-insensitive)
                combined = list(valid_existing) + matched_keywords
                seen = set()
                deduplicated = []
                for kw in combined:
                    if kw.lower() not in seen:
                        seen.add(kw.lower())
                        deduplicated.append(kw)
            else:
                # Replace: use only newly matched keywords (discard existing)
                deduplicated = matched_keywords

            # Filter out invalid keywords (should already be filtered, but belt-and-suspenders)
            invalid_lower = {kw.lower() for kw in INVALID_KEYWORDS}
            final_keywords = [kw for kw in deduplicated if kw.lower() not in invalid_lower]

            # Store keywords
            message["keywords"] = final_keywords

            if verbose:
                print(f"  Existing: {existing_keywords}")
                print(f"  Valid existing (in vocabulary): {valid_existing}")
                print(f"  Matched: {matched_keywords}")
                print(f"  Final: {final_keywords}")
                print(f"  Mode: {'merge' if keep_existing else 'replace'}")

            stats["processed"] += 1
            messages_processed += 1

        except Exception as e:
            print(f"ERROR processing message {msg_id}: {e}")
            # Keep existing keywords on error
            if "keywords" not in message:
                message["keywords"] = []
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
        json.dump(index_data, f, indent=2)
