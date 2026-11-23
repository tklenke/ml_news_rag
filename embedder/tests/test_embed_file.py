# ABOUTME: Tests for embedding a file into a collection
# ABOUTME: Uses a real Chroma server and the local Ollama; checks ids, sources and completeness

import pytest


def write_words(path, intWords):
    """Writes a file of numbered words and returns its path as a string."""
    path.write_text(" ".join(f"{path.name}{i}" for i in range(intWords)))
    return str(path)


def test_chunk_id_is_the_source_and_the_chunk_number(embdr, tmp_path):
    embdr.embed_file(write_words(tmp_path / "FPRDFZBtlaU.txt", 300))
    dctRows = embdr.chromacollection.get()
    assert sorted(dctRows["ids"]) == ["FPRDFZBtlaU#0", "FPRDFZBtlaU#1"]
    assert dctRows["metadatas"] == [{"source": "FPRDFZBtlaU"}] * 2


def test_sources_whose_names_end_in_digits_are_both_stored_whole(embdr, tmp_path):
    embdr.set_chunk_size(3)
    embdr.embed_file(write_words(tmp_path / "cp__no2", 3 * 11))
    embdr.embed_file(write_words(tmp_path / "cp__no21", 3 * 2))
    lstSources = [m["source"] for m in embdr.chromacollection.get()["metadatas"]]
    assert lstSources.count("cp__no2") == 11
    assert lstSources.count("cp__no21") == 2


def test_file_without_words_is_not_stored(embdr, tmp_path, capsys):
    embdr.embed_file(write_words(tmp_path / "empty.txt", 0))
    assert embdr.get_collection_count() == 0
    assert "zero chunks, skipping embed" in capsys.readouterr().out


def test_chunks_overlap_by_the_number_of_words_set(embdr, tmp_path):
    embdr.set_chunk_size(4)
    embdr.set_overlap(2)
    embdr.embed_file(write_words(tmp_path / "w", 6))
    dctRows = embdr.chromacollection.get()
    assert dict(zip(dctRows["ids"], dctRows["documents"])) == {
        "w#0": "search_document: w0 w1 w2 w3", "w#1": "search_document: w2 w3 w4 w5"}


@pytest.mark.parametrize("intOverlap", [4, 5, -1])
def test_overlap_outside_the_chunk_size_is_refused(embdr, intOverlap):
    embdr.set_chunk_size(4)
    with pytest.raises(ValueError, match="overlap"):
        embdr.set_overlap(intOverlap)
