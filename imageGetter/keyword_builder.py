# ABOUTME: Message sampling and text extraction for LLM keyword building
# ABOUTME: Samples random messages from image_index.json and extracts text for keyword extraction

import json
import random
from typing import List, Dict


def load_image_index(file_path: str) -> Dict:
    """Load image index JSON file.

    Args:
        file_path: Path to image_index.json

    Returns:
        Dictionary of messages with metadata and images
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def sample_random_messages(image_index: Dict, sample_size: int) -> List[Dict]:
    """Sample random messages from image index.

    Args:
        image_index: Dictionary of messages from load_image_index()
        sample_size: Number of messages to sample

    Returns:
        List of message dictionaries (includes metadata and images)
    """
    # Get all message values from the index
    all_messages = list(image_index.values())

    # If sample_size is larger than available messages, return all
    if sample_size >= len(all_messages):
        return all_messages

    # Sample random messages
    return random.sample(all_messages, sample_size)


def extract_message_text(message: Dict) -> str:
    """Extract clean text from message for LLM processing.

    Extracts subject and other relevant text fields.

    Args:
        message: Message dictionary with metadata

    Returns:
        Clean text string for LLM input
    """
    metadata = message.get("metadata", {})
    subject = metadata.get("subject", "")

    # Remove escaped characters for cleaner text
    clean_subject = subject.replace("\\[", "[").replace("\\]", "]").replace("\\-", "-")

    return clean_subject
