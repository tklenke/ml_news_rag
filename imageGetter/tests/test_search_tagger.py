"""Tests for search_tagger.py - keyword matching with stemming."""

import pytest
from search_tagger import SearchTagger


class TestSearchTagger:
    """Test SearchTagger class for keyword matching with stemming."""

    def test_exact_match(self):
        """Test exact keyword match in message text."""
        tagger = SearchTagger()
        message_text = "I installed the firewall today."
        keywords = ["firewall", "cowling", "engine"]

        matched = tagger.find_keywords(message_text, keywords)

        assert "firewall" in matched
        assert "cowling" not in matched
        assert "engine" not in matched

    def test_case_insensitive(self):
        """Test case-insensitive matching."""
        tagger = SearchTagger()
        message_text = "Installing the FIREWALL and Cowling."
        keywords = ["firewall", "cowling"]

        matched = tagger.find_keywords(message_text, keywords)

        assert "firewall" in matched
        assert "cowling" in matched

    def test_stemming_plural(self):
        """Test stemming matches plurals."""
        tagger = SearchTagger()
        message_text = "I installed the firewalls today."
        keywords = ["firewall"]

        matched = tagger.find_keywords(message_text, keywords)

        assert "firewall" in matched

    def test_stemming_ing_form(self):
        """Test stemming matches -ing forms."""
        tagger = SearchTagger()
        message_text = "I am installing the firewall."
        keywords = ["install"]

        matched = tagger.find_keywords(message_text, keywords)

        assert "install" in matched

    def test_stemming_ed_form(self):
        """Test stemming matches -ed forms."""
        tagger = SearchTagger()
        message_text = "I installed the firewall."
        keywords = ["install"]

        matched = tagger.find_keywords(message_text, keywords)

        assert "install" in matched

    def test_word_boundaries(self):
        """Test that partial word matches are excluded."""
        tagger = SearchTagger()
        message_text = "The software installation was successful."
        keywords = ["stall"]  # Should NOT match "inSTALLation"

        matched = tagger.find_keywords(message_text, keywords)

        assert "stall" not in matched

    def test_dedupe_keywords(self):
        """Test that duplicate matches are removed."""
        tagger = SearchTagger()
        message_text = "The firewall and firewall installation."
        keywords = ["firewall"]

        matched = tagger.find_keywords(message_text, keywords)

        assert matched.count("firewall") == 1

    def test_multiple_keywords_match(self):
        """Test multiple keywords matching in same text."""
        tagger = SearchTagger()
        message_text = "I installed the firewall and cowling today."
        keywords = ["firewall", "cowling", "install"]

        matched = tagger.find_keywords(message_text, keywords)

        assert len(matched) == 3
        assert "firewall" in matched
        assert "cowling" in matched
        assert "install" in matched

    def test_empty_message(self):
        """Test empty message returns empty list."""
        tagger = SearchTagger()
        message_text = ""
        keywords = ["firewall"]

        matched = tagger.find_keywords(message_text, keywords)

        assert matched == []

    def test_empty_keywords(self):
        """Test empty keyword list returns empty list."""
        tagger = SearchTagger()
        message_text = "I installed the firewall."
        keywords = []

        matched = tagger.find_keywords(message_text, keywords)

        assert matched == []

    def test_no_matches(self):
        """Test message with no keyword matches."""
        tagger = SearchTagger()
        message_text = "The weather is nice today."
        keywords = ["firewall", "cowling"]

        matched = tagger.find_keywords(message_text, keywords)

        assert matched == []

    def test_hyphenated_words(self):
        """Test matching hyphenated words."""
        tagger = SearchTagger()
        message_text = "The co-pilot checked the fuel-system."
        keywords = ["pilot", "fuel", "system"]

        matched = tagger.find_keywords(message_text, keywords)

        # Should match "pilot" in "co-pilot" and both "fuel" and "system"
        assert "pilot" in matched
        assert "fuel" in matched
        assert "system" in matched

    def test_invalid_keywords_filtered(self):
        """Test that invalid keywords are filtered out."""
        tagger = SearchTagger()
        message_text = "This cozy firewall and engine work was great."
        keywords = ["cozy", "firewall", "engine"]

        matched = tagger.find_keywords(message_text, keywords)

        # 'cozy' should be filtered out as it's in INVALID_KEYWORDS
        assert "cozy" not in matched
        assert "firewall" in matched
        assert "engine" in matched

    def test_invalid_keywords_case_insensitive(self):
        """Test that invalid keyword filtering is case-insensitive."""
        tagger = SearchTagger()
        message_text = "This COZY firewall installation."
        keywords = ["Cozy", "COZY", "cozy", "firewall"]

        matched = tagger.find_keywords(message_text, keywords)

        # All variations of 'cozy' should be filtered out
        assert "Cozy" not in matched
        assert "COZY" not in matched
        assert "cozy" not in matched
        assert "firewall" in matched
