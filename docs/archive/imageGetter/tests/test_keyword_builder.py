# ABOUTME: Tests for keyword_builder.py message sampling functions
# ABOUTME: Verifies message loading, random sampling, and text extraction

import pytest
import json
import tempfile
import os
from pathlib import Path

# Import from parent directory
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from keyword_builder import (
    load_image_index, sample_random_messages, extract_message_text,
    KeywordExtractor, aggregate_keywords,
    load_existing_keywords, merge_keyword_lists, filter_noise_keywords, sort_keywords
)


class TestLoadImageIndex:
    """Test loading image_index.json file."""

    def test_load_image_index(self):
        """Test loading a valid image index file."""
        # Create a temporary test index file
        test_index = {
            "MSG001": {
                "metadata": {
                    "message_id": "MSG001",
                    "subject": "Test firewall installation",
                    "author": "test@example.com",
                    "date": "Jan 1, 2020"
                },
                "images": [{"url": "http://example.com/img1.jpg"}]
            },
            "MSG002": {
                "metadata": {
                    "message_id": "MSG002",
                    "subject": "Cowling work",
                    "author": "test2@example.com",
                    "date": "Jan 2, 2020"
                },
                "images": [{"url": "http://example.com/img2.jpg"}]
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_index, f)
            temp_path = f.name

        try:
            result = load_image_index(temp_path)
            assert isinstance(result, dict)
            assert len(result) == 2
            assert "MSG001" in result
            assert "MSG002" in result
            assert result["MSG001"]["metadata"]["subject"] == "Test firewall installation"
        finally:
            os.unlink(temp_path)


class TestSampleRandomMessages:
    """Test random message sampling."""

    def test_sample_random_messages(self):
        """Test sampling N random messages from index."""
        test_index = {
            "MSG001": {
                "metadata": {
                    "message_id": "MSG001",
                    "subject": "Test 1",
                    "author": "test1@example.com",
                    "date": "Jan 1, 2020"
                },
                "images": []
            },
            "MSG002": {
                "metadata": {
                    "message_id": "MSG002",
                    "subject": "Test 2",
                    "author": "test2@example.com",
                    "date": "Jan 2, 2020"
                },
                "images": []
            },
            "MSG003": {
                "metadata": {
                    "message_id": "MSG003",
                    "subject": "Test 3",
                    "author": "test3@example.com",
                    "date": "Jan 3, 2020"
                },
                "images": []
            },
            "MSG004": {
                "metadata": {
                    "message_id": "MSG004",
                    "subject": "Test 4",
                    "author": "test4@example.com",
                    "date": "Jan 4, 2020"
                },
                "images": []
            },
            "MSG005": {
                "metadata": {
                    "message_id": "MSG005",
                    "subject": "Test 5",
                    "author": "test5@example.com",
                    "date": "Jan 5, 2020"
                },
                "images": []
            }
        }

        # Sample 3 messages
        result = sample_random_messages(test_index, 3)
        assert isinstance(result, list)
        assert len(result) == 3

        # Verify each sampled message has metadata
        for msg in result:
            assert "metadata" in msg
            assert "message_id" in msg["metadata"]
            assert "subject" in msg["metadata"]

    def test_sample_all_messages_when_sample_larger_than_index(self):
        """Test sampling when sample_size >= total messages."""
        test_index = {
            "MSG001": {
                "metadata": {"message_id": "MSG001", "subject": "Test 1"},
                "images": []
            },
            "MSG002": {
                "metadata": {"message_id": "MSG002", "subject": "Test 2"},
                "images": []
            }
        }

        # Request more than available
        result = sample_random_messages(test_index, 10)
        assert len(result) == 2  # Should return all available messages


class TestExtractMessageText:
    """Test extracting clean text from messages."""

    def test_extract_message_text(self):
        """Test extracting subject and relevant fields."""
        message = {
            "metadata": {
                "message_id": "MSG001",
                "subject": "Firewall installation complete",
                "author": "builder@example.com",
                "date": "Jan 1, 2020"
            },
            "images": [{"url": "http://example.com/img.jpg"}]
        }

        result = extract_message_text(message)
        assert isinstance(result, str)
        assert "Firewall installation complete" in result
        assert len(result) > 0

    def test_extract_text_handles_escaped_characters(self):
        """Test handling escaped characters in subject."""
        message = {
            "metadata": {
                "message_id": "MSG002",
                "subject": "Re: \\[c\\-a] Van's baffles",
                "author": "builder@example.com",
                "date": "Jan 1, 2020"
            },
            "images": []
        }

        result = extract_message_text(message)
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain the subject text
        assert "baffles" in result.lower()


class TestKeywordExtractor:
    """Test LLM-based keyword extraction."""

    @pytest.mark.skip(reason="Requires Ollama running - manual test only")
    def test_extract_keywords_from_message(self):
        """Test extracting keywords from a single message using LLM."""
        extractor = KeywordExtractor()
        message_text = "Firewall installation complete with new engine baffles"

        result = extractor.extract_keywords_from_message(message_text)
        assert isinstance(result, list)
        # Should extract aircraft-related keywords
        result_lower = [k.lower() for k in result]
        assert any("firewall" in k or "baffle" in k or "engine" in k for k in result_lower)

    @pytest.mark.skip(reason="Requires Ollama running - manual test only")
    def test_extract_keywords_from_multiple_messages(self):
        """Test extracting keywords from multiple messages."""
        extractor = KeywordExtractor()
        messages = [
            "Firewall installation complete",
            "Cowling work in progress",
            "Landing gear installed"
        ]

        result = extractor.extract_keywords_from_messages(messages)
        assert isinstance(result, list)
        assert len(result) > 0
        # Should have keywords from multiple messages
        result_lower = [k.lower() for k in result]
        # Check for keywords from different messages
        keyword_count = sum(1 for k in result_lower
                           if any(term in k for term in ["firewall", "cowling", "landing", "gear"]))
        assert keyword_count > 0


class TestAggregateKeywords:
    """Test keyword aggregation and deduplication."""

    def test_aggregate_keywords(self):
        """Test aggregating keywords from multiple lists."""
        keyword_lists = [
            ["firewall", "engine", "baffles"],
            ["cowling", "firewall", "panel"],
            ["landing gear", "nose gear", "FIREWALL"]
        ]

        result = aggregate_keywords(keyword_lists)
        assert isinstance(result, set)
        # Should have unique keywords (case-insensitive)
        assert "firewall" in result or "FIREWALL" in result
        assert len(result) == 7  # firewall, engine, baffles, cowling, panel, landing gear, nose gear

    def test_aggregate_empty_lists(self):
        """Test aggregating empty keyword lists."""
        result = aggregate_keywords([])
        assert isinstance(result, set)
        assert len(result) == 0

    def test_aggregate_handles_duplicates_case_insensitive(self):
        """Test that aggregation removes case-insensitive duplicates."""
        keyword_lists = [
            ["Firewall", "Engine"],
            ["firewall", "engine"],
            ["FIREWALL", "ENGINE"]
        ]

        result = aggregate_keywords(keyword_lists)
        assert len(result) == 2  # Only 2 unique keywords despite 6 total


class TestLoadExistingKeywords:
    """Test loading keywords from file."""

    def test_load_existing_keywords(self):
        """Test loading keywords from a text file."""
        # Create a temporary keywords file
        keywords = ["firewall", "engine", "cowling", "panel", "landing gear"]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for keyword in keywords:
                f.write(f"{keyword}\n")
            temp_path = f.name

        try:
            result = load_existing_keywords(temp_path)
            assert isinstance(result, list)
            assert len(result) == 5
            assert "firewall" in result
            assert "landing gear" in result
        finally:
            os.unlink(temp_path)

    def test_load_empty_file(self):
        """Test loading an empty keywords file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name

        try:
            result = load_existing_keywords(temp_path)
            assert isinstance(result, list)
            assert len(result) == 0
        finally:
            os.unlink(temp_path)


class TestMergeKeywordLists:
    """Test merging keyword lists."""

    def test_merge_keyword_lists(self):
        """Test merging new keywords with existing."""
        existing = ["firewall", "engine", "cowling"]
        new_keywords = {"panel", "firewall", "landing gear"}

        result = merge_keyword_lists(existing, new_keywords)
        assert isinstance(result, set)
        assert len(result) == 5  # firewall appears in both but counted once
        assert "firewall" in result
        assert "panel" in result

    def test_merge_handles_case_insensitive(self):
        """Test that merge handles case-insensitive duplicates."""
        existing = ["Firewall", "Engine"]
        new_keywords = {"firewall", "panel"}

        result = merge_keyword_lists(existing, new_keywords)
        assert len(result) == 3  # firewall/Firewall counted once, engine, panel


class TestFilterNoiseKeywords:
    """Test filtering noise keywords."""

    def test_filter_noise_keywords(self):
        """Test filtering common words and noise."""
        keywords = {
            "firewall", "engine", "cowling",
            "the", "and", "a", "is",  # Common words
            "it", "on",  # Short words (<3 chars)
            "123", "456"  # Numbers-only
        }

        result = filter_noise_keywords(keywords)
        assert isinstance(result, set)
        # Should keep aircraft keywords
        assert "firewall" in result
        assert "engine" in result
        # Should remove common words
        assert "the" not in result
        assert "and" not in result
        # Should remove short words
        assert "it" not in result
        assert "on" not in result
        # Should remove numbers-only
        assert "123" not in result

    def test_filter_keeps_valid_short_keywords(self):
        """Test that filter keeps valid 2-letter keywords like 'ng' (nose gear)."""
        keywords = {"ng", "firewall", "a"}

        result = filter_noise_keywords(keywords)
        # "ng" is a valid keyword (nose gear abbreviation) - keep it
        # "a" is a common word - remove it
        assert "ng" in result
        assert "a" not in result


class TestSortKeywords:
    """Test sorting keywords."""

    def test_sort_keywords(self):
        """Test sorting keywords alphabetically."""
        keywords = {"firewall", "engine", "cowling", "panel", "baffles"}

        result = sort_keywords(keywords)
        assert isinstance(result, list)
        assert len(result) == 5
        # Check alphabetical order
        assert result == ["baffles", "cowling", "engine", "firewall", "panel"]

    def test_sort_empty_set(self):
        """Test sorting empty set."""
        result = sort_keywords(set())
        assert isinstance(result, list)
        assert len(result) == 0
