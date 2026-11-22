# ABOUTME: Tests for reading a whole collection and repairing what it holds
# ABOUTME: Uses a real Chroma server and the local Ollama

import pytest

from f_collection import get_all_ids, hash_ids
from f_repair import add_missing_chunks, refresh_vectors

PREFIX = "search_document:"
LONG_TEXT = PREFIX + " " + " ".join(["antennas and feedlines of composite airplanes"] * 30)


def add_row(embdr, strId, strDocument, lstVector, strSource="doc"):
    """Stores one chunk with a given vector."""
    embdr.chromacollection.add(ids=[strId], documents=[strDocument], embeddings=[lstVector],
                               metadatas=[{"source": strSource}])


def get_row(embdr, strId):
    """Returns one stored chunk."""
    return embdr.chromacollection.get(ids=[strId],
                                      include=["documents", "metadatas", "embeddings"])


def get_wrong_vector():
    return [1.0] + [0.0] * 767


def test_all_ids_are_read_over_several_pages(embdr):
    for i in range(7):
        add_row(embdr, f"id{i}", f"text {i}", get_wrong_vector())
    assert get_all_ids(embdr.chromacollection, page_size=3) == [f"id{i}" for i in range(7)]


def test_hash_of_ids_does_not_depend_on_their_order():
    assert hash_ids(["a", "b"]) == hash_ids(["b", "a"])


def test_hash_of_ids_tells_different_ids_apart():
    assert hash_ids(["a", "b"]) != hash_ids(["ab"])


def test_missing_chunks_are_added_with_separated_ids(embdr, tmp_path):
    embdr.set_chunk_size(2)
    path = tmp_path / "cp__no2"
    path.write_text("a b c d e")
    add_row(embdr, "cp__no20", f"{PREFIX} a b", get_wrong_vector(), "cp__no2")

    assert add_missing_chunks(embdr, str(path)) == 2

    dctRows = embdr.chromacollection.get()
    assert dict(zip(dctRows["ids"], dctRows["documents"])) == {
        "cp__no20": f"{PREFIX} a b", "cp__no2#1": f"{PREFIX} c d", "cp__no2#2": f"{PREFIX} e"}
    assert all(m == {"source": "cp__no2"} for m in dctRows["metadatas"])


def test_complete_source_gets_no_chunks(embdr, tmp_path):
    path = tmp_path / "cp__no2"
    path.write_text("a b c d e")
    embdr.embed_file(str(path))
    assert add_missing_chunks(embdr, str(path)) == 0
    assert embdr.get_collection_count() == 1


def test_repeated_text_in_a_source_is_counted(embdr, tmp_path):
    embdr.set_chunk_size(2)
    path = tmp_path / "doc"
    path.write_text("a b a b")
    add_row(embdr, "doc0", f"{PREFIX} a b", get_wrong_vector())
    assert add_missing_chunks(embdr, str(path)) == 1
    assert embdr.get_collection_count() == 2


def test_chunk_of_another_source_with_the_same_text_does_not_count(embdr, tmp_path):
    path = tmp_path / "doc"
    path.write_text("a b")
    add_row(embdr, "other0", f"{PREFIX} a b", get_wrong_vector(), "other")
    assert add_missing_chunks(embdr, str(path)) == 1


def test_vector_that_differs_is_replaced_and_the_rest_is_kept(embdr, tmp_path):
    add_row(embdr, "doc0", LONG_TEXT, get_wrong_vector())

    assert refresh_vectors(embdr, str(tmp_path / "done.txt")) == (1, 1)

    dctRow = get_row(embdr, "doc0")
    lstExpected = embdr.get_embedding([LONG_TEXT])[0]
    assert list(dctRow["embeddings"][0]) == pytest.approx(lstExpected, abs=1e-4)
    assert dctRow["documents"] == [LONG_TEXT]
    assert dctRow["metadatas"] == [{"source": "doc"}]


def test_vector_that_matches_is_not_written(embdr, tmp_path):
    add_row(embdr, "doc0", LONG_TEXT, embdr.get_embedding([LONG_TEXT])[0])
    assert refresh_vectors(embdr, str(tmp_path / "done.txt")) == (1, 0)


def test_short_chunk_is_not_embedded_again(embdr, tmp_path):
    add_row(embdr, "doc0", "x" * 512, get_wrong_vector())
    assert refresh_vectors(embdr, str(tmp_path / "done.txt")) == (0, 0)
    assert list(get_row(embdr, "doc0")["embeddings"][0]) == get_wrong_vector()


def test_refresh_continues_after_the_chunks_already_done(embdr, tmp_path):
    add_row(embdr, "doc0", LONG_TEXT, get_wrong_vector())
    add_row(embdr, "doc1", LONG_TEXT, get_wrong_vector())
    path = tmp_path / "done.txt"
    path.write_text("doc0\n")

    assert refresh_vectors(embdr, str(path)) == (1, 1)

    assert list(get_row(embdr, "doc0")["embeddings"][0]) == get_wrong_vector()
    assert path.read_text().split() == ["doc0", "doc1"]
