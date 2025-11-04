# ABOUTME: LLM-based keyword tagger for aircraft builder messages
# ABOUTME: Matches message text against master keyword list using Ollama LLM

import ollama
from typing import List
from llm_config import OLLAMA_HOST, LLM_MODEL, KEYWORD_TAGGING_PROMPT, LLM_TIMEOUT


class KeywordTagger:
    """Tag messages with keywords using LLM semantic matching."""

    def __init__(self, ollamahost: str = None):
        """Initialize keyword tagger with Ollama client.

        Args:
            ollamahost: Ollama server URL (defaults to OLLAMA_HOST from config)
        """
        self.host = ollamahost or OLLAMA_HOST
        self.ollamaclient = ollama.Client(
            host=self.host,
            timeout=LLM_TIMEOUT
        )

    def tag_message(self, message_text: str, keywords: List[str], model: str = None) -> tuple[List[str], str]:
        """Tag message with relevant keywords using LLM.

        Args:
            message_text: Message text to analyze
            keywords: Master keyword list to match against
            model: Optional model override (defaults to LLM_MODEL from config)

        Returns:
            Tuple of (matched_keywords, raw_response):
            - matched_keywords: List of matching keywords from master list
            - raw_response: Full LLM response text
        """
        # Handle empty inputs
        if not message_text or not message_text.strip():
            return ([], "")
        if not keywords:
            return ([], "")

        try:
            # Format keyword list for prompt
            keywords_str = ", ".join(keywords)

            # Format prompt
            prompt = KEYWORD_TAGGING_PROMPT.format(
                keywords=keywords_str,
                message=message_text
            )

            # Call LLM
            response = self.ollamaclient.generate(
                model=model or LLM_MODEL,
                prompt=prompt,
                stream=False
            )

            # Parse response (keep raw for return, strip for parsing)
            raw_response = response.get('response', '')
            response_text = raw_response.strip()
            if not response_text or response_text.upper() == 'NONE':
                return ([], raw_response)

            # Split by comma and/or newline (handle both formats)
            matched_keywords = []
            for part in response_text.split(','):
                for keyword in part.split('\n'):
                    keyword = keyword.strip()
                    if keyword and keyword.upper() != 'NONE':
                        # Validate against master keyword list (case-insensitive)
                        keyword_lower = keyword.lower()
                        for master_kw in keywords:
                            if master_kw.lower() == keyword_lower:
                                if master_kw not in matched_keywords:
                                    matched_keywords.append(master_kw)
                                break

            return (matched_keywords, raw_response)

        except Exception as e:
            # Log error and return empty list (graceful degradation)
            # Don't crash the batch processing
            print(f"ERROR tagging message: {e}")
            return ([], f"ERROR: {e}")
