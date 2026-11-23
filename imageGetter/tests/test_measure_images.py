# ABOUTME: Unit tests for measuring downloaded images into the image index
# ABOUTME: Tests size, width, height and content hash written for real files on disk

import hashlib
import pytest
from pathlib import Path
from PIL import Image

# Import function to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from measure_images import measure_index


def make_index(*lstNames):
    return {"THREADaaaaa": {"metadata": {"message_id": "THREADaaaaa"},
                            "images": [{"local_filename": strName} for strName in lstNames]}}


class TestMeasureIndex:
    """Tests for writing measures into each image entry."""

    def test_measures_of_real_picture(self, tmp_path):
        """A real small picture gets its bytes, width, height and content hash."""
        pathPicture = tmp_path / "a.png"
        Image.new('RGB', (30, 20), color='red').save(pathPicture)
        bytesContent = pathPicture.read_bytes()
        dctIndex = make_index("a.png")

        dctStats = measure_index(dctIndex, str(tmp_path))

        dctImage = dctIndex["THREADaaaaa"]["images"][0]
        assert dctImage["size_bytes"] == len(bytesContent)
        assert dctImage["width"] == 30
        assert dctImage["height"] == 20
        assert dctImage["content_hash"] == hashlib.sha256(bytesContent).hexdigest()
        assert dctStats == {"measured": 1, "already_measured": 0, "missing": 0, "not_a_picture": 0}

    def test_missing_file_gets_no_measures(self, tmp_path):
        """An entry whose file is not on disk is left as it is."""
        dctIndex = make_index("missing.jpg")

        dctStats = measure_index(dctIndex, str(tmp_path))

        assert dctIndex["THREADaaaaa"]["images"][0] == {"local_filename": "missing.jpg"}
        assert dctStats["missing"] == 1

    def test_measured_entry_not_measured_again(self, tmp_path):
        """An entry that already has a content hash keeps its measures."""
        Image.new('RGB', (30, 20)).save(tmp_path / "a.png")
        dctIndex = make_index("a.png")
        dctIndex["THREADaaaaa"]["images"][0].update(
            {"size_bytes": 1, "width": 2, "height": 3, "content_hash": "earlier"})

        dctStats = measure_index(dctIndex, str(tmp_path))

        assert dctIndex["THREADaaaaa"]["images"][0]["content_hash"] == "earlier"
        assert dctIndex["THREADaaaaa"]["images"][0]["width"] == 2
        assert dctStats["already_measured"] == 1

    def test_file_that_is_not_a_picture(self, tmp_path):
        """A file that is not a picture gets its bytes and hash, and no width or height."""
        (tmp_path / "empty.jpg").write_bytes(b"")
        dctIndex = make_index("empty.jpg")

        dctStats = measure_index(dctIndex, str(tmp_path))

        dctImage = dctIndex["THREADaaaaa"]["images"][0]
        assert dctImage["size_bytes"] == 0
        assert dctImage["width"] is None
        assert dctImage["height"] is None
        assert dctImage["content_hash"] == hashlib.sha256(b"").hexdigest()
        assert dctStats["not_a_picture"] == 1
