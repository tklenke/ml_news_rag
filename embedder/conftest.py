# ABOUTME: Pytest fixtures for the embedder tests
# ABOUTME: Runs a throwaway Chroma server so that tests never touch the site's data

import socket
import subprocess
import time

import chromadb
import pytest

from f_embed import Embedder

CHROMA_IMAGE = "chromadb/chroma:1.5.9"


def get_free_port():
    """Returns a local port that nothing listens on."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return str(sock.getsockname()[1])


@pytest.fixture(scope="session")
def chroma_port():
    """Starts a Chroma container without a data volume and yields its port."""
    strPort = get_free_port()
    strContainer = subprocess.run(
        ["docker", "run", "-d", "--rm", "-p", f"127.0.0.1:{strPort}:8000", CHROMA_IMAGE],
        check=True, capture_output=True, text=True).stdout.strip()
    try:
        for _ in range(60):
            try:
                chromadb.HttpClient("localhost", strPort).heartbeat()
                break
            except Exception:
                time.sleep(0.5)
        else:
            pytest.fail("The Chroma test container did not start")
        yield strPort
    finally:
        subprocess.run(["docker", "stop", strContainer], check=True, capture_output=True)


@pytest.fixture
def embdr(chroma_port, capsys):
    """An Embedder with an empty collection on the throwaway Chroma server."""
    embedder = Embedder(chromaport=chroma_port)
    embedder.set_collection("test_collection", initialize=True)
    embedder.set_model("nomic-embed-text")
    embedder.set_prefix("search_document:")
    embedder.set_chunk_size(250)
    capsys.readouterr()
    return embedder
