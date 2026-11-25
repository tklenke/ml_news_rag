# ABOUTME: Tests for finding posts that a thread was saved with collapsed, and for the fetch
# ABOUTME: saving a thread only when none of its posts is collapsed
#
# The threads in tests/threads are real saved threads, shortened, with names and addresses
# replaced. Not tested here: the fetch waiting for Google's page to expand, which needs the
# page itself; the refetch of the collapsed threads is its check (plan, "Collapsed posts").

import os
import shutil

import pytest

from f_collapsed import count_collapsed_posts, get_collapsed_threads
import process_message

THREADS = os.path.join(os.path.dirname(__file__), "threads")


def read_thread(strName):
    with open(os.path.join(THREADS, strName + ".md"), encoding="utf-8") as f:
        return f.read()


@pytest.mark.parametrize("strName, nCollapsed", [
    ("collapsed_all_but_last", 1),
    ("collapsed_among_expanded", 3),
    ("collapsed_older_format", 3),
    ("whole_with_heading", 0),
    ("whole_older_format", 0),
])
def test_collapsed_posts_are_counted(strName, nCollapsed):
    assert count_collapsed_posts(read_thread(strName)) == nCollapsed


def test_a_collapsed_post_of_an_unread_message_is_counted():
    strThread = read_thread("collapsed_all_but_last").replace(
        " Mar 20, 2026, 4:11:23 PM", " unread, Mar 20, 2026, 4:11:23 PM")
    assert count_collapsed_posts(strThread) == 1


def test_the_threads_with_a_collapsed_post_are_listed(tmp_path):
    for strName, strSubdir in [("collapsed_all_but_last", "T"), ("collapsed_older_format", "C"),
                               ("whole_with_heading", "S"), ("whole_older_format", "aDigits")]:
        os.makedirs(tmp_path / strSubdir, exist_ok=True)
        shutil.copy(os.path.join(THREADS, strName + ".md"), tmp_path / strSubdir / (strName + ".md"))
    assert get_collapsed_threads(str(tmp_path)) == ["collapsed_all_but_last",
                                                    "collapsed_older_format"]


@pytest.fixture
def data_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr(process_message, "MESSAGE_MD_DIR", str(tmp_path / "msgs_md"))
    monkeypatch.setattr(process_message, "MESSAGE_FILTERED_DIR", str(tmp_path / "msgs"))
    return tmp_path


def test_a_fetched_thread_with_a_collapsed_post_leaves_no_file(data_dirs, capsys):
    assert process_message.save_thread("TE3sTRUz6xo", read_thread("collapsed_all_but_last"),
                                       True) is False
    assert list(data_dirs.rglob("*")) == []
    assert capsys.readouterr().out == "Id TE3sTRUz6xo has 1 collapsed posts, not saved\n"


def test_a_fetched_whole_thread_is_saved(data_dirs):
    strThread = read_thread("whole_with_heading")
    assert process_message.save_thread("sklLflSc-Q8", strThread, True) is True
    with open(data_dirs / "msgs_md" / "S" / "sklLflSc-Q8.md", encoding="utf-8") as f:
        assert f.read() == strThread
    assert (data_dirs / "msgs" / "S" / "sklLflSc-Q8.txt").exists()


def test_a_saved_markdown_file_with_a_collapsed_post_gets_no_text_file(data_dirs, capsys):
    assert process_message.save_thread("CFIdt9rCXvo", read_thread("collapsed_older_format"),
                                       False) is False
    assert list(data_dirs.rglob("*")) == []
    assert capsys.readouterr().out == "Id CFIdt9rCXvo has 3 collapsed posts, not saved\n"


def test_a_saved_whole_markdown_file_gets_only_its_text_file(data_dirs):
    assert process_message.save_thread("1FZkFhlGOTU", read_thread("whole_older_format"),
                                       False) is True
    assert sorted(p.name for p in data_dirs.rglob("*.*")) == ["1FZkFhlGOTU.txt"]
