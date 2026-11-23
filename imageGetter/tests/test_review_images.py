# ABOUTME: Unit tests for the local review tool of image contents (D50)
# ABOUTME: Tests the three lists, their order, clicks saved to the decisions file, and the tool's HTTP interface

import json
import threading
import urllib.error
import urllib.request
import pytest
from pathlib import Path

# Import function to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from image_decisions import load_decisions
from review_images import ReviewState, content_items, make_server


def image(strName, strHash, intBytes=5000, intWidth=640, intHeight=480, strFilename="photo.jpg"):
    return {"local_filename": strName, "filename": strFilename, "content_hash": strHash,
            "size_bytes": intBytes, "width": intWidth, "height": intHeight}


def thread(strId, strDate, lstImages):
    return {"metadata": {"message_id": strId, "subject": f"Subject {strId}", "date": strDate},
            "images": lstImages}


def make_index():
    return {
        "THREADlater": thread("THREADlater", "Mar 1, 2012", [
            image("l_photo.jpg", "photo_l"),
            image("l_sig.jpg", "sig"),
        ]),
        "THREADearly": thread("THREADearly", "Feb 3, 2010", [
            image("e_photo.jpg", "photo_e"),
            image("e_sig.jpg", "sig"),
            image("e_tiny.gif", "tiny", intBytes=999),
            {"local_filename": "e_missing.jpg", "filename": "missing.jpg"},
        ]),
    }


def by_hash(lstItems):
    return {dctItem["hash"]: dctItem for dctItem in lstItems}


class TestContentItems:
    """Tests for turning the index into one item per content."""

    def test_content_in_two_threads_is_one_item_under_its_earliest_thread(self):
        dctItems = by_hash(content_items(make_index(), {}, set()))

        assert dctItems["sig"]["thread_count"] == 2
        assert dctItems["sig"]["thread_id"] == "THREADearly"
        assert dctItems["sig"]["local_filename"] == "e_sig.jpg"

    def test_file_under_1000_bytes_and_unmeasured_entry_are_not_shown(self):
        dctItems = by_hash(content_items(make_index(), {}, set()))

        assert set(dctItems) == {"photo_l", "photo_e", "sig"}

    def test_threads_by_date_and_repeated_contents_first_within_a_thread(self):
        lstItems = content_items(make_index(), {}, set())

        assert [dctItem["hash"] for dctItem in lstItems] == ["sig", "photo_e", "photo_l"]


class TestLists:
    """Tests for which list a content is in: suggested, new or decided."""

    def list_of(self, dctImage, dctDecisions=None, setSuggestions=frozenset()):
        dctIndex = {"THREADaaaaa": thread("THREADaaaaa", "Jan 1, 2015", [dctImage])}
        return content_items(dctIndex, dctDecisions or {}, set(setSuggestions))[0]["list"]

    def test_ordinary_picture_is_new(self):
        assert self.list_of(image("a.jpg", "h")) == "new"

    def test_in_two_or_more_threads_is_suggested(self):
        lstItems = content_items(make_index(), {}, set())

        assert by_hash(lstItems)["sig"]["list"] == "suggested"

    def test_shorter_side_under_200_is_suggested(self):
        assert self.list_of(image("a.jpg", "h", intWidth=800, intHeight=199)) == "suggested"
        assert self.list_of(image("a.jpg", "h", intWidth=800, intHeight=200)) == "new"

    def test_named_imageNNN_under_20000_bytes_is_suggested(self):
        assert self.list_of(image("a.jpg", "h", intBytes=19999, strFilename="image003.png")) == "suggested"
        assert self.list_of(image("a.jpg", "h", intBytes=19999, strFilename="Image12.jpg")) == "suggested"
        assert self.list_of(image("a.jpg", "h", intBytes=20000, strFilename="image003.png")) == "new"
        assert self.list_of(image("a.jpg", "h", intBytes=5000, strFilename="myimage003.png")) == "new"

    def test_removed_in_some_copies_in_2025_is_suggested(self):
        assert self.list_of(image("a.jpg", "h"), setSuggestions={"h"}) == "suggested"

    def test_decided_is_decided_whatever_else_holds(self):
        dctImage = image("a.jpg", "h", intHeight=50)

        assert self.list_of(dctImage, {"h": "keep"}) == "decided"
        assert self.list_of(dctImage, {"h": "remove"}) == "decided"


class TestReviewState:
    """Tests for clicks and the keep button, each saved to the decisions file at once."""

    def make_state(self, tmp_path):
        return ReviewState(make_index(), set(), str(tmp_path / "decisions.json"))

    def test_decision_saved_at_once_and_can_be_changed(self, tmp_path):
        state = self.make_state(tmp_path)

        state.decide("sig", "remove")
        assert load_decisions(state.strDecisionsPath) == {"sig": "remove"}

        state.decide("sig", "keep")
        assert load_decisions(state.strDecisionsPath) == {"sig": "keep"}

    def test_decision_other_than_remove_or_keep_refused(self, tmp_path):
        state = self.make_state(tmp_path)

        with pytest.raises(ValueError):
            state.decide("sig", "maybe")
        assert not Path(state.strDecisionsPath).exists()

    def test_keep_marks_only_those_not_marked_remove(self, tmp_path):
        state = self.make_state(tmp_path)
        state.decide("sig", "remove")

        state.keep(["sig", "photo_e"])

        assert load_decisions(state.strDecisionsPath) == {"sig": "remove", "photo_e": "keep"}

    def test_unknown_content_refused(self, tmp_path):
        state = self.make_state(tmp_path)

        with pytest.raises(KeyError):
            state.decide("nothere", "remove")
        with pytest.raises(KeyError):
            state.keep(["nothere"])
        assert not Path(state.strDecisionsPath).exists()

    def test_decisions_already_in_the_file_are_kept(self, tmp_path):
        pathDecisions = tmp_path / "decisions.json"
        pathDecisions.write_text(json.dumps({"other": "remove"}))
        state = ReviewState(make_index(), set(), str(pathDecisions))

        state.decide("sig", "remove")

        assert load_decisions(str(pathDecisions)) == {"other": "remove", "sig": "remove"}


@pytest.fixture
def server(tmp_path):
    """The review tool served on a free local port, with real files for two contents."""
    pathFull = tmp_path / "full"
    pathThumbs = tmp_path / "thumbs"
    pathFull.mkdir()
    pathThumbs.mkdir()
    (pathFull / "e_sig.jpg").write_bytes(b"full sig")
    (pathThumbs / "e_sig_thumb.jpg").write_bytes(b"thumb sig")
    (pathFull / "e_photo.jpg").write_bytes(b"full photo")

    state = ReviewState(make_index(), set(), str(tmp_path / "decisions.json"))
    httpd = make_server(state, str(pathFull), str(pathThumbs), "127.0.0.1", 0)
    threadServe = threading.Thread(target=httpd.serve_forever, daemon=True)
    threadServe.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}", state
    httpd.shutdown()
    httpd.server_close()


def get(strUrl):
    with urllib.request.urlopen(strUrl) as response:
        return response.read()


def post(strUrl, objBody):
    request = urllib.request.Request(strUrl, data=json.dumps(objBody).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


class TestHttpInterface:
    """Tests through the tool's own HTTP interface."""

    def test_decision_saved_and_read_back(self, server):
        strBase, state = server

        assert post(strBase + "/decide", {"hash": "sig", "decision": "remove"}) == \
            {"hash": "sig", "decision": "remove"}

        assert json.loads(get(strBase + "/decisions")) == {"sig": "remove"}
        assert load_decisions(state.strDecisionsPath) == {"sig": "remove"}

    def test_keep_saved_and_read_back(self, server):
        strBase, state = server
        post(strBase + "/decide", {"hash": "sig", "decision": "remove"})

        assert post(strBase + "/keep", {"hashes": ["sig", "photo_e"]}) == {"kept": 1}

        assert json.loads(get(strBase + "/decisions")) == {"sig": "remove", "photo_e": "keep"}

    def test_page_of_a_list_shows_its_contents(self, server):
        strBase, _ = server

        strPage = get(strBase + "/?list=new&page=1").decode("utf-8")

        assert 'data-hash="photo_e"' in strPage
        assert 'data-hash="sig"' not in strPage
        assert "Subject THREADearly" in strPage

    def test_thumbnail_and_full_picture_served_by_content(self, server):
        strBase, _ = server

        assert get(strBase + "/thumb/sig") == b"thumb sig"
        assert get(strBase + "/full/sig") == b"full sig"

    def test_full_picture_served_when_there_is_no_thumbnail(self, server):
        strBase, _ = server

        assert get(strBase + "/thumb/photo_e") == b"full photo"

    def test_unknown_content_is_404(self, server):
        strBase, _ = server

        for strPath in ("/thumb/nothere", "/full/..%2Fdecisions.json", "/nothere"):
            with pytest.raises(urllib.error.HTTPError) as excinfo:
                get(strBase + strPath)
            assert excinfo.value.code == 404
        with pytest.raises(urllib.error.HTTPError) as excinfo:
            post(strBase + "/decide", {"hash": "nothere", "decision": "remove"})
        assert excinfo.value.code == 404

    def test_decision_other_than_remove_or_keep_is_400(self, server):
        strBase, _ = server

        with pytest.raises(urllib.error.HTTPError) as excinfo:
            post(strBase + "/decide", {"hash": "sig", "decision": "maybe"})
        assert excinfo.value.code == 400

    def test_page_has_a_keep_and_a_discard_choice_per_picture_with_the_decision_checked(self, server):
        strBase, _ = server
        post(strBase + "/decide", {"hash": "sig", "decision": "remove"})

        strPage = get(strBase + "/?list=decided&page=1").decode("utf-8")

        assert 'name="sig" value="keep">' in strPage
        assert 'name="sig" value="remove" checked>' in strPage
