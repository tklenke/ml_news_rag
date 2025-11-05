"""Tests for search_tag_messages.py - batch message tagging with search."""

import pytest
import json
import tempfile
from pathlib import Path
from search_tag_messages import (
    load_image_index,
    load_keywords,
    tag_messages,
    save_image_index,
    extract_message_text
)


class TestLoadImageIndex:
    """Test loading image index."""

    def test_load_image_index(self, tmp_path):
        """Test loading image index from JSON file."""
        index_file = tmp_path / "test_index.json"
        test_data = {
            "msg1": {
                "metadata": {"subject": "Test"},
                "images": []
            }
        }
        index_file.write_text(json.dumps(test_data))

        result = load_image_index(str(index_file))

        assert result == test_data


class TestLoadKeywords:
    """Test loading keywords."""

    def test_load_keywords(self, tmp_path):
        """Test loading keywords from text file."""
        kw_file = tmp_path / "keywords.txt"
        kw_file.write_text("firewall\ncowling\nengine\n")

        result = load_keywords(str(kw_file))

        assert result == ["firewall", "cowling", "engine"]


class TestExtractMessageText:
    """Test extracting message text."""

    def test_extract_subject_only(self):
        """Test extracting text from subject only."""
        message = {
            "metadata": {"subject": "Firewall installation"}
        }

        result = extract_message_text(message)

        assert "Firewall installation" in result


class TestTagMessages:
    """Test batch tagging of messages."""

    @pytest.fixture
    def test_index(self, tmp_path):
        """Create test index file."""
        index_file = tmp_path / "test_index.json"
        test_data = {
            "msg1": {
                "metadata": {"subject": "Installing firewall"},
                "images": []
            },
            "msg2": {
                "metadata": {"subject": "Cowling work"},
                "images": []
            },
            "msg3": {
                "metadata": {"subject": "Engine mount"},
                "images": [],
                "keywords": ["existing"]  # Already tagged
            }
        }
        index_file.write_text(json.dumps(test_data))
        return str(index_file)

    @pytest.fixture
    def test_keywords(self, tmp_path):
        """Create test keywords file."""
        kw_file = tmp_path / "keywords.txt"
        kw_file.write_text("firewall\ncowling\nengine\nfuel\ninstall\n")
        return str(kw_file)

    def test_tag_messages_basic(self, test_index, test_keywords):
        """Test basic message tagging."""
        stats = tag_messages(test_index, test_keywords)

        # Load result
        with open(test_index) as f:
            result = json.load(f)

        # msg1 should have firewall and install keywords
        assert "keywords" in result["msg1"]
        assert "firewall" in result["msg1"]["keywords"]
        assert "install" in result["msg1"]["keywords"]

        # msg2 should have cowling keyword
        assert "keywords" in result["msg2"]
        assert "cowling" in result["msg2"]["keywords"]

        # Stats should show 3 processed (all messages, no skipping)
        assert stats["processed"] == 3
        assert stats["skipped"] == 0

    def test_merge_existing_keywords(self, test_index, test_keywords):
        """Test that existing keywords are merged with newly matched keywords."""
        # Load original data
        with open(test_index) as f:
            original = json.load(f)

        # Tag messages
        stats = tag_messages(test_index, test_keywords)

        # Load result
        with open(test_index) as f:
            result = json.load(f)

        # msg3 had ["existing"], should now have ["existing", "engine"]
        # (engine is found in "Engine mount" subject)
        assert "existing" in result["msg3"]["keywords"]  # Original preserved
        assert "engine" in result["msg3"]["keywords"]  # New match added
        # No messages skipped
        assert stats["skipped"] == 0

    def test_empty_keywords_valid_state(self, test_index, test_keywords):
        """Test that empty keyword list [] is a valid state."""
        # Tag messages
        tag_messages(test_index, test_keywords)

        # Load result
        with open(test_index) as f:
            result = json.load(f)

        # All messages should have keywords field (even if empty)
        for msg_id, msg in result.items():
            assert "keywords" in msg
            assert isinstance(msg["keywords"], list)

    def test_invalid_keywords_filtered_in_batch(self, tmp_path):
        """Test that invalid keywords are filtered during batch tagging."""
        # Create index with message containing "cozy"
        index_file = tmp_path / "test_index.json"
        test_data = {
            "msg1": {
                "metadata": {"subject": "This cozy firewall installation"},
                "images": [],
                "keywords" : ["stevenlevy"]
            }
        }
        index_file.write_text(json.dumps(test_data))

        # Create keywords file including "cozy"
        kw_file = tmp_path / "keywords.txt"
        kw_file.write_text("cozy\nfirewall\nengine")

        # Tag messages
        tag_messages(str(index_file), str(kw_file))

        # Load result
        with open(index_file) as f:
            result = json.load(f)

        # "cozy" should be filtered out, firewall should be present
        assert "keywords" in result["msg1"]
        assert "cozy" not in result["msg1"]["keywords"]
        assert "firewall" in result["msg1"]["keywords"]
        assert "stevenlevy" in result["msg1"]["keywords"]
