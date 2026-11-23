# Required From Tom

**Last Updated:** 2026-11-23

Items the annual refresh needs from Tom. See `annual_refresh_plan.md`.

## Decisions

All decided: D1 to D51 in the plan's table.
 The dated list of what Tom decided and the
finished work items are in the git history of this file.

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
- [ ] Before leaving on 2026-11-22, for the overnight embedding (plan 2.2a): Windows set not to
      sleep, Docker Desktop left running, the GPU left free.
- [ ] Each morning until the five variants are done: run the stop command, and each evening the
      continue command ("Stop and continue" in `programmer_todo.md`). Read "For Tom in the
      morning" there.
- [ ] Image update (plan 4.0): try the review tool on the pictures of 2025 when the Programmer
      shows it; run the download on Windows with Chrome signed in; then decide the suggested
      and the new pictures in the tool.
- [ ] Label pooled retrieval candidates `y` / `n` in batches of 10 questions, 150 to 250
      rows per batch (Phase 2.3)

## Still true

- Tom waived the code review of the Phase 1 deploy (2026-11-21), the rest of that of the
  follow-on deploy (2026-11-22) and that of the model change (2026-11-22, D37). The UI
  changes and the corpus update were waived on 2026-11-22 (D47).
- The OpenAI account has a budget limit with no auto reload (S2).
- The account can call `gpt-6-luna`, `gpt-6.1-terra`, `gpt-6.2-sol` and `gpt-6.2-astra`.
- One OpenAI key serves the server and local runs.
- The certificate expires 2027-02-20.
