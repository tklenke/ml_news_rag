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
- [x] Code review of the Phase 0 branch is waived (2026-11-21)
- [x] Two gunicorn workers, and a 2 GB swap file on the server (2026-11-21)
- [x] The model evaluation runs every model at its default reasoning effort (plan 1.3)
      (2026-11-21)
- [x] DokuWiki sites (`/dokucozy/`, `/dokuN657CZ/`) are removed in this refresh; they
      are not used (2026-11-21)
- [x] No nginx rate limit; the OpenAI budget limit with no auto reload is the limit on
      abuse (plan S2, D25) (2026-11-21)
- [x] A revise is given every retrieved chunk and the job record keeps every chunk id
      (D26); a follow-up is given only what the previous answer was given, plus new chunks
      cut as for a first answer (D27) (2026-11-21)

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
- [x] Paste `sudo_renew_cert.sh` to the Programmer again (2026-11-21)
- [x] Remove the empty root-owned directory on the local machine (2026-11-21):
      `cd ~/projects/site_2024 && sudo rmdir -p home/admin/www/cgimages`
- [x] Run the deploy commands on the server with the Programmer (plan 0.8), then run the
      fixed `sudo_renew_cert.sh` once (2026-11-21). Certificate expires 2027-02-20.
- [ ] Decide whether the site containers restart after a reboot (`restart: unless-stopped`).
      Today the site stays down until started by hand.
- [ ] Decide whether the certificate should also cover `www.m24tom.com`.
- [ ] From 2026-11-28, if the site has run well: server cleanup with the Programmer
      (commands in `programmer_todo.md`, "Server cleanup").
- [x] Evaluation questions: all 52 candidates approved; Architect ordered them (2026-11-21)
- [x] Give the production nginx config to the Programmer at the start of their first session (2026-11-21)
- [ ] Rate model answers, blind, in batches of 10: `perfect` / `ok` / `not_good` plus
      factual errors (Phase 1.4, 1.5)
- [ ] Label pooled retrieval candidates `y` / `n` in batches of 10 questions, 150 to 250
      rows per batch (Phase 2.3)
- [x] Confirm OpenAI account has access to `gpt-6-luna`, `gpt-6.1-terra`, `gpt-6.2-sol`.
      Smoke calls repeated 2026-11-21: all three, and `gpt-6.2-astra`, answer.
- [x] Set a monthly spend cap on the OpenAI account (S2). Tom confirmed it is on (2026-11-21)
- [x] Confirm the `OPENAI_KEY` value in the tracked `.env_flask` was never a real key (S9).
      The server copy and every committed version contain only
      `put-your-openai-key-here` (2026-11-21)
