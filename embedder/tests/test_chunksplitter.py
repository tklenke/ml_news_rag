# ABOUTME: Tests for splitting a text into prefixed chunks of words
# ABOUTME: Covers chunk boundaries, overlap, the prefix, whitespace and texts without a remainder

from types import SimpleNamespace

import pytest

from f_embed import Embedder

PREFIX = "search_document:"


def split(strText, intChunkSize=3, intOverlap=0):
    """Splits a text with the given settings, without connecting to any server."""
    settings = SimpleNamespace(prefix=PREFIX, chunk_size=intChunkSize, overlap=intOverlap)
    return Embedder.chunksplitter(settings, strText)


def test_text_shorter_than_a_chunk_is_one_chunk():
    assert split("a b") == [f"{PREFIX} a b"]


def test_remainder_is_the_last_chunk():
    assert split("a b c d e") == [f"{PREFIX} a b c", f"{PREFIX} d e"]


def test_every_chunk_has_the_prefix():
    assert all(strChunk.startswith(f"{PREFIX} ") for strChunk in split("a b c d e f g"))


def test_whitespace_is_normalised_to_single_spaces():
    assert split("a\n\n b\t ") == [f"{PREFIX} a b"]


def test_words_keep_their_order_over_chunks():
    lstWords = [f"w{i}" for i in range(1000)]
    lstChunks = split(" ".join(lstWords), 250)
    assert " ".join(strChunk[len(PREFIX) + 1:] for strChunk in lstChunks).split() == lstWords


@pytest.mark.parametrize("intWords", [3, 6])
def test_no_chunk_without_words_after_the_last_full_chunk(intWords):
    lstChunks = split(" ".join(["w"] * intWords))
    assert lstChunks == [f"{PREFIX} w w w"] * (intWords // 3)


@pytest.mark.parametrize("strText", ["", " \n\t "])
def test_text_without_words_has_no_chunks(strText):
    assert split(strText) == []


def get_numbered_text(intWords):
    """Returns a text of the words 1, 2, 3 and so on."""
    return " ".join(str(i + 1) for i in range(intWords))


def test_overlapping_chunks_end_with_the_one_that_reaches_the_end_of_the_text():
    assert split(get_numbered_text(10), 4, 2) == [
        f"{PREFIX} 1 2 3 4", f"{PREFIX} 3 4 5 6", f"{PREFIX} 5 6 7 8", f"{PREFIX} 7 8 9 10"]


def test_overlapping_remainder_is_the_last_chunk():
    assert split(get_numbered_text(7), 4, 2) == [
        f"{PREFIX} 1 2 3 4", f"{PREFIX} 3 4 5 6", f"{PREFIX} 5 6 7"]


@pytest.mark.parametrize("intWords", [1, 3, 4])
def test_text_that_fits_in_one_chunk_is_one_chunk_with_overlap(intWords):
    strText = get_numbered_text(intWords)
    assert split(strText, 4, 2) == [f"{PREFIX} {strText}"]


@pytest.mark.parametrize("strText", ["", " \n\t "])
def test_text_without_words_has_no_chunks_with_overlap(strText):
    assert split(strText, 4, 2) == []


@pytest.mark.parametrize("intSize, intOverlap", [(250, 50), (400, 80), (4, 3)])
def test_every_chunk_has_words_the_chunk_before_it_lacks(intSize, intOverlap):
    for intWords in range(1, 4 * intSize):
        lstChunks = [strChunk.split()[1:]
                     for strChunk in split(get_numbered_text(intWords), intSize, intOverlap)]
        assert [int(lstChunk[0]) for lstChunk in lstChunks] == [
            1 + i * (intSize - intOverlap) for i in range(len(lstChunks))]
        assert all(len(lstChunk) == intSize for lstChunk in lstChunks[:-1])
        assert int(lstChunks[-1][-1]) == intWords
        assert all(int(lstChunk[-1]) > int(lstBefore[-1])
                   for lstBefore, lstChunk in zip(lstChunks, lstChunks[1:]))
