# ABOUTME: Finds posts that a thread was saved with collapsed: Google's one-line preview, cut off
# ABOUTME: Run as a command, it lists the threads of data/msgs_md that hold such a post
import os
import re
import sys

# A post's header is "### name", at the start of a line or, in older files, after the
# profile photo. An expanded post goes on with the author's address, a collapsed one
# straight with its date.
POST_HEADER = "### "
COLLAPSED_POST_START = re.compile(
    r"(unread, )?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4}, ")
MESSAGE_MD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "msgs_md")


def count_collapsed_posts(markdown):
    """The number of posts of a thread's markdown that are collapsed."""
    lines = [line.strip() for line in markdown.split("\n") if line.strip()]
    return sum(1 for line, nextline in zip(lines, lines[1:])
               if POST_HEADER in line and COLLAPSED_POST_START.match(nextline.lstrip("\\")))


def get_collapsed_threads(directory):
    """The ids of the threads in directory and its subdirectories with a collapsed post."""
    ids = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                with open(os.path.join(root, file), encoding="utf-8") as f:
                    if count_collapsed_posts(f.read()):
                        ids.append(file[:-3])
    return sorted(ids)


if __name__ == "__main__":
    ids = get_collapsed_threads(sys.argv[1] if len(sys.argv) > 1 else MESSAGE_MD_DIR)
    for id in ids:
        print(id)
    print(len(ids), "threads with a collapsed post")
