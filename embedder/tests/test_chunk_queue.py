# ABOUTME: Tests for the queue that embeds the chunk variants one after another
# ABOUTME: Uses real processes, a real Chroma container and the local Ollama

import subprocess
import sys
import time

import chromadb
import pytest

from chunk_queue import ChunkQueue, get_commands, run_variants
from conftest import CHROMA_IMAGE, get_free_port

SLEEPER = [sys.executable, "-c", "import time; print('sleeping', flush=True); time.sleep(120)"]


def is_container_running(strName):
    return subprocess.run(["docker", "inspect", "-f", "{{.State.Running}}", strName],
                          capture_output=True, text=True).stdout.strip() == "true"


@pytest.fixture(scope="module")
def container():
    """A stopped throwaway container and the address that answers when it is running."""
    strPort = get_free_port()
    strName = f"chunk_queue_test_{strPort}"
    subprocess.run(["docker", "create", "--name", strName, "-p", f"127.0.0.1:{strPort}:8000",
                    CHROMA_IMAGE], check=True, capture_output=True)
    yield strName, f"http://localhost:{strPort}/api/v2/heartbeat"
    subprocess.run(["docker", "rm", "-f", strName], check=True, capture_output=True)


@pytest.fixture
def queue(container, tmp_path):
    """A queue of the throwaway container, stopped at the end."""
    strName, strUrl = container
    chunkqueue = ChunkQueue(str(tmp_path), {strName: strUrl}, strName)
    yield chunkqueue
    chunkqueue.stop()


def wait_for_text(path, strText):
    for _ in range(100):
        if path.exists() and strText in path.read_text():
            return
        time.sleep(0.1)
    pytest.fail(f"{strText} not found in {path}")


def test_variants_are_queued_in_the_order_of_the_plan():
    assert [(strName, lstCommand[lstCommand.index("--chunk-size") + 1],
             lstCommand[lstCommand.index("--overlap") + 1])
            for strName, lstCommand in get_commands()] == [
        ("words250_overlap0", "250", "0"), ("words400_overlap0", "400", "0"),
        ("words150_overlap0", "150", "0"), ("words250_overlap50", "250", "50"),
        ("words400_overlap80", "400", "80")]


@pytest.mark.parametrize("strTrial", [None, "../data/test_min"])
def test_every_variant_goes_to_the_servers_of_the_experiment(strTrial):
    for strName, lstCommand in get_commands(strTrial):
        assert lstCommand[lstCommand.index("--chroma-port") + 1] == "8010"
        assert lstCommand[lstCommand.index("--ollama-port") + 1] == "11998"
        assert lstCommand[lstCommand.index("--collection") + 1] == strName


def test_trial_has_collections_and_sources_of_its_own():
    lstTrial = get_commands("../data/test_min")
    assert not {strName for strName, _ in lstTrial} & {strName for strName, _ in get_commands()}
    assert all(lstCommand[lstCommand.index("--sources") + 1] == "../data/test_min"
               for _, lstCommand in lstTrial)
    assert all("--sources" not in lstCommand for _, lstCommand in get_commands())


def test_variants_run_one_after_another_also_after_one_that_fails(chroma_port, tmp_path, capfd):
    (tmp_path / "doc.txt").write_text("some words")
    lstCommands = [
        (strName, [sys.executable, "-u", "embedder.py", "--collection", strName,
                   "--chroma-port", chroma_port, "--ollama-port", strOllamaPort,
                   "--sources", str(tmp_path)])
        for strName, strOllamaPort in (("queue_test_fails", get_free_port()),
                                       ("queue_test_works", "11434"))]
    import embedder
    from pathlib import Path
    lstProgress = [Path(embedder.get_progress_file(strName)) for strName, _ in lstCommands]
    try:
        run_variants(lstCommands)
        assert [path.exists() for path in lstProgress] == [False, True]
    finally:
        for path in lstProgress:
            path.unlink(missing_ok=True)

    strOutput = capfd.readouterr().out
    assert "START queue_test_fails" in strOutput
    assert "Failed to connect to Ollama" in strOutput
    assert "END queue_test_fails exit code 1" in strOutput
    assert strOutput.index("END queue_test_fails") < strOutput.index("START queue_test_works")
    assert "END queue_test_works exit code 0" in strOutput
    client = chromadb.HttpClient("localhost", chroma_port)
    assert client.get_collection("queue_test_works").count() == 1


def test_start_starts_the_container_and_runs_detached(queue, container, tmp_path, capsys):
    assert queue.start(SLEEPER)
    assert is_container_running(container[0])
    wait_for_text(tmp_path / "queue.log", "sleeping")
    assert queue.is_running()


def test_start_is_refused_while_the_queue_is_running(queue, tmp_path, capsys):
    assert queue.start(SLEEPER)
    capsys.readouterr()
    assert not queue.start([sys.executable, "-c", "print('second', flush=True)"])
    assert "already running" in capsys.readouterr().out
    time.sleep(1)
    assert "second" not in (tmp_path / "queue.log").read_text()


def test_queue_is_running_while_a_process_it_started_is(queue, tmp_path):
    strCode = f"import subprocess; subprocess.Popen({SLEEPER!r}, close_fds=False)"
    assert queue.start([sys.executable, "-c", strCode])
    wait_for_text(tmp_path / "queue.log", "sleeping")
    assert queue.is_running()


def test_stop_ends_every_process_and_the_container(queue, container, tmp_path, capsys):
    strCode = f"import subprocess; subprocess.run({SLEEPER!r}, close_fds=False)"
    assert queue.start([sys.executable, "-c", strCode])
    wait_for_text(tmp_path / "queue.log", "sleeping")
    queue.stop()
    assert not queue.is_running()
    assert not is_container_running(container[0])
    assert "stopped" in capsys.readouterr().out


def test_queue_can_be_started_again_after_a_stop(queue, tmp_path):
    assert queue.start(SLEEPER)
    queue.stop()
    assert queue.start([sys.executable, "-c", "print('second', flush=True)"])
    wait_for_text(tmp_path / "queue.log", "second")


def test_stop_of_a_queue_that_is_not_running_ends_no_process(queue, tmp_path, capsys):
    process = subprocess.Popen(SLEEPER, start_new_session=True, stdout=subprocess.DEVNULL)
    (tmp_path / "queue.lock").write_text(str(process.pid))
    try:
        queue.stop()
        assert process.poll() is None
        assert "not running" in capsys.readouterr().out
    finally:
        process.kill()
        process.wait()


def test_start_is_given_up_when_a_container_does_not_start(tmp_path, capsys):
    chunkqueue = ChunkQueue(str(tmp_path), {"no_such_container": "http://localhost"},
                            "no_such_container")
    assert not chunkqueue.start(SLEEPER)
    assert "no_such_container" in capsys.readouterr().out
    assert not chunkqueue.is_running()


def test_start_is_given_up_when_a_server_does_not_answer(container, tmp_path, capsys):
    chunkqueue = ChunkQueue(str(tmp_path), {container[0]: f"http://localhost:{get_free_port()}"},
                            container[0], wait_seconds=2)
    assert not chunkqueue.start(SLEEPER)
    assert "does not answer" in capsys.readouterr().out
    assert not chunkqueue.is_running()
