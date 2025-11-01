# ABOUTME: Unit tests for URL extraction from markdown files
# ABOUTME: Tests filtering logic to include only attachment images, exclude profile photos and logos

import pytest
import json
from pathlib import Path

# Import function to test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from extract_image_urls import extract_image_urls


# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(strFilename):
    """Load a test fixture markdown file."""
    strPath = FIXTURES_DIR / strFilename
    with open(strPath, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def load_expected(strFilename):
    """Load expected JSON output for a fixture."""
    strPath = FIXTURES_DIR / strFilename
    with open(strPath, 'r', encoding='utf-8') as f:
        return json.load(f)


class TestExtractAttachmentUrls:
    """Tests for extracting attachment URLs from markdown."""

    def test_extract_attachment_urls_from_markdown(self):
        """Should extract attachment image URLs from markdown content."""
        # Load fixture with multiple images
        strMarkdown = load_fixture("a42YFDFx8WY.md")
        lstExpected = load_expected("a42YFDFx8WY_expected.json")

        # Extract URLs
        lstResult = extract_image_urls(strMarkdown)

        # Should find 8 attachment images
        assert len(lstResult) == 8
        assert lstResult == lstExpected

    def test_exclude_profile_photos(self):
        """Should exclude profile photos from googleusercontent.com."""
        # Load fixture with only profile photos
        strMarkdown = load_fixture("A0OiG3usNBQ.md")
        lstExpected = load_expected("A0OiG3usNBQ_expected.json")

        # Extract URLs
        lstResult = extract_image_urls(strMarkdown)

        # Should find 0 images (all are profile photos)
        assert len(lstResult) == 0
        assert lstResult == lstExpected

    def test_exclude_logos_and_emojis(self):
        """Should exclude logos, tracking pixels, and UI elements."""
        # Profile photo markdown has tracking pixels and logos
        strMarkdown = load_fixture("A2ne3ed8CHE.md")
        lstExpected = load_expected("A2ne3ed8CHE_expected.json")

        # Extract URLs
        lstResult = extract_image_urls(strMarkdown)

        # Should find 0 images
        assert len(lstResult) == 0
        assert lstResult == lstExpected

    def test_extract_from_multiple_images(self):
        """Should handle markdown with multiple attachment images."""
        # Load fixture with 8 images
        strMarkdown = load_fixture("a42YFDFx8WY.md")

        # Extract URLs
        lstResult = extract_image_urls(strMarkdown)

        # Should find all 8 images
        assert len(lstResult) == 8

        # Each should have url, part, and filename fields
        for dctImg in lstResult:
            assert "url" in dctImg
            assert "part" in dctImg
            assert "filename" in dctImg
            assert dctImg["url"].startswith("https://groups.google.com/group/cozy_builders/attach/")

    def test_handle_markdown_with_no_images(self):
        """Should return empty list for markdown with no attachment images."""
        # Load fixture with no images
        strMarkdown = load_fixture("A2ne3ed8CHE.md")

        # Extract URLs
        lstResult = extract_image_urls(strMarkdown)

        # Should find 0 images
        assert lstResult == []

    def test_extract_single_image(self):
        """Should handle markdown with single attachment image."""
        # Load fixture with 1 image
        strMarkdown = load_fixture("A20JX9PGHII.md")
        lstExpected = load_expected("A20JX9PGHII_expected.json")

        # Extract URLs
        lstResult = extract_image_urls(strMarkdown)

        # Should find 1 image
        assert len(lstResult) == 1
        assert lstResult == lstExpected


class TestUrlParsing:
    """Tests for parsing URL components - covered by integration tests above."""

    @pytest.mark.skip(reason="Covered by integration tests")
    def test_extract_part_number(self):
        """Part number extraction is tested in main extraction tests."""
        pass

    @pytest.mark.skip(reason="Covered by integration tests")
    def test_extract_filename(self):
        """Filename extraction is tested in main extraction tests."""
        pass

    @pytest.mark.skip(reason="Covered by integration tests")
    def test_handle_url_with_ampersand_view(self):
        """URL parameter handling is tested in main extraction tests."""
        pass
