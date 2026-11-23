# ABOUTME: Unit tests for making the index the gallery reads from the full index and the decisions
# ABOUTME: Tests removed contents, missing files, a content twice in a thread, empty threads and the counts

import pytest
from pathlib import Path

# Import function to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from gallery_index import build_gallery_index


def image(strName, strHash, intBytes=5000):
    return {"url": f"https://example.com/{strName}", "part": "0.1", "filename": strName,
            "keywords": [], "local_filename": strName, "content_hash": strHash,
            "size_bytes": intBytes, "width": 640, "height": 480}


def make_index():
    return {
        "THREADaaaaa": {"metadata": {"message_id": "THREADaaaaa", "date": "Jan 1, 2015"},
                        "images": [image("a_photo.jpg", "photo"),
                                   image("a_tiny.gif", "tiny", intBytes=500),
                                   image("a_poster.jpg", "poster"),
                                   image("a_photo_again.jpg", "photo"),
                                   {"url": "https://example.com/a_gone.jpg", "part": "0.2",
                                    "filename": "gone.jpg", "keywords": [],
                                    "local_filename": "a_gone.jpg"}]},
        "THREADbbbbb": {"metadata": {"message_id": "THREADbbbbb", "date": "Feb 1, 2015"},
                        "images": [image("b_poster.jpg", "poster"), image("b_photo.jpg", "photo")]},
        "THREADccccc": {"metadata": {"message_id": "THREADccccc", "date": "Mar 1, 2015"},
                        "images": [image("c_poster.jpg", "poster")]},
    }


@pytest.fixture
def full_dir(tmp_path):
    for strName in ("a_photo.jpg", "a_tiny.gif", "a_poster.jpg", "a_photo_again.jpg",
                    "b_poster.jpg", "b_photo.jpg", "c_poster.jpg"):
        (tmp_path / strName).write_bytes(b"x")
    return str(tmp_path)


DECISIONS = {"photo": "keep", "tiny": "keep", "poster": "remove"}


def names(dctGallery, strThread):
    return [dctImage["local_filename"] for dctImage in dctGallery[strThread]["images"]]


class TestBuildGalleryIndex:
    """Tests for the index the gallery reads."""

    def test_removed_content_dropped_and_kept_file_under_1000_bytes_stays(self, full_dir):
        dctGallery, _ = build_gallery_index(make_index(), DECISIONS, full_dir)

        assert names(dctGallery, "THREADaaaaa") == ["a_photo.jpg", "a_tiny.gif"]

    def test_content_listed_once_per_thread_and_in_each_of_its_threads(self, full_dir):
        dctGallery, _ = build_gallery_index(make_index(), DECISIONS, full_dir)

        assert names(dctGallery, "THREADaaaaa").count("a_photo.jpg") == 1
        assert "a_photo_again.jpg" not in names(dctGallery, "THREADaaaaa")
        assert names(dctGallery, "THREADbbbbb") == ["b_photo.jpg"]

    def test_thread_left_with_no_picture_is_not_in_it(self, full_dir):
        dctGallery, _ = build_gallery_index(make_index(), DECISIONS, full_dir)

        assert set(dctGallery) == {"THREADaaaaa", "THREADbbbbb"}

    def test_entry_whose_file_is_missing_dropped(self, full_dir):
        dctGallery, _ = build_gallery_index(make_index(), DECISIONS, full_dir)

        assert "a_gone.jpg" not in names(dctGallery, "THREADaaaaa")

    def test_metadata_and_image_fields_carried_over(self, full_dir):
        dctIndex = make_index()

        dctGallery, _ = build_gallery_index(dctIndex, DECISIONS, full_dir)

        assert dctGallery["THREADbbbbb"]["metadata"] == dctIndex["THREADbbbbb"]["metadata"]
        assert dctGallery["THREADbbbbb"]["images"][0] == {**dctIndex["THREADbbbbb"]["images"][1],
                                                          "thumbnail_filename": "b_photo_thumb.jpg"}

    def test_each_picture_names_its_thumbnail(self, full_dir):
        dctIndex = make_index()
        dctIndex["THREADbbbbb"]["images"].append(image("b_two.dots.png", "dots"))
        (Path(full_dir) / "b_two.dots.png").write_bytes(b"x")

        dctGallery, _ = build_gallery_index(dctIndex, DECISIONS, full_dir)

        assert [dctImage["thumbnail_filename"] for dctImage in dctGallery["THREADbbbbb"]["images"]] \
            == ["b_photo_thumb.jpg", "b_two.dots_thumb.jpg"]
        assert [dctImage["thumbnail_filename"] for dctImage in dctGallery["THREADaaaaa"]["images"]] \
            == ["a_photo_thumb.jpg", "a_tiny_thumb.jpg"]

    def test_full_index_is_not_changed(self, full_dir):
        dctIndex = make_index()

        build_gallery_index(dctIndex, DECISIONS, full_dir)

        assert dctIndex == make_index()

    def test_undecided_content_stays_and_is_counted(self, full_dir):
        dctGallery, dctStats = build_gallery_index(make_index(), {"poster": "remove"}, full_dir)

        assert names(dctGallery, "THREADaaaaa") == ["a_photo.jpg", "a_tiny.gif"]
        assert dctStats["undecided_contents"] == 2

    def test_counts_of_each_cause(self, full_dir):
        _, dctStats = build_gallery_index(make_index(), DECISIONS, full_dir)

        assert dctStats == {"threads": 2, "pictures": 3, "removed": 3, "missing": 1,
                            "repeated_in_thread": 1, "undecided_contents": 0}

    def test_file_on_disk_not_measured_refused(self, full_dir):
        (Path(full_dir) / "a_gone.jpg").write_bytes(b"x")

        with pytest.raises(ValueError, match="a_gone.jpg"):
            build_gallery_index(make_index(), DECISIONS, full_dir)
