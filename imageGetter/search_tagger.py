# ABOUTME: Search-based keyword tagger using stemming for keyword matching
# ABOUTME: Fast, deterministic alternative to LLM-based tagging

import re
from typing import List


class SearchTagger:
    """Tag messages with keywords using search and stemming."""

    def __init__(self):
        """Initialize search tagger."""
        pass

    def _stem(self, word: str) -> str:
        """Apply simple stemming to a word.

        Handles common suffixes: plurals, -ing, -ed, -er, -est, -ly, -tion, -ness

        Args:
            word: Word to stem (lowercase)

        Returns:
            Stemmed word
        """
        # Handle empty/short words
        if len(word) <= 2:
            return word

        # Store original for minimum length checks
        original_len = len(word)

        # Suffix rules (order matters - try longer suffixes first)
        suffixes = [
            ('ational', 'ate'),    # relational -> relate
            ('tional', 'tion'),    # conditional -> condition
            ('tion', 'tion'),      # condition -> condition (keep as-is)
            ('ness', ''),          # goodness -> good
            ('ment', ''),          # establishment -> establish
            ('iest', 'y'),         # happiest -> happy
            ('iest', 'i'),         # prettiest -> pretti
            ('ying', 'y'),         # flying -> fly
            ('ing', ''),           # installing -> install
            ('ies', 'y'),          # berries -> berry
            ('ied', 'y'),          # tried -> try
            ('sses', 'ss'),        # dresses -> dress
            ('xes', 'x'),          # boxes -> box
            ('zes', 'z'),          # sizes -> size
            ('ches', 'ch'),        # switches -> switch
            ('shes', 'sh'),        # dishes -> dish
            ('ses', 's'),          # houses -> hous
            ('ess', 'ess'),        # dress -> dress (keep as-is)
            ('est', ''),           # fastest -> fast
            ('ers', 'er'),         # workers -> worker
            ('eer', 'eer'),        # engineer -> engineer (keep as-is)
            ('eer', 'eer'),        # engineer -> engineer (keep as-is)
            ('ied', 'y'),          # carried -> carry
            ('ied', 'i'),          # died -> di
            ('eed', 'ee'),         # agreed -> agree
            ('eds', 'ed'),         # beds -> bed
            ('ed', ''),            # installed -> install
            ('es', ''),            # boxes -> box (after longer rules)
            ('er', ''),            # faster -> fast
            ('ly', ''),            # quickly -> quick
            ('s', ''),             # firewalls -> firewall
        ]

        for suffix, replacement in suffixes:
            if word.endswith(suffix):
                stem = word[:-len(suffix)] + replacement
                # Don't make word too short (minimum 2 chars after stemming)
                if len(stem) >= 2:
                    return stem

        return word

    def find_keywords(self, message_text: str, keywords: List[str]) -> List[str]:
        """Find keywords that match in message text using stemming.

        Args:
            message_text: Message text to search
            keywords: List of keywords to search for

        Returns:
            List of matched keywords (deduped, from original keyword list)
        """
        # Handle empty inputs
        if not message_text or not message_text.strip():
            return []
        if not keywords:
            return []

        # Normalize message text
        message_lower = message_text.lower()

        # Split message into words (handle hyphens as word separators)
        # This allows "co-pilot" to match "pilot"
        message_words = re.findall(r'\b\w+\b', message_lower)

        # Stem all message words
        message_stems = set(self._stem(word) for word in message_words)

        # Find matching keywords
        matched = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            keyword_stem = self._stem(keyword_lower)

            # Check if keyword stem appears in message stems
            if keyword_stem in message_stems:
                if keyword not in matched:  # Dedupe
                    matched.append(keyword)

        return matched
