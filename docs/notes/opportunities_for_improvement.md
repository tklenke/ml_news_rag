# Opportunities For Improvement

Things worth doing later that are not scheduled now.

## site_2024: job processing (logged 2026-11-21, review finding S8)

Works at current volume (about 850 jobs). Revisit if answers stall or pages slow down.

- Each of the 4 gunicorn workers starts its own job-processing thread, and each
  scans every job file when it wakes. At startup all four scan at once and can
  pick up the same unprocessed job.
- `FileProcessorThread.__init__` sets `daemon = True` and then calls
  `super().__init__()`, which resets it.
- A job whose worker dies mid-run stays in `start` status forever; the user's
  page polls without end.
- The jobs page opens and parses every job file on each view.
- The OpenAI call has no timeout set; one hung call blocks that worker's queue.

## site_2024: housekeeping (logged 2026-11-21)

- No security headers (HSTS and similar) are sent.
- `site.ini.template` has `LLM = gpt-4o-mini`; the code reads `LLM_DRAFT` and `LLM_REVISE`.
