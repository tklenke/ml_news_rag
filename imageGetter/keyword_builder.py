# ABOUTME: Message sampling and text extraction for LLM keyword building
# ABOUTME: Samples random messages from image_index.json and extracts text for keyword extraction

import json
import random
from typing import List, Dict, Set
import ollama
from llm_config import OLLAMA_HOST, LLM_MODEL, KEYWORD_EXTRACTION_PROMPT


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


class KeywordExtractor:
    """Extract keywords from messages using LLM."""

    def __init__(self, ollama_host: str = None, model: str = None):
        """Initialize keyword extractor with Ollama client.

        Args:
            ollama_host: Ollama server URL (defaults to OLLAMA_HOST from config)
            model: LLM model name (defaults to LLM_MODEL from config)
        """
        self.ollama_client = ollama.Client(ollama_host or OLLAMA_HOST)
        self.model = model or LLM_MODEL

    def extract_keywords_from_message(self, message_text: str) -> List[str]:
        """Extract keywords from a single message using LLM.

        Args:
            message_text: Message text to extract keywords from

        Returns:
            List of extracted keywords
        """
        if not message_text or not message_text.strip():
            return []

        try:
            # Format the prompt
            prompt = KEYWORD_EXTRACTION_PROMPT.format(message=message_text)

            # Call LLM
            response = self.ollama_client.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )

            # Parse response - expecting comma-separated keywords
            response_text = response.get('response', '').strip()
            if not response_text:
                return []

            # Split by comma and clean up
            keywords = [k.strip() for k in response_text.split(',')]
            # Remove empty strings
            keywords = [k for k in keywords if k]

            return keywords

        except Exception as e:
            # Log error and return empty list (graceful degradation)
            print(f"Error extracting keywords: {e}")
            return []

    def extract_keywords_from_messages(self, messages: List[str]) -> List[str]:
        """Extract keywords from multiple messages.

        Args:
            messages: List of message texts

        Returns:
            List of all keywords from all messages (may contain duplicates)
        """
        all_keywords = []
        for message_text in messages:
            keywords = self.extract_keywords_from_message(message_text)
            all_keywords.extend(keywords)

        return all_keywords


def aggregate_keywords(keyword_lists: List[List[str]]) -> Set[str]:
    """Aggregate keywords from multiple lists and remove duplicates.

    Args:
        keyword_lists: List of keyword lists

    Returns:
        Set of unique keywords (case-insensitive)
    """
    # Flatten all keyword lists and convert to lowercase
    all_keywords = set()
    for keyword_list in keyword_lists:
        for keyword in keyword_list:
            all_keywords.add(keyword.lower())

    return all_keywords
