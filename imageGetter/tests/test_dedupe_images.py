"""Tests for image deduplication."""

import pytest
import json
import tempfile
from pathlib import Path
from dedupe_images import (
    load_index,
    dedupe_message_images,
    save_index
)


class TestLoadIndex:
    """Test loading image index."""

    def test_load_index(self, tmp_path):
        """Test loading valid image index."""
        index_file = tmp_path / "test_index.json"
        test_data = {
            "msg1": {
                "metadata": {"subject": "Test message"},
                "images": []
            }
        }
        index_file.write_text(json.dumps(test_data))

        result = load_index(str(index_file))

        assert isinstance(result, dict)
        assert "msg1" in result


class TestDedupeMessageImages:
    """Test deduplicating images within a message."""

    def test_dedupe_by_file_size(self, tmp_path):
        """Test that images with same file size are deduped (keep first)."""
        # Create test files with same and different sizes
        img_dir = tmp_path / "images"
        img_dir.mkdir()

        # Create three files: two with same size (100 bytes), one different (50 bytes)
        img1 = img_dir / "img1.jpg"
        img2 = img_dir / "img2.jpg"  # Same size as img1
        img3 = img_dir / "img3.jpg"  # Different size

        img1.write_bytes(b"x" * 100)
        img2.write_bytes(b"y" * 100)  # Same size, different content
        img3.write_bytes(b"z" * 50)

        message = {
            "metadata": {"subject": "Test"},
            "images": [
                {"local_filename": "img1.jpg"},
                {"local_filename": "img2.jpg"},
                {"local_filename": "img3.jpg"}
            ]
        }

        result, stats = dedupe_message_images(message, str(img_dir))

        # Should keep img1 (first), remove img2 (duplicate size), keep img3 (different size)
        assert len(result["images"]) == 2
        assert result["images"][0]["local_filename"] == "img1.jpg"
        assert result["images"][1]["local_filename"] == "img3.jpg"
        assert stats["duplicates_removed"] == 1

    def test_remove_missing_images(self, tmp_path):
        """Test that images with missing files are removed."""
        img_dir = tmp_path / "images"
        img_dir.mkdir()

        # Create only one file
        img1 = img_dir / "img1.jpg"
        img1.write_bytes(b"x" * 100)

        message = {
            "metadata": {"subject": "Test"},
            "images": [
                {"local_filename": "img1.jpg"},
                {"local_filename": "img2.jpg"},  # Missing file
                {"local_filename": "img3.jpg"}   # Missing file
            ]
        }

        result, stats = dedupe_message_images(message, str(img_dir))

        # Should keep only img1 (exists)
        assert len(result["images"]) == 1
        assert result["images"][0]["local_filename"] == "img1.jpg"
        assert stats["missing_removed"] == 2

    def test_dedupe_and_remove_missing(self, tmp_path):
        """Test both deduping and removing missing files."""
        img_dir = tmp_path / "images"
        img_dir.mkdir()

        # Create files
        img1 = img_dir / "img1.jpg"
        img2 = img_dir / "img2.jpg"  # Same size as img1
        img3 = img_dir / "img3.jpg"  # Different size

        img1.write_bytes(b"x" * 100)
        img2.write_bytes(b"y" * 100)  # Same size as img1
        img3.write_bytes(b"z" * 50)

        message = {
            "metadata": {"subject": "Test"},
            "images": [
                {"local_filename": "img1.jpg"},
                {"local_filename": "img2.jpg"},  # Duplicate size
                {"local_filename": "img3.jpg"},
                {"local_filename": "img4.jpg"}   # Missing file
            ]
        }

        result, stats = dedupe_message_images(message, str(img_dir))

        # Should keep img1, remove img2 (duplicate), keep img3, remove img4 (missing)
        assert len(result["images"]) == 2
        assert result["images"][0]["local_filename"] == "img1.jpg"
        assert result["images"][1]["local_filename"] == "img3.jpg"
        assert stats["duplicates_removed"] == 1
        assert stats["missing_removed"] == 1

    def test_no_duplicates_or_missing(self, tmp_path):
        """Test that messages with unique sizes and existing files are unchanged."""
        img_dir = tmp_path / "images"
        img_dir.mkdir()

        img1 = img_dir / "img1.jpg"
        img2 = img_dir / "img2.jpg"

        img1.write_bytes(b"x" * 100)
        img2.write_bytes(b"y" * 50)

        message = {
            "metadata": {"subject": "Test"},
            "images": [
                {"local_filename": "img1.jpg"},
                {"local_filename": "img2.jpg"}
            ]
        }

        result, stats = dedupe_message_images(message, str(img_dir))

        assert len(result["images"]) == 2
        assert stats["duplicates_removed"] == 0
        assert stats["missing_removed"] == 0

    def test_empty_images_list(self, tmp_path):
        """Test that messages with no images are handled correctly."""
        img_dir = tmp_path / "images"
        img_dir.mkdir()

        message = {
            "metadata": {"subject": "Test"},
            "images": []
        }

        result, stats = dedupe_message_images(message, str(img_dir))

        assert len(result["images"]) == 0
        assert stats["duplicates_removed"] == 0
        assert stats["missing_removed"] == 0


class TestSaveIndex:
    """Test saving index."""

    def test_save_index(self, tmp_path):
        """Test saving index to file."""
        output_file = tmp_path / "output.json"
        test_data = {
            "msg1": {
                "metadata": {"subject": "Test"},
                "images": []
            }
        }

        save_index(test_data, str(output_file))

        # Verify file was written
        assert output_file.exists()

        # Verify content
        with open(output_file) as f:
            result = json.load(f)
        assert result == test_data
