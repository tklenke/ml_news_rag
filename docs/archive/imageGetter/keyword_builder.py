# ABOUTME: Message sampling and text extraction for LLM keyword building
# ABOUTME: Samples random messages from image_index.json and extracts text for keyword extraction

import json
import random
from typing import List, Dict, Set
import ollama
from llm_config import OLLAMA_HOST, LLM_MODEL, KEYWORD_EXTRACTION_PROMPT, LLM_TIMEOUT


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
        # Create client with timeout at the HTTP request level
        self.ollama_client = ollama.Client(
            host=ollama_host or OLLAMA_HOST,
            timeout=LLM_TIMEOUT
        )
        self.model = model or LLM_MODEL

    def extract_keywords_from_message(self, message_text: str, existing_keywords: List[str] = None) -> List[str]:
        """Extract keywords from a single message using LLM.

        Args:
            message_text: Message text to extract keywords from
            existing_keywords: Optional list of existing keywords to provide as context

        Returns:
            List of extracted keywords

        Raises:
            RuntimeError: If Ollama is not running or model not found
        """
        if not message_text or not message_text.strip():
            return []

        try:
            # Format existing keywords for prompt (comma-separated)
            if existing_keywords:
                keywords_str = ", ".join(existing_keywords)
            else:
                keywords_str = "(none yet - this is the first extraction)"

            # Format the prompt with both message and existing keywords
            prompt = KEYWORD_EXTRACTION_PROMPT.format(
                keywords=keywords_str,
                message=message_text
            )

            # Call LLM (timeout is set at Client level)
            response = self.ollama_client.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )

            # Parse response - expecting comma-separated keywords (but LLM sometimes uses newlines)
            response_text = response.get('response', '').strip()
            if not response_text:
                return []

            # Split by comma first, then split each result by newline
            # This handles both "keyword1, keyword2" and "keyword1\nkeyword2" formats
            keywords = []
            for part in response_text.split(','):
                # Further split by newlines in case LLM used mixed format
                for keyword in part.split('\n'):
                    keyword = keyword.strip()
                    if keyword:
                        keywords.append(keyword)

            return keywords

        except Exception as e:
            # Provide clear error message and halt
            error_msg = str(e).lower()
            error_type = type(e).__name__

            # Check for timeout
            if 'timeout' in error_msg or 'timed out' in error_msg or 'TimeoutError' in error_type:
                raise RuntimeError(
                    f"LLM request timed out after {LLM_TIMEOUT} seconds. "
                    f"Message was too long or LLM is overloaded. "
                    f"Consider increasing LLM_TIMEOUT in llm_config.py (current: {LLM_TIMEOUT}s)"
                ) from e
            # Check for model not found
            elif 'not found' in error_msg or '404' in error_msg:
                raise RuntimeError(
                    f"LLM model '{self.model}' not found. "
                    f"Please ensure Ollama is running and the model is installed. "
                    f"Try: ollama pull {self.model}"
                ) from e
            # Check for connection errors
            elif 'connection' in error_msg or 'refused' in error_msg:
                raise RuntimeError(
                    f"Cannot connect to Ollama at {OLLAMA_HOST}. "
                    f"Please ensure Ollama is running."
                ) from e
            else:
                # Re-raise unexpected errors with context
                raise RuntimeError(f"Error extracting keywords ({error_type}): {e}") from e

    def extract_keywords_from_messages(self, messages: List[str], existing_keywords: List[str] = None) -> List[str]:
        """Extract keywords from multiple messages.

        Args:
            messages: List of message texts
            existing_keywords: Optional list of existing keywords to provide as context

        Returns:
            List of all keywords from all messages (may contain duplicates)
        """
        all_keywords = []
        for message_text in messages:
            keywords = self.extract_keywords_from_message(message_text, existing_keywords)
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


def load_existing_keywords(file_path: str) -> List[str]:
    """Load keywords from a text file (one keyword per line).

    Args:
        file_path: Path to keywords file

    Returns:
        List of keywords from file
    """
    keywords = []
    with open(file_path, 'r') as f:
        for line in f:
            keyword = line.strip()
            if keyword:  # Skip empty lines
                keywords.append(keyword)
    return keywords


def merge_keyword_lists(existing_keywords: List[str], new_keywords: Set[str]) -> Set[str]:
    """Merge new keywords with existing keywords, removing duplicates.

    Args:
        existing_keywords: List of existing keywords
        new_keywords: Set of new keywords to merge

    Returns:
        Set of merged keywords (case-insensitive)
    """
    # Convert all to lowercase for case-insensitive merging
    merged = set()

    # Add existing keywords
    for keyword in existing_keywords:
        merged.add(keyword.lower())

    # Add new keywords
    for keyword in new_keywords:
        merged.add(keyword.lower())

    return merged


def filter_noise_keywords(keywords: Set[str]) -> Set[str]:
    """Filter out noise keywords (common words, short words, numbers-only).

    Args:
        keywords: Set of keywords to filter

    Returns:
        Set of filtered keywords
    """
    # Common stop words to filter out
    stop_words = {
        "the", "and", "a", "an", "is", "are", "was", "were", "be", "been",
        "of", "to", "in", "for", "on", "at", "by", "with", "from", "as",
        "this", "that", "these", "those", "it", "its", "if", "or", "but"
    }

    filtered = set()
    for keyword in keywords:
        keyword_lower = keyword.lower()

        # Remove stop words
        if keyword_lower in stop_words:
            continue

        # Remove very short words (< 2 chars), except "ng" (nose gear)
        if len(keyword_lower) < 2:
            continue

        # Remove numbers-only
        if keyword_lower.isdigit():
            continue

        # Keep this keyword
        filtered.add(keyword_lower)

    return filtered


def sort_keywords(keywords: Set[str]) -> List[str]:
    """Sort keywords alphabetically.

    Args:
        keywords: Set of keywords

    Returns:
        Sorted list of keywords
    """
    return sorted(list(keywords))
