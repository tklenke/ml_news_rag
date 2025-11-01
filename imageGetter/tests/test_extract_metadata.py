# ABOUTME: Unit tests for message metadata extraction from markdown files
# ABOUTME: Tests extraction of message ID, subject, author, and date from Google Groups markdown

import pytest
from pathlib import Path

# Import function to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from extract_image_urls import extract_message_metadata


# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(strFilename):
    """Load a test fixture markdown file."""
    strPath = FIXTURES_DIR / strFilename
    with open(strPath, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


class TestExtractMessageMetadata:
    """Tests for extracting message metadata from markdown."""

    def test_extract_message_id(self):
        """Should extract message ID from first line."""
        strMarkdown = load_fixture("A20JX9PGHII.md")

        # Extract metadata
        dctMetadata = extract_message_metadata(strMarkdown)

        # Should extract message ID
        assert dctMetadata["message_id"] == "A20JX9PGHII"

    def test_extract_subject(self):
        """Should extract subject from markdown heading."""
        strMarkdown = load_fixture("A20JX9PGHII.md")

        # Extract metadata
        dctMetadata = extract_message_metadata(strMarkdown)

        # Should extract subject
        assert dctMetadata["subject"] == "WING LEADING EDGE MOLDS"

    def test_extract_author(self):
        """Should extract author name from markdown."""
        strMarkdown = load_fixture("A20JX9PGHII.md")

        # Extract metadata
        dctMetadata = extract_message_metadata(strMarkdown)

        # Should extract author
        assert dctMetadata["author"] == "ted davis"

    def test_extract_date(self):
        """Should extract date from markdown."""
        strMarkdown = load_fixture("A20JX9PGHII.md")

        # Extract metadata
        dctMetadata = extract_message_metadata(strMarkdown)

        # Should extract date (first date occurrence)
        assert dctMetadata["date"] == "Feb 11, 2011"

    def test_extract_all_metadata(self):
        """Should extract all metadata fields from markdown."""
        strMarkdown = load_fixture("a42YFDFx8WY.md")

        # Extract metadata
        dctMetadata = extract_message_metadata(strMarkdown)

        # Should have all fields
        assert "message_id" in dctMetadata
        assert "subject" in dctMetadata
        assert "author" in dctMetadata
        assert "date" in dctMetadata

        # Check values
        assert dctMetadata["message_id"] == "a42YFDFx8WY"
        assert dctMetadata["subject"] == "My just overhauled engine"
        assert dctMetadata["author"] == "agustin millan"
        assert dctMetadata["date"] == "Mar 30, 2020"

    def test_handle_missing_metadata(self):
        """Should handle markdown with missing metadata gracefully."""
        strMarkdown = "# Some random markdown\n\nNo metadata here."

        # Extract metadata
        dctMetadata = extract_message_metadata(strMarkdown)

        # Should return empty or default values
        assert dctMetadata["message_id"] == ""
        assert dctMetadata["subject"] == "Some random markdown"  # Still extracts heading
        assert dctMetadata["author"] == ""
        assert dctMetadata["date"] == ""

    def test_extract_lowercase_message_id(self):
        """Should handle message IDs that start with lowercase."""
        strMarkdown = load_fixture("a42YFDFx8WY.md")

        # Extract metadata
        dctMetadata = extract_message_metadata(strMarkdown)

        # Should preserve case
        assert dctMetadata["message_id"] == "a42YFDFx8WY"
