# ABOUTME: Unit tests for the one rename of downloaded images to names with the attachment id
# ABOUTME: Tests choosing each file's new name from the index and renaming pictures with their thumbnails

import pytest
from pathlib import Path

# Import function to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from rename_images import plan_renames, apply_renames, count_shared_names


ATTACH = "https://groups.google.com/group/cozy_builders/attach"


def make_index():
    """Two threads; the first has two attachments that share one present name."""
    return {
        "THREADaaaaa": {
            "metadata": {"message_id": "THREADaaaaa"},
            "images": [
                {"url": f"{ATTACH}/1111/image.png?part=0.1&view=1", "part": "0.1",
                 "local_filename": "THREADaaaaa_part0_1_image.png"},
                {"url": f"{ATTACH}/2222/image.png?part=0.1&view=1", "part": "0.1",
                 "local_filename": "THREADaaaaa_part0_1_image.png"},
                {"url": f"{ATTACH}/3333/missing.jpg?part=0.2&view=1", "part": "0.2",
                 "local_filename": "THREADaaaaa_part0_2_missing.jpg"},
            ],
        },
        "THREADbbbbb": {
            "metadata": {"message_id": "THREADbbbbb"},
            "images": [
                {"url": f"{ATTACH}/4444/wing%20root.jpg?part=0.1", "part": "0.1",
                 "local_filename": "THREADbbbbb_part0_1_wing_root.jpg"},
            ],
        },
    }


class TestPlanRenames:
    """Tests for choosing the new name of each file on disk."""

    def test_new_name_of_first_url_with_present_name(self):
        """A present name shared by two attachments goes to the first one in index order."""
        setPresent = {"THREADaaaaa_part0_1_image.png", "THREADbbbbb_part0_1_wing_root.jpg"}

        dctRenames = plan_renames(make_index(), setPresent)

        assert dctRenames == {
            "THREADaaaaa_part0_1_image.png": "THREADaaaaa_1111_part0_1_image.png",
            "THREADbbbbb_part0_1_wing_root.jpg": "THREADbbbbb_4444_part0_1_wing_root.jpg",
        }

    def test_entry_without_file_on_disk_is_not_renamed(self):
        """An index entry whose file is not on disk gets no rename."""
        dctRenames = plan_renames(make_index(), {"THREADbbbbb_part0_1_wing_root.jpg"})

        assert list(dctRenames) == ["THREADbbbbb_part0_1_wing_root.jpg"]


class TestCountSharedNames:
    """Tests for counting present names that more than one attachment had."""

    def test_count_names_and_attachments(self):
        """One name shared by two attachments; a second link to one attachment is not sharing."""
        dctIndex = make_index()
        dctIndex["THREADbbbbb"]["images"].append(
            {"url": f"{ATTACH}/4444/wing%20root.jpg?part=0.1&authuser=0", "part": "0.1",
             "local_filename": "THREADbbbbb_part0_1_wing_root.jpg"})

        assert count_shared_names(dctIndex) == (1, 2)


class TestApplyRenames:
    """Tests for renaming pictures and thumbnails on disk."""

    def make_dirs(self, tmp_path):
        pathFull = tmp_path / "full"
        pathThumbs = tmp_path / "thumbs"
        pathFull.mkdir()
        pathThumbs.mkdir()
        return pathFull, pathThumbs

    def test_picture_and_thumbnail_renamed(self, tmp_path):
        """The picture and its thumbnail get the new name; content is unchanged."""
        pathFull, pathThumbs = self.make_dirs(tmp_path)
        (pathFull / "T_part0_1_a.jpg").write_bytes(b"picture")
        (pathThumbs / "T_part0_1_a_thumb.jpg").write_bytes(b"thumb")

        intPictures, intThumbs = apply_renames(
            {"T_part0_1_a.jpg": "T_9999_part0_1_a.jpg"}, str(pathFull), str(pathThumbs))

        assert (intPictures, intThumbs) == (1, 1)
        assert sorted(p.name for p in pathFull.iterdir()) == ["T_9999_part0_1_a.jpg"]
        assert (pathFull / "T_9999_part0_1_a.jpg").read_bytes() == b"picture"
        assert sorted(p.name for p in pathThumbs.iterdir()) == ["T_9999_part0_1_a_thumb.jpg"]
        assert (pathThumbs / "T_9999_part0_1_a_thumb.jpg").read_bytes() == b"thumb"

    def test_picture_without_thumbnail_renamed(self, tmp_path):
        """A picture without a thumbnail is still renamed."""
        pathFull, pathThumbs = self.make_dirs(tmp_path)
        (pathFull / "T_part0_1_a.jpg").write_bytes(b"picture")

        intPictures, intThumbs = apply_renames(
            {"T_part0_1_a.jpg": "T_9999_part0_1_a.jpg"}, str(pathFull), str(pathThumbs))

        assert (intPictures, intThumbs) == (1, 0)
        assert (pathFull / "T_9999_part0_1_a.jpg").read_bytes() == b"picture"

    def test_files_not_in_renames_left_alone(self, tmp_path):
        """A file on disk that no rename names keeps its name."""
        pathFull, pathThumbs = self.make_dirs(tmp_path)
        (pathFull / "T_part0_1_a.jpg").write_bytes(b"picture")
        (pathFull / "T_part0_1_other").write_bytes(b"")

        apply_renames({"T_part0_1_a.jpg": "T_9999_part0_1_a.jpg"}, str(pathFull), str(pathThumbs))

        assert sorted(p.name for p in pathFull.iterdir()) == ["T_9999_part0_1_a.jpg", "T_part0_1_other"]

    def test_thumbnail_shared_by_two_pictures_left_alone(self, tmp_path):
        """A thumbnail name two pictures share (they differ only in extension) goes with neither."""
        pathFull, pathThumbs = self.make_dirs(tmp_path)
        (pathFull / "T_part0_1_image1.jpeg").write_bytes(b"jpeg")
        (pathFull / "T_part0_1_image1.png").write_bytes(b"png")
        (pathThumbs / "T_part0_1_image1_thumb.jpg").write_bytes(b"thumb of one of them")

        intPictures, intThumbs = apply_renames(
            {"T_part0_1_image1.jpeg": "T_1111_part0_1_image1.jpeg",
             "T_part0_1_image1.png": "T_2222_part0_1_image1.png"},
            str(pathFull), str(pathThumbs))

        assert (intPictures, intThumbs) == (2, 0)
        assert sorted(p.name for p in pathFull.iterdir()) == [
            "T_1111_part0_1_image1.jpeg", "T_2222_part0_1_image1.png"]
        assert sorted(p.name for p in pathThumbs.iterdir()) == ["T_part0_1_image1_thumb.jpg"]

    def test_existing_target_refused_before_any_rename(self, tmp_path):
        """If any new name is already taken, nothing is renamed and nothing overwritten."""
        pathFull, pathThumbs = self.make_dirs(tmp_path)
        (pathFull / "T_part0_1_a.jpg").write_bytes(b"first")
        (pathFull / "T_part0_2_b.jpg").write_bytes(b"second")
        (pathThumbs / "T_8888_part0_2_b_thumb.jpg").write_bytes(b"taken")

        with pytest.raises(FileExistsError, match="T_8888_part0_2_b_thumb.jpg"):
            apply_renames({"T_part0_1_a.jpg": "T_9999_part0_1_a.jpg",
                           "T_part0_2_b.jpg": "T_8888_part0_2_b.jpg"},
                          str(pathFull), str(pathThumbs))

        assert sorted(p.name for p in pathFull.iterdir()) == ["T_part0_1_a.jpg", "T_part0_2_b.jpg"]
        assert (pathThumbs / "T_8888_part0_2_b_thumb.jpg").read_bytes() == b"taken"
