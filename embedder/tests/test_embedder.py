# ABOUTME: Tests for a run of the embedder: its parameters, its progress file and its failures
# ABOUTME: Uses a real Chroma server and the local Ollama; failures come from real causes

import ollama
import pytest

from conftest import get_free_port
from embedder import NMAXFAILURES, embed_files, get_files_to_embed, get_progress_file, parse_args, run
from embedder_settings import CHUNKSIZE, COMPLETEDEMBEDFILE, EMBEDMODEL, SOURCEDOCPATHS


def write_files(directory, intFiles, intWords=3):
    """Writes text files of a few words and returns their paths."""
    lstPaths = []
    for i in range(intFiles):
        path = directory / f"doc{i}.txt"
        path.write_text(" ".join(["word"] * intWords))
        lstPaths.append(str(path))
    return lstPaths


def test_no_parameters_are_the_settings_of_the_production_collection():
    args = parse_args([])
    assert (args.chunk_size, args.overlap, args.collection) == (CHUNKSIZE, 0, EMBEDMODEL)
    assert (args.chroma_port, args.ollama_port) == ("8000", "11434")
    assert args.sources == SOURCEDOCPATHS
    assert get_progress_file(args.collection) == COMPLETEDEMBEDFILE


def test_parameters_are_read():
    args = parse_args(["--collection", "words400_overlap80", "--chunk-size", "400",
                       "--overlap", "80", "--chroma-port", "8010", "--ollama-port", "11998",
                       "--sources", "a", "b"])
    assert (args.chunk_size, args.overlap, args.collection) == (400, 80, "words400_overlap80")
    assert (args.chroma_port, args.ollama_port) == ("8010", "11998")
    assert args.sources == ["a", "b"]


def test_every_collection_has_its_own_progress_file():
    assert len({get_progress_file(strName)
                for strName in (EMBEDMODEL, "words150_overlap0", "words250_overlap0")}) == 3


@pytest.mark.parametrize("lstArgs", [["--chunk-size", "150"], ["--overlap", "50"]])
def test_production_collection_is_refused_with_other_chunks(lstArgs, capsys):
    with pytest.raises(SystemExit):
        parse_args(lstArgs)
    assert "needs a --collection" in capsys.readouterr().err


def test_files_in_the_progress_file_are_not_done_again(tmp_path):
    lstPaths = write_files(tmp_path, 3)
    progressfile = tmp_path / "progress"
    progressfile.write_text("doc1\n")
    assert get_files_to_embed(lstPaths, str(progressfile)) == [lstPaths[0], lstPaths[2]]


def test_all_files_are_done_without_a_progress_file(tmp_path):
    lstPaths = write_files(tmp_path, 3)
    assert get_files_to_embed(lstPaths, str(tmp_path / "progress")) == lstPaths


def test_embedded_files_are_in_the_collection_and_the_progress_file(embdr, tmp_path):
    lstPaths = write_files(tmp_path, 3)
    progressfile = tmp_path / "progress"
    assert embed_files(embdr, lstPaths, str(progressfile))
    assert progressfile.read_text().split() == ["doc0", "doc1", "doc2"]
    assert embdr.get_collection_count() == 3


def test_run_with_nothing_to_do_ends_well(embdr, tmp_path, capsys):
    assert embed_files(embdr, [], str(tmp_path / "progress"))
    assert "Total Embedded: 0" in capsys.readouterr().out


def test_run_uses_its_parameters_and_continues(chroma_port, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("embedder.EXPERIMENTDIR", str(tmp_path / "progress"))
    directory = tmp_path / "docs"
    directory.mkdir()
    write_files(directory, 2, intWords=6)
    args = parse_args(["--collection", "run_test", "--chunk-size", "4", "--overlap", "2",
                       "--chroma-port", chroma_port, "--sources", str(directory)])

    assert run(args)
    strOutput = capsys.readouterr().out
    assert "run_test" in strOutput
    assert "Total Embedded: 2" in strOutput
    assert "Chunks: 4" in strOutput
    assert "Size of Collection: 4" in strOutput

    assert run(args)
    strOutput = capsys.readouterr().out
    assert "Net to complete: 0" in strOutput
    assert "Size of Collection: 4" in strOutput


@pytest.fixture
def unreachable_embdr(embdr):
    """An Embedder whose Ollama address has nothing that listens."""
    embdr.ollamaclient = ollama.Client(f"http://localhost:{get_free_port()}")
    return embdr


def test_run_goes_on_after_a_file_that_fails(embdr, tmp_path, capsys):
    lstPaths = write_files(tmp_path, 2)
    strMissing = str(tmp_path / "missing.txt")
    progressfile = tmp_path / "progress"

    assert not embed_files(embdr, [lstPaths[0], strMissing, lstPaths[1]], str(progressfile))

    assert progressfile.read_text().split() == ["doc0", "doc1"]
    strOutput = capsys.readouterr().out
    assert f"FAILED {strMissing}" in strOutput
    assert "Traceback (most recent call last)" in strOutput
    assert "FileNotFoundError" in strOutput
    assert "Failed: 1" in strOutput
    assert "Remaining to Embed: 1" in strOutput


def test_file_that_failed_is_embedded_by_a_later_run(embdr, unreachable_embdr, chroma_port,
                                                     tmp_path, capsys):
    lstPaths = write_files(tmp_path, 1)
    progressfile = tmp_path / "progress"
    assert not embed_files(unreachable_embdr, lstPaths, str(progressfile))
    assert "Failed to connect to Ollama" in capsys.readouterr().out
    assert get_files_to_embed(lstPaths, str(progressfile)) == lstPaths

    embdr.ollamaclient = ollama.Client("http://localhost:11434")
    assert embed_files(embdr, get_files_to_embed(lstPaths, str(progressfile)), str(progressfile))
    assert progressfile.read_text().split() == ["doc0"]
    assert embdr.get_collection_count() == 1


def test_run_ends_after_many_failures_in_a_row(unreachable_embdr, tmp_path, capsys):
    lstPaths = write_files(tmp_path, NMAXFAILURES + 5)
    assert not embed_files(unreachable_embdr, lstPaths, str(tmp_path / "progress"))
    strOutput = capsys.readouterr().out
    assert strOutput.count("FAILED ") == NMAXFAILURES == 20
    assert f"{NMAXFAILURES} failures in a row" in strOutput
    assert f"Remaining to Embed: {NMAXFAILURES + 5}" in strOutput


def test_file_that_is_done_starts_the_count_of_failures_again(unreachable_embdr, tmp_path, capsys):
    (tmp_path / "empty").mkdir()
    strEmpty = write_files(tmp_path / "empty", 1, intWords=0)[0]
    lstPaths = write_files(tmp_path, 2 * (NMAXFAILURES - 1))
    lstPaths.insert(NMAXFAILURES - 1, strEmpty)
    assert not embed_files(unreachable_embdr, lstPaths, str(tmp_path / "progress"))
    strOutput = capsys.readouterr().out
    assert strOutput.count("FAILED ") == 2 * (NMAXFAILURES - 1)
    assert "in a row" not in strOutput
