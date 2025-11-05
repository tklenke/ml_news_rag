#!/usr/bin/env python3
"""Tests for generate_static_site module."""

import pytest
import json
import tempfile
from pathlib import Path
from generate_static_site import (
    load_index_data,
    count_images_per_keyword,
    sort_keywords_alphabetically,
    generate_index_html,
)


class TestLoadIndexData:
    """Tests for loading image index data."""

    def test_load_index_data(self, tmp_path):
        """Test loading image index from JSON file."""
        # Create test index file
        index_file = tmp_path / "test_index.json"
        test_data = {
            "MSG001": {
                "metadata": {"subject": "Test 1"},
                "images": [{"filename": "img1.jpg"}],
                "keywords": ["firewall", "engine"]
            },
            "MSG002": {
                "metadata": {"subject": "Test 2"},
                "images": [{"filename": "img2.jpg"}],
                "keywords": ["cowling"]
            }
        }
        with open(index_file, 'w') as f:
            json.dump(test_data, f)

        # Load and verify
        result = load_index_data(str(index_file))
        assert isinstance(result, dict)
        assert len(result) == 2
        assert "MSG001" in result
        assert "MSG002" in result
        assert result["MSG001"]["keywords"] == ["firewall", "engine"]


class TestCountImagesPerKeyword:
    """Tests for counting images per keyword."""

    def test_count_images_per_keyword(self):
        """Test counting how many images have each keyword."""
        index_data = {
            "MSG001": {
                "images": [{"filename": "img1.jpg"}, {"filename": "img2.jpg"}],
                "keywords": ["firewall", "engine"]
            },
            "MSG002": {
                "images": [{"filename": "img3.jpg"}],
                "keywords": ["cowling", "firewall"]
            },
            "MSG003": {
                "images": [{"filename": "img4.jpg"}],
                "keywords": ["engine"]
            }
        }

        result = count_images_per_keyword(index_data)

        assert isinstance(result, dict)
        # firewall: 2 images from MSG001 + 1 from MSG002 = 3
        assert result["firewall"] == 3
        # engine: 2 images from MSG001 + 1 from MSG003 = 3
        assert result["engine"] == 3
        # cowling: 1 image from MSG002 = 1
        assert result["cowling"] == 1

    def test_count_with_no_keywords(self):
        """Test counting when messages have no keywords."""
        index_data = {
            "MSG001": {
                "images": [{"filename": "img1.jpg"}],
                "keywords": []
            },
            "MSG002": {
                "images": [{"filename": "img2.jpg"}]
                # No keywords field
            }
        }

        result = count_images_per_keyword(index_data)
        assert isinstance(result, dict)
        assert len(result) == 0


class TestSortKeywordsAlphabetically:
    """Tests for sorting keywords alphabetically."""

    def test_alphabetical_keyword_sort(self):
        """Test sorting keywords in alphabetical order."""
        keyword_counts = {
            "zebra": 5,
            "apple": 10,
            "monkey": 3,
            "banana": 7
        }

        result = sort_keywords_alphabetically(keyword_counts)

        assert isinstance(result, list)
        assert len(result) == 4
        # Should be sorted alphabetically
        assert result[0] == ("apple", 10)
        assert result[1] == ("banana", 7)
        assert result[2] == ("monkey", 3)
        assert result[3] == ("zebra", 5)

    def test_empty_keyword_dict(self):
        """Test sorting empty keyword dictionary."""
        result = sort_keywords_alphabetically({})
        assert isinstance(result, list)
        assert len(result) == 0


class TestGenerateIndexHTML:
    """Tests for generating index.html."""

    def test_generate_index_html(self, tmp_path):
        """Test generating index.html with keyword list."""
        keyword_counts = [
            ("firewall", 127),
            ("cowling", 45),
            ("aileron", 23)
        ]
        output_file = tmp_path / "index.html"

        generate_index_html(keyword_counts, str(output_file))

        # Verify file was created
        assert output_file.exists()

        # Read and verify content
        content = output_file.read_text()

        # Should have link to "All Images"
        assert "All Images" in content
        assert "all/page1.html" in content

        # Should have keyword links with counts
        assert "firewall" in content
        assert "127" in content
        assert "keywords/firewall_page1.html" in content

        assert "cowling" in content
        assert "45" in content

        assert "aileron" in content
        assert "23" in content

        # Should have basic HTML structure
        assert "<html" in content
        assert "</html>" in content
        assert "<head>" in content
        assert "<body>" in content

    def test_generate_index_html_empty_keywords(self, tmp_path):
        """Test generating index.html with no keywords."""
        output_file = tmp_path / "index.html"

        generate_index_html([], str(output_file))

        assert output_file.exists()
        content = output_file.read_text()

        # Should still have link to all images
        assert "All Images" in content
        assert "all/page1.html" in content
