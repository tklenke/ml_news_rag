# ABOUTME: Unit tests for the decisions on image contents (remove or keep, one per content hash)
# ABOUTME: Tests deriving decisions from the 2025 removal lists and saving and loading the decisions file

import json
import pytest
from pathlib import Path

# Import function to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from image_decisions import decisions_from_removals, load_decisions, save_decisions


def image(strName, strHash):
    return {"local_filename": strName, "content_hash": strHash, "size_bytes": 5000}


def make_index():
    """Contents: 'sig' in two threads, 'poster' in two threads, 'photo' once, one unmeasured entry."""
    return {
        "THREADaaaaa": {"images": [image("a_sig.jpg", "sig"), image("a_poster.jpg", "poster"),
                                   image("a_photo.jpg", "photo"),
                                   image("a_photo.jpg", "photo"),  # one attachment linked twice
                                   {"local_filename": "a_new.jpg"}]},
        "THREADbbbbb": {"images": [image("b_sig.jpg", "sig"), image("b_poster.jpg", "poster")]},
    }


class TestDecisionsFromRemovals:
    """Tests for turning the 2025 removal list into decisions by content."""

    def test_every_copy_removed_becomes_remove(self):
        dctDecisions, setMixed = decisions_from_removals(make_index(), {"a_sig.jpg", "b_sig.jpg"})

        assert dctDecisions == {"sig": "remove"}
        assert setMixed == set()

    def test_removed_in_one_thread_kept_in_another_has_no_decision(self):
        dctDecisions, setMixed = decisions_from_removals(make_index(), {"a_poster.jpg"})

        assert dctDecisions == {}
        assert setMixed == {"poster"}

    def test_attachment_linked_twice_counts_as_one_copy(self):
        dctDecisions, setMixed = decisions_from_removals(make_index(), {"a_photo.jpg"})

        assert dctDecisions == {"photo": "remove"}

    def test_names_not_measured_are_ignored(self):
        dctDecisions, setMixed = decisions_from_removals(make_index(), {"a_new.jpg", "gone.jpg"})

        assert dctDecisions == {}
        assert setMixed == set()


class TestDecisionsFile:
    """Tests for saving and loading the decisions file."""

    def test_saved_sorted_and_read_back(self, tmp_path):
        pathFile = tmp_path / "image_decisions.json"

        save_decisions(str(pathFile), {"bbb": "keep", "aaa": "remove"})

        assert load_decisions(str(pathFile)) == {"aaa": "remove", "bbb": "keep"}
        assert list(json.loads(pathFile.read_text())) == ["aaa", "bbb"]

    def test_missing_file_is_no_decisions(self, tmp_path):
        assert load_decisions(str(tmp_path / "none.json")) == {}

    def test_value_other_than_remove_or_keep_refused(self, tmp_path):
        with pytest.raises(ValueError, match="maybe"):
            save_decisions(str(tmp_path / "d.json"), {"aaa": "maybe"})
