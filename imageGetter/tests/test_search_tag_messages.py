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
        """Test that existing keywords are merged when keep_existing=True."""
        # Modify test data to have a valid keyword in existing
        with open(test_index) as f:
            data = json.load(f)
        # Add "fuel" to existing keywords (fuel is in keywords.txt)
        data["msg3"]["keywords"] = ["fuel", "existing"]
        with open(test_index, 'w') as f:
            json.dump(data, f)

        # Tag messages with keep_existing=True
        stats = tag_messages(test_index, test_keywords, keep_existing=True)

        # Load result
        with open(test_index) as f:
            result = json.load(f)

        # msg3 had ["fuel", "existing"], should now have ["fuel", "engine"]
        # - "fuel" is in vocabulary, preserved
        # - "existing" NOT in vocabulary, filtered out
        # - "engine" found in "Engine mount" subject, added
        assert "fuel" in result["msg3"]["keywords"]  # Valid existing preserved
        assert "existing" not in result["msg3"]["keywords"]  # Invalid filtered out
        assert "engine" in result["msg3"]["keywords"]  # New match added
        # No messages skipped
        assert stats["skipped"] == 0

    def test_replace_existing_keywords_default(self, test_index, test_keywords):
        """Test that existing keywords are replaced by default (keep_existing=False)."""
        # Load original data
        with open(test_index) as f:
            original = json.load(f)

        # Tag messages with default behavior (keep_existing=False)
        stats = tag_messages(test_index, test_keywords)

        # Load result
        with open(test_index) as f:
            result = json.load(f)

        # msg3 had ["existing"], should now have ONLY ["engine"]
        # (engine is found in "Engine mount" subject, "existing" discarded)
        assert "existing" not in result["msg3"]["keywords"]  # Original discarded
        assert "engine" in result["msg3"]["keywords"]  # New match only
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
        """Test that invalid keywords are filtered during batch tagging (default replace mode)."""
        # Create index with message containing "cozy"
        index_file = tmp_path / "test_index.json"
        test_data = {
            "msg1": {
                "metadata": {"subject": "This cozy firewall installation"},
                "images": [],
                "keywords" : ["stevenlevy","COZY","cozy"]
            }
        }
        index_file.write_text(json.dumps(test_data))

        # Create keywords file including "cozy"
        kw_file = tmp_path / "keywords.txt"
        kw_file.write_text("cozy\nfirewall\nengine")

        # Tag messages (default: replace existing keywords)
        tag_messages(str(index_file), str(kw_file))

        # Load result
        with open(index_file) as f:
            result = json.load(f)

        # Default mode: existing keywords discarded, only newly matched kept
        assert "keywords" in result["msg1"]
        # Verify no case variant of 'cozy' exists (filtered as invalid)
        assert not any(kw.lower() == 'cozy' for kw in result["msg1"]["keywords"])
        # stevenlevy was in existing keywords but discarded (replace mode)
        assert "stevenlevy" not in result["msg1"]["keywords"]
        # firewall matched from message text and kept
        assert "firewall" in result["msg1"]["keywords"]

    def test_vocabulary_restriction(self, tmp_path):
        """Test that only keywords from aircraft_keywords.txt are allowed."""
        # Create index with keywords NOT in vocabulary
        index_file = tmp_path / "test_index.json"
        test_data = {
            "msg1": {
                "metadata": {"subject": "Firewall installation"},
                "keywords": ["firewall", "random_keyword_not_in_vocab", "another_invalid"],
                "images": []
            }
        }
        index_file.write_text(json.dumps(test_data))

        # Create keywords file with limited vocabulary
        kw_file = tmp_path / "keywords.txt"
        kw_file.write_text("firewall\nengine\nfuel")

        # Tag messages (default: replace mode)
        tag_messages(str(index_file), str(kw_file))

        # Load result
        with open(index_file) as f:
            result = json.load(f)

        # Only firewall should remain (in vocabulary and matched in subject)
        assert "keywords" in result["msg1"]
        assert "firewall" in result["msg1"]["keywords"]
        # Invalid keywords should be filtered out
        assert "random_keyword_not_in_vocab" not in result["msg1"]["keywords"]
        assert "another_invalid" not in result["msg1"]["keywords"]

    def test_vocabulary_restriction_with_merge(self, tmp_path):
        """Test that vocabulary restriction works in merge mode too."""
        # Create index with keywords NOT in vocabulary
        index_file = tmp_path / "test_index.json"
        test_data = {
            "msg1": {
                "metadata": {"subject": "Firewall and engine work"},
                "keywords": ["firewall", "random_keyword_not_in_vocab", "engine"],
                "images": []
            }
        }
        index_file.write_text(json.dumps(test_data))

        # Create keywords file with limited vocabulary
        kw_file = tmp_path / "keywords.txt"
        kw_file.write_text("firewall\nengine\nfuel")

        # Tag messages with keep_existing=True
        tag_messages(str(index_file), str(kw_file), keep_existing=True)

        # Load result
        with open(index_file) as f:
            result = json.load(f)

        # firewall and engine should remain (both in vocabulary)
        assert "keywords" in result["msg1"]
        assert "firewall" in result["msg1"]["keywords"]
        assert "engine" in result["msg1"]["keywords"]
        # Invalid keyword should be filtered out even in merge mode
        assert "random_keyword_not_in_vocab" not in result["msg1"]["keywords"]

    def test_invalid_keywords_filtered_with_merge(self, tmp_path):
        """Test that invalid keywords are filtered when merging (keep_existing=True)."""
        # Create index with message containing "cozy"
        index_file = tmp_path / "test_index.json"
        test_data = {
            "msg1": {
                "metadata": {"subject": "This cozy firewall installation"},
                "images": [],
                "keywords" : ["stevenlevy","COZY","cozy","firewall"]
            }
        }
        index_file.write_text(json.dumps(test_data))

        # Create keywords file - include firewall but not stevenlevy or cozy
        kw_file = tmp_path / "keywords.txt"
        kw_file.write_text("firewall\nengine\nfuel")

        # Tag messages with keep_existing=True
        tag_messages(str(index_file), str(kw_file), keep_existing=True)

        # Load result
        with open(index_file) as f:
            result = json.load(f)

        # Merge mode: only valid vocabulary keywords kept
        assert "keywords" in result["msg1"]
        # Verify "cozy" filtered out (in INVALID_KEYWORDS)
        assert not any(kw.lower() == 'cozy' for kw in result["msg1"]["keywords"])
        # stevenlevy filtered out (not in vocabulary)
        assert "stevenlevy" not in result["msg1"]["keywords"]
        # firewall preserved (in vocabulary and in existing keywords)
        assert "firewall" in result["msg1"]["keywords"]
