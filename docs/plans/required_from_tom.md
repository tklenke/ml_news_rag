# Required From Tom

**Last Updated:** 2026-11-22

Items the annual refresh needs from Tom. See `annual_refresh_plan.md`.

## Decisions

All decided: D1 to D45 in the plan's table. The dated list of what Tom decided and the
finished work items are in the git history of this file.

## Work items

- [x] For the Programmer, before the renewal script is changed: run `certbot certificates`
      on the server (the Programmer supplies the command).
- [ ] From 2026-11-28, if the site has run well: server cleanup with the Programmer
      (commands in `programmer_todo.md`, "Server cleanup").
- [ ] With the Programmer, before the answer display is reviewed: look at an answer with a
      table in a narrow browser window on the local site (AD6).
- [x] Fetch again the 10 threads that were already in the corpus (D44). Done 2026-11-22; 8 had new
      posts.
- [ ] Decide whether F2 is finished before the deploy or left to the rebuild in Phase 2.
- [ ] With the Programmer, at the deploy: upload the Chroma tar to the server (CU8).
- [ ] Delete `~/site.ini.before_s10` on the local machine (the backup with the keys from S10).
- [x] Rate model answers, blind, in batches of 10: `perfect` / `ok` / `not_good` plus
      factual errors (Phase 1.4, 1.5). Done 2026-11-22, first answer only (D35).
- [ ] Label pooled retrieval candidates `y` / `n` in batches of 10 questions, 150 to 250
      rows per batch (Phase 2.3)

## Still true

- Tom waived the code review of the Phase 1 deploy (2026-11-21), the rest of that of the
  follow-on deploy (2026-11-22) and that of the model change (2026-11-22, D37). The UI
  changes are not covered by a waiver.
- The OpenAI account has a budget limit with no auto reload (S2).
- The account can call `gpt-6-luna`, `gpt-6.1-terra`, `gpt-6.2-sol` and `gpt-6.2-astra`.
- One OpenAI key serves the server and local runs.
- The certificate expires 2027-02-20.
