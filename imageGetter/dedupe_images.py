# ABOUTME: Deduplicate images within messages based on file size
# ABOUTME: Removes duplicate images (same size) and missing image files from index

import json
from pathlib import Path
from typing import Dict, Tuple


def load_index(index_file: str) -> Dict:
    """Load image index from JSON file.

    Args:
        index_file: Path to image index JSON file

    Returns:
        Dictionary of messages with metadata and images
    """
    with open(index_file, 'r') as f:
        return json.load(f)


def dedupe_message_images(message: Dict, images_dir: str) -> Tuple[Dict, Dict]:
    """Deduplicate images within a message and remove missing files.

    Keeps first image for each unique file size, removes duplicates.
    Also removes images whose files don't exist in images_dir.

    Args:
        message: Message dictionary with images list
        images_dir: Path to directory containing image files

    Returns:
        Tuple of (modified_message, stats_dict)
        stats_dict contains: duplicates_removed, missing_removed
    """
    images_path = Path(images_dir)
    seen_sizes = set()
    kept_images = []
    stats = {
        "duplicates_removed": 0,
        "missing_removed": 0
    }

    for image in message.get("images", []):
        local_filename = image.get("local_filename", "")
        if not local_filename:
            continue

        image_file = images_path / local_filename

        # Check if file exists (handle OSError for filenames that are too long)
        try:
            if not image_file.exists():
                stats["missing_removed"] += 1
                continue

            # Get file size
            file_size = image_file.stat().st_size
        except OSError:
            # File name too long or other OS error - treat as missing
            stats["missing_removed"] += 1
            continue

        # Check if we've seen this size before
        if file_size in seen_sizes:
            stats["duplicates_removed"] += 1
            continue

        # Keep this image
        seen_sizes.add(file_size)
        kept_images.append(image)

    # Create modified message
    result = message.copy()
    result["images"] = kept_images

    return result, stats


def save_index(index_data: Dict, output_file: str):
    """Save image index to JSON file.

    Args:
        index_data: Dictionary to save
        output_file: Path to output file
    """
    with open(output_file, 'w') as f:
        json.dump(index_data, f, indent=2)
