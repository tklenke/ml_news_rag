"""Tests for removing images from index based on removal lists."""

import pytest
import json
import tempfile
from pathlib import Path
from remove_images import (
    load_index,
    load_removal_lists,
    remove_images_from_index,
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
                "images": [
                    {"local_filename": "img1.jpg"},
                    {"local_filename": "img2.jpg"}
                ]
            }
        }
        index_file.write_text(json.dumps(test_data))

        result = load_index(str(index_file))

        assert isinstance(result, dict)
        assert "msg1" in result
        assert len(result["msg1"]["images"]) == 2


class TestLoadRemovalLists:
    """Test loading removal list files."""

    def test_load_single_file(self, tmp_path):
        """Test loading a single removal list file."""
        removal_file = tmp_path / "remove.txt"
        removal_file.write_text("img1.jpg\nimg2.jpg\nimg3.jpg\n")

        result = load_removal_lists([str(removal_file)])

        assert len(result) == 3
        assert "img1.jpg" in result
        assert "img2.jpg" in result
        assert "img3.jpg" in result

    def test_load_multiple_files(self, tmp_path):
        """Test loading multiple removal list files."""
        file1 = tmp_path / "remove1.txt"
        file2 = tmp_path / "remove2.txt"
        file1.write_text("img1.jpg\nimg2.jpg\n")
        file2.write_text("img3.jpg\nimg4.jpg\n")

        result = load_removal_lists([str(file1), str(file2)])

        assert len(result) == 4
        assert all(f"img{i}.jpg" in result for i in range(1, 5))

    def test_deduplicate_across_files(self, tmp_path):
        """Test that duplicates across files are handled."""
        file1 = tmp_path / "remove1.txt"
        file2 = tmp_path / "remove2.txt"
        file1.write_text("img1.jpg\nimg2.jpg\n")
        file2.write_text("img2.jpg\nimg3.jpg\n")  # img2.jpg appears in both

        result = load_removal_lists([str(file1), str(file2)])

        assert len(result) == 3  # img1, img2, img3 (no duplicates)
        assert "img2.jpg" in result

    def test_skip_empty_lines(self, tmp_path):
        """Test that empty lines are skipped."""
        removal_file = tmp_path / "remove.txt"
        removal_file.write_text("img1.jpg\n\nimg2.jpg\n\n")

        result = load_removal_lists([str(removal_file)])

        assert len(result) == 2
        assert "img1.jpg" in result
        assert "img2.jpg" in result

    def test_strip_whitespace(self, tmp_path):
        """Test that whitespace is stripped from filenames."""
        removal_file = tmp_path / "remove.txt"
        removal_file.write_text("  img1.jpg  \nimg2.jpg\n")

        result = load_removal_lists([str(removal_file)])

        assert "img1.jpg" in result
        assert "  img1.jpg  " not in result


class TestRemoveImagesFromIndex:
    """Test removing images from index."""

    def test_remove_images_from_messages(self, tmp_path):
        """Test removing specific images from messages."""
        index_data = {
            "msg1": {
                "metadata": {"subject": "Test"},
                "images": [
                    {"local_filename": "img1.jpg"},
                    {"local_filename": "img2.jpg"},
                    {"local_filename": "img3.jpg"}
                ]
            },
            "msg2": {
                "metadata": {"subject": "Test 2"},
                "images": [
                    {"local_filename": "img4.jpg"},
                    {"local_filename": "img5.jpg"}
                ]
            }
        }
        removal_set = {"img2.jpg", "img5.jpg"}

        result, stats = remove_images_from_index(index_data, removal_set)

        # Check msg1 - img2 removed
        assert len(result["msg1"]["images"]) == 2
        assert result["msg1"]["images"][0]["local_filename"] == "img1.jpg"
        assert result["msg1"]["images"][1]["local_filename"] == "img3.jpg"

        # Check msg2 - img5 removed
        assert len(result["msg2"]["images"]) == 1
        assert result["msg2"]["images"][0]["local_filename"] == "img4.jpg"

        # Check stats
        assert stats["images_removed"] == 2
        assert stats["messages_affected"] == 2

    def test_no_images_to_remove(self, tmp_path):
        """Test when no images match the removal list."""
        index_data = {
            "msg1": {
                "metadata": {"subject": "Test"},
                "images": [
                    {"local_filename": "img1.jpg"},
                    {"local_filename": "img2.jpg"}
                ]
            }
        }
        removal_set = {"img99.jpg"}  # Doesn't exist

        result, stats = remove_images_from_index(index_data, removal_set)

        # Nothing should be removed
        assert len(result["msg1"]["images"]) == 2
        assert stats["images_removed"] == 0
        assert stats["messages_affected"] == 0

    def test_remove_all_images_from_message(self, tmp_path):
        """Test removing all images from a message."""
        index_data = {
            "msg1": {
                "metadata": {"subject": "Test"},
                "images": [
                    {"local_filename": "img1.jpg"},
                    {"local_filename": "img2.jpg"}
                ]
            }
        }
        removal_set = {"img1.jpg", "img2.jpg"}

        result, stats = remove_images_from_index(index_data, removal_set)

        # All images removed, but message still exists with empty list
        assert "msg1" in result
        assert len(result["msg1"]["images"]) == 0
        assert stats["images_removed"] == 2
        assert stats["messages_affected"] == 1

    def test_preserve_other_image_fields(self, tmp_path):
        """Test that other fields in image objects are preserved."""
        index_data = {
            "msg1": {
                "metadata": {"subject": "Test"},
                "images": [
                    {"local_filename": "img1.jpg", "keywords": ["test"], "url": "http://example.com"},
                    {"local_filename": "img2.jpg", "keywords": ["demo"]}
                ]
            }
        }
        removal_set = {"img2.jpg"}

        result, stats = remove_images_from_index(index_data, removal_set)

        # img1 should be preserved with all its fields
        assert len(result["msg1"]["images"]) == 1
        assert result["msg1"]["images"][0]["local_filename"] == "img1.jpg"
        assert result["msg1"]["images"][0]["keywords"] == ["test"]
        assert result["msg1"]["images"][0]["url"] == "http://example.com"

    def test_preserve_message_metadata(self, tmp_path):
        """Test that message metadata is preserved."""
        index_data = {
            "msg1": {
                "metadata": {"subject": "Test", "author": "John"},
                "llm_keywords": ["aircraft"],
                "images": [
                    {"local_filename": "img1.jpg"},
                    {"local_filename": "img2.jpg"}
                ]
            }
        }
        removal_set = {"img2.jpg"}

        result, stats = remove_images_from_index(index_data, removal_set)

        # Metadata should be unchanged
        assert result["msg1"]["metadata"]["subject"] == "Test"
        assert result["msg1"]["metadata"]["author"] == "John"
        assert result["msg1"]["llm_keywords"] == ["aircraft"]


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
