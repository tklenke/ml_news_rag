# ABOUTME: Batch processor for tagging messages with LLM keywords
# ABOUTME: Loads image index, applies keyword tagger to each message, saves results

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from llm_tagger import KeywordTagger


def load_image_index(index_file: str) -> Dict:
    """Load image index from JSON file.

    Args:
        index_file: Path to image_index.json

    Returns:
        Dictionary of messages with metadata and images

    Raises:
        FileNotFoundError: If index file doesn't exist
    """
    index_path = Path(index_file)
    if not index_path.exists():
        raise FileNotFoundError(f"Index file not found: {index_file}")

    with open(index_file, 'r') as f:
        return json.load(f)


def load_keywords(keywords_file: str) -> List[str]:
    """Load keywords from text file.

    Handles plain text and bullet-formatted lists.

    Args:
        keywords_file: Path to keywords file

    Returns:
        List of keywords

    Raises:
        FileNotFoundError: If keywords file doesn't exist
    """
    kw_path = Path(keywords_file)
    if not kw_path.exists():
        raise FileNotFoundError(f"Keywords file not found: {keywords_file}")

    keywords = []
    with open(keywords_file, 'r') as f:
        for line in f:
            # Strip whitespace
            keyword = line.strip()
            # Remove bullet points (e.g., "*   *   *   firewall")
            # Repeatedly strip * and whitespace until no more found
            while keyword and (keyword[0] == '*' or keyword[0].isspace()):
                keyword = keyword.lstrip('* \t')
            # Skip empty lines
            if keyword:
                keywords.append(keyword)

    return keywords


def extract_message_text(message: Dict, msgs_md_dir: str = "../data/msgs_md") -> str:
    """Extract full message text from markdown file for LLM processing.

    Reads the full message body from the corresponding markdown file
    in data/msgs_md/{first_letter}/{message_id}.md

    Args:
        message: Message dictionary with metadata
        msgs_md_dir: Path to msgs_md directory (default: ../data/msgs_md)

    Returns:
        Clean text string for LLM input (subject + body)
    """
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

        # Return subject + body (limited to reasonable length for LLM)
        # Limit to ~2000 characters to avoid timeout
        full_text = f"{subject}\n\n{body_text}"
        if len(full_text) > 2000:
            full_text = full_text[:2000] + "..."

        return full_text

    except Exception as e:
        # On any error, fall back to just subject
        print(f"Warning: Could not read message body for {message_id}: {e}")
        return subject


def tag_messages(
    index_file: str,
    keywords_file: str,
    overwrite: bool = False,
    limit: int = None,
    model: str = None
) -> Dict:
    """Tag messages in index with LLM keywords.

    Args:
        index_file: Path to image index JSON file
        keywords_file: Path to keywords file
        overwrite: If True, retag messages that already have llm_keywords
        limit: If specified, process only first N messages
        model: Optional model override

    Returns:
        Dictionary with statistics:
        - processed: Number of messages tagged
        - skipped: Number of messages skipped (already tagged)
        - errors: Number of errors encountered
    """
    # Load data
    index_data = load_image_index(index_file)
    keywords = load_keywords(keywords_file)

    # Initialize tagger
    tagger = KeywordTagger()

    # Statistics
    stats = {
        "processed": 0,
        "skipped": 0,
        "errors": 0
    }

    # Process messages
    messages_processed = 0
    for msg_id, message in index_data.items():
        # Check limit
        if limit is not None and messages_processed >= limit:
            break

        # Skip if already tagged (unless overwrite)
        if not overwrite and "llm_keywords" in message and message["llm_keywords"]:
            stats["skipped"] += 1
            continue

        # Extract message text
        message_text = extract_message_text(message)

        # Tag message
        try:
            matched_keywords, raw_response = tagger.tag_message(message_text, keywords, model=model)
            message["llm_keywords"] = matched_keywords
            stats["processed"] += 1
            messages_processed += 1
        except Exception as e:
            print(f"ERROR tagging message {msg_id}: {e}")
            # Set empty list on error (valid state)
            message["llm_keywords"] = []
            stats["errors"] += 1
            stats["processed"] += 1
            messages_processed += 1

        # Auto-save every 50 messages
        if stats["processed"] % 50 == 0:
            save_image_index(index_data, index_file)

    # Final save
    save_image_index(index_data, index_file)

    return stats


def save_image_index(index_data: Dict, index_file: str):
    """Save image index to JSON file with backup.

    Creates backup of existing file before overwriting.

    Args:
        index_data: Dictionary to save
        index_file: Path to save to
    """
    index_path = Path(index_file)

    # Create backup if file exists
    if index_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = index_path.parent / f"{index_path.name}.backup.{timestamp}"
        shutil.copy2(index_path, backup_path)

    # Write new data
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=2)
