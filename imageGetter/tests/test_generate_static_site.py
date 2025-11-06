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
        """Test counting how many images have each keyword (Phase 6: image-level scored keywords)."""
        index_data = {
            "MSG001": {
                "images": [
                    {"filename": "img1.jpg", "keywords": {"firewall": 100, "engine": 90}},
                    {"filename": "img2.jpg", "keywords": {"engine": 85}}
                ]
            },
            "MSG002": {
                "images": [
                    {"filename": "img3.jpg", "keywords": {"cowling": 120, "firewall": 75}}
                ]
            },
            "MSG003": {
                "images": [
                    {"filename": "img4.jpg", "keywords": {"engine": 110}}
                ]
            }
        }

        result = count_images_per_keyword(index_data)

        assert isinstance(result, dict)
        # firewall: img1 + img3 = 2 images
        assert result["firewall"] == 2
        # engine: img1 + img2 + img4 = 3 images
        assert result["engine"] == 3
        # cowling: img3 = 1 image
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


class TestSortMessagesByDate:
    """Tests for sorting messages chronologically."""

    def test_sort_messages_by_date_descending(self):
        """Test sorting messages by date, newest first."""
        from generate_static_site import sort_messages_by_date

        index_data = {
            "MSG001": {
                "metadata": {"date": "Jan 15, 2023"},
                "images": [{"filename": "img1.jpg"}]
            },
            "MSG002": {
                "metadata": {"date": "Dec 20, 2024"},
                "images": [{"filename": "img2.jpg"}]
            },
            "MSG003": {
                "metadata": {"date": "Mar 5, 2024"},
                "images": [{"filename": "img3.jpg"}]
            }
        }

        result = sort_messages_by_date(index_data)

        # Should be list of (message_id, message_data) tuples
        assert isinstance(result, list)
        assert len(result) == 3

        # Should be sorted newest first: 2024-12, 2024-03, 2023-01
        assert result[0][0] == "MSG002"  # Dec 2024
        assert result[1][0] == "MSG003"  # Mar 2024
        assert result[2][0] == "MSG001"  # Jan 2023


class TestGroupByYear:
    """Tests for grouping messages by year."""

    def test_group_by_year(self):
        """Test grouping messages into years with counts."""
        from generate_static_site import group_messages_by_year

        sorted_messages = [
            ("MSG002", {"metadata": {"date": "Dec 20, 2024"}, "images": [{"f": "i1"}, {"f": "i2"}]}),
            ("MSG003", {"metadata": {"date": "Mar 5, 2024"}, "images": [{"f": "i3"}]}),
            ("MSG001", {"metadata": {"date": "Jan 15, 2023"}, "images": [{"f": "i4"}, {"f": "i5"}, {"f": "i6"}]}),
        ]

        result = group_messages_by_year(sorted_messages)

        # Should be list of (year, image_count) tuples
        assert isinstance(result, list)
        assert len(result) == 2

        # Should be ordered newest first
        assert result[0] == (2024, 3)  # 2 images + 1 image = 3 total
        assert result[1] == (2023, 3)  # 3 images


class TestPaginateImages:
    """Tests for pagination."""

    def test_paginate_images(self):
        """Test paginating list of images."""
        from generate_static_site import paginate_images

        # Create 500 test images
        images = [{"filename": f"img{i}.jpg"} for i in range(500)]

        result = paginate_images(images, images_per_page=210)

        # Should return list of pages
        assert isinstance(result, list)
        # 500 images / 210 per page = 3 pages (210 + 210 + 80)
        assert len(result) == 3
        assert len(result[0]) == 210
        assert len(result[1]) == 210
        assert len(result[2]) == 80

    def test_paginate_images_single_page(self):
        """Test pagination with less than one page of images."""
        from generate_static_site import paginate_images

        images = [{"filename": f"img{i}.jpg"} for i in range(50)]

        result = paginate_images(images, images_per_page=210)

        assert len(result) == 1
        assert len(result[0]) == 50


@pytest.mark.skip(reason="Phase 6 TODO: Update for image-level scored keywords")
class TestGenerateAllImagesPage:
    """Tests for generating all images pages."""

    def test_generate_all_images_page(self, tmp_path):
        """Test generating a single all images page."""
        from generate_static_site import generate_all_images_page

        images = [
            {
                "message_id": "MSG001",
                "subject": "Test Subject 1",
                "keywords": ["firewall", "engine"],
                "thumbnail_path": "thumbs/img1_thumb.jpg",
                "full_path": "full/img1.jpg",
                "year": 2024
            },
            {
                "message_id": "MSG002",
                "subject": "Test Subject 2",
                "keywords": ["cowling"],
                "thumbnail_path": "thumbs/img2_thumb.jpg",
                "full_path": "full/img2.jpg",
                "year": 2024
            }
        ]

        output_file = tmp_path / "page1.html"
        generate_all_images_page(
            images=images,
            page_num=1,
            total_pages=1,
            output_file=str(output_file),
            year_groups=[(2024, 2)]
        )

        assert output_file.exists()
        content = output_file.read_text()

        # Should have image info
        assert "Test Subject 1" in content
        assert "MSG001" in content
        assert "firewall" in content

        # Should have pagination structure
        assert "First" in content
        assert "Previous" in content
        assert "Next" in content
        assert "Last" in content


class TestNavigationLinks:
    """Tests for first/prev/next/last navigation."""

    def test_first_prev_next_last_navigation(self, tmp_path):
        """Test that navigation links are correct for different pages."""
        from generate_static_site import generate_all_images_page

        images = [{"message_id": f"MSG{i}", "subject": f"Test {i}",
                   "keywords": [], "thumbnail_path": "", "full_path": "", "year": 2024}
                  for i in range(10)]

        # Test page 1 of 3 - Previous/First should be disabled
        output_file = tmp_path / "page1.html"
        generate_all_images_page(images, 1, 3, str(output_file), [(2024, 10)])
        content = output_file.read_text()

        # On page 1, links to next/last should be enabled
        assert "page2.html" in content  # Next
        assert "page3.html" in content  # Last

        # Test page 3 of 3 - Next/Last should be disabled
        output_file = tmp_path / "page3.html"
        generate_all_images_page(images, 3, 3, str(output_file), [(2024, 10)])
        content = output_file.read_text()

        # On page 3, links to first/prev should be enabled
        assert "page1.html" in content  # First
        assert "page2.html" in content  # Previous


@pytest.mark.skip(reason="Phase 6 TODO: Update for image-level scored keywords")
class TestFilterMessagesByKeyword:
    """Tests for filtering messages by keyword."""

    def test_filter_messages_by_keyword(self):
        """Test filtering messages that have a specific keyword."""
        from generate_static_site import filter_messages_by_keyword

        index_data = {
            "MSG001": {
                "keywords": ["firewall", "engine"],
                "images": [{"f": "i1"}]
            },
            "MSG002": {
                "keywords": ["cowling"],
                "images": [{"f": "i2"}]
            },
            "MSG003": {
                "keywords": ["firewall", "cowling"],
                "images": [{"f": "i3"}, {"f": "i4"}]
            },
            "MSG004": {
                "keywords": [],
                "images": [{"f": "i5"}]
            }
        }

        result = filter_messages_by_keyword(index_data, "firewall")

        # Should return messages that have "firewall" keyword
        assert len(result) == 2
        assert "MSG001" in result
        assert "MSG003" in result
        assert "MSG002" not in result
        assert "MSG004" not in result

    def test_filter_case_insensitive(self):
        """Test that keyword filtering is case-insensitive."""
        from generate_static_site import filter_messages_by_keyword

        index_data = {
            "MSG001": {"keywords": ["Firewall", "Engine"], "images": [{"f": "i1"}]},
            "MSG002": {"keywords": ["FIREWALL"], "images": [{"f": "i2"}]},
        }

        result = filter_messages_by_keyword(index_data, "firewall")
        assert len(result) == 2


class TestSafeKeywordFilenames:
    """Tests for sanitizing keyword names for filenames."""

    def test_safe_keyword_filenames(self):
        """Test converting keywords to safe filenames."""
        from generate_static_site import sanitize_keyword_for_filename

        assert sanitize_keyword_for_filename("firewall") == "firewall"
        assert sanitize_keyword_for_filename("landing gear") == "landing_gear"
        assert sanitize_keyword_for_filename("Oil-Cooler") == "oil_cooler"
        assert sanitize_keyword_for_filename("Co-Pilot") == "co_pilot"
        assert sanitize_keyword_for_filename("3/4 inch") == "3_4_inch"


@pytest.mark.skip(reason="Phase 6 TODO: Update for image-level scored keywords")
class TestGenerateKeywordPage:
    """Tests for generating keyword-specific pages."""

    def test_generate_keyword_page(self, tmp_path):
        """Test generating a keyword page."""
        from generate_static_site import generate_keyword_page

        images = [
            {
                "message_id": "MSG001",
                "subject": "Firewall test",
                "keywords": ["firewall", "engine"],
                "thumbnail_path": "thumbs/img1_thumb.jpg",
                "full_path": "full/img1.jpg",
                "year": 2024
            }
        ]

        output_file = tmp_path / "firewall_page1.html"
        generate_keyword_page(
            keyword="firewall",
            images=images,
            page_num=1,
            total_pages=1,
            output_file=str(output_file)
        )

        assert output_file.exists()
        content = output_file.read_text()

        # Should have breadcrumb back to index
        assert "index.html" in content or "Back to Index" in content

        # Should have keyword in title/heading
        assert "firewall" in content.lower()

        # Should have image info
        assert "MSG001" in content
        assert "Firewall test" in content

        # Should have pagination
        assert "First" in content
        assert "Previous" in content


@pytest.mark.skip(reason="Phase 6 TODO: Update for image-level scored keywords")
class TestKeywordPageNavigation:
    """Tests for keyword page navigation."""

    def test_keyword_page_navigation(self, tmp_path):
        """Test navigation links on keyword pages."""
        from generate_static_site import generate_keyword_page

        images = [{"message_id": f"MSG{i}", "subject": f"Test {i}",
                   "keywords": ["test"], "thumbnail_path": "", "full_path": "", "year": 2024}
                  for i in range(10)]

        # Test page 1 of 2
        output_file = tmp_path / "test_page1.html"
        generate_keyword_page("test", images, 1, 2, str(output_file))
        content = output_file.read_text()

        # Should have link to page 2
        assert "test_page2.html" in content

        # Test page 2 of 2
        output_file = tmp_path / "test_page2.html"
        generate_keyword_page("test", images, 2, 2, str(output_file))
        content = output_file.read_text()

        # Should have link to page 1
        assert "test_page1.html" in content
