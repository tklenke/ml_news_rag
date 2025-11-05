# ABOUTME: Unit tests for keyword extraction from image filenames
# ABOUTME: Tests filtering logic to extract meaningful keywords and filter invalid ones

import pytest
import sys
from pathlib import Path

# Import function to test
sys.path.insert(0, str(Path(__file__).parent.parent))
from extract_image_urls import extract_keywords_from_filename


class TestExtractKeywordsFromFilename:
    """Tests for extracting keywords from image filenames."""

    def test_basic_keyword_extraction(self):
        """Should extract basic keywords from filename."""
        result = extract_keywords_from_filename("landing_gear_assembly.jpg")
        assert result == ["landing", "gear", "assembly"]

    def test_camel_case_splitting(self):
        """Should split camelCase filenames."""
        result = extract_keywords_from_filename("FuelTankInstall.jpg")
        assert "fuel" in result
        assert "tank" in result
        assert "install" in result

    def test_filter_stopwords(self):
        """Should filter out generic stopwords."""
        result = extract_keywords_from_filename("the_image_of_landing_gear.jpg")
        assert "the" not in result
        assert "image" not in result
        assert "of" not in result
        assert "landing" in result
        assert "gear" in result

    def test_filter_invalid_keywords(self):
        """Should filter out invalid keywords from INVALID_KEYWORDS list."""
        # "cozy" should be filtered out
        result = extract_keywords_from_filename("Cozy_Builder_Firewall.jpg")
        assert "cozy" not in result
        assert "builder" in result
        assert "firewall" in result

    def test_filter_invalid_keywords_case_insensitive(self):
        """Should filter invalid keywords regardless of case."""
        # Test various cases of "cozy"
        result1 = extract_keywords_from_filename("cozy_firewall.jpg")
        result2 = extract_keywords_from_filename("Cozy_firewall.jpg")
        result3 = extract_keywords_from_filename("COZY_firewall.jpg")

        assert "cozy" not in result1
        assert "cozy" not in result2
        assert "cozy" not in result3

        # All should have firewall
        assert "firewall" in result1
        assert "firewall" in result2
        assert "firewall" in result3
