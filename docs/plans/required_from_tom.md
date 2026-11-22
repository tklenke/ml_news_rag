# Required From Tom

**Last Updated:** 2026-11-22

Items the annual refresh needs from Tom. See `annual_refresh_plan.md`.

## Decisions

All decided: D1 to D32 in the plan's table. The dated list of what Tom decided and the
finished work items are in the git history of this file.

## Work items

- [x] Containers restart after a reboot: yes (D31, 2026-11-22).
- [ ] At the follow-on deploy: decide whether to reboot the server to prove the restart policy.
- [x] `www.m24tom.com`: covered by the certificate and redirected to `m24tom.com` (D32, 2026-11-22).
- [ ] For the Programmer, before the renewal script is changed: run `certbot certificates`
      on the server (the Programmer supplies the command).
- [ ] From 2026-11-28, if the site has run well: server cleanup with the Programmer
      (commands in `programmer_todo.md`, "Server cleanup").
- [ ] Delete `~/site.ini.before_s10` on the local machine (the backup with the keys from S10).
- [ ] Rate model answers, blind, in batches of 10: `perfect` / `ok` / `not_good` plus
      factual errors (Phase 1.4, 1.5)
- [ ] Label pooled retrieval candidates `y` / `n` in batches of 10 questions, 150 to 250
      rows per batch (Phase 2.3)

## Still true

- Tom waived the code review of the Phase 1 deploy (2026-11-21).
- The OpenAI account has a budget limit with no auto reload (S2).
- The account can call `gpt-6-luna`, `gpt-6.1-terra`, `gpt-6.2-sol` and `gpt-6.2-astra`.
- One OpenAI key serves the server and local runs.
- The certificate expires 2027-02-20.
