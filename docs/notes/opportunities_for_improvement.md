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

## site_2024: housekeeping (logged 2026-11-21)

- No security headers (HSTS and similar) are sent.
- Two warnings appear in the container logs on both the old and the upgraded stack
  (seen in the Phase 0 rehearsal, 2026-11-21). Ollama: `requested context size too
  large for model` (8192 requested, `nomic-embed-text` takes 2048). gunicorn 27: the
  config file should have a `.py` name.
