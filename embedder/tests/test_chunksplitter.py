# ABOUTME: Tests for splitting a text into prefixed chunks of words
# ABOUTME: Covers chunk boundaries, the prefix, whitespace and texts without a remainder

from types import SimpleNamespace

import pytest

from f_embed import Embedder

PREFIX = "search_document:"


def split(strText, intChunkSize=3):
    """Splits a text with the given chunk size, without connecting to any server."""
    settings = SimpleNamespace(prefix=PREFIX, chunk_size=intChunkSize)
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
