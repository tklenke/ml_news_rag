"""Tests for batch message tagger."""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from llm_tag_messages import (
    load_image_index,
    load_keywords,
    tag_messages,
    save_image_index,
    extract_message_text
)


class TestLoadImageIndex:
    """Test loading image index."""

    def test_load_image_index(self, tmp_path):
        """Test loading valid image index."""
        index_file = tmp_path / "test_index.json"
        test_data = {
            "msg1": {
                "metadata": {"subject": "Test message"},
                "images": []
            }
        }
        index_file.write_text(json.dumps(test_data))

        result = load_image_index(str(index_file))

        assert isinstance(result, dict)
        assert "msg1" in result
        assert result["msg1"]["metadata"]["subject"] == "Test message"

    def test_load_nonexistent_file(self):
        """Test loading nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_image_index("nonexistent.json")


class TestLoadKeywords:
    """Test loading keywords from file."""

    def test_load_keywords_plain_list(self, tmp_path):
        """Test loading keywords from plain text file."""
        kw_file = tmp_path / "keywords.txt"
        kw_file.write_text("firewall\ncowling\nengine\n")

        result = load_keywords(str(kw_file))

        assert isinstance(result, list)
        assert len(result) == 3
        assert "firewall" in result
        assert "cowling" in result
        assert "engine" in result

    def test_load_keywords_with_bullets(self, tmp_path):
        """Test loading keywords with bullet points (like kw2.txt)."""
        kw_file = tmp_path / "keywords.txt"
        kw_file.write_text("*   *   *   firewall\n*   *   *   cowling\n")

        result = load_keywords(str(kw_file))

        assert isinstance(result, list)
        assert "firewall" in result
        assert "cowling" in result
        # Should strip bullets
        assert "*" not in result[0]

    def test_load_keywords_empty_lines(self, tmp_path):
        """Test loading keywords with empty lines."""
        kw_file = tmp_path / "keywords.txt"
        kw_file.write_text("firewall\n\ncowling\n  \nengine\n")

        result = load_keywords(str(kw_file))

        assert len(result) == 3
        assert "" not in result

    def test_load_nonexistent_keywords_file(self):
        """Test loading nonexistent keywords file raises error."""
        with pytest.raises(FileNotFoundError):
            load_keywords("nonexistent.txt")


class TestExtractMessageText:
    """Test extracting text from messages."""

    def test_extract_subject_only(self):
        """Test extracting subject from message (when markdown file not found)."""
        message = {
            "metadata": {
                "subject": "Installing firewall today",
                "message_id": "nonexistent123"
            }
        }

        # Should fall back to subject if markdown file not found
        result = extract_message_text(message)

        assert "Installing firewall today" in result

    def test_extract_empty_message(self):
        """Test extracting from empty message."""
        message = {
            "metadata": {}
        }

        result = extract_message_text(message)

        assert isinstance(result, str)
        assert len(result) == 0

    def test_extract_full_message_from_markdown(self, tmp_path):
        """Test extracting full message body from markdown file."""
        # Create temporary markdown file
        md_dir = tmp_path / "A"
        md_dir.mkdir()
        md_file = md_dir / "A-TestMsg.md"
        md_content = """[Original Message ID:A-TestMsg](...)
 # Installing firewall today

 ### author

 This is the message body.
 I'm installing the firewall.
 It's going well.
"""
        md_file.write_text(md_content)

        message = {
            "metadata": {
                "subject": "Installing firewall today",
                "message_id": "A-TestMsg"
            }
        }

        result = extract_message_text(message, msgs_md_dir=str(tmp_path))

        # Should contain both subject and body
        assert "Installing firewall today" in result
        assert "message body" in result
        assert "installing the firewall" in result


class TestTagMessages:
    """Test batch tagging messages."""

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
                "metadata": {"subject": "Cowling attachment"},
                "images": []
            },
            "msg3": {
                "metadata": {"subject": "Already tagged"},
                "images": [],
                "keywords": ["engine"]
            }
        }
        index_file.write_text(json.dumps(test_data, indent=2))
        return str(index_file)

    @pytest.fixture
    def test_keywords(self, tmp_path):
        """Create test keywords file."""
        kw_file = tmp_path / "keywords.txt"
        kw_file.write_text("firewall\ncowling\nengine\nfuel\n")
        return str(kw_file)

    def test_skip_already_tagged_messages(self, test_index, test_keywords):
        """Test that messages with keywords are skipped by default."""
        # Load original data
        with open(test_index) as f:
            original = json.load(f)

        # Tag messages
        stats = tag_messages(test_index, test_keywords)

        # Load result
        with open(test_index) as f:
            result = json.load(f)

        # msg3 already had keywords, should be unchanged
        assert result["msg3"]["keywords"] == original["msg3"]["keywords"]
        # Should report skipped message
        assert stats["skipped"] >= 1

    def test_tag_empty_list_valid_state(self, test_index, test_keywords):
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

    def test_limit_processing(self, test_index, test_keywords):
        """Test --limit flag processes exactly N messages."""
        # Tag with limit of 1
        stats = tag_messages(test_index, test_keywords, limit=1)

        # Should process exactly 1 message
        assert stats["processed"] == 1

        # Load result
        with open(test_index) as f:
            result = json.load(f)

        # Count how many have keywords
        tagged_count = sum(1 for msg in result.values() if "keywords" in msg)
        assert tagged_count >= 1

    def test_preserves_other_fields(self, test_index, test_keywords):
        """Test that tagging preserves all other message fields."""
        # Load original
        with open(test_index) as f:
            original = json.load(f)

        # Tag messages
        tag_messages(test_index, test_keywords)

        # Load result
        with open(test_index) as f:
            result = json.load(f)

        # Check that metadata and images are preserved
        for msg_id in original:
            assert result[msg_id]["metadata"] == original[msg_id]["metadata"]
            assert result[msg_id]["images"] == original[msg_id]["images"]

    def test_skip_already_tagged_on_retag(self, test_index, test_keywords):
        """Test that messages with keywords are skipped on second run."""
        # First tag all messages
        tag_messages(test_index, test_keywords)

        # Load result
        with open(test_index) as f:
            result = json.load(f)

        # Save original keywords
        original_keywords = {}
        for msg_id in result:
            if "keywords" in result[msg_id]:
                original_keywords[msg_id] = result[msg_id]["keywords"].copy()

        # Try to tag again
        stats = tag_messages(test_index, test_keywords)

        # All messages should be skipped (they all have keywords now)
        assert stats["skipped"] == 3
        assert stats["processed"] == 0

        # Load result again
        with open(test_index) as f:
            result2 = json.load(f)

        # Keywords should be unchanged
        for msg_id in result2:
            assert result2[msg_id]["keywords"] == original_keywords[msg_id]

    def test_verbose_mode_prints_output(self, test_index, test_keywords, capsys):
        """Test that verbose mode prints detailed output."""
        # Import and mock at module level to avoid model not found errors
        from unittest.mock import patch
        from llm_tagger import KeywordTagger

        with patch.object(KeywordTagger, 'tag_message') as mock_tag:
            # Mock successful responses
            mock_tag.return_value = (['firewall'], 'firewall')

            # Tag with verbose mode
            tag_messages(test_index, test_keywords, limit=1, verbose=True)

            # Capture output
            captured = capsys.readouterr()

            # Should contain verbose markers
            assert "KEYWORD TAGGING" in captured.out
            assert "LLM Response:" in captured.out
            assert "firewall" in captured.out


class TestSaveImageIndex:
    """Test saving image index."""

    def test_save_image_index(self, tmp_path):
        """Test saving image index to file."""
        index_file = tmp_path / "test_index.json"
        test_data = {
            "msg1": {
                "metadata": {"subject": "Test"},
                "keywords": ["firewall"]
            }
        }

        save_image_index(test_data, str(index_file))

        # Verify file was written
        assert index_file.exists()

        # Verify content
        with open(index_file) as f:
            result = json.load(f)
        assert result == test_data

    def test_save_overwrites_existing_file(self, tmp_path):
        """Test that saving overwrites existing file without backup."""
        index_file = tmp_path / "test_index.json"
        original_data = {"msg1": {"metadata": {"subject": "Original"}}}
        new_data = {"msg1": {"metadata": {"subject": "New"}}}

        # Create original file
        index_file.write_text(json.dumps(original_data))

        # Save new data (no backup created since we write to new files in practice)
        save_image_index(new_data, str(index_file))

        # Check no backup exists
        backup_files = list(tmp_path.glob("test_index.json.backup.*"))
        assert len(backup_files) == 0

        # Check new data was written
        result = json.loads(index_file.read_text())
        assert result["msg1"]["metadata"]["subject"] == "New"
