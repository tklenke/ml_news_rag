# ABOUTME: Embeds the variants of the chunk-size experiment one after another, detached
# ABOUTME: Usage: python chunk_queue.py start|stop [--trial DIRECTORY]; continues where it stopped

import argparse
import fcntl
import os
import signal
import subprocess
import sys
import time
import urllib.request

from embedder_settings import EXPERIMENTDIR

# Chunk size and overlap in words, in the order they are embedded
VARIANTS = [(250, 0), (400, 0), (150, 0), (250, 50), (400, 80)]
CHROMA_PORT = "8010"
OLLAMA_PORT = "11998"
OLLAMA_CONTAINER = "chunk_experiment_ollama"
CONTAINERS = {"chunk_experiment_chroma": f"http://localhost:{CHROMA_PORT}/api/v2/heartbeat",
              OLLAMA_CONTAINER: f"http://localhost:{OLLAMA_PORT}/api/version"}


def get_commands(trial=None):
    """
    Makes the embedder command of every variant.

    :param trial: The directory of the files of a trial, or None for the whole corpus.
    :return: A list of collection names and commands, in the order they are run.
    """
    lstCommands = []
    for intSize, intOverlap in VARIANTS:
        strName = f"{'trial_' if trial else ''}words{intSize}_overlap{intOverlap}"
        lstCommand = [sys.executable, "-u", "embedder.py", "--collection", strName,
                      "--chunk-size", str(intSize), "--overlap", str(intOverlap),
                      "--chroma-port", CHROMA_PORT, "--ollama-port", OLLAMA_PORT]
        if trial:
            lstCommand += ["--sources", trial]
        lstCommands.append((strName, lstCommand))
    return lstCommands


def run_variants(commands):
    """Runs the commands one after another, also after one that fails."""
    for strName, lstCommand in commands:
        fStart = time.time()
        print(f"{time.ctime()} START {strName}", flush=True)
        # The lock of the queue is passed on, so that it is held until the last process ends
        intExitCode = subprocess.run(lstCommand, close_fds=False).returncode
        print(f"{time.ctime()} END {strName} exit code {intExitCode} "
              f"{(time.time() - fStart) / 3600:.2f} hours", flush=True)


class ChunkQueue():
    """A detached process of which only one runs at a time, and the containers it needs."""

    def __init__(self, directory, containers, stop_container, wait_seconds=120):
        """
        :param directory: The directory of the log and of the lock.
        :param containers: The names of the containers with an address that answers when ready.
        :param stop_container: The name of the container that is stopped with the queue.
        :param wait_seconds: The time a container has to answer.
        """
        os.makedirs(directory, exist_ok=True)
        self.lockfile = os.path.join(directory, "queue.lock")
        self.logfile = os.path.join(directory, "queue.log")
        self.containers = containers
        self.stop_container = stop_container
        self.wait_seconds = wait_seconds

    def take_lock(self):
        """Returns the opened lock file, or None when the queue is running."""
        lock = open(self.lockfile, "a+")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            lock.close()
            return None
        return lock

    def is_running(self):
        """Tells whether any process of the queue is running."""
        lock = self.take_lock()
        if lock is None:
            return True
        lock.close()
        return False

    def start_container(self, name, url):
        """Starts a container and waits for its server. Returns whether it answers."""
        result = subprocess.run(["docker", "start", name], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"{name} did not start: {result.stderr.strip()}")
            return False
        fEnd = time.time() + self.wait_seconds
        while time.time() < fEnd:
            try:
                urllib.request.urlopen(url, timeout=5).close()
                return True
            except OSError:
                time.sleep(0.5)
        print(f"{name} does not answer at {url}")
        return False

    def start(self, command):
        """
        Starts the containers and runs a command detached, with its output in the log.

        :param command: The command as a list of strings.
        :return: Whether the command was started.
        """
        lock = self.take_lock()
        if lock is None:
            print("The queue is already running")
            return False
        with lock, open(self.logfile, "a") as log:
            if not all(self.start_container(*item) for item in self.containers.items()):
                return False
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True,
                                       pass_fds=[lock.fileno()])
            lock.truncate(0)
            lock.write(str(process.pid))
        print(f"The queue is started. Log: {os.path.abspath(self.logfile)}")
        return True

    def stop(self):
        """Ends every process of the queue and stops the container that is stopped with it."""
        if self.is_running():
            with open(self.lockfile) as lock:
                intGroup = int(lock.read())
            for intSignal in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.killpg(intGroup, intSignal)
                except ProcessLookupError:
                    break
                fEnd = time.time() + 20
                while self.is_running() and time.time() < fEnd:
                    time.sleep(0.1)
                if not self.is_running():
                    break
            print("The queue did not stop" if self.is_running() else "The queue is stopped")
        else:
            print("The queue is not running")
        result = subprocess.run(["docker", "stop", self.stop_container], capture_output=True,
                                text=True)
        print(f"{self.stop_container} is stopped" if result.returncode == 0
              else f"{self.stop_container} did not stop: {result.stderr.strip()}")


def main():
    parser = argparse.ArgumentParser(description="Embeds the variants of the chunk experiment")
    parser.add_argument("action", choices=["start", "stop", "run"])
    parser.add_argument("--trial", metavar="DIRECTORY")
    args = parser.parse_args()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if args.action == "run":
        run_variants(get_commands(args.trial))
        return 0
    queue = ChunkQueue(EXPERIMENTDIR, CONTAINERS, OLLAMA_CONTAINER)
    if args.action == "stop":
        queue.stop()
        return 0
    lstTrial = ["--trial", args.trial] if args.trial else []
    return 0 if queue.start([sys.executable, "-u", "chunk_queue.py", "run"] + lstTrial) else 1


if __name__ == "__main__":
    sys.exit(main())
