# Required From Tom

**Last Updated:** 2026-11-24

Items the annual refresh needs from Tom. See `annual_refresh_plan.md`.

## Decisions

Decided: D1 to D57 in the plan's table, D50, D51 and D55 as amended on 2026-11-23.
 The dated list of what Tom decided and the
finished work items are in the git history of this file.

### Waiting for a decision (asked by Architect 2026-11-24)

Details of each are in `architect_todo.md`, "Notes from Programmer".

- [x] **Collapsed posts.** Decided 2026-11-24: found, fixed and deployed now (D58).
- [ ] **Up to 60 threads of 2024-25 never fetched.** Fetch them, and if so in the same pass
      as the collapsed posts?
- [ ] **Process suggestions (8) and the yearly steps that could be small tested scripts
      (4).** Which to take up, and when.
- [ ] **World-writable directories on the server** (`~/site_2024`, `~/www`,
      `~/chroma_before_corpus_update`). Look into why and tighten, or leave.

## Work items

- [x] For the Programmer, before the renewal script is changed: run `certbot certificates`
      on the server (the Programmer supplies the command).
- [ ] From 2026-11-28, if the site has run well: server cleanup with the Programmer
      (commands in `programmer_todo.md`, "Server cleanup").
- [x] Look at an answer with a table in a narrow browser window on the local site (AD6). Approved
      2026-11-22.
- [x] Fetch again the 10 threads that were already in the corpus (D44). Done 2026-11-22; 8 had new
      posts.
- [x] At the deploy: upload the Chroma tar to the server (CU8). Done 2026-11-22.
- [x] Report the browser checks of the deploy of 2026-11-22 (AD7). All passed.
- [ ] Delete `~/site.ini.before_s10` on the local machine (the backup with the keys from S10).
- [x] Rate model answers, blind, in batches of 10: `perfect` / `ok` / `not_good` plus
      factual errors (Phase 1.4, 1.5). Done 2026-11-22, first answer only (D35).
- [x] Before leaving on 2026-11-22, for the overnight embedding (plan 2.2a): Windows set not to
      sleep, Docker Desktop left running, the GPU left free. The run started that evening.
- [x] (Done: the fifth variant finished 2026-11-23 21:57.) Each morning until the five variants are done: run the stop command, and each evening the
      continue command ("Stop and continue" in `programmer_todo.md`). Read "For Tom in the
      morning" there.
- [x] Image update (plan 4.0): try the review tool on the pictures of 2025 when the Programmer
      shows it; run the download on Windows with Chrome signed in; then decide the suggested
      and the new pictures in the tool. Done 2026-11-23; nothing is undecided.
- [x] (Approved 2026-11-24, YU4.) Yearly update instructions: follow the Programmer's draft from the page alone and say
      where it leaves you guessing (`programmer_todo.md`, YU4).
- [x] (Done 2026-11-24, PA7 to PA9.) Pictures of an answer (plan 4.2): look at the local site when the Programmer shows it
      (PA7); at the deploy, upload the thumbnails and the index (under 100 MB; the Programmer
      supplies the commands) and do the browser checks, one of them in a browser that is not
      signed in to Google.
- [ ] Collapsed posts (D58): be at Chrome on Windows while the Programmer finds the cause;
      fetch the affected threads again; download and review pictures if the repaired threads
      bring new ones; run the deploy of the collection from the top-level `README.md`.
- [ ] Reference links, the trial (plan 4.1a): on the local page the Programmer shows, rate the
      10 answers of batch 1 and mark up to 50 citations `yes` / `no` (does the chunk support
      the sentence). A second batch only if the result is on the line.
- [ ] Label pooled retrieval candidates `y` / `n` in batches of 10 questions, 150 to 250
      rows per batch (Phase 2.3)

## Still true

- Tom waived the code review of the Phase 1 deploy (2026-11-21), the rest of that of the
  follow-on deploy (2026-11-22) and that of the model change (2026-11-22, D37). The UI
  changes and the corpus update were waived on 2026-11-22 (D47). The rest of the review of
  the pictures of an answer was waived on 2026-11-24.
- The OpenAI account has a budget limit with no auto reload (S2).
- The account can call `gpt-6-luna`, `gpt-6.1-terra`, `gpt-6.2-sol` and `gpt-6.2-astra`.
- One OpenAI key serves the server and local runs.
- The certificate expires 2027-02-20.
