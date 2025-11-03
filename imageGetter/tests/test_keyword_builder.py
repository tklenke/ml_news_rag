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
from keyword_builder import load_image_index, sample_random_messages, extract_message_text


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
