# ABOUTME: Tests for embedding a file into a collection
# ABOUTME: Uses a real Chroma server and the local Ollama; checks ids, sources and completeness


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
