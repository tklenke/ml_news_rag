# Opportunities For Improvement

Things worth doing later that are not scheduled now.

## site_2024: job processing (logged 2026-11-21, review finding S8)

Works at current volume (about 850 jobs). Revisit if answers stall or pages slow down.

- Each gunicorn worker (2 in production) starts its own job-processing thread, and
  each scans every job file when it wakes. At startup they scan at once and can
  pick up the same unprocessed job.
- `FileProcessorThread.__init__` sets `daemon = True` and then calls
  `super().__init__()`, which resets it.
- A job whose worker dies mid-run stays in `start` status forever; the user's
  page polls without end.
- The jobs page opens and parses every job file on each view.
- The OpenAI call has no timeout set; one hung call blocks that worker's queue.
- A job file is updated by reading it, changing a value and writing it back, with
  the lock released in between. Two updates of the same job at once (feedback
  arriving while the job thread saves a status) can overwrite each other.
- (logged 2026-11-22, review finding R5, accepted as D34) A job file is empty for a moment
  between its creation and the lock. A scan that reads it then treats it as unreadable and
  does not look at it again, so that worker never answers it; if the file becomes readable
  before the status is saved, the job ends in `error` instead. Not seen in 12,000 jobs
  unless the timing was forced.
- (logged 2026-11-22, read from the code, not tried) `update_process_info` prints an
  `IOError` and returns, so a result that cannot be saved raises nothing: the job stays
  in `start`.

## site_2024: housekeeping (logged 2026-11-21)

- No security headers (HSTS and similar) are sent.
- Two warnings appear in the container logs on both the old and the upgraded stack
  (seen in the Phase 0 rehearsal, 2026-11-21). Ollama: `requested context size too
  large for model` (8192 requested, `nomic-embed-text` takes 2048). gunicorn 27: the
  config file should have a `.py` name.

## ml: corpus (logged 2026-11-22)

- The collection holds 42 chunks with only the prefix. None reached the top 60 of the 52
  questions, so they are left. A full re-embed removes them.
- `process_message.py` skips a thread that has a `.txt`, so replies to a known thread are
  not fetched at the next update unless its `.txt` and `.md` are moved aside first.

## ml: yearly update (logged 2026-11-24, Programmer's report YU5)

Steps Tom does by hand each year from the READMEs. None is built; Tom decided on
2026-11-24 to leave them here. They work as written.

- `get_msg_ids.py`: the start date is a constant to edit, and the id file is written into
  `msgGetter` and must be moved to `data` by hand.
- ChromeDriver's path is written into both `msgGetter` scripts as a relative path;
  `imageGetter` takes `--chromedriver`. One option in all three would remove the rule that
  ChromeDriver must sit in `/home/tom/projects`.
- Python pasted from the READMEs, each of which could be a small command with tests: the
  older threads with new replies (set aside, fetch again, keep the longer copy), the
  deletion of their chunks, the rebuild of `.txt` from `.md`, the count and hash of the
  collection. The check for collapsed posts was on this list and is built with D58.
- The index, gallery and list names carry a date that the steps keep in shell variables
  (`$IDX`, `$G`, `$L`); a new terminal means setting them again.
- `webGetter` has no yearly instructions; it was not run in 2026.
