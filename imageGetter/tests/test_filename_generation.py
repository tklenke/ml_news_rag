# ABOUTME: Unit tests for generating standardized filenames for downloaded images
# ABOUTME: Tests message_id + part + original filename combination with space/dot replacement

import pytest
from pathlib import Path

# Import function to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from extract_image_urls import generate_filename


class TestFilenameGeneration:
    """Tests for generating standardized local filenames."""

    def test_generate_filename_basic(self):
        """Should generate filename with message_id, part, and original filename."""
        strMessageId = "A20JX9PGHII"
        strUrl = "https://groups.google.com/group/cozy_builders/attach/b7b89755afd4fbca/image001.gif?part=0.1"
        strPart = "0.1"
        strOriginalFilename = "image001.gif"

        # Generate filename
        strFilename = generate_filename(strMessageId, strUrl, strPart)

        # Should be: message_id + part + filename
        assert strFilename == "A20JX9PGHII_part0_1_image001.gif"

    def test_replace_spaces_with_underscores(self):
        """Should replace spaces in filename with underscores."""
        strMessageId = "ABC123"
        strUrl = "https://groups.google.com/group/cozy_builders/attach/hash/p-lead wiring.gif?part=0.1"
        strPart = "0.1"
        strOriginalFilename = "p-lead wiring.gif"

        # Generate filename
        strFilename = generate_filename(strMessageId, strUrl, strPart)

        # Spaces should be replaced with underscores
        assert strFilename == "ABC123_part0_1_p-lead_wiring.gif"

    def test_replace_dots_in_part_number(self):
        """Should replace dots in part number with underscores."""
        strMessageId = "XYZ789"
        strUrl = "https://groups.google.com/group/cozy_builders/attach/hash/image.jpg?part=0.2"
        strPart = "0.2"
        strOriginalFilename = "image.jpg"

        # Generate filename
        strFilename = generate_filename(strMessageId, strUrl, strPart)

        # Part number dot should be replaced
        assert strFilename == "XYZ789_part0_2_image.jpg"

    def test_preserve_file_extension(self):
        """Should preserve the file extension correctly."""
        strMessageId = "TEST123"
        strUrl = "https://groups.google.com/group/cozy_builders/attach/hash/Photo.JPEG?part=0.1"
        strPart = "0.1"
        strOriginalFilename = "Photo.JPEG"

        # Generate filename
        strFilename = generate_filename(strMessageId, strUrl, strPart)

        # Extension should be preserved (case-sensitive)
        assert strFilename == "TEST123_part0_1_Photo.JPEG"

    def test_handle_multiple_spaces(self):
        """Should handle multiple consecutive spaces."""
        strMessageId = "ABC"
        strUrl = "https://groups.google.com/group/cozy_builders/attach/hash/Screenshot 2025-06-15 145512.png?part=0.1"
        strPart = "0.1"
        strOriginalFilename = "Screenshot 2025-06-15 145512.png"

        # Generate filename
        strFilename = generate_filename(strMessageId, strUrl, strPart)

        # All spaces replaced
        assert strFilename == "ABC_part0_1_Screenshot_2025-06-15_145512.png"

    def test_handle_filename_from_url(self):
        """Should extract filename from URL when passed separately."""
        strMessageId = "a42YFDFx8WY"
        strUrl = "https://groups.google.com/group/cozy_builders/attach/7d6ac224e41ae/Image.jpeg?part=0.1&view=1"
        strPart = "0.1"
        strOriginalFilename = "Image.jpeg"

        # Generate filename
        strFilename = generate_filename(strMessageId, strUrl, strPart)

        # Should work with query parameters in URL
        assert strFilename == "a42YFDFx8WY_part0_1_Image.jpeg"

    def test_handle_lowercase_message_id(self):
        """Should preserve case of message_id."""
        strMessageId = "a42YFDFx8WY"  # lowercase 'a'
        strUrl = "https://groups.google.com/group/cozy_builders/attach/hash/test.jpg?part=0.3"
        strPart = "0.3"
        strOriginalFilename = "test.jpg"

        # Generate filename
        strFilename = generate_filename(strMessageId, strUrl, strPart)

        # Case should be preserved
        assert strFilename == "a42YFDFx8WY_part0_3_test.jpg"
