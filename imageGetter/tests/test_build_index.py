# ABOUTME: Unit tests for building image index from directory of markdown files
# ABOUTME: Tests processing single files, directories, skipping files without images, and error handling

import pytest
from pathlib import Path

# Import function to test (will be implemented in GREEN phase)
# import sys
# sys.path.insert(0, str(Path(__file__).parent.parent))
# from extract_image_urls import build_image_index


# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestBuildImageIndex:
    """Tests for building image index from markdown files."""

    def test_process_single_markdown_file(self):
        """Should process a single markdown file and extract metadata + image URLs."""
        # Point to single file with 1 image
        strFilePath = str(FIXTURES_DIR / "A20JX9PGHII.md")

        # Build index
        # dctIndex = build_image_index(strFilePath)

        # Should have one entry keyed by message_id
        # assert "A20JX9PGHII" in dctIndex

        # Entry should have metadata and images
        # dctEntry = dctIndex["A20JX9PGHII"]
        # assert "metadata" in dctEntry
        # assert "images" in dctEntry

        # Metadata should match
        # assert dctEntry["metadata"]["message_id"] == "A20JX9PGHII"
        # assert dctEntry["metadata"]["subject"] == "WING LEADING EDGE MOLDS"
        # assert dctEntry["metadata"]["author"] == "ted davis"
        # assert dctEntry["metadata"]["date"] == "Feb 11, 2011"

        # Images should match (1 image)
        # assert len(dctEntry["images"]) == 1
        # assert dctEntry["images"][0]["part"] == "0.1"
        # assert dctEntry["images"][0]["filename"] == "image001.gif"

        # RED: This test should fail
        pytest.fail("Function build_image_index() not yet implemented")

    def test_process_directory_of_markdown_files(self):
        """Should process all markdown files in a directory."""
        # Point to fixtures directory with multiple files
        strDirPath = str(FIXTURES_DIR)

        # Build index
        # dctIndex = build_image_index(strDirPath)

        # Should process all .md files in directory
        # Should have entries for files with images
        # assert "A20JX9PGHII" in dctIndex  # 1 image
        # assert "a42YFDFx8WY" in dctIndex  # 8 images

        # Should NOT have entries for files without images
        # assert "A0OiG3usNBQ" not in dctIndex  # profile photos only
        # assert "A2ne3ed8CHE" not in dctIndex  # profile photo only

        # Check one entry in detail
        # dctEntry = dctIndex["a42YFDFx8WY"]
        # assert len(dctEntry["images"]) == 8
        # assert dctEntry["metadata"]["subject"] == "My just overhauled engine"

        # RED: This test should fail
        pytest.fail("Function build_image_index() not yet implemented")

    def test_skip_files_without_images(self):
        """Should skip markdown files that have no attachment images."""
        # Point to file with profile photos only (no attachments)
        strFilePath = str(FIXTURES_DIR / "A0OiG3usNBQ.md")

        # Build index
        # dctIndex = build_image_index(strFilePath)

        # Should be empty (no attachment images)
        # assert len(dctIndex) == 0

        # RED: This test should fail
        pytest.fail("Function build_image_index() not yet implemented")

    def test_handle_malformed_markdown(self):
        """Should handle markdown files with missing or partial metadata gracefully."""
        # Create test markdown with missing metadata
        strMarkdown = "# Some markdown\n\nNo metadata here.\n\nJust text."

        # Write to temp file
        from tempfile import NamedTemporaryFile
        import os

        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(strMarkdown)
            strTempPath = f.name

        try:
            # Build index
            # dctIndex = build_image_index(strTempPath)

            # Should not crash, should skip files without proper metadata
            # assert len(dctIndex) == 0
            pass
        finally:
            # Clean up
            os.unlink(strTempPath)

        # RED: This test should fail
        pytest.fail("Function build_image_index() not yet implemented")

    def test_returns_dict_ready_for_json(self):
        """Should return a dict structure ready to serialize as JSON."""
        # Point to file with images
        strFilePath = str(FIXTURES_DIR / "A20JX9PGHII.md")

        # Build index
        # dctIndex = build_image_index(strFilePath)

        # Should be JSON-serializable (test by converting to JSON)
        # import json
        # try:
        #     strJson = json.dumps(dctIndex)
        #     assert len(strJson) > 0
        # except (TypeError, ValueError) as e:
        #     pytest.fail(f"Index not JSON-serializable: {e}")

        # RED: This test should fail
        pytest.fail("Function build_image_index() not yet implemented")
