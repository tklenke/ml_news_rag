# ABOUTME: Remove images from index based on removal list files
# ABOUTME: Reads image filenames from text files and removes them from the index

import json
from pathlib import Path
from typing import Dict, Set, List, Tuple


def load_index(index_file: str) -> Dict:
    """Load image index from JSON file.

    Args:
        index_file: Path to image index JSON file

    Returns:
        Dictionary of messages with metadata and images
    """
    with open(index_file, 'r') as f:
        return json.load(f)


def load_removal_lists(removal_files: List[str]) -> Set[str]:
    """Load image filenames from one or more removal list files.

    Args:
        removal_files: List of paths to removal list text files

    Returns:
        Set of unique image filenames to remove
    """
    filenames = set()

    for removal_file in removal_files:
        with open(removal_file, 'r') as f:
            for line in f:
                filename = line.strip()
                if filename:  # Skip empty lines
                    filenames.add(filename)

    return filenames


def remove_images_from_index(index_data: Dict, removal_set: Set[str]) -> Tuple[Dict, Dict]:
    """Remove images from index based on removal set.

    Messages with no remaining images are removed entirely from the index.

    Args:
        index_data: Dictionary of messages with images
        removal_set: Set of image filenames to remove

    Returns:
        Tuple of (modified_index, stats_dict)
        stats_dict contains: images_removed, messages_affected, messages_removed
    """
    stats = {
        "images_removed": 0,
        "messages_affected": 0,
        "messages_removed": 0
    }

    # Deep copy the index to avoid modifying original
    result = {}

    for msg_id, message in index_data.items():
        # Filter images
        original_images = message.get("images", [])
        kept_images = []
        message_affected = False

        for image in original_images:
            filename = image.get("local_filename", "")
            if filename in removal_set:
                stats["images_removed"] += 1
                message_affected = True
            else:
                kept_images.append(image)

        # Only keep messages that have at least one image remaining
        if len(kept_images) > 0:
            # Copy the message
            result[msg_id] = message.copy()
            result[msg_id]["images"] = kept_images

            if message_affected:
                stats["messages_affected"] += 1
        else:
            # Message has no images left, remove it entirely
            stats["messages_removed"] += 1
            if message_affected:
                stats["messages_affected"] += 1

    return result, stats


def save_index(index_data: Dict, output_file: str):
    """Save image index to JSON file.

    Args:
        index_data: Dictionary to save
        output_file: Path to output file
    """
    with open(output_file, 'w') as f:
        json.dump(index_data, f, indent=2)
