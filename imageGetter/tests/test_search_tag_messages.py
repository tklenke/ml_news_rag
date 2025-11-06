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


class TestImageLevelScoring:
    """Test image-level keyword scoring (Phase 6)."""

    @pytest.fixture
    def test_index_with_images(self, tmp_path):
        """Create test index with images."""
        index_file = tmp_path / "test_index.json"
        test_data = {
            "MSG001": {
                "metadata": {
                    "subject": "Firewall and wing build",
                    "message_id": "MSG001",
                    "message_md": "M/MSG001.md"
                },
                "images": [
                    {
                        "url": "https://example.com/img1.jpg",
                        "part": "0.1",
                        "filename": "firewall.jpg",
                        "local_filename": "MSG001_part0_1_firewall.jpg"
                    },
                    {
                        "url": "https://example.com/img2.jpg",
                        "part": "0.2",
                        "filename": "wing.jpg",
                        "local_filename": "MSG001_part0_2_wing.jpg"
                    }
                ]
            }
        }
        index_file.write_text(json.dumps(test_data))

        # Create mock markdown file
        msgs_md_dir = tmp_path / "msgs_md" / "M"
        msgs_md_dir.mkdir(parents=True)
        md_file = msgs_md_dir / "MSG001.md"
        md_content = """# Firewall and wing build

Here's my firewall installation.
https://example.com/img1.jpg

And here's the wing spar layup.
https://example.com/img2.jpg
"""
        md_file.write_text(md_content)

        return str(index_file), str(tmp_path / "msgs_md")

    @pytest.fixture
    def test_keywords_scoring(self, tmp_path):
        """Create test keywords file."""
        kw_file = tmp_path / "keywords.txt"
        kw_file.write_text("firewall\nwing\nspar\ninstall\nlayup\n")
        return str(kw_file)

    def test_image_level_scoring(self, test_index_with_images, test_keywords_scoring):
        """Test that each image gets its own scored keywords."""
        index_file, msgs_md_dir = test_index_with_images

        # Tag with image-level scoring
        stats = tag_messages(index_file, test_keywords_scoring, msgs_md_dir=msgs_md_dir)

        # Load result
        with open(index_file) as f:
            result = json.load(f)

        msg = result["MSG001"]

        # Verify image 1 has keywords (dict format)
        assert "keywords" in msg["images"][0]
        assert isinstance(msg["images"][0]["keywords"], dict)
        assert len(msg["images"][0]["keywords"]) > 0

        # Verify image 2 has keywords (dict format)
        assert "keywords" in msg["images"][1]
        assert isinstance(msg["images"][1]["keywords"], dict)
        assert len(msg["images"][1]["keywords"]) > 0

    def test_keywords_are_dict_with_scores(self, test_index_with_images, test_keywords_scoring):
        """Test that keywords are stored as {keyword: score} dict."""
        index_file, msgs_md_dir = test_index_with_images

        stats = tag_messages(index_file, test_keywords_scoring, msgs_md_dir=msgs_md_dir)

        with open(index_file) as f:
            result = json.load(f)

        image = result["MSG001"]["images"][0]
        assert isinstance(image["keywords"], dict)
        assert len(image["keywords"]) > 0

        # Check format: {keyword: score}
        for kw, score in image["keywords"].items():
            assert isinstance(kw, str)
            assert isinstance(score, int)
            assert score > 0

    def test_message_level_keywords_removed(self, test_index_with_images, test_keywords_scoring):
        """Test that message-level keywords field is removed."""
        index_file, msgs_md_dir = test_index_with_images

        # Add old-style message-level keywords
        with open(index_file) as f:
            data = json.load(f)
        data["MSG001"]["keywords"] = ["old", "keywords"]
        with open(index_file, 'w') as f:
            json.dump(data, f)

        # Tag messages
        stats = tag_messages(index_file, test_keywords_scoring, msgs_md_dir=msgs_md_dir)

        with open(index_file) as f:
            result = json.load(f)

        # Message-level keywords should be removed
        assert "keywords" not in result["MSG001"]

    def test_all_scores_positive(self, test_index_with_images, test_keywords_scoring):
        """Test that all keyword scores are positive (dict format)."""
        index_file, msgs_md_dir = test_index_with_images

        stats = tag_messages(index_file, test_keywords_scoring, msgs_md_dir=msgs_md_dir)

        with open(index_file) as f:
            result = json.load(f)

        keywords = result["MSG001"]["images"][0]["keywords"]

        # All scores should be positive
        assert all(score > 0 for score in keywords.values())

    def test_proximity_affects_scoring(self, test_index_with_images, test_keywords_scoring):
        """Test that keywords near image URL score higher."""
        index_file, msgs_md_dir = test_index_with_images

        stats = tag_messages(index_file, test_keywords_scoring, msgs_md_dir=msgs_md_dir)

        with open(index_file) as f:
            result = json.load(f)

        # Image 1: "install" should be near it (not in subject)
        img1_kw = dict(result["MSG001"]["images"][0]["keywords"])

        # Image 2: "spar" and "layup" should be near it (not in subject)
        img2_kw = dict(result["MSG001"]["images"][1]["keywords"])

        # Both images should have non-zero scores for their nearby keywords
        assert "install" in img1_kw
        assert img1_kw["install"] > 0

        assert "spar" in img2_kw
        assert img2_kw["spar"] > 0

        assert "layup" in img2_kw
        assert img2_kw["layup"] > 0
