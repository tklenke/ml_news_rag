# Required From Tom

**Last Updated:** 2026-11-21

Items the annual refresh needs from Tom. See `annual_refresh_plan.md`.

## Decisions

- [x] LLM provider: stay with OpenAI for this version (2026-11-21)
- [x] Keep two tiers: cheap first answer, better model for dig deeper (2026-11-21)
- [x] Chunk size decided by experiment (2026-11-21)
- [x] Work order: models, chunking, website, then reference links and gallery (2026-11-21)
- [x] `CozyRAG_rev1_Back_Test.pdf` superseded (2026-11-21)
- [x] Website refresh scope: reference links and images only (2026-11-21)
- [x] Model evaluation checked at 10, 20 and 30 questions (2026-11-21)
- [x] Site review findings are to be fixed; schedule in plan Phase 3 (2026-11-21)
- [x] No password on the jobs page; a full email address is never sent to a web page (2026-11-21)
- [x] Chunk experiment question set: same 30 plus about 10 new (2026-11-21)
- [x] Production nginx config: the live file is `~/site_2024/server/nginx_all_apps.conf`,
      edited in place on the server. Production code matches the repo; only that file and
      `docker-compose.yaml` differ. Details in
      `docs/references/site_2024_production_state_2026-11-21.md` (2026-11-21)
- [x] Refresh the server to current stable Python, Chroma, OpenAI SDK and dependencies
      (plan Phase 0) (2026-11-21)
- [x] The January 14 date is not a constraint; order work for least repeated effort (2026-11-21)
- [x] Archive the finished image database sections of the todo files (2026-11-21)
- [x] Wiki data is not kept: everything needed has been pulled, so both wikis are deleted from
      the server (2026-11-21). Replaces the plan's tar step; steps in `programmer_todo.md` 0.8
- [x] `fwww/static/test_08_fixture/` was a test upload; remove it from the server (2026-11-21)
- [x] Changes are delivered by `git pull` on the server (2026-11-21)
- [x] The first answer gets 15 chunks; the code that sends 14 is fixed before the
      baseline (2026-11-21)
- [x] Keys move out of `site.ini` into a git-ignored `site_local.ini` (plan S10) (2026-11-21)
- [x] One OpenAI key for the server and local runs; no second key (2026-11-21)
- [x] The stale `__main__` block in `llm_functions.py` is removed (plan 1.1) (2026-11-21)
- [x] DokuWiki sites (`/dokucozy/`, `/dokuN657CZ/`) are removed in this refresh; they
      are not used (2026-11-21)

## Work items

**Before the Programmer can start Phase 0:**

- [x] Enable Docker Desktop's WSL integration for this distro (Settings, Resources, WSL
      integration). If that is not possible, say so: the plan changes (Phase 0).
      Engine 28.3.2, Compose 2.39.1; a container can read `data/chroma` (2026-11-21)
- [x] On the server, `cat exclude_from_tar.txt sudo_renew_cert.sh server/old.nginx_all_apps.conf`
      and `ls -R fwww/static/test_08_fixture/`, and paste the output. (2026-11-21)

**Later:**

- [x] Provide an OpenAI key for a local `site.ini` (rehearsal 0.6, smoke calls 0.7).
      Tom approved using the key already there (2026-11-21)
- [ ] Paste `sudo_renew_cert.sh` to the Programmer again (`cat sudo_renew_cert.sh` on the
      server); the text was not saved and the script is to be fixed and tracked.
- [ ] Remove the empty root-owned directory on the local machine:
      `cd ~/projects/site_2024 && sudo rmdir -p home/admin/www/cgimages`
- [ ] Run the deploy commands on the server with the Programmer (plan 0.8), then run the
      fixed `sudo_renew_cert.sh` once. The certificate expires 2027-01-26.
- [x] Evaluation questions: all 52 candidates approved; Architect ordered them (2026-11-21)
- [x] Give the production nginx config to the Programmer at the start of their first session (2026-11-21)
- [ ] Rate model answers, blind, in batches of 10: `perfect` / `ok` / `not_good` plus
      factual errors (Phase 1.4, 1.5)
- [ ] Label pooled retrieval candidates `y` / `n` in batches of 10 questions, 150 to 250
      rows per batch (Phase 2.3)
- [~] Confirm OpenAI account has access to `gpt-6-luna`, `gpt-6.1-terra`, `gpt-6.2-sol`.
      Smoke calls (2026-11-21): all three, and `gpt-6.2-astra`, return 403 for the
      project `site.ini` uses. Tom (2026-11-21): probably not yet; find out with the smoke calls in plan 0.7,
      and Tom changes account access as needed.
- [x] Set a monthly spend cap on the OpenAI account (S2). Tom confirmed it is on (2026-11-21)
- [x] Confirm the `OPENAI_KEY` value in the tracked `.env_flask` was never a real key (S9).
      The server copy and every committed version contain only
      `put-your-openai-key-here` (2026-11-21)
